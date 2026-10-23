/** One capture lifetime. All browser and ASR resources are released together. */
export type RecorderError = 'insecure' | 'microphone' | 'unsupported' | { asr: number }
export type RecorderState = 'idle' | 'requesting' | 'recording' | 'finalizing' | 'done'
type Update = { state?: RecorderState; seconds?: number; transcript?: string; audio?: Blob | null; error?: RecorderError | null }
type Transcribe = (blob: Blob, language: string, signal: AbortSignal) => Promise<{ text: string }>
const TYPES = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus']

export class RecorderSession {
  private active = false
  private media: MediaRecorder | null = null
  private stream: MediaStream | null = null
  private timers: ReturnType<typeof setInterval>[] = []
  private abort = new AbortController()
  private partial: Promise<void> | null = null
  private chunks: Blob[] = []
  private full: Blob | null = null
  private finishing = false
  private language: string
  private transcribe: Transcribe
  private update: (value: Update) => void
  constructor(language: string, transcribe: Transcribe, update: (value: Update) => void) {
    this.language = language; this.transcribe = transcribe; this.update = update
  }
  get isActive() { return this.active }

  private clearTimers() {
    this.timers.forEach(clearInterval)
    this.timers = []
  }
  private blob() { return new Blob(this.chunks, { type: this.media?.mimeType || '' }) }
  private emit(value: Update) { if (this.active) this.update(value) }

  async start() {
    if (this.active) return
    if (!window.isSecureContext) return this.update({ error: 'insecure' })
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined')
      return this.update({ error: 'unsupported' })
    this.active = true
    this.emit({ state: 'requesting', error: null })
    let stream: MediaStream
    try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }) }
    catch { this.emit({ state: 'idle', error: 'microphone' }); this.active = false; return }
    if (!this.active) { stream.getTracks().forEach((track) => track.stop()); return }
    this.stream = stream
    try {
      const mimeType = TYPES.find((type) => MediaRecorder.isTypeSupported(type))
      const media = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      this.media = media
      media.ondataavailable = (event) => { if (this.active && event.data.size) this.chunks.push(event.data) }
      media.onerror = () => {
        this.emit({ state: 'idle', error: 'microphone' })
        this.dispose()
      }
      media.onstop = () => {
        this.clearTimers()
        stream.getTracks().forEach((track) => track.stop())
        if (!this.active) return
        // MediaRecorder delivers its last dataavailable before stop.
        this.full = this.blob()
        this.finishing = true
        this.emit({ state: 'finalizing', audio: this.full })
        void this.finalize()
      }
      media.start(1000)
      this.emit({ state: 'recording', transcript: '', audio: null, seconds: 0 })
      const started = Date.now()
      this.timers.push(setInterval(() => {
        const seconds = Math.floor((Date.now() - started) / 1000)
        this.emit({ seconds })
        if (seconds >= 90) this.stop()
      }, 250), setInterval(() => {
        if (this.partial || this.finishing || !this.chunks.length) return
        this.partial = this.transcribe(this.blob(), this.language, this.abort.signal).then(({ text }) => {
          if (!this.finishing) this.emit({ transcript: text })
        }).catch(() => { /* The final transcript covers a missed partial. */ }).finally(() => { this.partial = null })
      }, 4000))
    } catch {
      this.emit({ state: 'idle', error: 'unsupported' })
      this.dispose()
    }
  }

  stop() {
    if (this.media?.state !== 'recording') return
    this.finishing = true
    this.clearTimers()
    this.emit({ state: 'finalizing' })
    this.media.stop()
  }

  async finalize() {
    if (!this.active || !this.full) return
    this.emit({ state: 'finalizing', error: null })
    // Never overlap a final ASR call with a partial call, even on a slow connection.
    await this.partial
    if (!this.active) return
    try {
      const { text } = await this.transcribe(this.full, this.language, this.abort.signal)
      this.emit({ transcript: text })
    } catch (error) {
      this.emit({ error: { asr: typeof error === 'object' && error && 'status' in error ? Number(error.status) : 0 } })
    }
    this.emit({ state: 'done' })
  }

  dispose() {
    this.active = false
    this.abort.abort()
    this.clearTimers()
    if (this.media) {
      this.media.onstop = this.media.ondataavailable = this.media.onerror = null
      if (this.media.state !== 'inactive') this.media.stop()
    }
    this.stream?.getTracks().forEach((track) => track.stop())
  }
}
