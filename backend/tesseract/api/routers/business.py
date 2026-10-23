"""Published dashboard projections: read the selected run's frozen artifact only."""

from fastapi import APIRouter, HTTPException

from tesseract.api.routers.runs import PublishedRepo
from tesseract.core.contracts import BusinessSnapshot
from tesseract.core.contracts.business import KpiDay, MarketSeries

router = APIRouter(prefix="/api/runs/{run_id}")


def snapshot(repo):
    item = repo.get(BusinessSnapshot, "business")
    if item is None:
        raise HTTPException(404, "Business series are not available in this run")
    return item


@router.get("/kpi", response_model=tuple[KpiDay, ...])
def kpi(repo: PublishedRepo):
    return snapshot(repo).kpi


@router.get("/market", response_model=MarketSeries)
def market(repo: PublishedRepo):
    return snapshot(repo).market
