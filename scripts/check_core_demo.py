"""Verify a published dev candidate through the real repository and HTTP API.

The optional decision output exercises a scripted, explicitly synthetic reviewer
command. It never dispatches stock or messages and does not claim operator approval.
All checks run with networking denied, including the decision's stock revalidation.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from fastapi.testclient import TestClient
from replay_demo import (
    FrozenDecision,
    allowed,
    digest,
    environment,
    offline,
    semantic_payload,
)

from tesseract.api.main import create_app
from tesseract.api.routers.options import decision_clock
from tesseract.core.config import Settings
from tesseract.core.contracts import (
    ActionOption,
    AgentTrace,
    Case,
    Clarification,
    ContextEvent,
    EvidenceRelation,
    ForecastAdjustment,
    MetricFact,
    Observation,
    Segment,
    SourceDocument,
)
from tesseract.core.db import connect
from tesseract.core.repo import KINDS, latest
from tesseract.core.run_repo import repo_session
from tesseract.modules.actions.approval import DecisionRequest, LocalDraft


def decision_export(spec, *, at, request, draft):
    """Export the returned draft verbatim; never reconstruct its identity from a request."""
    return FrozenDecision(
        snapshot_sha256=digest(spec.model_dump(mode="json")),
        namespace="fixture" if spec.mode == "fixture" else "product",
        at=at,
        request=DecisionRequest.model_validate(request),
        draft=LocalDraft.model_validate(draft),
    ).model_dump(mode="json")


def input_inventory(root):
    return digest(
        [
            (
                p.relative_to(root).as_posix(),
                hashlib.sha256(allowed(p).read_bytes()).hexdigest(),
            )
            for p in sorted(root.rglob("*"))
            if not p.is_dir()
        ]
    )


def check(candidate, *, decision_output=None):
    candidate = allowed(candidate)
    # Refuse before sending a decision command, including an idempotent retry.
    if decision_output is not None and allowed(decision_output).exists():
        raise ValueError("decision export already exists; preserve the original exact draft")
    execution_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True
    ).strip()
    code_roots = ("backend/tesseract", "backend/prompts", "scripts")
    dirty_code = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all", "--", *code_roots],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
        )
    )
    settings = Settings(
        _env_file=None,
        llm_mode="replay",
        sources_dir=candidate / "sources",
        config_dir=candidate / "config",
        data_dir=candidate / "runtime",
        fastweb_keys_file=candidate / "no-credentials.json",
    )
    engine = connect(settings.db_url)
    fixture = connect("sqlite://")
    try:
        from tesseract.core.contracts import RunSpec

        spec = RunSpec.model_validate_json((candidate / "run-spec.json").read_text())
        assert spec.mode == "recorded" and not spec.authorized_fixture_refs
        assert input_inventory(candidate / "sources") == spec.source_manifest_hash
        assert input_inventory(candidate / "config") == spec.config_hash
        app = create_app(engine=engine, fixture_engine=fixture, settings=settings)
        app.dependency_overrides[decision_clock] = lambda: spec.as_of + timedelta(minutes=1)
        with offline() as denied, environment(settings), TestClient(app) as api:
            prefix = f"/api/runs/{spec.run_id}"

            def get(path, **params):
                response = api.get(prefix + path, params=params)
                assert response.status_code == 200, (path, response.status_code)
                return response.json()

            state = get("")
            assert state["published"] and state["status"] in {"succeeded", "degraded"}
            assert all(not (m.get("result") or {}).get("errors") for m in state["module_runs"])
            assert api.get(prefix + "/cases", params={"fixture": True}).status_code == 403
            assert api.get("/api/runs/not-this-run/cases").status_code == 404
            assert api.get(prefix + "/cases/not-this-case/options").status_code == 404
            with repo_session(engine, spec.run_id) as repo:
                assert repo.spec == spec, "published snapshot differs from candidate RunSpec"
                documents = repo.list(SourceDocument)
                observations = repo.list(Observation)
                cases = latest(repo.list(Case))
                traces = repo.list(AgentTrace)
                clarifications = repo.list(Clarification)
                assert documents and observations and cases and traces
                quotes = 0
                for observation in observations:
                    assert observation.store_id in spec.stores
                    assert observation.available_at <= spec.as_of
                    for evidence in observation.evidence:
                        doc = repo.get(
                            SourceDocument,
                            evidence.document_id,
                            evidence.document_version,
                        )
                        segment = repo.get(Segment, evidence.segment_id)
                        assert doc and segment
                        evidence.validate_against(doc, segment)
                        quotes += 1
                negative_ids = {d.id for d in documents if "ooo" in d.id}
                assert negative_ids and not any(o.document_id in negative_ids for o in observations)
                assert any(c.scope_level == "unknown" and c.status == "verify" for c in cases)
                assert (
                    repo.list(MetricFact)
                    and repo.list(ContextEvent)
                    and repo.list(EvidenceRelation)
                )
                for option in repo.list(ActionOption):
                    for ref in option.input_refs:
                        if ref.kind in KINDS:
                            assert repo.get(KINDS[ref.kind], ref.id, ref.version) is not None
                for case in cases:
                    exact = get(f"/cases/{case.id}", version=case.version)
                    assert exact["version"] == case.version and exact["run_id"] == spec.run_id
                    assert (
                        api.get(
                            prefix + f"/cases/{case.id}", params={"version": "absent"}
                        ).status_code
                        == 404
                    )
                for trace in traces:
                    assert trace.mode == "recorded"
                    assert trace.steps[0].tool == "get_case_evidence"
                    exact = get(
                        f"/cases/{trace.case_id}/traces/{trace.id}",
                        version=trace.version,
                    )
                    assert exact == trace.model_dump(mode="json")
                for clarification in clarifications:
                    assert clarification.status == "draft" and clarification.simulated
                    for ref in clarification.observation_refs:
                        assert repo.get(Observation, ref.id, ref.version) is not None
                    exact = get(
                        f"/cases/{clarification.case_id}/clarifications/{clarification.id}",
                        version=clarification.version,
                    )
                    assert exact == clarification.model_dump(mode="json")
                forecasts = repo.list(ForecastAdjustment)
                reports = get("/reports")
                assert forecasts and reports
                for owner in {c.owner for c in cases}:
                    details = get(f"/reports/{owner}")
                    assert details
                result = {
                    "format": 2,
                    "execution_sha": execution_sha,
                    "execution_has_dirty_code": dirty_code,
                    "snapshot_code_version": spec.code_version,
                    "snapshot_sha256": digest(spec.model_dump(mode="json")),
                    "namespace": repo.namespace,
                    "scenario_id": spec.scenario_id,
                    "source_manifest_hash": spec.source_manifest_hash,
                    "config_hash": spec.config_hash,
                    "artifact_inventory_sha256": digest(
                        [
                            (
                                kind,
                                item.id,
                                item.version,
                                digest(semantic_payload(kind, item.model_dump(mode="json"))),
                            )
                            for kind, model in sorted(KINDS.items())
                            for item in sorted(repo.list(model), key=lambda x: (x.id, x.version))
                        ]
                    ),
                    "artifact_inventory_scope": "published projection before optional decision",
                    "run_id": spec.run_id,
                    "status": "passed",
                    "documents": len(documents),
                    "observations": len(observations),
                    "verified_quotes": quotes,
                    "cases": len(cases),
                    "traces": len(traces),
                    "clarification_drafts": len(clarifications),
                    "reports": len(reports),
                    "negative_documents": len(negative_ids),
                    "evidence_relation_counts": dict(
                        Counter(relation.relation for relation in repo.list(EvidenceRelation))
                    ),
                    "trace_tools": {t.case_id: [s.tool for s in t.steps] for t in traces},
                    "trace_fallbacks": {t.case_id: t.fallback_used for t in traces},
                }
                choices = [
                    o
                    for o in latest(repo.list(ActionOption))
                    if o.recommended
                    and o.kind in {"hold", "notify_owner", "ask_store", "verify_stock"}
                ]
            if decision_output is not None:
                assert choices
                option = choices[0]
                path = f"/cases/{option.case_id}/decisions"
                body = {
                    "option_id": option.id,
                    "input_version_hash": option.input_version_hash,
                    "decision": "approved",
                    "by": "DEMO-02 scripted synthetic reviewer",
                    "idempotency_key": "demo02-explicit-local-command",
                    "note": "Integration rehearsal; no actual operator or external dispatch.",
                }
                stale = api.post(
                    prefix + path,
                    json={
                        **body,
                        "input_version_hash": "stale",
                        "idempotency_key": "demo02-stale",
                    },
                )
                assert stale.status_code == 409
                saved = api.post(prefix + path, json=body)
                assert saved.status_code == 200, saved.text
                draft = saved.json()
                assert draft["simulated"] and draft["decision"]["dispatch_status"] == "draft"
                assert draft["reservations"] == []
                assert api.post(prefix + path, json=body).json() == draft
                # The stale attempt saved nothing; the retry is read back once, exactly.
                assert get("/decisions") == get("/decisions", case_id=option.case_id) == [draft]
                assert get(f"/decisions/{draft['decision']['id']}") == draft
                output = allowed(decision_output)
                encoded = (
                    json.dumps(
                        [
                            decision_export(
                                spec,
                                at=spec.as_of + timedelta(minutes=1),
                                request={
                                    "run_id": spec.run_id,
                                    "scenario_id": spec.scenario_id,
                                    **body,
                                },
                                draft=draft,
                            )
                        ],
                        sort_keys=True,
                        indent=2,
                    )
                    + "\n"
                )
                with output.open("x") as stream:
                    stream.write(encoded)
                result["decision"] = {
                    "stale_status": stale.status_code,
                    "idempotent": True,
                    "dispatch_status": "draft",
                    "synthetic_reviewer": True,
                }
            result["network_attempts"] = len(denied)
            assert not denied
        path = candidate / "api-verification.json"
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        print(json.dumps(result, sort_keys=True))
    finally:
        engine.dispose()
        fixture.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--decision-output", type=Path)
    args = parser.parse_args()
    check(args.candidate, decision_output=args.decision_output)


if __name__ == "__main__":
    main()
