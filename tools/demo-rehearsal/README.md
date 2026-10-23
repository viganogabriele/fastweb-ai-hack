# Timed demo rehearsal (DEMO-03)

`rehearse.mjs` drives the real UI through the click path of
[docs/demo_script.md](../../docs/demo_script.md) with Playwright and records a video. Each beat
is timed from the start of the recording, so a run gives a measured duration rather than the
sum of targets. It never edits `web/` and never mocks the API: it needs `make demo` running on a
fresh replay attempt.

## Run

```sh
make setup
(cd tools/demo-rehearsal && npm ci && npx playwright install chromium)   # once
rm -f data/demo/current && make demo        # fresh attempt; keep it running
# second terminal
cd tools/demo-rehearsal
node rehearse.mjs --base-url http://localhost:5173 --out ../../data/demo/video/take-$(date -u +%Y%m%dT%H%MZ)
```

Options: `--pace 1` (default) holds each screen for its speaking time; `--pace 0.1` is a fast
smoke run. `--no-captions` records the bare UI (for a voice-over). `--slide <file>` replaces the
closing results slide. `--reviewer <name>` is the local reviewer identity typed in the decision
beat. The output directory must not exist and should be under ignored `data/`.

The run refuses to start if the unknown-product case already has a decision in this attempt
(re-run `rm data/demo/current && make demo-data`, then restart the backend).

## Output

- `rehearsal.webm` (Playwright recording) and `rehearsal.mp4` (H.264, if `ffmpeg` is on `PATH`).
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
