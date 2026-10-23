"""Published option reads and local human decisions. No external dispatch."""

from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import OperationalError

from tesseract.api.artifacts import CurrentArtifacts
from tesseract.api.routers.runs import PublishedRepo, engine_for
from tesseract.core.cache import CacheCorrupt, ReplayMiss
from tesseract.core.contracts import ActionOption, Case
from tesseract.core.contracts.common import Contract, Text
from tesseract.modules.actions import approval

router = APIRouter(prefix="/api/runs/{run_id}")


class DecisionInput(Contract):
    option_id: Text
    input_version_hash: Text
    decision: Literal["approved", "rejected"]
    by: Text
    idempotency_key: Text
    note: str | None = None


def option_input_loader() -> approval.InputLoader:
    """Trusted server dependency; HTTP clients cannot supply inputs or validation results."""
    return approval.load_inputs


def decision_clock() -> datetime:
    return datetime.now(UTC)


Loader = Annotated[approval.InputLoader, Depends(option_input_loader)]
Clock = Annotated[datetime, Depends(decision_clock)]


def visible_case(repo, case_id: str) -> Case:
    case = repo.get(Case, case_id)
    if case is None:
        raise HTTPException(404, "Case not found")
    return case


@router.get("/cases/{case_id}/options", response_model=tuple[ActionOption, ...])
def options(case_id: str, repo: PublishedRepo):
    """The options evaluated by act.options for this case in the selected snapshot.

    Reading does not refresh or reserve stock. Approval reruns evaluate_options through
    the ACT-03 service and rejects a proposal whose current inputs no longer match.
    """
    visible_case(repo, case_id)
    return repo.list(ActionOption, case_id=case_id)


def submit(request: Request, repo, body: DecisionInput, loader, clock) -> approval.LocalDraft:
    option = repo.get(ActionOption, body.option_id)
    if option is None:
        raise HTTPException(404, "Option not found")
    visible_case(repo, option.case_id)
    command = approval.DecisionRequest(
        run_id=repo.run_id,
        scenario_id=repo.spec.scenario_id,
        **body.model_dump(),
    )
    try:
        return approval.decide(
            engine_for(request, repo.namespace),
            command,
            loader=lambda current, case: loader(CurrentArtifacts(current), case),
            now=clock,
        )
    except approval.Conflict as error:
        raise HTTPException(409, str(error)) from None
    except (ReplayMiss, CacheCorrupt):
        raise HTTPException(
            503, "Missing or corrupt systems recording; decision not saved"
        ) from None
    except OperationalError as error:
        if "locked" not in str(error.orig):
            raise
        raise HTTPException(
            503, "Ledger is busy; retry with the same key", {"Retry-After": "5"}
        ) from None


@router.post("/cases/{case_id}/decisions", response_model=approval.LocalDraft)
def case_decision(
    case_id: str,
    body: DecisionInput,
    request: Request,
    repo: PublishedRepo,
    loader: Loader,
    clock: Clock,
):
    visible_case(repo, case_id)
    option = repo.get(ActionOption, body.option_id)
    if option is None or option.case_id != case_id:
        raise HTTPException(404, "Option not found in this case")
    return submit(request, repo, body, loader, clock)


def saved(request: Request, repo) -> tuple[approval.LocalDraft, ...]:
    return approval.saved_drafts(
        engine_for(request, repo.namespace), repo.spec.scenario_id, repo.run_id
    )


@router.get("/decisions", response_model=tuple[approval.LocalDraft, ...])
def decisions(request: Request, repo: PublishedRepo, case_id: str | None = None):
    """Local drafts saved for this snapshot, in decision-clock order.

    Exactly what the decision endpoints committed, including idempotent retries once and
    no rejected (409) attempt. An option without a draft is undecided; reads never
    revalidate, refresh or dispatch anything.
    """
    if case_id is not None:
        visible_case(repo, case_id)
    return tuple(d for d in saved(request, repo) if case_id is None or d.option.case_id == case_id)


@router.get("/decisions/{decision_id}", response_model=approval.LocalDraft)
def decision(decision_id: str, request: Request, repo: PublishedRepo):
    draft = next((d for d in saved(request, repo) if d.decision.id == decision_id), None)
    if draft is None:
        raise HTTPException(404, "Decision not found")
    return draft


@router.post("/options/{option_id}/decision", response_model=approval.LocalDraft)
def option_decision(
    option_id: str,
    body: DecisionInput,
    request: Request,
    repo: PublishedRepo,
    loader: Loader,
    clock: Clock,
):
    """RFC §4.6 option-addressed equivalent of the case decision endpoint."""
    if body.option_id != option_id:
        raise HTTPException(422, "Option ID must match the URL")
    return submit(request, repo, body, loader, clock)
