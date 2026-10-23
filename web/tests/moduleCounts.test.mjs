import test from 'node:test'
import assert from 'node:assert/strict'
import { countLabel, moduleMetrics, splitMetrics } from '../src/sections/moduleCounts.ts'

test('rows/new pairs merge into one metric, new shown only when it differs', () => {
  assert.deepEqual(moduleMetrics({ stores_rows: 4, stores_new: 4, sales_rows: 10, sales_new: 3, events: 2 }), [
    { key: 'stores', label: 'negozi', value: 4, fresh: null },
    { key: 'sales', label: 'vendite', value: 10, fresh: 3 },
    { key: 'events', label: 'eventi', value: 2, fresh: null }
  ])
})

test('headline metrics skip zeros and diagnostics; the rest keeps zeros last', () => {
  const metrics = moduleMetrics({ documents_unmapped: 12, rows_outside_run: 38, documents: 1, facts: 0, sheets: 7 })
  const { primary, rest } = splitMetrics(metrics)
  assert.deepEqual(primary.map((metric) => metric.key), ['documents', 'sheets'])
  assert.deepEqual(rest.map((metric) => metric.key), ['documents_unmapped', 'rows_outside_run', 'facts'])
})

test('unknown keys fall back to word-by-word labels', () => {
  assert.equal(countLabel('sku_size_ean'), 'SKU taglia')
  assert.equal(countLabel('cases_new_things'), 'casi nuovi things')
})
