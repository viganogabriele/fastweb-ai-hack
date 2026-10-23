import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import ts from 'typescript'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import * as api from '../src/api/caseClarifications.ts'

const item = { id: 'case/a', version: 'v2', run_id: 'run/a', scenario_id: 'dev' }
const selection = { item, runId: item.run_id, fixtureMode: false }
const record = { id: 'q/a', version: 'v10', run_id: item.run_id, scenario_id: 'dev', case_id: item.id,
  input_refs: [{ kind: 'Case', id: item.id, version: item.version }], observation_refs: [{ kind: 'Observation', id: 'missing/a', version: 'v1' }],
  question: '<script>alert("model")</script>\nQuestion?', status: 'draft', simulated: true, asked_at: '2026-10-22T23:30:00+02:00', answered_at: null, answer_document_id: null }
const tick = () => new Promise(resolve => setImmediate(resolve))

// Compile the real presentation component for server rendering, keeping React
// hooks and plain-text escaping while substituting only the shared UI wrappers.
const require = createRequire(import.meta.url)
const source = readFileSync(new URL('../src/sections/CaseClarificationsPanel.tsx', import.meta.url), 'utf8')
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } }).outputText
const module = { exports: {} }
new Function('require', 'exports', compiled)(name => {
  if (name.endsWith('.css')) return {}
  if (name === '../api/caseClarifications') return api
  if (name === '../api/client') return { readApi: () => assert.fail('render must not fetch') }
  if (name === '../ui') return { Button: ({ children }) => React.createElement('button', null, children), StatusBadge: ({ label }) => React.createElement('span', null, label) }
  return require(name)
}, module.exports)
const { ClarificationRecord, CaseClarificationsPanel } = module.exports

test('paths encode IDs and pin selected versions; namespace and selection keys isolate all contexts', () => {
  assert.equal(api.clarificationsPath(selection), '/runs/run%2Fa/cases/case%2Fa/clarifications?fixture=false')
  assert.equal(api.clarificationsPath({ ...selection, fixtureMode: true }, record), '/runs/run%2Fa/cases/case%2Fa/clarifications/q%2Fa?fixture=true&version=v10')
  assert.equal(api.answerDocumentPath(selection, 'https://untrusted/a'), '/runs/run%2Fa/documents/https%3A%2F%2Funtrusted%2Fa?fixture=false')
  for (const next of [{ ...selection, runId: 'other' }, { ...selection, fixtureMode: true }, { ...selection, item: { ...item, id: 'other' } }, { ...selection, item: { ...item, version: 'v3' } }]) {
    assert.notEqual(api.clarificationSelectionKey(next), api.clarificationSelectionKey(selection))
    assert.notEqual(CaseClarificationsPanel(next).key, CaseClarificationsPanel(selection).key)
  }
})

test('list trusts API version selection and never substitutes mismatched case versions, run or scenario', async () => {
  const states = []
  api.requestClarifications(selection, async () => [record], state => states.push(state))
  await tick()
  assert.deepEqual(states.at(-1), { status: 'ready', data: [record] })
  for (const change of [{ run_id: 'other' }, { case_id: 'other' }, { scenario_id: 'other' }, { input_refs: [] }, { input_refs: [{ kind: 'Case', id: item.id, version: 'v1' }] }]) {
    assert.equal(api.clarificationMatches({ ...record, ...change }, selection), false)
  }
  const mismatched = []
  api.requestClarifications(selection, async () => [{ ...record, input_refs: [] }], state => mismatched.push(state))
  await tick()
  assert.equal(mismatched.at(-1).status, 'unavailable')
})

test('exact detail never silently substitutes latest; list and detail requests stay independent', async () => {
  for (const change of [{ version: 'v11' }, { id: 'other' }, { case_id: 'other' }, { run_id: 'other' }]) {
    const states = []
    api.requestClarification(selection, record, async () => ({ ...record, ...change }), state => states.push(state))
    await tick()
    assert.equal(states.at(-1).status, 'unavailable')
  }
  const list = [], detail = []
  api.requestClarifications(selection, async () => [record], state => list.push(state))
  api.requestClarification(selection, record, async () => { throw Error('HTTP 404') }, state => detail.push(state))
  await tick()
  assert.equal(list.at(-1).status, 'ready')
  assert.equal(detail.at(-1).status, 'error')
})

test('independent loading, empty, unavailable and API errors never activate synthetic records', async () => {
  for (const [reader, expected] of [[async () => [], 'empty'], [async () => { throw Error('HTTP 503') }, 'error']]) {
    const states = []
    api.requestClarifications(selection, reader, state => states.push(state))
    await tick()
    assert.equal(states[0].status, 'loading')
    assert.equal(states.at(-1).status, expected)
    assert.equal(states.at(-1).data, undefined)
  }
  const states = []
  api.requestClarifications({ ...selection, runId: 'other' }, () => assert.fail('invalid run must not fetch'), state => states.push(state))
  assert.equal(states.at(-1).status, 'unavailable')
})

test('list and detail ignore late successes and failures after cleanup on selection or retry', async () => {
  for (const detail of [false, true]) for (const fail of [false, true]) {
    let finish, signal
    const states = []
    const reader = (_path, received) => {
      signal = received
      return new Promise((resolve, reject) => { finish = () => fail ? reject(Error('late')) : resolve(detail ? record : [record]) })
    }
    const stop = detail ? api.requestClarification(selection, record, reader, state => states.push(state))
      : api.requestClarifications(selection, reader, state => states.push(state))
    stop()
    finish()
    await tick()
    assert.equal(signal.aborted, true)
    assert.deepEqual(states, [{ status: 'loading' }])
  }
})

test('real record rendering preserves stored status, UTC instants, simulated flag and unresolved exact refs as escaped text', () => {
  for (const status of ['draft', 'asked', 'answered', 'cancelled']) {
    const html = renderToStaticMarkup(React.createElement(ClarificationRecord, { selection, record: { ...record, status, answered_at: '2026-10-23T01:00:00Z', answer_document_id: 'answer/a' } }))
    assert.ok(html.includes(api.clarificationStatus[status]))
    assert.ok(html.includes('Simulato: sì'))
    assert.ok(html.includes('2026-10-22T21:30:00.000Z · UTC'))
    assert.ok(html.includes('2026-10-23T01:00:00.000Z · UTC'))
    assert.ok(html.includes('answer/a'))
    assert.ok(html.includes('Observation · missing/a · v1'))
    assert.ok(html.includes('Riferimento non risolto'))
    assert.ok(html.includes('&lt;script&gt;'))
    assert.ok(!html.includes('<script>'))
    assert.ok(!html.includes('<form'))
    assert.ok(!html.includes('href='))
  }
  assert.equal(api.clarificationTimestamp(null), 'Non disponibile')
  assert.equal(api.clarificationTimestamp('invalid'), 'invalid · fuso non verificabile')
  assert.ok(api.answerDocumentMatches({ document: { ...item, id: 'answer/a' } }, 'answer/a'))
  for (const change of [{ id: 'other' }]) {
    assert.equal(api.answerDocumentMatches({ document: { ...item, id: 'answer/a', ...change } }, 'answer/a'), false)
  }
})
