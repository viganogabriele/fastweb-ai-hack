import { useCallback, useEffect, useState } from 'react'
import { Mic, Square } from 'lucide-react'
import type { Case } from '../api/client'
import { fmt, messages } from '../i18n'
import { Button } from '../ui'
import { useRecorder } from './useRecorder'
import type { RecorderError } from './useRecorder'
import { ApiError, listNotes, processNotes, readCases, readRun, sendNote } from './voiceApi'
import './recordPage.css'

const t = messages.record
const POLL_MS = 2000
const POLL_LIMIT = 90
const DONE = new Set(['succeeded', 'degraded', 'blocked', 'failed'])

const params = new URLSearchParams(window.location.search)
const STORE = (params.get('store') ?? '').trim().toUpperCase()
const LANGUAGE = (params.get('lang') ?? 'it').trim().toLowerCase()

const status = (error: unknown) => (error instanceof ApiError ? error.status : 0)
const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms))

function errorText(error: RecorderError) {
  return typeof error === 'string' ? t.errors[error] : fmt(t.errors.asr, { status: error.asr })
}

const casePath = (item: Case) =>
  `/#/casi/${encodeURIComponent(item.id)}/${encodeURIComponent(item.version)}`

type Processing =
  | { state: 'idle' }
  | { state: 'running' }
  | { state: 'done'; cases: Case[]; failed: string | null }
  | { state: 'error'; message: string }

export function RecordPage() {
  const recorder = useRecorder(LANGUAGE)
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState('')
  const [sent, setSent] = useState(false)
  const [pending, setPending] = useState(0)
  const [processing, setProcessing] = useState<Processing>({ state: 'idle' })

  const refresh = useCallback(async () => {
    if (!STORE) return
    try {
      setPending((await listNotes(STORE)).filter((note) => !note.run_id).length)
    } catch {
      // The counter is a hint; the process button reports real errors.
    }
  }, [])

  useEffect(() => {
    // Initial read of the server's inbox: an external system, updated again after each action.
    const timer = window.setTimeout(() => void refresh(), 0)
    return () => window.clearTimeout(timer)
  }, [refresh])

  if (!STORE)
    return (
      <main className="rec">
        <p className="rec__error">{t.noStore}</p>
      </main>
    )

  const send = async () => {
    if (!recorder.audio) return
    setSending(true)
    setSendError('')
    try {
      await sendNote(recorder.audio, STORE, recorder.transcript, LANGUAGE)
      setSent(true)
      setProcessing({ state: 'idle' })
      await refresh()
    } catch (error) {
      setSendError(fmt(t.errors.send, { status: status(error) }))
    } finally {
      setSending(false)
    }
  }

  const process = async () => {
    setProcessing({ state: 'running' })
    try {
      const runs = await processNotes(STORE)
      const cases: Case[] = []
      let failed: string | null = null
      for (const run of runs) {
        let view = run
        for (let i = 0; i < POLL_LIMIT && !DONE.has(view.status); i++) {
          await sleep(POLL_MS)
          view = await readRun(run.spec.run_id)
        }
        if (view.status === 'blocked' || view.status === 'failed' || !DONE.has(view.status))
          failed = view.status
        else cases.push(...(await readCases(run.spec.run_id)))
      }
      setProcessing({ state: 'done', cases, failed })
    } catch (error) {
      setProcessing({ state: 'error', message: fmt(t.errors.process, { status: status(error) }) })
    }
    await refresh()
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
          {(state === 'idle' || state === 'recording') && (
            <button
              type="button"
              className={`rec__mic${state === 'recording' ? ' rec__mic--on' : ''}`}
              onClick={state === 'recording' ? recorder.stop : recorder.start}
            >
              {state === 'recording' ? <Square size={36} /> : <Mic size={40} />}
              <span>{state === 'recording' ? t.stop : t.start}</span>
            </button>
          )}
          {state === 'recording' && (
            <p className="rec__status" aria-live="polite">
              {fmt(t.recording, { seconds: recorder.seconds })} · {t.listening}
            </p>
          )}
          {state === 'finalizing' && <p className="rec__status">{t.finalizing}</p>}
          {recorder.error && <p className="rec__error">{errorText(recorder.error)}</p>}

          {(state === 'recording' || state === 'finalizing') && (
            <p className="rec__live" aria-live="polite">
              {recorder.transcript || <span className="rec__muted">{t.liveEmpty}</span>}
            </p>
          )}

          {state === 'done' && (
            <div className="rec__review">
              <h2>{t.reviewTitle}</h2>
              <p className="rec__muted">{t.reviewHint}</p>
              <textarea
                className="rec__text"
                value={recorder.transcript}
                onChange={(event) => recorder.setTranscript(event.target.value)}
                rows={7}
              />
              {sendError && <p className="rec__error">{sendError}</p>}
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
          <p className="rec__ok">✓ {t.sent}</p>
          <Button onClick={again}>{t.another}</Button>
        </section>
      )}

      <section className="rec__card rec__process">
        <p className="rec__muted">{fmt(t.pending, { count: pending })}</p>
        <Button
          variant="secondary"
          onClick={process}
          loading={processing.state === 'running'}
          disabled={pending === 0}
        >
          {processing.state === 'running' ? t.processing : t.process}
        </Button>
        {processing.state === 'error' && <p className="rec__error">{processing.message}</p>}
        {processing.state === 'done' && (
          <div className="rec__cases">
            <p className="rec__ok">✓ {t.processed}</p>
            {processing.failed && (
              <p className="rec__error">{fmt(t.errors.run, { status: processing.failed })}</p>
            )}
            {!processing.failed && !processing.cases.length && (
              <p className="rec__muted">{t.noCases}</p>
            )}
            {processing.cases.map((item) => (
              <a key={item.id} className="rec__case" href={casePath(item)}>
                <strong>{t.caseTypes[item.case_type] ?? item.case_type}</strong>
                <span>{item.scope_id ?? t.unknownScope}</span>
                <span className="rec__muted">{item.priority_reason}</span>
              </a>
            ))}
            {processing.cases.length > 0 && (
              <a className="rec__link" href="/#/casi">
                {t.openDashboard}
              </a>
            )}
          </div>
        )}
      </section>
    </main>
  )
}
