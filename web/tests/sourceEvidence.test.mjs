import assert from 'node:assert/strict'
import test from 'node:test'
import { evidenceRanges } from '../src/sections/sourceEvidence.ts'

const document = { id: 'doc-1', version: 'v1' }
function item(quote, char_start, char_end, overrides = {}) {
  return {
    caseId: 'case-1',
    caseType: 'unmet_demand',
    relation: 'supporting',
    evidence: {
      document_id: 'doc-1',
      document_version: 'v1',
      segment_id: 'segment-1',
      quote,
      char_start,
      char_end
    },
    ...overrides
  }
}

test('converts code-point offsets after emoji to UTF-16 indexes without changing text', () => {
  const text = 'A🧥東京を確認'
  const ranges = evidenceRanges(text, document, [item('東京', 2, 4)])

  assert.deepEqual(ranges.map(({ start, end }) => [start, end]), [[3, 5]])
  assert.equal(text.slice(ranges[0].start, ranges[0].end), '東京')
  assert.equal(text, 'A🧥東京を確認')
})

test('keeps supporting and contradicting references across overlapping spans', () => {
  const text = 'A🧥東京を確認'
  const ranges = evidenceRanges(text, document, [
    item('東京を', 2, 5),
    item('京を確認', 3, 7, {
      caseId: 'case-2',
      relation: 'contradicting'
    })
  ])

  assert.deepEqual(
    ranges.map(({ start, end, relation, references }) => [
      start,
      end,
      relation,
      references.map(({ caseId }) => caseId)
    ]),
    [
      [3, 4, 'supporting', ['case-1']],
      [4, 6, 'mixed', ['case-1', 'case-2']],
      [6, 8, 'contradicting', ['case-2']]
    ]
  )
  assert.equal(ranges.map(({ start, end }) => text.slice(start, end)).join(''), '東京を確認')
})

test('ignores stale versions and quotes that do not match canonical text', () => {
  const text = 'A🧥東京'
  const ranges = evidenceRanges(text, document, [
    item('東京', 2, 4),
    item('東京', 2, 4, {
      caseId: 'stale',
      evidence: { ...item('東京', 2, 4).evidence, document_version: 'v0' }
    }),
    item('京都', 2, 4, { caseId: 'mismatch' })
  ])

  assert.equal(ranges.length, 1)
  assert.deepEqual(ranges[0].references.map(({ caseId }) => caseId), ['case-1'])
})
