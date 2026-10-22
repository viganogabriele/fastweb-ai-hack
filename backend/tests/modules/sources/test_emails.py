"""src.email: real dev mailboxes match the DATA-01a fixtures; synthetic ones cover the edges."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tessera.core.contracts import ModuleSnapshot, RunSpec, Segment, SourceDocument
from tessera.core.db import connect
from tessera.core.orchestrator import run
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.sources import emails
from tessera.modules.sources.emails import MANIFEST, collect

ROOT = Path(__file__).resolve().parents[4]
SOURCES = ROOT / "generated" / "sources"
FIXTURES = ROOT / "data" / "fixtures" / "documents"


def spec(stores, as_of, run_id="email-run"):
    return RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=as_of,
        stores=tuple(stores),
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode="live",
        modules=(ModuleSnapshot(manifest=MANIFEST, params={}),),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def execute(tmp_path, request, sources_dir=SOURCES):
    engine = connect(f"sqlite:///{tmp_path / 'emails.db'}")
    registry = Registry(
        (RegisteredModule(MANIFEST, lambda ctx: emails.run(ctx, sources_dir=sources_dir)),)
    )
    statuses = run(request, engine=engine, registry=registry, clients={})
    return engine, statuses[0]


def test_registry_discovers_src_email():
    assert MANIFEST in Registry.discover().manifests()


def test_dev_mailboxes_match_data01a_fixtures():
    batch = collect(SOURCES, ["MIL01", "NYC01"], datetime(2026, 10, 22, 23, 59, tzinfo=UTC))
    produced = {document.id: (document, segments) for document, segments in batch.documents}
    fixtures = sorted(FIXTURES.glob("*.json"))
    assert fixtures
    for path in fixtures:
        items = json.loads(path.read_text())
        expected = next(i["payload"] for i in items if i["kind"] == "SourceDocument")
        document, segments = produced[expected["id"]]
        actual = document.model_dump(mode="json")
        expected_meta = {k: v for k, v in expected.pop("meta").items() if k != "fixture_case"}
        assert {k: actual["meta"][k] for k in expected_meta} == expected_meta
        assert {k: actual[k] for k in expected} == expected
        assert [s.model_dump(mode="json") for s in segments] == [
            i["payload"] for i in items if i["kind"] == "Segment"
        ]


def test_run_publishes_only_mails_available_at_as_of(tmp_path):
    as_of = datetime(2026, 10, 1, 20, 0, tzinfo=UTC)
    request = spec(["MIL01"], as_of)
    engine, status = execute(tmp_path, request)
    assert status.status == "succeeded"
    counts = status.result.counts
    assert counts["documents"] > 0 and counts["after_as_of"] > 0
    with repo_session(engine, request) as repo:
        documents = repo.list(SourceDocument)
        assert len(documents) == counts["documents"]
        assert len(repo.list(Segment)) == counts["segments"]
        assert all(d.available_at <= as_of for d in documents)
        assert {d.meta["store_id"] for d in documents} == {"MIL01"}
        assert repo.run_state()["published"]
    engine.dispose()


def eml(message_id, date, body, *, in_reply_to=None, subject="chiusura"):
    headers = [
        "From: Store <mil01.store@moncler-retail.example>",
        "To: hq@moncler-retail.example",
        f"Subject: {subject}",
        f"Message-ID: {message_id}",
        "Content-Type: text/plain; charset=utf-8",
    ]
    if date:
        headers.append(f"Date: {date}")
    if in_reply_to:
        headers.append(f"In-Reply-To: {in_reply_to}")
        headers.append(f"References: {in_reply_to}")
    return ("\r\n".join(headers) + "\r\n\r\n" + body + "\r\n").encode()


@pytest.fixture
def sources(tmp_path):
    root = tmp_path / "sources"
    (root / "erp" / "master_data").mkdir(parents=True)
    (root / "erp" / "master_data" / "stores.csv").write_text(
        "store_id,language,timezone\nMIL01,it,Europe/Rome\nPAR01,fr,Europe/Paris\n"
        "NYC01,en,America/New_York\n"
    )
    mil, par = root / "store_emails" / "MIL01", root / "store_emails" / "PAR01"
    mil.mkdir(parents=True)
    par.mkdir(parents=True)
    # Reply sorts first by name but is sent later: the parent must still be resolved.
    (mil / "a_reply.eml").write_bytes(
        eml("<r@x>", "Fri, 02 Oct 2026 22:30:00 +0200", "Re: ok", in_reply_to="<p@x>")
    )
    (mil / "b_parent.eml").write_bytes(eml("<p@x>", "Fri, 02 Oct 2026 21:00:00 +0200", "Ciao"))
    (mil / "c_undated.eml").write_bytes(eml("<u@x>", None, "senza data"))
    (mil / "d_future.eml").write_bytes(eml("<f@x>", "Sat, 03 Oct 2026 21:00:00 +0200", "dopo"))
    (par / "other.eml").write_bytes(eml("<o@x>", "Fri, 02 Oct 2026 21:00:00 +0200", "Salut"))
    return root


def test_replies_undated_future_and_other_stores(tmp_path, sources):
    as_of = datetime(2026, 10, 2, 23, 0, tzinfo=UTC)
    request = spec(["MIL01", "NYC01"], as_of)
    engine, status = execute(tmp_path, request, sources)
    result = status.result
    assert status.status == "degraded"
    assert result.counts == {"documents": 2, "segments": 2, "after_as_of": 1, "skipped": 1}
    assert result.abstentions == (
        "dataset://store_emails/MIL01/c_undated.eml: no usable Date header",
    )
    assert result.errors == ("no mailbox for store NYC01",)
    with repo_session(engine, request) as repo:
        documents = {d.id: d for d in repo.list(SourceDocument)}
        assert set(documents) == {"doc-a-reply", "doc-b-parent"}
        assert documents["doc-a-reply"].parent_document_id == "doc-b-parent"
        assert documents["doc-a-reply"].thread_key == "<p@x>"
        assert documents["doc-b-parent"].business_date.isoformat() == "2026-10-02"
        assert documents["doc-b-parent"].language == "it"
    engine.dispose()
