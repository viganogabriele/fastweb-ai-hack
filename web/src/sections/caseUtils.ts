import type { Case } from '../api/client'

export type CaseSelection = { id: string; version: string }
export type CaseQueueFilters = {
  search: string
  store: string
  owner: string
  product: string
  priority: string
  deadline: string
  uncertainty: string
  status: string
  sort: string
}

export const DEFAULT_CASE_QUEUE_FILTERS: CaseQueueFilters = {
  search: '',
  store: 'all',
  owner: 'all',
  product: 'all',
  priority: 'all',
  deadline: 'all',
  uncertainty: 'all',
  status: 'all',
  sort: 'recent'
}

export function caseKey(item: Pick<Case, 'id' | 'version'>) {
  return `${item.id}\u0000${item.version}`
}

export function latestCaseVersions(cases: Case[]) {
  const latest = new Map<string, Case>()
  for (const item of cases) {
    const current = latest.get(item.id)
    if (
      !current ||
      item.version.localeCompare(current.version, undefined, {
          numeric: true
        }) > 0 ||
      (item.version === current.version &&
        Date.parse(item.computed_at) > Date.parse(current.computed_at))
    ) {
      latest.set(item.id, item)
    }
  }
  return [...latest.values()]
}

export function isPastDeadline(deadline: string | null | undefined, asOf: string) {
  if (!deadline || !asOf) return false
  const deadlineTime = Date.parse(deadline)
  const cutoffTime = Date.parse(asOf)
  return Number.isFinite(deadlineTime) && Number.isFinite(cutoffTime) && deadlineTime < cutoffTime
}

export function uncertaintyReasons(item: Case) {
  return [
    ...item.blocking_uncertainties,
    ...(item.scope_level === 'unknown'
      ? ['Il perimetro del prodotto non è ancora identificato.']
      : []),
    ...(item.n_unknown_origins > 0
      ? [`Origine non identificata per ${item.n_unknown_origins} documenti.`]
      : [])
  ]
}
