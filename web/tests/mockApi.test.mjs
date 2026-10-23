import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CASES, DOCUMENTS, MODULES, OBSERVATIONS, RUNS, documentDetail, forRun } from '../mock-api/data.ts'
import { mockApi } from '../mock-api/plugin.ts'

const storeOf = item => item.store_id ?? String(item.meta.store_id)
test('mock snapshots exclude future data and respect run/store scope and publication', () => {
  for (const records of [CASES, DOCUMENTS]) {
    assert.deepEqual(forRun('mock-2026-10-21', records, storeOf), [])
    assert.deepEqual(forRun('mock-2026-10-23', records, storeOf), [])
    const visible = forRun('fixture', records, storeOf)
    assert.ok(visible.length)
    assert.ok(visible.every(item => Date.parse(item.available_at) <= Date.parse(RUNS[0].spec.as_of)))
    assert.ok(visible.every(item => RUNS[0].spec.stores.includes(storeOf(item))))
  }
  assert.equal(documentDetail(DOCUMENTS[0].id, 'mock-2026-10-21'), undefined)
  assert.ok(MODULES.every(item => item.mode === 'fixture'))
})
test('visible derived artifacts carry the selected run id', () => {
  const run = RUNS[1]
  const records = [{ available_at: '2026-10-20T00:00:00Z', store_id: run.spec.stores[0], run_id: 'fixture' }]
  assert.equal(forRun(run.spec.run_id, records, storeOf)[0].run_id, run.spec.run_id)
  assert.equal(records[0].run_id, 'fixture')
  const excluded = [
    { ...records[0], store_id: 'OUTSIDE' },
    { ...records[0], available_at: null },
    { ...records[0], available_at: '2026-10-22T00:00:00Z' }
  ]
  assert.deepEqual(forRun(run.spec.run_id, excluded, storeOf), [])
})

async function request(path) {
  let middleware
  mockApi().configureServer({ middlewares: { use(_prefix, handler) { middleware = handler } } })
  return new Promise(resolve => {
    const response = { statusCode: 200, setHeader() {}, end(body) { resolve({ status: this.statusCode, body: JSON.parse(body) }) } }
    middleware({ method: 'GET', url: path }, response)
  })
}
test('mock middleware handles malformed encoding without unhandled rejection', async () => {
  assert.equal((await request('/runs/%ZZ')).status, 400)
})
test('unpublished collection requests match API 409 behavior', async () => {
  assert.equal((await request('/runs/mock-2026-10-23/cases')).status, 409)
})

test('visible cases never cite observations available after the cutoff', () => {
  const visible = forRun('fixture', CASES, storeOf)
  for (const item of visible) {
    for (const ref of [...item.supporting, ...item.contradicting]) {
      const obs = OBSERVATIONS.find(record => record.id === ref.id)
      assert.ok(obs)
      assert.ok(Date.parse(obs.available_at) <= Date.parse(RUNS[0].spec.as_of))
    }
  }
})

test('unsupported nested routes return 404 instead of an unrelated case DTO', async () => {
  assert.equal((await request(`/runs/fixture/cases/${CASES[0].id}/clarifications`)).status, 404)
})
