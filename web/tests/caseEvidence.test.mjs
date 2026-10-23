import assert from 'node:assert/strict'
import test from 'node:test'
import { caseQuotes } from '../src/sections/caseEvidence.ts'

const evidence = (quote, start = 0) => ({ document_id: 'doc-1', document_version: 'v1', segment_id: 's', char_start: start, char_end: start + quote.length, quote })
const observation = (id, quotes, version = 'v1') => ({ id, version, kind: 'unmet_demand', evidence: quotes.map((q, i) => evidence(q, i * 10)) })
const detail = (observations) => ({ document: { id: 'doc-1', source_type: 'email' }, segments: [], links: [], observations })
const ref = (id, version = 'v1') => ({ kind: 'Observation', id, version })

test('quotes come from the exact observations a case cites, supporting before contradicting', () => {
  const quotes = caseQuotes(
    { supporting: [ref('a')], contradicting: [ref('b')] },
    [detail([observation('b', ['no']), observation('a', ['5 richieste']), observation('c', ['altro'])])]
  )
  assert.deepEqual(quotes.map((q) => [q.relation, q.quote]), [['supporting', '5 richieste'], ['contradicting', 'no']])
})

test('a different version is not the cited observation, and repeated quotes show once', () => {
  const quotes = caseQuotes(
    { supporting: [ref('a', 'v2')], contradicting: [] },
    [detail([observation('a', ['vecchia'], 'v1')]), detail([observation('a', ['nuova'], 'v2')]), detail([observation('a', ['nuova'], 'v2')])]
  )
  assert.deepEqual(quotes.map((q) => q.quote), ['nuova'])
})
