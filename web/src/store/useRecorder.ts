import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, transcribe } from './voiceApi'

// Opus in WebM on Chrome/Android/Firefox, AAC in MP4 on iOS Safari.
const MIME_TYPES = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus']
const SLICE_MS = 1000
// The whole recording so far is re-transcribed at this pace: the team ASR allows 20 calls/min.
const PARTIAL_MS = 4000
const MAX_SECONDS = 90

export type RecorderError = 'insecure' | 'microphone' | 'unsupported' | { asr: number }
export type RecorderState = 'idle' | 'recording' | 'finalizing' | 'done'

/** Records the microphone and keeps a live transcript of everything said so far. */
export function useRecorder(language: string) {
  const [state, setState] = useState<RecorderState>('idle')
  const [seconds, setSeconds] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [audio, setAudio] = useState<Blob | null>(null)
  const [error, setError] = useState<RecorderError | null>(null)
  const recorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])
  const timers = useRef<number[]>([])
  const inFlight = useRef(false)
  // A partial answer that arrives after the final one must not overwrite it.
  const generation = useRef(0)

  const clearTimers = () => {
    timers.current.forEach((id) => window.clearInterval(id))
    timers.current = []
  }

  const stop = useCallback(() => {
    if (recorder.current?.state === 'recording') recorder.current.stop()
  }, [])

  useEffect(
    () => () => {
      clearTimers()
      recorder.current?.stream.getTracks().forEach((track) => track.stop())
    },
    []
  )

  const start = useCallback(async () => {
    setError(null)
    if (!window.isSecureContext) return setError('insecure')
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined')
      return setError('unsupported')
    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      return setError('microphone')
    }
    const mimeType = MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type))
    const media = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
    const current = ++generation.current
    const blob = () => new Blob(chunks.current, { type: media.mimeType || mimeType || '' })
    chunks.current = []
    recorder.current = media
    media.ondataavailable = (event) => {
      if (event.data.size) chunks.current.push(event.data)
    }
    media.onstop = async () => {
      clearTimers()
      stream.getTracks().forEach((track) => track.stop())
      const full = blob()
      setAudio(full)
      setState('finalizing')
      const final = ++generation.current
      try {
        const { text } = await transcribe(full, language)
        if (generation.current === final) setTranscript(text)
      } catch (failure) {
        if (generation.current === final)
          setError({ asr: failure instanceof ApiError ? failure.status : 0 })
      }
      if (generation.current === final) setState('done')
    }
    media.start(SLICE_MS)
    setTranscript('')
    setAudio(null)
    setSeconds(0)
    setState('recording')
    const startedAt = Date.now()
    timers.current.push(
      window.setInterval(() => {
        const elapsed = Math.floor((Date.now() - startedAt) / 1000)
        setSeconds(elapsed)
        if (elapsed >= MAX_SECONDS) stop()
      }, 250),
      window.setInterval(async () => {
        if (inFlight.current || !chunks.current.length) return
        inFlight.current = true
        try {
          const { text } = await transcribe(blob(), language)
          if (generation.current === current) setTranscript(text)
        } catch {
          // A missed partial is harmless: the final transcription covers the whole note.
        } finally {
          inFlight.current = false
        }
      }, PARTIAL_MS)
    )
  }, [language, stop])

  const reset = useCallback(() => {
    generation.current++
    setState('idle')
    setTranscript('')
    setAudio(null)
    setSeconds(0)
    setError(null)
  }, [])

  return { state, seconds, transcript, setTranscript, audio, error, start, stop, reset }
}
