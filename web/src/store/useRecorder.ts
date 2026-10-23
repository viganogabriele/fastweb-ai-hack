import { useCallback, useEffect, useRef, useState } from 'react'
import { transcribe } from './voiceApi'
import { RecorderSession } from './recorderSession'
import type { RecorderError, RecorderState } from './recorderSession'
export type { RecorderError } from './recorderSession'

export function useRecorder(language: string) {
  const [state, setState] = useState<RecorderState>('idle')
  const [seconds, setSeconds] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [audio, setAudio] = useState<Blob | null>(null)
  const [error, setError] = useState<RecorderError | null>(null)
  const session = useRef<RecorderSession | null>(null)
  useEffect(() => () => session.current?.dispose(), [])

  const start = useCallback(() => {
    if (session.current?.isActive) return
    session.current?.dispose()
    const capture = new RecorderSession(language, transcribe, (update) => {
      if (update.state !== undefined) setState(update.state)
      if (update.seconds !== undefined) setSeconds(update.seconds)
      if (update.transcript !== undefined) setTranscript(update.transcript)
      if (update.audio !== undefined) setAudio(update.audio)
      if (update.error !== undefined) setError(update.error)
    })
    session.current = capture
    void capture.start()
  }, [language])
  const stop = useCallback(() => session.current?.stop(), [])
  const retry = useCallback(() => void session.current?.finalize(), [])
  const reset = useCallback(() => {
    session.current?.dispose()
    session.current = null
    setState('idle'); setTranscript(''); setAudio(null); setSeconds(0); setError(null)
  }, [])
  return { state, seconds, transcript, setTranscript, audio, error, start, stop, retry, reset }
}
