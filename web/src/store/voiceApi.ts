import type { components } from '../api/schema'
import type { RunView } from '../api/client'

export type LiveNote = components['schemas']['LiveNoteView']
export type Transcription = components['schemas']['Transcription']

export class ApiError extends Error {
  readonly status: number
  constructor(status: number) {
    super(`HTTP ${status}`)
    this.status = status
  }
}

// Capability goes in the URL fragment (not the HTTP URL, referrer or provider keys).
export const voiceToken = () => new URLSearchParams(window.location.hash.slice(1)).get('voice-token') ?? ''
const headers = () => ({ Authorization: `Bearer ${voiceToken()}` })

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) throw new ApiError(response.status)
  return response.json() as Promise<T>
}

// The file name only carries the container; the backend probes the bytes with ffmpeg anyway.
const fileName = (blob: Blob) => (blob.type.includes('mp4') ? 'note.mp4' : 'note.webm')

export async function transcribe(blob: Blob, language: string, signal?: AbortSignal) {
  const form = new FormData()
  form.append('audio', blob, fileName(blob))
  form.append('language', language)
  return json<Transcription>(
    await fetch('/api/voice/transcribe', { method: 'POST', headers: headers(), body: form, signal })
  )
}

export async function sendNote(blob: Blob, store: string, transcript: string, language: string) {
  const form = new FormData()
  form.append('audio', blob, fileName(blob))
  form.append('store_id', store)
  form.append('transcript', transcript)
  form.append('language', language)
  return json<LiveNote>(await fetch('/api/voice/notes', { method: 'POST', headers: headers(), body: form }))
}

export async function listNotes(store?: string) {
  const query = store ? `?store=${encodeURIComponent(store)}` : ''
  return json<LiveNote[]>(await fetch(`/api/voice/notes${query}`, { headers: headers() }))
}

export async function processNotes(store?: string) {
  return json<RunView[]>(
    await fetch('/api/voice/process', {
      method: 'POST',
      headers: { ...headers(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ store_id: store ?? null })
    })
  )
}

export async function readRun(runId: string) {
  return json<RunView>(await fetch(`/api/runs/${encodeURIComponent(runId)}`))
}
