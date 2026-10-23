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
