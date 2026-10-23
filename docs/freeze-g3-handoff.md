# G3 freeze handoff: candidate binding and blind hold-out recording (REL-01)

Status: **candidate bound and verified; not yet tagged.** This is the #211 handoff that
[`holdout-evaluation-protocol.md`](holdout-evaluation-protocol.md) §3 asks for. Each binding
below holds the value actually produced on the candidate, or the reason a value is
unavailable. No scoring was run and no answer, label or answer-key file was opened. The
`freeze-g3` tag is created after the final approval check (section 9), not by this PR.
#126/#127/#128 start from that tag.

All values come from the commands in section 8. The experiment directory
`data/experiments/g3-20261023/` (gitignored, append-only) holds every log and record named
here; paths below are relative to the repository root of the recording host checkout
`/home/dev/.t3/worktrees/fastweb-ai-hack/REL-01-freeze-g3/`.

## 0. Ordering disclosure: blind pre-record before the freeze tag

The Fastweb keys expire on **2026-10-25 00:00 UTC**. LLM cache keys bind the request bytes
(document and prompt hashes) and RunSpecs bind `code_version`, so the hold-out had to be
recorded on the exact candidate commit while the keys still worked. Lorenzo decided to
**record the hold-out LLM cache on the candidate before the formal `freeze-g3` approval and
tag**, blind:

- During and after recording, the hold-out product outputs were inspected only through
  counts, SHA-256 digests, cache inventories, run/module statuses, exit codes and structural
  validators (`eval.harness.freeze`/`FrozenRun`, `eval.forecast.choices`/`predictions`,
  `eval.lead_time.case_alerts`, `freeze_record.py`). No case, observation, option, forecast or
  trace content was read, and nothing was compared with any answer.
- No prompt, threshold, alias, selection, module or parameter changed after recording
  started. The executing code is the candidate commit in section 1.
- Scoring (#126 reading, #127 lead time, #128 forecast) starts only after the approval and
  the tag in section 9.
- Order on the candidate: to save time before the key expiry, the record started at
  07:27:44Z, before `make check`, the gate suite and the dev replays finished (07:31–07:32Z).
  The runbook puts the `make check` log before the exports. All of them passed; had one
  failed, the recording would have been discarded.

The final report (#128) must repeat this disclosure.

## 1. Candidate

| Binding | Value |
|---|---|
| Candidate commit | `1f7f35590782520d362c532c1e8159c4262703d7` (main; tree `c2b70188afe1b8b9fee1cae0ae123641f5c9b339`) |
| Contents beyond `57199ec` (#240) | #247 PLT-15, #238 OUT-02e, #250 REL-01e (voice on/off gate test), #252 (make demo → core-dev-20261023). #253 deliberately excluded |
| Clean tree | `git status --porcelain --untracked-files=all` was empty on the detached candidate before `make check` and the record (checked interactively, not logged) and is recorded by `freeze_record.py record` at 10:05Z (`candidate.clean: true`, `allow_dirty: false`) and `verify` (HEAD = candidate). The record process wrote no execution log (section 5) and the replay's says `head: unavailable`, because the read-isolated launcher cannot read git |
| Evaluator | same commit; `eval/` tree `b7706ebe3c97625ed2954c181aa6faec47d6a4c1` |
| Protocol revision | `docs/holdout-evaluation-protocol.md` sha256 `f4c4ac092bc1862133c59555b5470299e49a343773ff2f24f7e754807f2c381d` |
| `freeze-g3` target | to be created on the candidate commit after the approval check (section 9) |
| Reviewer, approval time | to be appended with `freeze_record.py append --reviewer … --approved-at …` |

## 2. Integration evidence on the candidate

| Binding | Value |
|---|---|
| `make check` | **passed**: ruff clean, 201 files formatted, **1,915 backend tests**, **86 web tests**, no OpenAPI type diff. Log `make-check.log` sha256 `cb1e8eed062966660ff17ed60a2b6049b35b904ff3f64da6931b0102b9b3f4a2` |
| Gate regressions | **242 passed** (`gate-regressions.log`): `tests/core/test_gate_temporal.py`, `test_gate_voice.py`, `test_repo.py`, `test_llm.py`, `test_replay_demo.py`; `tests/modules/integration/test_gate_dedup.py`; `tests/modules/actions/test_gate_blocking.py`, `test_simulation.py`, `test_approval_gate.py`, `test_gate_cutoffs.py`; `tests/modules/intelligence/test_gate_sizes.py`; `tests/modules/agents/test_runtime.py`, `test_investigator.py` (#123 budget, injection, wrong-store numbers); `tests/fixtures/test_ag03b.py` |
| #115 dev Core replay (`scripts/core_demo.md`) | prepared RunSpec byte-identical to the package; two fresh offline replays, exit 0, status `degraded` (documented), zero network attempts, no missing prerequisites; both output `9346b85e48e39119838e0aa88b1d6362379be5d5fa1a6cea50f2fc3463fba56f`, ledger `7b4f494a100a7ce204cc16a1fd4345314a16d0473895d5c1f5cac021ec0b230e`, snapshot `c522703633170af4933e06ed0f02edc29f2beb5f85cb32873ac46bb426b86edb`, equal to the documented values |
| Bound investigate job | `core_investigate_job.py verify`: `passed`, job `investigate-b3df8405…b9fe` published, zero network attempts (`dev-job-verify-2.json`). A first attempt failed before running on a wrong `--attempt` path (`attempt-attempt-…`, FileNotFoundError; `dev-job-verify.stderr`, preserved); the rerun changed only the path |
| #123 safety | closed; its agent runtime/investigator tests are in the gate suite above |
| #226 gate audit | `docs/release-gate-audit.md`; every test it names re-ran above on the candidate |
| Voice on/off (audit §2) | section 6.5: passed on the candidate |
| #115 human items | closed by #260 (genuine operator decision, UI re-check) |

## 3. Selection and universe

| Binding | Value |
|---|---|
| Split | `config/eval_split.yaml` sha256 `a8f03633b9a623c2a1612b180ad5c39604ffb3833102d8ca5cf07f349d20c16b`; hold-out ROM01, PAR02, LON02, ZRH01, NYC02, TYO02, SEL02, BJS01, TPE01, DXB01 |
| Period and origins | 2026-08-31 … 2026-10-21 inclusive, 20:00 local in each store's IANA zone, 52 origins per store, **520 origin runs** (312 distinct instants). Full pre-registered period, no narrowing |
| Origin list | `protocol.json` `origins_by_store` (export, section 5) |
| Preselection | from file names and `Date:` headers only: 533 reading mails, 8 dated after the last origin (read by the reading pass, cannot open cases), 0 undated. First dry run before 06:35Z; the sample is fixed in the plan written at record start, 07:27:46Z (`plan.json`, section 4). The same dry run was saved afterwards, with identical counts: `estimate-holdout.json` sha256 `2f773ec1a0f20e35c0ee6a57f006ee9cd770e387b7d6881afbb5cd23203846e1` (10:17Z) |
| Reading universe | every hold-out mail with a `Date:` in the local period: `reading_files`, **533 files**, no exclusions |
| Lead-time universe | 10 stores × 52 days = 520 store-days, including days without mail or alerts |
| Forecast universe | every store × SKU-colour with an `fc.baseline` record (ERP forecast coverage, not alerts or outcomes), explicit `store_id, sku, timezone`: 783 pairs in six groups of stores sharing origin instants (BJS01-TPE01 168, DXB01 81, LON02 65, NYC02 90, PAR02-ROM01-ZRH01 233, SEL02-TYO02 146). Every group has a daily baseline for every origin × pair |

## 4. Product identity

| Binding | Value |
|---|---|
| Runner | `tesseract.rolling` (REL-01c, protocol §5.1.1), `--investigate 0`, no `--sys-client`, `--workers 4` |
| Run id / plan | `rolling-holdout-2026-08-31-2026-10-21` / plan file sha256 `4d46717d18ce9d99fb478699c0659c91625af21348f0b1ea3161da28d6a2fa1b` (identical for record and replay), `plan_sha256` `fabf70754060bfc5859b61449253e36f365a8d752ed5cc06657549efff2f1c99` |
| RunSpecs | 520 origin RunSpecs + 1 reading RunSpec (`export/run-specs/`, digest `30fa97c08c7623f08542f6dc2ea850c3f9ace62433fb4184981f7a410a50bdcc`). All 521: `matches_recorded_inputs` config `true`, sources `false`, as the runbook expects (each origin binds its own selection; the record binds the union) |
| Modules | `src.email, src.erp, src.docs, ing.metrics, src.external, ing.extract, int.link, int.dedup, int.cases, int.context, fc.baseline, fc.overlay, act.options, out.reports` |
| Models | chat `google/gemma-4-26B-A4B-it` (settings alias) at `https://spod.ai-factory.fastweb.it/v1`; the served model in all 715 cache envelopes is `RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic`; prompts `extract_observations.v1`, `link_choice.v1` (bytes hashed in the record) |
| Lockfiles and runtime | `backend/uv.lock`, `web/package-lock.json`, `scripts/openapi/package-lock.json`; Python 3.12.15, uv 0.13.5, Node v24.18.0, npm 11.16.0 (in the record) |

## 5. Inputs, caches and exports

| Binding | Value |
|---|---|
| Consumed sources | `export/sources.txt`: **667 files**, each hashed in the record; 61 evaluator live inputs for the window (with warm-up). One expected evaluator input is absent and recorded as such: `erp/inventory/store_stock_daily/stock_eod_2026-10-22.csv` (`verify` flags it if it appears) |
| LLM cache | `data/rolling/holdout-cache/llm`: **715 entries**, record aggregate `add908c24ebab7e63044b74e789929ee1ef02c13a984262ff124feb30455b4df` (run manifest `dad7d3aa85ee3e7f0c6c995034c7f7bddc0ff6cc341495476b6e160c8d387ca7`); replay policy: a miss is an error |
| Systems cache | `data/rolling/holdout-cache/systems`: 0 entries (`sys.client` off); `4f53cda1…b945` |
| ASR / investigator | declared `unavailable`: the rolling runner has no `src.voice`; the hold-out export runs `--investigate 0` |
| Record run | 2026-10-23 07:27:44 → manifest 08:27 UTC (≈60 min). **715 provider calls** (estimate ≤ 827), **1,342,646 tokens**, all in the reading pass; 17,836 origin cache hits; 520/520 origins on the first attempt, **0 failures, 0 retries**. Module statuses: none failed (`act.options`, `int.cases`, `out.reports` degraded at every origin, `fc.overlay` 484 degraded / 36 succeeded, `src.external` 52 degraded) |
| Offline replay (`eval product`) | 09:19:37 → 10:05:11 UTC (2,696 s), exit 0, **0 provider calls**, 18,551/18,551 requests from cache, 0 failures |
| Replay identity | every export hash in the record and replay run manifests is **identical** (all files, `run-specs/` digest, counts, plan, cache digest) |
| Exports (replay, `data/rolling/holdout-replay/export/`) | `predictions.json` `36df6d088faa49c3a5f57174c6711f895d449b3195f322be06498d1df77a6666` (11,380 records: 533 documents, 2,216 segments, 4,313 observations, 4,313 links, 4 module runs, 1 RunSpec); `cases.json` `0e86c35be9481dd51b7f3812475769270b8aee032c3cb651fe4282a8dda1b4c4` (1,554); `options.json` `d457ada3cc623dca5dcaba5d601496fad0b077812b7ba68b2cc0850333773dc0` (150,872 versions); `forecast.json` `01cb909e81c22d0787140e7354f4057f28b66a1e462aad2ee34647cbfc3e3d46` (58,391); `traces.json` `37517e5f…a7b8` (0); `protocol.json` `38316c8a784c3acc03613eb03910fb1c18078319c4f69de992a2605bf5175a7b` |
| Derived `lead-emit` export | `data/experiments/g3-20261023/lead-emit/cases.json` `8912d854765251d48c18e39c153e723fc65a8d1587b0ddea4954c9d8689e96b7` (1,554); predictions/options byte-identical to the replay; transform `tools/lead_emit.py` `1a2df1b1e94098b065a6d0be32d6eb913c2479891003f7cdfd5a16ccb4b56de6` |
| `case_identity_drift` | **0**; 0 cases withdrawn before the final origin |
| Freeze record | `data/experiments/g3-20261023/freeze-record.json` sha256 **`219b99bb53c9a514cb98f43de20b92b266c06022f8e5d2e21b67da90f7ccb340`** |
| Bundle addendum | `freeze-record.001-bundles.json` sha256 **`e825c1a623174228b4dfef113b4c00e59c32c7c4dadcee6640fe3539726037fc`** |
| Integrity log | `integrity-001.json` sha256 `847bf7cda4c9fc6d256e5ecfe702710b573051e1bf48e30212b5b2aaf8c29e37`: status `ok`, 3,049 files, no drift, no warnings. It verified both chain files; its `chain` field lists each addendum's parent, so it names only the base record |

Bundles (`data/bundles/g3-20261023/`), each with a protocol bound by `tools/bundles.py`
(status *bound, pending approval*), sources/config from `sources.txt`/`config.txt`, and each
validated through `FrozenRun` without answers (`bundle-validation.jsonl`). The addendum binds
`tools/bundles.py`, `tools/validate_bundle.py` and the validation log as evidence:

| Bundle | Manifest sha256 | Validation |
|---|---|---|
| `reading` | `1ea6ee0fe4c56786b7ff5ef7c69ab4b2f0ac72809941dc972fec6c74fbee0e99` | 533 reading files, 10 stores |
| `lead` (first evidence) | `d2717c8acd07326f999d4338741929cffe8560f687835c441ef89c84a357b742` | 1,554 cases → 909 alerts, 589 verify, 56 context |
| `lead-emit` (emission time) | `934f2a8c2b0298bbc2f0ab31d562227bb34bfc3ec0a3edc24202c42de13fb9c9` | same counts |
| `forecast-BJS01-TPE01` | `7d0d9e3d2d284596aab79ea1a1bb5b2df172beaec4c1f4b91c9a0eba985967ed` | `base`, 52 origins × 168 pairs = 8,736 baselines |
| `forecast-DXB01` | `092d2c4ffdac291251ac3dc35838b4c9e1dd586a26f4a880acec3993f12f52c0` | 52 × 81 = 4,212 |
| `forecast-LON02` | `40525118700afea9e80c02451dff84d59d32870fe73d6e288255141ab8f0a3c9` | 52 × 65 = 3,380 |
| `forecast-NYC02` | `b19de0114c9b60de230b7d016c42e7da2a7e34d15439c5f2aa09941dba0b5ec0` | 52 × 90 = 4,680 |
| `forecast-PAR02-ROM01-ZRH01` | `8dd2d1777978f5bc0f8b4d773afefc03103bfd914760a8864ae31969a7359528` | 52 × 233 = 12,116 |
| `forecast-SEL02-TYO02` | `4f79744c9052c491a9316ac3964ad2eb8cb937b0082961f720e188bcd5090779` | 52 × 146 = 7,592 |

All of `data/` is gitignored: these files stay on the recording host. Only this document is
in git.

### Operational notes (no effect on outputs)

- **Disk.** The rolling runner keeps one SQLite database per store across its origins
  (0.59–1.72 GB each). To fit the host, `tools/reclaim_db.sh` deleted a store's working
  database only after all 52 of its origin files were written and no process held it open
  (`db-reclaim.log`, `db-reclaim-replay.log`, sizes logged). Exports are rebuilt only from
  `origins/*.json` (`build_exports`), and a store with all origins final is never reopened.
- **Record process.** After writing every export and `run-manifest.json` (08:27 UTC), the
  record process thrashed swap in the post-manifest execution log (`llm_totals` loads all
  520 origin results while the exports are still in memory, on a 7.9 GB host). It was
  stopped at 09:19 UTC (exit 143; `operator-notes.log`). Before that, every export file was
  rehashed against the manifest (all equal; the check is not logged, but the record's
  `record_manifest` evidence and the identical replay manifest cover it), and the LLM totals were recomputed by streaming the origin
  files (`record-a1-totals.json`). The replay finished normally.
- **Size.** `options.json` is 499 MB, not the ≈180 MB estimated by REL-01c.

## 6. Dispositions (proposed from the code; to be decided at approval)

No proposal uses hold-out answers, labels or outcomes; each cites the code it reads. The
forecast universe (6.6) comes from the hold-out export's `fc.baseline` coverage, a product
output that does not depend on outcomes.

### 6.1 Lead-time grace day (end censoring)

**Code.** `eval/lead_time.py::event_units` sets `T_end` to 23:59:59 local on
`min(event end, period end) + 1 day`. `eval/baselines.py` alerts on business dates up to
`end`, certified at `end + 1` 20:00 local (`CERTIFIED_AT`), so a baseline can alert on
2026-10-22 20:00. `case_alerts` drops pipeline cases whose `first_available_at` is after
`end` 23:59:59 local, and the last product origin is 2026-10-21 20:00 local. For units that
reach the last period day, baselines observe up to one evening more than the pipeline.

**Proposal.** Keep the scorer unchanged. The extra evening mostly favours the baselines
(baseline-first or baseline-only outcomes); the pipeline-only lower bound `T_end − t_pipeline`
also uses the extended `T_end`, so report it with that caveat. Report the number of
units whose `T_end` is after the period end and mark their rows *end-censored for the
pipeline*. The chance check (`chance_units`) already caps `T_end` at the period end. Do not
claim equal observation coverage.

### 6.2 First-evidence credit versus emission time

**Code.** `case_alerts` times a pipeline alert at `Case.first_available_at`, the evidence
availability. The rolling export keeps, per case id, the payload of the **first origin that
emitted it** (the scope credited is the scope at first emission; `case_identity_drift` is
0) and adds `alert_at = max(first_available_at, origin)`. Closing mails often arrive after 20:00 (dev evidence in protocol §5.1.1:
0–24 h gap, mean 12 h; the hold-out timing diagnostic is not read before scoring), so the product emits a case at the next origin, up to 24 h after
`first_available_at`. Baselines are timed at certification (B+1 20:00), when they can act.

**Bound.** Both lead bundles exist, frozen before any inspection: `lead` (cases as
exported, *first-evidence lead*) and `lead-emit` (`payload.first_available_at :=
alert_at`, evidence time kept as `evidence_first_available_at`, *emission-time lead*).

**Proposal.** Headline: the **emission-time lead**, because it compares the times at
which each method could act; report the first-evidence lead next to it.

### 6.3 Fixed-default baselines (false-alert load not equalised)

**Code.** `lead_time_report` calibrates the baseline grids by pipeline false-alert load
only when `split == "dev"`. On the hold-out it uses `DEFAULTS` (`threshold=0`, `z=3.0`)
with `within_pipeline_load: None`. The CLI cannot transfer a dev-chosen setting.

**Proposal.** Accept the fixed defaults: code constants chosen before any hold-out run.
Report each method's alerts, false alerts and false alerts per store-day side by side, and
state that equal false-alert load is **not established** (a departure from RFC §7.2). No
hold-out grid result may select a setting. A dev-split rolling record for a dev calibration
diagnostic was **not** recorded (deadline and host limits); a dev calibration therefore
stays unavailable once the keys expire.

### 6.4 #223 interface status

**Code.** #223 is closed by PR #224 (`e0540c1`), an ancestor of the candidate.
`lead_time_report` emits `chance_check` with paired real/placebo rates per breadth group,
`excluded_no_placebo` and capped windows. Its oracle-free tests run inside `make check`
(`backend/tests/eval/test_suite.py`), which passed on the candidate.

**Proposal.** Paired placebo evidence is available. Report it as descriptive only, never
as significance; the old pooled #218 rates are not used.

### 6.5 Voice on/off rerun (release-gate-audit §2)

**Code.** The audit names a gap: the generic source-disable test switches off
`src.external`, not `src.voice`. The hold-out export contains no voice: `ROLLING_MODULES`
in `backend/tesseract/rolling.py` has no `src.voice`, and the three DATA-03 notes are
MIL01/MIL02 synthetic extensions.

**Why not a recorded rerun.** The dev Core runner binds its cache with `LLMClient.for_run`
(`backend/tesseract/core/llm.py`), whose scope is the whole RunSpec except run id and mode:
modules, sources and `code_version` included. A voice-on and a voice-off recording there
would be two independent model samples, and their difference could not isolate voice. A
shared `for_scope` scope (as in `tesseract.rolling`) would replay the byte-identical
non-voice requests, but no such runner includes `src.voice`, and the voice requests would
still need new recordings. The three ASR envelopes from ING-03b are
also not on the recording host.

**What was run.** #249/#250 add `backend/tests/core/test_gate_voice.py`: the
`test_gate_temporal` MIL01 graph (real mailbox, ERP, weather) plus `src.voice` over the
committed DATA-03 notes in `fixture` mode, the explicitly declared manual-transcript
fallback. A scripted extractor answers one closing mail and the two MIL01 notes with
verbatim quotes; the notes open one SKU and one SKU-size case and a forecast overlay. With
voice off, at the same clock and on the same database: no note id, quote or LLM request
survives; every artifact outside the voice-derived set is identical field by field (observed:
15 voice-derived, 351 identical); reports keep their ids and drop only voice consequences; the
other sources report the same results. This is **partial dev graph** evidence with a
scripted model (audit evidence class 2), not a recorded-model run.

**Result on the candidate.** Passed (part of `make check` and of the 242-test gate suite).

### 6.6 Other bindings to approve

- **Forecast scenario.** `base`, chosen ex ante for the whole comparison (bound in every
  forecast bundle protocol).
- **Forecast universe.** Derived from `fc.baseline` coverage (section 3).
- **Investigator and systems checks off** in the hold-out export (`--investigate 0`, no
  `--sys-client`): options are per store, without cross-store donors or simulated-system
  checks. Option feasibility is not evaluated on the hold-out (protocol §4).
- **Reading sample** is the full 533-mail universe, including no-signal mails, duplicates,
  forwards and corrections. **Label plan (pending, owner lane A, #126):** after the tag,
  lane A writes one hold-out YAML under `eval/labels/` in the `reading_dev_v1.yaml` schema
  (`eval.reading.load_labels`), covering every claim of the 533 files, including negations
  and ambiguities; its SHA-256 is appended with `append --label-sha reading_holdout=…`, and
  scoring uses the explicit-label wrapper of protocol §5.2.
- **Report owner:** #128 (lane D) publishes results; #127 (lane D) runs lead time.
- **`sources.txt`** lists files opened, including later mails of the same mailbox
  (`src.email` filters by `Date:` after opening). That does not admit them into a run.
- **Changed dispositions.** If the approval changes 6.2 or 6.6, freeze new bundles from
  the same export before any inspection and append them; the product does not re-run.

## 7. Known limitations and post-freeze fixes

- Dev Core: the D1 investigator stops on the six-tool budget with a visible `verify`
  fallback; the NYC01 correction is kept as a possible overlap, not applied
  (`scripts/core_demo.md`).
- **#258 (post-candidate bug fix).** The investigator's `evaluate_options` republished
  donor-scoped options that approval could never accept (409) on the dev demo case D1. It
  is fixed on main by #261 (AG-03d), after the candidate, as a bug fix under protocol §8. It
  does not touch the hold-out: the hold-out export runs with the investigator off.
- **Main after the candidate.** Main has since gained other commits (for example #257,
  #266, #270, #272, some touching modules the hold-out runs, such as
  `backend/tesseract/modules/sources/external.py`). They are outside the bound product.
  Scoring runs from the `freeze-g3` tag on `1f7f355`, never from main.
- No hold-out metric, uplift, ROI, acoustic alignment, public bundle or G3/G4 certificate
  is claimed. The record proves file identity, not row-level availability or correctness
  (`freeze-runbook.md`).
- After the freeze only bug fixes are allowed, under protocol §8.

## 8. Commands run

From the repository root on the clean candidate checkout, `export
PATH=/home/dev/.cache/ffmpeg-bin:$PATH`, `E=data/experiments/g3-20261023`,
`X=data/rolling/holdout-replay/export`. Wrappers with the exact arguments are kept in `$E`
(`record.sh`, `replay.sh`, `freeze-record.sh`, `tools/`).

```sh
git checkout --detach 1f7f35590782520d362c532c1e8159c4262703d7
test -z "$(git status --porcelain --untracked-files=all)"
make setup
TMPDIR="$PWD/data/core_demo/check-tmp" make check 2>&1 | tee $E/make-check.log
cd backend && .venv/bin/python -m pytest -q tests/core/test_gate_temporal.py tests/core/test_gate_voice.py \
  tests/core/test_repo.py tests/core/test_llm.py tests/modules/integration/test_gate_dedup.py \
  tests/modules/actions/test_gate_blocking.py tests/modules/actions/test_simulation.py \
  tests/modules/intelligence/test_gate_sizes.py tests/modules/actions/test_approval_gate.py \
  tests/modules/actions/test_gate_cutoffs.py tests/modules/agents/test_runtime.py \
  tests/modules/agents/test_investigator.py tests/core/test_replay_demo.py tests/fixtures/test_ag03b.py; cd ..
# dev Core replay and job verification: scripts/core_demo.md, outputs $E/dev-replay-{1,2}.json, $E/dev-job-verify-2.json
make mocks   # systems mock server on :8088 (no systems recording occurred: sys.client off)
# record (outside the launcher; keys file path only, never read)
cd backend && .venv/bin/python -m tesseract.rolling run --split holdout --start 2026-08-31 \
  --end 2026-10-21 --mode record --cache ../data/rolling/holdout-cache \
  --workspace ../data/rolling/holdout-record \
  --code-version 1f7f35590782520d362c532c1e8159c4262703d7 --workers 4 --llm-concurrency 8 \
  --keys-file /home/dev/dev/fastweb-ai-hack/.secrets/fastweb_keys.json --yes; cd ..
# evaluated offline replay
backend/.venv/bin/python -m eval product -- -m tesseract.rolling run --split holdout \
  --start 2026-08-31 --end 2026-10-21 --mode replay --cache ../data/rolling/holdout-cache \
  --workspace ../data/rolling/holdout-replay \
  --code-version 1f7f35590782520d362c532c1e8159c4262703d7 --workers 4
# record vs replay: run-manifest.json `exports` equal ($E/record-vs-replay.json)
backend/.venv/bin/python -I $E/tools/lead_emit.py $X $E/lead-emit
$E/freeze-record.sh   # freeze_record.py record (all runbook arguments, plus --exports lead_emit)
backend/.venv/bin/python -I $E/tools/bundles.py $X $E/lead-emit $E   # 9 bundles
backend/.venv/bin/python -I $E/tools/validate_bundle.py <bundle> <digest>   # per bundle
backend/.venv/bin/python scripts/freeze_record.py append --record $E/freeze-record.json \
  --output $E/freeze-record.001-bundles.json --bundle <dir>=<digest> ... (9)
backend/.venv/bin/python scripts/freeze_record.py verify \
  --record $E/freeze-record.json $E/freeze-record.001-bundles.json --output $E/integrity-001.json
```

## 9. Approval checklist and tag

To tick in #211 before tagging:

- [ ] Candidate `1f7f355`, clean tree and `make check` log reviewed (sections 1–2).
- [x] #115 human items done (#260).
- [ ] Blind pre-record ordering (section 0) accepted; #128 discloses it.
- [ ] Record/replay identity and zero-call replay reviewed (section 5).
- [ ] Record `219b99bb…`, addendum `e825c1a6…`, nine bundle digests and integrity log
      `847bf7cd…` reviewed (section 5).
- [ ] Dispositions 6.1–6.6 decided (headline lead definition, defaults, scenario, universe).
- [ ] Approval appended:
      `freeze_record.py append --record $E/freeze-record.json $E/freeze-record.001-bundles.json --output $E/freeze-record.002-approval.json --reviewer "<name>" --approved-at "<aware ISO timestamp>"`.

Then tag the candidate commit, never a branch:

```sh
git tag -a freeze-g3 1f7f35590782520d362c532c1e8159c4262703d7 \
  -m "G3 freeze, record data/experiments/g3-20261023/freeze-record.json sha256 219b99bb53c9a514cb98f43de20b92b266c06022f8e5d2e21b67da90f7ccb340" \
  && git push origin freeze-g3
```

Before each scoring run (#126/#127/#128), repeat `verify` with a new `--output`
(`integrity-002.json`, …) and append label receipts once lane A has annotated.
