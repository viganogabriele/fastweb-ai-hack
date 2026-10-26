import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import test from 'node:test'
import vm from 'node:vm'

const require = createRequire(import.meta.url)
const React = require('react')
const ts = require('typescript')
const { renderToStaticMarkup } = require('react-dom/server')
const { DEFAULT_CASE_QUEUE_FILTERS } = require('../src/sections/caseUtils.ts')
const source = readFileSync(new URL('../src/sections/CaseQueue.tsx', import.meta.url), 'utf8')
const output = ts.transpileModule(source, { compilerOptions: {
  module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX
} }).outputText

const item = (id, received, extra = {}) => ({
  id, version: 'v1', store_id: 'MIL01', scope_level: 'sku', scope_id: 'COAT-BLACK',
  owner: 'merchandising', status: 'open', case_type: 'unmet_demand', priority: 'low',
  priority_reason: 'New voice evidence', blocking_uncertainties: [], n_unknown_origins: 0,
  source_refs: [], decision_due_at: null,
  first_available_at: received, last_received_at: received,
  // Recomputing a run gives old and new cases the same computation timestamp.
  computed_at: '2026-10-23T20:00:00Z', ...extra
})

function render(cases, filters = {}) {
  const module = { exports: {} }
  vm.runInNewContext(output, {
    exports: module.exports,
    require: (name) => {
      if (name === './caseUtils') return require('../src/sections/caseUtils.ts')
      if (name === './CaseDetail') return { CaseDetail: () => null }
      if (name === './caseLabels') return { ownerLabel: (value) => value }
      if (name === './productView') return { caseTypeLabel: (value) => value }
      if (name.endsWith('.css')) return {}
      if (name === '../ui') return {
        Button: ({ children }) => React.createElement('button', null, children),
        Input: () => null,
        StatusBadge: ({ label }) => React.createElement('span', null, label),
        EmptyState: ({ title }) => React.createElement('p', null, title),
        Select: ({ label, value, options }) => React.createElement('select', {
          'aria-label': label, value, onChange: () => {}
        }, options.map(option => React.createElement('option', {
          key: option.value, value: option.value
        }, option.label)))
      }
      return require(name)
    }
  })
  return renderToStaticMarkup(React.createElement(module.exports.CaseQueue, {
    cases, stores: ['MIL01', 'MIL02'], asOf: '2026-10-23T20:00:00Z', runId: 'run',
    fixtureMode: false, selection: null, onSelect() {}, onReturn() {},
    filters: { ...DEFAULT_CASE_QUEUE_FILTERS, ...filters }, onFiltersChange() {}
  }))
}
const order = (html) => [...html.matchAll(/aria-label="Apri caso ([^.]+)\./g)].map(match => match[1])
const old = item('older', '2026-10-21T18:00:00Z', {
  priority: 'critical', decision_due_at: '2026-10-22T08:00:00Z'
})
const audio = item('new-audio', '2026-10-23T18:00:00Z')

test('a newly transcribed audio case appears first by default, above an older critical case', () => {
  const cases = [old, audio]
  const html = render(cases)
  assert.deepEqual(order(html), ['new-audio', 'older'])
  assert.match(html, /value="recent" selected="">Più recenti/)
  assert.deepEqual(cases.map(c => c.id), ['older', 'new-audio'])
})

test('new evidence brings an existing case to the top, using received time rather than its creation', () => {
  const updated = item('updated', '2026-10-23T19:00:00Z', { first_available_at: old.first_available_at })
  assert.deepEqual(order(render([old, audio, updated])), ['updated', 'new-audio', 'older'])
})

test('received timestamps are compared as instants across time zones', () => {
  const earlier = item('earlier', '2026-10-23T10:00:00+02:00')
  const later = item('later', '2026-10-23T08:30:00Z')
  assert.deepEqual(order(render([earlier, later])), ['later', 'earlier'])
})

test('explicit priority and deadline sorting remain available', () => {
  assert.deepEqual(order(render([audio, old], { sort: 'priority' })), ['older', 'new-audio'])
  assert.deepEqual(order(render([audio, old], { sort: 'deadline' })), ['older', 'new-audio'])
})
