# Frozen hold-out evaluation protocol (REL-01b)

Status: preparation for #211, not freeze approval or measured results. This document
reuses #124 (reading), #125 (lead time), #138 (forecast) and #218 (placebo).
No hold-out source content, labels or hidden answers were inspected to prepare it.
No final evaluation has run. Commands below are execution instructions for the
post-freeze owners, not evidence that those commands have been executed.

## 1. Ownership and execution gates

Lane D owns this protocol; lane A must review reading/linking semantics. #211
owns approval, integrated #115 evidence, final candidate revalidation and the
reviewed `freeze-g3` tag. #126 executes reading, #127 executes lead time, and #128
publishes their evidence and any eligible forecast comparison. These tasks remain
blocked until the real #211 handoff; merging this document does not unblock them.

Before any hold-out inspection, #211 must bind all items in section 3, approve the
sample and commands, and resolve the interface status of #223. That assigned work
is not modified here. Its paired placebo diagnostic must be revalidated against
the merged evaluator before final execution. Never present the older pooled
placebo rates as significance or proof that alerts are coincidences.

Only evaluator functions in `eval/` may open answers. Product runs must use the
`eval product` read-isolated launcher, with a clean `data/` namespace containing
no evaluation outputs or labels. Mock systems run separately (`make mocks`).
Landlock is read isolation, not network/write isolation: record external service
versions and use frozen/replay responses. Never import evaluator code into product
code or move answers into prompts, fixtures, RAG, caches or the product database.

## 2. Preselected sample and historical clocks

The authoritative split is `config/eval_split.yaml` / RFC §5.1, overriding the
README's suggestion that unlisted stores become dev:

- Dev: MIL01, MIL02, PAR01, LON01, MUN01, MAD01, NYC01, TYO01, SEL01, SHA01,
  HKG01, SYD01. Tuning is confined to these stores.
- Hold-out: ROM01, PAR02, LON02, ZRH01, NYC02, TYO02, SEL02, BJS01, TPE01,
  DXB01. These ten stores are the proposed final reporting universe.
- Unassigned stores are context/donors only, under the frozen time rules; they
  never become tuning or metric stores implicitly.

Pre-register the historical period **2026-08-31 through 2026-10-21**, inclusive,
with explicit per-store aware replay origins at 20:00 local on each day, using
IANA zones from `stores.csv`. #211 must confirm this full coverage is actually
exportable. If budget requires a subset, approve and enumerate it *before*
inspection, with rationale and expected file/store-day counts; narrow the metric
period to comparable coverage. Do not score a full-period lead-time claim from a
single final-day reading slice. Document missing/open/closed store-days without
selecting only days on which the product detected something.

For reading, select all email files in the approved store/day windows, including
no-signal messages, duplicates, forwards, corrections and noise. Freeze the
filename-only sample before annotating. File selection must follow availability
from email Date headers, not a claim, answer key or a misleading subject date.
Hold-out annotations are written once by lane A after the freeze, covering all
claims in that sample, including negations/ambiguities. They cannot be inferred
as complete claim labels from an answer-key index alone. Never use dev labels as
hold-out labels. Known scenario descriptions mean this is a store hold-out,
not a claim that the storylines were unknown to the team.

At evening D, enforce `generated/README.md` §4 at row level:

| Input | Latest admissible data |
|---|---|
| Sales, POS, KPI, traffic | Business date ≤ D−1, including posting/certification lags |
| Inventory | Snapshot date ≤ D−1 |
| Forecast | Run vintage ≤ D |
| Email | Date-header instant ≤ origin in the store's local zone |
| Internal/system facts | Own availability timestamp ≤ origin |
| Weather | Observation date ≤ D; forecast issue instant ≤ origin |
| Tourism, social, news | Publication/collection availability ≤ origin |
| Reports | Both period end and issue date ≤ origin |

Keep aware timestamps; compare instants in UTC and advance local *calendar* days
through DST. A file hash does not prove row-level availability. Replay export
must retain the origin and input provenance used for each decision. Do not credit
later corrections or later-resolved scopes to earlier decisions without disclosing
that limitation (section 6). Synthetic extensions, new audio and simulated
clarification answers are separate scenarios, never historical forecast targets.

## 3. Freeze handoff: values #211 must supply

No values in this list are certified by this preparation task. Archive a reviewed
experiment record outside the bundle, then link it from #211:

| Required binding | Content / evidence |
|---|---|
| Candidate | Full reviewed commit SHA, `freeze-g3` target, clean-tree status, evaluator SHA if different, protocol revision/hash, reviewer and approval time |
| Integration | #115 replay evidence and #123 safety evidence on this candidate, #226 gate audit disposition, actual `make check` log |
| Selection | Split snapshot/hash; store/day/file manifest, expected counts, local zones, aware origins, scope and exclusions; preselection timestamp |
| Universe | Reading file list; lead-time stores/period; explicit forecast store×SKU-colour×timezone list if forecast is enabled, including no-alert/decoy products |
| Product identity | Frozen RunSpec(s), run ids, module manifests and versions/enabled states, parameters, scenario ids, model ids/versions, prompt contents/hashes, aliases/domain/pipeline configs, dependency lockfiles and runtime versions |
| Inputs | Every consumed source path plus SHA-256 (including baseline warm-up, master data, ERP, relevant donor/system facts and responses), extraction/derived-input provenance and availability rules |
| Caches | LLM/ASR cache entry path+content-hash inventory and aggregate digest, cache-key/model/endpoint versions, selected entry count, replay miss policy, replay log; recorded vs fixture vs unavailable components |
| Exports | Exact predictions/cases/options paths, SHA-256 and counts per kind/origin; bundle paths and manifest digests recorded outside each bundle before answers are opened |
| Scoring | Exact command transcript, reading-label plan/path/schema, baseline settings, period and T_end convention, forecast scenario or explicit unavailable reason, merged #223 SHA/interface validation |
| Evidence storage | New experiment directory and append-only output filenames, source/config/catalog integrity check logs, post-freeze answer/label hash receipts, report owner |

Never include secrets, key material, `.env` or `.secrets/` in these records. Cache
fingerprints are file/entry identity, not credentials or a transcript printed to
chat. Preserve the exact selected cache snapshot without oracle material.

The harness snapshots configs and exports but only records source hashes; its
`FrozenRun` verifier **does not rehash live sources**. Lead-time baselines and
reading catalog checks read live sources. Before scoring, compare the complete
selected input inventory against its recorded digests, or use an immutable source
snapshot. Include the evaluator's baseline inputs even if the product did not
consume them. Capture split/catalog hashes too: current scorers use those live
files. Cache, code and lockfile fingerprints require the separate experiment
record; `freeze --configuration` only accepts paths under `config/` or `backend/`.

### How #211 produces the freeze record

`scripts/freeze_record.py` (REL-01d) writes that experiment record mechanically.
`record` binds the candidate, runtime, prompt/config/RunSpec, source, evaluator-input,
cache and export identities. `append` chains bundle manifest digests, the approval
and post-freeze label hash receipts (values only). `verify` rehashes the live inputs
and fails on drift. Sequence: candidate SHA → `make check` log → REL-01c exports →
`record` → `eval freeze` bundles → `append --bundle` → `verify` → human review →
`append` approval → tag `freeze-g3`. The exact commands are in
[`freeze-runbook.md`](freeze-runbook.md).

## 4. Frozen export contracts

All three export files are JSON arrays of objects. Empty arrays are structurally
valid, but do not establish that a module ran or that a metric is available.
Freeze distinct reading and forecast bundles if their protocols/predictions differ;
connect both to the same candidate and origins. A reading universe with `sku: "*"`
is not a valid explicit forecast universe.

| Export | Required fields / interpretation |
|---|---|
| Reading predictions | `{kind, payload}` records: SourceDocument `id, uri, text`; URI `dataset://store_emails/<STORE>/<file>`; Observation `id, document_id, kind, evidence[0].{char_start,char_end,quote}, negated, product_mention`; EntityLink `observation_id, status` and for accepted links `target_id, level`; ModuleRun `module_id, result` with status/errors/abstentions/counts. Retain RunSpec and Segment records and all DTO provenance. |
| Lead-time cases | Raw Case or `{payload: Case}`; `id, store_id, scope_level, scope_id, case_type, status, first_available_at`; optional `decision_due_at`; `source_refs[].uri` for noise audit. Require aware timestamps, valid catalog scope and first-availability provenance. One historical case identity with its earliest valid alert; do not concatenate repeated snapshots of the same case as new alerts. Preserve revisions separately. |
| Forecast predictions | Native ForecastAdjustment or `{as_of, payload}`; `producer` = `fc.baseline` / `fc.overlay`, `store_id, sku, scenario_id, status, available_at, computed_at, baseline_ref, series`. Daily points: `date, baseline`, and overlay `latent.{low,base,high}`. Explicit wrapper `as_of` is required if export compute time differs from historical origin. |
| Options | Native exported options with provenance; retained for audit. These evaluators do not independently certify option feasibility, donor harm or execution outcomes. |

Retain the full DTOs rather than reducing them to this minimum. Frozen protocols
must supply nonempty `run_id, split, stores, origins, universe, sampling_criterion,
models, parameters`. Bind actual module/config/source identities in parameters.
For forecast add `forecast.scenario` (one of low/base/high chosen ex ante),
`forecast.scenario_id: historical`, unique aware origins and unique universe pairs
with `timezone`. Require daily baselines for every origin×store×SKU, including
unchanged/no-alert products. Computed overlays must match baseline vintage and
values and have complete selected-scenario latent quantities. Future or unknown
input availability fails; nonhistorical scenarios cannot enter this comparison.

## 5. Command runbook (after #211 approval only)

Run from repository root. The shell variables below are deliberately unbound;
#211 must provide actual reviewed paths/digests, not placeholder hashes. `P` is
`backend/.venv/bin/python`. `E` is a new directory under `data/` for this experiment;
`B_READING`, `B_LEAD`, `B_FORECAST` are bundle paths under `data/`, with corresponding
`SHA_READING`, `SHA_LEAD`, `SHA_FORECAST` externally recorded manifest digests.
`START=2026-08-31`, `END=2026-10-21` unless the approved protocol narrows coverage.
Export these variables for the Python invocation below. `LABELS` names the reviewed
hold-out YAML under `eval/labels/`; `LABEL_SHA` is its recorded SHA-256 after annotation.
No label file is opened as part of this preparation.

### 5.1 Product isolation and bundle creation

Use #115's integrated Core runner and approved frozen RunSpecs for the actual
candidate; the reading-only runner produces empty cases/options and cannot
substitute for the integrated lead-time export. Its supported invocation is:

```sh
# Execution example: paths/run id must be supplied by #211.
$P -m eval product -- -m tesseract.modules.ingestion.reading_export run \
  --run-spec "$READING_SPEC_FROM_BACKEND" --run-id "$READING_RUN_ID" \
  --out "$READING_EXPORT_FROM_BACKEND"
```

The launcher changes cwd to `backend/`; spec/output arguments above must be
absolute or relative to that directory (for example `../data/...`). Explicitly
set replay mode in the run environment; cache misses are errors. Any authorized
recording uses sources only and precedes the evaluated replay/export; never add
answers or change prompts to fill misses after inspecting hold-out scores.

For each bundle, supply the approved protocol and all three matching exports.
This Python wrapper expands complete newline-separated source/config path lists
without shell word-splitting. Lists contain repository-relative paths, no headers.
`PROTOCOL`, `EXPORT_DIR`, `BUNDLE`, `SOURCE_LIST`, `CONFIG_LIST` are #211 bindings;
use a fresh bundle name for each call. Save stdout to a new external receipt.

```sh
$P - <<'PY'
import json
import os
from pathlib import Path
from eval.harness import freeze
root = Path.cwd()
paths = lambda name: [Path(p) for p in Path(os.environ[name]).read_text().splitlines() if p]
exports = Path(os.environ['EXPORT_DIR'])
print(freeze(
    Path(os.environ['BUNDLE']),
    json.loads(Path(os.environ['PROTOCOL']).read_text()),
    {kind: exports / f'{kind}.json' for kind in ('predictions', 'cases', 'options')},
    paths('SOURCE_LIST'), paths('CONFIG_LIST'), root=root,
))
PY
```

This calls the same library as `eval freeze`; the CLI equivalent has mandatory
`--protocol`, `--predictions`, `--cases`, `--options`, repeated `--source` for every
selected input, repeated `--configuration` for every selected config/prompt.
Never overwrite a bundle. Record the manifest digest externally before scoring.

### 5.2 #126: reading/linking evaluation

**Current interface constraint:** `eval reading` and `eval reading-sample` load
`reading_dev_v1.yaml` unconditionally; there is no `--labels` or hold-out switch.
Do not run them as a hold-out evaluation. Use the existing library with an explicit
hold-out label path, after lane A reviews the annotation schema and bindings:

```sh
$P - <<'PY'
import json
import os
from pathlib import Path
from eval.harness import FrozenRun
from eval.reading import catalog_ids, load_labels, score
run = FrozenRun(Path(os.environ['B_READING']), os.environ['SHA_READING'])
protocol = run.manifest['protocol']
labels, label_sha = load_labels(Path(os.environ['LABELS']))
assert label_sha == os.environ['LABEL_SHA'], 'label fingerprint mismatch'
assert protocol['split'] == labels['sample']['split'] == 'holdout'
assert set(protocol['stores']) == {name.split('/')[0] for name in labels['files']}
# #211 records the approved filename-only sample in the protocol.
assert sorted(protocol['reading_files']) == sorted(labels['files'])
result = score(labels, run.artifacts['predictions'],
               catalog_ids(Path('generated/sources/erp/master_data')))
result.update(manifest_sha256=run.manifest_sha256,
              labels_sha256=label_sha, protocol=protocol)
out = Path(os.environ['E']) / 'reading.json'
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
PY
```

`reading_files` is an additional protocol field required by this runbook (not
currently validated by the harness). The wrapper opens no answers itself:
`load_labels` / `score` are in `eval/`. Record the label hash and annotation review
alongside results. A future CLI improvement would require a separate task, not
changes to #223 or product code in this task.

### 5.3 #127: lead-time evaluation and oracle receipt

After source/catalog/split integrity checks, record the exact keys the current
lead-time scorer uses, then execute on the approved common period:

```sh
$P -m eval verify "$B_LEAD" --sha256 "$SHA_LEAD" \
  --key scenario/events.json \
  --key answer_keys/emails/emails_en_intl_index.csv \
  --key answer_keys/emails/emails_fr_index.csv \
  --key answer_keys/emails/emails_it_index.csv \
  --key answer_keys/emails/emails_ko_index.csv \
  --output "$E/lead-time-inputs.json"
$P -m eval lead-time --bundle "$B_LEAD" --sha256 "$SHA_LEAD" \
  --start "$START" --end "$END" --output "$E/lead-time.json"
```

The bundle protocol selects stores/split; `--split holdout` alone is a
baseline-only run and is not the frozen pipeline evaluation. Baseline-only
results cannot substantiate a pipeline comparison. Reconfirm keys/output schema
and common observation-period boundaries after #223 merges.

### 5.4 #128: optional forecast comparison

Execute only if the fixed-universe requirements in sections 4 and 7 pass:

```sh
$P -m eval forecast "$B_FORECAST" --sha256 "$SHA_FORECAST" \
  --output "$E/forecast-errors.json"
```

The scorer validates predictions before opening the specific demand CSV and
records its hash in the output. Do not substitute sales, event expectations or
synthetic targets for realised demand. If prerequisites are absent, record
`unavailable` with the missing inputs instead of running a selected-case proxy.

### 5.5 Verification performed during REL-01b

Command syntax was checked with `python -m eval --help` and `freeze`, `verify`,
`reading`, `lead-time`, `forecast` subcommand help. Library wrappers are checked
against the current signatures and with temporary synthetic data; examples do not
read real answers. `make check` is required before this PR becomes ready. These
checks validate interfaces/regressions, not candidate freeze or measured efficacy.

## 6. Reading and lead-time reporting rules

For reading, publish overall and per-language file counts, label counts, required
labels, observations, matched observations, matched required/all labels, missed
required labels, redundant matches, negation errors, false positives, accepted-link
errors and every exclusion/unread reason. Add counts by document/noise type where
annotations support them; otherwise mark that breakdown unavailable.

- Observation precision = matched observations / observations on sampled documents.
  Recall = required labels matched at least once / all required labels. Also show
  all-label recall. A coarse observation can match multiple labels; redundant
  observations do not become false positives under the existing scorer.
- Missing exported documents remain in required-label recall as misses. Extractor
  abstentions/unread documents remain in the main denominator. The separate
  `recall_required_read_files` subtracts required labels of extractor-unread files;
  it is a conditional diagnostic, not the headline recall or blanket exclusion
  of all missing documents. Report exclusions next to coverage, never silently
  remove them to improve the score.
- `links.product_labels` is actually the number of *matched observations with an
  expected product*, not all independent product labels. Accepted-link error
  rate = errors / accepted links in that subset. Accepted and abstention rates
  divide by that subset; abstention = ambiguous + unlinked. Report not_product,
  no_link and coarser-correct links separately. Missing observations are already
  penalised by reading recall, not by this conditional link denominator.
- Zero denominators are undefined (`null`), never perfect accuracy. Evidence-span
  overlap and allowed kind do not prove semantic, quantity or period correctness.
  Negation mismatches are separately listed; do not claim they reduce the current
  scorer's span/kind precision. Quantities and periods are unscored.

For lead time, the unit is planted event × selected store overlapping the approved
period, not an alert, email, SKU count or independent experimental replicate.
The fixed protocol universe does not constrain event matching: the existing
lead-time evaluator uses its stores and CLI period. Publish `n_events`, `n_units`,
the complete per-unit table, excluded event ids/reasons and all method denominators.

- Match on store, compatible SKU intersection/size and direction within the unit's
  window. Store-wide events match only store-level alerts. Unknown scope/type and
  unresolved store are verify requests; customer_profile is context. Count these
  non-alert cases separately. Resolved verify-status cases still count as alerts.
- Report each method's detected units / all units, `not_detected_by_t_end`, total
  alerts, false alerts and false alerts / store-day. The current denominator is
  selected stores × inclusive calendar days, including no-alert days; it is not
  open days or days with email. Report missing input/observation coverage next to
  that rate. No planted-event match means false for this metric even when the
  signal is a real unplanted stock-out or sales swing.
- For both-detected pairs use `(t_baseline − t_pipeline) / 86400` in UTC days.
  Keep zero and negative values and report their counts from per-unit values,
  alongside positive counts and distributions. Never show only positive leads.
  Only-pipeline detection gives a separate lower bound `T_end − t_pipeline`;
  do not mix bounds into the both-detected mean/median or call them infinity.
  Only-baseline detection is a pipeline miss; neither detected is a miss for both,
  retained in the denominator. Publish all four pairwise categories per baseline.
- Publish `decision_due_at − t_pipeline` only where a deadline exists, including
  zero/negative margins and the missing-deadline count. An early alert is not
  automatically an actionable option.
- Preserve duplicate/correction/forward/noise diagnostics, folded copies and
  fragmented-unit counts from `noise`. These are diagnostics, not additional
  independent events or proof that all languages have complete noise labels.

**Baseline settings:** the present hold-out path always uses stock threshold 0
and sales z=3.0; the sales window/history/minimum/cooldown are 3/28/3/7 days.
Stock fires when a size crosses from above threshold to at/below it and rearms
only after recovery. Sales uses a trailing Poisson surprise, SKU upward and
store-total both directions. Both certify ERP day B at B+1 20:00 local; include
warm-up data (stock preceding snapshot and sales history before period start).
Missing stock snapshots carry state; absent sales rows are treated as zero by
the implementation, so verify source completeness and disclose gaps.

Dev bundles can calibrate grids by pipeline false-alert load. The current CLI
cannot transfer a chosen dev setting into hold-out; it uses the fixed defaults
and `within_pipeline_load: null`. Thus equal false-alert load is **not established**
for this hold-out comparison. Report actual loads and this departure from RFC
§7.2. Do not select thresholds from hold-out grid outcomes. If #211 requires
transferred dev thresholds, it needs a separately reviewed evaluator change
before inspection, followed by updated commands and revalidation.

**Window/credit limitations requiring #211 disposition:** current `event_units`
uses local midnight at max(event start, period start) and local 23:59:59 on
`min(event end, period end) + 1 day` as T_end. Despite the older docstring's cap
wording, the extra ERP grace day can extend beyond pipeline observation coverage;
pipeline cases are filtered to the inclusive CLI end date. Record these actual
boundaries and treat end-censored comparisons explicitly; do not claim equal
observation coverage without validation. Also the scorer credits final exported
resolved scope at the case's `first_available_at`; it does not reconstruct the
time when that scope became actionable. Label lead times as first-evidence lead
under this implementation, not proven first-valid-actionable-alert times, unless
freeze evidence validates that equivalence. If either issue invalidates the
intended comparison, resolve it through a reviewed eval task before execution,
or declare that comparison unavailable; do not silently repair measured rows.

The #218 placebo output is descriptive. #223 must replace its unequal pooled
comparison with common-period, equal-unit paired real/control rates, explicit
no-control exclusions, local-calendar shifts, no overlap with any same-store
real event, and raw auditing counts. Report breadth groups (store-wide, broad
>10 SKUs, specific), eligible/excluded units, shifts per unit and paired rates.
Never infer significance, causality or independent sample sizes from raw gaps;
units overlap in time/stores. If #223 is not merged/revalidated at freeze,
paired placebo evidence is unavailable and old pooled rates cannot substitute.

## 7. Forecast denominators and unavailable measures

For each H=1,3,7 separately, evaluate the next H complete store-local calendar
days after each frozen origin. Every origin×store×SKU in the preselected universe
is eligible, including no-alert/decoy examples. Missing target days/blank demand
make the entire horizon pending, never zero-filled or shortened. A mature
horizon lacking daily baseline or a complete computed overlay is unscorable;
retain reasons and counts. Baseline and selected forecast use exactly the same
remaining daily points. An unchanged/not_estimable overlay, or no overlay,
uses the baseline, with abstention/no-alert coverage reported separately.

Publish eligible, mature, pending, unscorable, scored, adjusted, abstained and
no-alert origin counts per H, plus ignored prediction counts and detailed reasons.
Prediction coverage = scored / mature; adjustment coverage = adjusted / scored.
Both are undefined at denominator zero. Quantities are daily realised demand
versus latent selected-scenario forecast at SKU-colour grain, not sales or
expected demand. WAPE = sum daily absolute errors / sum actual units (ratio),
MAE = sum daily absolute errors / n_days. Publish volumes, n_days and absolute
error sums for both comparators. Zero actual volume makes WAPE undefined but
leaves MAE meaningful for nonempty samples; empty samples have both undefined.
Daily errors cannot cancel by aggregation before taking absolute values.

Require one historical scenario chosen ex ante for the whole comparison; do not
choose low/base/high per outcome. Reject negative/nonfinite quantities, duplicate
oracle days/origins/pairs, multiple computed overlays or mismatched vintages.
Overlapping origins/horizons are not independent replications. Incomplete
prediction coverage limits claims to the reported common sample; it cannot be
presented as full-universe improvement. If the export has only alerted SKUs,
only final-day pending targets, wildcard SKUs or no trustworthy baseline, declare
WAPE/MAE unavailable for the intended comparison.

These evaluators do not establish unmet-demand episode/size recall or lost-unit
quantification, top-K usefulness, independent option feasibility, donor harm,
counterfactual stock trajectories, ASR/name accuracy, latency/token/cost metrics,
B1 no-dedup/no-abstention comparisons, or incremental value of voice. Mark each
unimplemented/unexported measure unavailable, or cite separately frozen evidence
with its own denominator and limits. Stock-out detection is not lost-demand
quantification. Synthetic demo/clarification/voice evidence remains separate.
No uplift, ROI, recovered revenue or real-world optimality may be inferred.

## 8. Outputs, preservation and invalid comparisons

#126 hands off `reading.json`, the reviewed eval-only labels/hash, annotation
coverage/exclusions and the reading bundle digest. #127 hands off
`lead-time-inputs.json`, `lead-time.json`, source-integrity evidence, actual
boundaries, baseline settings/load limits and the merged #223 diagnostic.
#128 adds `forecast-errors.json` when eligible, otherwise a machine-readable
unavailable-measures list with reasons; it publishes a concise report and an
artifact inventory of paths/SHA-256/counts tying every result to candidate,
protocol, bundle, label/oracle fingerprints and command transcript. The report
must include N and denominators, abstentions, missed events, errors, exclusions,
coverage and limitations even when a metric is poor or undefined. Keep dev
results, synthetic examples and final hold-out results separately labelled.
Hash the final outputs as well as the inputs; preserve logs and approvals.

The `verify`, `lead-time`, `forecast` commands and reading wrapper create result
files exclusively; the freeze library rejects existing bundle directories. Use
new experiment/revision paths, preserve failed logs/partial outputs, and never
delete results to retry under the same identity. A rerun for an operational
failure must record why no tuning or sample change occurred.

Once anyone inspects hold-out results, do not tune prompts, thresholds, aliases,
selection, matching, scenarios or product features against them. For a genuine
bug affecting a comparison:

1. Record the defect, affected candidate/protocol/bundle/results and why the
   comparison is invalid; open or reuse a tracked issue. Preserve all artifacts
   and mark their status invalidated/superseded with a reason.
2. Obtain cross-lane review of a minimal bug fix; reproduce it with synthetic or
   dev evidence, without importing hold-out answers into tests/product fixtures.
3. #211 reviews the new commit, protocol and fingerprints, reruns relevant gates
   and integration, and records a distinct candidate/bundle identity. Do not move
   the old tag or overwrite the old experiment silently.
4. Re-execute all affected comparators on the same preselected universe and
   publish old/new status, fix and implications together. Disclose that this is
   post-inspection re-evaluation, not a new untouched hold-out or fresh tuning
   opportunity. If comparability cannot be restored, declare it unavailable.

#128 hands only reviewed measured claims and their limitations to #129. This
preparation neither signs off G3/G4 nor supplies SHA values, measured improvements
or final approval on behalf of #211 or lane A.
