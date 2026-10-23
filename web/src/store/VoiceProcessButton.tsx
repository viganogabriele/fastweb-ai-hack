import { useCallback, useEffect, useState } from 'react'
import { Mic } from 'lucide-react'
import type { RunView } from '../api/client'
import { fmt, messages } from '../i18n'
import { Button } from '../ui'
import { listNotes, processNotes, readCases, readRun } from './voiceApi'
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
  const [pending, setPending] = useState(0)
  const [state, setState] = useState<'idle' | 'running' | 'error'>('idle')

  const refresh = useCallback(async () => {
    try {
      setPending((await listNotes()).filter((note) => !note.run_id).length)
    } catch {
      setPending(0)
    }
  }, [])

  useEffect(() => {
    // The inbox is filled from the phone: poll it so the counter appears without a reload.
    const timer = window.setInterval(() => void refresh(), REFRESH_MS)
    const first = window.setTimeout(() => void refresh(), 0)
    return () => {
      window.clearInterval(timer)
      window.clearTimeout(first)
    }
  }, [refresh])

  const process = async () => {
    setState('running')
    try {
      let last: RunView | null = null
      for (const run of await processNotes()) {
        let view = run
        for (let i = 0; i < POLL_LIMIT && !DONE.has(view.status); i++) {
          await sleep(POLL_MS)
          view = await readRun(run.spec.run_id)
        }
        last = view
      }
      const ok = last !== null && ['succeeded', 'degraded'].includes(last.status)
      setState(ok ? 'idle' : 'error')
      if (last) onDone(last, ok ? (await readCases(last.spec.run_id)).length : 0)
    } catch {
      setState('error')
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
