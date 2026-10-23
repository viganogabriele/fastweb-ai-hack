import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { once } from 'node:events'
import test from 'node:test'
import { CASES, DOCUMENTS, MAIN_RUN, RUNS, forRun } from '../mock-api/data.ts'
import { mockApi } from '../mock-api/plugin.ts'

test('synthetic records respect publication, run identity, store scope and cutoff', () => {
  for (const run of RUNS) {
    const cases = forRun(run.spec.run_id, CASES, item => item.store_id)
    const documents = forRun(run.spec.run_id, DOCUMENTS, item => item.meta.store_id)
    for (const item of [...cases, ...documents]) {
      assert.ok(run.published)
      assert.ok(Date.parse(item.available_at) <= Date.parse(run.spec.as_of))
      if ('run_id' in item) assert.equal(item.run_id, run.spec.run_id)
    }
    if (!run.published) assert.deepEqual([cases, documents], [[], []])
  }
  assert.equal(forRun('missing', CASES, item => item.store_id), undefined)
  assert.ok(forRun(MAIN_RUN, CASES, item => item.store_id).length > 0)
  assert.deepEqual(forRun(MAIN_RUN, [
    { available_at: '2026-10-23T00:00:00Z', store: 'MIL01' },
    { available_at: '2026-10-21T00:00:00Z', store: 'OUTSIDE' },
  ], item => item.store), [])
})

test('mock middleware rejects malformed, unsupported and mutation routes locally', async t => {
  let middleware
  const plugin = mockApi()
  assert.equal(plugin.apply, 'serve')
  plugin.configureServer({ middlewares: { use(path, handler) {
    assert.equal(path, '/api')
    middleware = handler
  } } })
  const server = createServer((req, res) => middleware(req, res))
  server.listen(0, '127.0.0.1')
  await once(server, 'listening')
  t.after(() => server.close())
  const base = `http://127.0.0.1:${server.address().port}`
  for (const [path, method, status] of [
    ['/runs', 'GET', 200],
    ['/runs', 'POST', 409],
    ['/runs', 'DELETE', 405],
    ['/not-mocked', 'GET', 404],
    ['/health/extra', 'GET', 404],
    [`/runs/${MAIN_RUN}/cases/missing/extra`, 'GET', 404],
    ['/runs/%E0%A4%A', 'GET', 400],
  ]) {
    const response = await fetch(base + path, { method })
    assert.equal(response.status, status, `${method} ${path}`)
    assert.equal(response.headers.get('x-tesseract-mock'), '1')
    await response.json()
  }
})
