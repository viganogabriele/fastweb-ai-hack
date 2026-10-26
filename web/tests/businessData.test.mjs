import assert from 'node:assert/strict'
import { test } from 'node:test'
import { change, countByDay, dailySeries, lastDay, storePerformance, totals } from '../src/sections/businessData.ts'

const row = (date, store_id, sales_eur, budget_eur, receipts = 1, visitors = 10) => ({
  date, store_id, available_at: `${date}T06:00:00Z`, sales_eur, budget_eur, receipts, visitors, units: 1, returns_units: 0
})
const rows = [
  row('2026-10-19', 'MIL01', 100, 200, 2, 20),
  row('2026-10-20', 'MIL01', 300, 200, 3, 30),
  row('2026-10-20', 'ROM01', 50, 100, 1, 10),
  row('2026-10-21', 'ROM01', 70, 100, 2, 0),
  row('2026-10-25', 'ROM01', 999, 1, 1, 1)
]

test('daily series keeps every calendar day, sums stores and ignores days outside the window', () => {
  const series = dailySeries(rows, null, 4, '2026-10-21')
  assert.deepEqual(series.map((point) => point.date), ['2026-10-18', '2026-10-19', '2026-10-20', '2026-10-21'])
  assert.deepEqual(series.map((point) => point.sales), [0, 100, 350, 70])
  assert.deepEqual(dailySeries(rows, new Set(['ROM01']), 2, '2026-10-21').map((point) => point.sales), [50, 70])
})

test('totals derive budget gap and conversion, and refuse to divide by zero', () => {
  const sum = totals(dailySeries(rows, new Set(['MIL01']), 3, '2026-10-21'))
  assert.equal(sum.sales, 400)
  assert.equal(sum.vsBudget, 0)
  assert.equal(sum.conversion, 5 / 50)
  const empty = totals([])
  assert.equal(empty.vsBudget, null)
  assert.equal(empty.conversion, null)
  assert.equal(change(110, 100).toFixed(2), '0.10')
  assert.equal(change(5, 0), null)
})

test('store performance and day counts stay inside the window', () => {
  const [mil, rom] = storePerformance(rows, ['MIL01', 'ROM01'], 3, '2026-10-21')
  assert.equal(mil.vsBudget, 0)
  assert.deepEqual(rom.daily, [0, 50, 70])
  assert.equal(lastDay(rows), '2026-10-25')
  const counts = countByDay(
    [{ at: '2026-10-20T09:00:00Z' }, { at: '2026-10-20T23:00:00Z' }, { at: '2026-11-01T00:00:00Z' }, { at: null }],
    (item) => item.at,
    ['2026-10-20', '2026-10-21']
  )
  assert.deepEqual([...counts], [['2026-10-20', 2], ['2026-10-21', 0]])
})


test('missing visitor counters keep conversion unavailable across an aggregate', () => {
  const input = [row('2026-10-20', 'MIL01', 100, 80, 2, null), row('2026-10-20', 'NYC01', 100, 80, 1, 10)]
  const result = totals(dailySeries(input, null, 1, '2026-10-20'))
  assert.equal(result.sales, 200)
  assert.equal(result.visitors, null)
  assert.equal(result.conversion, null)
})
