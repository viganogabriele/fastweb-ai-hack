# DEMO-02: source-backed Core candidate and offline handoff

This is the integration evidence for #115 and the input to #211's human release
review. It is a historical **synthetic dev** rehearsal, not a hold-out result,
an actual operator approval, a production transfer or a public bundle.

## Frozen inputs and recordings

The portable package is `data/fixtures/runs/core-dev-20261023/`. Its location
does not make the run a fixture: the RunSpec has `mode: recorded`, the namespace
is `product`, and `authorized_fixture_refs` is empty. The normal fixture loader
does not load this nested package. No derived projections are preloaded.

The actual provider recording executed commit
`8e3436f084557e55b1979fc88ab84690be252ff4` (DEMO-02b, PR #237: source-backed
correction/resend handling). It replaces the earlier `f1d7923` recording, whose
resend and correction emails produced zero certain relations. The positive
POST-investigate job was recorded at `5cdcc1c2efa6d126fdbf32bfc895b9330efd6415`,
which adds only the deterministic API job trace ID and job-script fixes (no
pipeline module changed); the job is bound to this
candidate's snapshot. Later commits that do not change executable code keep
these identities; the final verification SHA is recorded in the PR/#211 handoff.

- Clock: `2026-10-22T20:00:00Z`; dev stores MIL01, MIL02, MUN01, NYC01.
- 12 explicitly selected Italian, English and German emails, including resend,
  correction, reply and out-of-office inputs; one actual W42 workbook; Milan and
  Munich weather feeds; 60 days of ERP history with row availability filtering.
- 108 selected source files; source tree SHA-256
  `a3d3d221987593f9512ddc82265a1f518da4218efd88e66c7a00f433b9984d70`.
- Four configuration files; tree SHA-256
  `fb50f57d8b4b1ad55076726fab97f2ee586b2ea3098b96f7aed651d5e9a89bc8`.
- 20 real provider envelopes: Gemma extraction/constrained linking and GLM
  investigation, plus 6 GLM envelopes for the separate investigate job in
  `investigate-job/`. GLM's outside-EU hosting is already disclosed in
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
  --code-version 8e3436f084557e55b1979fc88ab84690be252ff4 \
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

For the two negative rehearsals, copy a cache outside the owned replay workspace,
withhold one envelope in that copy and pass it to the same command. The actual
LLM-negative run withheld key
`0fab8264445c2d83079b0401bcd0ef3288ad096b7f87c6d8ec1e0bc50bf9e333`;
the systems-negative run withheld
`0295a3b534fa4a2eb1ad46e088a5447f9706ae602a7f755e022d62669af5c45f`.
Both must exit 1, list recording misses, skip decision replay and report zero
network attempts. Original caches and previous positive attempts remain intact.

## Actual Core outcome

The completed recording and two fresh cold replays publish:

- 13 documents, 206 segments, 74 observations with 74 independently validated
  exact document/segment quote spans, and 74 entity links.
- 37 current cases (48 stored case versions), including unresolved products kept
  visible as `verify`; the out-of-office input produces no observation.
- 110 evidence relations: **10 certain `duplicates`**, **1 certain `supersedes`**
  and 99 possible overlaps (29 non-additive origins). 74 facts form 64 origin
  groups, 63 of them active. 16 report metric facts, two actual weather context
  events, 346 baselines and 28 case overlays.
- 158 stored option versions, two investigator traces, one simulated clarification
  draft, two owner/priority reports, and an exact versioned local decision draft.
- No fabricated numerical uplift: overlays stay unchanged with explicit reasons;
  missing baseline coverage remains `not_estimable`. No transfer is recommended.

Both replays: output `0f35766e7a950806bbad4be407f8a8cbe3d16032b7653bfdaabb976f9977fb6a`,
ledger `f6e6983f363605a2261dbb9c3f7d733a95df36f63c6268b034bff59122795508`,
snapshot `303f1a81962c331141364203f6e53846c37fa762e2ab6cbae655ed1ffcb014ae`,
exit 0, no missing prerequisites and zero network attempts (`replay-comparison.json`).

The final status is honestly `degraded`: unknown SKU scopes require verification,
the optional product-insights module is absent, the NYC01 correction abstains (see
below) and the D1 investigator reaches the six-tool budget. D1 calls evidence,
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
  model quotes only `il fatturato di oggi e' 85,0k`; dedup now reads the whole
  sentence of the fact's own segment, so `e non 58` is kept. The parent figure
  `Fatturato: 58,0k` has no stated period, so it is matched only because the
  correction names the replaced value (58 at the replacement's `k` scale), comes
  from the explicit `In-Reply-To` parent, and covers the parent's business day.
  The 85k fact supersedes the 58k fact; only 85k is active and the two are never
  added (`inactive_facts: 1`).
- **NYC01 04/10 "correction, sales were 45.1k not 54.1k" abstains.** That mail
  has no `In-Reply-To` parent, and `not` outside the supported Italian/English
  contrast grammar is treated as uncertain wording. Both figures are kept, with
  the explicit abstention `uncertain correction intent; facts retained`. Matching
  by subject or same-day proximity would be an unsafe heuristic, so it is not done.

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
`investigate-5ae70946…65cc`, the trace and every envelope hash. The model
calls evidence, then stock four times with guessed sizes that the crosswalk
rejects before any HTTP call, and finishes `verify` without fallback, so the job
needs no systems recordings.

Recording uses a private copy of the candidate database in which only the
parent's stored RunSpec is marked live, because the API never records on a
recorded parent; job identity and cache keys exclude execution mode. The copy
is deleted afterwards:

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

Browser verification was done on the earlier `f1d7923` candidate and has not
been repeated for this recording, so no `ui-verification.json` is packaged. The
UI reads the same API, which `check_core_demo.py` verifies above.

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
connector, clarification-answer loop, hold-out metric, public release, external
dispatch or human adoption result is claimed. No release tag is created here.

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
review/merge. The packaged decision is a scripted synthetic reviewer command, not a
genuine operator decision; freezing a real operator decision stays open for a
human. The NYC01 correction abstention and the D1 fallback must remain visible in
that handoff.
