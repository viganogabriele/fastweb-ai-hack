# Voice notes (lane A)

Store voice notes read by `src.voice` (`backend/tessera/modules/sources/voice.py`). RFC §5.2:
2-3 recordings of 20-60 s (it/en) made by the team, no real personal data, plus a **manual
transcript** written by the person who recorded them. DATA-03 (#29) produces the recordings;
`src.voice` is intentionally stricter than a hand-written fixture so a bad file fails loudly.

One folder per note, named after its `note_id`:

```
data/fixtures/voice/<note_id>/
  note.json        sidecar metadata (below)
  <audio>          the recording, as named by note.json (wav/mp3; ogg only after a smoke test)
  transcript.txt   the manual transcript, UTF-8 (name configurable in the sidecar)
```

Nested folders, not flat files: `tessera fixtures load` treats every `data/fixtures/*/*.json` as
a list of stored contract records, and a sidecar is neither.

## `note.json`

| Field | Required | Meaning |
|---|---|---|
| `note_id` | yes | Must equal the folder name, e.g. `mil01-cardigan-unavailable` |
| `store_id` | yes | Master-data store id (`MIL01`...); notes for stores outside a run are skipped |
| `sent_at` | yes | ISO instant **with offset**, e.g. `2026-10-09T18:40:00+02:00`; the note is available from then, never from the file's mtime |
| `timezone` | yes | IANA zone of the store, used for `business_date` (`Europe/Rome`) |
| `language` | no | Language tag (`it`, `en`); when set it is the ASR language hint, never inferred |
| `author_ref` | yes | Pseudonymous author, e.g. `pseudonym:mil01-manager` |
| `fixture_kind` | yes | `paraphrase` (same episode as a dev email, proves ASR/dedup) or `synthetic_extension` (an independent team note, scenario separate from the historical ground truth) |
| `audio` | yes | Audio file name inside the folder |
| `audio_sha256` | yes | `sha256:` + 64 hex digits of that file. A mismatch is an error: the transcript was checked against different bytes |
| `duration_s` | no | Declared duration |
| `manual_transcript` | no | Transcript file name, default `transcript.txt`; must not be empty |
| `related_source_refs` | no | URIs of the sources the note refers to (e.g. `dataset://store_emails/MIL01/...eml`) |
| `asr_prompt` | no | Spelling hint for product names, not context |

Example:

```json
{
  "note_id": "mil01-cardigan-unavailable",
  "store_id": "MIL01",
  "sent_at": "2026-10-09T18:40:00+02:00",
  "timezone": "Europe/Rome",
  "language": "it",
  "author_ref": "pseudonym:mil01-manager",
  "fixture_kind": "paraphrase",
  "audio": "cardigan.wav",
  "audio_sha256": "sha256:<64 hex digits>",
  "duration_s": 38.4,
  "manual_transcript": "transcript.txt",
  "related_source_refs": ["dataset://store_emails/MIL01/20261009_1035_MIL01.eml"]
}
```

## What a run publishes

- `mode: recorded` (default): `transcribe()` on the team ASR server; one `Segment` per ASR
  segment with the server's `t_start_s`/`t_end_s`, text version `voice-asr-v1`.
- `mode: fixture`: the declared transcript, one segment, no intervals, text version
  `voice-transcript-v1`. Also the fallback when the ASR is unreachable or returns nothing
  usable: the note is published with `meta.transcript_mode = "fixture"` and an abstention.
- `meta.manual_transcript_sha256` in both modes: the reference used to check the ASR.
- Audio evidence timestamps exist only in `recorded` mode and only from real ASR intervals.

Rebuild nothing here by hand: the files are the source. Record a note, compute
`sha256sum cardigan.wav`, write `note.json` and `transcript.txt`.

## The recorded notes (DATA-03)

Three Italian closing notes recorded by the team on phones (m4a, AAC 48 kHz), converted to WAV
16 kHz mono PCM with no metadata (`ffmpeg -i in.m4a -ar 16000 -ac 1 -c:a pcm_s16le
-map_metadata -1 note.wav`). All are `synthetic_extension`: independent notes, not paraphrases of
a dataset email, sent on the demo evening (2026-10-22, before the evening run).

| `note_id` | Store | Length | Signals in the note |
|---|---|---|---|
| `mil01-melange-touch-belted-coat-fit` | MIL01 | 31 s | grey melange wool down jacket rejected on touch (4); chocolate belted long down coat, size 2, tight at the waist (3); 5-minute connection outage |
| `mil02-navy-long-down-lining` | MIL02 | 49 s | navy long down jacket put down over the lining (5), a request for it without hood; black padded cardigan tried by 2, 1 sold; low traffic, rain; one person short tomorrow |
| `mil01-cashmere-scarf-vest-size` | MIL01 | 40 s | grey melange cashmere scarf liked, a request for beige; navy down vest, size 3 missing (2 and 4 only), 2 walk-outs; payment terminal froze |

Every product named exists in the catalogue, with the catalogue's sizes (outerwear is numeric).
The products handled or tried are in the store's assortment; the requested beige scarf is not
in MIL01's assortment. Expected links, for the manual labels:

| Spoken | Expected SKU | Note |
|---|---|---|
| piumino in lana grigio melange | `J10911A00213-90X` | the only wool down jacket; `90X` also on the ripstop down jacket and the padded cardigan at MIL01 |
| cappotto lungo in piumino con cintura, marrone cioccolato, 2 | `J20931A00622-23R-2` | unique; MIL01 stock on 2026-10-21 has 0 of size 2, so "tried in size 2" conflicts with stock |
| piumino lungo blu notte | `J20931A00087-742` or `J20931A00203-742` | ambiguous at MIL02; `J20931A00087` has a detachable hood, so "without hood" is not unmet demand for it |
| cardigan imbottito nero | `I10919B00042-999` | unique |
| sciarpa in cashmere grigio melange / beige | `I10913A00004-90X` / `I10913A00004-034` | beige is in the catalogue but not in MIL01's assortment |
| gilet in piumino blu notte, 3 | `J10911A00305-742-3` | the only navy down vest; MIL01 stock on 2026-10-21 has 7 of size 3, so "only 2 and 4" conflicts with stock and must surface as a conflict, not be reconciled |

Connection outages, the payment terminal, traffic, weather and staffing are operational or context
notes, not SKU signals. The transcripts were written from the script the speakers read; check them
against the ASR output when the cache is recorded (ING-03b, #139).

ING-03b status, verified reference hashes, observed fallback publication and safe
record/replay commands are in [VERIFICATION.md](VERIFICATION.md). All three real ASR
responses are cached; two notes publish recorded intervals and one explicitly falls
back to untimed manual text because the server returned an end past the audio duration.

## Live notes from the phone (DEMO-04)

`/store/record?store=<STORE_ID>` (opened from a per-store QR) records a note in the browser and
shows a live transcript: every 4 s the recording so far goes to `POST /api/voice/transcribe` (team
ASR, never cached; 20 calls/min per key). On stop the store checks the text and sends it:
`POST /api/voice/notes` writes `data/voice_inbox/<note_id>/` (gitignored) with the same three
files as above and `fixture_kind: "live"`; `transcript.txt` is the accepted live ASR text, not a
hand-written one. `src.voice` reads this folder next to `data/fixtures/voice/`.

The dashboard top bar shows "Elabora note vocali (N)" while notes wait; it calls
`POST /api/voice/process`, which starts one small product run per store over the new notes: scenario `live-voice`, `as_of` now, only `src.voice → ing.extract → int.link →
int.dedup → int.cases` (+ `src.erp`). `src.email` is given a file outside the run's stores so it
reads no mail; the run is therefore `degraded` by design. LLM calls run in `record` mode, so the
run replays later without keys. Notes whose run failed or was blocked are offered again. The
dashboard lists runs by `as_of`, so the live run becomes the default selection; pick the demo
run again from the run menu. After the run the button selects it and opens Cases.

Demo checklist:

- Keys: Fastweb chat key (`.secrets/fastweb_keys.json`) and `ASR_API_KEY` in `.env` on the
  laptop that runs the backend. Without the ASR key the page says so and the text can be typed.
- The microphone needs HTTPS on the phone: `make dev`, then `cloudflared tunnel --url
  http://127.0.0.1:5173` (`brew install cloudflared`) and put
  `https://<name>.trycloudflare.com/store/record?store=MIL01` in the QR. Vite allows
  `*.trycloudflare.com` and `*.ngrok-free.app` hosts.
- Name the model when speaking ("il gilet VEL blu notte taglia 3"): descriptions alone often
  stay unlinked and open a "to verify" case.
