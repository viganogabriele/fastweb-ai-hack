import type { components, operations } from './schema'
import type { ArtifactRef, Case } from './client'

export type ForecastAdjustment = components['schemas']['ForecastAdjustment']
type ForecastQuery = NonNullable<operations['forecast_api_runs__run_id__forecast_get']['parameters']['query']>
export type ForecastSelection = { item: Case; runId: string; fixtureMode: boolean }
export type ForecastData = { baselines: ForecastAdjustment[]; overlays: { forecast: ForecastAdjustment; baseline: ForecastAdjustment | null }[]; unresolved: number }
export type ForecastState = { status: 'loading' | 'empty' | 'unavailable' | 'error'; message?: string } | { status: 'ready'; data: ForecastData }
export type ForecastReader = <T>(path: string, signal: AbortSignal) => Promise<T>

const sameRef = (a: ArtifactRef | null, b: ArtifactRef | null) =>
  a === null || b === null ? a === b : a.kind === b.kind && a.id === b.id && a.version === b.version
const matchesRef = (ref: ArtifactRef, kind: string, item: { id: string; version: string }) =>
  sameRef(ref, { kind, id: item.id, version: item.version })

// Scope identifiers follow the repository's SKU / SKU-size convention. Never
// guess a colour for style cases; the response can contain several exact SKUs.
export function caseSku(item: Case) {
  if (item.scope_level === 'sku') return item.scope_id ?? null
  if (item.scope_level === 'sku_size') {
    const separator = item.scope_id?.lastIndexOf('-') ?? -1
    return separator > 0 ? item.scope_id!.slice(0, separator) : null
  }
  return null
}
export function forecastPath({ item, runId, fixtureMode }: ForecastSelection) {
  const query: ForecastQuery = { fixture: fixtureMode, store: item.store_id, sku: caseSku(item) }
  const params = new URLSearchParams({ fixture: String(query.fixture) })
  if (query.store) params.set('store', query.store)
  if (query.sku) params.set('sku', query.sku)
  return `/runs/${encodeURIComponent(runId)}/forecast?${params}`
}
export function selectCaseForecast(records: ForecastAdjustment[], { item, runId }: ForecastSelection): ForecastData {
  const sku = caseSku(item)
  const scoped = records.filter((record) => record.run_id === runId && item.run_id === runId &&
    record.scenario_id === item.scenario_id && record.store_id === item.store_id &&
    (sku ? record.sku === sku : item.scope_level === 'style' && record.sku.startsWith(`${item.scope_id}-`)))
  const baselines = scoped.filter((record) => record.producer === 'fc.baseline' && record.case_ids.length === 0)
  let unresolved = 0
  const overlays = scoped.filter((record) => {
    if (record.producer !== 'fc.overlay' || !record.case_ids.includes(item.id)) return false
    const refs = record.input_refs.filter((ref) => ref.kind === 'Case' && ref.id === item.id)
    if (refs.length !== 1 || !matchesRef(refs[0], 'Case', item)) { unresolved++; return false }
    return true
  }).map((forecast) => {
    const refs = forecast.input_refs.filter((ref) => ref.kind === 'ForecastAdjustment')
    const candidates = baselines.filter((base) => refs.length === 1 && matchesRef(refs[0], 'ForecastAdjustment', base) &&
      base.sku === forecast.sku && base.horizon_start === forecast.horizon_start && base.horizon_end === forecast.horizon_end &&
      sameRef(base.baseline_ref, forecast.baseline_ref))
    const baseline = candidates.length === 1 ? candidates[0] : null
    if (!baseline) unresolved++
    return { forecast, baseline }
  })
  return { baselines, overlays, unresolved }
}

// The cancellation guard also protects against readers that ignore AbortSignal.
// The component mounts this request inside a selection-keyed child, clearing
// the previous snapshot synchronously when the selection changes.
export function requestCaseForecast(selection: ForecastSelection, read: ForecastReader, publish: (state: ForecastState) => void) {
  const controller = new AbortController()
  const { item, runId } = selection
  if (!item.store_id || (!caseSku(item) && item.scope_level !== 'style') || item.run_id !== runId) {
    publish({ status: 'unavailable', message: 'Forecast non disponibile: negozio o ambito SKU non risolto nel run selezionato.' })
  } else {
    publish({ status: 'loading' })
    void read<ForecastAdjustment[]>(forecastPath(selection), controller.signal).then((records) => {
      if (controller.signal.aborted) return
      const data = selectCaseForecast(records, selection)
      publish(data.baselines.length || data.overlays.length ? { status: 'ready', data }
        : data.unresolved ? { status: 'unavailable', message: 'Gli overlay pubblicati non riferiscono la versione selezionata del caso.' }
          : { status: 'empty', message: 'Nessun forecast pubblicato per questo caso e SKU.' })
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) publish({ status: 'error', message: error instanceof Error ? error.message : 'Errore API forecast.' })
    })
  }
  return () => controller.abort()
}
