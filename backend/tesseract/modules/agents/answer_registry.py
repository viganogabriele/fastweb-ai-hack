"""Durable simulated source events and follow-up jobs (OUT-02b).

The platform HTTP adapter calls submit_answer, then queues execute_follow_up.
Only trusted recording import code may call register_recorded_answer. Neither
function sends messages. Tables have no projection foreign keys, like the action
ledger: reset_run must not erase human input or its exact parent lineage.
"""

from dataclasses import replace
from threading import Event
from typing import Literal

from sqlalchemy import (
    JSON,
    Column,
    Engine,
    MetaData,
    String,
    Table,
    and_,
    insert,
    inspect,
    select,
    update,
)

from tesseract.core.cache import CacheCorrupt, ReplayMiss
from tesseract.core.config import Settings
from tesseract.core.contracts import (
    ArtifactRef,
    Case,
    Clarification,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tesseract.core.contracts.common import Contract, DerivedRecord, Instant, Text
from tesseract.core.db import runs
from tesseract.core.orchestrator import run
from tesseract.core.registry import RegisteredModule, Registry
from tesseract.core.repo import KINDS
from tesseract.core.run_repo import RunRepo
from tesseract.modules.agents.clarifications import (
    InvalidAnswer,
    SimulatedAnswer,
    UnrecordedAnswer,
    prepare_answer,
)
from tesseract.modules.agents.contextual_answers import ContextualExtraction

metadata = MetaData()
events = Table(
    "clarification_answer_events",
    metadata,
    Column("namespace", String, primary_key=True),
    Column("fingerprint", String, primary_key=True),
    Column("payload", JSON, nullable=False),
    Column("replay_ready", String, nullable=False),
)
jobs = Table(
    "clarification_answer_jobs",
    metadata,
    Column("namespace", String, primary_key=True),
    Column("idempotency_key", String, primary_key=True),
    Column("run_id", String, unique=True, nullable=False),
    Column("request", JSON, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("status", String, nullable=False),
)
receipts = Table(
    "clarification_answer_receipts",
    metadata,
    Column("namespace", String, primary_key=True),
    Column("idempotency_key", String, primary_key=True),
    Column("request", JSON, nullable=False),
    Column("payload", JSON, nullable=False),
)
_REQUIRED = {"ing.extract", "int.link", "fc.overlay", "act.options"}


class AnswerConflict(ValueError):
    """Stale state or conflicting retry; platform maps to HTTP 409."""

    status_code = 409


class AnswerUnavailable(LookupError):
    """Missing parent/source/job or unsupported pipeline; map to HTTP 503."""

    status_code = 503


class AnswerRequest(Contract):
    run_id: Text
    scenario_id: Text
    case_id: Text
    case_version: Text
    clarification_id: Text
    clarification_version: Text
    text: Text
    received_at: Instant
    language: Text | None = None
    follow_up_scenario_id: Text
    as_of: Instant
    idempotency_key: Text


class AnswerJob(Contract):
    fingerprint: Text
    run: RunSpec
    document: SourceDocument
    simulated: Literal[True] = True


def _namespace(fixture_mode):
    return "fixture" if fixture_mode else "product"


def _key(table, ns, **values):
    return and_(table.c.namespace == ns, *(table.c[k] == v for k, v in values.items()))


def _open(conn, run_id, fixture_mode):
    spec = conn.execute(select(runs.c.spec).where(runs.c.run_id == run_id)).scalar()
    if spec is None or (spec["mode"] == "fixture") != fixture_mode:
        raise AnswerUnavailable("Run not found in the selected namespace")
    return RunRepo(conn, RunSpec.model_validate(spec), fixture_mode=fixture_mode)


def _load(parent, kind, id, version=None):
    record = parent.get(kind, id, version)
    if record is None:
        raise AnswerUnavailable(f"Missing visible {kind.__name__} version")
    return record


def _closure(parent, roots):
    """Topologically ordered exact lineage, including evidence segments.

    ERP refs remain refs to the shared, availability-filtered source tables.
    All artifact dependencies are copied explicitly, never read across runs by
    downstream modules. Cycles/unresolvable refs fail before accepting input.
    """
    ordered, visiting, seen = [], set(), set()

    def references(value):
        if isinstance(value, ArtifactRef):
            yield value
        elif isinstance(value, Contract):
            for field in type(value).model_fields:
                yield from references(getattr(value, field))
        elif isinstance(value, (tuple, list)):
            for item in value:
                yield from references(item)

    def visit(ref):
        if ref.kind.startswith("erp.") or ref.kind == "ForecastVintage":
            return  # RunRepo validates these against the child's filtered ERP view.
        if ref in seen:
            return
        if ref in visiting:
            raise InvalidAnswer("Cyclic parent artifact lineage")
        kind = KINDS.get(ref.kind)
        if kind is None:
            raise AnswerUnavailable("Unsupported parent reference")
        record = _load(parent, kind, ref.id, ref.version)
        visiting.add(ref)
        # Include supporting/contradicting/context and observation_refs, not
        # just input_refs. Raw JSON source metadata remains original provenance.
        for dependency in references(record):
            visit(dependency)
        if isinstance(record, Observation):
            for evidence in record.evidence:
                # Real extractor observations cite the segment in input_refs;
                # require its exact version there rather than guessing one.
                matches = [
                    r
                    for r in record.input_refs
                    if r.kind == "Segment" and r.id == evidence.segment_id
                ]
                if len(matches) != 1:
                    raise AnswerUnavailable("Evidence segment version is not explicitly referenced")
                visit(matches[0])
        if isinstance(record, Segment):
            docs = parent.list(
                SourceDocument,
                where={"id": record.document_id, "text_version": record.text_version},
            )
            if len(docs) != 1:
                raise AnswerUnavailable("Ambiguous segment document version")
            visit(ArtifactRef(kind="SourceDocument", id=docs[0].id, version=docs[0].version))
        visiting.remove(ref)
        seen.add(ref)
        ordered.append(record)

    for root in roots:
        visit(root)
    return ordered


def _prepare(conn, request, fixture_mode):
    parent = _open(conn, request.run_id, fixture_mode)
    if not parent.run_state()["published"]:
        raise AnswerConflict("Parent run must be published")
    if parent.spec.scenario_id != request.scenario_id:
        raise InvalidAnswer("Parent scenario mismatch")
    newest = conn.execute(
        select(runs.c.run_id)
        .where(
            runs.c.scenario_id == request.scenario_id,
            runs.c.status == "published",
            (runs.c.spec["mode"].as_string() == "fixture") == fixture_mode,
        )
        .order_by(runs.c.created_at.desc())
        .limit(1)
    ).scalar()
    if newest != parent.run_id:
        raise AnswerConflict("Parent is no longer the current published run of this scenario")
    case = _load(parent, Case, request.case_id)
    question = _load(parent, Clarification, request.clarification_id)
    if (case.version, question.version) != (request.case_version, request.clarification_version):
        raise AnswerConflict("Case or clarification version changed")
    if question.case_id != case.id:
        raise InvalidAnswer("Clarification belongs to another case")
    observations = [_load(parent, Observation, r.id, r.version) for r in question.observation_refs]
    doc_refs = {(e.document_id, e.document_version) for o in observations for e in o.evidence}
    documents = [_load(parent, SourceDocument, id, version) for id, version in sorted(doc_refs)]
    prepared = prepare_answer(
        parent.spec,
        case,
        question,
        observations,
        documents,
        SimulatedAnswer(request.text, request.received_at, request.language),
        scenario_id=request.follow_up_scenario_id,
        as_of=request.as_of,
        replay=False,
    )
    active = {
        s.manifest.id
        for s in prepared.run.modules
        if s.manifest.enabled and s.manifest.mode != "unavailable"
    }
    if not _REQUIRED <= active:
        raise AnswerUnavailable("Follow-up requires extraction, linking, forecast and options")
    for snapshot in prepared.run.modules:
        if snapshot.manifest.id in active and not set(snapshot.manifest.requires) <= active:
            raise AnswerUnavailable("Follow-up has a missing or disabled required module")
    inherited = tuple(
        ArtifactRef(kind="Observation", id=o.id, version=o.version)
        for o in parent.list(Observation)
        if o.producer == "ag.contextual_answer" and not o.version.startswith("parent:")
    )
    seeds = _closure(parent, (*prepared.seed_refs, *inherited))
    return prepared, seeds


def _encode(record):
    return {"kind": type(record).__name__, "payload": record.model_dump(mode="json")}


def _payload(prepared, seeds):
    return {
        "job": AnswerJob(
            fingerprint=prepared.fingerprint, run=prepared.run, document=prepared.document
        ).model_dump(mode="json"),
        "seeds": [_encode(r) for r in seeds],
        "segment": prepared.segment.model_dump(mode="json"),
        "clarification": prepared.clarification.model_dump(mode="json"),
    }


def _same_request(left, right):
    def identity(value):
        return {
            k: v.replace("\r\n", "\n").replace("\r", "\n") if k == "text" else v
            for k, v in value.items()
            if k != "idempotency_key"
        }

    return identity(left) == identity(right)


def register_recorded_answer(engine: Engine, request: AnswerRequest, *, fixture_mode=False):
    """Trusted importer seam, NEVER an HTTP/free-text registration endpoint.

    Call only for an accepted event whose required model/tool responses have
    been recorded for this snapshot. A fingerprint alone is not a recording.
    Live submissions never call this implicitly.
    """
    ns = _namespace(fixture_mode)
    with engine.begin() as conn:
        conn.exec_driver_sql("BEGIN IMMEDIATE")
        metadata.create_all(conn)
        prepared, seeds = _prepare(conn, request, fixture_mode)
        key = _key(events, ns, fingerprint=prepared.fingerprint)
        saved = conn.execute(select(events).where(key)).mappings().first()
        if saved is None:
            conn.execute(
                insert(events).values(
                    namespace=ns,
                    fingerprint=prepared.fingerprint,
                    payload=_payload(prepared, seeds),
                    replay_ready="yes",
                )
            )
        else:
            conn.execute(update(events).where(key).values(replay_ready="yes"))
        return prepared.fingerprint


def submit_answer(
    engine: Engine, request: AnswerRequest, *, fixture_mode=False, registry: Registry | None = None
) -> AnswerJob:
    """Atomically persist input + lineage + pending run + job, with idempotent retries.

    Mode comes from the immutable parent, never the HTTP caller. Offline runs
    require a trusted registered recording. Live answers stay non-replayable.
    The API must authorize fixture_mode separately and queue the returned run ID
    with execute_follow_up after this transaction commits (202).
    """
    ns = _namespace(fixture_mode)
    registry = registry if registry is not None else Registry.discover()
    with engine.begin() as conn:
        conn.exec_driver_sql("BEGIN IMMEDIATE")
        metadata.create_all(conn)
        key = _key(receipts, ns, idempotency_key=request.idempotency_key)
        saved = conn.execute(select(receipts).where(key)).mappings().first()
        encoded = request.model_dump(mode="json")
        if saved:
            if saved["request"] != encoded:
                raise AnswerConflict("Idempotency key used for another request")
            return AnswerJob.model_validate(saved["payload"]["job"])
        # A retry with a new key must not depend on reconstructible parent state.
        # Consult the accepted immutable request before revalidating a new input.
        candidates = conn.execute(
            select(jobs).where(
                jobs.c.namespace == ns,
                jobs.c.request["run_id"].as_string() == request.run_id,
                jobs.c.request["clarification_id"].as_string() == request.clarification_id,
            )
        ).mappings()
        for candidate in candidates:
            if _same_request(candidate["request"], encoded):
                conn.execute(
                    insert(receipts).values(
                        namespace=ns,
                        idempotency_key=request.idempotency_key,
                        request=encoded,
                        payload=candidate["payload"],
                    )
                )
                return AnswerJob.model_validate(candidate["payload"]["job"])
        prepared, seeds = _prepare(conn, request, fixture_mode)
        for snapshot in prepared.run.modules:
            if snapshot.manifest.enabled and snapshot.manifest.mode != "unavailable":
                registry.resolve(snapshot)
        event_key = _key(events, ns, fingerprint=prepared.fingerprint)
        event = conn.execute(select(events).where(event_key)).mappings().first()
        if prepared.run.mode != "live" and (event is None or event["replay_ready"] != "yes"):
            raise UnrecordedAnswer("No registered answer recording for this exact parent and event")
        payload = _payload(prepared, seeds)
        # A different retry key for the identical deterministic job is harmless.
        existing = (
            conn.execute(select(jobs).where(jobs.c.run_id == prepared.run.run_id))
            .mappings()
            .first()
        )
        if existing:
            conn.execute(
                insert(receipts).values(
                    namespace=ns,
                    idempotency_key=request.idempotency_key,
                    request=encoded,
                    payload=existing["payload"],
                )
            )
            return AnswerJob.model_validate(existing["payload"]["job"])
        if conn.execute(select(runs.c.run_id).where(runs.c.run_id == prepared.run.run_id)).first():
            raise AnswerConflict("Follow-up run ID already exists outside the answer registry")
        if event is None:
            conn.execute(
                insert(events).values(
                    namespace=ns,
                    fingerprint=prepared.fingerprint,
                    payload=payload,
                    replay_ready="no",
                )
            )
        RunRepo(conn, prepared.run, fixture_mode=fixture_mode)
        conn.execute(
            insert(jobs).values(
                namespace=ns,
                idempotency_key=request.idempotency_key,
                run_id=prepared.run.run_id,
                request=encoded,
                payload=payload,
                status="pending",
            )
        )
        conn.execute(
            insert(receipts).values(
                namespace=ns,
                idempotency_key=request.idempotency_key,
                request=encoded,
                payload=payload,
            )
        )
        return AnswerJob.model_validate(payload["job"])


def _seed(repo, payload):
    job = AnswerJob.model_validate(payload["job"])
    records = [KINDS[r["kind"]].model_validate(r["payload"]) for r in payload["seeds"]]
    # Keep IDs usable for navigation, but put historical derived versions in a
    # separate namespace so freshly recomputed observations/cases cannot collide.
    versions = {
        (type(r).__name__, r.id, r.version): f"parent:{job.fingerprint}:{r.version}"
        for r in records
        if isinstance(r, DerivedRecord)
    }

    def remap(value):
        if isinstance(value, dict):
            if set(value) == {"kind", "id", "version"}:
                return {
                    **value,
                    "version": versions.get(
                        (value["kind"], value["id"], value["version"]), value["version"]
                    ),
                }
            return {k: remap(v) for k, v in value.items()}
        if isinstance(value, list):
            return [remap(v) for v in value]
        return value

    for record in records:
        data = record.model_dump(mode="json")
        if isinstance(record, DerivedRecord):
            data = remap(data)
            data.update(
                run_id=job.run.run_id,
                scenario_id=job.run.scenario_id,
                version=versions[(type(record).__name__, record.id, record.version)],
            )
        repo.put(type(record).model_validate(data))
    repo.put(job.document, Segment.model_validate(payload["segment"]))
    repo.put(Clarification.model_validate(remap(payload["clarification"])))
    return set(versions.values())


class _PipelineView:
    """Historical lineage stays resolvable, but is not fresh pipeline evidence."""

    def __init__(self, repo, historical):
        self._repo, self._historical = repo, historical

    def __getattr__(self, name):
        return getattr(self._repo, name)

    def list(self, kind, **filters):
        return [r for r in self._repo.list(kind, **filters) if r.version not in self._historical]

    def get(self, kind, id, version=None):
        record = self._repo.get(kind, id, version)
        if version is None and record is not None and record.version in self._historical:
            return None
        return record

    def contextual_history(self):
        return [
            o
            for o in self._repo.list(Observation)
            if o.version in self._historical and o.producer == "ag.contextual_answer"
        ]


class _RecordingGuard:
    """Notice cache misses even when a module catches them and degrades."""

    def __init__(self, client):
        self._client = client
        self.missing = Event()

    def __getattr__(self, name):
        value = getattr(self._client, name)
        if not callable(value):
            return value

        def call(*args, **kwargs):
            try:
                return value(*args, **kwargs)
            except (ReplayMiss, CacheCorrupt):
                self.missing.set()
                raise

        return call


def pending_follow_ups(engine: Engine, *, fixture_mode=False) -> tuple[AnswerJob, ...]:
    """Recover accepted jobs after a restart before a background task was queued."""
    with engine.connect() as conn:
        if not inspect(conn).has_table(jobs.name):
            return ()
        payloads = conn.execute(
            select(jobs.c.payload).where(_key(jobs, _namespace(fixture_mode), status="pending"))
        ).scalars()
        return tuple(AnswerJob.model_validate(p["job"]) for p in payloads)


def execute_follow_up(
    engine: Engine,
    run_id: str,
    *,
    fixture_mode=False,
    registry: Registry | None = None,
    clients=None,
    settings: Settings | None = None,
) -> AnswerJob:
    """Idempotent worker boundary; failed projections require explicit reset_run.

    Pending jobs can be enumerated from this durable table on process startup.
    A running job is never automatically stolen: after a worker crash, stop the
    old worker and reset its projection before retrying this same durable job.
    """
    ns = _namespace(fixture_mode)
    with engine.begin() as conn:
        conn.exec_driver_sql("BEGIN IMMEDIATE")
        metadata.create_all(conn)
        key = _key(jobs, ns, run_id=run_id)
        saved = conn.execute(select(jobs).where(key)).mappings().first()
        if saved is None:
            raise AnswerUnavailable("Answer job not found in this namespace")
        payload = saved["payload"]
        job = AnswerJob.model_validate(payload["job"])
        current_spec = conn.execute(select(runs.c.spec).where(runs.c.run_id == run_id)).scalar()
        if current_spec is not None and RunSpec.model_validate(current_spec) != job.run:
            raise AnswerConflict("Follow-up run ID now belongs to a different snapshot")
        projection = conn.execute(select(runs.c.status).where(runs.c.run_id == run_id)).scalar()
        if projection == "published":
            conn.execute(update(jobs).where(key).values(status="succeeded"))
            return job
        if projection not in {None, "pending"} or (
            saved["status"] == "running" and projection is not None
        ):
            raise AnswerConflict("Job already running or failed; reset its projection before retry")
        repo = RunRepo(conn, job.run, fixture_mode=fixture_mode)
        historical = _seed(repo, payload)
        conn.execute(update(jobs).where(key).values(status="running"))

    def wrap(entry):
        def execute(ctx):
            clients = dict(ctx.clients)
            guard = _RecordingGuard(clients["llm"]) if "llm" in clients else None
            if guard is not None:
                clients["llm"] = guard
            view = _PipelineView(ctx.repo, historical)
            contextual = None
            if entry.manifest.id == "ing.extract":
                contextual = ContextualExtraction(view, job, clients["llm"])
                view = contextual
            result = entry.run(replace(ctx, repo=view, clients=clients))
            if contextual is not None and result.status in {"succeeded", "degraded"}:
                contextual.finish()
            if guard is not None and guard.missing.is_set():
                # General pipeline modules may publish partial results as degraded.
                # An answer replay must fail closed instead of publishing unread input.
                return result.model_copy(
                    update={
                        "status": "failed",
                        "errors": (*result.errors, "Answer follow-up recording unavailable"),
                    }
                )
            return result

        return RegisteredModule(entry.manifest, execute)

    try:
        registry = registry if registry is not None else Registry.discover()
        wrapped = Registry(
            wrap(registry.resolve(s))
            for s in job.run.modules
            if s.manifest.enabled and s.manifest.mode != "unavailable"
        )
        results = run(job.run, engine=engine, registry=wrapped, clients=clients, settings=settings)
    except BaseException:
        with engine.begin() as conn:
            conn.exec_driver_sql("BEGIN IMMEDIATE")
            projection = conn.execute(select(runs.c.status).where(runs.c.run_id == run_id)).scalar()
            if projection in {"pending", "running"}:
                # Registry/client setup may fail before the orchestrator owns the
                # run lifecycle. Expose that failure through the normal RunView.
                repo = RunRepo(conn, job.run, fixture_mode=fixture_mode)
                repo.discard_artifacts()
                repo.set_run_status("failed")
            conn.execute(update(jobs).where(key).values(status="failed"))
        raise
    succeeded = all(r.status in {"succeeded", "degraded"} for r in results)
    with engine.begin() as conn:
        conn.execute(update(jobs).where(key).values(status="succeeded" if succeeded else "failed"))
    return job
