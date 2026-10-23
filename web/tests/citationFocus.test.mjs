import test from 'node:test'
import assert from 'node:assert/strict'
import { closeCitationAndRestoreFocus } from '../src/sections/citationFocus.ts'

test('closing a citation restores focus to its trigger before removing the panel', () => {
  const calls = []
  const trigger = { focus: () => calls.push('focus trigger') }
  closeCitationAndRestoreFocus(trigger, () => calls.push('close panel'))
  assert.deepEqual(calls, ['focus trigger', 'close panel'])
})

test('closing a citation with no surviving trigger still closes the panel', () => {
  let closed = false
  closeCitationAndRestoreFocus(null, () => { closed = true })
  assert.equal(closed, true)
})
