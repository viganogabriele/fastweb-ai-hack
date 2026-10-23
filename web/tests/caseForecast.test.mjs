import test from 'node:test'
import assert from 'node:assert/strict'
import { caseSku, forecastPath, selectCaseForecast, requestCaseForecast } from '../src/api/caseForecast.ts'

const item = { id: 'case/a', version: 'v2', run_id: 'run/a', scenario_id: 'dev', store_id: 'MIL/01', scope_level: 'sku', scope_id: 'STYLE-999' }
const selection = { item, runId: item.run_id, fixtureMode: false }
const ref = (kind, record) => ({ kind, id: record.id, version: record.version })
const base = { id: 'baseline', version: 'v3', run_id: item.run_id, scenario_id: 'dev', store_id: item.store_id, sku: item.scope_id, producer: 'fc.baseline', case_ids: [], baseline_ref: { kind: 'ForecastVintage', id: 'erp/a', version: 'v1' }, horizon_start: '2026-10-23', horizon_end: '2026-10-24', input_refs: [], status: 'unchanged', series: [] }
const overlay = { ...base, id: 'overlay', version: 'v1', producer: 'fc.overlay', case_ids: [item.id], input_refs: [ref('Case', item), ref('ForecastAdjustment', base)], status: 'not_estimable', reason: 'no valid quantitative evidence', series: [{ date: '2026-10-23', baseline: null, latent: null, servable: null }, { date: '2026-10-24', baseline: 0, latent: null, servable: null }] }
const tick = () => new Promise((resolve) => setImmediate(resolve))

test('forecast endpoint encodes run, store, SKU and explicitly sets namespace', () => {
  assert.equal(forecastPath(selection), '/runs/run%2Fa/forecast?fixture=false&store=MIL%2F01&sku=STYLE-999')
  assert.match(forecastPath({ ...selection, fixtureMode: true }), /fixture=true/)
  assert.equal(caseSku({ ...item, scope_level: 'sku_size', scope_id: 'STYLE-999-XL' }), 'STYLE-999')
  assert.equal(caseSku({ ...item, scope_level: 'style' }), null)
  assert.equal(caseSku({ ...item, scope_level: 'sku_size', scope_id: 'unresolved' }), null)
})

test('only exact run, scenario, store, SKU and producer are accepted', () => {
  for (const change of [{ run_id: 'other' }, { scenario_id: 'other' }, { store_id: 'other' }, { sku: 'other' }, { producer: 'other' }]) {
    assert.equal(selectCaseForecast([{ ...base, ...change }], selection).baselines.length, 0)
    assert.equal(selectCaseForecast([base, { ...overlay, ...change }], selection).overlays.length, 0)
  }
  assert.equal(selectCaseForecast([base, { ...overlay, case_ids: ['other'] }], selection).overlays.length, 0)
  assert.equal(selectCaseForecast([base, { ...overlay, input_refs: [ref('Case', { ...item, version: 'v1' })] }], selection).overlays.length, 0)
  assert.equal(selectCaseForecast([base, { ...overlay, input_refs: [] }], selection).overlays.length, 0)
})

test('resolves exact baseline version and vintage; never substitutes latest or another horizon', () => {
  const newer = { ...base, version: 'v4' }
  assert.equal(selectCaseForecast([newer, base, overlay], selection).overlays[0].baseline, base)
  for (const change of [{ version: 'v4' }, { horizon_end: '2026-10-25' }, { baseline_ref: { ...base.baseline_ref, version: 'v2' } }, { sku: 'other' }]) {
    const result = selectCaseForecast([{ ...base, ...change }, overlay], selection)
    assert.equal(result.overlays[0].baseline, null)
    assert.equal(result.unresolved, 1)
  }
})

test('stored abstention, dates, nulls and zero survive without inferred scenarios', () => {
  const result = selectCaseForecast([base, overlay], selection)
  assert.equal(result.overlays[0].forecast, overlay)
  assert.equal(result.overlays[0].forecast.series[0].baseline, null)
  assert.equal(result.overlays[0].forecast.series[1].baseline, 0)
  assert.equal(result.overlays[0].forecast.series[1].latent, null)
  assert.equal(result.overlays[0].forecast.reason, overlay.reason)
})

test('style cases retain each exact SKU; unknown scopes do not request arbitrary forecasts', async () => {
  const style = { ...selection, item: { ...item, scope_level: 'style', scope_id: 'STYLE' } }
  assert.equal(selectCaseForecast([base, { ...base, id: 'other', sku: 'STYLEX-999' }], style).baselines.length, 1)
  const states = []
  requestCaseForecast({ ...selection, item: { ...item, scope_level: 'unknown' } }, async () => { assert.fail('must not request') }, (state) => states.push(state))
  assert.equal(states.at(-1).status, 'unavailable')
  await tick()
})

test('API errors never fall back to fixtures; empty and unresolved are distinct', async () => {
  for (const [reader, expected] of [
    [async () => { throw new Error('HTTP 503') }, 'error'],
    [async () => [], 'empty'],
    [async () => [{ ...overlay, input_refs: [] }], 'unavailable']
  ]) {
    const states = []
    requestCaseForecast(selection, reader, (state) => states.push(state))
    await tick()
    assert.equal(states[0].status, 'loading')
    assert.equal(states.at(-1).status, expected)
  }
})

test('selection cleanup discards late success and error even when reader ignores cancellation', async () => {
  for (const fail of [false, true]) {
    let finish
    let signal
    const stale = []
    const cleanup = requestCaseForecast(selection, (_path, received) => {
      signal = received
      return new Promise((resolve, reject) => { finish = () => fail ? reject(new Error('late error')) : resolve([base, overlay]) })
    }, (state) => stale.push(state))
    cleanup()
    const active = []
    requestCaseForecast({ ...selection, fixtureMode: true, item: { ...item, version: 'v3' } }, async () => [], (state) => active.push(state))
    finish()
    await tick()
    assert.equal(signal.aborted, true)
    assert.deepEqual(stale, [{ status: 'loading' }])
    assert.equal(active.at(-1).status, 'empty')
  }
})
