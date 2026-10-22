"""Build the DATA-01b fixtures: links, relations, cases, forecast baselines and a report.

Run from the repo root after DATA-01a (rewrites `data/fixtures/{links,cases,forecast,reports}/`):

    backend/.venv/bin/python data/fixtures/build_data01b.py

Everything is derived from the DATA-01a documents and observations, the ERP catalog and the
forecast vintages in `generated/sources/erp/`, and `config/domain.yaml`. Links, relations and
cases are written by hand here: they are what correct INT-01/02/03 modules should return, not
model output. Baselines are computed with FC-01 `disaggregate` from the vintage available at the
time. Only dev stores, only `generated/sources/`, no look-ahead: each record is available at the
latest availability of its inputs.
"""

import csv
import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from tessera.core.contracts import (
    ArtifactRef,
    Case,
    Citation,
    EntityLink,
    EvidenceRelation,
    ForecastAdjustment,
    ForecastPoint,
    LinkCandidate,
    Observation,
    Report,
    ScenarioValues,
    SourceDocument,
    SourceRef,
)
from tessera.core.contracts.common import SourceRecord
from tessera.modules.intelligence.disaggregation import disaggregate

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "generated" / "sources"
MASTER = SOURCES / "erp" / "master_data"
FORECASTS = SOURCES / "erp" / "forecast" / "sku_store_weekly"
OUT = ROOT / "data" / "fixtures"

RUN_ID = "fixture"
SCENARIO_ID = "historical"
COMPUTED_AT = datetime(2026, 10, 22, 12, 0, tzinfo=UTC)
PRODUCER = "fixture.data01b"
PRODUCER_VERSION = "1"
VERSION = "v1"
TZ = {"MIL01": "Europe/Rome", "NYC01": "America/New_York"}
# Forecast runs only carry `run_date`: available at 06:00 local the next day (RFC §4.3).
VINTAGE_AVAILABLE_AT = time(6, 0)

DOMAIN = yaml.safe_load((ROOT / "config" / "domain.yaml").read_text(encoding="utf-8"))
OWNERS = DOMAIN["owners"]
POLICY = DOMAIN["policy"]
SCORE = {"score_min": 0.0, "score_max": 1.0}  # string-match scale, not a probability

# Hand labels, one per DATA-01a observation. Catalog codes come from erp/master_data; every
# candidate is checked against the catalog and the store assortment when building.
LINKS = {
    "obs-20261009-1035-mil01-stockout": {
        "status": "linked",
        "level": "style",
        "target_id": "I10919B00011",
        "candidates": [
            ("I10919B00011", "style", "alias_exact", 1.0),
            ("I10919B00042", "style", "category_word", 0.3),
        ],
        "decided_by": "rule:unique_alias",
        "rationale": "'cardigan logo' is an alias of LOGO CARDIGAN only; 'nero' and 'blu' name "
        "both its colours (999, 742), so the link stays at style level. Size M is in the mention.",
    },
    "obs-20261009-1035-mil01-unmet-demand": {
        "status": "linked",
        "level": "style",
        "target_id": "I10919B00011",
        "candidates": [
            ("I10919B00011", "style", "alias_exact", 1.0),
            ("I10919B00042", "style", "category_word", 0.3),
        ],
        "decided_by": "rule:unique_alias",
        "rationale": "Same sentence as the stock-out: 'cardigan logo in M', no single colour.",
    },
    "obs-20261002-2112-mil01-maire-requests": {
        "status": "linked",
        "level": "sku",
        "target_id": "J20931A00012-999",
        "candidates": [("J20931A00012-999", "sku", "catalog_name_colour", 1.0)],
        "decided_by": "rule:unique_catalog_match",
        "rationale": "'Maire' is the catalog name of style J20931A00012; 'nera' is colour 999.",
    },
    "obs-20261002-2113-mil01-dup-maire-requests": {
        "status": "linked",
        "level": "sku",
        "target_id": "J20931A00012-999",
        "candidates": [("J20931A00012-999", "sku", "catalog_name_colour", 1.0)],
        "decided_by": "rule:unique_catalog_match",
        "rationale": "'Maire' is the catalog name of style J20931A00012; 'nera' is colour 999.",
    },
    "obs-20261001-1124-mil01-fwd-tib-zip": {
        "status": "linked",
        "level": "sku_size",
        "target_id": "J10911A00305-742-4",
        "candidates": [("J10911A00305-742-4", "sku_size", "catalog_name_colour_size", 1.0)],
        "decided_by": "rule:unique_catalog_match",
        "rationale": "'gilet Tib' is TIB (J10911A00305); its only blue is 742 (blu notte); "
        "'taglia 4' is in its size run.",
    },
    "obs-20260906-1837-nyc01-sweatshirt-return": {
        "status": "ambiguous",
        "candidates": [
            ("I10918G00045", "style", "catalog_name_partial", 0.5),
            ("I10918G00031", "style", "shared_alias", 0.5),
        ],
        "decided_by": "rule:tie_keeps_candidates",
        "rationale": "'a sweatshirt' fits CREWNECK SWEATSHIRT and LOGO HOODIE (shared alias "
        "'sweat'), both sold at NYC01; no colour or size narrows it. Ask the store.",
    },
    "obs-20260918-2115-mil01-net-sales": {
        "status": "not_product",
        "decided_by": "rule:observation_kind",
        "rationale": "Store-level sales figure, no product mention.",
    },
    "obs-20260918-2207-mil01-corr-net-sales": {
        "status": "not_product",
        "decided_by": "rule:observation_kind",
        "rationale": "Store-level sales figure, no product mention.",
    },
}

# from → to; `evidence` are the documents that show the relation.
RELATIONS = [
    {
        "id": "rel-20261002-mil01-maire-duplicates",
        "from": "obs-20261002-2113-mil01-dup-maire-requests",
        "to": "obs-20261002-2112-mil01-maire-requests",
        "relation": "duplicates",
        "basis": "Same text sent twice 1 min apart by the same sender, different Message-ID: "
        "a certain copy, the 7 requests count once.",
    },
    {
        "id": "rel-20260918-mil01-net-sales-supersedes",
        "from": "obs-20260918-2207-mil01-corr-net-sales",
        "to": "obs-20260918-2115-mil01-net-sales",
        "relation": "supersedes",
        "basis": "Reply to the closing email: 'il fatturato di oggi e' 85,0k e non 58'. "
        "Only the net sales fact is corrected, not the rest of the email.",
    },
]

CASES = [
    {
        "id": "case-mil01-i10919b00011-20261008",
        "case_type": "unmet_demand",
        "store_id": "MIL01",
        "scope_level": "style",
        "scope_id": "I10919B00011",
        "supporting": [
            "obs-20261009-1035-mil01-stockout",
            "obs-20261009-1035-mil01-unmet-demand",
        ],
        "relations": [],
        "status": "open",
        "priority": "high",
        "priority_reason": "Size M at 0 units in both colours since 2026-10-08 and customers keep "
        "asking; no count, so no numeric uplift.",
        "decision_due": "valid_until",
        "valid_until": True,
        "blocking_uncertainties": [
            "Unmet demand is vague ('in continuazione'): no count of requests or units.",
            "Stock-out is the store's statement; ERP stock for size M not checked yet.",
            "No verified size curve: the share of size M in the colour forecast is unknown.",
        ],
        "forecast_skus": ["I10919B00011-999", "I10919B00011-742"],
        "forecast_reason": "Vague unmet demand and a plain stock-out give no numeric uplift "
        "(RFC §4.9 step 5): scenarios equal the baseline.",
    },
    {
        "id": "case-mil01-j20931a00012-999-20261002",
        "case_type": "unmet_demand",
        "store_id": "MIL01",
        "scope_level": "sku",
        "scope_id": "J20931A00012-999",
        "supporting": [
            "obs-20261002-2112-mil01-maire-requests",
            "obs-20261002-2113-mil01-dup-maire-requests",
        ],
        "relations": ["rel-20261002-mil01-maire-duplicates"],
        "status": "open",
        "priority": "medium",
        "priority_reason": "Exact count of requests in one day for MAIRE black; two copies of the same email "
        "count as one origin.",
        "decision_due": None,
        "valid_until": True,
        "blocking_uncertainties": [
            "Requests are not units: no conversion to demand without evidence.",
        ],
        "forecast_skus": ["J20931A00012-999"],
        "forecast_reason": "A count of past requests is not units of future demand "
        "(RFC §4.9 steps 3 and 5): scenarios equal the baseline.",
    },
    {
        "id": "case-mil01-j10911a00305-742-4-20261001",
        "case_type": "product_feedback",
        "store_id": "MIL01",
        "scope_level": "sku_size",
        "scope_id": "J10911A00305-742-4",
        "supporting": ["obs-20261001-1124-mil01-fwd-tib-zip"],
        "relations": [],
        "status": "open",
        "priority": "medium",
        "priority_reason": "Quality defect (zip) reported by a customer in a forwarded mail.",
        "decision_due": None,
        "valid_until": False,
        "blocking_uncertainties": [
            "One customer complaint; the store's 'same problem as recent returns' is not "
            "counted here.",
            "Purchase and defect dates come from the customer, not from POS.",
        ],
        "forecast_skus": [],
    },
    {
        "id": "case-nyc01-unknown-20260906",
        "case_type": "product_feedback",
        "store_id": "NYC01",
        "scope_level": "unknown",
        "scope_id": None,
        "supporting": ["obs-20260906-1837-nyc01-sweatshirt-return"],
        "relations": [],
        "status": "verify",
        "priority": "low",
        "priority_reason": "One return of 'a sweatshirt'; the product is not identified.",
        "decision_due": None,
        "valid_until": False,
        "blocking_uncertainties": [
            "Product ambiguous: CREWNECK SWEATSHIRT or LOGO HOODIE, colour and size unknown.",
        ],
        "forecast_skus": [],
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def file_ref(path: Path, locator: str | None = None) -> SourceRef:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    uri = "dataset://" + path.relative_to(SOURCES).as_posix()
    return SourceRef(uri=uri, content_hash=f"sha256:{digest}", locator=locator)


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def merge_sources(*groups) -> tuple[SourceRef, ...]:
    return tuple(dict.fromkeys(s for group in groups for s in group))


def derived(inputs: list[SourceRecord], extra_sources=(), extra_refs=()) -> dict:
    """Common fields: available at the latest input, never before any of them."""
    return {
        "version": VERSION,
        "available_at": max(r.available_at for r in inputs if r.available_at is not None),
        "availability_basis": "max_input_available_at",
        "source_refs": merge_sources(*(r.source_refs for r in inputs), extra_sources),
        "run_id": RUN_ID,
        "scenario_id": SCENARIO_ID,
        "computed_at": COMPUTED_AT,
        "input_refs": (*(ref(r) for r in inputs), *extra_refs),
        "producer": PRODUCER,
        "producer_version": PRODUCER_VERSION,
    }


def load_folder(folder: str) -> list:
    kinds = {"SourceDocument": SourceDocument, "Observation": Observation}
    records = []
    for path in sorted((OUT / folder).glob("*.json")):
        for rec in json.loads(path.read_text(encoding="utf-8")):
            if rec["kind"] in kinds:
                records.append(kinds[rec["kind"]].model_validate(rec["payload"]))
    return records


class Catalog:
    def __init__(self) -> None:
        self.styles = {r["style_code"]: r for r in read_csv(MASTER / "styles.csv")}
        self.skus = {r["sku"]: r for r in read_csv(MASTER / "sku_colour.csv")}
        self.sku_sizes = {r["sku_size"]: r for r in read_csv(MASTER / "sku_size_ean.csv")}
        self.assortment = {(r["store_id"], r["sku"]) for r in read_csv(MASTER / "store_assortment.csv")}

    def check(self, store: str, target: str, level: str) -> SourceRef:
        """The target exists at its level and the store carries it; returns its catalog row ref."""
        if level == "style":
            assert target in self.styles, target
            assert any(sku.startswith(target + "-") for s, sku in self.assortment if s == store)
            return file_ref(MASTER / "styles.csv", f"style_code={target}")
        if level == "sku":
            assert target in self.skus and (store, target) in self.assortment, target
            return file_ref(MASTER / "sku_colour.csv", f"sku={target}")
        assert level == "sku_size" and target in self.sku_sizes, target
        assert (store, self.sku_sizes[target]["sku"]) in self.assortment, target
        return file_ref(MASTER / "sku_size_ean.csv", f"sku_size={target}")


def build_links(observations: dict[str, Observation], catalog: Catalog) -> list[EntityLink]:
    assert set(LINKS) == set(observations), "one link per DATA-01a observation"
    links = []
    for obs_id, label in LINKS.items():
        obs = observations[obs_id]
        assert obs.store_id is not None
        candidates = [
            LinkCandidate(target_id=t, level=lv, method=m, score=s, **SCORE)
            for t, lv, m, s in label.get("candidates", ())
        ]
        catalog_refs = [catalog.check(obs.store_id, c.target_id, c.level) for c in candidates]
        links.append(
            EntityLink(
                id=f"link-{obs_id.removeprefix('obs-')}",
                **derived([obs], catalog_refs),
                observation_id=obs_id,
                status=label["status"],
                level=label.get("level"),
                target_id=label.get("target_id"),
                candidates=candidates,
                decided_by=label["decided_by"],
                rationale=label["rationale"],
            )
        )
    return links


def build_relations(
    observations: dict[str, Observation], documents: dict[str, SourceDocument]
) -> list[EvidenceRelation]:
    relations = []
    for label in RELATIONS:
        src, dst = observations[label["from"]], observations[label["to"]]
        docs = [documents[dst.document_id], documents[src.document_id]]
        relations.append(
            EvidenceRelation(
                id=label["id"],
                **derived([src, dst]),
                from_ref=ref(src),
                to_ref=ref(dst),
                relation=label["relation"],
                basis=label["basis"],
                evidence_refs=[ref(d) for d in docs],
            )
        )
    return relations


def local_midnight(day: date, store: str) -> datetime:
    return datetime.combine(day, time(0), tzinfo=ZoneInfo(TZ[store]))


def build_cases(
    observations: dict[str, Observation],
    documents: dict[str, SourceDocument],
    links: dict[str, EntityLink],
    relations: dict[str, EvidenceRelation],
) -> list[Case]:
    copies = {r.from_ref.id for r in relations.values() if r.relation == "duplicates"}
    validity = timedelta(days=POLICY["decay"]["max_validity"]["value"])
    cases = []
    for label in CASES:
        obs = [observations[o] for o in label["supporting"]]
        assert {o.store_id for o in obs} == {label["store_id"]}
        docs = [documents[i] for i in dict.fromkeys(o.document_id for o in obs)]
        received = [d.available_at for d in docs]
        assert all(r is not None for r in received)
        independent = [o.available_at for o in obs if o.id not in copies]
        starts = [o.period_start for o in obs if o.period_start is not None]
        ends = [o.period_end for o in obs if o.period_end is not None]
        last_received = max(received)
        # An ongoing fact (no end) is known only up to its latest document.
        window_end = max(ends) if ends and len(ends) == len(obs) else last_received
        window_start = min(starts) if starts else min(received)
        last_independent = max(independent)
        valid_until = last_independent + validity if label["valid_until"] else None
        rels = [relations[r] for r in label["relations"]]
        own_links = [links[f"link-{o.id.removeprefix('obs-')}"] for o in obs]
        inputs = [*obs, *own_links, *rels]
        cases.append(
            Case(
                id=label["id"],
                **derived(inputs),
                case_type=label["case_type"],
                store_id=label["store_id"],
                scope_level=label["scope_level"],
                scope_id=label["scope_id"],
                window_start=window_start,
                window_end=window_end,
                status=label["status"],
                owner=OWNERS[label["case_type"]],
                priority=label["priority"],
                priority_reason=label["priority_reason"],
                decision_due_at=valid_until if label["decision_due"] == "valid_until" else None,
                first_available_at=min(received),
                last_received_at=last_received,
                last_independent_evidence_at=last_independent,
                valid_until=valid_until,
                supporting=[ref(o) for o in obs],
                contradicting=[],
                n_documents=len(docs),
                n_origin_groups=len(docs) - len({o.document_id for o in obs if o.id in copies}),
                n_unknown_origins=0,
                blocking_uncertainties=label["blocking_uncertainties"],
                context_refs=[ref(r) for r in (*own_links, *rels)],
            )
        )
    return cases


def vintage(store: str, as_of: datetime) -> tuple[Path, datetime]:
    """Latest forecast run available at `as_of` and its availability instant."""
    tz = ZoneInfo(TZ[store])
    best = None
    for path in sorted(FORECASTS.glob("fcst_sku_store_run_*.csv")):
        run = date.fromisoformat(path.stem.removeprefix("fcst_sku_store_run_"))
        available = datetime.combine(run + timedelta(days=1), VINTAGE_AVAILABLE_AT, tzinfo=tz)
        if available <= as_of:
            best = (path, available.astimezone(UTC))
    assert best is not None
    return best


def weekly_units(path: Path, store: str, sku: str) -> dict[date, float]:
    rows: dict[date, set[float]] = {}
    for r in read_csv(path):
        if r["store_id"] == store and r["sku"] == sku:
            rows.setdefault(date.fromisoformat(r["week_start"]), set()).add(float(r["fcst_units"]))
    # Exact duplicate rows exist in the source; conflicting values for one week would not.
    assert all(len(values) == 1 for values in rows.values()), (path.name, store, sku)
    return {week: values.pop() for week, values in rows.items()}


def build_forecasts(cases: list[Case]) -> list[ForecastAdjustment]:
    by_id = {c.id: c for c in cases}
    days = POLICY["horizon"]["days"]["value"]
    adjustments = []
    for label in CASES:
        case = by_id[label["id"]]
        assert case.store_id is not None and case.available_at is not None
        store = case.store_id
        path, available = vintage(store, case.available_at)
        run_date = path.stem.removeprefix("fcst_sku_store_run_")
        d = case.available_at.astimezone(ZoneInfo(TZ[store])).date()
        start = d + timedelta(days=1)
        for sku in label["forecast_skus"]:
            weekly = weekly_units(path, store, sku)
            daily = disaggregate(weekly, start, days)  # MIL01 has no closed weekday
            assert daily.status == "computed", daily.reasons
            weeks = sorted({p.week_start for p in daily.points})
            locator = f"store_id={store};sku={sku};week_start=" + "|".join(map(str, weeks))
            baseline = ArtifactRef(
                kind="ForecastVintage", id=f"{path.stem}/{store}/{sku}", version=run_date
            )
            fields = derived([case], [file_ref(path, locator)], [baseline])
            assert fields["available_at"] >= available
            series = []
            for p in daily.points:
                assert p.baseline is not None
                flat = ScenarioValues(low=p.baseline, base=p.baseline, high=p.baseline)
                series.append(
                    ForecastPoint(date=p.day, baseline=p.baseline, latent=flat, servable=flat)
                )
            adjustments.append(
                ForecastAdjustment(
                    id=f"fc-{store.lower()}-{sku.lower()}-{start:%Y%m%d}",
                    **fields,
                    case_ids=[case.id],
                    store_id=store,
                    sku=sku,
                    baseline_ref=baseline,
                    horizon_start=start,
                    horizon_end=start + timedelta(days=days - 1),
                    status="unchanged",
                    reason=label["forecast_reason"],
                    series=series,
                    components=[],
                    proposal_source="code",
                )
            )
    return adjustments


def input_version_hash(refs) -> str:
    keys = sorted(f"{r.kind}:{r.id}@{r.version}" for r in refs)
    return "sha256:" + hashlib.sha256("\n".join(keys).encode()).hexdigest()


def fmt(value: float) -> str:
    return f"{value:.1f}"


def build_report(
    cases: list[Case],
    forecasts: list[ForecastAdjustment],
    observations: dict[str, Observation],
    links: dict[str, EntityLink],
    relations: dict[str, EvidenceRelation],
    catalog: Catalog,
    as_of: datetime,
) -> Report:
    """Per-owner brief. Every number is rendered from a cited field (RFC §4.8.1)."""
    citations: list[Citation] = []
    cited: dict[str, SourceRecord] = {}
    copies = {r.from_ref.id for r in relations.values() if r.relation == "duplicates"}

    def cite(record, field: str | None = None, unit=None, **kw) -> str:
        citations.append(Citation(ref=ref(record), field=field, unit=unit, **kw))
        cited.setdefault(record.id, record)
        return f"[{len(citations)}]"

    def label(case: Case) -> str:
        if case.scope_id is None:
            return f"{case.store_id} · product not identified"
        code = case.scope_id
        style = catalog.styles[code.split("-")[0]]["style_name"]
        parts = code.split("-")
        if len(parts) >= 2:
            style += " " + catalog.skus["-".join(parts[:2])]["color_name_en"]
        if len(parts) == 3:
            style += f" size {parts[2]}"
        return f"{case.store_id} · {style} ({code})"

    lines = [f"# Brief by office, as of {as_of:%Y-%m-%d %H:%M} UTC", ""]
    for owner in sorted({c.owner for c in cases}):
        lines += [f"## {owner}", ""]
        for case in sorted(cases, key=lambda c: (c.priority != "high", c.id)):
            if case.owner != owner:
                continue
            head = f"- **{label(case)}**: {case.status}, priority {case.priority} {cite(case)}."
            body = []
            for obs_ref in case.supporting:
                obs = observations[obs_ref.id]
                if obs.id in copies:  # a certain copy is counted once, via its original
                    continue
                q = obs.quantity
                scope = {"store_id": str(obs.store_id)}
                period = {"period_start": obs.period_start, "period_end": obs.period_end}
                if q.kind == "exact":
                    body.append(
                        f"{obs.kind.replace('_', ' ')} {q.value:g} {q.unit} "
                        + cite(obs, "quantity.value", q.unit, scope=scope, **period)
                    )
                else:
                    body.append(
                        f"{obs.kind.replace('_', ' ')}, quantity {q.kind} "
                        + cite(obs, "quantity.kind", scope=scope, **period)
                    )
                link = links[f"link-{obs.id.removeprefix('obs-')}"]
                if link.status == "ambiguous":
                    names = " or ".join(c.target_id for c in link.candidates)
                    body.append(f"product is {names} {cite(link, 'candidates')}")
            if case.n_documents > case.n_origin_groups:
                body.append(
                    f"{case.n_documents} documents from {case.n_origin_groups} origin "
                    + cite(case, "n_origin_groups")
                )
            for fc in forecasts:
                if case.id not in fc.case_ids:
                    continue
                total = sum(p.baseline or 0.0 for p in fc.series)
                body.append(
                    f"baseline {fc.sku} {fc.horizon_start:%m-%d}..{fc.horizon_end:%m-%d} "
                    f"{fmt(total)} units, {fc.status} "
                    + cite(fc, "series.baseline", "units", scope={"sku": fc.sku})
                )
            for u in case.blocking_uncertainties:
                body.append(f"open: {u}")
            lines.append(head)
            lines += [f"  - {b}" for b in body]
        lines.append("")
    fields = derived(list(cited.values()))
    assert fields["available_at"] <= as_of
    return Report(
        id=f"report-by-office-{as_of:%Y%m%dT%H%M}",
        **fields,
        as_of=as_of,
        view="by_office",
        markdown="\n".join(lines).rstrip() + "\n",
        citations=citations,
        generated_by="template:fixture.data01b.v1",
        input_version_hash=input_version_hash(fields["input_refs"]),
    )


def record(dto) -> dict:
    return {"kind": type(dto).__name__, "payload": dto.model_dump(mode="json")}


def write(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    documents = {d.id: d for d in load_folder("documents") if isinstance(d, SourceDocument)}
    observations = {o.id: o for o in load_folder("observations")}
    catalog = Catalog()
    links = build_links(observations, catalog)
    relations = build_relations(observations, documents)
    cases = build_cases(
        observations, documents, {k.id: k for k in links}, {r.id: r for r in relations}
    )
    forecasts = build_forecasts(cases)
    # The fixture run's as_of is the latest availability among all fixtures (PLT-03).
    as_of = max(r.available_at for r in [*documents.values(), *observations.values()])
    report = build_report(
        cases,
        forecasts,
        observations,
        {k.id: k for k in links},
        {r.id: r for r in relations},
        catalog,
        as_of,
    )

    for folder in ("links", "cases", "forecast", "reports"):
        for old in (OUT / folder).glob("*.json"):
            old.unlink()
    for link in links:
        write(OUT / "links" / f"{link.id}.json", [record(link)])
    write(OUT / "links" / "relations.json", [record(r) for r in relations])
    for case in cases:
        write(OUT / "cases" / f"{case.id}.json", [record(case)])
    for fc in forecasts:
        write(OUT / "forecast" / f"{fc.id}.json", [record(fc)])
    write(OUT / "reports" / f"{report.id}.json", [record(report)])
    print(len(links), "links,", len(relations), "relations,", len(cases), "cases,")
    print(len(forecasts), "forecasts, 1 report")


if __name__ == "__main__":
    main()
