import test from 'node:test'
import assert from 'node:assert/strict'
import { canDecideOption, decisionForRecord, decisionKey, optionBlockers } from '../src/sections/caseDecision.ts'
import { findCaseDetailFixture } from '../src/mocks/caseDetails.ts'

const option = (checks, blockers = []) => ({ id: 'o1', kind: 'transfer', recommended: true, rationale: 'synthetic', checks, blockers })
const check = (status, mandatory = true) => ({ name: 'inventory', status, mandatory, detail: 'test evidence' })

test('fixture examples require fixture mode and exact case/version; run state remains separately scoped', () => {
  assert.ok(findCaseDetailFixture('fixture-run-a', 'case-mil01-j20931a00012-999-20261002', 'v1', true))
  assert.ok(findCaseDetailFixture('fixture-run-b', 'case-mil01-j20931a00012-999-20261002', 'v1', true), 'the same example data is explicitly rendered in a separately scoped fixture context')
  assert.equal(findCaseDetailFixture('live-run', 'case-mil01-j20931a00012-999-20261002', 'v1', false), undefined)
  assert.equal(findCaseDetailFixture('fixture', 'case-mil01-j20931a00012-999-20261002', 'v2', true), undefined)
  const abstention = findCaseDetailFixture('fixture-run-a', 'case-nyc01-unknown-20260906', 'v1', true)
  assert.equal(abstention.forecast.status, 'not_estimable')
  assert.match(abstention.forecast.reason, /SKU verificata/)
})

test('mandatory failed and unknown checks block approval while rejection remains available in fixture demo', () => {
  for (const status of ['fail', 'unknown']) {
    const candidate = option([check(status)])
    assert.equal(canDecideOption(true, 'action_proposed', candidate, 'approved'), false)
    assert.equal(canDecideOption(true, 'action_proposed', candidate, 'rejected'), true)
    assert.match(optionBlockers(candidate).join(' '), status === 'unknown' ? /sconosciuto/ : /non superato/)
  }
})

test('passing or not-applicable mandatory checks allow approval; optional unknown checks do not block', () => {
  assert.equal(canDecideOption(true, 'action_proposed', option([check('pass')]), 'approved'), true)
  assert.equal(canDecideOption(true, 'action_proposed', option([check('not_applicable')]), 'approved'), true)
  assert.equal(canDecideOption(true, 'action_proposed', option([check('unknown', false)]), 'approved'), true)
  assert.deepEqual(optionBlockers(option([check('unknown', false)])), [])
})

test('decisions require fixture mode and an active case, and keys isolate run, case, version, and option', () => {
  const candidate = option([check('pass')])
  assert.equal(canDecideOption(false, 'action_proposed', candidate, 'approved'), false)
  assert.equal(canDecideOption(true, 'closed', candidate, 'rejected'), false)
  assert.equal(canDecideOption(true, 'decided', candidate, 'rejected'), false)
  const key = decisionKey('run-a', 'case-a', 'v1', 'o1')
  const decision = { key, action: 'approved' }
  assert.deepEqual(decisionForRecord(decision, 'run-a', 'case-a', 'v1'), decision)
  assert.equal(decisionForRecord(decision, 'run-b', 'case-a', 'v1'), null, 'changing runs clears the visible decision')
  assert.equal(decisionForRecord(decision, 'run-a', 'case-a', 'v2'), null, 'changing case version clears the visible decision')
  assert.notEqual(key, decisionKey('run-b', 'case-a', 'v1', 'o1'))
  assert.notEqual(key, decisionKey('run-a', 'case-b', 'v1', 'o1'))
  assert.notEqual(key, decisionKey('run-a', 'case-a', 'v2', 'o1'))
  assert.notEqual(key, decisionKey('run-a', 'case-a', 'v1', 'o2'))
})
