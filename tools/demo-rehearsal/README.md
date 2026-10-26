# Timed demo rehearsal (DEMO-03)

`rehearse.mjs` drives the real UI through the click path of
[docs/demo_script.md](../../docs/demo_script.md) with Playwright and records a video. Each beat
is timed from the start of the recording, so a run gives a measured duration rather than the
sum of targets. It never edits `web/` and never mocks the API: it needs
`serve-core-dev.sh` running a fresh replay attempt of the recorded `core-dev-20261023` run.

## Run

```sh
make setup
(cd tools/demo-rehearsal && npm ci && npx playwright install chromium)   # once
tools/demo-rehearsal/serve-core-dev.sh     # fresh attempt; backend :8000, web :5173
cd tools/demo-rehearsal
node rehearse.mjs --base-url http://localhost:5173 --out ../../data/demo/video/take-$(date -u +%Y%m%dT%H%MZ)
```

Options: `--pace 1` (default) holds each screen for its speaking time; `--pace 0.1` is a fast
smoke run. `--no-captions` records the bare UI (for a voice-over). `--slide <file>` replaces the
closing results slide. `--reviewer <name>` is the local reviewer identity typed in the decision
beat. The output directory must not exist and should be under ignored `data/`.

The run refuses to start if D1 already has a decision in this attempt: re-run
`serve-core-dev.sh` (it starts a new attempt and restarts the backend it started).
`make demo` serves a different, later run (production-demo, #257) and does not fit this path.

## Current preparation status

The 2026-10-26 normal-paced internal take completed in 232.917 seconds; metadata
and file hashes are in [the verification record](../../docs/demo_bundle/verification-20261026.json).
It uses the current collapsed overview, explicitly expands **Mostra decisioni**,
and identifies the approval beat as automated rehearsal rather than a human
operator's decision. The closing slide states that evaluation results are unavailable.

Reports explicitly carry `status: internal_rehearsal_only` and `release_ready: false`.
The current recording contains names flagged by the deny scan and is not a public
video. The scan reads DOM text conservatively (including text outside the viewport)
at beat boundaries, not every video frame; it cannot certify video privacy.
Final metrics and a separately reviewed public take remain #128/#129.

## Output

- `rehearsal.webm` (raw Playwright recording, up to the browser closing) and `rehearsal.mp4`
  (H.264, if `ffmpeg` is on `PATH`, cut at the end of the last beat). `walkthrough_s` in
  `rehearsal.json` is the measured duration of the walkthrough.
- `rehearsal.json`: beat timeline (`start_s`, `end_s`, target), caption text, console errors,
  per-file sha256 and a playback check: `ffprobe` when installed, otherwise a full `ffmpeg`
  decode of every frame (a decode error fails the run). It also lists **deny hits**: brand names,
  email addresses, hold-out store ids or token fragments seen in the visible text of a beat. A
  hit is reported, never hidden.
- `captions.srt`: one cue per beat, for subtitles or a voice-over script.
- `NN-<beat>.png`: one screenshot per beat for review.

## Captions

The caption bar is injected into the page at recording time (bottom 56 px, above the UI). It
carries the spoken line and the disclosure "Dati sintetici · replay registrato offline · azioni
simulate (bozze locali)", because the UI has no disclosure strip yet
(demo-walkthrough M1). It is not part of the application.
