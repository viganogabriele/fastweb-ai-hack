# G3 freeze handoff: candidate binding and blind hold-out recording (REL-01)

Status: **candidate bound, not approved, not tagged.** This is the #211 handoff that
[`holdout-evaluation-protocol.md`](holdout-evaluation-protocol.md) §3 asks for. It fills
each binding with the values actually produced on the candidate, or names why a value is
unavailable. No scoring was run and no answer, label or answer-key file was opened.
`freeze-g3` does not exist yet. #126/#127/#128 stay blocked until Lorenzo approves this
record and tags the candidate (section 9).

Values marked `⟨TBD⟩` are filled after the candidate is chosen. Every value comes from a
command in section 8, run on the candidate.

## 0. Ordering disclosure: blind pre-record before the freeze tag

The Fastweb keys expire on **2026-10-25 00:00 UTC**. LLM cache keys bind the request bytes
(document and prompt hashes), and RunSpecs bind `code_version`, so the hold-out must be
recorded on the exact candidate commit while the keys still work. Lorenzo decided to
**record the hold-out LLM and systems caches on the candidate before the formal
`freeze-g3` approval and tag**, blind:

- During and after recording, the hold-out product outputs were inspected only through
  counts, SHA-256 digests, cache inventories, exit codes and structural validators
  (`eval.harness.freeze`, `freeze_record.py`). No case, observation, option, forecast or
  trace content was read, and nothing was compared with any answer.
- No prompt, threshold, alias, selection, module or parameter changed after recording
  started. The candidate code is the commit in section 1.
- Scoring (#126 reading, #127 lead time, #128 forecast) starts only after the approval and
  the tag in section 9.

The final report (#128) must repeat this disclosure.

## 1. Candidate

| Binding | Value |
|---|---|
| Candidate commit (full SHA) | `⟨TBD⟩` |
| Contents beyond `57199ec` (#240) | `⟨TBD⟩` (PLT-15 #247, OUT-02e #238 if merged) |
| Clean tree at recording | `⟨TBD⟩` (`git status --porcelain --untracked-files=all` empty) |
| Evaluator SHA | same as candidate (`eval/` tree `⟨TBD⟩`) |
| Protocol revision | `docs/holdout-evaluation-protocol.md` sha256 `⟨TBD⟩` at the candidate |
| `freeze-g3` target | not created; to be created by Lorenzo after approval (section 9) |
| Reviewer, approval time | `⟨Lorenzo, aware ISO timestamp⟩`, appended with `freeze_record.py append` |

## 2. Integration evidence on the candidate

| Binding | Value |
|---|---|
| `make check` | `⟨TBD: result, backend/web test counts⟩`; log `data/experiments/g3-20261023/make-check.log` sha256 `⟨TBD⟩` |
| Gate regressions (release-gate-audit focused suite) | `⟨TBD: passed/failed counts⟩` |
| #115 dev Core replay (`scripts/core_demo.md`) | `⟨TBD⟩`: expected output `9346b85e…a56f`, ledger `7b4f494a…230e`, snapshot `c5227036…6edb` |
| #123 safety | closed; its tests (`agents/test_runtime.py`, `agents/test_investigator.py`) are in the gate suite above |
| #226 gate audit | `docs/release-gate-audit.md` (audited at `f5cb0cb`); every test it names re-runs above on the candidate |
| Voice on/off (audit §2) | `⟨TBD⟩` (section 6.5) |
| #115 human items | genuine operator decision on the candidate and browser re-check: **open, Lorenzo** |

## 3. Selection and universe

| Binding | Value |
|---|---|
| Split | `config/eval_split.yaml` sha256 `⟨TBD⟩`; hold-out ROM01, PAR02, LON02, ZRH01, NYC02, TYO02, SEL02, BJS01, TPE01, DXB01 |
| Period and origins | 2026-08-31 … 2026-10-21 inclusive, 20:00 local in each store's IANA zone (`stores.csv`), 52 origins per store, 520 origin runs. The full pre-registered period is exportable: no narrowing |
| Origin list | `protocol.json` `origins_by_store` in the export (sha256 in section 5) |
| Preselection | dry-run on 2026-10-23 from file names and `Date:` headers only: 533 reading mails (per store 49–56), 8 mails dated after the last origin (read by the reading pass, cannot open cases), 0 undated |
| Reading universe | every hold-out mail with a `Date:` in the local period: `protocol.json` `reading_files`, 533 files expected. No narrowing, no exclusions |
| Lead-time universe | the 10 stores × 52 days = 520 store-days, including days without mail or alerts |
| Forecast universe | every store × SKU-colour with an `fc.baseline` record at any origin (`forecast/protocol-<STORES>.json`, explicit `store_id, sku, timezone`). This set is fixed by ERP forecast coverage, not by alerts or outcomes; it includes no-alert products |

## 4. Product identity

| Binding | Value |
|---|---|
| Runner | `tesseract.rolling` (REL-01c, protocol §5.1.1), `--investigate 0`, no `--sys-client` |
| Run id / plan | `⟨TBD⟩` / plan sha256 `⟨TBD⟩` |
| RunSpecs | 520 origin RunSpecs + 1 reading RunSpec under `export/run-specs/` |
| Modules | `src.email, src.erp, src.docs, ing.metrics, src.external, ing.extract, int.link, int.dedup, int.cases, int.context, fc.baseline, fc.overlay, act.options, out.reports` (versions/params in `protocol.json` `parameters`) |
| Models | `⟨TBD⟩` (`protocol.json` `models`; endpoints in the freeze record, never keys) |
| Prompts and configs | `export/config.txt`, hashed by `freeze_record.py record` |
| Lockfiles and runtime | hashed by `freeze_record.py record` |

## 5. Inputs, caches and exports

| Binding | Value |
|---|---|
| Consumed sources | `export/sources.txt`, `⟨TBD⟩` files, hashed in the freeze record |
| LLM cache | `data/rolling/holdout-cache/llm`: `⟨TBD⟩` entries, aggregate digest `⟨TBD⟩` |
| Systems cache | `data/rolling/holdout-cache/systems`: `⟨TBD⟩` entries, aggregate digest `⟨TBD⟩` |
| ASR | unavailable by design: the rolling runner has no `src.voice` (voice is a synthetic extension, section 6.5) |
| Record run | `⟨TBD: provider calls, cache hits, tokens, wall time, failures, retries⟩` |
| Offline replay (`eval product`) | `⟨TBD: provider calls 0, wall time⟩`; export hashes identical to the record run: `⟨TBD⟩` |
| Export files | `⟨TBD: sha256 and counts of predictions/cases/options/forecast/traces⟩` |
| `case_identity_drift` | `⟨TBD: count⟩` |
| Freeze record | `data/experiments/g3-20261023/freeze-record.json` sha256 `⟨TBD⟩` |
| Bundles | reading `⟨TBD⟩`, lead `⟨TBD⟩`, lead-emit `⟨TBD⟩` (section 6.2), forecast per group `⟨TBD⟩` |
| Integrity log | `data/experiments/g3-20261023/integrity-001.json`: `⟨TBD⟩` |

All of `data/` is gitignored: these files stay on the recording host
(`/home/dev/.t3/worktrees/fastweb-ai-hack/REL-01-freeze-g3/data/`). Only this document is in git.

## 6. Dispositions (proposed from the code; Lorenzo decides)

None of these proposals uses hold-out data. Each cites the code it reads.

### 6.1 Lead-time grace day (end censoring)

**Code.** `eval/lead_time.py::event_units` sets `T_end` to 23:59:59 local on
`min(event end, period end) + 1 day`. `eval/baselines.py` alerts on business dates up to
`end`, certified at `end + 1` 20:00 local (`CERTIFIED_AT`), so a baseline can alert on
2026-10-22 20:00. `case_alerts` drops pipeline cases whose `first_available_at` is after
`end` 23:59:59 local, and the last product origin is 2026-10-21 20:00 local. For units that
reach the last period day, baselines observe up to one evening more than the pipeline.

**Proposal.** Keep the scorer unchanged (no evaluator change before the freeze). The
asymmetry can only add baseline-first or baseline-only outcomes, so it is conservative
against the pipeline. Report: the number of units whose `T_end` is after the period end,
and for them the per-unit rows as they are, marked *end-censored for the pipeline*. The
chance check (`chance_units`) already caps `T_end` at the period end. Do not claim equal
observation coverage.

### 6.2 First-evidence credit versus emission time

**Code.** `case_alerts` times a pipeline alert at `Case.first_available_at`, the evidence
availability. The rolling export keeps, per case id, the payload of the **first origin that
emitted it** (so the scope credited is the scope at first emission, not a later resolved
scope, unless `case_identity_drift` lists a change) and adds
`alert_at = max(first_available_at, origin)`. Most closing mails arrive after 20:00, so
the product emits the case at the next origin, up to 24 h after `first_available_at`
(dev: 0–24 h, mean 12 h). Baselines are timed at certification (B+1 20:00), which is when
they could act.

**Proposal.** Freeze two lead bundles from the same export, both before any inspection:

- `lead`: `cases.json` as exported, scored by the unchanged scorer. Label it
  *first-evidence lead*.
- `lead-emit`: the same records with `payload.first_available_at` replaced by `alert_at`
  (a mechanical transform; script and input/output hashes in the experiment record). Label
  it *emission-time lead*.

Recommend the **emission-time lead as the headline**, because it compares the times at
which each method could actually act, and the first-evidence lead next to it. If
`case_identity_drift` is not empty, list the drifted cases' count with the result.

### 6.3 Fixed-default baselines (false-alert load not equalised)

**Code.** `lead_time_report` calibrates the baseline grids by pipeline false-alert load
only when `split == "dev"`. On the hold-out it uses `DEFAULTS` (`threshold=0`, `z=3.0`)
with `within_pipeline_load: None`. The CLI cannot transfer a dev-chosen setting.

**Proposal.** Accept the fixed defaults. They are code constants chosen before any
hold-out run. Report each method's alerts, false alerts and false alerts per store-day
side by side, and state that equal false-alert load is **not established** (a departure
from RFC §7.2). No grid result on the hold-out may select a setting. Optional diagnostic:
a dev-split rolling record (1,048 LLM calls upper bound, ~36 min) keeps a dev calibration
possible after the keys expire. Its result could only be reported as a dev diagnostic; it
cannot change the hold-out settings without a reviewed evaluator change before inspection.
Recorded: `⟨TBD: yes/no⟩`.

### 6.4 #223 interface status

**Code.** #223 is closed by PR #224, merged at `e0540c1` (2026-10-23 04:24 UTC), an
ancestor of the candidate. `lead_time_report` emits `chance_check` with paired real/placebo
rates per breadth group, `excluded_no_placebo` and capped windows. Its oracle-free tests
(`eval/tests/test_lead_time.py`) run inside `make check` (`backend/tests/eval/test_suite.py`).

**Proposal.** Paired placebo evidence is available on the candidate, revalidated by the
candidate's `make check` (section 2). Report it as descriptive only, never as significance;
the old pooled #218 rates are not used.

### 6.5 Voice on/off rerun (release-gate-audit §2)

**Code.** The audit names a gap: the generic source-disable test switches off
`src.external`, not `src.voice`. The hold-out export contains no voice: `ROLLING_MODULES`
in `backend/tesseract/rolling.py` has no `src.voice`, and the three DATA-03 notes are
MIL01/MIL02 synthetic extensions.

**Result.** `⟨TBD⟩`

### 6.6 Other bindings to approve

- **Forecast scenario.** `base`, chosen ex ante for the whole comparison (`protocol.json`
  proposes it). Confirm.
- **Forecast universe.** Derived from `fc.baseline` coverage (section 3). Confirm.
- **Investigator and systems checks off** in the hold-out export (`--investigate 0`, no
  `--sys-client`): options are per store, without cross-store donors or simulated-system
  checks. Option feasibility is not evaluated on the hold-out (protocol §4).
- **Reading sample** is the full 533-mail universe, including no-signal mails,
  duplicates, forwards and corrections. Lane A annotates all of them after the freeze.
- **`sources.txt`** lists files opened, which includes later mails of the same mailbox
  (`src.email` filters by `Date:` after opening). That does not admit them into a run.

## 7. Known limitations carried forward

- Dev Core: the D1 investigator stops on the six-tool budget with a visible `verify`
  fallback; the NYC01 correction is kept as a possible overlap, not applied
  (`scripts/core_demo.md`).
- The #115 packaged decision is a scripted synthetic reviewer command, not an operator.
- No hold-out metric, uplift, ROI, acoustic alignment, public bundle or G3/G4 certificate
  is claimed here. The record proves file identity, not row-level availability or
  correctness (`freeze-runbook.md`).
- After the freeze only bug fixes are allowed, under protocol §8.

## 8. Commands run

`⟨TBD: exact transcript⟩`

## 9. Approval checklist and tag (Lorenzo)

Tick in #211 before tagging:

- [ ] Candidate SHA, clean tree and `make check` log reviewed (sections 1–2).
- [ ] #115 human items done: genuine operator decision on the candidate, browser re-check.
- [ ] Blind pre-record ordering (section 0) accepted and to be disclosed in #128.
- [ ] Hold-out record/replay identity and zero-call replay reviewed (section 5).
- [ ] Bundle manifest digests and integrity log reviewed (section 5).
- [ ] Dispositions 6.1–6.6 decided (headline lead definition, defaults, scenario, universe).
- [ ] Approval appended: `freeze_record.py append --reviewer … --approved-at …`.

Then, from a checkout with the candidate commit:

```sh
git tag -a freeze-g3 ⟨SHA⟩ -m "G3 freeze, record data/experiments/g3-20261023/freeze-record.json" \
  && git push origin freeze-g3
```
