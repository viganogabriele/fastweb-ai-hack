import type { ArtifactRef, Evidence, SourceDocument } from '../api/client'

export interface CaseEvidence {
  caseId: string
  caseType: string
  relation: 'supporting' | 'contradicting'
  evidence: Evidence
}

export function refKey(ref: ArtifactRef): string {
  return `${ref.kind}:${ref.id}:${ref.version}`
}

export function evidenceRanges(
  text: string,
  document: SourceDocument,
  evidence: CaseEvidence[]
) {
  const points = Array.from(text)
  return evidence
    .filter(({ evidence: item }) =>
      item.document_id === document.id &&
      item.document_version === document.version &&
      item.char_start >= 0 &&
      item.char_end > item.char_start &&
      item.char_end <= points.length &&
      points.slice(item.char_start, item.char_end).join('') === item.quote
    )
    .map((item) => ({
      ...item,
      // Contract offsets count Unicode code points; String#slice counts UTF-16 units.
      start: points.slice(0, item.evidence.char_start).join('').length,
      end: points.slice(0, item.evidence.char_end).join('').length
    }))
    .sort((a, b) => a.start - b.start || a.end - b.end)
}
