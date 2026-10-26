import assert from 'node:assert/strict'
import test from 'node:test'
import { compareSizes, productCards, productStock, storeRows } from '../src/sections/productsData.ts'

const colour = (sku, stores = [], stock = {}) => ({ sku, colour: 'nero', stores, stock })
const product = (style_code, name, colours) => ({
  style_code, name, category: 'Outerwear', subcategory: 'Jacket', gender: 'W', price_eur: 1000,
  image: '/x.jpg', reference: { name: 'Ref', url: 'https://example.test' }, colours
})
const catalog = {
  available_at: '2026-10-22T06:00:00Z', snapshot_date: '2026-10-21',
  products: [
    product('AAA', 'AUREA', [colour('AAA-999'), colour('AAA-034')]),
    product('BBB', 'BRUNEA', [colour('BBB-41F')]),
    product('CCC', 'CALMA', [colour('CCC-001')])
  ]
}
const item = (id, overrides = {}) => ({
  id, version: 'v1', run_id: 'run-1', computed_at: '2026-10-22T19:00:00Z', scope_level: 'sku',
  scope_id: 'AAA-999', store_id: 'MIL01', status: 'open', priority: 'medium', case_type: 'unmet_demand',
  priority_reason: 'Richieste', owner: 'allocation', decision_due_at: null, ...overrides
})

test('cases link by exact style, SKU or SKU-size and set the attention tier', () => {
  const { cards, unresolved } = productCards(catalog, [
    item('a', { priority: 'critical', scope_level: 'sku_size', scope_id: 'AAA-999-2' }),
    item('b', { priority: 'low', scope_level: 'style', scope_id: 'BBB' }),
    item('c', { priority: 'high', status: 'closed', scope_id: 'CCC-001' })
  ], 'run-1')
  const by = Object.fromEntries(cards.map((card) => [card.product.style_code, card]))
  assert.equal(by.AAA.attention, 'now')
  assert.deepEqual([...by.AAA.skus], ['AAA-999'])
  assert.equal(by.BBB.attention, 'later')
  assert.equal(by.CCC.attention, 'none', 'closed cases do not ask for attention')
  assert.deepEqual(cards.map((card) => card.product.name), ['AUREA', 'BRUNEA', 'CALMA'])
  assert.deepEqual(unresolved, [])
})

test('unknown, category and near-miss scopes stay unresolved instead of being guessed', () => {
  const { cards, unresolved } = productCards(catalog, [
    item('unknown', { scope_level: 'unknown', scope_id: null }),
    item('category', { scope_level: 'category', scope_id: 'Outerwear' }),
    item('prefix', { scope_id: 'AAA' }),
    item('missing', { scope_level: 'style', scope_id: 'ZZZ' }),
    item('nodash', { scope_level: 'sku_size', scope_id: 'AAA999' })
  ], 'run-1')
  assert.ok(cards.every((card) => card.attention === 'none'))
  assert.deepEqual(unresolved.map((entry) => entry.id).sort(), ['category', 'missing', 'nodash', 'prefix', 'unknown'])
})

test('cards order by the most urgent case, then by name', () => {
  const { cards } = productCards(catalog, [
    item('late', { scope_id: 'CCC-001', priority: 'high', decision_due_at: '2026-10-24T10:00:00Z' }),
    item('soon', { scope_id: 'BBB-41F', priority: 'high', decision_due_at: '2026-10-23T10:00:00Z' })
  ], 'run-1')
  assert.deepEqual(cards.map((card) => card.product.name), ['BRUNEA', 'CALMA', 'AUREA'])
})

test('store rows separate stock, sold out and not carried, with sizes in wearing order', () => {
  const rows = storeRows(colour('AAA-999', ['MIL01', 'ROM01'], {
    MIL01: { sizes: { 2: 1, 0: 3, '00': 2 }, in_transit: 4 },
    ROM01: { sizes: { 0: 0, 1: 0 }, in_transit: 0 }
  }), ['MIL01', 'ROM01', 'TYO01'])
  assert.deepEqual(rows.map((row) => [row.store, row.availability, row.units]), [['MIL01', 'in', 6], ['ROM01', 'out', 0], ['TYO01', 'none', 0]])
  assert.deepEqual(rows[0].sizes.map(([size]) => size), ['00', '0', '2'])
  assert.equal(rows[0].inTransit, 4)
  assert.deepEqual(['L', 'XS', 'M'].sort(compareSizes), ['XS', 'M', 'L'])
  assert.deepEqual(['40', '38.5', '39'].sort(compareSizes), ['38.5', '39', '40'])
})

test('network stock counts a store as in stock when any colour is available there', () => {
  const summary = productStock(product('AAA', 'AUREA', [
    colour('AAA-999', ['MIL01', 'ROM01'], { MIL01: { sizes: { 1: 0 }, in_transit: 0 }, ROM01: { sizes: { 1: 0 }, in_transit: 0 } }),
    colour('AAA-034', ['MIL01'], { MIL01: { sizes: { 1: 2 }, in_transit: 0 } })
  ]), ['MIL01', 'ROM01', 'TYO01'])
  assert.deepEqual(summary, { units: 2, storesIn: 1, storesOut: 1 })
})
