import { useState } from 'react'
import { Mic, Square } from 'lucide-react'
import { fmt, messages } from '../i18n'
import { Button } from '../ui'
import { useRecorder } from './useRecorder'
import type { RecorderError } from './useRecorder'
import { ApiError, sendNote, voiceToken } from './voiceApi'
import './recordPage.css'

const t = messages.record

const params = new URLSearchParams(window.location.search)
const STORE = (params.get('store') ?? '').trim().toUpperCase()
const LANGUAGE = (params.get('lang') ?? 'it').trim().toLowerCase()

const status = (error: unknown) => (error instanceof ApiError ? error.status : 0)

function errorText(error: RecorderError) {
  return typeof error === 'string' ? t.errors[error] : fmt(t.errors.asr, { status: error.asr })
}

export function RecordPage() {
  const recorder = useRecorder(LANGUAGE)
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState('')
  const [sent, setSent] = useState(false)

  if (!STORE)
    return (
      <main className="rec">
        <p className="rec__error">{t.noStore}</p>
      </main>
    )

  const send = async () => {
    if (!recorder.audio || sending) return
    setSending(true)
    setSendError('')
    try {
      await sendNote(recorder.audio, STORE, recorder.transcript, LANGUAGE)
      setSent(true)
    } catch (error) {
      setSendError(fmt(t.errors.send, { status: status(error) }))
    } finally {
      setSending(false)
    }
  }

  const again = () => {
    recorder.reset()
    setSent(false)
    setSendError('')
  }

  const { state } = recorder
  return (
    <main className="rec">
      <header className="rec__header">
        <p className="rec__eyebrow">{t.eyebrow}</p>
        <h1 className="rec__store">{fmt(t.storeLabel, { store: STORE })}</h1>
      </header>

      {!sent && (
        <section className="rec__card">
          {(state === 'idle' || state === 'requesting' || state === 'recording') && (
            <button
              type="button"
              disabled={state === 'requesting' || !voiceToken()}
              className={`rec__mic${state === 'recording' ? ' rec__mic--on' : ''}`}
              onClick={state === 'recording' ? recorder.stop : recorder.start}
            >
              {state === 'recording' ? <Square size={36} /> : <Mic size={40} />}
              <span>{state === 'recording' ? t.stop : t.start}</span>
            </button>
          )}
          {!voiceToken() && <p role="alert" className="rec__error">{t.errors.access}</p>}
          {state === 'requesting' && <p role="status" className="rec__status">{t.requesting}</p>}
          {state === 'recording' && (
            <p className="rec__status" aria-live="polite">
              {fmt(t.recording, { seconds: recorder.seconds })} · {t.listening}
            </p>
          )}
          {state === 'finalizing' && <p role="status" className="rec__status">{t.finalizing}</p>}
          {recorder.error && <p role="alert" className="rec__error">{errorText(recorder.error)}</p>}

          {(state === 'recording' || state === 'finalizing') && (
            <p className="rec__live" aria-live="polite">
              {recorder.transcript || <span className="rec__muted">{t.liveEmpty}</span>}
            </p>
          )}

          {state === 'done' && (
            <div className="rec__review">
              <h2 id="rec-review-title">{t.reviewTitle}</h2>
              <p className="rec__muted">{t.reviewHint}</p>
              <textarea
                className="rec__text"
                aria-labelledby="rec-review-title"
                maxLength={5000}
                disabled={sending}
                value={recorder.transcript}
                onChange={(event) => recorder.setTranscript(event.target.value)}
                rows={7}
              />
              {sendError && <p role="alert" className="rec__error">{sendError}</p>}
              {recorder.error && <Button onClick={recorder.retry}>{t.retryAsr}</Button>}
              <div className="rec__actions">
                <Button variant="ghost" onClick={again} disabled={sending}>
                  {t.redo}
                </Button>
                <Button
                  variant="primary"
                  onClick={send}
                  loading={sending}
                  disabled={!recorder.transcript.trim() || !recorder.audio}
                >
                  {t.send}
                </Button>
              </div>
            </div>
          )}
        </section>
      )}

      {sent && (
        <section className="rec__card">
          <p role="status" className="rec__ok">✓ {t.sent}</p>
          <p className="rec__muted">{t.sentHint}</p>
          <Button onClick={again}>{t.another}</Button>
        </section>
      )}
    </main>
  )
}
