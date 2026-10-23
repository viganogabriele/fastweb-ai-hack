// Module result counts are free-form keys chosen by each module. This turns them into a few
// readable metrics: `<x>_rows` / `<x>_new` pairs merge into one, labels become Italian words.

export type ModuleMetric = { key: string; label: string; value: number; fresh: number | null }

const phrases: Record<string, string> = {
  sku_colour: 'SKU colore', sku_size_ean: 'SKU taglia', not_estimable: 'non stimabili', not_product: 'non prodotto',
  possibly_same_episode: 'stesso episodio possibile', optional_fields_dropped: 'campi opzionali scartati',
  numbers_dropped: 'numeri scartati', candidates_rejected: 'candidati scartati', documents_unmapped: 'documenti non mappati',
  rows_outside_run: 'righe fuori dal run', rows_unknown_scope: 'righe senza ambito', no_case_kind: 'senza tipo di caso',
  inactive_facts: 'fatti inattivi', negated_unattached: 'negazioni non collegate', stale_snapshots: 'snapshot scaduti',
  non_additive_origins: 'origini non sommabili', transfers_recommended: 'trasferimenti consigliati', cases_verify: 'casi da verificare',
  scope_unknown: 'ambito sconosciuto', llm_linked: 'collegati da LLM', links_new: 'nuovi collegamenti', relations_new: 'nuove relazioni',
  stock_facts: 'dati di stock', stock_facts_new: 'nuovi dati di stock', updated_cases: 'casi aggiornati', reports_new: 'nuovi report'
}
const words: Record<string, string> = {
  documents: 'documenti', segments: 'segmenti', sheets: 'fogli', skipped: 'saltati', observations: 'osservazioni', cases: 'casi',
  options: 'opzioni', transfers: 'trasferimenti', traces: 'indagini', fallbacks: 'fallback', baselines: 'baseline', unchanged: 'invariati',
  overlays: 'overlay', computed: 'calcolati', events: 'eventi', cities: 'città', reports: 'report', citations: 'citazioni',
  linked: 'collegati', unlinked: 'non collegati', ambiguous: 'ambigui', duplicates: 'duplicati', supersedes: 'sostituzioni',
  retracts: 'ritrattazioni', facts: 'fatti', requests: 'richieste', unknown: 'sconosciuti', stores: 'negozi', styles: 'stili',
  assortment: 'assortimento', prices: 'prezzi', sales: 'vendite', returns: 'resi', stock: 'stock', forecast: 'previsioni',
  origin: 'origine', origins: 'origini', active: 'attive', unknown_origins: 'origini sconosciute', origin_groups: 'gruppi di origine',
  active_origins: 'origini attive', new: 'nuovi'
}
export const countLabel = (key: string) => phrases[key] ?? words[key] ?? key.split('_').map((word) => words[word] ?? word).join(' ')

export function moduleMetrics(counts: Record<string, number>): ModuleMetric[] {
  const entries = Object.entries(counts)
  const keys = new Set(entries.map(([key]) => key))
  const metrics: ModuleMetric[] = []
  for (const [key, value] of entries) {
    if (key.endsWith('_new') && keys.has(`${key.slice(0, -4)}_rows`)) continue
    if (key.endsWith('_rows')) {
      const base = key.slice(0, -5)
      const fresh = counts[`${base}_new`]
      metrics.push({ key: base, label: countLabel(base), value, fresh: fresh === undefined || fresh === value ? null : fresh })
      continue
    }
    metrics.push({ key, label: countLabel(key), value, fresh: null })
  }
  return metrics
}

// Diagnostic counters (what was dropped, skipped or left unresolved) never take a headline slot.
const diagnostic = /(^|_)(unmapped|unlinked|unattached|unresolved|unknown|not|no|non|outside|dropped|rejected|skipped|stale|inactive|negated|ambiguous|fallbacks|possibly)(_|$)/
export const isDiagnostic = (key: string) => diagnostic.test(key)

/** The module's first non-zero outputs lead; diagnostics and the rest (zeros last) go in the detail list. */
export function splitMetrics(metrics: ModuleMetric[], lead = 3) {
  const primary = metrics.filter((metric) => metric.value !== 0 && !isDiagnostic(metric.key)).slice(0, lead)
  const rest = metrics.filter((metric) => !primary.includes(metric))
  return { primary, rest: [...rest.filter((metric) => metric.value !== 0), ...rest.filter((metric) => metric.value === 0)] }
}
