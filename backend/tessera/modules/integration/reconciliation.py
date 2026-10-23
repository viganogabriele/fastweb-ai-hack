"""Pure INT-04 rules for stock conflicts and source-backed decision calendars.

A stock snapshot is evidence at an instant, never evidence of latent demand or
proof that a case is resolved. Calendar slots already include departure cutoff,
receiving days and sellable time; no transit-day subtraction is performed here.
"""

from collections.abc import Iterable
from datetime import datetime, time
from typing import Annotated, Self
from zoneinfo import ZoneInfo

from pydantic import Field, model_validator

from tessera.core.contracts import ArtifactRef, Case, Observation, SourceRef, StockFact
from tessera.core.contracts.common import Contract, Instant, Text, ordered
from tessera.core.repo import ErpRecord


class ArrivalSlot(Contract):
    cutoff_at: Instant
    sellable_at: Instant

    @model_validator(mode="after")
    def sequence(self) -> Self:
        ordered(self.cutoff_at, self.sellable_at)
        return self


class DecisionCalendar(Contract):
    """Source-backed slots, pinned to one case (never inferred from episode end).

    This optional run parameter is a normalized calendar input, not permission
    to move stock. The source must establish required_by and both calendars.
    """

    case_id: Text
    available_at: Instant
    required_by: Instant
    source_refs: tuple[SourceRef, ...]
    slots: tuple[ArrivalSlot, ...]

    @model_validator(mode="after")
    def provenance(self) -> Self:
        if not self.source_refs:
            raise ValueError("decision calendar requires source references")
        return self


class ReconciliationParams(Contract):
    max_validity_days: Annotated[int, Field(ge=1, le=60)] | None = None
    decision_calendars: tuple[DecisionCalendar, ...] = ()


def _ref(record) -> ArtifactRef:
    return ArtifactRef(
        kind=f"erp.{record.table}" if isinstance(record, ErpRecord) else type(record).__name__,
        id=record.id,
        version=record.version,
    )


def reconcile(
    case: Case,
    observations: Iterable[Observation],
    stocks: Iterable[StockFact],
    erp_stock: Iterable[ErpRecord],
    calendars: Iterable[DecisionCalendar],
    *,
    as_of: datetime,
    timezone: str | None,
) -> Case:
    """Keep all evidence and conflicts; missing/old evidence never closes a case."""
    supporting = list(case.supporting)
    contradicting = list(case.contradicting)
    context = list(case.context_refs)
    inputs = list(case.input_refs)
    sources = list(case.source_refs)
    uncertainties = list(case.blocking_uncertainties)
    available = case.available_at
    conflict = False

    stock_claims = [
        o
        for o in observations
        if o.kind == "stockout"
        and not o.negated
        and o.period_start is not None
        and o.period_end is not None
    ]
    # A size-specific stock statement needs the exact linked size. SKU-wide
    # statements can have potential conflicts, but never assert all sizes sellable.
    candidates = []
    if case.scope_level in ("sku", "sku_size") and case.store_id and timezone:
        zone = ZoneInfo(timezone)
        for stock in stocks:
            scope = stock.sku if case.scope_level == "sku" else f"{stock.sku}-{stock.size}"
            if (
                stock.location_id == case.store_id
                and scope == case.scope_id
                and stock.available_at is not None
                and stock.available_at <= as_of
                and stock.snapshot_at <= as_of
                and stock.qty is not None
            ):
                candidates.append((stock, stock.snapshot_at, stock.qty, stock.basis))
        for row in erp_stock:
            data = row.data
            scope = (
                data.get("sku")
                if case.scope_level == "sku"
                else (f"{data.get('sku')}-{data.get('size')}")
            )
            if (
                row.table != "stock"
                or data.get("store_id") != case.store_id
                or scope != case.scope_id
                or row.available_at is None
                or row.available_at > as_of
                or data.get("on_hand") is None
                or datetime.combine(data["snapshot_date"], time(23, 59, 59), zone) > as_of
            ):
                continue
            # EOD is only comparable to a claim explicitly covering that full
            # local date. It cannot contradict an intraday out-of-stock episode.
            day = data["snapshot_date"]
            matching = [
                o
                for o in stock_claims
                if o.period_start.astimezone(zone).date() == day
                and o.period_end.astimezone(zone).date() == day
                and o.period_start.astimezone(zone).time() == time.min
                and o.period_end.astimezone(zone).time() >= time(23, 59, 59)
            ]
            if matching:
                candidates.append((row, None, data["on_hand"], "on_hand"))

    for record, snapshot, qty, basis in candidates:
        if snapshot is not None and not any(
            o.period_start <= snapshot <= o.period_end for o in stock_claims
        ):
            continue
        reference = _ref(record)
        context.append(reference)
        inputs.append(reference)
        sources.extend(record.source_refs)
        available = max(available, record.available_at)
        if qty > 0:
            contradicting.append(reference)
            conflict = True
            uncertainties.append(
                f"Potential stock conflict: {reference.kind} {reference.id}@{reference.version} "
                f"reports {qty} {basis} units during the reported stockout. "
                "Check timing, size coverage and sellability; this does not disprove unmet demand."
            )
        elif basis == "on_hand" and case.scope_level == "sku_size":
            supporting.append(reference)
        # Zero ATP/sellable does not prove zero physical stock; one empty size
        # does not prove a whole SKU out of stock.

    if context != list(case.context_refs):
        uncertainties = [
            u
            for u in uncertainties
            if u != ("Stock level is the store's statement; ERP stock not checked yet.")
        ]

    deadline = None
    applicable = [c for c in calendars if c.case_id == case.id and c.available_at <= as_of]
    if case.case_type == "unmet_demand":
        if (
            len(applicable) == 1
            and case.store_id is not None
            and case.scope_level in ("sku", "sku_size")
        ):
            calendar = applicable[0]
            sources.extend(calendar.source_refs)
            available = max(available, calendar.available_at)
            feasible = [
                s
                for s in calendar.slots
                if as_of <= s.cutoff_at and s.sellable_at <= calendar.required_by
            ]
            if feasible:
                first = min(feasible, key=lambda s: (s.sellable_at, s.cutoff_at))
                deadline = first.cutoff_at
            else:
                uncertainties.append(
                    "No remaining calendar slot delivers sellable stock by required_by."
                )
        else:
            uncertainties.append(
                "Decision deadline not estimable: missing or conflicting verified "
                "required_by and departure/receiving calendars."
            )

    # The sources provide a potential contradiction, never a resolution. Existing
    # human workflow statuses and original evidence/age/counts remain intact.
    status = "verify" if conflict and case.status in ("open", "monitor") else case.status
    return case.model_copy(
        update={
            "supporting": tuple(dict.fromkeys(supporting)),
            "contradicting": tuple(dict.fromkeys(contradicting)),
            "context_refs": tuple(dict.fromkeys(context)),
            "input_refs": tuple(dict.fromkeys(inputs)),
            "source_refs": tuple(dict.fromkeys(sources)),
            "blocking_uncertainties": tuple(dict.fromkeys(uncertainties)),
            "available_at": available,
            "decision_due_at": deadline,
            "status": status,
        }
    )
