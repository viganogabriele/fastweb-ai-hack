"""REL-01c rolling-origin runner: origins, selection, case identity, resume and replay misses.

No credentials or network. Pipeline tests use the dev store MIL01 and replay an empty cache.
"""

import json
import os
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from tesseract import rolling
from tesseract.core.config import REPO_ROOT, Settings, get_settings
from tesseract.modules.ingestion.email_parser import parse_eml

SOURCES = REPO_ROOT / "generated" / "sources"
CONFIG = REPO_ROOT / "config"


@pytest.fixture
def environment(tmp_path):
    """The runner configures modules through the process environment: restore it."""
    saved, env_file = dict(os.environ), Settings.model_config.get("env_file")
    rolling.install_environment(
        rolling.worker_settings(
            mode="replay", data_dir=tmp_path / "data", keys_file=None, concurrency=2, mocks=None
        )
    )
    yield
    os.environ.clear()
    os.environ.update(saved)
    Settings.model_config["env_file"] = env_file
    get_settings.cache_clear()


def plan_for(start, end, stores=("MIL01",)):
    return rolling.build_plan(
        split="dev",
        stores=list(stores),
        start=start,
        end=end,
        at=time(20),
        code_version="test",
        sources_dir=SOURCES,
        config_dir=CONFIG,
    )


def test_origins_follow_the_local_clock_across_dst():
    rome = rolling.origins(date(2026, 10, 24), date(2026, 10, 26), "Europe/Rome", time(20))
    assert [o.isoformat() for o in rome] == [
        "2026-10-24T20:00:00+02:00",
        "2026-10-25T20:00:00+01:00",
        "2026-10-26T20:00:00+01:00",
    ]
    utc = [o.astimezone(ZoneInfo("UTC")) for o in rome]
    assert utc[1] - utc[0] == timedelta(hours=25)  # a local calendar day, not 24 h
    york = rolling.origins(date(2026, 10, 31), date(2026, 11, 2), "America/New_York", time(20))
    assert [o.utcoffset() for o in york] == [timedelta(hours=h) for h in (-4, -5, -5)]
    tokyo = rolling.origins(date(2026, 8, 31), date(2026, 10, 21), "Asia/Tokyo", time(20))
    assert len(tokyo) == 52 and {o.utcoffset() for o in tokyo} == {timedelta(hours=9)}
    assert all(o.hour == 20 and o.tzinfo is not None for o in rome + york + tokyo)


@pytest.mark.parametrize(
    ("day", "at"),
    [
        (date(2026, 3, 29), time(2, 30)),  # spring-forward gap
        (date(2026, 10, 25), time(2, 30)),  # fall-back fold
    ],
)
def test_nonexistent_or_ambiguous_origins_are_refused(day, at):
    with pytest.raises(ValueError, match="unique local time"):
        rolling.origins(day, day, "Europe/Rome", at)


def test_header_date_matches_the_parser_and_reads_only_headers(tmp_path):
    for path in sorted((SOURCES / "store_emails" / "MIL01").glob("*.eml"))[:6]:
        assert rolling.header_date(path) == parse_eml(path.read_bytes()).sent_at
    mail = tmp_path / "mail.eml"
    mail.write_bytes(
        b"Subject: Chiusura del 30/09/2026\r\nDate: Tue, 01 Sep 2026 21:15:00 +0200\r\n\r\n"
        b"Date: Wed, 30 Sep 2026 10:00:00 +0200\r\n"
    )
    assert rolling.header_date(mail).isoformat() == "2026-09-01T21:15:00+02:00"
    mail.write_bytes(b"Subject: no date\r\n\r\nDate: Wed, 30 Sep 2026 10:00:00 +0200\r\n")
    assert rolling.header_date(mail) is None


def test_latest_report_is_the_latest_issued_by_the_origin():
    reports = [
        ("w40_v1", "2026-10-06T00:00:00+02:00"),
        ("w40_v2_corrected", "2026-10-08T00:00:00+02:00"),
        ("w41", "2026-10-13T00:00:00+02:00"),
    ]
    at = datetime.fromisoformat
    assert rolling.latest_report(reports, at("2026-10-05T20:00:00+02:00")) is None
    assert rolling.latest_report(reports, at("2026-10-07T20:00:00+02:00")) == "w40_v1"
    assert rolling.latest_report(reports, at("2026-10-12T20:00:00+02:00")) == "w40_v2_corrected"
    assert rolling.latest_report(reports, at("2026-10-13T00:00:00+02:00")) == "w41"


def test_split_membership_is_checked_before_any_mail_is_read():
    with pytest.raises(rolling.RunnerError, match="outside the dev split"):
        plan_for(date(2026, 9, 1), date(2026, 9, 2), stores=("ROM01",))


def test_origin_specs_admit_only_mail_dated_by_the_origin(environment):
    plan = plan_for(date(2026, 9, 1), date(2026, 9, 4))
    zone = ZoneInfo("Europe/Rome")
    mailbox = rolling.mailbox(SOURCES, "MIL01")
    memo, previous, run_ids = {}, set(), set()
    for index, origin in enumerate(plan["stores"]["MIL01"]["origins"]):
        spec = rolling.origin_spec(plan, "MIL01", index, memo, SOURCES)
        params = {m.manifest.id: m.params for m in spec.modules}
        files = set(params.get("src.email", {}).get("files", []))
        assert spec.as_of == datetime.fromisoformat(origin) and spec.stores == ("MIL01",)
        assert files == {name for name, sent in mailbox if sent and sent <= spec.as_of}
        assert previous <= files  # the mail set only grows: case ids stay stable
        assert "ag.investigator" not in params and "sys.client" not in params
        assert params["src.erp"] == {"history_days": rolling.HISTORY_DAYS}
        previous = files
        run_ids.add(spec.run_id)
    assert len(run_ids) == 4
    sent = dict(mailbox)
    assert plan["reading"]["files"] and all(
        date(2026, 9, 1) <= sent[name].astimezone(zone).date() <= date(2026, 9, 4)
        for name in plan["reading"]["files"]
    )
    assert datetime.fromisoformat(plan["reading"]["as_of"]) == max(
        sent[name] for name in plan["reading"]["files"]
    )
    est = rolling.estimate(plan)
    assert est["origin_runs"] == 4 and est["reading_files"] == len(plan["reading"]["files"])


def case(case_id, status, first, *, version="v1", run="r1", scope_id="J1-999"):
    return {
        "id": case_id,
        "version": version,
        "status": status,
        "priority": "high",
        "first_available_at": first,
        "scope_level": "sku",
        "scope_id": scope_id,
        "case_type": "unmet_demand",
        "store_id": "MIL01",
        "run_id": run,
        "computed_at": run,
    }


def write_results(workspace, origins, cases_per_origin):
    reading = {
        "spec": {"run_id": "reading"},
        "modules": [{"module_id": "ing.extract", "started_at": "t0", "finished_at": "t1"}],
        "records": [],
        "opened": [],
        "llm": {"keys": []},
    }
    rolling.write_json(workspace / "reading.json", reading)
    for origin, cases in zip(origins, cases_per_origin, strict=True):
        day = datetime.fromisoformat(origin).date().isoformat()
        rolling.write_json(
            workspace / "origins" / "MIL01" / f"{day}.json",
            {
                "run_id": f"run-{day}",
                "status": "degraded",
                "spec": {"as_of": origin},
                "modules": [],
                "cases": cases,
                "options": [],
                "option_count": 0,
                "forecast": [],
                "traces": [],
                "opened": [],
                "llm": {"keys": []},
                "systems": {"keys": []},
                "investigation": None,
            },
        )


def test_a_case_keeps_one_identity_and_its_earliest_alert(tmp_path):
    origins = [f"2026-09-0{d}T20:00:00+02:00" for d in (1, 2, 3)]
    plan = {"stores": {"MIL01": {"origins": origins}}}
    first = "2026-08-31T21:15:00+02:00"
    write_results(
        tmp_path,
        origins,
        [
            [case("case-a", "verify", first)],
            [
                case("case-a", "open", first, version="v2", run="r2"),
                case("case-b", "open", origins[1]),
            ],
            [case("case-a", "open", first, version="v2", run="r3")],
        ],
    )

    exports = rolling.build_exports(tmp_path, plan)

    rows = {row["payload"]["id"]: row for row in exports["cases"]}
    assert list(rows) == ["case-a", "case-b"]  # never one alert per snapshot
    a, b = rows["case-a"], rows["case-b"]
    assert a["origin"] == origins[0] and a["payload"]["status"] == "verify"
    assert a["alert_at"] == origins[0]  # evidence at 21:15, product acts at the next 20:00
    assert b["alert_at"] == origins[1]
    assert a["payload"]["first_available_at"] == first
    assert [r["status"] for r in a["revisions"]] == ["verify", "open"]  # r3 only re-ran
    assert a["present_at_final_origin"] and not b["present_at_final_origin"]
    assert exports["diagnostics"]["case_identity_drift"] == []
    assert exports["predictions"][1]["payload"]["started_at"] is None

    write_results(
        tmp_path,
        origins,
        [[case("case-a", "verify", first)], [case("case-a", "open", origins[1])], []],
    )
    drift = rolling.build_exports(tmp_path, plan)["diagnostics"]["case_identity_drift"]
    assert drift == [{"case": "case-a", "origin": origins[1], "field": "first_available_at"}]


def outcome(**changes):
    base = {
        "error": None,
        "llm": {"missing": [], "corrupt": [], "provider_failures": 0},
        "systems": {"missing": [], "corrupt": []},
        "network_denied": 0,
        "module_errors": [],
    }
    return {**base, **changes}


def worker(tmp_path, mode, plan=None):
    options = {"llm_concurrency": 2, "forecast": True, "keys_file": str(tmp_path / "keys.json")}
    guard = rolling.Guard(offline=mode == "replay", allow_secret=None)
    return rolling.Worker(tmp_path / "ws", plan or {}, mode, tmp_path / "cache", options, guard)


def test_replay_miss_fails_at_once_and_record_retries(tmp_path, monkeypatch):
    published = {"published": True, "status": "degraded"}
    missing = outcome(llm={"missing": ["k" * 64], "corrupt": [], "provider_failures": 0})
    calls = []

    def flaky():
        calls.append(1)
        return (missing if len(calls) == 1 else outcome()), published, {}

    with pytest.raises(rolling.RunnerError, match="llm recordings missing"):
        worker(tmp_path, "replay").attempt("MIL01-2026-09-01", flaky)
    assert len(calls) == 1
    failure = tmp_path / "ws/failures/MIL01-2026-09-01-attempt1-replay.json"
    assert json.loads(failure.read_text())["llm_missing"] == ["k" * 64]

    calls.clear()
    monkeypatch.setattr(rolling.clock, "sleep", lambda seconds: None)
    done = worker(tmp_path, "record").attempt("MIL01-2026-09-01", flaky)
    assert done["outcome"]["attempts"] == 2 and len(calls) == 2

    unrecorded = outcome(systems={"missing": [], "corrupt": [], "unrecorded": 2})
    with pytest.raises(rolling.RunnerError, match="systems GETs without a recording"):
        worker(tmp_path, "record").attempt("y", lambda: (unrecorded, published, {}))

    with pytest.raises(rolling.RunnerError, match="provider failures"):
        worker(tmp_path, "record").attempt(
            "x",
            lambda: (
                outcome(llm={"missing": [], "corrupt": [], "provider_failures": 1}),
                published,
                {},
            ),
        )


def test_guard_refuses_answers_and_secrets_and_denies_network_offline():
    guard = rolling.Guard(offline=True, allow_secret=None)
    for path in (
        "generated/ground_truth/scenario/events.json",
        "generator/world.py",
        "eval/labels/reading_dev_v1.yaml",
        "generated/sources/store_emails/x_notes.md",
        ".secrets/fastweb_keys.json",
    ):
        with pytest.raises(PermissionError):
            guard("open", (str(REPO_ROOT / path), "r", 0))
    guard("open", (str(SOURCES / "erp/master_data/stores.csv"), "r", 0))
    guard("open", (str(REPO_ROOT / "backend/tesseract/rolling.py"), "r", 0))
    assert guard.take() == ["generated/sources/erp/master_data/stores.csv"]
    with pytest.raises(PermissionError):
        guard("socket.connect", (None, ("127.0.0.1", 8088)))


def test_store_run_replays_offline_resumes_and_fails_closed_on_a_miss(tmp_path, environment):
    # 2026-08-31 20:00 precedes MIL01's first mail: deterministic modules only, no recording
    # needed. 2026-09-01 has mail: an empty cache must stop the store without any network.
    plan = plan_for(date(2026, 8, 31), date(2026, 9, 1))
    first = tmp_path / "ws/origins/MIL01/2026-08-31.json"

    with pytest.raises(rolling.RunnerError, match="llm recordings missing"):
        worker(tmp_path, "replay", plan).store("MIL01")

    result = json.loads(first.read_text())
    assert result["status"] in {"succeeded", "degraded"} and result["llm"]["requests"] == 0
    assert datetime.fromisoformat(result["spec"]["as_of"]) == datetime.fromisoformat(
        plan["stores"]["MIL01"]["origins"][0]
    )
    assert not (tmp_path / "ws/origins/MIL01/2026-09-01.json").exists()
    failure = json.loads(
        (tmp_path / "ws/failures/MIL01-2026-09-01-attempt1-replay.json").read_text()
    )
    assert failure["llm_missing"]

    executed = []
    resumed = worker(tmp_path, "replay", plan)
    original = resumed.execute

    def counting(spec, *args, **kwargs):
        executed.append(spec.run_id)
        return original(spec, *args, **kwargs)

    resumed.execute = counting
    with pytest.raises(rolling.RunnerError):
        resumed.store("MIL01")
    assert executed == [f"{plan['run_id']}-MIL01-2026-09-01"]  # the finished origin is kept
    assert json.loads(first.read_text()) == result


def test_a_replay_never_resumes_a_record_workspace(tmp_path):
    plan = {"run_id": "p"}
    rolling.freeze_plan(tmp_path, plan, "record")
    rolling.freeze_plan(tmp_path, plan, "record")  # resume
    with pytest.raises(rolling.RunnerError, match="not created by a replay run"):
        rolling.freeze_plan(tmp_path, plan, "replay")
    with pytest.raises(rolling.RunnerError, match="plan differs"):
        rolling.freeze_plan(tmp_path, {"run_id": "q"}, "record")


def test_forecast_protocols_group_stores_by_their_origin_instants():
    def origins(zone):
        return [
            o.isoformat()
            for o in rolling.origins(date(2026, 10, 24), date(2026, 10, 26), zone, time(20))
        ]

    zones = {"MIL01": "Europe/Rome", "MUN01": "Europe/Berlin", "NYC01": "America/New_York"}
    plan = {
        "run_id": "r",
        "split": "dev",
        "stores": {s: {"origins": origins(z), "timezone": z} for s, z in zones.items()},
        "model_versions": {"chat": "m"},
        "code_version": "c",
        "origin_time": "20:00",
        "start": "2026-10-24",
        "end": "2026-10-26",
        "modules": [],
        "module_versions": {},
        "params": {},
        "investigate_per_origin": 0,
        "prompt_versions": {},
        "config": {},
        "llm_scope": {},
        "reading": {"files": ["MIL01/x.eml"]},
    }
    forecast = [
        {"payload": {"producer": "fc.baseline", "store_id": s, "sku": "J1-999"}} for s in zones
    ]

    lead, protocols = rolling.protocol_skeletons(plan, {"forecast": forecast}, {})

    assert len(lead["origins"]) == 6 and lead["universe"] == [
        {"store_id": s, "sku": "*"} for s in sorted(zones)
    ]
    assert sorted(protocols) == ["MIL01-MUN01", "NYC01"]
    for protocol in protocols.values():
        stores = protocol["stores"]
        assert {u["store_id"] for u in protocol["universe"]} == set(stores)
        assert all(protocol["origins"] == plan["stores"][s]["origins"] for s in stores)
        assert len(set(protocol["origins"])) == len(protocol["origins"]) == 3
