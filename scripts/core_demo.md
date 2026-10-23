# DEMO-02: source-backed Core candidate and offline handoff

This is the integration evidence for #115 and the input to #211's human release
review. It is a historical **synthetic dev** rehearsal, not a hold-out result,
an actual operator approval, a production transfer or a public bundle.

## Frozen inputs and recordings

The portable package is `data/fixtures/runs/core-dev-20261022/`. Its location
does not make the run a fixture: the RunSpec has `mode: recorded`, the namespace
is `product`, and `authorized_fixture_refs` is empty. The normal fixture loader
does not load this nested package. No derived projections are preloaded.

The actual provider recording executed commit
`f1d7923c788bdc519fcab5460dfe4ad1b9de8af0`. Later integration changes add exact
decision replay validation and verification tooling; their checks run on the PR
head. The exact final verification SHA is recorded in the PR/#211 handoff, rather
than incorrectly changing the recording's historical code identity.

- Clock: `2026-10-22T20:00:00Z`; dev stores MIL01, MIL02, MUN01, NYC01.
- 12 explicitly selected Italian, English and German emails, including resend,
  correction, reply and out-of-office inputs; one actual W42 workbook; Milan and
  Munich weather feeds; 60 days of ERP history with row availability filtering.
- 108 selected source files; source tree SHA-256
  `a3d3d221987593f9512ddc82265a1f518da4218efd88e66c7a00f433b9984d70`.
- Four configuration files; tree SHA-256
  `fb50f57d8b4b1ad55076726fab97f2ee586b2ea3098b96f7aed651d5e9a89bc8`.
- 23 real provider envelopes: Gemma extraction/constrained linking and GLM
  investigation. GLM's outside-EU hosting is already disclosed in
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
demo_assets="$PWD/data/fixtures/runs/core-dev-20261022"
demo_candidate="$PWD/data/core_demo/reproduction"

backend/.venv/bin/python scripts/prepare_core_demo.py \
  --output "$demo_candidate" \
  --code-version f1d7923c788bdc519fcab5460dfe4ad1b9de8af0 \
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
`a2ae8134e8fecfe2d5e0d143ac2f731e0f2629d21934159d9f04471c877dd4fa`;
the systems-negative run withheld
`92c985b7c07441389193a8a06b19dff3aac15c8c14760acb023ffd97170f34be`.
Both must exit 1, list recording misses, skip decision replay and report zero
network attempts. Original caches and previous positive attempts remain intact.

## Actual Core outcome

The completed recording and fresh replays publish:

- 13 documents, 206 segments, 81 observations with 81 independently validated
  exact document/segment quote spans, and 81 entity links.
- 41 current cases (51 stored case versions), including unresolved products kept
  visible as `verify`; the out-of-office input produces no observation.
- 114 possible-overlap relations, with 45 non-additive origins; 16 report metric
  facts, two actual weather context events, 346 baselines and 26 case overlays.
- 173 stored option versions, two investigator traces, one simulated clarification
  draft, two owner/priority reports, and an exact versioned local decision draft.
- No fabricated numerical uplift: overlays stay unchanged with explicit reasons;
  missing baseline coverage remains `not_estimable`. No transfer is recommended.

The final status is honestly `degraded`: unknown SKU scopes require verification,
the optional product-insights module is absent, and the D1 investigator reaches
the six-tool budget. D1 actually calls evidence, stock twice, lanes twice and the
deterministic options engine, then publishes a visible `verify` fallback. The
unresolved MIL01 case instead calls evidence, drafts a clarification and finishes
without fallback. These are real-model choices on source-derived cases.

The older two successful, non-fallback GLM paths from #199 remain distinct:
`tests/fixtures/test_ag03b.py` verifies their explicitly fixture-backed inputs.
They are not relabeled as source-pipeline outputs or used to replace this run.

The real resend/correction emails are included, but this candidate infers zero
certain duplicate or supersedes relations. It conservatively retains possible
overlaps and does not count them additively. This is not evidence of successful
automatic monetary correction extraction. The dedicated fact-level correction,
copy/forward and time-travel regressions remain the evidence for those specific
invariants; #211 must retain this distinction when reviewing G2/G3 claims.

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

A separate real POST-investigate rehearsal copied the actual published source
snapshot into a private API test database, made an explicitly live recording
parent, recorded a real clarification investigation, reset only that child job
and replayed it with networking denied. The job ID stayed identical, trace
semantics matched, and the parent artifact hash stayed unchanged. This API test
uses a published snapshot as intended; it is **not** the evidence for rebuilding
sources from empty projections. See `api-job-verification.json` and the focused
`tests/api/test_investigations.py` regressions.

To inspect an offline attempt in the UI, set `demo_attempt` to the returned attempt
directory, then run these in separate terminals:

```sh
LLM_MODE=replay DATA_DIR="$demo_attempt/data" \
  SOURCES_DIR="$demo_attempt/inputs/sources" CONFIG_DIR="$demo_attempt/inputs/config" \
  backend/.venv/bin/uvicorn tesseract.api.main:app --port 8106

cd web
TESSERACT_API_TARGET=http://127.0.0.1:8106 npm run dev -- --port 5186
```

Browser verification opened both real case details, expanded the stored trace and
clarification, and verified `recorded`, the explicit D1 fallback, draft status and
simulated labels with no page errors. The T3 preview timed out twice on snapshots;
a separate Playwright browser completed these checks. Screenshots and text stay
in the ignored local candidate directory, not a public bundle.

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
review/merge. The recording's conservative correction and fallback limits above
must remain visible in that handoff.
