import test from 'node:test'
import assert from 'node:assert/strict'
import { caseOptionsPath, loadCaseOptions, mandatoryBlockers, OptionsApiError, optionsContextKey, postCaseDecision } from '../src/api/caseOptions.ts'
import { createOptionsSession, intentKey } from '../src/sections/caseOptionsState.ts'

const context = { runId: 'run / a', caseId: 'case / a', version: 'v1', fixture: true }
const option = { id: 'o1', version: 'v1', input_version_hash: 'exact-hash', checks: [] }
const intent = { option_id: 'o1', input_version_hash: 'exact-hash', decision: 'approved', by: 'Local reviewer', note: 'Reviewed' }
const draft = body => ({ decision: { ...body, id: 'decision-1', dispatch_status: 'draft' }, option, reservations: [], simulated: true })
const deferred = () => {
  let resolve, reject
  const promise = new Promise((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
function harness({ load = async () => [option], post = async (_, body) => draft(body), ctx = context } = {}) {
  let keys = 0
  const calls = []
  const session = createOptionsSession(ctx, { load, post: async (...args) => { calls.push(args); return post(...args) }, key: () => `key-${++keys}` })
  return { session, calls }
}

test('transport uses encoded case endpoint, exact payload and explicit fixture namespace for reads and writes', async () => {
  const original = globalThis.fetch
  const calls = []
  globalThis.fetch = async (...args) => { calls.push(args); return Response.json(args[1].method ? draft(intent) : [option]) }
  try {
    for (const fixture of [true, false]) {
      const ctx = { ...context, fixture }
      assert.deepEqual(await loadCaseOptions(ctx, new AbortController().signal), [option])
      const body = Object.freeze({ ...intent, idempotency_key: 'fixed' })
      await postCaseDecision(ctx, body)
      const [read, write] = calls.splice(0)
      assert.equal(read[0], `${caseOptionsPath(ctx)}/options?fixture=${fixture}`)
      assert.equal(write[0], `/api/runs/run%20%2F%20a/cases/case%20%2F%20a/decisions?fixture=${fixture}`)
      assert.equal(write[1].method, 'POST')
      assert.deepEqual(JSON.parse(write[1].body), body)
      assert.ok(write[1].signal instanceof AbortSignal)
    }
  } finally { globalThis.fetch = original }
})

test('transport distinguishes conflict, validation, missing and busy; no error falls back to demo data', async () => {
  const original = globalThis.fetch
  try {
    for (const status of [409, 422, 404, 503]) {
      globalThis.fetch = async () => new Response('{}', { status })
      await assert.rejects(postCaseDecision(context, { ...intent, idempotency_key: 'k' }), error => error instanceof OptionsApiError && error.status === status)
      await assert.rejects(loadCaseOptions(context, new AbortController().signal), OptionsApiError)
    }
  } finally { globalThis.fetch = original }
})

test('double-click lock prevents duplicate commands; success only exists after server reply', async () => {
  const response = deferred()
  const { session, calls } = harness({ post: () => response.promise })
  await session.load()
  assert.equal(calls.length, 0, 'loading never submits')
  const pending = session.submit(intent)
  await session.submit(intent)
  assert.equal(calls.length, 1)
  assert.equal(session.snapshot().commands.get(intentKey(intent)).status, 'pending')
  assert.equal(session.snapshot().commands.get(intentKey(intent)).result, undefined)
  assert.equal(session.snapshot().pending, true)
  response.resolve(draft(calls[0][1]))
  await pending
  assert.equal(session.snapshot().commands.get(intentKey(intent)).result.decision.id, 'decision-1')
  await session.submit(intent)
  assert.equal(calls.length, 1, 'a confirmed success cannot be submitted again')
})

test('503, network errors and timeouts preserve one frozen payload/key through retries, even if caller edits intent', async () => {
  for (const error of [new OptionsApiError(503), new TypeError('offline'), new DOMException('timeout', 'TimeoutError')]) {
    let attempts = 0
    const { session, calls } = harness({ post: async (_, body) => { if (++attempts === 1) throw error; return draft(body) } })
    await session.load()
    const edited = { ...intent }
    const first = session.submit(edited)
    edited.by = 'Someone else'
    await first
    const failed = session.snapshot().commands.get(intentKey(intent))
    assert.equal(failed.status, 'retryable')
    assert.equal(failed.result, undefined)
    assert.ok(Object.isFrozen(failed.body))
    await session.submit({ ...intent })
    assert.equal(calls[0][1], calls[1][1], 'retry reuses the exact object, including key and note')
    assert.equal(calls[1][1].by, intent.by)
    assert.equal(session.snapshot().commands.get(intentKey(intent)).status, 'success')
  }
})

test('each changed reviewer, note, action, option or hash is a new command', async () => {
  const second = { ...option, id: 'o2', input_version_hash: 'other-hash' }
  const { session, calls } = harness({ load: async () => [option, second] })
  await session.load()
  for (const next of [intent, { ...intent, by: 'Other' }, { ...intent, note: 'Other note' }, { ...intent, decision: 'rejected' }, { ...intent, option_id: second.id, input_version_hash: second.input_version_hash }]) {
    await session.submit(next)
  }
  assert.equal(new Set(calls.map(([, body]) => body.idempotency_key)).size, 5)
  const sameIdNewHash = { ...option, input_version_hash: 'new-hash' }
  const next = harness({ load: async () => [sameIdNewHash] })
  await next.session.load()
  await next.session.submit(intent)
  assert.equal(next.calls.length, 0, 'an old hash never submits against refreshed inputs')
  await next.session.submit({ ...intent, input_version_hash: 'new-hash' })
  assert.equal(next.calls.length, 1)
})

test('409 refetches and blocks decisions until fresh options have loaded and human review is acknowledged', async () => {
  const refreshed = deferred()
  let reads = 0, writes = 0
  const { session, calls } = harness({ load: async () => ++reads === 1 ? [option] : refreshed.promise,
    post: async (_, body) => { if (++writes === 1) throw new OptionsApiError(409); return draft(body) } })
  await session.load()
  const conflicting = session.submit(intent)
  await Promise.resolve(); await Promise.resolve(); await Promise.resolve()
  assert.equal(session.snapshot().reviewRequired, true)
  assert.equal(session.snapshot().loading, true)
  session.reviewed()
  await session.submit(intent)
  assert.equal(calls.length, 1)
  refreshed.resolve([option])
  await conflicting
  assert.equal(session.snapshot().commands.get(intentKey(intent)).status, 'conflict')
  await session.submit(intent)
  assert.equal(calls.length, 1, 'refetch alone does not authorize another decision')
  session.reviewed()
  await session.submit(intent)
  assert.equal(calls.length, 2)
  assert.notEqual(calls[0][1].idempotency_key, calls[1][1].idempotency_key, 'fresh review creates a new command even if published hash is unchanged')
})

test('failed conflict refresh cannot be acknowledged, and 404/422 are explicit terminal failures', async () => {
  let reads = 0
  const conflict = harness({ load: async () => { if (++reads > 1) throw new TypeError('offline'); return [option] }, post: async () => { throw new OptionsApiError(409) } })
  await conflict.session.load()
  await conflict.session.submit(intent)
  conflict.session.reviewed()
  assert.equal(conflict.session.snapshot().reviewRequired, true)
  assert.match(conflict.session.snapshot().error, /rete/)
  for (const status of [404, 422]) {
    const { session, calls } = harness({ post: async () => { throw new OptionsApiError(status) } })
    await session.load(); await session.submit(intent); await session.submit(intent)
    assert.equal(calls.length, 1)
    assert.equal(session.snapshot().commands.get(intentKey(intent)).status, 'failed')
    assert.equal(session.snapshot().commands.get(intentKey(intent)).result, undefined)
  }
})

test('mandatory unknown/fail block approval but allow rejection; optional unknown never becomes pass', async () => {
  for (const status of ['unknown', 'fail']) {
    const candidate = { ...option, checks: [{ name: 'stock', status, mandatory: true }] }
    const { session, calls } = harness({ load: async () => [candidate] })
    await session.load(); await session.submit(intent)
    assert.equal(calls.length, 0)
    assert.equal(mandatoryBlockers(candidate)[0].status, status)
    await session.submit({ ...intent, decision: 'rejected' })
    assert.equal(calls.length, 1)
  }
  const candidate = { ...option, checks: [{ name: 'stock', status: 'unknown', mandatory: false }] }
  const { session, calls } = harness({ load: async () => [candidate] })
  await session.load(); await session.submit(intent)
  assert.equal(calls.length, 1)
  assert.equal(session.snapshot().options[0].checks[0].status, 'unknown')
})

test('run/case/version/namespace changes isolate sessions, reject late reads and writes, and never auto-resubmit', async () => {
  const base = optionsContextKey(context)
  for (const change of [{ runId: 'other' }, { caseId: 'other' }, { version: 'v2' }, { fixture: false }]) {
    const nextContext = { ...context, ...change }
    assert.notEqual(optionsContextKey(nextContext), base)
    const response = deferred()
    const old = harness({ post: () => response.promise })
    await old.session.load()
    const pending = old.session.submit(intent)
    old.session.dispose()
    const frozen = old.session.snapshot()
    const next = harness({ ctx: nextContext })
    await next.session.load()
    response.resolve(draft(intent))
    await pending
    assert.equal(old.session.snapshot(), frozen)
    assert.equal(next.session.snapshot().commands.size, 0)
    assert.equal(next.calls.length, 0)
    await old.session.submit(intent)
    assert.equal(old.calls.length, 1)
  }
  const late = deferred()
  const old = harness({ load: () => late.promise })
  const loading = old.session.load()
  old.session.dispose()
  const frozen = old.session.snapshot()
  late.resolve([option]); await loading
  assert.equal(old.session.snapshot(), frozen)
})

test('superseded loads and React StrictMode restart reject old results', async () => {
  const first = deferred(), second = deferred()
  let reads = 0
  const { session } = harness({ load: () => ++reads === 1 ? first.promise : second.promise })
  session.start(); session.dispose(); session.start()
  second.resolve([option])
  await Promise.resolve(); await Promise.resolve()
  first.resolve([{ ...option, input_version_hash: 'stale' }])
  await Promise.resolve(); await Promise.resolve()
  assert.equal(session.snapshot().options[0].input_version_hash, 'exact-hash')
})

test('returning to a case preserves an uncertain command and requires an explicit retry with its original key', async () => {
  const response = deferred()
  const old = harness({ post: () => response.promise })
  await old.session.load()
  const pending = old.session.submit(intent)
  old.session.dispose()
  const saved = old.session.snapshotForResume()
  const calls = []
  const next = createOptionsSession(context, { load: async () => [option], post: async (_, body) => { calls.push(body); return draft(body) }, key: () => 'should-not-be-used' }, saved)
  await next.load()
  assert.equal(calls.length, 0)
  assert.equal(next.snapshot().commands.get(intentKey(intent)).status, 'retryable')
  response.resolve(draft(intent)); await pending
  assert.equal(next.snapshot().commands.get(intentKey(intent)).status, 'retryable', 'late result from old selection is ignored')
  await next.submit(saved.commands.get(intentKey(intent)).body)
  assert.equal(calls[0], old.calls[0][1])
  assert.equal(next.snapshot().commands.get(intentKey(intent)).status, 'success')
})

test('acknowledging one conflict preserves other uncertain commands and confirmed results', async () => {
  const uncertain = { ...option, id: 'uncertain' }
  const confirmed = { ...option, id: 'confirmed' }
  const calls = []
  let retry = false
  const session = createOptionsSession(context, {
    load: async () => [option, uncertain, confirmed],
    post: async (_, body) => {
      calls.push(body)
      if (body.option_id === uncertain.id && !retry) throw new TypeError('lost response')
      if (body.option_id === option.id) throw new OptionsApiError(409)
      return draft(body)
    },
    key: () => `key-${calls.length}`
  })
  await session.load()
  const uncertainIntent = { ...intent, option_id: uncertain.id }
  const confirmedIntent = { ...intent, option_id: confirmed.id }
  await session.submit(uncertainIntent)
  await session.submit(confirmedIntent)
  const original = session.snapshot().commands.get(intentKey(uncertainIntent)).body
  await session.submit(intent)
  session.reviewed()
  assert.equal(session.snapshot().commands.has(intentKey(intent)), false, 'only the conflicted command is cleared for fresh review')
  assert.equal(session.snapshot().commands.get(intentKey(confirmedIntent)).status, 'success')
  assert.equal(session.snapshot().commands.get(intentKey(uncertainIntent)).body, original)
  retry = true
  await session.submit(uncertainIntent)
  assert.equal(calls.at(-1), original, 'uncertain command must keep its frozen payload and key after unrelated review')
  const count = calls.length
  await session.submit(confirmedIntent)
  assert.equal(calls.length, count, 'confirmed commands remain protected against resubmission')
})
