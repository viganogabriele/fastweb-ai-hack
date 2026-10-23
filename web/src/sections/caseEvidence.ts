import type { Case, DocumentDetail } from '../api/client'

export type CaseQuote = {
  key: string
  relation: 'supporting' | 'contradicting'
  quote: string
  kind: string
  document: DocumentDetail['document']
}

/**
 * The verified quotes behind a case: evidence of the observations it cites as supporting or
 * contradicting, matched by exact kind, id and version. Same quote twice is shown once.
 */
export function caseQuotes(item: Pick<Case, 'supporting' | 'contradicting'>, details: DocumentDetail[]): CaseQuote[] {
  const relation = new Map<string, CaseQuote['relation']>()
  for (const ref of item.supporting) relation.set(`${ref.kind}:${ref.id}:${ref.version}`, 'supporting')
  for (const ref of item.contradicting) relation.set(`${ref.kind}:${ref.id}:${ref.version}`, 'contradicting')
  const seen = new Set<string>()
  const quotes: CaseQuote[] = []
  for (const detail of details)
    for (const observation of detail.observations) {
      const found = relation.get(`Observation:${observation.id}:${observation.version}`)
      if (!found) continue
      for (const evidence of observation.evidence) {
        const key = `${found}:${evidence.document_id}:${evidence.char_start}:${evidence.quote}`
        if (seen.has(key) || !evidence.quote.trim()) continue
        seen.add(key)
        quotes.push({ key, relation: found, quote: evidence.quote, kind: observation.kind, document: detail.document })
      }
    }
  return quotes.sort((a, b) => (a.relation === b.relation ? 0 : a.relation === 'supporting' ? -1 : 1))
}
