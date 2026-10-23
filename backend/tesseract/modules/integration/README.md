# Integration evidence relations

`int.dedup` runs after `int.link` and writes only `EvidenceRelation` artifacts. It
does not remove or edit documents, observations or quantities. It reads the current
run through the repository and validates each quote against its document version
and segment before relating facts.

- `duplicates`: identical facts/quotes in an exact body resend with matching sender
  and business date (or identical source hash), or an exact quoted fact with an
  explicit parent document. A forward flag, sender, product link or thread alone
  does not establish a copy.
- `possibly_same_episode`: compatible store/product/type with overlapping or
  unknown periods. Different quantities and negation do not establish independence.
  Keep both facts; do not add their quantities. Known disjoint periods remain
  separate episodes.
- `supersedes` / `retracts`: an explicit replacement or withdrawal in the fact's
  own unquoted evidence, with exactly one compatible fact in its explicit parent
  document. Known periods, product scope and units must match. Recognition currently
  covers a conservative set of Italian/English phrases; unresolvable correction
  targets, negation, hypothetical statements and questions produce an abstention
  and a degraded result. Only affirmative supported statements can suppress facts.
  Other wording/languages remain separate observations for human verification.

Every relation retains endpoint versions, evidence references and all inspected
input artifacts. Availability is the maximum of those inputs, including the new
correction's availability, rather than its historical event date. The relation is
therefore invisible to earlier snapshots. Repeated execution is idempotent.
Segments resolve through the observation's versioned input references, and entity
links apply only to the exact observation version they reference. Missing or
ambiguous version pins abstain; a newer version never silently replaces a pin.

The pure `state_at` helper demonstrates the consumer rules: union only certain
copies; choose the earliest member as the representative and keep its original
period/availability for age; apply corrections only when their endpoint versions
and relation are visible; suppress all copies of a corrected target. Withdrawal
statements are not new demand, and correction chains do not revive earlier facts.
Possible overlaps mark active representatives as non-additive. No quantity is
summed or imputed. Document count and origin-group count remain distinct; groups
are provenance groups, not statistically independent demand observations.

Downstream modules consume the contract artifacts through the repository, following
these rules; they must not import another module or treat absent overlap relations
as proof that unknown episodes are independent. The helper's dataclasses are local
views, not new persisted contracts.

# Cases

`int.cases` runs after `int.dedup` and writes only `Case` artifacts. Each observation kind
maps to a case type with an owner in `config/domain.yaml` (`stockout`/`low_stock` →
`unmet_demand`, `demand_up/down` → `demand_shift`, `other` → `unknown`); `sales_figure` and
`local_event` open no case. Ambiguous, unlinked or missing links keep their own `verify`
case with `scope=unknown`, citing the link and its candidates; they are never merged.
Certain copies stay in one case and count as one origin; corrected or retracted facts are
not supporting evidence; negated facts are `contradicting`. A later report joins the open
case of the same store, type and scope only within `policy.decay.max_validity` of its last
independent evidence. INT-04 adds structured stock conflicts and optional source-backed decision deadlines below.

## Structured stock conflicts and deadlines (INT-04)

`int.cases` v2 optionally consumes ERP stock and `StockFact` artifacts after
`src.erp` / `sys.client`. The pure `reconciliation.py` helper matches the exact
store and linked SKU or SKU-size, and only compares a snapshot inside an
explicit stockout period. ERP EOD rows require an explicitly stated whole local
day (midnight through 23:59:59); a snapshot from yesterday never contradicts an
intraday statement today. Missing dates, timezone or identity abstain from the
comparison. Low stock has no invented threshold. Positive stock is a **potential**
conflict, not evidence that unmet demand is false or that all sizes are sellable.

Matching positive stock is retained in `contradicting`, with versioned input and
context references, raw source locators, and a blocking explanation; an open or
monitoring case becomes `verify`. Zero physical stock can support an exact-size
stockout. Zero ATP/sellable is not equated to zero physical stock. A single empty
size never establishes a whole-SKU stockout. Quantities, document/origin counts,
independent confirmation time and validity are preserved. No rule closes a case
because of silence, expiry or a later stock snapshot.

### Optional normalized decision calendars

The current ERP loader and stock artifacts do not publish departure/receiving
calendars or an actionable `required_by`. Consequently, the default is
`decision_due_at=null` with a specific uncertainty. An episode end or scenario
expiry is never substituted for a logistics deadline.

A caller that has checked both calendars and the required-by source may supply
`int.cases.params.decision_calendars` in the immutable run snapshot. This is a
normalized input, not an automatic raw-logistics parser. Each entry names one
exact case and carries its knowledge time and source hashes/locators:

```json
{
  "decision_calendars": [{
    "case_id": "case-mil01-j20931a00012-999-20261002",
    "available_at": "2026-10-02T16:00:00Z",
    "required_by": "2026-10-05T08:00:00Z",
    "source_refs": [{
      "uri": "generated/sources/systems/logistics/calendar-example.csv",
      "content_hash": "<hash of the actual source>",
      "locator": "<required-by and departure/receiving rows>"
    }],
    "slots": [{
      "cutoff_at": "2026-10-02T17:00:00Z",
      "sellable_at": "2026-10-05T07:00:00Z"
    }]
  }]
}
```

The path and values above are illustrative, not an existing dataset fixture.
`cutoff_at` is the decision cutoff for a calendar-confirmed pickup; `sellable_at`
already includes receiving hours, closures and any delay before stock can be sold.
All instants require timezones. Slots must be ordered cutoff ≤ sellable. Future
calendar inputs are ignored, conflicting entries abstain, and source references
are retained on the case. The deadline is the cutoff of the first remaining
useful sellable arrival, requiring arrival ≤ `required_by`. A missed cutoff skips
to the next feasible slot; if none exists the deadline remains null. It does not
prove stock feasibility or authorize a movement. Unknown product/store scope
keeps a null deadline even if a calendar is supplied.

## Optional embedding retrieval and dimension comparison (INT-05)

`int.link` v2 accepts `use_embeddings: true` and `embedding_dimensions: 512|2048`
(default 512). Embeddings remain off by default. `llm: false` disables the final
choice, independently of candidate retrieval. A requested embedding path without
an LLM client is blocked. Provider/cache/vector failures are explicit module
errors and retain the deterministic fuzzy result with degraded status.

The retriever receives the observation-date catalog, prefers the store assortment,
and builds source-derived labels from style/colour aliases and ERP category,
subcategory and gender. It cannot add future-launched catalog identities. Catalog
vectors are reused in memory within the run and persist through the existing
LLM client's record/replay cache. Keys include dimensions, provider/model/payload
and a fingerprint of the ordered catalog IDs and labels. No new vector store or
external service is introduced.

Existing confident fuzzy links and blocking colour/size constraints bypass
embedding retrieval. For other mentions, fuzzy and cosine rankings are combined
by equal-weight reciprocal rank fusion, `sum(1/(60+rank))`, with deterministic
ID tie-breaking and at most `top_k` results. Scores are normalized to 0–100 against
the maximum two-list RRF score: they are rank scores, not fuzzy similarities or
probabilities. Raw cosine is never compared to or maximized with a fuzzy score.
Flags are retained. Semantic-only candidates stay ambiguous until the existing
constrained LLM choice or human review; one semantic candidate is not automatically
accepted. Nonpositive similarities are excluded, without claiming a calibrated
acceptance threshold.

### Reproduce a dimension comparison

`embeddings.compare_dimensions(queries, catalog, client, top_k=8,
descriptions=...)` runs fuzzy-only, fused-512 and fused-2048 retrieval on the same
catalog, caller-supplied dev labels, and k. `RetrievalQuery` contains a mention,
`expected_ids` at the same identity granularity as the desired candidates, an
optional explicit size and optional store assortment. Empty `expected_ids` marks
a negative. For example, with an existing time-filtered dev catalog and configured
`LLMClient`:

```python
from tesseract.modules.integration.embeddings import RetrievalQuery, compare_dimensions

# Labels must be manually checked against permitted dev sources, not answer keys.
# Fill these from the dev sample; do not use this placeholder as measured data.
queries = [RetrievalQuery(mention=dev_mention, expected_ids=(dev_sku,))]
comparison = compare_dimensions(
    queries, dev_catalog, client, top_k=8, descriptions=source_descriptions
)
```

The result includes `n`, positive/negative denominators, recall@k (a hit if any
acceptable ID is retrieved), abstention count/rate and incorrect accepted links.
Recall is null when there are no positives. Abstention refers to the retrieval
stage before optional LLM tie-breaking, making the two dimensions comparable.
Already-confident fuzzy links are retained in every arm. Record through the
existing client once, then compare in replay mode; a replay miss propagates and
produces no substitute metrics. Use the same fixed dev sample for both dimensions;
hold-out labels, `ground_truth`, generator files and tuning on hold-out remain
forbidden. This implementation supplies the comparison; the synthetic vector
tests are not an observed Fastweb recall result and justify no dimension-quality
claim. Keep 512 and the default embedding-off configuration until an actual dev
comparison supports changing them.
