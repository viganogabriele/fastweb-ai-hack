import assert from 'node:assert/strict'
import { test } from 'node:test'
import { canUseMicrophone, currentQuestion, isValidStaffCode, normalizeStaffCode, remainingTime } from '../src/store/guidedRecording.ts'
import { sendNote } from '../src/store/voiceApi.ts'

test('staff pseudonyms trim and lowercase, without removing invalid internal characters', () => {
  assert.equal(normalizeStaffCode('  STAFF-09  '), 'staff-09')
  for (const valid of ['a', '123', 'staff-09', 'a'.repeat(32)]) assert.ok(isValidStaffCode(valid))
  for (const invalid of ['', 'A', 'a b', 'à', 'a_b', 'a'.repeat(33), 'a\n']) assert.ok(!isValidStaffCode(invalid))
  assert.ok(!isValidStaffCode(normalizeStaffCode('  STAFF 09 ')))
})

test('microphone needs a valid code and access, and waits for permission', () => {
  assert.equal(canUseMicrophone('staff-09', true, false), true)
  assert.equal(canUseMicrophone('', true, false), false)
  assert.equal(canUseMicrophone('a b', true, false), false)
  assert.equal(canUseMicrophone('staff-09', false, false), false)
  assert.equal(canUseMicrophone('staff-09', true, true), false)
})

test('question emphasis changes every 15 seconds and loops without restricting speech', () => {
  for (const [seconds, index] of [[0, 0], [14, 0], [15, 1], [29, 1], [30, 2], [45, 3], [59, 3], [60, 0], [75, 1], [89, 1]]) {
    assert.equal(currentQuestion(seconds), index)
  }
})

test('remaining time counts down from 90 seconds and clamps at zero', () => {
  for (const [elapsed, display] of [[0, '1:30'], [1, '1:29'], [45, '0:45'], [89, '0:01'], [90, '0:00'], [100, '0:00'], [-1, '1:30']]) {
    assert.equal(remainingTime(elapsed), display)
  }
})

test('note upload includes staff and guided prompt set alongside existing fields and accepts 201', async (t) => {
  const before = Object.getOwnPropertyDescriptor(globalThis, 'window')
  Object.defineProperty(globalThis, 'window', { configurable: true, value: { location: { hash: '#voice-token=fake' } } })
  t.after(() => before ? Object.defineProperty(globalThis, 'window', before) : delete globalThis.window)
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/voice/notes')
    assert.equal(options.body.get('staff_ref'), 'staff-09')
    assert.equal(options.body.get('prompt_set'), 'guided-v1')
    assert.equal(options.body.get('store_id'), 'MIL01')
    assert.equal(options.body.get('transcript'), 'Testo controllato')
    assert.equal(options.body.get('language'), 'it')
    assert.equal(options.body.get('audio').name, 'note.webm')
    return new Response(JSON.stringify({ note_id: 'test-note' }), { status: 201 })
  })
  assert.equal((await sendNote(new Blob(['audio'], { type: 'audio/webm' }), 'MIL01', 'Testo controllato', 'it', 'staff-09')).note_id, 'test-note')
})
