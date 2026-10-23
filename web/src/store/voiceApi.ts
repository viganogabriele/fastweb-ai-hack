import type { components } from '../api/schema'
import type { Case, RunView } from '../api/client'

export type LiveNote = components['schemas']['LiveNoteView']
export type Transcription = components['schemas']['Transcription']

export class ApiError extends Error {
  readonly status: number
  constructor(status: number) {
    super(`HTTP ${status}`)
    this.status = status
  }
}

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
    await fetch('/api/voice/transcribe', { method: 'POST', body: form, signal })
  )
}

export async function sendNote(blob: Blob, store: string, transcript: string, language: string) {
  const form = new FormData()
  form.append('audio', blob, fileName(blob))
  form.append('store_id', store)
  form.append('transcript', transcript)
  form.append('language', language)
  return json<LiveNote>(await fetch('/api/voice/notes', { method: 'POST', body: form }))
}

export async function listNotes(store: string) {
  return json<LiveNote[]>(await fetch(`/api/voice/notes?store=${encodeURIComponent(store)}`))
}

export async function processNotes(store: string) {
  return json<RunView[]>(
    await fetch('/api/voice/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ store_id: store })
    })
  )
}

export async function readRun(runId: string) {
  return json<RunView>(await fetch(`/api/runs/${encodeURIComponent(runId)}`))
}

export async function readCases(runId: string) {
  return json<Case[]>(await fetch(`/api/runs/${encodeURIComponent(runId)}/cases`))
}
