"""OUT-02a: pure preparation of simulated answers; persistence/job wiring is OUT-02b.

An answer is a new source event, not a correction to a published historical run.
The caller supplies exact source versions and a trusted replay allowlist. This
module never loads data, calls a provider, updates a repository or sends messages.
"""

import hashlib
import json
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import quote

from tesseract.core.contracts import (
    ArtifactRef,
    Case,
    Clarification,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
    SourceRef,
)

VERSION = "1"
CONNECTOR = "src.clarifications"


class InvalidAnswer(ValueError):
    """The supplied answer, scope or source lineage is not admissible."""


class UnrecordedAnswer(LookupError):
    """Replay has no registered answer for this exact question and answer event."""


@dataclass(frozen=True)
class SimulatedAnswer:
    text: str
    received_at: datetime
    language: str | None = None


@dataclass(frozen=True)
class PreparedAnswer:
    fingerprint: str
    document: SourceDocument
    segment: Segment
    clarification: Clarification
    run: RunSpec
    # These exact parent versions must be seeded/remapped before the new derived
    # clarification is persisted. They are references, not cross-run reads.
    seed_refs: tuple[ArtifactRef, ...]


def _ref(record) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def _hash(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _instant(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InvalidAnswer("Answer and follow-up timestamps must be timezone-aware")
    return value.astimezone(UTC)


def _visible(record, parent: RunSpec) -> None:
    if record.available_at is None or record.available_at > parent.as_of:
        raise InvalidAnswer("Every referenced source version must be visible in the parent run")
    if isinstance(record, (Case, Clarification, Observation)) and (
        record.run_id != parent.run_id or record.scenario_id != parent.scenario_id
    ):
        raise InvalidAnswer("Case, clarification and observations must belong to the parent run")


def answer_fingerprint(
    parent: RunSpec, clarification: Clarification, answer: SimulatedAnswer
) -> str:
    """Key for registering an answer before offline replay; never authorizes it itself.

    Identity includes the immutable question/run context, receipt time, language
    and canonical text. A recording for another case/question cannot authorize it.
    Scheduling the same recorded event at a later follow-up clock remains possible.
    """
    if not isinstance(answer.text, str) or not answer.text.strip():
        raise InvalidAnswer("A simulated answer needs nonempty text")
    if answer.language is not None and (
        not isinstance(answer.language, str) or not answer.language.strip()
    ):
        raise InvalidAnswer("Answer language must be nonempty when supplied")
    return _hash(
        {
            "version": VERSION,
            "parent": parent.model_dump(mode="json"),
            "clarification": clarification.model_dump(mode="json"),
            "text": answer.text.replace("\r\n", "\n").replace("\r", "\n"),
            "received_at": _instant(answer.received_at).isoformat(),
            "language": answer.language,
        }
    )


def prepare_answer(
    parent: RunSpec,
    case: Case,
    clarification: Clarification,
    observations: Sequence[Observation],
    documents: Sequence[SourceDocument],
    answer: SimulatedAnswer,
    *,
    scenario_id: str,
    as_of: datetime,
    replay: bool = True,
    registered_answers: Collection[str] = (),
) -> PreparedAnswer:
    """Prepare an isolated scenario; default replay fails closed on unregistered text.

    ``replay=False`` is an explicit live/record preparation path for a *simulated*
    human answer. It never calls an LLM. The integration must persist the source
    event durably and register its fingerprint before promising offline reuse.
    No observation quantity, product link, forecast or stock action is inferred.
    """
    as_of = _instant(as_of)
    received_at = _instant(answer.received_at)
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise InvalidAnswer("A nonempty follow-up scenario ID is required")
    if scenario_id == parent.scenario_id:
        raise InvalidAnswer("Simulated answers require a distinct declared scenario")
    if parent.mode == "unavailable":
        raise InvalidAnswer("An unavailable parent run cannot continue")
    for record in (case, clarification, *observations, *documents):
        _visible(record, parent)
    if case.store_id is None or case.store_id not in parent.stores:
        raise InvalidAnswer("The selected case must belong to a store in the parent run")
    if clarification.case_id != case.id:
        raise InvalidAnswer("Clarification must belong to the selected case")
    case_refs = {reference for reference in clarification.input_refs if reference.kind == "Case"}
    if case_refs != {_ref(case)}:
        raise InvalidAnswer("Supply exactly the case version referenced by the clarification")
    if case.status in {"closed", "decided"}:
        raise InvalidAnswer("A closed or decided case cannot accept a clarification answer")
    if clarification.status not in {"draft", "asked"}:
        raise InvalidAnswer("Clarification is already answered or cancelled")
    if clarification.asked_at > parent.as_of:
        raise InvalidAnswer("The question must already exist at the parent replay clock")
    if received_at <= max(parent.as_of, clarification.asked_at) or as_of < received_at:
        raise InvalidAnswer("Answer must follow the parent clock and be available by the new clock")

    expected = set(clarification.observation_refs)
    supplied = {_ref(observation): observation for observation in observations}
    related = {*case.input_refs, *case.supporting, *case.contradicting}
    if not expected or expected != supplied.keys() or len(supplied) != len(observations):
        raise InvalidAnswer("Supply exactly the clarification's observation versions")
    if not expected <= related:
        raise InvalidAnswer("Clarification observations must be linked to the selected case")
    if any(observation.store_id != case.store_id for observation in observations):
        raise InvalidAnswer("Clarification observations must belong to the selected store")
    parents = {(document.id, document.version): document for document in documents}
    required = {(e.document_id, e.document_version) for obs in observations for e in obs.evidence}
    if set(parents) != required or len(parents) != len(documents):
        raise InvalidAnswer("Supply exactly the documents backing the observation evidence")
    for observation in observations:
        for evidence in observation.evidence:
            document = parents[(evidence.document_id, evidence.document_version)]
            if document.meta.get("store_id") not in (None, case.store_id):
                raise InvalidAnswer("A backing document belongs to another store")
            if document.text[evidence.char_start : evidence.char_end] != evidence.quote:
                raise InvalidAnswer("Observation quote does not match its document version")

    fingerprint = answer_fingerprint(parent, clarification, answer)
    if replay and fingerprint not in registered_answers:
        raise UnrecordedAnswer("No registered simulated answer for this question and receipt time")
    text = answer.text.replace("\r\n", "\n").replace("\r", "\n")
    digest = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
    document_id = f"clarification-answer:{fingerprint}"
    uri = f"clarification://{quote(clarification.id, safe='')}/answers/{fingerprint}"
    source = SourceRef(uri=uri, content_hash=digest)
    origin_groups = {document.origin for document in documents}
    parent_ids = sorted({document.id for document in documents})
    languages = {document.language for document in documents}
    document = SourceDocument(
        id=document_id,
        version=VERSION,
        available_at=received_at,
        availability_basis="simulated_answer_received",
        source_refs=(source,),
        source_type="clarification_reply",
        connector=CONNECTOR,
        uri=uri,
        content_hash=digest,
        origin=next(iter(origin_groups)) if len(origin_groups) == 1 else None,
        language=answer.language or (next(iter(languages)) if len(languages) == 1 else None),
        thread_key=f"clarification:{clarification.id}",
        parent_document_id=parent_ids[0] if len(documents) == 1 else None,
        text=text,
        text_version=VERSION,
        meta={
            "simulated": True,
            "store_id": case.store_id,
            "case_id": case.id,
            "clarification_ref": _ref(clarification).model_dump(mode="json"),
            "observation_refs": [
                r.model_dump(mode="json") for r in sorted(expected, key=lambda r: (r.id, r.version))
            ],
            "parent_document_ids": parent_ids,
            "parent_document_refs": [
                _ref(d).model_dump(mode="json")
                for d in sorted(documents, key=lambda d: (d.id, d.version))
            ],
            "source_run_id": parent.run_id,
            "source_scenario_id": parent.scenario_id,
        },
    )
    segment = Segment(
        id=f"{document_id}:segment:0",
        version=VERSION,
        available_at=received_at,
        availability_basis=document.availability_basis,
        source_refs=(source,),
        document_id=document_id,
        text_version=VERSION,
        idx=0,
        text=text,
        char_start=0,
        char_end=len(text),
        is_quoted=False,
    )
    segment.validate_against(document)
    identity = _hash(
        {
            "parent": parent.run_id,
            "answer": fingerprint,
            "scenario_id": scenario_id,
            "as_of": as_of.isoformat(),
        }
    )
    # New source identity invalidates source-dependent retrieval/cache entries.
    child = RunSpec.model_validate(
        {
            **parent.model_dump(),
            "run_id": f"clarification-run:{identity}",
            "scenario_id": scenario_id,
            "as_of": as_of,
            "source_manifest_hash": "sha256:"
            + _hash(
                {
                    "parent": parent.source_manifest_hash,
                    "answer": fingerprint,
                    "document": document.model_dump(mode="json"),
                }
            ),
        }
    )
    seed_refs = tuple(
        dict.fromkeys(
            (
                _ref(case),
                _ref(clarification),
                *clarification.observation_refs,
                *(_ref(d) for d in sorted(documents, key=lambda d: (d.id, d.version))),
            )
        )
    )
    answered = Clarification.model_validate(
        {
            **clarification.model_dump(),
            "version": f"answer:{fingerprint}",
            "run_id": child.run_id,
            "scenario_id": child.scenario_id,
            "computed_at": child.as_of,
            "available_at": received_at,
            "availability_basis": document.availability_basis,
            "input_refs": (*seed_refs, _ref(document)),
            "producer": "out.clarifications",
            "producer_version": VERSION,
            "answer_document_id": document_id,
            "answered_at": received_at,
            "status": "answered",
        }
    )
    return PreparedAnswer(fingerprint, document, segment, answered, child, seed_refs)
