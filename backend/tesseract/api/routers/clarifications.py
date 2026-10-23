"""Published questions and explicitly simulated answers in isolated follow-up jobs."""

import logging
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from jsonschema.exceptions import ValidationError as SchemaError
from sqlalchemy.exc import OperationalError

from tesseract.api.routers.runs import Namespace, PublishedRepo, engine_for, registry_for
from tesseract.core.config import get_settings
from tesseract.core.contracts import Case, Clarification
from tesseract.core.repo import latest
from tesseract.modules.agents.answer_registry import (
    AnswerConflict,
    AnswerJob,
    AnswerRequest,
    AnswerUnavailable,
    RegisteredAnswer,
    execute_follow_up,
    registered_answers,
    submit_answer,
)
from tesseract.modules.agents.clarifications import InvalidAnswer, UnrecordedAnswer

router = APIRouter(prefix="/api/runs/{run_id}/cases/{case_id}/clarifications")
Status = Literal["draft", "asked", "answered", "cancelled"]


def execute_answer(engine, job, fixture, registry, settings):
    try:
        execute_follow_up(
            engine, job.run.run_id, fixture_mode=fixture, registry=registry, settings=settings
        )
    except Exception:
        # The durable worker records failures. A background failure must not turn
        # an already committed answer into an apparent failed HTTP submission.
        logging.getLogger("tesseract.api").exception("Answer job %s failed", job.run.run_id)


@router.post("/{clarification_id}/answer", response_model=AnswerJob, status_code=202)
def answer(
    run_id: str,
    case_id: str,
    clarification_id: str,
    body: AnswerRequest,
    request: Request,
    tasks: BackgroundTasks,
    ns: Namespace,
):
    if (body.run_id, body.case_id, body.clarification_id) != (run_id, case_id, clarification_id):
        raise HTTPException(422, "Answer scope must match the run, case and clarification URL")
    engine = engine_for(request, ns)
    try:
        registry = registry_for(request)
        job = submit_answer(engine, body, fixture_mode=ns == "fixture", registry=registry)
    except AnswerConflict as error:
        raise HTTPException(409, str(error)) from None
    except UnrecordedAnswer as error:
        raise HTTPException(424, str(error)) from None
    except InvalidAnswer as error:
        raise HTTPException(422, str(error)) from None
    except AnswerUnavailable as error:
        raise HTTPException(503, str(error)) from None
    except (ValueError, SchemaError):
        raise HTTPException(503, "Frozen pipeline implementation is unavailable") from None
    except OperationalError as error:
        if "locked" not in str(error.orig):
            raise
        raise HTTPException(503, "Pipeline is writing; retry", {"Retry-After": "5"}) from None
    tasks.add_task(
        execute_answer,
        engine,
        job,
        ns == "fixture",
        registry,
        request.app.state.settings or get_settings(),
    )
    return job


@router.get("/{clarification_id}/registered-answers", response_model=tuple[RegisteredAnswer, ...])
def registered(
    run_id: str,
    case_id: str,
    clarification_id: str,
    repo: PublishedRepo,
    request: Request,
    ns: Namespace,
):
    """Offline-replayable answer bodies; no registration or submission happens here."""
    question = repo.get(Clarification, clarification_id)
    if question is None or question.case_id != case_id:
        raise HTTPException(404, "Clarification not found")
    return registered_answers(
        engine_for(request, ns), run_id, case_id, clarification_id, fixture_mode=ns == "fixture"
    )


@router.get("", response_model=tuple[Clarification, ...])
def clarifications(case_id: str, repo: PublishedRepo, status: Status | None = None):
    if repo.get(Case, case_id) is None:
        raise HTTPException(404, "Case not found")
    return tuple(
        sorted(
            (
                item
                for item in latest(repo.list(Clarification))
                if item.case_id == case_id and (status is None or item.status == status)
            ),
            key=lambda item: item.id,
        )
    )


@router.get("/{clarification_id}", response_model=Clarification)
def clarification(
    case_id: str,
    clarification_id: str,
    repo: PublishedRepo,
    version: str | None = None,
):
    if version is None and repo.get(Case, case_id) is None:
        raise HTTPException(404, "Case not found")
    item = repo.get(Clarification, clarification_id, version)
    if item is None or item.case_id != case_id:
        raise HTTPException(404, "Clarification not found")
    return item
