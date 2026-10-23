"""REL-01c: rolling-origin runner over the integrated Core pipeline, and its frozen exports.

Not a registered module: a driver over the orchestrator, like ``reading_export``. It runs the
existing modules unchanged at every evaluation origin of every selected store and writes the
three exports of ``docs/holdout-evaluation-protocol.md`` §4 for ``eval.harness.freeze``.

Selection. A split from ``config/eval_split.yaml`` (dev | holdout), its stores (all by default),
an inclusive local date range and an origin clock (20:00 by default). Each store's origins are
that local time on every local calendar day, in the store's IANA zone from ``stores.csv``, as
aware instants: the UTC offset follows DST per day. Emails are selected by their ``Date:``
header only; nothing else of a mail is read before the run.

Origins. One RunSpec per store × origin (``as_of`` = origin), with every mail of the store dated
at or before the origin, the latest weekly flash issued by then, 60 days of ERP history and the
weather feed. Row availability is enforced by the modules at that ``as_of`` (``src.email`` by
Date header, ``src.erp`` by posting/vintage availability, ``src.docs`` by issue date,
``src.external`` by end of day), exactly as in any other run. The mail set only grows, and
``int.cases`` fixes a case id by the group that opened it, without dependence on later arrivals:
a case keeps its id at every later origin and the export keeps its first snapshot (the earliest
valid alert), with later status/version changes listed as revisions, never as new alerts.

Shared state across origins. Each store has one SQLite database for all its origins (ERP rows
are shared, run artifacts are partitioned by run id) and all runs share one LLM cache scope:
``LLMClient.for_scope`` with a scope that names the runner, the LLM-calling module versions and
parameters, the model and the namespace, but not the origin. A recording is therefore reused by
a later origin only for a byte-identical request (payload plus the module's own cache context:
document hash and prompt hash for extraction, observation and candidates for linking). The
answer can depend only on that request, so no later information can reach an earlier origin.
The systems (mock warehouse/logistics) recordings keep the full per-origin RunSpec scope.

Reading pass. Before the origins, one reading run (``reading_export``'s modules) over every mail
of the selected stores dated within the local date range writes ``predictions.json``. The
reading scorer reads one ``ModuleRun`` per module, so a single run must cover the sample. Its
requests are the same as the origins' (same scope), so in record mode it records the extraction
calls with full parallelism and the origins replay them.

Record and replay. ``--mode record`` reuses existing recordings before calling Fastweb and is
resumable: an origin is done once ``origins/<STORE>/<DATE>.json`` exists, a failed attempt is
reset and retried, and nothing recorded is ever lost. ``--mode replay`` never reads keys, denies
sockets in the worker processes, and treats any LLM or systems cache miss as a hard error.
Exports exclude only execution timings (``ModuleRun.started_at/finished_at``), so a record run
and a fresh replay produce byte-identical export files. Run the replay under the isolated
launcher (``python -m eval product -- -m tesseract.rolling run ...``): it cannot read answers.

Commands (see ``docs/holdout-evaluation-protocol.md`` §5.1.1)::

    python -m tesseract.rolling estimate --split holdout --start 2026-08-31 --end 2026-10-21
    python -m tesseract.rolling run --split dev --stores MIL01 MUN01 --start 2026-10-01 \\
        --end 2026-10-14 --mode record --cache ../data/rolling/dev-cache \\
        --workspace ../data/rolling/dev-record --code-version "$(git rev-parse HEAD)" --yes
"""

import argparse
import csv
import fcntl
import hashlib
import json
import math
import multiprocessing
import os
import shutil
import sys
import threading
import time as clock
from collections import Counter
from collections.abc import Iterable, Mapping
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from email.parser import BytesHeaderParser
from email.policy import default as email_policy
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

from tesseract.core.cache import CacheCorrupt, ReplayMiss, ResponseCache
from tesseract.core.config import REPO_ROOT, Settings, get_settings

FORMAT = 1
SPLITS = ("dev", "holdout")
ROLLING_MODULES = (
    "src.email",
    "src.erp",
    "src.docs",
    "ing.metrics",
    "src.external",
    "ing.extract",
    "int.link",
    "int.dedup",
    "int.cases",
    "int.context",
    "fc.baseline",
    "fc.overlay",
    "act.options",
    "out.reports",
)
LLM_MODULES = ("ing.extract", "int.link", "ag.investigator")
CONFIG_FILES = ("domain.yaml", "aliases.yaml", "eval_split.yaml", "report_metrics.yaml")
FLASH_DIR = "retail_controlling/weekly_flash"
HISTORY_DAYS = 60
WEATHER_WINDOW_DAYS = 21
# Answer material and credentials never become product inputs (AGENTS.md).
FORBIDDEN_PREFIXES = (
    ("generated", "ground_truth"),
    ("generator",),
    ("eval", "labels"),
)
INFRA_ERRORS = ("ReplayMiss", "CacheCorrupt", "LLMCallFailed", "BudgetExceeded", "budget")
MAX_ATTEMPTS = 3


class RunnerError(RuntimeError):
    """A failed precondition or origin; the message never contains credentials."""


# Selection: stores, zones, origins and mail Date headers.


def load_split(config_dir: Path) -> dict[str, list[str]]:
    split = yaml.safe_load((config_dir / "eval_split.yaml").read_text(encoding="utf-8"))
    return {name: list(split[name]) for name in SPLITS}


def store_zones(sources_dir: Path) -> dict[str, str]:
    path = sources_dir / "erp" / "master_data" / "stores.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        return {row["store_id"]: row["timezone"] for row in csv.DictReader(stream)}


def origins(start: date, end: date, zone: str, at: time) -> list[datetime]:
    """``at`` local on every local calendar day of ``[start, end]``, as aware instants.

    Days advance on the local calendar, so the UTC offset of each origin follows DST. A local
    time that does not exist (a spring-forward gap) or is ambiguous is refused, not shifted.
    """
    if end < start:
        raise ValueError("end precedes start")
    tz = ZoneInfo(zone)
    result = []
    for offset in range((end - start).days + 1):
        local = datetime.combine(start + timedelta(days=offset), at, tzinfo=tz)
        other = local.replace(fold=1)
        roundtrip = local.astimezone(ZoneInfo("UTC")).astimezone(tz)
        if roundtrip.replace(tzinfo=None) != local.replace(tzinfo=None) or (
            other.utcoffset() != local.utcoffset()
        ):
            raise ValueError(f"{local.isoformat()} is not a unique local time in {zone}")
        result.append(local)
    return result


def header_date(path: Path) -> datetime | None:
    """The mail's ``Date:`` as ``src.email`` reads it; only the header block is read."""
    lines = []
    with path.open("rb") as stream:
        for line in stream:
            if line in (b"\n", b"\r\n"):
                break
            lines.append(line)
    header = BytesHeaderParser(policy=email_policy).parsebytes(b"".join(lines)).get("date")
    try:
        value = header.datetime if header is not None else None
    except (AttributeError, TypeError, ValueError):
        return None
    return value if value is not None and value.tzinfo is not None else None


def mailbox(sources_dir: Path, store: str) -> list[tuple[str, datetime | None]]:
    folder = sources_dir / "store_emails" / store
    return [(f"{store}/{p.name}", header_date(p)) for p in sorted(folder.glob("*.eml"))]


def flash_reports(sources_dir: Path) -> list[tuple[str, datetime]]:
    """Weekly flash workbooks with the issue instant their own cover states (``src.docs``)."""
    from tesseract.modules.sources import docs

    found = []
    folder = sources_dir / docs.REPORTS_DIR / FLASH_DIR
    for path in sorted(folder.glob("*.xlsx")):
        relative = f"{FLASH_DIR}/{path.name}"
        try:
            parsed = docs.parse_report(docs.report_path(sources_dir, relative), relative=relative)
        except ValueError:
            continue  # undated or unreadable: src.docs would refuse it too
        found.append((relative, parsed.available_at))
    return found


def latest_report(reports: Iterable[tuple[str, str]], origin: datetime) -> str | None:
    """The latest flash issued at ``origin``; ties go to the later file name (v2_corrected)."""
    issued = [(at, name) for name, at in reports if datetime.fromisoformat(at) <= origin]
    return (
        max(issued, key=lambda item: (datetime.fromisoformat(item[0]), item[1]))[1]
        if issued
        else None
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt_version(path: Path) -> str:
    """The prompt file stem: freeze_record.py resolves backend/prompts/<version>.md and hashes it.

    The content hash lives in the plan (``prompt_files``) and in config.txt; the extraction
    cache context pins it too, so recordings follow the prompt bytes, not this label.
    """
    return path.stem


# Plan: everything that defines the run, frozen in the workspace before any execution.


def build_plan(
    *,
    split: str,
    stores: list[str] | None,
    start: date,
    end: date,
    at: time,
    code_version: str,
    sources_dir: Path,
    config_dir: Path,
    history_days: int = HISTORY_DAYS,
    sys_client: bool = False,
    investigate: int = 0,
    run_id: str | None = None,
) -> dict:
    from tesseract.core.registry import Registry
    from tesseract.modules.agents import investigator
    from tesseract.modules.ingestion import extract
    from tesseract.modules.integration import link

    membership = load_split(config_dir)
    if split not in membership:
        raise RunnerError(f"split must be one of {SPLITS}")
    stores = sorted(stores or membership[split])
    if len(set(stores)) != len(stores) or not stores:
        raise RunnerError("select a nonempty set of unique stores")
    outside = sorted(set(stores) - set(membership[split]))
    if outside:
        raise RunnerError(f"stores outside the {split} split: {', '.join(outside)}")
    zones = store_zones(sources_dir)
    unknown = sorted(set(stores) - set(zones))
    if unknown:
        raise RunnerError(f"unknown stores: {', '.join(unknown)}")
    manifests = {m.id: m for m in Registry.discover().manifests()}
    modules = list(ROLLING_MODULES)
    if sys_client:
        modules.insert(modules.index("int.cases"), "sys.client")
    settings = get_settings()
    reports = [(name, at_.isoformat()) for name, at_ in flash_reports(sources_dir)]
    per_store = {}
    reading_files = []
    for store in stores:
        zone = ZoneInfo(zones[store])
        clocks = origins(start, end, zones[store], at)
        mails = mailbox(sources_dir, store)
        entries = []
        for name, sent in mails:
            # The first origin that admits the mail (None: after the last origin or undated).
            first = next((i for i, o in enumerate(clocks) if sent is not None and sent <= o), None)
            entries.append([name, sent.isoformat() if sent else None, first])
            if sent is not None and start <= sent.astimezone(zone).date() <= end:
                reading_files.append((sent, name))
        per_store[store] = {
            "timezone": zones[store],
            "origins": [o.isoformat() for o in clocks],
            "emails": entries,
        }
    if not reading_files:
        raise RunnerError("no mail of the selected stores is dated inside the range")
    llm_params = {"ing.extract": {}, "int.link": {}}
    if investigate:
        llm_params["ag.investigator"] = {}
    plan = {
        "format": FORMAT,
        "runner": "tesseract.rolling",
        "run_id": run_id or f"rolling-{split}-{start.isoformat()}-{end.isoformat()}",
        "split": split,
        "stores": per_store,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "origin_time": at.isoformat(timespec="minutes"),
        "code_version": code_version,
        "scenario_id": "historical",
        "modules": modules,
        "module_versions": {
            m: manifests[m].version for m in sorted(set(modules) | set(LLM_MODULES))
        },
        "params": {
            "src.erp": {"history_days": history_days},
            "src.external": {"window_days": WEATHER_WINDOW_DAYS},
        },
        "investigate_per_origin": investigate,
        "reports": reports,
        "reading": {
            "files": [name for _, name in sorted(reading_files)],
            "as_of": max(sent for sent, _ in reading_files).isoformat(),
        },
        "prompt_versions": {
            "ing.extract": prompt_version(extract.PROMPT_PATH),
            "int.link": prompt_version(link.PROMPT_PATH),
            **({"ag.investigator": investigator.PROMPT_VERSION} if investigate else {}),
        },
        "model_versions": {
            "chat": settings.chat_model,
            **({"ag.investigator": investigator.MODEL} if investigate else {}),
        },
        "config": {name: sha256_file(config_dir / name) for name in CONFIG_FILES},
        "prompt_files": {
            path.relative_to(REPO_ROOT).as_posix(): sha256_file(path)
            for path in (extract.PROMPT_PATH, link.PROMPT_PATH)
        },
        "llm_scope": {
            "format": 1,
            "runner": "tesseract.rolling",
            "namespace": "product",
            "scenario_id": "historical",
            "chat_model": settings.chat_model,
            "modules": {
                m: {"version": manifests[m].version, "params": llm_params[m]} for m in llm_params
            },
        },
    }
    # The JSON form is the identity: a resumed run compares it to the frozen plan.json.
    return json.loads(canonical(plan))


def estimate(plan: dict, rates: Mapping[str, float] | None = None) -> dict:
    """Mail volume and expected work, from file names and Date headers only."""
    rates = {**DEFAULT_RATES, **(rates or {})}
    stores = {}
    for store, item in plan["stores"].items():
        per_day = Counter(
            e[2] for e in item["emails"] if e[2] is not None
        )  # admitting origin index → mails
        n_origins = len(item["origins"])
        stores[store] = {
            "timezone": item["timezone"],
            "origins": n_origins,
            "emails_total": len(item["emails"]),
            "emails_admitted": sum(per_day.values()),
            "emails_after_last_origin": sum(
                1 for e in item["emails"] if e[1] is not None and e[2] is None
            ),
            "emails_undated": sum(1 for e in item["emails"] if e[1] is None),
            "new_emails_per_origin": {
                "min": min((per_day.get(i, 0) for i in range(n_origins)), default=0),
                "max": max(per_day.values(), default=0),
                "mean": round(sum(per_day.values()) / n_origins, 2) if n_origins else 0,
            },
        }
    files = len(plan["reading"]["files"])
    # Mails read by any run: the reading sample plus earlier mail admitted by the origins.
    read = set(plan["reading"]["files"]) | {
        e[0] for item in plan["stores"].values() for e in item["emails"] if e[2] is not None
    }
    n_runs = sum(s["origins"] for s in stores.values())
    extract_calls = math.ceil(len(read) * rates["extract_calls_per_email"])
    link_calls = math.ceil(len(read) * rates["link_calls_per_email"])
    investigate = plan["investigate_per_origin"] * n_runs * rates["investigator_calls_per_case"]
    calls = extract_calls + link_calls + math.ceil(investigate)
    return {
        "stores": stores,
        "reading_files": files,
        "emails_read": len(read),
        "origin_runs": n_runs,
        "expected_llm_calls": {
            "extract": extract_calls,
            "link": link_calls,
            "investigator": math.ceil(investigate),
            "total_upper_bound_before_cache": calls,
        },
        "rates": rates,
        "note": (
            "Calls are counted before cache reuse: existing recordings for identical requests "
            "cost nothing. Rates come from the dev record evidence in the runbook."
        ),
    }


def wall_time(est: dict, workers: int, concurrency: int, rates: Mapping[str, float]) -> dict:
    llm = est["expected_llm_calls"]["total_upper_bound_before_cache"]
    reading = llm * rates["seconds_per_call"] / max(concurrency, 1)
    per_store = max((s["origins"] for s in est["stores"].values()), default=0)
    lanes = max(1, min(workers, len(est["stores"])))
    rounds = math.ceil(len(est["stores"]) / lanes)
    origins_seconds = rounds * per_store * rates["seconds_per_origin"]
    return {
        "reading_pass_seconds": round(reading),
        "origins_seconds": round(origins_seconds),
        "total_minutes": round((reading + origins_seconds) / 60, 1),
    }


# Rates from the dev record evidence (docs/holdout-evaluation-protocol.md §5.1.1).
DEFAULT_RATES = {
    # Dev record (MIL01+MUN01, 27 mails): 27 extraction + 13 link calls, no retries.
    "extract_calls_per_email": 1.05,
    "link_calls_per_email": 0.5,
    "investigator_calls_per_case": 6.0,
    # 40 calls in 22 s at concurrency 8, i.e. ~4.4 s each when serial.
    "seconds_per_call": 4.5,
    # 4.9 s mean, 8.6 s max over 14 origins; it grows with the cumulative mailbox.
    "seconds_per_origin": 10.0,
}


# Process environment: settings, read guard, network guard.


def worker_settings(
    *, mode: str, data_dir: Path, keys_file: Path | None, concurrency: int, mocks: str | None
) -> Settings:
    values: dict[str, Any] = {
        "llm_mode": mode,
        "data_dir": data_dir,
        "sources_dir": REPO_ROOT / "generated" / "sources",
        "config_dir": REPO_ROOT / "config",
        "llm_concurrency": concurrency,
        "llm_max_calls": 2000,
        "llm_max_tokens": 20_000_000,
        "llm_deadline_seconds": 7200,
        "asr_api_key": None,
        "fastweb_keys_file": keys_file if keys_file else data_dir / "no-credentials.json",
    }
    if mocks:
        values["mocks_base_url"] = mocks
    return Settings(_env_file=None, **values)


def install_environment(settings: Settings) -> None:
    """Modules call ``get_settings()``: make it return exactly these settings, without .env."""
    Settings.model_config["env_file"] = None
    for key, value in settings.model_dump().items():
        name = key.upper()
        if value is None:
            os.environ.pop(name, None)
        elif not hasattr(value, "get_secret_value"):
            os.environ[name] = str(value)
    get_settings.cache_clear()


class Guard:
    """Audit hook: record source/config reads, refuse answer material, deny network in replay."""

    NETWORK = frozenset(
        {
            "socket.connect",
            "socket.getaddrinfo",
            "socket.gethostbyname",
            "socket.gethostbyaddr",
            "socket.sendto",
            "socket.sendmsg",
        }
    )

    def __init__(self, *, offline: bool, allow_secret: Path | None):
        self.offline = offline
        self.allow_secret = allow_secret.resolve() if allow_secret else None
        self.opened: set[str] = set()
        self.denied: list[str] = []
        self._lock = threading.Lock()

    def __call__(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0]
            if isinstance(path, bytes):
                path = os.fsdecode(path)
            if not isinstance(path, str):
                return
            self.check(Path(path))
        elif self.offline and event in self.NETWORK:
            self.denied.append(event)
            raise PermissionError("replay denies network access")

    def check(self, path: Path) -> None:
        path = Path(os.path.abspath(path))
        if not path.is_relative_to(REPO_ROOT):
            return
        parts = path.relative_to(REPO_ROOT).parts
        if any(parts[: len(p)] == p for p in FORBIDDEN_PREFIXES) or any(
            part == "email_context" or part.endswith("_notes.md") for part in parts
        ):
            raise PermissionError("answer material is not a product input")
        if parts[:1] in ((".secrets",), (".env",)):
            if self.allow_secret is None or path.resolve() != self.allow_secret:
                raise PermissionError("credentials are not readable here")
            return
        if (
            parts[:2] == ("generated", "sources")
            or parts[:1] == ("config",)
            or (parts[:2] == ("backend", "prompts"))
        ):
            with self._lock:
                self.opened.add("/".join(parts))

    def take(self) -> list[str]:
        with self._lock:
            opened, self.opened = sorted(self.opened), set()
        return opened


class TrackingCache(ResponseCache):
    """Records the keys used; in replay it is read-only and remembers every miss."""

    def __init__(self, directory: Path, *, read_only: bool):
        super().__init__(directory)
        self.read_only = read_only
        self.used: set[str] = set()
        self.missing: set[str] = set()
        self.corrupt: set[str] = set()

    def get(self, key):
        try:
            response = super().get(key)
        except ReplayMiss:
            if self.read_only:
                self.missing.add(key)
            raise
        except CacheCorrupt:
            self.corrupt.add(key)
            raise
        self.used.add(key)
        return response

    def put(self, key, response):
        if self.read_only:
            raise PermissionError("replay cache is read-only")
        return super().put(key, response)

    def take(self) -> tuple[list[str], list[str], list[str]]:
        result = sorted(self.used), sorted(self.missing), sorted(self.corrupt)
        self.used, self.missing, self.corrupt = set(), set(), set()
        return result


def tracking_systems_cache(directory: Path):
    from tesseract.core.systems_cache import SystemsCache

    class TrackingSystems(SystemsCache):
        def __init__(self, path):
            super().__init__(path)
            self.used: set[str] = set()

        def get(self, key):
            response = super().get(key)
            self.used.add(key)
            return response

    return TrackingSystems(directory)


# Files: atomic JSON, workspace lock.


def write_json(path: Path, value: Any, *, pretty: bool = False) -> str:
    data = (
        json.dumps(value, sort_keys=True, ensure_ascii=False, indent=1, allow_nan=False) + "\n"
        if pretty
        else canonical(value).decode() + "\n"
    ).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def workspace_lock(workspace: Path):
    workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (workspace / ".lock").open("w") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RunnerError("another runner holds this workspace") from None
        yield


def freeze_plan(workspace: Path, plan: dict) -> None:
    """The first run freezes the plan; a resume must request exactly the same plan."""
    path = workspace / "plan.json"
    if path.exists():
        if read_json(path) != plan:
            raise RunnerError("workspace plan differs from this request; use a new workspace")
        return
    if any(p.name not in {".lock"} for p in workspace.iterdir()):
        raise RunnerError("workspace is not empty and has no plan")
    write_json(path, plan, pretty=True)


# Specs.


def _hashes(names: Iterable[str], sources_dir: Path, memo: dict[str, str]) -> list[list[str]]:
    result = []
    for name in names:
        if name not in memo:
            memo[name] = sha256_file(sources_dir / name)
        result.append([name, memo[name]])
    return result


def config_hash(plan: dict) -> str:
    return digest(sorted(plan["config"].items()))


@lru_cache(maxsize=1)
def manifests() -> dict:
    from tesseract.core.registry import Registry

    return {m.id: m for m in Registry.discover().manifests()}


def origin_spec(plan: dict, store: str, index: int, memo: dict[str, str], sources_dir: Path):
    from tesseract.core.contracts import ModuleSnapshot, RunSpec

    item = plan["stores"][store]
    origin = datetime.fromisoformat(item["origins"][index])
    files = [e[0] for e in item["emails"] if e[2] is not None and e[2] <= index]
    report = latest_report(plan["reports"], origin)
    params: dict[str, dict] = {k: dict(v) for k, v in plan["params"].items()}
    if files:
        params["src.email"] = {"files": files}
    if report:
        params["src.docs"] = {"report": report}
    selection = {
        "emails": _hashes((f"store_emails/{f}" for f in files), sources_dir, memo),
        "report": _hashes([f"reports/{report}"], sources_dir, memo) if report else [],
        "erp_history_days": plan["params"]["src.erp"]["history_days"],
    }
    return RunSpec(
        run_id=f"{plan['run_id']}-{store}-{origin.date().isoformat()}",
        scenario_id=plan["scenario_id"],
        as_of=origin,
        stores=(store,),
        source_manifest_hash=digest(selection),
        config_hash=config_hash(plan),
        code_version=plan["code_version"],
        mode="recorded",
        modules=tuple(
            ModuleSnapshot(manifest=manifests()[m], params=params.get(m, {}))
            for m in plan["modules"]
        ),
        prompt_versions=plan["prompt_versions"],
        model_versions=plan["model_versions"],
        authorized_fixture_refs=(),
    )


def reading_spec(plan: dict, memo: dict[str, str], sources_dir: Path):
    from tesseract.core.contracts import ModuleSnapshot, RunSpec
    from tesseract.modules.ingestion import reading_export

    files = plan["reading"]["files"]
    params = {"src.email": {"files": files}, "src.erp": dict(reading_export.ERP_PARAMS)}
    return RunSpec(
        run_id=f"{plan['run_id']}-reading",
        scenario_id=plan["scenario_id"],
        as_of=datetime.fromisoformat(plan["reading"]["as_of"]),
        stores=tuple(plan["stores"]),
        source_manifest_hash=digest(
            {"emails": _hashes((f"store_emails/{f}" for f in files), sources_dir, memo)}
        ),
        config_hash=config_hash(plan),
        code_version=plan["code_version"],
        mode="recorded",
        modules=tuple(
            ModuleSnapshot(manifest=manifests()[m], params=params.get(m, {}))
            for m in reading_export.MODULES
        ),
        prompt_versions={k: plan["prompt_versions"][k] for k in ("ing.extract", "int.link")},
        model_versions={"chat": plan["model_versions"]["chat"]},
        authorized_fixture_refs=(),
    )


# Execution, inside one worker process.


class Worker:
    def __init__(
        self, workspace: Path, plan: dict, mode: str, cache: Path, options: dict, guard: Guard
    ):
        self.workspace = workspace
        self.plan = plan
        self.mode = mode
        self.options = options
        self.guard = guard
        self.memo: dict[str, str] = {}
        self.keys = Path(options["keys_file"]) if mode == "record" else None
        self.llm_cache = TrackingCache(cache / "llm", read_only=mode == "replay")
        self.systems = tracking_systems_cache(cache / "systems")

    def settings(self, data_dir: Path) -> Settings:
        settings = worker_settings(
            mode=self.mode,
            data_dir=data_dir,
            keys_file=self.keys,
            concurrency=self.options["llm_concurrency"],
            mocks=self.options.get("mocks"),
        )
        install_environment(settings)
        return settings

    def clients(self, settings: Settings, spec):
        from tesseract.core.llm import LLMClient
        from tesseract.core.systems_cache import systems_factory

        client = LLMClient(settings, cache=self.llm_cache, concurrency=settings.llm_concurrency)
        return client, {
            "llm": client.for_scope(self.plan["llm_scope"]),
            "systems": systems_factory(
                settings, spec, self.systems, allow_recording=self.mode == "record"
            ),
        }

    def execute(self, spec, engine, settings, modules=None) -> dict:
        """One orchestrated run plus its LLM/systems/read accounting; never raises on misses."""
        from tesseract.core.orchestrator import run
        from tesseract.core.repo import RunNotFound, reset_run

        try:
            reset_run(engine, spec.run_id)  # a crashed or failed earlier attempt
        except RunNotFound:
            pass
        self.guard.take()
        self.llm_cache.take()
        self.systems.used, self.systems.missing, self.systems.corrupt = set(), set(), set()
        self.systems.failures = 0
        client, clients = self.clients(settings, spec)
        started = clock.monotonic()
        error = None
        statuses = ()
        try:
            statuses = run(spec, engine=engine, clients=clients, settings=settings)
        except Exception as exc:  # recorded below; a failed run publishes nothing
            error = type(exc).__name__
        used, missing, corrupt = self.llm_cache.take()
        failed_keys = {t["key"] for t in client.traces if t.get("status") not in (None, 200)}
        failed_keys |= {t["key"] for t in client.traces if t.get("error")}
        ok_keys = {t["key"] for t in client.traces if t.get("status") == 200 or t.get("cache_hit")}
        module_errors = [e for s in statuses if s.result for e in s.result.errors]
        return {
            "statuses": statuses,
            "error": error,
            "elapsed_seconds": round(clock.monotonic() - started, 3),
            "llm": {
                "requests": len({t["key"] for t in client.traces}),
                "cache_hits": sum(1 for t in client.traces if t.get("cache_hit")),
                "provider_calls": sum(1 for t in client.traces if not t.get("cache_hit")),
                "provider_failures": len(failed_keys - ok_keys),
                "tokens_billed": sum(
                    t.get("tokens", 0) for t in client.traces if not t.get("cache_hit")
                ),
                "keys": used,
                "missing": missing,
                "corrupt": corrupt,
            },
            "systems": {
                "keys": sorted(self.systems.used),
                "missing": sorted(self.systems.missing),
                "corrupt": sorted(self.systems.corrupt),
            },
            "opened": self.guard.take(),
            "module_errors": module_errors,
            "network_denied": len(self.guard.denied),
        }

    def problems(self, outcome: dict, state: dict | None) -> list[str]:
        found = []
        if outcome["error"]:
            found.append(f"run raised {outcome['error']}")
        if state is None or not state["published"]:
            found.append(f"run not published ({state['status'] if state else 'missing'})")
        for kind in ("llm", "systems"):
            if outcome[kind]["missing"]:
                found.append(f"{kind} recordings missing: {len(outcome[kind]['missing'])}")
            if outcome[kind]["corrupt"]:
                found.append(f"{kind} recordings corrupt: {len(outcome[kind]['corrupt'])}")
        if outcome["llm"]["provider_failures"]:
            found.append(f"provider failures: {outcome['llm']['provider_failures']}")
        if outcome["network_denied"]:
            found.append("network access attempted in replay")
        infra = [e for e in outcome["module_errors"] if any(t in e for t in INFRA_ERRORS)]
        if infra:
            found.append(f"module LLM/cache errors: {infra[:5]}")
        return found

    def attempt(self, label: str, run_once) -> dict:
        """Record retries transient failures (recordings are kept); replay fails at once."""
        last: list[str] = []
        for number in range(1, MAX_ATTEMPTS + 1 if self.mode == "record" else 2):
            outcome, state, extra = run_once()
            last = self.problems(outcome, state)
            if not last:
                outcome["attempts"] = number
                return {"outcome": outcome, "state": state, **extra}
            write_json(
                self.workspace / "failures" / f"{label}-attempt{number}-{self.mode}.json",
                {
                    "label": label,
                    "problems": last,
                    "llm_missing": outcome["llm"]["missing"],
                    "systems_missing": outcome["systems"]["missing"],
                    "module_errors": outcome["module_errors"],
                },
                pretty=True,
            )
            if self.mode == "record" and number < MAX_ATTEMPTS:
                clock.sleep(5 * number)
        raise RunnerError(f"{label}: {'; '.join(last)}")

    # Reading pass.

    def reading(self) -> dict:
        from tesseract.core.contracts import EntityLink, Observation, Segment, SourceDocument
        from tesseract.core.db import connect
        from tesseract.core.run_repo import repo_session

        path = self.workspace / "reading.json"
        if path.exists():
            return {"skipped": True}
        settings = self.settings(self.workspace / "db" / "reading")
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        spec = reading_spec(self.plan, self.memo, settings.sources_dir)
        engine = connect(settings.db_url)

        def once():
            outcome = self.execute(spec, engine, settings)
            records, state = [], None
            try:
                with repo_session(engine, spec.run_id) as repo:
                    state = repo.run_state()
                    for kind in (SourceDocument, Segment, Observation, EntityLink):
                        records += [
                            {"kind": kind.__name__, "payload": r.model_dump(mode="json")}
                            for r in repo.list(kind)
                        ]
            except Exception:
                state = None
            return outcome, state, {"records": records}

        try:
            done = self.attempt("reading", once)
        finally:
            engine.dispose()
        outcome = done["outcome"]
        result = {
            "format": FORMAT,
            "run_id": spec.run_id,
            "spec": spec.model_dump(mode="json"),
            "status": done["state"]["status"],
            "modules": [s.model_dump(mode="json") for s in outcome["statuses"]],
            "records": done["records"],
            **{k: outcome[k] for k in ("llm", "systems", "opened", "elapsed_seconds", "attempts")},
        }
        write_json(path, result)
        return {"skipped": False, "llm": outcome["llm"]["provider_calls"]}

    # Rolling origins of one store.

    def store(self, store: str) -> dict:
        from tesseract.core.contracts import ActionOption, AgentTrace, Case, ForecastAdjustment
        from tesseract.core.db import connect
        from tesseract.core.repo import latest
        from tesseract.core.run_repo import repo_session

        item = self.plan["stores"][store]
        settings = self.settings(self.workspace / "db" / store)
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        engine = connect(settings.db_url)
        seen_options: set[tuple[str, str]] = set()
        seen_cases: set[str] = set()
        summary = Counter()
        try:
            for index, origin in enumerate(item["origins"]):
                day = datetime.fromisoformat(origin).date().isoformat()
                path = self.workspace / "origins" / store / f"{day}.json"
                if path.exists():
                    previous = read_json(path)
                    seen_options.update((o["id"], o["version"]) for o in previous["options"])
                    seen_cases.update(c["id"] for c in previous["cases"])
                    summary["resumed"] += 1
                    continue
                spec = origin_spec(self.plan, store, index, self.memo, settings.sources_dir)

                def once(spec=spec):
                    outcome = self.execute(spec, engine, settings)
                    extra: dict[str, Any] = {}
                    state = None
                    try:
                        with repo_session(engine, spec.run_id) as repo:
                            state = repo.run_state()
                            extra["cases"] = [
                                c.model_dump(mode="json") for c in latest(repo.list(Case))
                            ]
                            extra["options"] = [
                                o.model_dump(mode="json") for o in repo.list(ActionOption)
                            ]
                            extra["forecast"] = [
                                f.model_dump(mode="json") for f in repo.list(ForecastAdjustment)
                            ]
                    except Exception:
                        state = None
                    return outcome, state, extra

                done = self.attempt(f"{store}-{day}", once)
                outcome = done["outcome"]
                options = [
                    o for o in done["options"] if (o["id"], o["version"]) not in seen_options
                ]
                seen_options.update((o["id"], o["version"]) for o in done["options"])
                traces, investigation = [], None
                new_cases = [c for c in done["cases"] if c["id"] not in seen_cases]
                seen_cases.update(c["id"] for c in done["cases"])
                if self.plan["investigate_per_origin"]:
                    traces, investigation = self.investigate(
                        spec, engine, settings, new_cases, AgentTrace, repo_session
                    )
                result = {
                    "format": FORMAT,
                    "store": store,
                    "date": day,
                    "origin": origin,
                    "run_id": spec.run_id,
                    "spec": spec.model_dump(mode="json"),
                    "status": done["state"]["status"],
                    "modules": [s.model_dump(mode="json") for s in outcome["statuses"]],
                    "cases": done["cases"],
                    "options": options,
                    "option_count": len(done["options"]),
                    "forecast": done["forecast"] if self.options["forecast"] else [],
                    "traces": traces,
                    "investigation": investigation,
                    **{
                        k: outcome[k]
                        for k in ("llm", "systems", "opened", "elapsed_seconds", "attempts")
                    },
                }
                write_json(path, result)
                summary["executed"] += 1
                summary["provider_calls"] += outcome["llm"]["provider_calls"]
        finally:
            engine.dispose()
        return {"store": store, **summary}

    def investigate(self, spec, engine, settings, new_cases, AgentTrace, repo_session):
        """Optional: investigate up to N newly opened resolved cases in a sibling run."""
        from tesseract.core.contracts import ModuleSnapshot

        rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        chosen = [
            c["id"]
            for c in sorted(new_cases, key=lambda c: (rank[c["priority"]], c["id"]))
            if c["scope_level"] != "unknown"
        ][: self.plan["investigate_per_origin"]]
        if not chosen:
            return [], {"case_ids": []}
        manifest = manifests()["ag.investigator"]
        modules = [*spec.modules]
        modules.insert(
            next(i for i, m in enumerate(modules) if m.manifest.id == "out.reports"),
            ModuleSnapshot(manifest=manifest, params={"case_ids": chosen}),
        )
        sibling = spec.model_copy(
            update={"run_id": spec.run_id + "-inv", "modules": tuple(modules)}
        )

        def once():
            outcome = self.execute(sibling, engine, settings)
            state, traces = None, []
            try:
                with repo_session(engine, sibling.run_id) as repo:
                    state = repo.run_state()
                    traces = [t.model_dump(mode="json") for t in repo.list(AgentTrace)]
            except Exception:
                state = None
            return outcome, state, {"traces": traces}

        done = self.attempt(sibling.run_id, once)
        return done["traces"], {
            "case_ids": chosen,
            "run_id": sibling.run_id,
            "status": done["state"]["status"],
            "llm": done["outcome"]["llm"],
        }


_GUARD: Guard | None = None


def _worker(task: tuple) -> dict:
    global _GUARD
    workspace, plan, mode, cache, options, job = task
    if _GUARD is None:
        # Audit hooks cannot be removed: one per pool process, which serves one mode.
        keys = Path(options["keys_file"]) if mode == "record" else None
        _GUARD = Guard(offline=mode == "replay", allow_secret=keys)
        sys.addaudithook(_GUARD)
    worker = Worker(Path(workspace), plan, mode, Path(cache), options, _GUARD)
    if job == "reading":
        return {"job": job, **worker.reading()}
    return {"job": job, **worker.store(job)}


# Exports.


def _strip_timing(module_run: dict) -> dict:
    return {**module_run, "started_at": None, "finished_at": None}


def _semantic(payload: dict) -> str:
    return digest({k: v for k, v in payload.items() if k not in ("run_id", "computed_at")})


def build_exports(workspace: Path, plan: dict) -> dict:
    """The protocol §4 exports, rebuilt deterministically from the per-origin results."""
    reading = read_json(workspace / "reading.json")
    specs = [reading["spec"]]
    predictions = [{"kind": "RunSpec", "payload": reading["spec"]}]
    predictions += [{"kind": "ModuleRun", "payload": _strip_timing(m)} for m in reading["modules"]]
    predictions += reading["records"]
    cases: dict[str, dict] = {}
    options, forecast, traces, runs = [], [], [], []
    opened = set(reading["opened"])
    llm_keys = set(reading["llm"]["keys"])
    systems_keys: set[str] = set()
    drift = []
    counters = Counter()
    for store, item in plan["stores"].items():
        last_origin = item["origins"][-1] if item["origins"] else None
        for origin in item["origins"]:
            day = datetime.fromisoformat(origin).date().isoformat()
            result = read_json(workspace / "origins" / store / f"{day}.json")
            runs.append(
                {
                    "store": store,
                    "origin": origin,
                    "run_id": result["run_id"],
                    "status": result["status"],
                    "spec_sha256": digest(result["spec"]),
                    "modules": {m["module_id"]: m["status"] for m in result["modules"]},
                    "counts": {
                        "cases": len(result["cases"]),
                        "options": result["option_count"],
                        "forecast": len(result["forecast"]),
                    },
                }
            )
            specs.append(result["spec"])
            opened.update(result["opened"])
            llm_keys.update(result["llm"]["keys"])
            systems_keys.update(result["systems"]["keys"])
            if result.get("investigation"):
                llm_keys.update(result["investigation"].get("llm", {}).get("keys", []))
            for case in result["cases"]:
                entry = cases.get(case["id"])
                state = {
                    "origin": origin,
                    "version": case["version"],
                    "status": case["status"],
                    "priority": case["priority"],
                    "sha256": _semantic(case),
                }
                if entry is None:
                    cases[case["id"]] = {
                        "payload": case,
                        "store": store,
                        "origin": origin,
                        "run_id": result["run_id"],
                        "revisions": [state],
                        "last_seen_origin": origin,
                    }
                    continue
                first = entry["payload"]
                for field in ("first_available_at", "scope_level", "scope_id", "case_type"):
                    if case[field] != first[field]:
                        drift.append({"case": case["id"], "origin": origin, "field": field})
                if entry["revisions"][-1]["sha256"] != state["sha256"]:
                    entry["revisions"].append(state)
                entry["last_seen_origin"] = origin
            options += [
                {"origin": origin, "run_id": result["run_id"], "payload": o}
                for o in result["options"]
            ]
            forecast += [{"as_of": origin, "payload": f} for f in result["forecast"]]
            traces += [{"origin": origin, "payload": t} for t in result["traces"]]
            counters["origin_runs"] += 1
        for case in cases.values():
            if case["store"] == store:
                case["present_at_final_origin"] = case["last_seen_origin"] == last_origin
    case_rows = sorted(cases.values(), key=lambda c: (c["origin"], c["payload"]["id"]))
    options.sort(key=lambda o: (o["origin"], o["payload"]["id"], o["payload"]["version"]))
    forecast.sort(key=lambda f: (f["as_of"], f["payload"]["store_id"], f["payload"]["id"]))
    lagged = [
        (
            datetime.fromisoformat(c["origin"])
            - datetime.fromisoformat(c["payload"]["first_available_at"])
        ).total_seconds()
        / 3600
        for c in case_rows
    ]
    return {
        "predictions": predictions,
        "cases": case_rows,
        "options": options,
        "forecast": forecast,
        "traces": traces,
        "runs": runs,
        "specs": specs,
        "opened": sorted(opened),
        "llm_keys": sorted(llm_keys),
        "systems_keys": sorted(systems_keys),
        "diagnostics": {
            "case_identity_drift": drift,
            "cases": len(case_rows),
            "cases_withdrawn_before_final_origin": sum(
                1 for c in case_rows if not c.get("present_at_final_origin", True)
            ),
            "alert_origin_minus_first_available_hours": {
                "min": round(min(lagged), 2) if lagged else None,
                "max": round(max(lagged), 2) if lagged else None,
                "mean": round(sum(lagged) / len(lagged), 2) if lagged else None,
            },
            **counters,
        },
    }


def cache_inventory(cache: Path, kind: str, keys: Iterable[str]) -> dict:
    entries = []
    for key in sorted(keys):
        path = cache / kind / key[:2] / f"{key}.json"
        entries.append([key, sha256_file(path)])
    return {"entries": len(entries), "sha256": digest(entries)}


def protocol_skeletons(plan: dict, exports: dict, manifest_fields: dict) -> tuple[dict, dict]:
    stores = sorted(plan["stores"])
    origins_by_store = {s: plan["stores"][s]["origins"] for s in stores}
    unique_origins = sorted(
        {o for values in origins_by_store.values() for o in values},
        key=lambda o: (datetime.fromisoformat(o), o),
    )
    common = {
        "status": "skeleton_unapproved: #211 must review, bind and approve before scoring",
        "run_id": plan["run_id"],
        "split": plan["split"],
        "stores": stores,
        "origins": unique_origins,
        "origins_by_store": origins_by_store,
        "models": {
            "chat": plan["model_versions"]["chat"],
            **(
                {"ag.investigator": plan["model_versions"]["ag.investigator"]}
                if "ag.investigator" in plan["model_versions"]
                else {}
            ),
        },
        "parameters": {
            "runner": "tesseract.rolling",
            "plan_sha256": digest(plan),
            "code_version": plan["code_version"],
            "origin_rule": f"{plan['origin_time']} local, IANA zone from stores.csv, every day",
            "period": [plan["start"], plan["end"]],
            "modules": plan["modules"],
            "module_versions": plan["module_versions"],
            "module_params": plan["params"],
            "investigate_per_origin": plan["investigate_per_origin"],
            "prompt_versions": plan["prompt_versions"],
            "config_sha256": plan["config"],
            "llm_scope": plan["llm_scope"],
            **manifest_fields,
        },
    }
    lead = {
        **common,
        "universe": [{"store_id": s, "sku": "*"} for s in stores],
        "sampling_criterion": (
            "Every mail of the selected stores whose Date header falls in the local period "
            "(reading pass); every store x day origin at the origin clock (rolling cases and "
            "options), including days without mail or alerts. Selected before any scoring."
        ),
        "reading_files": plan["reading"]["files"],
        "case_alert_time": (
            "Case.first_available_at as exported (evidence availability). The wrapper `origin` "
            "is the first origin at which the product emitted the case; see diagnostics."
        ),
    }
    pairs = sorted(
        {
            (f["payload"]["store_id"], f["payload"]["sku"])
            for f in exports["forecast"]
            if f["payload"].get("producer") == "fc.baseline"
        }
    )
    forecast = {
        **common,
        "universe": [
            {"store_id": s, "sku": sku, "timezone": plan["stores"][s]["timezone"]}
            for s, sku in pairs
        ],
        "sampling_criterion": (
            "Every store x SKU-colour with a fc.baseline record at any origin, at every origin "
            "of the period, including unchanged/no-alert products."
        ),
        "forecast": {
            "scenario": "base",
            "scenario_id": "historical",
            "requires_approval": "#211 confirms the ex-ante scenario before scoring",
        },
    }
    return lead, forecast


def finish(workspace: Path, plan: dict, cache: Path, mode: str, wall: float) -> dict:
    exports = build_exports(workspace, plan)
    out = workspace / "export"
    hashes = {}
    counts = {}
    for name in ("predictions", "cases", "options", "forecast", "traces"):
        hashes[f"{name}.json"] = write_json(out / f"{name}.json", exports[name])
        counts[name] = len(exports[name])
    sources = sorted(p for p in exports["opened"] if p.startswith("generated/sources/"))
    # Read configs/prompts plus every declared one (a prompt is read only when it is used).
    configs = sorted(
        {p for p in exports["opened"] if p.startswith(("config/", "backend/prompts/"))}
        | {f"config/{name}" for name in plan["config"]}
        | set(plan["prompt_files"])
    )
    for name, paths in (("sources.txt", sources), ("config.txt", configs)):
        data = "".join(p + "\n" for p in paths).encode()
        (out / name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    caches = {
        "llm": cache_inventory(cache, "llm", exports["llm_keys"]),
        "systems": cache_inventory(cache, "systems", exports["systems_keys"]),
    }
    source_inventory = digest([[p, sha256_file(REPO_ROOT / p)] for p in sources])
    fields = {
        "source_inventory_sha256": source_inventory,
        "llm_cache_sha256": caches["llm"]["sha256"],
        "systems_cache_sha256": caches["systems"]["sha256"],
    }
    lead, forecast = protocol_skeletons(plan, exports, fields)
    # One RunSpec file per run, for `freeze_record.py record --run-spec`.
    spec_hashes = {
        spec["run_id"]: write_json(out / "run-specs" / f"{spec['run_id']}.json", spec, pretty=True)
        for spec in exports["specs"]
    }
    hashes["run-specs/"] = digest(sorted(spec_hashes.items()))
    # A ready forecast bundle directory: its predictions are the forecast records.
    bundle = out / "forecast"
    bundle.mkdir(exist_ok=True)
    for name, target in (
        ("forecast.json", "predictions.json"),
        ("cases.json", "cases.json"),
        ("options.json", "options.json"),
    ):
        link = bundle / target
        link.unlink(missing_ok=True)
        try:
            os.link(out / name, link)
        except OSError:  # Landlock refuses cross-directory links (EXDEV): copy instead
            shutil.copyfile(out / name, link)
    hashes["protocol.json"] = write_json(out / "protocol.json", lead, pretty=True)
    hashes["protocol-forecast.json"] = write_json(
        out / "protocol-forecast.json", forecast, pretty=True
    )
    manifest = {
        "format": FORMAT,
        "plan_sha256": digest(plan),
        "run_id": plan["run_id"],
        "code_version": plan["code_version"],
        "exports": hashes,
        "counts": counts,
        "sources": len(sources),
        "configs": len(configs),
        "caches": caches,
        "runs": exports["runs"],
        "diagnostics": exports["diagnostics"],
        "export_hash_excludes": ["ModuleRun.started_at", "ModuleRun.finished_at"],
    }
    hashes["run-manifest.json"] = write_json(out / "run-manifest.json", manifest, pretty=True)
    execution = workspace / "executions" / f"{mode}-{int(clock.time())}.json"
    write_json(
        execution,
        {
            "mode": mode,
            "execution": execution_identity(),
            "wall_seconds": round(wall, 1),
            "exports": hashes,
            "llm": llm_totals(workspace, plan),
        },
        pretty=True,
    )
    return {"exports": hashes, "counts": counts, "diagnostics": exports["diagnostics"]}


def execution_identity() -> dict:
    """HEAD and dirty code paths when git is readable (not under the isolated launcher)."""
    import subprocess

    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain", "--", "backend/tesseract", "backend/prompts"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return {"head": "unavailable", "dirty_code": None}
    return {"head": head, "dirty_code": bool(dirty)}


def llm_totals(workspace: Path, plan: dict) -> dict:
    totals = Counter()
    results = [read_json(workspace / "reading.json")]
    for store, item in plan["stores"].items():
        for origin in item["origins"]:
            day = datetime.fromisoformat(origin).date().isoformat()
            results.append(read_json(workspace / "origins" / store / f"{day}.json"))
    for result in results:
        for key in ("requests", "cache_hits", "provider_calls", "tokens_billed"):
            totals[key] += result["llm"][key]
        totals["elapsed_seconds"] += result["elapsed_seconds"]
    totals["elapsed_seconds"] = round(totals["elapsed_seconds"], 1)
    return dict(totals)


# CLI.


def _date(value: str) -> date:
    return date.fromisoformat(value)


def _clock(value: str) -> time:
    return time.fromisoformat(value)


def _plan_from(args) -> dict:
    settings = get_settings()
    return build_plan(
        split=args.split,
        stores=args.stores,
        start=args.start,
        end=args.end,
        at=args.origin_time,
        code_version=getattr(args, "code_version", None) or "estimate-only",
        sources_dir=settings.sources_dir,
        config_dir=settings.config_dir,
        history_days=getattr(args, "history_days", HISTORY_DAYS),
        sys_client=getattr(args, "sys_client", False),
        investigate=getattr(args, "investigate", 0),
        run_id=getattr(args, "run_id", None),
    )


def preflight(keys: Path, mocks: str) -> None:
    """Record needs the keys file (only its existence is checked) and the systems mocks."""
    import httpx

    if not keys.is_file():
        raise RunnerError("record mode needs the Fastweb keys file")
    try:
        httpx.get(mocks.rstrip("/") + "/logistics/v1/lanes", timeout=5)
    except httpx.HTTPError:
        raise RunnerError(f"systems mock server unreachable at {mocks} (make mocks)") from None


def run_command(args) -> int:
    install_environment(
        worker_settings(
            mode="replay", data_dir=REPO_ROOT / "data", keys_file=None, concurrency=1, mocks=None
        )
    )
    plan = _plan_from(args)
    est = estimate(plan)
    est["wall_time"] = wall_time(est, args.workers, args.llm_concurrency, DEFAULT_RATES)
    print(json.dumps({"estimate": est}, indent=1, sort_keys=True), file=sys.stderr)
    if args.mode == "record" and not args.yes:
        print("record mode: review the estimate above and repeat with --yes", file=sys.stderr)
        return 2
    workspace = args.workspace.resolve()
    cache = args.cache.resolve()
    if workspace.is_relative_to(cache) or cache.is_relative_to(workspace):
        raise RunnerError("workspace and cache must be separate directories")
    if args.mode == "replay" and not (cache / "llm").is_dir():
        raise RunnerError("replay needs an existing cache directory with recordings")
    keys = Path(args.keys_file).resolve() if args.keys_file else get_settings().fastweb_keys_file
    if args.mode == "record":
        preflight(keys, args.mocks_url or get_settings().mocks_base_url)
        for kind in ("llm", "systems"):  # both exist even when nothing is recorded
            (cache / kind).mkdir(parents=True, exist_ok=True)
    options = {
        "llm_concurrency": args.llm_concurrency,
        "forecast": not args.no_forecast,
        "keys_file": str(keys),
        "mocks": args.mocks_url,
    }
    with workspace_lock(workspace):
        freeze_plan(workspace, plan)
        started = clock.monotonic()
        context = multiprocessing.get_context("spawn")
        common = (str(workspace), plan, args.mode, str(cache), options)
        with ProcessPoolExecutor(max_workers=max(1, args.workers), mp_context=context) as pool:
            first = pool.submit(_worker, (*common, "reading")).result()
            print(json.dumps(first, sort_keys=True), file=sys.stderr)
            futures = [pool.submit(_worker, (*common, store)) for store in plan["stores"]]
            failures = []
            for future in futures:
                try:
                    print(json.dumps(future.result(), sort_keys=True), file=sys.stderr)
                except RunnerError as error:
                    failures.append(str(error))
        if failures:
            print(json.dumps({"status": "failed", "failures": failures}, indent=1))
            return 1
        summary = finish(workspace, plan, cache, args.mode, clock.monotonic() - started)
    print(json.dumps({"status": "complete", **summary}, indent=1, sort_keys=True))
    return 0


def estimate_command(args) -> int:
    install_environment(
        worker_settings(
            mode="replay", data_dir=REPO_ROOT / "data", keys_file=None, concurrency=1, mocks=None
        )
    )
    rates = dict(DEFAULT_RATES)
    plan = _plan_from(args)
    est = estimate(plan, rates)
    est["wall_time"] = wall_time(est, args.workers, args.llm_concurrency, rates)
    print(json.dumps(est, indent=1, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("estimate", "run"):
        command = sub.add_parser(name)
        command.add_argument("--split", choices=SPLITS, required=True)
        command.add_argument("--stores", nargs="+", help="default: every store of the split")
        command.add_argument("--start", type=_date, required=True)
        command.add_argument("--end", type=_date, required=True)
        command.add_argument("--origin-time", type=_clock, default=time(20, 0))
        command.add_argument("--workers", type=int, default=4, help="parallel store processes")
        command.add_argument("--llm-concurrency", type=int, default=8)
        command.add_argument("--investigate", type=int, default=0, metavar="N")
        command.add_argument("--sys-client", action="store_true")
        command.add_argument("--history-days", type=int, default=HISTORY_DAYS)
    run = sub.choices["run"]
    run.add_argument("--mode", choices=("record", "replay"), required=True)
    run.add_argument("--cache", type=Path, required=True)
    run.add_argument("--workspace", type=Path, required=True)
    run.add_argument("--code-version", required=True)
    run.add_argument("--run-id")
    run.add_argument("--keys-file", help="record only; default from Settings")
    run.add_argument("--mocks-url", help="systems mock server (record); default from Settings")
    run.add_argument("--no-forecast", action="store_true")
    run.add_argument("--yes", action="store_true", help="confirm a record run after the estimate")
    args = parser.parse_args(argv)
    try:
        return run_command(args) if args.command == "run" else estimate_command(args)
    except RunnerError as error:
        print(json.dumps({"status": "failed", "error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
