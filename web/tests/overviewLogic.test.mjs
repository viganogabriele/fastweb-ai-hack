import assert from 'node:assert/strict'
import { test } from 'node:test'
import { compareDeadlines, deadline } from '../src/sections/overviewLogic.ts'

const cutoff = Date.parse('2026-10-22T21:00:00Z')
test('deadline classification preserves sub-hour expiry and exact 48-hour boundary', () => {
  assert.equal(deadline('2026-10-22T20:59:59Z', cutoff).tone, 'past')
  assert.equal(deadline('2026-10-22T21:00:01Z', cutoff).text, '1 h')
  assert.equal(deadline('2026-10-24T21:00:00Z', cutoff).tone, 'soon')
  assert.equal(deadline('2026-10-24T21:00:01Z', cutoff).tone, 'later')
  assert.equal(deadline(null, cutoff).tone, 'none')
})
test('deadline sorting compares instants across offsets, with missing deadlines last', () => {
  const earlier = '2026-10-23T10:00:00+02:00'
  const later = '2026-10-23T09:00:00Z'
  assert.deepEqual([null, later, earlier].sort(compareDeadlines), [earlier, later, null])
  assert.equal(compareDeadlines(earlier, '2026-10-23T08:00:00Z'), 0)
})
