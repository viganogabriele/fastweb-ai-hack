# Live voice UI (#191, DEMO-04)

Goal: a store manager records a closing voice note on a real phone. HQ processes it into a
separate **live** run, and the dashboard shows the resulting cases with live provenance. This is
never mixed with the frozen offline replay. Priority: **Should**, and the feature itself is
optional (Could in `docs/PLAN.md` reserve; #129 does not depend on it). Show it in the demo
only after the real-device dry run in §5 passes on the exact build.

Code is merged (#225). What remains: the UI fixes below and the human dry run. Runtime and
operator setup: `data/fixtures/voice/README.md:105-153`.

## 1. What exists

| Piece | Where | Behaviour |
|---|---|---|
| Phone page | `/store/record?store=MIL01&lang=it#voice-token=<capability>` → `web/src/main.tsx:8-11`, `web/src/store/RecordPage.tsx` | Big record button; live partial transcript every ≤4 s; auto-stop before 90 s (`web/src/store/recorderSession.ts:68-78`); editable final text; send |
| API client | `web/src/store/voiceApi.ts:16-63` | Bearer token from the URL fragment (`voiceApi.ts:16-17`) |
| Dashboard trigger | `web/src/store/VoiceProcessButton.tsx`, mounted in the top bar (`web/src/App.tsx:200-207`) | Polls `GET /api/voice/notes` every 5 s. "Elabora note vocali (N)" calls `POST /api/voice/process`, polls each run, then selects it and opens Casi |
| Backend | `backend/tesseract/api/routers/voice.py:152-345` | `transcribe` (ASR, never cached), `notes` (save/list), `process` (one `live-voice` run per store, `mode="live"`, `voice.py:270`). Disabled unless `VOICE_ACCESS_TOKEN` is set (`voice.py:68-74`) |

Endpoints and DTOs: `POST /api/voice/transcribe` (multipart `audio`, `language`) → `Transcription {text, duration_s}`.
`POST /api/voice/notes` (multipart `audio`, `store_id`, `transcript`, `language`) → 201 `LiveNoteView {note_id, store_id, sent_at, duration_s, transcript, run_id}`.
`GET /api/voice/notes?store=` → `LiveNoteView[]`.
`POST /api/voice/process` `{store_id|null}` → 202 `RunView[]`.
All require `Authorization: Bearer <capability>`.

## 2. Gaps and acceptance criteria

- [ ] **G1 Token survives dashboard navigation (bug, verified).** Opening
      `/#voice-token=X` and clicking any sidebar item replaces the hash with `#/casi`
      (`web/src/App.tsx:151-165`). The token is gone, `refresh()` stops early
      (`web/src/store/VoiceProcessButton.tsx:24`), and a stale "Elabora (N)" button then
      fails with 401. `onDone` itself navigates (`web/src/App.tsx:205`).
      *Accept:* on load, read `voice-token` once and keep it in `sessionStorage` (tab scope).
      Strip it from the visible URL (`history.replaceState`), and read it from storage in
      `voiceApi`. The hash router ignores it. The token never appears in the DOM, logs,
      screenshots or the run selector.
- [ ] **G2 Early availability check on the phone.** Today a disabled server (503) or wrong token
      (401) is discovered only after recording. *Accept:* on load, call
      `GET /api/voice/notes?store=<STORE>`. Map 401 → "link non valido", 503 → "note vocali
      live disattivate", network → "server non raggiungibile". Disable recording until it
      succeeds.
- [ ] **G3 Live provenance on the phone.** Before recording, the page states "Nota live per la
      demo · elaborata dalla sede · non fa parte del replay offline". During recording it shows
      "Trascrizione automatica provvisoria". The review step says the accepted text is what
      the system reads (`transcript_mode: manual`, `data/fixtures/voice/README.md:120-122`).
      After sending, show `note_id`, store, `sent_at` with zone, "In attesa di elaborazione".
      Today only "Nota inviata" (`web/src/store/RecordPage.tsx:127`).
- [ ] **G4 Recording limit visible**: show remaining time against the 90 s limit, not only
      elapsed seconds (`web/src/i18n/it/record.ts:10`).
- [ ] **G5 Process button feedback.** Show the API `detail` for 409 ("elaborazione già in
      corso", "nessuna nota nuova", "snapshot cambiato") and 503 (`voice.py:305,320,331`).
      Show per-run status while polling. "Riprova" must re-check notes rather than blindly POST.
- [ ] **G6 Live run labelling in the dashboard.** When the selected run has
      `spec.scenario_id === 'live-voice'` / `mode === 'live'`, the disclosure strip (README M1)
      reads "Run live · note vocali dal telefono". The run status `degraded` is explained
      ("nessuna email letta per scelta", `voice.py:9-14`). Sources show `live-voice://` URIs as
      "Nota vocale live", never as dataset files.
- [ ] **G7 Return to the demo run.** Processing makes the live run the default selection
      (`data/fixtures/voice/README.md:136-137`). Offer an explicit "Torna al run demo" control
      that restores the previously selected run id.
- [ ] **G8 Mobile polish**: keep `100dvh` (`web/src/store/recordPage.css:4`), 16 px textarea
      (no iOS zoom; `--sd-font-size-body` is 16 px), safe-area padding, no hover-only cues,
      a focus ring on the mic button. Test real Safari and Chrome.

Out of scope: Telegram/WhatsApp connectors, audio upload from files, live audio in the frozen
replay (`docs/RFC-001-piattaforma.md:529`; #191 acceptance).

## 3. States checklist (phone page)

| State | Must show |
|---|---|
| No `store` param | Existing message (`web/src/i18n/it/record.ts:5`) |
| No/invalid token, server disabled | G2 messages; record button disabled |
| Not HTTPS | "Serve HTTPS" (`record.ts:23`) |
| Mic permission denied | How to re-enable in iOS Safari / Android Chrome settings |
| Recording | Elapsed/remaining time, provisional transcript |
| ASR failed (429/502/503) | Status code and "puoi scrivere il testo a mano" (`record.ts:26`); manual text allowed |
| Sending / send failed | Spinner; error with status and retry; audio and text kept |
| Sent | G3 receipt |

## 4. Manual test script (desktop, before the device run)

1. Backend with `VOICE_ACCESS_TOKEN` set in `.env` (never paste it into issues or chat). `make dev`.
2. Open `http://localhost:5173/store/record?store=MIL01#voice-token=<capability>` in a desktop
   browser with a mic. Check: availability passes (G2), live notice (G3).
3. Record about 15 s naming a model ("il gilet VEL blu notte taglia 3",
   `data/fixtures/voice/README.md:147-148`). Check: the provisional transcript updates, the text
   is editable at stop, send shows the receipt with `note_id`.
4. Open `http://localhost:5173/#voice-token=<capability>`. Check: "Elabora note vocali (1)".
   Click Casi, then Fonti. Check: the button is still present and the URL no longer shows the
   token (G1).
5. Click "Elabora". Check: per-run status, then the live run is selected with the "Run live"
   strip and its cases. "Torna al run demo" restores the previous run (G7).
6. Wrong token in the fragment → "link non valido". Unset `VOICE_ACCESS_TOKEN`, restart →
   "disattivate".

## 5. Real-device dry run (human, required to close #191)

Record the results in #191, without tokens, keys or tunnel URLs. Do it before
**2026-10-25 00:00 UTC** (Fastweb keys expire; `AGENTS.md`, "Backend setup and secrets").

- [ ] Demo laptop: `ffmpeg` on PATH, `ASR_API_KEY` and the Fastweb key configured, **one** backend
      worker (`data/fixtures/voice/README.md:153`), `VOICE_ACCESS_TOKEN` set.
- [ ] HTTPS tunnel up (`cloudflared tunnel --url http://127.0.0.1:5173`). The QR encodes
      `/store/record?store=<dev store>#voice-token=…`. Use dev stores only.
- [ ] iPhone Safari: permission prompt, record, partial transcript, stop, edit, send. Note the
      container that was uploaded (mp4 expected).
- [ ] Android Chrome: same (webm/opus expected).
- [ ] 90 s auto-stop works; a second phone recording at the same time gets a clear 429 message.
- [ ] Dashboard on the laptop: process, live run appears with `live` label, cases open, sources
      show the live note. Then return to the frozen demo run and confirm it is unchanged
      (same counts as before: 41 cases).
- [ ] Network drop mid-send on the phone: error shown, retry works, no duplicate note.
- [ ] Time the whole segment (target ≤ 40 s on stage) and decide go/no-go for the demo.
- [ ] Revoke/rotate `VOICE_ACCESS_TOKEN` after the demo; never show the QR link in the video.
