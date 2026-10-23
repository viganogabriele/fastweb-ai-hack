import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import vm from 'node:vm'
import { tracePath, traceMatches, requestCaseTraces, requestCaseTrace } from '../src/api/caseTraces.ts'

const item = { id: 'case/a', version: 'v2', run_id: 'run/a', scenario_id: 'dev' }
const selection = { item, runId: item.run_id, fixtureMode: false }
const ref = { kind: 'Case', id: item.id, version: item.version }
const malicious = '<script>alert(1)</script><img src=x onerror=alert(2)> https://evil.test'
const trace = { id: 'trace/a', version: 'v10', run_id: item.run_id, scenario_id: item.scenario_id, case_id: item.id,
  input_refs: [ref], producer: 'ag.investigator', producer_version: 'v1', computed_at: '2026-10-22', mode: 'fixture',
  outcome: malicious, fallback_used: true, tokens_in: null, tokens_out: 0,
  steps: [{ tool: 'get_stock', arguments: { text: malicious }, input_refs: [ref], output_refs: [{ kind: 'StockFact', id: 'missing', version: 'v3' }], duration_ms: 0, error: malicious }] }
const tick = () => new Promise((resolve) => setImmediate(resolve))

async function run(reader, exact, context = selection) {
  const states = []
  if (exact) requestCaseTrace(context, exact, reader, (state) => states.push(state))
  else requestCaseTraces(context, reader, (state) => states.push(state))
  await tick()
  return states
}

test('GET paths encode scope, namespace and exact version without substituting latest', () => {
  assert.equal(tracePath(selection), '/runs/run%2Fa/cases/case%2Fa/traces?fixture=false')
  assert.equal(tracePath({ ...selection, fixtureMode: true }, { id: 't/a', version: 'v /2' }), '/runs/run%2Fa/cases/case%2Fa/traces/t%2Fa?fixture=true&version=v+%2F2')
})
test('run, scenario, case and exact case/trace versions are isolated', async () => {
  for (const change of [{ run_id: 'other' }, { scenario_id: 'other' }, { case_id: 'other' }, { input_refs: [] }, { input_refs: [{ ...ref, version: 'v1' }] }, { input_refs: [ref, ref] }]) {
    assert.equal(traceMatches({ ...trace, ...change }, selection), false)
    assert.equal((await run(async () => [{ ...trace, ...change }])).at(-1).status, 'unavailable')
  }
  for (const change of [{ id: 'other' }, { version: 'v11' }]) {
    assert.equal((await run(async () => ({ ...trace, ...change }), trace)).at(-1).status, 'unavailable')
  }
  const states = await run(async () => { assert.fail('invalid run must not request') }, null, { ...selection, runId: 'other' })
  assert.equal(states.at(-1).status, 'unavailable')
})
test('publication order, multiple identities, failed/fallback steps and null/zero fields survive unchanged', async () => {
  const records = [trace, { ...trace, id: 'second', version: 'v2' }]
  const states = await run(async () => records)
  assert.deepEqual(states.at(-1), { status: 'ready', data: records })
  const detail = await run(async () => trace, trace)
  assert.equal(detail.at(-1).data[0], trace)
})
test('empty, unavailable and API errors stay independent without fixture fallback', async () => {
  assert.equal((await run(async () => [])).at(-1).status, 'empty')
  assert.equal((await run(async () => [], trace)).at(-1).status, 'unavailable')
  for (const code of [404, 409, 503]) {
    const states = await run(async () => { throw new Error(`HTTP ${code}`) }, trace)
    assert.deepEqual(states, [{ status: 'loading' }, { status: 'error', message: `HTTP ${code}` }])
  }
  assert.equal((await run(async () => trace, trace)).at(-1).status, 'ready', 'explicit retry can recover')
})
test('list and detail cleanup ignores stale successes/errors for every changed selection dimension', async () => {
  for (const exact of [undefined, trace]) for (const fail of [false, true]) for (const next of [
    { ...selection, runId: 'other', item: { ...item, run_id: 'other' } },
    { ...selection, item: { ...item, id: 'other' } },
    { ...selection, item: { ...item, version: 'v3' } },
    { ...selection, fixtureMode: true }
  ]) {
    let finish, signal
    const stale = []
    const reader = (_path, received) => { signal = received; return new Promise((resolve, reject) => { finish = () => fail ? reject(new Error('late')) : resolve(exact ? trace : [trace]) }) }
    const publish = (state) => stale.push(state)
    const cleanup = exact ? requestCaseTrace(selection, exact, reader, publish) : requestCaseTraces(selection, reader, publish)
    cleanup()
    await run(async () => [], undefined, next)
    finish(); await tick()
    assert.equal(signal.aborted, true)
    assert.deepEqual(stale, [{ status: 'loading' }])
  }
})
test('actual trace rendering escapes model/tool text, keeps errors, order, fallback and unresolved references', () => {
  const require = createRequire(import.meta.url)
  const ts = require('typescript')
  const React = require('react')
  const { renderToStaticMarkup } = require('react-dom/server')
  const source = readFileSync(new URL('../src/sections/CaseTracePanel.tsx', import.meta.url), 'utf8')
  const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } }).outputText
  const module = { exports: {} }
  vm.runInNewContext(output, { exports: module.exports, require: (name) => {
    if (name === '../ui') return { StatusBadge: ({ label }) => React.createElement('span', null, label) }
    if (name.startsWith('../api/') || name.endsWith('.css')) return {}
    return require(name)
  } })
  const html = renderToStaticMarkup(React.createElement(module.exports.TraceRecord, { trace: { ...trace, steps: [...trace.steps, { ...trace.steps[0], tool: 'finish', error: null }] }, selection }))
  assert.ok(html.includes('&lt;script&gt;'))
  assert.ok(!/<script|<img|<a\b/.test(html))
  for (const text of ['fallback sì', 'Errore:', 'Token input: Non disponibili', 'token output: 0', 'StockFact', 'missing', 'v3', 'riferimento non risolto', 'non presente nel contratto', 'Esempio sintetico fixture']) assert.ok(html.includes(text), text)
  assert.ok(html.indexOf('get_stock') < html.indexOf('finish'))
  assert.ok(source.includes('key={JSON.stringify([props.runId, props.fixtureMode, props.item])}'), 'selection changes remount and clear expanded state synchronously')
  assert.ok(source.includes('key={JSON.stringify([selected.id, selected.version])}'), 'exact detail version changes remount detail state')
})
