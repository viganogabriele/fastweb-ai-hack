"""REL-01d experiment record: synthetic temporary repositories only, no real data or keys."""

import hashlib
import importlib.util
import json
import subprocess

import pytest

from tesseract.core.config import REPO_ROOT

module_spec = importlib.util.spec_from_file_location(
    "freeze_record", REPO_ROOT / "scripts/freeze_record.py"
)
freeze_record = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(freeze_record)

from eval.harness import freeze  # noqa: E402  (importable once the script set sys.path)

SETTINGS = {"chat_model": "synthetic-chat", "fastweb_base_url": "https://example.invalid/v1"}
FILES = {
    ".gitignore": "data/\n",
    "docs/protocol.md": "# Synthetic protocol\n",
    "docs/audit.md": "# Synthetic gate audit\n",
    "backend/uv.lock": "version = 1\n",
    "backend/prompts/extract.v1.md": "Extract synthetic observations.\n",
    "config/aliases.yaml": "aliases: {}\n",
    "eval/__init__.py": "",
    "generated/sources/erp/master_data/stores.csv": "store_id,timezone\nMIL01,Europe/Rome\n",
    "generated/sources/erp/master_data/sku_colour.csv": "sku\nSYN-001\n",
    "generated/sources/erp/master_data/sku_size_ean.csv": "sku_size,sku\nSYN-001-M,SYN-001\n",
    "generated/sources/erp/inventory/store_stock_daily/stock_eod_2026-10-01.csv": "store_id\n",
    "generated/sources/store_emails/MIL01/20261001_2100_MIL01.eml": "Subject: synthetic\n",
}
EMAIL = "generated/sources/store_emails/MIL01/20261001_2100_MIL01.eml"


def envelope(response):
    canonical = json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    key = hashlib.sha256(json.dumps({"request": response}).encode()).hexdigest()
    checksum = hashlib.sha256(canonical.encode()).hexdigest()
    return key, {"version": 1, "key": key, "response": response, "checksum": checksum}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(freeze_record, "settings_identity", lambda: dict(SETTINGS))
    for name, text in FILES.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    # The harness validates protocol stores against the real split file.
    (tmp_path / "config/eval_split.yaml").write_text(
        (REPO_ROOT / "config/eval_split.yaml").read_text()
    )
    for kind, model in (("llm", "synthetic-chat"), ("systems", None)):
        key, data = envelope({"model": model} if model else {"status": 200})
        path = tmp_path / f"data/{kind}_cache/{key[:2]}/{key}.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data))
    for kind in ("predictions", "cases", "options"):
        rows = (
            [{"kind": "Observation", "payload": {"store_id": "MIL01"}}]
            if kind == "predictions"
            else []
        )
        (tmp_path / "data/exports").mkdir(parents=True, exist_ok=True)
        (tmp_path / f"data/exports/{kind}.json").write_text(json.dumps(rows))
    (tmp_path / "data/check.log").write_text("make check: passed\n")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run([*git, "add", "."], cwd=tmp_path, check=True)
    subprocess.run([*git, "commit", "-qm", "synthetic"], cwd=tmp_path, check=True)
    return tmp_path


def record_args(*extra, output="data/E/freeze-record.json"):
    return [
        "record", "--output", output, "--protocol", "docs/protocol.md",
        "--source", EMAIL, "--cache", "llm=data/llm_cache", "--cache", "systems=data/systems_cache",
        "--exports", "reading=data/exports", "--make-check-log", "data/check.log",
        "--gate-audit", "docs/audit.md", "--reviewer", "synthetic reviewer",
        "--approved-at", "2026-10-23T09:00:00+00:00", "--window", "2026-10-02", "2026-10-03",
        *extra,
    ]  # fmt: skip


def run(repo, argv):
    return freeze_record.main(argv, root=repo)


def load(repo, name="data/E/freeze-record.json"):
    return json.loads((repo / name).read_text())


def test_source_list_is_hashed_as_the_selection_manifest(repo):
    (repo / "data/sources.txt").write_text(f"{EMAIL}\n\n")
    argv = record_args("--source-list", "data/sources.txt")
    argv.remove("--source")
    argv.remove(EMAIL)
    assert run(repo, argv) == 0
    inputs = load(repo)["inputs"]
    assert [e["path"] for e in inputs["source_lists"]] == ["data/sources.txt"]
    assert [e["path"] for e in inputs["sources"]["files"]] == [EMAIL]


def test_record_binds_candidate_inputs_caches_and_exports(repo):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    assert run(repo, record_args("--candidate-sha", head)) == 0
    record = load(repo)
    assert record["candidate"]["sha"] == head and record["candidate"]["clean"]
    assert record["candidate"]["protocol"]["path"] == "docs/protocol.md"
    assert record["product_identity"]["settings"] == SETTINGS
    assert [e["path"] for e in record["lockfiles"]] == ["backend/uv.lock"]
    assert record["inputs"]["sources"]["files"][0]["source_relative"].startswith("store_emails/")
    evaluator = record["inputs"]["evaluator"]
    assert evaluator["split"]["path"] == "config/eval_split.yaml"
    stock = "generated/sources/erp/inventory/store_stock_daily/stock_eod_2026-10-01.csv"
    assert stock in {e["path"] for e in evaluator["inventory"]["files"]}
    assert (
        "generated/sources/erp/sales/daily_store_sku/sales_daily_2026_09.csv" in evaluator["absent"]
    )
    caches = {c["kind"]: c for c in record["caches"]["inventories"]}
    assert caches["llm"]["entries"] == 1 and caches["llm"]["models"] == {"synthetic-chat": 1}
    components = record["caches"]["components"]
    assert components["llm"]["status"] == "recorded"
    assert components["asr"]["status"] == "unavailable"
    predictions = next(e for e in record["exports"] if e["kind"] == "predictions")
    assert predictions["rows"] == 1 and predictions["by_kind"] == {"Observation": 1}
    assert predictions["by_store"] == {"MIL01": 1}
    assert record["post_freeze"]["label_receipts"] == {}
    assert ".secrets" not in json.dumps(record) and "api_key" not in json.dumps(record)


def test_record_is_append_only_and_refuses_unsafe_inputs(repo):
    assert run(repo, record_args()) == 0
    original = (repo / "data/E/freeze-record.json").read_bytes()
    assert run(repo, record_args()) == 2
    assert (repo / "data/E/freeze-record.json").read_bytes() == original
    assert run(repo, record_args(output="elsewhere/record.json")) == 2
    for extra in (
        ["--source", "generated/sources/store_emails/MIL01/x_notes.md"],
        ["--source", "generated/ground_truth/answers.csv"],
        ["--evidence", "labels=eval/labels/holdout.yaml"],
        ["--evidence", "env=.env"],
        ["--source-list", ".secrets/sources.txt"],
        ["--candidate-sha", "0" * 40],
        ["--label-sha", "holdout=not-a-digest"],
        ["--component", "asr=invented:reason"],
    ):
        assert run(repo, record_args(*extra, output="data/E/refused.json")) == 2, extra
    assert not (repo / "data/E/refused.json").exists()


def test_dirty_tree_needs_an_explicit_recorded_flag(repo):
    (repo / "config/aliases.yaml").write_text("aliases: {tuned: true}\n")
    assert run(repo, record_args()) == 2
    assert run(repo, record_args("--allow-dirty")) == 0
    candidate = load(repo)["candidate"]
    assert candidate["allow_dirty"] and not candidate["clean"]
    assert candidate["dirty_paths"] == ["config/aliases.yaml"]


def test_invalid_cache_envelope_and_input_manifest_drift_are_refused(repo):
    key, data = envelope({"model": "tampered"})
    data["response"]["model"] = "changed after recording"
    path = repo / f"data/llm_cache/{key[:2]}/{key}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data))
    assert run(repo, record_args()) == 2
    path.unlink()
    manifest = {"sources": [[EMAIL.removeprefix("generated/sources/"), "0" * 64]], "config": []}
    (repo / "data/input-manifest.json").write_text(json.dumps(manifest))
    assert run(repo, record_args("--input-manifest", "data/input-manifest.json")) == 2


def test_verify_detects_source_cache_and_availability_drift(repo, capsys):
    assert run(repo, record_args()) == 0
    chain = ["verify", "--record", "data/E/freeze-record.json"]
    assert run(repo, [*chain, "--output", "data/E/verify-1.json"]) == 0
    assert load(repo, "data/E/verify-1.json")["status"] == "ok"
    (repo / EMAIL).write_text("Subject: edited after the freeze\n")
    key, data = envelope({"model": "late"})
    (repo / f"data/llm_cache/{key[:2]}").mkdir(exist_ok=True)
    (repo / f"data/llm_cache/{key[:2]}/{key}.json").write_text(json.dumps(data))
    late = repo / "generated/sources/erp/sales/daily_store_sku/sales_daily_2026_10.csv"
    late.parent.mkdir(parents=True)
    late.write_text("business_date\n")
    capsys.readouterr()
    assert run(repo, chain) == 1
    drift = json.loads(capsys.readouterr().out)["drift"]
    assert f"changed: {EMAIL}" in drift
    assert f"added cache entry: data/llm_cache/{key[:2]}/{key}.json" in drift
    assert f"appeared: {late.relative_to(repo).as_posix()}" in drift


def test_append_binds_bundles_and_label_receipts_in_a_chain(repo, capsys):
    assert run(repo, record_args()) == 0
    protocol = {
        "run_id": "synthetic-dev",
        "split": "dev",
        "stores": ["MIL01"],
        "origins": ["2026-10-01T20:00:00+02:00"],
        "universe": [{"store_id": "MIL01", "sku": "SYN-001"}],
        "sampling_criterion": "synthetic",
        "models": {"chat": "synthetic-chat"},
        "parameters": {"threshold": 1},
    }
    exports = {k: repo / f"data/exports/{k}.json" for k in ("predictions", "cases", "options")}
    manifest = freeze(
        repo / "data/bundle", protocol, exports, [repo / EMAIL], [repo / "config/aliases.yaml"],
        root=repo,
    )  # fmt: skip
    receipt = "a" * 64
    addendum = [
        "append", "--record", "data/E/freeze-record.json", "--output", "data/E/addendum-1.json",
        "--bundle", f"data/bundle={manifest}", "--label-sha", f"reading_holdout={receipt}",
    ]  # fmt: skip
    assert run(repo, addendum) == 0
    added = load(repo, "data/E/addendum-1.json")
    assert added["bundles"][0]["manifest_sha256"] == manifest
    assert added["bundles"][0]["counts"] == {"predictions": 1, "cases": 0, "options": 0}
    assert added["post_freeze"]["label_receipts"] == {"reading_holdout": receipt}
    chain = ["verify", "--record", "data/E/freeze-record.json", "data/E/addendum-1.json"]
    assert run(repo, chain) == 0
    assert run(repo, ["verify", "--record", "data/E/addendum-1.json"]) == 2
    (repo / "data/bundle/predictions.json").write_text("[]")
    capsys.readouterr()
    assert run(repo, chain) == 1
    assert any("bundle data/bundle" in d for d in json.loads(capsys.readouterr().out)["drift"])
    assert (
        run(repo, [*addendum[:4], "data/E/wrong.json", "--bundle", "data/bundle=" + "0" * 64]) == 2
    )


def test_append_refuses_a_bundle_of_unrecorded_exports(repo):
    assert run(repo, record_args()) == 0
    (repo / "data/other").mkdir()
    for kind in ("predictions", "cases", "options"):
        (repo / f"data/other/{kind}.json").write_text('[{"kind": "tuned"}]')
    protocol = {
        "run_id": "synthetic-dev", "split": "dev", "stores": ["MIL01"],
        "origins": ["2026-10-01T20:00:00+02:00"], "universe": [{"store_id": "MIL01", "sku": "S"}],
        "sampling_criterion": "synthetic", "models": {"m": "x"}, "parameters": {"p": 1},
    }  # fmt: skip
    exports = {k: repo / f"data/other/{k}.json" for k in ("predictions", "cases", "options")}
    freeze(
        repo / "data/b2",
        protocol,
        exports,
        [repo / EMAIL],
        [repo / "config/aliases.yaml"],
        root=repo,
    )
    argv = ["append", "--record", "data/E/freeze-record.json", "--output", "data/E/a.json"]
    assert run(repo, [*argv, "--bundle", "data/b2"]) == 2
    assert not (repo / "data/E/a.json").exists()
