# Frozen hold-out evaluation results (EVL-05, #128)

Status: **DRAFT, no results yet.** Every `TBD` below is filled in only after the
`freeze-g3` tag, from the files in the experiment directory. This page reports the hold-out
stores only. Dev diagnostics (#124, #125, #138) stay in their own documents and are not mixed
in. It makes no uplift, ROI, recovered-revenue or real-world claim (protocol §7).

## 1. What was evaluated

| Item | Value |
|---|---|
| Candidate commit (`freeze-g3`) | TBD |
| Evaluator code | scorers byte-identical to the candidate (`eval/reading.py`, `lead_time.py`, `baselines.py`, `forecast.py`, `harness.py`), plus the `eval/holdout.py` wrappers from this PR: TBD check |
| Protocol | `docs/holdout-evaluation-protocol.md`, SHA-256 TBD (bound in the freeze record) |
| Freeze record | TBD (path, SHA-256, chain) |
| Hold-out stores | ROM01, PAR02, LON02, ZRH01, NYC02, TYO02, SEL02, BJS01, TPE01, DXB01 (`config/eval_split.yaml`) |
| Period | 2026-08-31 .. 2026-10-21, 20:00 local origins (52 per store, 520 runs) |
| Product run | `tesseract.rolling` record, then an offline replay under `eval product` (Landlock read isolation). The replay export is evaluated. |
| Bundles | reading TBD, lead TBD, forecast TBD (path = manifest SHA-256, recorded before scoring) |
| Experiment directory | TBD (append-only; inventory with SHA-256 in §6) |

**Order of operations.** Because of the Fastweb key expiry (2026-10-25 00:00 UTC), the
hold-out LLM cache was recorded blind on the candidate before the tag. Nobody inspected
hold-out outputs at that point. Then came the offline replay, the bundles, the freeze record
and the tag. The reading sample and these scoring wrappers were committed before the tag
(commit TBD). Hold-out labels were written after the tag, and scoring ran once after the labels
were hashed. Nothing was tuned after any hold-out result was seen.

## 2. #126 Reading and linking (EVL-02H)

**Sample.** 110 of the 533 eligible mails, 11 per store. The sample was drawn by a seeded hash
of the file name and fixed before the tag (`eval/labels/README.md`). Labels:
`eval/labels/reading_holdout_v1.yaml`, SHA-256 TBD.

> **The hold-out labels are AI-drafted.** Two independent annotator agents labelled each mail
> from the canonical email text and the source catalog only. A third agent reconciled the two.
> No agent saw answer keys, ground truth or product output. Lorenzo's review: TBD (not
> human-reviewed unless stated here). Dev labels (`reading_dev_v1.yaml`) were hand-written with
> the answer keys. The two label sets are not equivalent, and hold-out numbers are not directly
> comparable with dev numbers.

| | Files | Labels | Required | Observations | Matched obs. | Precision | Recall (required) | Recall (all) | Recall (required, read files) |
|---|---|---|---|---|---|---|---|---|---|
| Overall | 110 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| it / fr / de / ja / ko / zh-CN / zh-TW / en | TBD | | | | | | | | |

Links, on matched observations whose label names a product (`links.product_labels` = TBD):
accepted TBD, errors TBD (error rate among accepted TBD), coarser-correct TBD, ambiguous TBD,
unlinked TBD (abstention rate TBD), not_product TBD, no_link TBD.

Also reported: redundant matches TBD, negation mismatches TBD, exclusions and unread files
TBD (with reasons), and every false positive, missed required label and link error
(`reading.json`). Breakdown by document type (dup/reply/forward/no-signal) is TBD:
available only where the file suffix or the label note states it.

## 3. #127 Lead time against baselines (EVL-04H)

Unit = planted event × hold-out store overlapping the period. `n_events` TBD, `n_units` TBD,
excluded events TBD.

| Method | Detected / units | Not detected by T_end | Alerts | False alerts | False alerts / store-day |
|---|---|---|---|---|---|
| Pipeline (exported Cases) | TBD | TBD | TBD | TBD | TBD |
| Stock baseline (threshold 0) | TBD | TBD | TBD | TBD | TBD |
| Sales baseline (z = 3.0, 3/28/3/7) | TBD | TBD | TBD | TBD | TBD |

Store-days = 10 × 52 = 520 (calendar days, including days without alerts). Non-alert cases
(verify requests, customer-profile context): TBD.

Pairwise against each baseline: both detected TBD, with `t_baseline − t_pipeline` in days
reported as count, positive/zero/negative counts, median, mean and range; pipeline only TBD
(lower bound `T_end − t_pipeline`, kept separate); baseline only TBD; neither TBD. Decision
margin `decision_due_at − t_pipeline`: TBD, plus the missing-deadline count.

**Placebo (paired, #223).** Per breadth group (store-wide, broad > 10 SKUs, specific ≤ 10):
eligible units, excluded units, paired real rate against mean placebo rate. TBD. This is a
descriptive sensitivity check, not a significance test.

Noise diagnostics (duplicate/correction/forward/noise mails behind cases, folded copies,
fragmented units): TBD.

## 4. Forecast WAPE/MAE (EVL-03, optional)

TBD: either the scored H=1/3/7 table with eligible, mature, pending, unscorable and scored
counts, or the explicit `unavailable` record with its reasons (`forecast-errors.json`).

## 5. Unavailable measures

Not measured by these evaluators (protocol §7): unmet-demand episode and size recall,
lost-unit quantification, top-K usefulness, independent option feasibility, donor harm,
counterfactual stock trajectories, ASR/name accuracy, latency/token/cost, B1
no-dedup/no-abstention comparisons and the incremental value of voice. TBD: any additions.

## 6. Commands and artifacts

TBD: exact command transcript and an inventory (path, SHA-256, bytes) of every input
receipt and output. Machine-readable outputs that are small enough are committed under
`docs/holdout-results/`. Larger ones are listed by hash.

## 7. Limitations

- **AI-drafted labels.** See §2. Reading precision and recall measure agreement with
  agent-written labels on a 110-file sample, not with human ground truth. Sampling error is
  not quantified.
- **Sample, not census.** 110 of 533 mails. Per-language N is 11 (33 for English), too small
  for per-language claims.
- **Blind pre-record before the tag.** The cache was recorded before the tag because of the key
  expiry. The replay is byte-identical to the record (TBD confirm), and no output was inspected
  before scoring.
- **Lead time.** First-evidence lead (`Case.first_available_at`), not proven
  first-actionable-alert time. The extra ERP grace day can reach beyond pipeline observation
  coverage. Baselines use fixed defaults, so equal false-alert load is **not established**
  (departure from RFC §7.2). False alerts are relative to planted events. Units overlap in time
  and are not independent.
- **Hold-out, not unseen storylines.** Scenario descriptions were public. This is a store
  hold-out.
- TBD: any operational rerun, invalidation or exclusion found during execution.
