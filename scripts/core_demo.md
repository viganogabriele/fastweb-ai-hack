# DEMO-02: source-backed Core candidate and offline handoff

This is the integration evidence for #115 and the input to #211's human release
review. It is a historical **synthetic dev** rehearsal, not a hold-out result,
a production transfer or a public bundle. Its one genuine operator decision is a
local rejection (see "Genuine operator decision" below).

## Frozen inputs and recordings

The portable package is `data/fixtures/runs/core-dev-20261023/`. Its location
does not make the run a fixture: the RunSpec has `mode: recorded`, the namespace
is `product`, and `authorized_fixture_refs` is empty. The normal fixture loader
does not load this nested package. No derived projections are preloaded.

The actual provider recording executed commit
`38fe618a91a9d4f573e96fc2ec3cde2ee6ec8ebe` (DEMO-02b, PR #237: source-backed
correction/resend handling, after independent review). It replaces the earlier
`f1d7923` recording, whose resend and correction emails produced zero certain
relations. The positive POST-investigate job was recorded at
`6803eeada64e03678dd84a23b099f44e4634733f`, which changes only
`scripts/core_investigate_job.py`; the job is bound to this candidate's snapshot.
Later commits that do not change executable code keep these identities; the final
verification SHA is recorded in the PR/#211 handoff.

- Clock: `2026-10-22T20:00:00Z`; dev stores MIL01, MIL02, MUN01, NYC01.
- 12 explicitly selected Italian, English and German emails, including resend,
  correction, reply and out-of-office inputs; one actual W42 workbook; Milan and
  Munich weather feeds; 60 days of ERP history with row availability filtering.
- 108 selected source files; source tree SHA-256
  `a3d3d221987593f9512ddc82265a1f518da4218efd88e66c7a00f433b9984d70`.
- Four configuration files; tree SHA-256
  `fb50f57d8b4b1ad55076726fab97f2ee586b2ea3098b96f7aed651d5e9a89bc8`.
- 21 real provider envelopes: Gemma extraction/constrained linking and GLM
  investigation, plus 6 GLM envelopes and 1 systems envelope for the separate
  investigate job in `investigate-job/`. GLM's outside-EU hosting is already disclosed in
  `docs/smoke-fastweb.md`; the inputs here are synthetic.
- 12 real HTTP response envelopes from the dataset's simulated warehouse and
  logistics server. The adapter's ordinary timestamp, stock and lane checks
  still apply. Raw response bytes remain unchanged for SourceRef hashes.
- `input-manifest.json` lists every source/config path and byte hash;
  `asset-manifest.json` hashes the portable JSON evidence/cache files.
  Responses contain no credentials or request headers. No `.env`, secrets,
  answer labels, commercial display catalog or generator input is packaged.

## Rebuild without credentials, a mock server or networking

Run from the repository root after `make setup`. Choose an output directory that
does not already exist; the preparation command refuses to overwrite a candidate.

```sh
demo_assets="$PWD/data/fixtures/runs/core-dev-20261023"
demo_candidate="$PWD/data/core_demo/reproduction"

backend/.venv/bin/python scripts/prepare_core_demo.py \
  --output "$demo_candidate" \
  --code-version 38fe618a91a9d4f573e96fc2ec3cde2ee6ec8ebe \
  --case-id case-mil01-i10919b00011-20261008 \
  --case-id case-mil01-unknown-20261009
cmp "$demo_candidate/run-spec.json" "$demo_assets/run-spec.json"

backend/.venv/bin/python scripts/replay_demo.py \
  --run-spec "$demo_assets/run-spec.json" \
  --sources "$demo_candidate/sources" \
  --config "$demo_candidate/config" \
  --cache "$demo_assets/llm_cache" \
  --systems-cache "$demo_assets/systems_cache" \
  --decisions "$demo_assets/decisions.json" \
  --workspace "$PWD/data/core_demo/offline-reproduction"
```

Repeat the replay command against the same owned workspace. Each attempt stages
new regular input files, creates a fresh database and ledger, and never resets a
shared application session. It denies socket networking and subprocesses during
execution. Compare `inputs`, `snapshot_sha256`, `output_sha256`, `ledger_sha256`,
artifact identities/versions, and `decisions` across attempts. Trace elapsed times
are the only documented artifact-hash exclusion; exact raw artifact hashes are
also preserved. Frozen decision IDs, versions and complete drafts are retained
and revalidated, rather than regenerated as merely equivalent choices.

`--decisions` is an ordered list containing namespace, snapshot hash, original
request, decision clock and exact exported LocalDraft. The scripted synthetic
reviewer approves an informational `notify_owner` option. The result is a local
draft with zero reservations and no external message. A timestamp before the
snapshot, foreign namespace/hash, changed draft or stale option is refused.

### Genuine operator decision

`decisions-operator.json` holds the one decision a human took on this candidate.
On 2026-10-23 Lorenzo (`lorenzocorallo`, maintainer) chose to **reject**
`opt-case-mil01-i10919b00011-20261008-transfer` (version `4c5c3713b5a3498f`;
move 1 × I10919B00011-742 size L, MIL02 → MIL01) with the note: "The transfer
moves size L to MIL01, which already holds 8 in L; the store reported zero in size
M. It doesn't address the reported shortage." He decided it during the DEMO-02c
session, and the agent entered it on his instruction:

- through the real `POST /api/runs/core-dev-candidate/cases/case-mil01-i10919b00011-20261008/decisions`
- on an offline replay of this candidate that has no other decision
- with `by: lorenzocorallo`, which is a declared local identity, not an authenticated login.

The API clock stamped `2026-10-23T07:38:02.026637Z`, before the option's
`valid_until` (`2026-10-23T13:30:00Z`). The identical retry and the decision read
API returned the same draft:

- ID `decision-2e6afdfc5f534eaf9950412f40e70efa`
- `dispatch_status: draft`
- zero reservations, because a rejection holds no stock.

The export uses the same `decision_export` as `check_core_demo.py`. It replays on
its own, in place of the synthetic file, which stays unchanged:

```sh
backend/.venv/bin/python scripts/replay_demo.py \
  --run-spec "$demo_assets/run-spec.json" \
  --sources "$demo_candidate/sources" \
  --config "$demo_candidate/config" \
  --cache "$demo_assets/llm_cache" \
  --systems-cache "$demo_assets/systems_cache" \
  --decisions "$demo_assets/decisions-operator.json" \
  --workspace "$PWD/data/core_demo/operator-replay"
```

`operator-decision-replay.json` records two cold attempts. Both exit 0 with zero
network attempts and no missing prerequisites. They match on inputs, exact
artifact IDs and versions, the decision (draft sha256 `69a9a767…85fd`), output
`faccb706836a72ff87fd1aca9dba151985f8d6b1980f5109d0d6db810fc0c61f` and ledger
`a4829accf1c98b7989d85b9636f8d8fa560c526693a4f0289366fff0c46ea785`. As above,
only the AgentTrace raw hashes differ, because of the excluded `duration_ms`.
`make demo` still replays the synthetic `decisions.json`.

Which options a human can decide here was checked by POSTing every current
option against a throwaway copy of a fresh replay:

- Reject: all 157.
- Approve: 152. The exceptions are the D1 `hold`, `verify_stock`, `ask_store` and
  `notify_owner` at version `02f273c06fbcb197`, which return 409 "proposal inputs
  or checks changed". The investigator's donor-scoped `evaluate_options` step
  republished them under the deterministic IDs (#258). Separately,
  `opt-case-mil01-j10911a00305-20261002-transfer` correctly fails `donor_protection`.

For the two negative rehearsals, copy a cache outside the owned replay workspace,
withhold one envelope in that copy and pass it to the same command. The actual
LLM-negative run withheld key
`15d758e1f5f23a97baee22888167b030989da7be581c7c532a4c51900efc3a93`;
the systems-negative run withheld
`11aa63dc990862ec3127c3ed81222565a9c0d5ff1843b02d82eb4e992239bcf1`.
Both must exit 1, list recording misses, skip decision replay and report zero
network attempts. Original caches and previous positive attempts remain intact.

## Actual Core outcome

The completed recording and two fresh cold replays publish:

- 13 documents, 206 segments, 82 observations with 82 independently validated
  exact document/segment quote spans, and 82 entity links.
- 38 current cases (49 stored case versions), including unresolved products kept
  visible as `verify`; the out-of-office input produces no observation.
- 129 evidence relations: **10 certain `duplicates`**, **1 certain `supersedes`**
  and 118 possible overlaps (33 non-additive origins). 82 facts form 72 origin
  groups, 71 of them active. 16 report metric facts, two actual weather context
  events, 346 baselines and 27 case overlays.
- 161 stored option versions, two investigator traces, one simulated clarification
  draft, two owner/priority reports, and an exact versioned local decision draft.
- No fabricated numerical uplift: overlays stay unchanged with explicit reasons;
  missing baseline coverage remains `not_estimable`. No transfer is recommended.

Both replays: output `9346b85e48e39119838e0aa88b1d6362379be5d5fa1a6cea50f2fc3463fba56f`,
ledger `7b4f494a100a7ce204cc16a1fd4345314a16d0473895d5c1f5cac021ec0b230e`,
snapshot `c522703633170af4933e06ed0f02edc29f2beb5f85cb32873ac46bb426b86edb`,
exit 0, no missing prerequisites and zero network attempts (`replay-comparison.json`).

The final status is honestly `degraded`: unknown SKU scopes require verification,
the optional product-insights module is absent and the D1 investigator reaches
the six-tool budget. D1 calls evidence,
stock twice, lanes twice and the deterministic options engine, then publishes a
visible `verify` fallback. The unresolved MIL01 case instead calls evidence,
drafts a clarification and finishes without fallback. These are real-model
choices on source-derived cases.

The older two successful, non-fallback GLM paths from #199 remain distinct:
`tests/fixtures/test_ag03b.py` verifies their explicitly fixture-backed inputs.
They are not relabeled as source-pipeline outputs or used to replace this run.

### Source-backed resend and correction

- **Resend (MIL01 02/10, 21:12 and 21:13).** The two mails have the same sender,
  subject, local date and body. `ing.extract` reads the earliest copy once and
  reuses that reading for the resend (`resend_readings_reused: 1`); `int.dedup`
  then proves all 10 copied facts certain `duplicates` (same text, sender and
  business date). The Aurea nera case cites both copies but counts one origin
  (`n_origin_groups: 1`), and the copy does not refresh
  `last_independent_evidence_at`. Before, the model sampled each copy separately,
  the facts differed, and nothing was proven.
- **Correction (MIL01 18/09, "il fatturato di oggi e' 85,0k e non 58").** The
  model quotes only `il fatturato di oggi e' 85,0k`; dedup now extends the quote
  by a value contrast that follows it directly, so `e non 58` is kept. Wording
  from another clause (`Ritiriamo …, Aurea nera: 9 richieste`) never applies. The parent figure
  `Fatturato: 58,0k` has no stated period, so it is matched only because the
  correction names the replaced value (58 at the replacement's `k` scale), comes
  from the explicit `In-Reply-To` parent, and covers the parent's business day.
  The 85k fact supersedes the 58k fact; only 85k is active and the two are never
  added (`inactive_facts: 1`).
- **NYC01 04/10 "correction, sales were 45.1k not 54.1k" is not applied.** The
  word `correction` precedes the quoted figure, `not` is outside the supported
  Italian/English contrast grammar, and the mail has no `In-Reply-To` parent. Both
  figures are kept as a possible overlap and never added. Matching by subject or
  same-day proximity would be an unsafe heuristic, so it is not done.

## API, UI and isolated jobs

```sh
backend/.venv/bin/python scripts/check_core_demo.py \
  --candidate /absolute/path/to/the/recorded/candidate \
  --decision-output /absolute/path/to/frozen-decisions.json
```

This checks actual published API reads, exact case/trace/clarification versions,
every option's stored artifact refs, evidence offsets, negative/unknown inputs,
same-run report reads and namespace isolation. It exercises a stale-hash 409,
an explicit scripted decision and an identical idempotent retry, with networking
denied. It never substitutes mock UI data. An existing decision output is refused
before issuing any command: preserve the original exact export and choose a new
path only for an explicitly requested synthetic rehearsal. Ordinary verification
omits `--decision-output` and creates no approval.

Verification format 2 binds the result to the actual executing HEAD (with a dirty
code flag), canonical snapshot, namespace/scenario, source/config inventories and
an inventory of exact artifact identities, versions and semantic payload hashes.
The published database RunSpec must equal the supplied candidate, even when the
run ID matches. The artifact inventory describes the published projection before
an optional synthetic decision command; it is not a human acceptance signature.

### Positive POST-investigate job bound to this candidate

`investigate-job/` holds one real GLM investigation of
`case-mil01-j20931a00012-999-20261002` (the Aurea nera case that cites the
resend), recorded through the actual API endpoint. `manifest.json` pins the
parent snapshot hash, the parent artifact inventory (equal to
`api-verification.json`), the case version, the content-derived job ID
`investigate-b3df8405…b9fe`, the trace and every envelope hash. The model calls
evidence, stock four times (one recorded simulated-system read) and the options
engine, then reaches the six-tool budget and publishes a visible `verify`
fallback (`stop_reason: budget_tool_calls`).

Recording uses a private copy of the candidate database (SQLite backup, in a
temporary directory outside the candidate, removed on every exit) in which only
the parent's stored RunSpec is marked live, because the API never records on a
recorded parent; job identity and cache keys exclude execution mode. A job that
stops on the 90-second wall-clock budget is refused: a faster replay would
request a turn that was never recorded. Record again in that case:

```sh
backend/.venv/bin/python scripts/core_investigate_job.py record \
  --candidate /absolute/path/to/the/recorded/candidate \
  --case-id case-mil01-j20931a00012-999-20261002 \
  --output /absolute/path/to/the/recorded/candidate/investigate-job
```

Offline verification needs only the package. Run it against each replay attempt
from the rebuild above:

```sh
backend/.venv/bin/python scripts/core_investigate_job.py verify \
  --attempt "$PWD/data/core_demo/offline-reproduction/attempt-<id>" \
  --job "$demo_assets/investigate-job" \
  --workspace "$PWD/data/core_demo/job-verify"
```

It POSTs the job against the unmodified recorded parent in replay mode with
networking denied. The job ID, trace (ID, version, tools and semantic hash),
job artifact inventory, case version and parent inventory must all match, and
the parent must be unchanged. Both cold attempts passed with zero network
attempts. Withholding one job envelope in a copied job directory makes the job
fail unpublished, with exit 1 and the parent unchanged
(`api-job-verification.json`). Earlier API jobs minted a random trace ID on
every execution, so a replayed job could never reproduce the recorded trace.
The API now uses `trace:<job id>:<case id>` (see `tests/api/test_investigations.py`).

To inspect an offline attempt in the UI, set `demo_attempt` to the returned attempt
directory, then run these in separate terminals:

```sh
LLM_MODE=replay DATA_DIR="$demo_attempt/data" \
  SOURCES_DIR="$demo_attempt/inputs/sources" CONFIG_DIR="$demo_attempt/inputs/config" \
  backend/.venv/bin/uvicorn tesseract.api.main:app --port 8106

cd web
TESSERACT_API_TARGET=http://127.0.0.1:8106 npm run dev -- --port 5186
```

The browser check was repeated on this recording on 2026-10-23 (DEMO-02c, #115).
It used headless Chromium (Playwright) on `make demo-data`, whose output, ledger
and snapshot hashes matched the ones above. All 42 checks passed with 0 page
errors, 0 console errors and 0 API responses ≥ 400. It checked:

- the `recorded` and `degraded` run labels;
- for D1: its evidence refs, the 9 option versions with the transfer leg and its
  22 checks, and the recorded trace (fallback `sì`, outcome `verify`, 7 steps);
- for the unknown-product case: its trace with no fallback, and the Italian
  clarification shown as **Bozza** and **Simulato: sì**;
- the exact quotes highlighted in Fonti;
- after a page reload, the frozen NYC01 decision, read identically through
  `GET /decisions`, `?case_id=` and `/decisions/{id}`.

The screenshots and check log stay local (`data/core_demo/ui-check-20261023/`,
ignored). The summary is on #115. Known gaps:

- The case page does not yet render a saved decision after reload (M5), so
  persistence is verified through the API only.
- The D1 options panel shows both versions of four options, and the current ones
  cannot be approved (#258).

The scoped Memi audit (`web/`, `diagnose . --json --no-write --fail-on none`)
reported 50/100; it is unchanged because this task changes no design tokens or
layout. Its generic design findings are not a G2 functional acceptance score.

## Voice and release limits

The separate #139 voice replay was repeated from the three existing real ASR
envelopes: three cache hits, two recorded notes, one explicitly manual fallback
for an interval exceeding audio duration, ten segments and no errors. These are
`synthetic_extension` notes in their own scenario; they are excluded from this
historical source run and cannot be used for historical forecast accuracy claims.
See `data/fixtures/voice/VERIFICATION.md`. Those ASR envelopes stay ignored and
are not silently presented as part of this portable text candidate.

The run remains synthetic and dev-only. No acoustic alignment score, live phone
connector, hold-out metric, public release, external dispatch or human adoption
result is claimed. The simulated clarification-answer loop on this run's MIL01
question is separate OUT-02e evidence in
`data/fixtures/runs/core-dev-20261023/clarification-answers/VERIFICATION.md`:
three answers in their own scenarios, recorded with real models; this parent stays unchanged. No release tag is created here.

## Checks and handoff to #211

`make check` covers Python lint/format, backend tests, web lint/types/tests and
generated schema consistency. During this rehearsal the shared `/tmp` returned
EDQUOT and SQLite I/O errors; repeating with an isolated temporary directory
completed successfully. The reproducible command is:

```sh
mkdir -p data/core_demo/check-tmp
TMPDIR="$PWD/data/core_demo/check-tmp" make check
```

The gate regressions include `test_gate_temporal.py`, `test_gate_dedup.py`,
`test_gate_blocking.py`, `test_simulation.py`, `test_gate_sizes.py`,
`test_approval_gate.py`, `test_gate_cutoffs.py`, agent runtime/investigator safety
tests and the replay/cache tests. #211 owns the final invariant audit, human
sign-off, candidate selection, export freeze and eventual `freeze-g3` tag after
review/merge. `decisions.json` is a scripted synthetic reviewer command.
`decisions-operator.json` is the genuine operator decision, Lorenzo's local
rejection of the D1 transfer. The NYC01 correction abstention, the D1 fallback
and #258 must remain visible in that handoff.
