import assert from 'node:assert/strict'
import { test } from 'node:test'
import { nextRunRequest, selectionIssues, submitModuleRun } from '../src/api/moduleSelection.ts'

const snapshot = (id, enabled = true, requires = [], mode = 'recorded') => ({
  manifest: { id, version: 'v1', layer: 'sources', description: id, requires, optional_inputs: [], produces: [], enabled, mode, params_schema: {} },
  params: { stores: ['MIL01'] }
})
const run = {
  spec: {
    run_id: 'original', scenario_id: 'dev', as_of: '2026-10-22T20:00:00Z', stores: ['MIL01'],
    source_manifest_hash: 'source-v1', config_hash: 'config-v1', code_version: 'code-v1', schema_version: '1.0',
    mode: 'recorded', modules: [snapshot('src.email'), snapshot('ing.extract', true, ['src.email'])],
    prompt_versions: { extract: 'v1' }, model_versions: { extract: 'model-v1' }, authorized_fixture_refs: []
  },
  namespace: 'product', status: 'succeeded', published: true, module_runs: []
}

test('new run preserves scope and provenance without mutating the historical snapshot', async () => {
  const original = structuredClone(run)
  const body = await nextRunRequest(run, { 'ing.extract': false })
  assert.equal('run_id' in body, false)
  assert.deepEqual(run, original)
  assert.deepEqual(body.modules[0], run.spec.modules[0])
  assert.equal(body.modules[1].manifest.enabled, false)
  assert.deepEqual(body.modules[1].params, run.spec.modules[1].params)
  for (const field of ['as_of', 'stores', 'source_manifest_hash', 'code_version', 'schema_version', 'prompt_versions', 'model_versions', 'authorized_fixture_refs']) {
    assert.deepEqual(body[field], run.spec[field])
  }
  assert.match(body.config_hash, /^[a-f0-9]{64}$/)
  assert.notEqual(body.config_hash, run.spec.config_hash)
  assert.equal(body.config_hash, (await nextRunRequest(run, { 'ing.extract': false })).config_hash)
  assert.notEqual(body.config_hash, (await nextRunRequest(run, { 'src.email': false })).config_hash)
})

test('disabled or absent dependencies and empty executable graphs cannot be submitted', () => {
  assert.deepEqual(selectionIssues(run, { 'ing.extract': false }), [])
  assert.match(selectionIssues(run, { 'src.email': false })[0], /ing.extract richiede src.email/)
  assert.match(selectionIssues(run, { 'src.email': false, 'ing.extract': false })[0], /almeno un modulo/)
  const missing = structuredClone(run)
  missing.spec.modules = [snapshot('ing.extract', true, ['missing'])]
  assert.match(selectionIssues(missing, {})[0], /richiede missing/)
  missing.spec.modules = [snapshot('unavailable', true, [], 'unavailable')]
  assert.match(selectionIssues(missing, {})[0], /almeno un modulo/)
})

test('new pipeline requests omit the investigation ERP boundary and retain a stable hash', async () => {
  const baseline = await nextRunRequest(run, {})
  for (const erp_max_seq of [null, 0, 42]) {
    const selected = { ...run, spec: { ...run.spec, erp_max_seq } }
    const body = await nextRunRequest(selected, {})
    assert.equal('erp_max_seq' in body, false)
    assert.deepEqual(body, baseline)
    assert.equal(selected.spec.erp_max_seq, erp_max_seq)
  }
})

test('submission persists the complete selection and surfaces server rejection', async (t) => {
  const body = await nextRunRequest(run, { 'ing.extract': false })
  const created = { ...run, spec: { ...body, run_id: 'new-run' }, status: 'pending', published: false }
  t.mock.method(globalThis, 'fetch', async (url, init) => {
    assert.equal(url, '/api/runs')
    assert.equal(init.method, 'POST')
    assert.deepEqual(JSON.parse(init.body), body)
    return Response.json(created, { status: 202 })
  })
  assert.deepEqual(await submitModuleRun(body), created)
  globalThis.fetch.mock.mockImplementation(async () => new Response('', { status: 422 }))
  await assert.rejects(submitModuleRun(body), /422/)
})

test('configuration identity is canonical and independent of prior toggle history', async () => {
  const firstOff = await nextRunRequest(run, { 'ing.extract': false })
  const backOn = await nextRunRequest({ ...run, spec: { ...firstOff, run_id: 'second' } }, { 'ing.extract': true })
  const secondOff = await nextRunRequest({ ...run, spec: { ...backOn, run_id: 'third' } }, { 'ing.extract': false })
  assert.equal(firstOff.config_hash, secondOff.config_hash)
  const reordered = structuredClone(run)
  reordered.spec = Object.fromEntries(Object.entries(reordered.spec).reverse())
  reordered.spec.modules[0].manifest = Object.fromEntries(Object.entries(reordered.spec.modules[0].manifest).reverse())
  assert.equal(firstOff.config_hash, (await nextRunRequest(reordered, { 'ing.extract': false })).config_hash)
})
