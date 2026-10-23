import assert from 'node:assert/strict'
import test from 'node:test'
import { filterProductCases, productIndex } from '../src/sections/productView.ts'

const item = (id, overrides = {}) => ({
  id, version: 'v1', run_id: 'run-1', computed_at: '2026-10-22T19:00:00Z',
  scope_level: 'sku', scope_id: 'STYLE-BLACK', store_id: 'MIL01',
  status: 'open', case_type: 'unmet_demand', priority_reason: 'Richieste riportate', owner: 'Retail',
  ...overrides
})

test('uses only latest case versions in the selected run before grouping', () => {
  const result = productIndex([
    item('correction', { scope_id: 'OLD', version: 'v2' }),
    item('correction', { version: 'v10' }),
    item('correction', { run_id: 'run-2', version: 'v11', scope_id: 'FOREIGN' }),
    item('second', { store_id: 'PAR01' })
  ], 'run-1')
  assert.equal(result.groups.length, 1)
  assert.equal(result.groups[0].id, 'STYLE-BLACK')
  assert.deepEqual(result.groups[0].cases.map((c) => c.version), ['v10', 'v1'])
  assert.deepEqual(result.groups[0].stores, ['MIL01', 'PAR01'])
})

test('does not infer product identity or roll style, SKU and SKU-size into one total', () => {
  const result = productIndex([
    item('sku'), item('size', { scope_level: 'sku_size' }),
    item('style', { scope_level: 'style' }),
    item('category', { scope_level: 'category', scope_id: 'Outerwear' }),
    item('unknown', { scope_level: 'unknown', scope_id: null }),
    item('missing', { scope_id: '  ' }),
    item('store', { scope_level: 'store', scope_id: 'MIL01' })
  ], 'run-1')
  assert.equal(result.groups.length, 3)
  assert.ok(result.groups.every((group) => group.cases.length === 1))
  assert.equal(new Set(result.groups.map((group) => group.key)).size, 3)
  assert.deepEqual(result.unresolved.map((c) => c.id), ['category', 'unknown', 'missing', 'store'])
})

test('counts cases without summing overlapping documents or quantitative signals', () => {
  const result = productIndex([
    item('a', { n_documents: 5, n_origin_groups: 2, supporting: [{ id: 'shared' }] }),
    item('b', { n_documents: 5, n_origin_groups: 2, supporting: [{ id: 'shared' }] }),
    item('b')
  ], 'run-1')
  assert.equal(result.groups[0].cases.length, 2)
  assert.deepEqual(Object.keys(result.groups[0]).sort(), ['cases', 'id', 'key', 'level', 'stores'])
})

test('filters the same case by store, status, type and Unicode search without hiding closed or unresolved cases by default', () => {
  const cases = [
    item('a', { priority_reason: 'Taglia indisponibile 東京' }),
    item('b', { store_id: 'PAR01', status: 'closed' }),
    item('c', { scope_id: null, status: 'verify' })
  ]
  const filters = { search: '', store: 'all', status: 'all', type: 'all' }
  assert.equal(filterProductCases(cases, filters).length, 3)
  assert.deepEqual(filterProductCases(cases, { ...filters, search: '  TAGLIA 東京  ' }), [])
  assert.deepEqual(filterProductCases(cases, { ...filters, search: '東京', store: 'MIL01', status: 'open', type: 'unmet_demand' }).map((c) => c.id), ['a'])
  assert.equal(filterProductCases(cases, { ...filters, store: 'PAR01', status: 'verify' }).length, 0)
  assert.equal(filterProductCases(cases, { ...filters, search: 'taglia' }).length, 1)
})

test('empty or foreign-run results produce no invented products', () => {
  assert.deepEqual(productIndex([], 'run-1'), { groups: [], unresolved: [] })
  assert.deepEqual(productIndex([item('a')], 'run-2'), { groups: [], unresolved: [] })
})
