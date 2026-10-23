import assert from 'node:assert/strict'
import { test } from 'node:test'
import { RecorderSession } from '../src/store/recorderSession.ts'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import vm from 'node:vm'
import { transcribe } from '../src/store/voiceApi.ts'

const flush = async () => { for (let i = 0; i < 12; i++) await Promise.resolve() }
const deferred = () => {
  let resolve, reject
  const promise = new Promise((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}

function browser(t, { permission, types = ['audio/webm;codecs=opus'], constructorError = false } = {}) {
  let stops = 0
  const stream = { getTracks: () => [{ stop: () => { stops++ } }] }
  t.mock.timers.enable({ apis: ['setInterval', 'Date'] })
  const global = (name, value) => {
    const before = Object.getOwnPropertyDescriptor(globalThis, name)
    Object.defineProperty(globalThis, name, { configurable: true, value })
    t.after(() => before ? Object.defineProperty(globalThis, name, before) : delete globalThis[name])
  }
  global('window', { isSecureContext: true })
  global('navigator', { mediaDevices: { getUserMedia: () => permission ?? Promise.resolve(stream) } })
  class MediaRecorder {
    static latest
    static isTypeSupported(type) { return types.includes(type) }
    state = 'inactive'
    constructor(_stream, options) {
      if (constructorError) throw new Error('codec unavailable')
      this.mimeType = options?.mimeType ?? 'audio/mp4'
      MediaRecorder.latest = this
    }
    start() { this.state = 'recording' }
    chunk(text) { this.ondataavailable?.({ data: new Blob([text], { type: this.mimeType }) }) }
    stop() {
      this.state = 'inactive'
      queueMicrotask(() => { this.chunk('final'); this.onstop?.() })
    }
  }
  global('MediaRecorder', MediaRecorder)
  return { stream, get media() { return MediaRecorder.latest }, stops: () => stops }
}

test('late microphone permission after unmount closes tracks without starting capture', async (t) => {
  const permission = deferred()
  const env = browser(t, { permission: permission.promise })
  const updates = []
  const session = new RecorderSession('it', async () => assert.fail('no ASR'), (v) => updates.push(v))
  const start = session.start()
  assert.equal(updates.at(-1).state, 'requesting')
  session.dispose()
  permission.resolve(env.stream)
  await start
  assert.equal(env.stops(), 1)
  assert.equal(env.media, undefined)
  assert.equal(updates.length, 1)
})

test('permission denial remains retryable', async (t) => {
  const permission = deferred()
  browser(t, { permission: permission.promise })
  const updates = []
  const session = new RecorderSession('it', async () => assert.fail('no ASR'), (v) => updates.push(v))
  const start = session.start()
  permission.reject(new Error('denied'))
  await start
  assert.deepEqual(updates.at(-1), { state: 'idle', error: 'microphone' })
  assert.equal(session.isActive, false)
})

test('recorder construction failure closes the acquired stream', async (t) => {
  const env = browser(t, { constructorError: true })
  const updates = []
  const session = new RecorderSession('it', async () => assert.fail('no ASR'), (v) => updates.push(v))
  await session.start()
  assert.deepEqual(updates.at(-1), { state: 'idle', error: 'unsupported' })
  assert.equal(env.stops(), 1)
  assert.equal(session.isActive, false)
})

test('iOS MP4 final blob includes final dataavailable and waits for the partial ASR', async (t) => {
  const env = browser(t, { types: ['audio/mp4'] })
  const partial = deferred()
  const requests = [], updates = []
  const session = new RecorderSession('it', (blob, language, signal) => {
    requests.push({ blob, language, signal })
    return requests.length === 1 ? partial.promise : Promise.resolve({ text: 'final words' })
  }, (v) => updates.push(v))
  await session.start()
  env.media.chunk('first')
  t.mock.timers.tick(4000)
  assert.equal(requests.length, 1)
  session.stop()
  await flush()
  assert.equal(requests.length, 1)
  partial.resolve({ text: 'stale partial' })
  await flush()
  assert.equal(requests.length, 2)
  assert.equal(requests[1].blob.type, 'audio/mp4')
  assert.equal(await requests[1].blob.text(), 'firstfinal')
  assert.equal(updates.some((u) => u.transcript === 'stale partial'), false)
  assert.equal(updates.findLast((u) => u.transcript)?.transcript, 'final words')
  assert.equal(updates.at(-1).state, 'done')
  assert.equal(env.stops(), 1)
  session.dispose()
})

test('slow partials stay serial and disposal aborts ASR without further updates', async (t) => {
  const env = browser(t)
  const partial = deferred()
  const requests = [], updates = []
  const session = new RecorderSession('it', (blob, language, signal) => {
    requests.push({ blob, language, signal })
    return partial.promise
  }, (v) => updates.push(v))
  await session.start()
  env.media.chunk('speech')
  t.mock.timers.tick(12000)
  assert.equal(requests.length, 1)
  session.dispose()
  const count = updates.length
  assert.equal(requests[0].signal.aborted, true)
  partial.resolve({ text: 'too late' })
  await flush()
  assert.equal(updates.length, count)
  assert.equal(env.stops(), 1)
})

test('capture auto-stops below the strict 90-second backend limit', async (t) => {
  const env = browser(t)
  const updates = []
  const session = new RecorderSession('it', async () => ({ text: 'done' }), (v) => updates.push(v))
  await session.start()
  t.mock.timers.tick(90000)
  await flush()
  assert.equal(env.media.state, 'inactive')
  assert.equal(env.stops(), 1)
  assert.equal(updates.at(-1).state, 'done')
  session.dispose()
})

test('a failed final transcript keeps audio for manual text and supports one retry', async (t) => {
  const env = browser(t)
  const requests = [], updates = []
  const retry = deferred()
  const session = new RecorderSession('it', (blob) => {
    requests.push(blob)
    return requests.length === 1 ? Promise.reject({ status: 503 }) : retry.promise
  }, (v) => updates.push(v))
  await session.start()
  session.stop()
  await flush()
  assert.equal(updates.findLast((u) => u.error)?.error.asr, 503)
  assert.ok(updates.find((u) => u.audio)?.audio.size)
  assert.equal(updates.at(-1).state, 'done')
  const first = session.finalize()
  const duplicate = session.finalize()
  await flush()
  assert.equal(requests.length, 2)
  retry.resolve({ text: 'recovered' })
  await Promise.all([first, duplicate])
  assert.equal(updates.findLast((u) => u.transcript)?.transcript, 'recovered')
  assert.equal(env.media.state, 'inactive')
  session.dispose()
})

test('voice uploads preserve the actual Ogg/MP4 container and capability header', async (t) => {
  const env = browser(t)
  const calls = []
  window.location = { hash: '#voice-token=fake-capability' }
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url, options })
    return new Response(JSON.stringify({ text: 'words' }), { headers: { 'Content-Type': 'application/json' } })
  })
  const signal = new AbortController().signal
  for (const [type, name] of [['audio/ogg;codecs=opus', 'note.ogg'], ['audio/mp4', 'note.mp4']]) {
    await transcribe(new Blob(['speech'], { type }), 'it', signal)
    const { url, options } = calls.at(-1)
    assert.equal(url, '/api/voice/transcribe')
    assert.equal(options.headers.Authorization, 'Bearer fake-capability')
    assert.equal(options.body.get('audio').name, name)
    assert.equal(options.signal, signal)
  }
  assert.equal(env.stops(), 0)
})

test('the actual review page renders accepted transcript as controlled, escaped text', () => {
  const require = createRequire(import.meta.url)
  const ts = require('typescript'), React = require('react')
  const { renderToStaticMarkup } = require('react-dom/server')
  const { record } = require('../src/i18n/it/record.ts')
  const transcript = '<script>alert(1)</script><img src=x onerror=alert(2)>'
  const source = readFileSync(new URL('../src/store/RecordPage.tsx', import.meta.url), 'utf8')
  const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } }).outputText
  const module = { exports: {} }
  vm.runInNewContext(output, {
    exports: module.exports,
    window: { location: { search: '?store=MIL01' } },
    URLSearchParams,
    require: (name) => {
      if (name === './useRecorder') return { useRecorder: () => ({ state: 'done', transcript, audio: new Blob(['audio']) }) }
      if (name === './voiceApi') return { voiceToken: () => 'fake', ApiError: Error }
      if (name === '../i18n') return { messages: { record }, fmt: (text) => text }
      if (name === '../ui') return { Button: ({ children }) => React.createElement('button', null, children) }
      if (name.endsWith('.css')) return {}
      return require(name)
    }
  })
  const html = renderToStaticMarkup(React.createElement(module.exports.RecordPage))
  assert.ok(html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'))
  assert.ok(!/<script|<img/.test(html))
  assert.match(html, /<textarea[^>]*aria-labelledby="rec-review-title"[^>]*maxLength="5000"/)
})
