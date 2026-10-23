"""Read persisted simulated clarification drafts without executing the agent."""

from typing import Literal

from fastapi import APIRouter, HTTPException

from tessera.api.routers.runs import PublishedRepo
from tessera.core.contracts import Case, Clarification
from tessera.core.repo import latest

router = APIRouter(prefix="/api/runs/{run_id}/cases/{case_id}/clarifications")
Status = Literal["draft", "asked", "answered", "cancelled"]


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
    if repo.get(Case, case_id) is None:
        raise HTTPException(404, "Case not found")
    item = repo.get(Clarification, clarification_id, version)
    if item is None or item.case_id != case_id:
        raise HTTPException(404, "Clarification not found")
    return item
