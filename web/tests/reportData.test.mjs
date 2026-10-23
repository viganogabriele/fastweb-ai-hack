import test from 'node:test'
import assert from 'node:assert/strict'
import { belongsToRun, briefTokens, citedValue, loadReports, reportOwners, resolveReportCitation, runPath } from '../src/sections/reportData.ts'

const run = { namespace: 'product', spec: { run_id: 'run/a', scenario_id: 'dev', as_of: '2026-10-22T20:00:00Z' } }
const citation = { ref: { kind: 'Observation', id: 'obs1', version: 'v2' }, field: 'quantity.value', unit: 'requests' }
const caseRef = { ref: { kind: 'Case', id: 'case1', version: 'v1' } }
const report = { id: 'brief', version: 'v2', run_id: 'run/a', scenario_id: 'dev', as_of: run.spec.as_of, view: 'by_office', markdown: '# Brief\n\n7 requests [1]', citations: [citation, caseRef], input_version_hash: 'hash-v2' }
const cases = [{ id: 'case1', version: 'v1', owner: 'allocation/a' }, { id: 'case1', version: 'v2', owner: 'other' }]
const artifact = { id: 'obs1', version: 'v2', run_id: 'run/a', scenario_id: 'dev', quantity: { value: 7 } }
const detail = () => ({ report: structuredClone(report), citations: [{ citation: structuredClone(citation), artifact: structuredClone(artifact) }] })
const signal = new AbortController().signal

test('run paths escape identifiers and explicitly isolate fixture/product namespaces', () => {
  assert.equal(runPath(run, 'reports'), '/runs/run%2Fa/reports?fixture=false')
  assert.equal(runPath({ ...run, namespace: 'fixture' }, 'reports/a?view=by_office'), '/runs/run%2Fa/reports/a?view=by_office&fixture=true')
})

test('office filtering uses the exact cited Case version, not the current owner', () => {
  assert.deepEqual(reportOwners(report, cases), ['allocation/a'])
  assert.deepEqual(reportOwners(report, cases.slice(1)), [])
})

test('load is read-only and rejects reports from another run, scenario or cutoff', async () => {
  const calls = []
  const reader = async (path, receivedSignal) => { calls.push(path); assert.equal(receivedSignal, signal); return path.includes('/reports') ? [report] : cases }
  assert.deepEqual(await loadReports(run, signal, reader), { reports: [report], cases })
  assert.deepEqual(calls, ['/runs/run%2Fa/reports?fixture=false', '/runs/run%2Fa/cases?fixture=false'])
  for (const changed of [{ run_id: 'other' }, { scenario_id: 'other' }, { as_of: '2026-10-23T20:00:00Z' }]) {
    assert.equal(belongsToRun({ ...report, ...changed }, run), false)
    await assert.rejects(loadReports(run, signal, async (path) => path.includes('/reports') ? [{ ...report, ...changed }] : cases), /non appartiene/)
  }
})

test('clicking a citation resolves its pinned artifact through the same-run owner API', async () => {
  const result = await resolveReportCitation(run, report, cases, 0, signal, async (path, receivedSignal) => {
    assert.equal(path, '/runs/run%2Fa/reports/allocation%2Fa?view=by_office&fixture=false')
    assert.equal(receivedSignal, signal)
    return [detail()]
  })
  assert.deepEqual(result, { citation, artifact })
  assert.equal(citedValue(result.artifact, citation.field), 7)
})

test('citation resolution rejects stale report versions, numbering, fields and foreign artifacts', async () => {
  for (const mutate of [
    (d) => { d.report.version = 'v3' },
    (d) => { d.report.run_id = 'other' },
    (d) => { d.report.input_version_hash = 'other' },
    (d) => { d.report.markdown = 'changed text' },
    (d) => { d.citations[0].citation.ref.version = 'v1' },
    (d) => { d.citations[0].citation.field = 'quantity.kind' },
    (d) => { d.citations[0].citation.unit = 'units' },
    (d) => { d.citations[0].artifact.version = 'v1' },
    (d) => { d.citations[0].artifact.run_id = 'other' },
    (d) => { d.citations[0].artifact.scenario_id = 'other' },
    (d) => { d.citations = [] }
  ]) {
    const data = detail(); mutate(data)
    await assert.rejects(resolveReportCitation(run, report, cases, 0, signal, async () => [data]), /stesso run/)
  }
  await assert.rejects(resolveReportCitation(run, report, [], 0, signal, async () => []), /non risolvibile/)
  await assert.rejects(resolveReportCitation(run, report, cases, 99, signal, async () => []), /non risolvibile/)
  await assert.rejects(resolveReportCitation(run, report, cases, 0, signal, async () => { throw new Error('API unavailable') }), /API unavailable/)
})

test('brief text only turns valid citation numbers and strong text into tokens; raw HTML stays text', () => {
  assert.deepEqual(briefTokens('**MIL01** 7 requests [1] [0] [99] <script>x</script>', 2), [
    { kind: 'strong', value: 'MIL01' }, { kind: 'text', value: ' 7 requests ' },
    { kind: 'citation', value: '[1]', index: 0 }, { kind: 'text', value: ' ' },
    { kind: 'text', value: '[0]' }, { kind: 'text', value: ' ' },
    { kind: 'text', value: '[99]' }, { kind: 'text', value: ' <script>x</script>' }
  ])
})

test('field inspection preserves zero, unknowns, units and arrays without inventing totals', () => {
  assert.equal(citedValue({ quantity: { value: 0 } }, 'quantity.value'), 0)
  assert.equal(citedValue({ quantity: { value: null } }, 'quantity.value'), null)
  assert.equal(citedValue({}, 'quantity.value'), undefined)
  assert.equal(citedValue({}, '__proto__.toString'), undefined)
  assert.deepEqual(citedValue({ series: [{ baseline: 2 }, { baseline: null }, { baseline: 0 }] }, 'series.baseline'), [2, null, 0])
})
