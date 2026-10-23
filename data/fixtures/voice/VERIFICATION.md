# ING-03b verification of DATA-03

Status on 2026-10-23: **recording and offline replay verified**. The authorized ASR
endpoint `https://hack-sst.lorenzocorallo.net/v1`, model
`openai/whisper-large-v3-turbo`, returned HTTP 200 for all three actual WAV files.
Credentials were loaded only through `Settings(_env_file=...)` and `Settings.asr_key()`;
no credential was printed or committed. All three real response envelopes are cached.
Two notes publish recorded transcripts with real intervals. The third explicitly
falls back to its manual transcript because the server's final interval exceeds the
audio duration; its published timestamps are null. It is not relabeled as recorded.

## Integrity, availability and scope

`backend/.venv/bin/python data/fixtures/voice/verify.py --mode check` validates all
three WAV hashes, mono 16 kHz format, declared duration within 0.1 s, stripped UTF-8
manual-transcript hashes, character offsets and absence of manual timestamps.
All notes are available at `2026-10-22T20:00:00Z` (22:00 Europe/Rome); MIL01/MIL02 agree
with the store master. Earlier verification denied audio loading entirely at
`2026-10-22T17:00:00Z`, and for a ROM01-only run. No sidecar correction was needed.

All three notes are **synthetic_extension**, independent of historical emails.
There are **no paraphrase notes** in DATA-03. Keep them and forecasts influenced by
them out of historical WAPE; use the separate synthetic voice demo scenario. This
PR does not modify or certify the evaluation pipeline's exclusion filter.

## Actual manual-versus-ASR comparison

The reference hashes below match each published document's
`meta.manual_transcript_sha256`. Comparison is against the supplied manual script;
an ASR-only word is a difference, not proof of an audio hallucination. Raw responses
and full manual/ASR texts remain in the ignored local evidence/cache.

- `mil01-cashmere-scarf-vest-size`: 40.448 s; sent at 19:40 +02:00.
  Reference: `sha256:9882b4a799c6d64793f8c2ea4d84386db20bb914b25ecdd6c3289a372e15b87f`.
  Products, colours and quantities preserved: cashmere scarf, grey melange/beige,
  six handled, three appreciated; two clients seeking navy down vest size 3,
  only 2 and 4 stated available. ASR changes “una signora” to “la signora”, weakening
  the explicit one-request wording; “Montenapoleone” becomes “a Monte Napoleone”,
  “in negozio” becomes “il negozio” twice, and “primo pomeriggio” loses “primo”.
  Payment retries remain three; the final “a chi di dovere” loses “di”. Punctuation
  and digit/word representations differ. Published **recorded**, three server
  intervals: `[0, 15.64]`, `[16.4, 25.900000000000002]`, `[25.9, 39.18]` seconds.
  The tiny floating-point overlap at 25.9 is preserved, not rewritten.
- `mil01-melange-touch-belted-coat-fit`: 30.720 s (sidecar 30.7); sent at 19:05 +02:00.
  Reference: `sha256:bf21299bee230d9a19dff75d30bc328db18411bf8875b5782ce7153cc7cd4879`.
  Grey melange wool down jacket/four clients and chocolate belted long down coat/
  three clients/size 2/tight waist are preserved. Five-minute outage preserved.
  ASR spells counts as words, changes “riverificasse” to “riferificassi”, and adds
  “Grazie.” absent from the manual script. Raw server intervals: `[0, 12.06]`,
  `[13.4, 22.3]`, `[23.580000000000002, 29.92]`, **`[30, 31]`**.
  The last end exceeds both the 30.720 s WAV and 30.7 s sidecar. Published **fixture
  fallback**, one manual segment with `t_start_s = t_end_s = null`, with abstention:
  `UnusableTranscript: ASR interval ends at 31s beyond audio duration 30.7s` and
  `declared transcript used`. The real ASR response is still cached unchanged.
- `mil02-navy-long-down-lining`: 49.3226875 s; sent at 19:20 +02:00.
  Reference: `sha256:1ae275ef7c053d22beec0f1ba80f0f7c996e0ddcfd181905eca23d301ef045df`.
  Navy long down jacket/five clients/two visible reactions, plastic-like lining,
  one hoodless request, black padded cardigan/two tried/one bought all preserved.
  “posato” becomes “apposato”; quotation marks disappear; “dal pomeriggio” becomes
  “del pomeriggio”. The staffing phrase “fascia pomeridiana” becomes the malformed
  “faccio pomerigiana”, though “un collega in meno” survives. Do not silently
  normalize this operational context into additional SKU demand.
  Published **recorded**, six server intervals: `[0, 16.580000000000002]`,
  `[17.76, 23.54]`, `[23.54, 32.4]`, `[34.04, 39.66]`, `[40.86, 43.96]`,
  `[45.18, 48.620000000000005]` seconds.

All published recorded intervals have positive length, start within the audio and
end within its measured duration. This is a numeric bounds/quote validation, not a
human listening assessment of word-level alignment. No timestamp was estimated,
clamped or fabricated. A genuine module format fix rejects zero-length intervals
and intervals past the declared audio duration, using the existing explicit manual
fallback path. Regression tests cover both cases.

## Observed execution and portable evidence

Initial real calls (all first attempt, HTTP 200; approximately 5.06, 3.80 and 5.77 s):
`ing03b-record-b729ccc0-39b4-450e-9fc1-8a304a193295`. This pre-fix run published all
three as recorded, but the verifier correctly exited nonzero for the bad interval.
After the format fix, record mode reused those immutable actual responses:
`ing03b-record-ccf5ee89-b7a1-46d3-8d87-012e54d93ba8`.
Network-denied replay:
`ing03b-replay-f5b3bf3c-493a-4d9d-b7e2-0be7b5b4728f`.
Both final runs verified **three cache hits, two recorded documents, one explicit
interval fallback, ten published segments, zero errors**. Module status is honestly
`degraded` for that fallback. The verifier accepts this only when every real response
is cached/successful and every fallback has an explicit `UnusableTranscript` reason;
missing credentials, network failure and `ReplayMiss` remain incomplete.

Cache keys (each at `data/llm_cache/<first-two-chars>/<key>.json`):

- scarf/vest: `c9c152587e8f24070c43f8117120f703ee89e9fda74b8a1597b5425ab6062490`
- melange/coat: `e1ffa92526398bc3cf10d5c0e218848a8a342ee1a51d708c30f06eebb7d404b0`
- navy/lining: `86b71ba0de2c099154a68bf8c764ad8627e61a681c64eb65408ee04e2336b9f4`

These three envelopes and the three worktree execution JSONs were copied to
`/home/gabriele/dev/fastweb-ai-hack/data/` without replacing unrelated cache entries.
The worktree DB was backed up there as
`voice_verification/ing03b-d3ad7e89-runs.db`. A further network-denied replay using the
root cache passed with identical publication:
`ing03b-replay-df466e06-066b-4948-bc8a-6486be938d0a` in the root's `runs.db` and JSON.
An earlier root replay hit all three envelopes but reported an incidental utility
`__pycache__` directory as an invalid note; that generated directory was removed
and the successful replay above supersedes it. The failed evidence remains honest.

Cache and evidence are **gitignored and do not travel with this PR**. Keep the
actual envelopes and JSON/DB evidence separately for the offline demo. Never
force-add these or credentials. Cache identity includes audio, hints, configured ASR
URL/model and run provenance (stores, as-of, module/config/source snapshot/model
versions). This voice-only snapshot does **not** warm a different full-demo RunSpec;
record the actual demo snapshot separately or reuse this exact snapshot. Run IDs
and execution mode alone may change without invalidating its cache.

## Reproduce

```sh
backend/.venv/bin/python data/fixtures/voice/verify.py --mode check
backend/.venv/bin/python data/fixtures/voice/verify.py --mode record
backend/.venv/bin/python data/fixtures/voice/verify.py --mode replay
```

For another checkout's authorized configuration, add `--env-file /path/to/checkout/.env`.
Only Settings loads it. Record uses the provider on cache misses; replay denies
socket connections. Cache/evidence are written to the executing checkout's `data/`.
Exit zero means cached responses plus valid recorded publication or explicitly
explained unusable-response fallbacks, not that every transcript is recorded.

Initial validation before syncing main: plain `make check` reproduced existing
issue #203 (1618 backend passes, one eval isolation failure:
`_Py_HashRandomization_Init: failed to get random numbers to initialize Python`).
The isolation code was left untouched. `PYTHONHASHSEED=0 make check` passed all 1621 backend tests (including both new
interval regressions), lint/format, web lint/typecheck, 38 web tests and schema
verification. Explicit verifier Ruff lint/format and `git diff --check` also passed.

## Independent offline review (2026-10-23)

Reviewed head `610009740669241aaf9db3c42b65fbee194f68b0` in an isolated checkout,
then merged main at `7202e78` to include the Landlock test fix from #204. No further
product-code defect was found. No provider calls, credential reads or listening
assessment were performed by this review.

The three existing root-cache envelopes passed checksum validation. Their original
record traces show first-attempt HTTP 200 responses, and the manual scripts agree
with the differences documented above. Fresh network-denied replay after the merge
(`ing03b-replay-c490e587-dbce-4f5d-b274-97b776c3dede`) reproduced three cache hits,
two recorded documents, one explicit duration-invalid manual fallback, ten segments
and zero errors. The reference transcript hashes matched all three published documents.
This verifies replay, numeric interval bounds and reference comparisons; it does
not establish word-level acoustic alignment or an ASR accuracy score.

A negative replay with one cache envelope temporarily withheld exited 1 with
`ReplayMiss`, despite publishing its manual fallback. Actual-sidecar runs at
`2026-10-22T17:00:00Z` and for ROM01 alone skipped all three notes without opening
audio or publishing documents. Only copied cache entries in the isolated checkout
were changed for the negative check; the root cache remained untouched.

Plain `make check` now passes without `PYTHONHASHSEED`: **1655 backend tests,
74 web tests**, Python lint/format, web lint/typecheck and generated-schema check.
Fixture integrity check, explicit verifier Ruff lint/format and `git diff --check`
also pass. Issue #139's recorded-response, explicit-fallback and comparison
acceptance is satisfied for this voice-only snapshot. The separate full-demo cache
portability limitation above remains; it is not a claim that another RunSpec is warmed.
