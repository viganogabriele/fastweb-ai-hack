"""INT-06 module: ``int.context`` associates external context to cases by geo/time.

Inputs are ``Case`` and ``ContextEvent`` records visible at ``as_of`` (from
``src.external``). Each event is considered for stores it covers
(``ContextEvent.store_ids``); a case is a candidate if it belongs to one of those
stores and the event's time window overlaps the case's window or its window is
within a small slack, or simply if both are co-located at the store level and
time-adjacent. We only attach context when it is relevant by geo and time; we
do **not** compute an uplift or change any quantity. For each association we set
the event's ``role`` to ``corroborating`` if it is plausibly relevant to the case
type (cold/warm weather for stockout/unmet demand/traffic change in plausible
conditions), else ``context_only``. Associations are recorded by adding the
``ContextEvent`` as an ``ArtifactRef`` to ``Case.context_refs`` (deduplicated by
``(kind,id,version)``) without mutating other fields. If a case already has
references to a given context event, we do not duplicate them. The module never
creates cases and never drops cases.
"""

from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Protocol

from tessera.core import repo
from tessera.core.contracts import (
    ArtifactRef,
    Case,
    ContextEvent,
    ModuleManifest,
    ModuleResult,
    RunSpec,
)
from tessera.core.contracts.common import SourceRecord

MANIFEST = ModuleManifest(
    id="int.context",
    version="1",
    layer="integration",
    description=(
        "Associate ContextEvent (geo/time) to cases: add corroborating/context_only "
        "refs to Case.context_refs without automatic uplift"
    ),
    requires=("int.cases", "src.external"),
    optional_inputs=(),
    produces=("Case",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "slack_hours": {"type": "integer", "minimum": 0, "maximum": 72},
        },
        "additionalProperties": False,
    },
)


class Context(Protocol):
    @property
    def spec(self) -> RunSpec: ...

    @property
    def repo(self) -> repo.Repo: ...

    @property
    def params(self) -> Mapping[str, Any]: ...


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def _overlap(a_start, a_end, b_start, b_end, slack: timedelta) -> bool:
    # allow slack on both sides
    if a_end + slack < b_start - slack:
        return False
    if b_end + slack < a_start - slack:
        return False
    return True


CORROBORATING_KINDS = {
    ("weather_cold", {"unmet_demand", "stockout", "low_stock", "traffic_change"}),
    ("weather_warm", {"unmet_demand", "stockout", "low_stock", "traffic_change"}),
}


def _role(event: ContextEvent, case: Case) -> str:
    for ekind, case_types in CORROBORATING_KINDS:
        if event.kind == ekind and case.case_type in case_types:
            return "corroborating"
    return "context_only"


def run(ctx: Context) -> ModuleResult:
    slack_hours = int(ctx.params.get("slack_hours", 24))
    slack = timedelta(hours=slack_hours)
    cases = ctx.repo.list(Case)
    events = ctx.repo.list(ContextEvent)
    updated = 0
    errors = []
    for case in cases:
        if case.store_id is None:
            continue
        existing = set((r.kind, r.id, r.version) for r in case.context_refs)
        new_refs = []
        for ev in events:
            if case.store_id not in ev.store_ids:
                continue
            if not _overlap(case.window_start, case.window_end, ev.start, ev.end, slack):
                continue
            k = (type(ev).__name__, ev.id, ev.version)
            if k in existing:
                continue
            new_refs.append(ref(ev))
            existing.add(k)
        if new_refs:
            updated_case = case.model_copy(
                update={"context_refs": tuple(list(case.context_refs) + new_refs)}
            )
            written = ctx.repo.put(updated_case)
            updated += written
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="succeeded",
        counts={"cases": len(cases), "events": len(events), "updated_cases": updated},
        errors=tuple(errors),
        abstentions=(),
    )
