import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import vm from 'node:vm'
import assert from 'node:assert/strict'
import { test } from 'node:test'

const require = createRequire(import.meta.url)
const ts = require('typescript'), React = require('react')
const { renderToStaticMarkup } = require('react-dom/server')
const { record } = require('../src/i18n/it/record.ts')
const source = readFileSync(new URL('../src/store/RecordPage.tsx', import.meta.url), 'utf8')
const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } }).outputText

function render({ search = '?store=MIL01', saved = '', state = 'idle', seconds = 0, access = true, storageError = false } = {}) {
  const module = { exports: {} }
  vm.runInNewContext(output, {
    exports: module.exports, URLSearchParams,
    window: { location: { search } },
    localStorage: { getItem: () => { if (storageError) throw Error('storage blocked'); return saved } },
    require: (name) => {
      if (name === './guidedRecording') return require('../src/store/guidedRecording.ts')
      if (name === './useRecorder') return { useRecorder: () => ({ state, seconds, transcript: '', audio: null }) }
      if (name === './voiceApi') return { voiceToken: () => access ? 'fake' : '', ApiError: Error }
      if (name === '../i18n') return { messages: { record }, fmt: (text, args) => text.replace(/\{(\w+)\}/g, (_, key) => args[key]) }
      if (name === '../ui') return { Button: ({ children }) => React.createElement('button', null, children) }
      if (name.endsWith('.css')) return {}
      return require(name)
    }
  })
  return renderToStaticMarkup(React.createElement(module.exports.RecordPage))
}

test('idle page shows all four questions and explains the disabled microphone', () => {
  const html = render()
  for (const question of record.questions) assert.ok(html.includes(question))
  assert.match(html, /disabled=""[^>]*aria-describedby="rec-staff-required rec-access rec-limit"/)
  assert.ok(html.includes(record.staffRequired))
  assert.ok(html.includes(record.staffHint))
})

test('URL staff wins over saved identity; invalid URL never falls back to a different employee', () => {
  assert.match(render({ search: '?store=MIL01&staff=STAFF-09', saved: 'other' }), /value="staff-09"/)
  const invalid = render({ search: '?store=MIL01&staff=bad_code', saved: 'other' })
  assert.match(invalid, /value="bad_code"/)
  assert.ok(invalid.includes(record.staffRequired))
  assert.match(render({ saved: 'saved-09' }), /value="saved-09"/)
  assert.ok(render({ storageError: true }).includes(record.staffRequired))
})

test('recording keeps four compact prompts, a visible countdown and stop control', () => {
  const html = render({ saved: 'staff-09', state: 'recording', seconds: 45 })
  assert.match(html, /aria-current="step"><span aria-hidden="true">4<\/span> Episodi/)
  assert.match(html, /ancora 0:45/)
  assert.match(html, /aria-label="Ferma"/)
  assert.ok(!html.includes(record.questions[0]))
  assert.ok(html.includes(record.provisional))
})
