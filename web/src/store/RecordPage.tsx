import { useEffect, useState } from 'react'
import { Check, Mic, Square, Trash2 } from 'lucide-react'
import { fmt, messages } from '../i18n'
import { Button } from '../ui'
import { useRecorder } from './useRecorder'
import type { RecorderError } from './useRecorder'
import { ApiError, sendNote, voiceToken } from './voiceApi'
import type { LiveNote } from './voiceApi'
import { canUseMicrophone, currentQuestion, isValidStaffCode, normalizeStaffCode, remainingTime } from './guidedRecording'
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
  const [sent, setSent] = useState<{ note: LiveNote; staff: string } | null>(null)
  const [staff, setStaff] = useState(() => {
    // An explicit URL code takes precedence, even if invalid; never silently use another identity.
    const fromUrl = params.get('staff')
    try { return normalizeStaffCode(fromUrl ?? localStorage.getItem('tessera-staff-ref') ?? '') }
    catch { return normalizeStaffCode(fromUrl ?? '') }
  })
  useEffect(() => {
    try {
      if (isValidStaffCode(staff)) localStorage.setItem('tessera-staff-ref', staff)
      else localStorage.removeItem('tessera-staff-ref')
    } catch { /* Recording still works when browser storage is unavailable. */ }
  }, [staff])

  if (!STORE)
    return (
      <main className="rec">
        <p className="rec__error">{t.noStore}</p>
      </main>
    )

  const send = async () => {
    if (!recorder.audio || sending || !isValidStaffCode(staff)) return
    setSending(true)
    setSendError('')
    try {
      const note = await sendNote(recorder.audio, STORE, recorder.transcript, LANGUAGE, staff)
      setSent({ note, staff })
    } catch (error) {
      const detail = error instanceof ApiError && error.detail ? ` ${error.detail}` : ''
      setSendError(fmt(t.errors.send, { status: status(error) }) + detail)
    } finally {
      setSending(false)
    }
  }

  const again = () => {
    recorder.reset()
    setSent(null)
    setSendError('')
  }

  const { state } = recorder
  return (
    <main className="rec">
      <header className="rec__header">
        <p className="rec__eyebrow">{t.eyebrow}</p>
        <h1 className="rec__store">{fmt(t.storeLabel, { store: STORE })}</h1>
      </header>

      {!sent && <>
        <p className="rec__muted">{t.liveHint}</p>
        <div className="rec__staff">
          <label htmlFor="rec-staff">{t.staffLabel}</label>
          <input id="rec-staff" className="rec__input" value={staff}
            onChange={(event) => setStaff(normalizeStaffCode(event.target.value))}
            disabled={state !== 'idle'} autoCapitalize="none" autoCorrect="off" spellCheck={false}
            autoComplete="off" maxLength={64} aria-describedby="rec-staff-hint rec-staff-required"
            aria-invalid={!isValidStaffCode(staff)} />
          <p id="rec-staff-hint" className="rec__muted">{t.staffHint}</p>
          <p id="rec-staff-required" className="rec__error">
            {!isValidStaffCode(staff) ? t.staffRequired : ''}
          </p>
        </div>
        <section className={`rec__guide${state === 'recording' ? ' rec__guide--compact' : ''}`} aria-label={t.guideTitle}>
          {state === 'recording' ? (
            <ol>{t.keywords.map((word, index) => <li key={word}
              aria-current={currentQuestion(recorder.seconds) === index ? 'step' : undefined}>
              <span aria-hidden="true">{index + 1}</span> {word}
            </li>)}</ol>
          ) : <><h2>{t.guideTitle}</h2><ol>{t.questions.map((question) => <li key={question}>{question}</li>)}</ol>
            <p className="rec__muted">{t.guideHint}</p></>}
        </section>
        <section
          className={`rec__card rec__card--fill${state === 'idle' || state === 'requesting' ? ' rec__card--center' : ''}`}
        >
          {(state === 'idle' || state === 'requesting' || state === 'recording') && (
            <div className="rec__controls">
              {/* Side slots have the same width, so the microphone stays centred. */}
              <span className="rec__side" aria-hidden="true" />
              <button
                type="button"
                disabled={state !== 'recording' && !canUseMicrophone(staff, Boolean(voiceToken()), state === 'requesting')}
                aria-describedby="rec-staff-required rec-access rec-limit"
                className={`rec__mic${state === 'recording' ? ' rec__mic--on' : ''}`}
                aria-label={state === 'recording' ? t.stop : t.start}
                onClick={state === 'recording' ? recorder.stop : recorder.start}
              >
                {state === 'recording' ? <Square size={52} /> : <Mic size={72} />}
              </button>
              {state === 'recording' ? (
                <button
                  type="button"
                  className="rec__side rec__discard"
                  aria-label={t.discard}
                  title={t.discard}
                  onClick={again}
                >
                  <Trash2 size={22} />
                </button>
              ) : (
                <span className="rec__side" aria-hidden="true" />
              )}
            </div>
          )}
          <p id="rec-limit" className="rec__status">{t.limit}</p>
          {state === 'recording' && <p role="timer" className="rec__seconds">
            {fmt(t.remaining, { time: remainingTime(recorder.seconds) })}
          </p>}
          <p id="rec-access" className="rec__error">{!voiceToken() ? t.errors.access : ''}</p>
          {state === 'requesting' && <p role="status" className="rec__status">{t.requesting}</p>}
          {state === 'finalizing' && <p role="status" className="rec__status">{t.finalizing}</p>}
          {recorder.error && <p role="alert" className="rec__error">{errorText(recorder.error)}</p>}

          {(state === 'recording' || state === 'finalizing') && (
            <div><p className="rec__muted">{t.provisional}</p>
              <p className="rec__live" aria-live="polite">{recorder.transcript}</p>
            </div>
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
                  disabled={!recorder.transcript.trim() || !recorder.audio || !isValidStaffCode(staff)}
                >
                  {t.send}
                </Button>
              </div>
            </div>
          )}
        </section>
      </>}

      {sent && (
        <section className="rec__sent">
          <div className="rec__sent-badge" role="status" aria-label={t.sent}>
            <Check size={64} strokeWidth={3} aria-hidden="true" />
          </div>
          <h2>{t.sent}</h2>
          <p className="rec__sent-text">{t.sentHint}</p>
          <dl className="rec__receipt">
            <div><dt>{t.storeLabel.replace(' {store}', '')}</dt><dd>{sent.note.store_id}</dd></div>
            <div><dt>{t.staffLabel}</dt><dd>{sent.staff}</dd></div>
            <div><dt>{t.sentAt}</dt><dd><time dateTime={sent.note.sent_at}>
              {new Intl.DateTimeFormat('it-IT', { year: 'numeric', month: '2-digit', day: '2-digit',
                hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' }).format(new Date(sent.note.sent_at))}
            </time></dd></div>
            <div><dt>{t.noteLabel}</dt><dd>{sent.note.note_id}</dd></div>
          </dl>
          <Button variant="primary" onClick={again}>
            {t.another}
          </Button>
        </section>
      )}
    </main>
  )
}
