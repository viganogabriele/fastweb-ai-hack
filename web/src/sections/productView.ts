import type { Case } from '../api/client'
import { latestCaseVersions } from './caseUtils.ts'

export const productScopes = {
  sku_size: 'SKU e taglia',
  sku: 'SKU',
  style: 'Stile'
} as const

export type ProductScope = keyof typeof productScopes
export type ProductGroup = {
  key: string
  id: string
  level: ProductScope
  cases: Case[]
  stores: string[]
}

export const caseStatuses: Record<Case['status'], string> = {
  open: 'Aperto', verify: 'Da verificare', monitor: 'Monitoraggio',
  action_proposed: 'Azione proposta', decided: 'Deciso', closed: 'Chiuso'
}

const caseTypeLabels: Record<string, string> = {
  unmet_demand: 'Domanda non soddisfatta',
  demand_up: 'Aumento della domanda',
  demand_down: 'Calo della domanda',
  demand_shift: 'Variazione della domanda',
  stockout: 'Prodotto esaurito',
  low_stock: 'Scorte basse',
  stock_discrepancy: 'Discrepanza di magazzino',
  product_feedback: 'Feedback sul prodotto',
  traffic_change: 'Variazione del traffico',
  customer_profile: 'Profilo cliente',
  operational_issue: 'Problema operativo',
  sales_figure: 'Dato di vendita',
  local_event: 'Evento locale',
  other: 'Altro'
}

export function caseTypeLabel(value: string) {
  return caseTypeLabels[value] ?? value.replaceAll('_', ' ')
}

// Group only explicitly identified product scopes. A category or ambiguous
// mention must never silently become a SKU, nor may a size be inferred.
export function productIndex(cases: Case[], runId: string) {
  const current = latestCaseVersions(cases.filter((item) => item.run_id === runId))
  const groups = new Map<string, ProductGroup>()
  const unresolved: Case[] = []
  for (const item of current) {
    if (!item.scope_id?.trim() || !Object.hasOwn(productScopes, item.scope_level)) {
      unresolved.push(item)
      continue
    }
    const level = item.scope_level as ProductScope
    const key = JSON.stringify([level, item.scope_id])
    let group = groups.get(key)
    if (!group) {
      group = { key, id: item.scope_id, level, cases: [], stores: [] }
      groups.set(key, group)
    }
    group.cases.push(item)
    if (item.store_id && !group.stores.includes(item.store_id)) group.stores.push(item.store_id)
  }
  return {
    groups: [...groups.values()].sort((a, b) => a.id.localeCompare(b.id) || a.level.localeCompare(b.level)),
    unresolved
  }
}

export type ProductFilters = { search: string; store: string; status: string; type: string }

export function filterProductCases(cases: Case[], filters: ProductFilters) {
  const query = filters.search.trim().toLocaleLowerCase('it-IT')
  return cases.filter((item) =>
    (filters.store === 'all' || item.store_id === filters.store) &&
    (filters.status === 'all' || item.status === filters.status) &&
    (filters.type === 'all' || item.case_type === filters.type) &&
    [item.scope_id, item.store_id, item.case_type, item.priority_reason, item.owner]
      .join(' ').toLocaleLowerCase('it-IT').includes(query)
  )
}
