import test from 'node:test'
import assert from 'node:assert/strict'
import { canSimulateDecision } from '../src/sections/caseDecision.ts'

test('only fixture runs can simulate rejection, and terminal cases cannot', () => {
  assert.equal(canSimulateDecision(true, 'open', 'rejected'), true)
  assert.equal(canSimulateDecision(false, 'open', 'rejected'), false)
  assert.equal(canSimulateDecision(true, 'closed', 'rejected'), false)
  assert.equal(canSimulateDecision(true, 'decided', 'rejected'), false)
})

test('approval stays disabled until an option and checks can be reviewed', () => {
  assert.equal(canSimulateDecision(true, 'action_proposed', 'approved'), false)
  assert.equal(canSimulateDecision(false, 'action_proposed', 'approved'), false)
})
