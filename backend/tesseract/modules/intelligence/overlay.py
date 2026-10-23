"""FC-03 module: ``fc.overlay`` turns a demand case into low/base/high scenarios, or abstains.

For every demand case (``unmet_demand``, ``demand_shift``) with a resolved store and product, one
``ForecastAdjustment`` per SKU-colour of the case, on top of the run's ``fc.baseline`` record
(RFC §4.9 steps 3–7). Policy values come from ``policy`` in ``config/domain.yaml``.

Quantitative gates, per supporting observation (the first that fails is its abstention reason):
not negated; kind ``unmet_demand`` or ``demand_up`` (a stock-out alone gives no uplift); direction
up; an ``exact`` count; unit ``units`` (requests and customers are not units); a known period with
at least one open day ``g``. Certain copies (``duplicates``) are one episode, never two.

One overlay per piece of information: exactly one admissible episode in the case and no other
case with an admissible episode on the same store × SKU. Several possible episodes give
``unchanged`` and a reason to verify, never a sum. A style-level case is not split over colours.

Scenarios, under the declared hypothesis that the episode's rate persists beyond the baseline
(param ``incremental``, on by default; off gives ``unchanged``):

    u = n / g                                  units per open day
    w_d = 2^(-age_d / half_life)               age_d from max(episode end, last independent
                                               evidence), never from the run; 0 after valid_until
    latent_s,d = clip(b_d + delta_s * u * w_d, 0, cap * b_d)     r = 1: residuals are off
    servable = latent                          no exposure factor in the MVP (step 8)

``valid_until`` is the case's own, else the reference plus ``max_validity``. A zero baseline on an
open day that would get an uplift is ``not_estimable`` (cold start), never a hidden increase.
Components expose the uplift per day and what the cap clipped, so
``sum(latent) == sum(baseline) + sum(uplift) - sum(clipped)`` for every scenario.

A record without uplift is ``unchanged`` (scenarios equal the baseline) with the abstention reason;
a baseline that is ``not_estimable`` stays so. Records are available at their latest input.
"""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Protocol
from zoneinfo import ZoneInfo

import yaml

from tesseract.core import repo
from tesseract.core.config import get_settings
from tesseract.core.contracts import (
    AdjustmentComponent,
    ArtifactRef,
    Case,
    EvidenceRelation,
    ForecastAdjustment,
    ForecastPoint,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
    ScenarioValues,
)
from tesseract.core.contracts.common import SourceRecord
from tesseract.modules.intelligence import baseline as fc_baseline
from tesseract.modules.sources import erp

DEMAND_CASE_TYPES = frozenset({"unmet_demand", "demand_shift"})
UPLIFT_KINDS = frozenset({"unmet_demand", "demand_up"})
SCENARIOS = ("low", "base", "high")
FORMULA_VERSION = "rfc001-4.9-overlay-v1"
HYPOTHESIS = (
    "Declared scenario hypothesis: the episode's rate of units persists over the horizon beyond "
    "the demand already in the baseline. Policy coefficients, not a calibrated estimate."
)

MANIFEST = ModuleManifest(
    id="fc.overlay",
    version="1",
    layer="intelligence",
    description=(
        "Low/base/high scenarios per demand case × SKU-colour from one admissible episode, "
        "with decay and cap; baseline unchanged with the abstention reason otherwise"
    ),
    requires=("fc.baseline", "int.cases"),
    optional_inputs=(),
    produces=("ForecastAdjustment",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {"incremental": {"type": "boolean"}},
        "additionalProperties": False,
    },
)


class Context(Protocol):
    """The part of PLT-04's ``RunContext`` this module uses."""

    @property
    def spec(self) -> RunSpec: ...

    @property
    def repo(self) -> repo.Repo: ...

    @property
    def params(self) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class Policy:
    delta: Mapping[str, float]  # fraction of u per scenario
    half_life_days: float
    max_validity: timedelta
    cap: float
    incremental: bool = True


@dataclass(frozen=True)
class Store:
    store_id: str
    tz: ZoneInfo
    closed: frozenset[int]


@dataclass(frozen=True)
class Episode:
    observation: Observation
    n: float
    g: int
    end: datetime


def load_policy(config_dir: Path, incremental: bool = True) -> Policy:
    domain = yaml.safe_load((config_dir / "domain.yaml").read_text(encoding="utf-8"))
    p = domain["policy"]
    return Policy(
        delta={s: float(p["incremental"][f"delta_{s}"]["value"]) for s in SCENARIOS},
        half_life_days=float(p["decay"]["half_life"]["value"]),
        max_validity=timedelta(days=p["decay"]["max_validity"]["value"]),
        cap=float(p["latent"]["cap"]["value"]),
        incremental=incremental,
    )


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def _local_days(start: datetime, end: datetime, store: Store) -> list[date]:
    first, last = start.astimezone(store.tz).date(), end.astimezone(store.tz).date()
    days = [first + timedelta(days=i) for i in range((last - first).days + 1)]
    return [d for d in days if d.weekday() not in store.closed]


def gate(obs: Observation, store: Store) -> Episode | str:
    """The observation as a numerically admissible episode, or the first gate it fails."""
    q = obs.quantity
    if obs.negated:
        return "negated"
    if obs.kind not in UPLIFT_KINDS:
        return f"kind_{obs.kind}_gives_no_uplift"
    if obs.direction != "up":
        return f"direction_{obs.direction}"
    if q.kind != "exact" or q.value is None:
        return f"quantity_{q.kind}"
    if q.unit != "units":
        return f"unit_{q.unit}_not_units"
    if q.value <= 0:
        return "count_not_positive"
    if obs.period_start is None or obs.period_end is None:
        return "period_unknown"
    g = len(_local_days(obs.period_start, obs.period_end, store))
    if g == 0:
        return "no_open_day_in_period"
    return Episode(obs, q.value, g, obs.period_end)


def copies(relations: Iterable[EvidenceRelation]) -> dict[str, str]:
    """Observation id → the original it certainly duplicates."""
    return {
        r.from_ref.id: r.to_ref.id
        for r in relations
        if r.relation == "duplicates" and r.from_ref.kind == r.to_ref.kind == "Observation"
    }


def episodes(
    case: Case, observations: Mapping[str, Observation], dup: Mapping[str, str], store: Store
) -> tuple[list[Episode], list[str]]:
    """Admissible episodes of one case (copies once) and why each other fact is not one."""
    found, reasons = [], []
    ids = {r.id for r in case.supporting}
    for r in case.supporting:
        obs = observations.get(r.id)
        if obs is None or r.kind != "Observation":
            reasons.append(f"{r.id}: not_an_observation")
            continue
        if r.id in dup and dup[r.id] in ids:
            reasons.append(f"{r.id}: copy_of:{dup[r.id]}")
            continue
        verdict = gate(obs, store)
        if isinstance(verdict, str):
            reasons.append(f"{r.id}: {verdict}")
        else:
            found.append(verdict)
    return found, reasons


def _flat(point: ForecastPoint) -> ForecastPoint:
    if point.baseline is None:
        return point
    flat = ScenarioValues(low=point.baseline, base=point.baseline, high=point.baseline)
    return point.model_copy(update={"latent": flat, "servable": flat})


def _instant(day: date, store: Store) -> datetime:
    return datetime.combine(day, time(0), store.tz).astimezone(UTC)


def build_overlay(
    spec: RunSpec,
    case: Case,
    base: ForecastAdjustment,
    store: Store,
    policy: Policy,
    found: Sequence[Episode],
    reasons: Sequence[str],
    concurrent: Sequence[str] = (),
) -> ForecastAdjustment:
    """One case's adjustment on one SKU's baseline. Pure: inputs are given."""
    episode = found[0] if len(found) == 1 else None
    inputs: list[SourceRecord] = [case, base, *(e.observation for e in found)]
    status, reason, components = "unchanged", None, ()
    series = tuple(_flat(p) for p in base.series)

    if base.status == "not_estimable":
        status, reason = "not_estimable", f"baseline_not_estimable: {base.reason}"
        series = tuple(p.model_copy(update={"latent": None, "servable": None}) for p in base.series)
    elif case.scope_level == "style":
        reason = "scope_style: the evidence names the style, not this colour; nothing is split"
    elif not found:
        reason = "no_admissible_episode: " + "; ".join(reasons or ("no supporting fact",))
    elif len(found) > 1:
        ids = ", ".join(e.observation.id for e in found)
        reason = f"overlapping_episodes: {ids} may be one episode; verify, never summed"
    elif concurrent:
        reason = f"concurrent_cases: {', '.join(concurrent)} also quantify this SKU; verify"
    elif not policy.incremental:
        reason = "incremental_hypothesis_off: scenarios equal the baseline"
    else:
        assert episode is not None
        status, reason, series, components = _scenarios(case, base, store, policy, episode)

    available = [r.available_at for r in inputs if r.available_at is not None]
    return ForecastAdjustment(
        id=f"overlay-{case.id}-{base.sku.lower()}-{base.horizon_start:%Y%m%d}",
        version="v1",
        available_at=max(available),
        availability_basis="max(case, baseline, episode observations)",
        source_refs=tuple(dict.fromkeys(s for r in inputs for s in r.source_refs)),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=tuple(ref(r) for r in inputs),
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        case_ids=(case.id,),
        store_id=base.store_id,
        sku=base.sku,
        baseline_ref=base.baseline_ref,
        horizon_start=base.horizon_start,
        horizon_end=base.horizon_end,
        status=status,
        reason=reason,
        series=series,
        components=components,
        proposal_source="code",
    )


def _scenarios(
    case: Case, base: ForecastAdjustment, store: Store, policy: Policy, episode: Episode
) -> tuple[str, str | None, tuple[ForecastPoint, ...], tuple[AdjustmentComponent, ...]]:
    obs = episode.observation
    u = episode.n / episode.g
    anchor = max(episode.end, case.last_independent_evidence_at or episode.end)
    valid_until = case.valid_until or anchor + policy.max_validity
    anchor_day = anchor.astimezone(store.tz).date()
    last_day = valid_until.astimezone(store.tz).date()

    daily, clipped, points = [], [], []
    for p in base.series:
        assert p.baseline is not None  # an estimable baseline has every day
        is_open = p.date.weekday() not in store.closed
        age = (p.date - anchor_day).days
        w = 2 ** (-max(age, 0) / policy.half_life_days) if is_open and p.date <= last_day else 0.0
        uplift = {s: policy.delta[s] * u * w for s in SCENARIOS}
        if p.baseline == 0 and uplift["high"] > 0:
            reason = f"cold_start: zero baseline on open day {p.date} with an uplift to apply"
            empty = tuple(
                q.model_copy(update={"latent": None, "servable": None}) for q in base.series
            )
            return "not_estimable", reason, empty, ()
        raw = {s: p.baseline + uplift[s] for s in SCENARIOS}
        latent = {s: min(max(raw[s], 0.0), policy.cap * p.baseline) for s in SCENARIOS}
        daily.append({"date": p.date.isoformat(), "age_days": age, "w": w, **uplift})
        clipped.append({"date": p.date.isoformat(), **{s: raw[s] - latent[s] for s in SCENARIOS}})
        values = ScenarioValues(**latent)
        points.append(p.model_copy(update={"latent": values, "servable": values}))

    if not any(d["high"] > 0 for d in daily):
        reason = f"episode_expired: valid until {valid_until.isoformat()}, no weight on the horizon"
        return "unchanged", reason, tuple(_flat(p) for p in base.series), ()

    window = (_instant(base.horizon_start, store), _instant(base.horizon_end + timedelta(1), store))
    until = min(window[1], max(valid_until, window[0]))
    evidence = tuple(
        dict.fromkeys(
            ArtifactRef(kind="SourceDocument", id=e.document_id, version=e.document_version)
            for e in obs.evidence
        )
    )
    totals = {s: sum(d[s] for d in daily) for s in SCENARIOS}
    episode_component = AdjustmentComponent(
        type="incremental_episode",
        episode_refs=(ref(obs),),
        evidence_refs=evidence,
        params={
            "case_scope": f"{case.scope_level}:{case.scope_id}",
            "n_units": episode.n,
            "open_days_counted": episode.g,
            "u_units_per_day": u,
            "delta_fraction_of_u": dict(policy.delta),
            "r": 1.0,
            "half_life_days": policy.half_life_days,
            "decay_anchor": anchor.isoformat(),
            "valid_until": valid_until.isoformat(),
            "total_uplift": totals,
            "daily": daily,
        },
        unit="units",
        effective_from=window[0],
        effective_until=until,
        reference_time=anchor,
        formula_version=FORMULA_VERSION,
        explanation=(
            f"{episode.n:g} units over {episode.g} open day(s) → u = {u:g} units/day; "
            f"scenario uplift delta_s·u·w_d with w_d = 2^(-age/{policy.half_life_days:g}) from "
            f"{anchor_day}, zero after {last_day}. {HYPOTHESIS}"
        ),
    )
    components = [episode_component]
    cut = {s: sum(c[s] for c in clipped) for s in SCENARIOS}
    if any(v > 0 for v in cut.values()):
        components.append(
            AdjustmentComponent(
                type="cap_clip",
                episode_refs=(ref(obs),),
                evidence_refs=evidence,
                params={"cap_multiple_of_baseline": policy.cap, "total_clipped": cut,
                        "daily": [c for c in clipped if any(c[s] > 0 for s in SCENARIOS)]},
                unit="units",
                effective_from=window[0],
                effective_until=window[1],
                reference_time=anchor,
                formula_version=FORMULA_VERSION,
                explanation=(
                    f"Latent demand capped at {policy.cap:g}× the baseline: the clipped units are "
                    "removed so the daily series reconciles with baseline + uplift − clipped."
                ),
            )
        )  # fmt: skip
    return "computed", None, tuple(points), tuple(components)


def case_skus(case: Case, sku_of_size: Mapping[str, str], carried: Iterable[str]) -> list[str]:
    """SKU-colours a case speaks about: its SKU, the SKU of its size, the store's colours of its
    style. Category, store and unknown scopes have none."""
    if case.scope_id is None:
        return []
    if case.scope_level == "sku":
        return [case.scope_id]
    if case.scope_level == "sku_size":
        return [sku_of_size[case.scope_id]] if case.scope_id in sku_of_size else []
    if case.scope_level == "style":
        return sorted(s for s in carried if s.startswith(case.scope_id + "-"))
    return []


@dataclass(frozen=True)
class OverlayBuild:
    records: tuple[ForecastAdjustment, ...]
    abstentions: tuple[str, ...]


def build_overlays(
    spec: RunSpec,
    cases: Iterable[Case],
    observations: Iterable[Observation],
    relations: Iterable[EvidenceRelation],
    baselines: Mapping[tuple[str, str], ForecastAdjustment],
    stores: Mapping[str, Store],
    sku_of_size: Mapping[str, str],
    carried: Mapping[str, set[str]],
    policy: Policy,
) -> OverlayBuild:
    by_id = {o.id: o for o in observations}
    dup = copies(relations)
    abstentions: list[str] = []
    plans = []
    for case in cases:
        if case.case_type not in DEMAND_CASE_TYPES or case.store_id is None:
            continue
        store = stores.get(case.store_id)
        skus = case_skus(case, sku_of_size, carried.get(case.store_id, set()))
        if store is None or not skus:
            abstentions.append(f"{case.id}: no SKU-colour scope ({case.scope_level})")
            continue
        found, reasons = episodes(case, by_id, dup, store)
        for sku in skus:
            base = baselines.get((case.store_id, sku))
            if base is None:
                abstentions.append(f"{case.id}: no fc.baseline for {case.store_id} × {sku}")
                continue
            plans.append((case, base, store, found, reasons))
    quantified: dict[tuple[str, str], list[str]] = {}
    for case, base, _, found, _ in plans:
        if found and case.scope_level != "style":
            quantified.setdefault((base.store_id, base.sku), []).append(case.id)
    records = []
    for case, base, store, found, reasons in plans:
        others = [c for c in quantified.get((base.store_id, base.sku), []) if c != case.id]
        records.append(build_overlay(spec, case, base, store, policy, found, reasons, others))
    return OverlayBuild(tuple(records), tuple(abstentions))


def run(ctx: Context) -> ModuleResult:
    policy = load_policy(get_settings().config_dir, bool(ctx.params.get("incremental", True)))
    run_repo = ctx.repo
    stores = {
        str(r.data["store_id"]): Store(
            str(r.data["store_id"]),
            ZoneInfo(str(r.data["timezone"])),
            fc_baseline.closed_weekdays(r.data.get("closed_dow")),
        )
        for r in erp.read(run_repo, "stores")
    }
    baselines = {
        (b.store_id, b.sku): b
        for b in run_repo.list(ForecastAdjustment, where={"producer": fc_baseline.MANIFEST.id})
    }
    carried: dict[str, set[str]] = {}
    for r in erp.read(run_repo, "assortment"):
        carried.setdefault(str(r.data["store_id"]), set()).add(str(r.data["sku"]))
    built = build_overlays(
        ctx.spec,
        repo.latest(run_repo.list(Case)),
        run_repo.list(Observation),
        run_repo.list(EvidenceRelation),
        baselines,
        stores,
        {str(r.data["sku_size"]): str(r.data["sku"]) for r in erp.read(run_repo, "sku_size_ean")},
        carried,
        policy,
    )
    existing = {(f.id, f.version) for f in run_repo.list(ForecastAdjustment)}
    new = [r for r in built.records if (r.id, r.version) not in existing]
    written = run_repo.put(*new) if new else 0
    by_status = {s: sum(r.status == s for r in built.records) for s in
                 ("computed", "unchanged", "not_estimable")}  # fmt: skip
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if built.abstentions else "succeeded",
        counts={"overlays": len(built.records), **by_status, "new": written},
        errors=(),
        abstentions=built.abstentions,
    )
