import { useCallback, useEffect, useRef, useState } from 'react'
import { Mic } from 'lucide-react'
import type { RunView } from '../api/client'
import { fmt, messages } from '../i18n'
import { Button } from '../ui'
import { listNotes, processNotes, readCases, readRun, voiceToken } from './voiceApi'
import './voiceProcessButton.css'

const t = messages.record.dashboard
const REFRESH_MS = 5000
const POLL_MS = 2000
const POLL_LIMIT = 90
const DONE = new Set(['succeeded', 'degraded', 'blocked', 'failed'])
const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms))

/** Dashboard trigger for DEMO-04: one live-voice run over the notes sent from /store/record. */
export function VoiceProcessButton({
  onDone
}: {
  onDone: (run: RunView, cases: number) => void
}) {
  const mounted = useRef(true)
  const busy = useRef(false)
  const [pending, setPending] = useState(0)
  const [state, setState] = useState<'idle' | 'running' | 'error'>('idle')

  const refresh = useCallback(async () => {
    try {
      if (!voiceToken()) return
      const count = (await listNotes()).filter((note) => !note.run_id).length
      if (mounted.current) setPending(count)
    } catch {
      if (mounted.current) setPending(0)
    }
  }, [])

  useEffect(() => {
    mounted.current = true
    // The inbox is filled from the phone: poll it so the counter appears without a reload.
    const timer = window.setInterval(() => void refresh(), REFRESH_MS)
    const first = window.setTimeout(() => void refresh(), 0)
    return () => {
      mounted.current = false
      window.clearInterval(timer)
      window.clearTimeout(first)
    }
  }, [refresh])

  const process = async () => {
    if (busy.current) return
    busy.current = true
    setState('running')
    try {
      let last: RunView | null = null
      let allSucceeded = true
      for (const run of await processNotes()) {
        let view = run
        for (let i = 0; i < POLL_LIMIT && !DONE.has(view.status); i++) {
          await sleep(POLL_MS)
          if (!mounted.current) return
          view = await readRun(run.spec.run_id)
        }
        if (['succeeded', 'degraded'].includes(view.status)) last = view
        else allSucceeded = false
      }
      if (!mounted.current) return
      setState(last && allSucceeded ? 'idle' : 'error')
      if (last) onDone(last, (await readCases(last.spec.run_id)).length)
    } catch {
      if (mounted.current) setState('error')
    } finally {
      busy.current = false
    }
    await refresh()
  }

  if (!pending && state === 'idle') return null
  return (
    <Button
      size="sm"
      className="voice-process"
      icon={<Mic size={14} />}
      loading={state === 'running'}
      disabled={!pending}
      onClick={process}
    >
      {state === 'running'
        ? t.running
        : state === 'error'
          ? t.failed
          : fmt(t.process, { count: pending })}
    </Button>
  )
}
