import type { ArtifactRef, Case, RunView } from '../api/client'

// PLT-11 (#112) owns the API and generated types. These are its wire contracts
// until that API is merged; schema.d.ts must only be changed by make types.
export type Citation = {
  ref: ArtifactRef
  field?: string | null
  unit?: string | null
  scope?: Record<string, string> | null
  period_start?: string | null
  period_end?: string | null
}
export type Report = {
  id: string
  version: string
  run_id: string
  scenario_id: string
  as_of: string
  view: string
  markdown: string
  citations: Citation[]
  generated_by: string
  input_version_hash: string
}
export type ResolvedCitation = { citation: Citation; artifact: Record<string, unknown> }
export type ReportDetail = { report: Report; citations: ResolvedCitation[] }
export type Reader = <T>(path: string, signal: AbortSignal) => Promise<T>

const sameRef = (a: ArtifactRef, b: ArtifactRef) =>
  a.kind === b.kind && a.id === b.id && a.version === b.version

export function runPath(run: RunView, resource: string) {
  return `/runs/${encodeURIComponent(run.spec.run_id)}/${resource}${resource.includes('?') ? '&' : '?'}fixture=${run.namespace === 'fixture'}`
}

export function reportOwners(report: Report, cases: Case[]) {
  return [...new Set(report.citations.flatMap(({ ref }) =>
    ref.kind === 'Case'
      ? cases.filter((item) => item.id === ref.id && item.version === ref.version).map((item) => item.owner)
      : []
  ))].sort()
}

export function belongsToRun(report: Report, run: RunView) {
  return report.run_id === run.spec.run_id && report.scenario_id === run.spec.scenario_id &&
    Date.parse(report.as_of) === Date.parse(run.spec.as_of)
}

export async function loadReports(run: RunView, signal: AbortSignal, read: Reader) {
  const [reports, cases] = await Promise.all([
    read<Report[]>(runPath(run, 'reports'), signal),
    read<Case[]>(runPath(run, 'cases'), signal)
  ])
  if (reports.some((report) => !belongsToRun(report, run)))
    throw new Error('Il brief ricevuto non appartiene al run selezionato.')
  return { reports, cases }
}

export async function resolveReportCitation(
  run: RunView, report: Report, cases: Case[], index: number,
  signal: AbortSignal, read: Reader
): Promise<ResolvedCitation> {
  const citation = report.citations[index]
  const owner = reportOwners(report, cases)[0]
  if (!citation || !owner || !belongsToRun(report, run))
    throw new Error('Riferimento non risolvibile nel run selezionato.')
  const details = await read<ReportDetail[]>(runPath(run,
    `reports/${encodeURIComponent(owner)}?view=${encodeURIComponent(report.view)}`), signal)
  const detail = details.find(({ report: item }) => item.id === report.id && item.version === report.version)
  const resolved = detail?.citations[index]
  if (!detail || !belongsToRun(detail.report, run) ||
      detail.report.input_version_hash !== report.input_version_hash ||
      detail.report.markdown !== report.markdown || !resolved ||
      !sameRef(resolved.citation.ref, citation.ref) ||
      resolved.artifact.id !== citation.ref.id || resolved.artifact.version !== citation.ref.version ||
      resolved.artifact.run_id !== run.spec.run_id || resolved.artifact.scenario_id !== run.spec.scenario_id)
    throw new Error('La citazione o la sua versione non è disponibile nello stesso run.')
  return { citation, artifact: resolved.artifact }
}

// Render only the template's strong text and numbered citations. Everything
// else stays escaped text: email content cannot introduce HTML or URLs.
export function briefTokens(text: string, citationCount: number) {
  return text.split(/(\*\*[^*]+\*\*|\[\d+\])/g).filter(Boolean).map((value) => {
    const number = /^\[(\d+)\]$/.exec(value)
    if (number && Number(number[1]) >= 1 && Number(number[1]) <= citationCount)
      return { kind: 'citation' as const, value, index: Number(number[1]) - 1 }
    if (value.startsWith('**') && value.endsWith('**'))
      return { kind: 'strong' as const, value: value.slice(2, -2) }
    return { kind: 'text' as const, value }
  })
}

export function citedValue(artifact: Record<string, unknown>, field?: string | null): unknown {
  if (!field) return undefined
  const walk = (value: unknown, path: string[]): unknown => {
    if (!path.length) return value
    if (Array.isArray(value)) return value.map((item) => walk(item, path))
    if (!value || typeof value !== 'object' || !Object.hasOwn(value, path[0])) return undefined
    return walk((value as Record<string, unknown>)[path[0]], path.slice(1))
  }
  return walk(artifact, field.split('.'))
}
