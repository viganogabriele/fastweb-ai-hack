# ING-03b verification of DATA-03

Status on 2026-10-23: **blocked, recording incomplete**. `Settings.asr_key()` reports no
ASR credential in either this worktree's normal configuration or the main checkout's
configuration loaded through `Settings(_env_file=...)`. No credential was printed or
copied. No ASR request was made, so server reachability is unverified. No real ASR
response, ASR accuracy claim or successful recorded replay is claimed here.

## Fixture checks

`backend/.venv/bin/python data/fixtures/voice/verify.py --mode check` validates all
three WAV hashes, mono 16 kHz format, declared duration within 0.1 s, manual transcript
publication, character offsets, absence of fallback timestamps, and availability at
`2026-10-22T20:00:00Z` (22:00 Europe/Rome). MIL01 and MIL02 agree with the store master.
No sidecar correction or product module change was needed.

All three notes are **synthetic_extension**, with no related historical email. There
are **no paraphrase notes** in DATA-03. These independent scenarios must stay out of
historical WAPE, including forecasts influenced by them; use a separate demo run.
This task does not change the evaluation pipeline or certify its exclusion filter.

The following are manual reference claims to check against real ASR, not observed ASR
results. Hashes use the module's stripped UTF-8 transcript, rather than raw file bytes.

- `mil01-cashmere-scarf-vest-size`: 40.448 s; sent at 19:40 +02:00.
  Reference hash: `sha256:9882b4a799c6d64793f8c2ea4d84386db20bb914b25ecdd6c3289a372e15b87f`.
  Check cashmere scarf, grey melange and beige; six handled, three appreciated,
  one beige request; navy down vest, two clients needing size 3, only 2 and 4
  stated available. Payment-terminal retry counts are operational context.
  **ASR differences: not assessable, no recording available.**
- `mil01-melange-touch-belted-coat-fit`: 30.720 s; sent at 19:05 +02:00.
  Reference hash: `sha256:bf21299bee230d9a19dff75d30bc328db18411bf8875b5782ce7153cc7cd4879`.
  Check grey melange wool down jacket (four clients); chocolate belted long down
  coat (three clients, size 2, tight waist); five-minute outage is operational context.
  **ASR differences: not assessable, no recording available.**
- `mil02-navy-long-down-lining`: 49.3226875 s; sent at 19:20 +02:00.
  Reference hash: `sha256:1ae275ef7c053d22beec0f1ba80f0f7c996e0ddcfd181905eca23d301ef045df`.
  Check navy long down jacket (five clients, two visible reactions), lining complaint,
  one hoodless request; black padded cardigan (two tried, one bought). Rain, traffic
  and tomorrow's staffing shortage are context, not additional SKU quantities.
  **ASR differences: not assessable, no recording available.**

## Observed offline publication

`verify.py --mode replay` denies socket connections and ran the actual `src.voice`
through the orchestrator and repository. Run
`ing03b-replay-5e84df02-1f82-49bd-9aff-ab1516ad3fc4` published three documents and three
segments with status `degraded`: **zero recorded, three declared**. Every document has
`meta.transcript_mode = fixture`, the reference hash above, and a validated segment
with `t_start_s = t_end_s = null`. The module's `mode: recorded` describes the requested
mode; it is not proof of a recorded transcript. Each abstention explicitly states
`ReplayMiss` and `declared transcript used`.

Expected cache keys for this verification snapshot (all missing):

- scarf/vest: `c9c152587e8f24070c43f8117120f703ee89e9fda74b8a1597b5425ab6062490`
- melange/coat: `e1ffa92526398bc3cf10d5c0e218848a8a342ee1a51d708c30f06eebb7d404b0`
- navy/lining: `86b71ba0de2c099154a68bf8c764ad8627e61a681c64eb65408ee04e2336b9f4`

Local evidence is in `data/voice_verification/<run_id>.json` and `runs.db`, both
gitignored. The JSON contains the exact spec, published documents/segments, module
result, reference text/hashes and successful-call cache traces. The command returns
nonzero for degraded publication or unusable intervals, so fallback is not counted
as successful recording. This evidence is not included in a clone of the PR.

## Resume recording

Have the authorized consumer configure their own ASR credential out of band, then:

```sh
backend/.venv/bin/python data/fixtures/voice/verify.py --mode record
backend/.venv/bin/python data/fixtures/voice/verify.py --mode replay
```

When reusing an existing checkout's config, supply `--env-file /path/to/checkout/.env`.
Only `Settings` loads it; the script obtains credentials via `Settings.asr_key()`.
The configured ASR base URL/model are preserved. Cache and evidence always go into
this checkout's `data/`, avoiding writes to the checkout providing configuration.

Record mode executes real ASR on cache misses and uses existing immutable responses
on hits. Replay denies network connections. Inspect the JSON's manual text versus
published ASR text and segments for each product/count above, and document actual
differences here before marking #139 complete. Check every interval against the
audio (the utility rejects empty, reversed or out-of-duration intervals). If the
server provides no usable segments, keep the explicit fallback reason and null
timestamps; do not manufacture intervals or relabel the fallback as recorded.

Recordings belong at `data/llm_cache/<first-two-key-chars>/<key>.json`. Never force-add
them or credentials to Git. Offline demos on another checkout/machine need a separate
copy of these cache envelopes plus identical audio, hints, configured ASR URL/model
and run provenance. The run-bound cache identity includes the selected store set,
as-of, module/config/source snapshot and model versions: recording this voice-only
verification snapshot does **not** warm a different full-demo RunSpec. Record the
actual demo snapshot separately, or use this exact snapshot for the voice demo.
Run IDs and execution mode alone can change without invalidating its cache.
