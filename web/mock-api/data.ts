/**
 * Synthetic API responses for `npm run dev:mock`. Typed against the generated OpenAPI schema,
 * so a contract change breaks `tsc` here instead of silently drifting. Store ids and SKUs come
 * from `generated/sources/erp/master_data/` (style names as
 * renamed by DATA-04); every text, number and case is invented.
 */
import type { components } from '../src/api/schema.d.ts'

type S = components['schemas']
type Case = S['Case']
type SourceDocument = S['SourceDocument']
type Observation = S['Observation']
type ModuleManifest = S['ModuleManifest']
type RunView = S['RunView']
type DocumentDetail = S['DocumentDetail']

const AS_OF = '2026-10-22T21:00:00Z'
const COMPUTED = '2026-10-22T21:04:00Z'
// `fixture` lets the case detail show the hand-written examples in `src/mocks/caseDetails.ts`.
export const MAIN_RUN = 'fixture'
const STORES = ['MIL01', 'ROM01', 'CRT01', 'PAR01', 'GVA01', 'LON01', 'NYC01', 'TYO01']

const hours = (h: number) => new Date(Date.parse(AS_OF) + h * 3600_000).toISOString()
const hash = (seed: string) =>
  [...seed].reduce((acc, ch) => (acc * 31 + ch.charCodeAt(0)) >>> 0, 7).toString(16).padStart(8, '0')
const sourceRef = (uri: string): S['SourceRef'] => ({ uri, content_hash: hash(uri), locator: null })

// ── Modules ────────────────────────────────────────────────────────────────────────────────
const manifest = (
  id: string,
  layer: ModuleManifest['layer'],
  description: string,
  requires: string[],
  produces: string[],
  mode: ModuleManifest['mode'] = 'recorded'
): ModuleManifest => ({
  id,
  layer,
  description,
  requires,
  produces,
  mode,
  enabled: true,
  version: '0.4.0',
  optional_inputs: [],
  params_schema: {}
})

export const MODULES: ModuleManifest[] = [
  manifest('src.email', 'sources', 'Email di chiusura dei negozi', [], ['SourceDocument'], 'fixture'),
  manifest('src.voice', 'sources', 'Note vocali trascritte', [], ['SourceDocument'], 'fixture'),
  manifest('ing.segment', 'ingestion', 'Segmentazione e lingua', ['src.email'], ['Segment']),
  manifest('ing.extract', 'ingestion', 'Estrazione osservazioni', ['ing.segment'], ['Observation']),
  manifest('int.link', 'integration', 'Collegamento a SKU e taglia', ['ing.extract'], ['EntityLink']),
  manifest('int.cases', 'integration', 'Casi per negozio, prodotto e finestra', ['int.link'], ['Case']),
  manifest('fc.overlay', 'intelligence', 'Correzione del forecast a breve', ['int.cases'], ['ForecastOverlay']),
  manifest('act.options', 'actions', 'Opzioni di stock con controlli', ['fc.overlay'], ['ActionOption']),
  manifest('ag.investigator', 'agents', 'Agente investigatore', ['int.cases'], ['AgentTrace']),
  manifest('out.reports', 'outputs', 'Brief per ufficio', ['int.cases'], ['Report'])
]

const moduleRuns = (runId: string, degraded: string[] = []): S['ModuleRun'][] =>
  MODULES.map((item, index) => {
    const status = degraded.includes(item.id) ? 'degraded' : 'succeeded'
    return {
      run_id: runId,
      module_id: item.id,
      mode: item.mode,
      status,
      started_at: hours(index * 0.02),
      finished_at: hours(index * 0.02 + 0.015),
      result: {
        module_id: item.id,
        module_version: item.version,
        status,
        counts: { [item.produces[0] ?? 'items']: 12 + index * 7 },
        errors: [],
        abstentions: status === 'degraded' ? ['2 documenti senza lingua riconosciuta'] : []
      }
    }
  })

const spec = (runId: string, asOf: string, stores = STORES): S['RunSpec'] => ({
  run_id: runId,
  as_of: asOf,
  stores,
  mode: 'fixture',
  scenario_id: 'dev',
  schema_version: '1.0',
  code_version: 'mock',
  config_hash: hash(runId),
  source_manifest_hash: hash(`${runId}-sources`),
  authorized_fixture_refs: [],
  model_versions: { extract: 'Qwen/Qwen3.8-27B-FP8' },
  prompt_versions: { extract: 'v3' },
  modules: MODULES.map((item) => ({ manifest: item, params: {} }))
})

export const RUNS: RunView[] = [
  { spec: spec(MAIN_RUN, AS_OF), namespace: 'fixture', published: true, status: 'succeeded', module_runs: moduleRuns(MAIN_RUN) },
  {
    spec: spec('mock-2026-10-21', '2026-10-21T21:00:00Z', STORES.slice(0, 6)),
    namespace: 'fixture',
    published: true,
    status: 'degraded',
    module_runs: moduleRuns('mock-2026-10-21', ['ing.segment'])
  },
  {
    spec: spec('mock-2026-10-23', '2026-10-23T21:00:00Z'),
    namespace: 'fixture',
    published: false,
    status: 'running',
    module_runs: []
  }
]

// ── Documents ──────────────────────────────────────────────────────────────────────────────
type DocSeed = { id: string; store: string; lang: string; type: SourceDocument['source_type']; at: number; text: string }

const DOC_SEEDS: DocSeed[] = [
  {
    id: 'doc-mil01-20261022', store: 'MIL01', lang: 'it', type: 'email', at: -3,
    text: 'Oggetto: Chiusura MIL01 22/10\n\nGiornata intensa. Sette clienti hanno chiesto il AUREA nero in 2 e 3, che non abbiamo più dal weekend. Due hanno lasciato il numero. Il ARIA bianco latte invece resta fermo, nessuna richiesta.\nLa vetrina nuova attira molto traffico la sera.\n\nGiulia'
  },
  {
    id: 'doc-rom01-20261022', store: 'ROM01', lang: 'it', type: 'email', at: -2.5,
    text: 'Chiusura ROM01.\nIl sistema segna 4 FIAMMETTA nero in taglia 1 ma in magazzino ne contiamo solo 1: probabile errore di ricevimento. Chiediamo verifica prima di qualsiasi trasferimento.\nCalo di turisti americani rispetto alla settimana scorsa.'
  },
  {
    id: 'doc-par01-20261022', store: 'PAR01', lang: 'fr', type: 'email', at: -4,
    text: 'Bonjour à tous,\nForte demande sur le BRUNEA rouge : plusieurs clientes l’ont demandé aujourd’hui, surtout en taille 0. Il nous en reste un seul.\nLe salon privé était complet tout l’après-midi.\nCamille'
  },
  {
    id: 'doc-lon01-20261022', store: 'LON01', lang: 'en', type: 'email', at: -1,
    text: 'Closing notes LON01\nThree customers returned the VTRACK GTX this week, all citing the sole peeling after a few days. Flagging to product quality.\nFootfall was steady, slightly below last Thursday.'
  },
  {
    id: 'doc-nyc01-20261022', store: 'NYC01', lang: 'en', type: 'voice_note', at: -2,
    text: 'Hey team, quick one from Madison. A VIP asked for "that long navy parka from the campaign", we couldn’t tell which style. She is coming back Saturday. Also the scarf table is almost empty, lots of people asking for the beige cashmere.'
  },
  {
    id: 'doc-crt01-20261022', store: 'CRT01', lang: 'it', type: 'email', at: -5,
    text: 'Cortina, chiusura del 22.\nCon la prima neve è ripartita la domanda di MISTRAL nero: 5 richieste in giornata, ne abbiamo 2. Previsto pienone nel fine settimana per l’apertura degli impianti.'
  },
  {
    id: 'doc-gva01-20261022', store: 'GVA01', lang: 'fr', type: 'email', at: -2,
    text: 'Genève, clôture.\nLe VLOGO HOODIE noir part très vite, 6 ventes aujourd’hui. Rien à signaler sur les vestes. Panne du terminal de paiement pendant une heure le matin.'
  },
  {
    id: 'doc-tyo01-20261022', store: 'TYO01', lang: 'ja', type: 'chat_message', at: -9,
    text: '銀座店より：ASTRA BALACLAVA 白の問い合わせが多いです。在庫は残り3点。週末に向けて追加をご検討ください。'
  }
]

export const DOCUMENTS: SourceDocument[] = DOC_SEEDS.map((seed) => ({
  id: seed.id,
  version: 'v1',
  text: seed.text,
  text_version: 'v1',
  language: seed.lang,
  source_type: seed.type,
  connector: seed.type === 'email' ? 'imap' : seed.type === 'voice_note' ? 'asr' : 'chat',
  uri: `mock://${seed.store.toLowerCase()}/${seed.id}`,
  content_hash: hash(seed.text),
  origin: `store:${seed.store}`,
  author_ref: `${seed.store.toLowerCase()}.store`,
  available_at: hours(seed.at),
  availability_basis: 'received_at',
  business_date: '2026-10-22',
  thread_key: null,
  parent_document_id: null,
  event_start: null,
  event_end: null,
  meta: { store_id: seed.store },
  source_refs: [sourceRef(`mock://${seed.store.toLowerCase()}/${seed.id}`)]
}))

// ── Observations: each quote is located in its document by code-point offset ───────────────
type ObsSeed = { id: string; doc: string; kind: Observation['kind']; quote: string; product?: string; value?: number }

const OBS_SEEDS: ObsSeed[] = [
  { id: 'obs-mil01-maire', doc: 'doc-mil01-20261022', kind: 'unmet_demand', quote: 'Sette clienti hanno chiesto il AUREA nero in 2 e 3', product: 'AUREA nero', value: 7 },
  { id: 'obs-mil01-bady', doc: 'doc-mil01-20261022', kind: 'demand_down', quote: 'Il ARIA bianco latte invece resta fermo', product: 'ARIA bianco latte' },
  { id: 'obs-rom01-fiam', doc: 'doc-rom01-20261022', kind: 'stock_discrepancy', quote: 'Il sistema segna 4 FIAMMETTA nero in taglia 1 ma in magazzino ne contiamo solo 1', product: 'FIAMMETTA nero', value: 3 },
  { id: 'obs-par01-brunea', doc: 'doc-par01-20261022', kind: 'unmet_demand', quote: 'Forte demande sur le BRUNEA rouge', product: 'BRUNEA rosso' },
  { id: 'obs-lon01-vtrack', doc: 'doc-lon01-20261022', kind: 'product_feedback', quote: 'Three customers returned the VTRACK GTX this week', product: 'VTRACK GTX', value: 3 },
  { id: 'obs-nyc01-parka', doc: 'doc-nyc01-20261022', kind: 'unmet_demand', quote: 'that long navy parka from the campaign', product: 'long navy parka' },
  { id: 'obs-nyc01-scarf', doc: 'doc-nyc01-20261022', kind: 'low_stock', quote: 'the scarf table is almost empty', product: 'VALENTINO SCARF beige' },
  { id: 'obs-crt01-mistral', doc: 'doc-crt01-20261022', kind: 'unmet_demand', quote: '5 richieste in giornata, ne abbiamo 2', product: 'MISTRAL nero', value: 5 },
  { id: 'obs-gva01-hoodie', doc: 'doc-gva01-20261022', kind: 'demand_up', quote: 'Le VLOGO HOODIE noir part très vite', product: 'VLOGO HOODIE nero', value: 6 },
  { id: 'obs-gva01-pos', doc: 'doc-gva01-20261022', kind: 'operational_issue', quote: 'Panne du terminal de paiement pendant une heure' },
  { id: 'obs-tyo01-bala', doc: 'doc-tyo01-20261022', kind: 'unmet_demand', quote: 'ASTRA BALACLAVA 白の問い合わせが多いです', product: 'ASTRA BALACLAVA bianco' }
]

const documentById = new Map(DOCUMENTS.map((item) => [item.id, item]))

export const OBSERVATIONS: Observation[] = OBS_SEEDS.map((seed) => {
  const document = documentById.get(seed.doc)!
  const points = Array.from(document.text)
  const start = Array.from(document.text.slice(0, document.text.indexOf(seed.quote))).length
  if (points.slice(start, start + Array.from(seed.quote).length).join('') !== seed.quote)
    throw new Error(`mock quote not found: ${seed.id}`)
  return {
    id: seed.id,
    version: 'v1',
    run_id: MAIN_RUN,
    scenario_id: 'dev',
    document_id: document.id,
    store_id: String(document.meta.store_id),
    kind: seed.kind,
    direction: seed.kind === 'demand_down' ? 'down' : 'up',
    negated: false,
    attribution: 'store_staff',
    product_mention: seed.product ?? null,
    quantity: seed.value
      ? { kind: 'exact', value: seed.value, unit: 'customers', raw: String(seed.value) }
      : { kind: 'vague', raw: null },
    evidence: [{
      document_id: document.id,
      document_version: document.version,
      segment_id: `${document.id}-s1`,
      quote: seed.quote,
      char_start: start,
      char_end: start + Array.from(seed.quote).length
    }],
    extractor_version: 'mock',
    producer: 'ing.extract',
    producer_version: '0.4.0',
    available_at: document.available_at,
    availability_basis: 'derived',
    computed_at: COMPUTED,
    input_refs: [],
    source_refs: document.source_refs
  }
})

// ── Cases ──────────────────────────────────────────────────────────────────────────────────
type CaseSeed = {
  id: string
  store: string | null
  scope: string | null
  level: Case['scope_level']
  type: string
  owner: string
  priority: Case['priority']
  status: Case['status']
  reason: string
  due: number | null
  obs?: string[]
  contra?: string[]
  docs?: number
  origins?: number
  uncertain?: string[]
}

const CASE_SEEDS: CaseSeed[] = [
  // The two ids below match `src/mocks/caseDetails.ts`, so their detail shows forecast and options.
  { id: 'case-mil01-j20931a00012-999-20261002', store: 'MIL01', scope: 'J20931A00012-999', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'critical', status: 'action_proposed', reason: 'Sette richieste non servite in un giorno su uno SKU a zero stock, flagship.', due: 14, obs: ['obs-mil01-maire'], docs: 2, origins: 2 },
  { id: 'case-nyc01-unknown-20260906', store: 'NYC01', scope: null, level: 'unknown', type: 'unmet_demand', owner: 'allocation', priority: 'high', status: 'verify', reason: 'Cliente VIP di ritorno sabato; prodotto descritto ma non identificato.', due: 30, obs: ['obs-nyc01-parka'], uncertain: ['Quale parka blu della campagna? Due stili candidati.'] },
  { id: 'case-rom01-j20931a00203-999-fiam', store: 'ROM01', scope: 'J20931A00203-999-1', level: 'sku_size', type: 'stock_discrepancy', owner: 'retail_ops', priority: 'high', status: 'verify', reason: 'Stock ERP 4, conteggio fisico 1: blocca ogni trasferimento dal negozio.', due: 20, obs: ['obs-rom01-fiam'], uncertain: ['Conteggio fisico da confermare.'] },
  { id: 'case-par01-j20931a00410-41f-brunea', store: 'PAR01', scope: 'J20931A00410-41F', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'high', status: 'open', reason: 'Domanda forte in taglia 0, un solo capo residuo.', due: 40, obs: ['obs-par01-brunea'] },
  { id: 'case-crt01-j10911a00088-999-mistral', store: 'CRT01', scope: 'J10911A00088-999', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'critical', status: 'open', reason: 'Prima neve e apertura impianti: 5 richieste contro 2 capi.', due: 10, obs: ['obs-crt01-mistral'], docs: 1, origins: 1 },
  { id: 'case-lon01-i10914m00061-999-vtrack', store: 'LON01', scope: 'I10914M00061-999', level: 'sku', type: 'product_feedback', owner: 'product_quality', priority: 'medium', status: 'monitor', reason: 'Tre resi con lo stesso difetto della suola in una settimana.', due: 96, obs: ['obs-lon01-vtrack'] },
  { id: 'case-nyc01-i10913a00004-034-scarf', store: 'NYC01', scope: 'I10913A00004-034', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'medium', status: 'open', reason: 'Tavolo sciarpe quasi vuoto, richieste vaghe ma ripetute.', due: 60, obs: ['obs-nyc01-scarf'], uncertain: ['Quantità vaga ("lots of people").'] },
  { id: 'case-gva01-i10918g00031-999-hoodie', store: 'GVA01', scope: 'I10918G00031-999', level: 'sku', type: 'demand_shift', owner: 'merchandising', priority: 'medium', status: 'open', reason: 'Vendite sopra baseline per tre giorni consecutivi.', due: 72, obs: ['obs-gva01-hoodie'] },
  { id: 'case-tyo01-g20921a00903-001-bala', store: 'TYO01', scope: 'G20921A00903-001', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'high', status: 'open', reason: 'Molte richieste prima del weekend, 3 pezzi residui.', due: 26, obs: ['obs-tyo01-bala'] },
  { id: 'case-gva01-store-pos', store: 'GVA01', scope: 'GVA01', level: 'store', type: 'operational_issue', owner: 'retail_ops', priority: 'low', status: 'monitor', reason: 'Guasto POS di un’ora: possibile vendita persa non quantificabile.', due: null, obs: ['obs-gva01-pos'] },
  { id: 'case-mil01-j20931a00144-20d-bady', store: 'MIL01', scope: 'J20931A00144-20D', level: 'sku', type: 'demand_shift', owner: 'merchandising', priority: 'low', status: 'open', reason: 'Nessuna richiesta nonostante l’esposizione in vetrina.', due: 120, obs: ['obs-mil01-bady'] },
  { id: 'case-rom01-store-traffic', store: 'ROM01', scope: 'ROM01', level: 'store', type: 'traffic_change', owner: 'retail_ops', priority: 'low', status: 'closed', reason: 'Calo di turisti, già visibile nei dati di traffico.', due: null },
  { id: 'case-par01-j10911a00577-999-artem', store: 'PAR01', scope: 'J10911A00577-999', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'medium', status: 'decided', reason: 'Trasferimento da LON01 approvato ieri.', due: -6 },
  { id: 'case-lon01-j10911a00745-742-mario', store: 'LON01', scope: 'J10911A00745-742', level: 'sku', type: 'unmet_demand', owner: 'allocation', priority: 'medium', status: 'verify', reason: 'Una nota interna smentisce la richiesta registrata dal negozio.', due: 8, contra: ['obs-lon01-vtrack'], uncertain: ['Fonti in contrasto.'] }
]

const obsRef = (id: string): S['ArtifactRef'] => ({ kind: 'Observation', id, version: 'v1' })

export const CASES: Case[] = CASE_SEEDS.map((seed) => ({
  id: seed.id,
  version: 'v1',
  run_id: MAIN_RUN,
  scenario_id: 'dev',
  case_type: seed.type,
  store_id: seed.store,
  scope_level: seed.level,
  scope_id: seed.scope,
  status: seed.status,
  owner: seed.owner,
  priority: seed.priority,
  priority_reason: seed.reason,
  decision_due_at: seed.due === null ? null : hours(seed.due),
  window_start: '2026-10-20T00:00:00Z',
  window_end: '2026-10-29T00:00:00Z',
  first_available_at: hours(-30),
  last_received_at: hours(-2),
  last_independent_evidence_at: hours(-2),
  valid_until: hours(72),
  available_at: hours(-2),
  availability_basis: 'derived',
  computed_at: COMPUTED,
  supporting: (seed.obs ?? []).map(obsRef),
  contradicting: (seed.contra ?? []).map(obsRef),
  context_refs: [],
  input_refs: [],
  source_refs: [],
  n_documents: seed.docs ?? 1,
  n_origin_groups: seed.origins ?? 1,
  n_unknown_origins: 0,
  blocking_uncertainties: seed.uncertain ?? [],
  producer: 'int.cases',
  producer_version: '0.4.0'
}))

export function documentDetail(id: string): DocumentDetail | undefined {
  const document = documentById.get(id)
  if (!document) return undefined
  return {
    document,
    segments: [],
    links: [],
    observations: OBSERVATIONS.filter((item) => item.document_id === id)
  }
}

/** Respect the selected run, store scope and availability cutoff, even for synthetic data. */
export function forRun<T extends { available_at: string | null; run_id?: string }>(runId: string, items: T[], storeOf: (item: T) => string | null | undefined): T[] | undefined {
  const run = RUNS.find((item) => item.spec.run_id === runId)
  if (!run) return undefined
  if (!run.published) return []
  return items.filter((item) => {
    const store = storeOf(item)
    return (!store || run.spec.stores.includes(store))
      && item.available_at !== null
      && Date.parse(item.available_at) <= Date.parse(run.spec.as_of)
      && (!item.run_id || item.run_id === runId)
  })
}
