"""Verify a published dev candidate through the real repository and HTTP API.

The optional decision output exercises a scripted, explicitly synthetic reviewer
command. It never dispatches stock or messages and does not claim operator approval.
All checks run with networking denied, including the decision's stock revalidation.
"""

import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from fastapi.testclient import TestClient
from replay_demo import allowed, digest, environment, offline

from tessera.api.main import create_app
from tessera.api.routers.options import decision_clock
from tessera.core.config import Settings
from tessera.core.contracts import (
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
from tessera.core.db import connect
from tessera.core.repo import KINDS, latest
from tessera.core.run_repo import repo_session


def check(candidate, *, decision_output=None):
    candidate = allowed(candidate)
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
        from tessera.core.contracts import RunSpec

        spec = RunSpec.model_validate_json((candidate / "run-spec.json").read_text())
        assert spec.mode == "recorded" and not spec.authorized_fixture_refs
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
                            SourceDocument, evidence.document_id, evidence.document_version
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
                for trace in traces:
                    assert trace.mode == "recorded"
                    assert trace.steps[0].tool == "get_case_evidence"
                    exact = get(f"/cases/{trace.case_id}/traces/{trace.id}", version=trace.version)
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
                    "format": 1,
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
                    json={**body, "input_version_hash": "stale", "idempotency_key": "demo02-stale"},
                )
                assert stale.status_code == 409
                saved = api.post(prefix + path, json=body)
                assert saved.status_code == 200, saved.text
                draft = saved.json()
                assert draft["simulated"] and draft["decision"]["dispatch_status"] == "draft"
                assert draft["reservations"] == []
                assert api.post(prefix + path, json=body).json() == draft
                output = allowed(decision_output)
                encoded = (
                    json.dumps(
                        [
                            {
                                "snapshot_sha256": digest(spec.model_dump(mode="json")),
                                "namespace": "product",
                                "at": (spec.as_of + timedelta(minutes=1)).isoformat(),
                                "request": {
                                    "run_id": spec.run_id,
                                    "scenario_id": spec.scenario_id,
                                    **body,
                                },
                                "draft": draft,
                            }
                        ],
                        sort_keys=True,
                        indent=2,
                    )
                    + "\n"
                )
                if output.exists() and output.read_text() != encoded:
                    raise ValueError("decision output differs from the frozen command")
                if not output.exists():
                    output.write_text(encoded)
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
