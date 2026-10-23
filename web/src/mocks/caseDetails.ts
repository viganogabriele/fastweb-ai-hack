/** Handwritten synthetic UI examples. Never presented for live API runs. */
export type Scenario = { low: number; base: number; high: number }
export type ForecastAdjustment = {
  status: 'computed' | 'unchanged' | 'not_estimable'
  reason: string | null
  horizonStart: string
  series: Array<{ date: string; baseline: number | null; latent: Scenario | null; servable: Scenario | null }>
}
export type TraceStep = { tool: string; arguments: Record<string, unknown>; result: string; durationMs: number; error?: string }
export type AgentTrace = { outcome: string; mode: string; fallbackUsed: boolean; steps: TraceStep[] }
export type OptionCheck = { name: string; status: 'pass' | 'fail' | 'unknown' | 'not_applicable'; mandatory: boolean; detail: string }
export type ActionOption = {
  id: string; kind: string; recommended: boolean; rationale: string; checks: OptionCheck[]; blockers: string[]
}
export type CaseDetailFixture = {
  runId: string; caseId: string; caseVersion: string; forecast: ForecastAdjustment; trace: AgentTrace; options: ActionOption[]
}

const days = ['2026-10-10', '2026-10-11', '2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16']
// Entire record is synthetic: figures and trace content are examples, not operational data.
export const CASE_DETAIL_FIXTURES: CaseDetailFixture[] = [{
  runId: 'fixture', caseId: 'case-mil01-j20931a00012-999-20261002', caseVersion: 'v1',
  forecast: {
    status: 'computed', reason: null, horizonStart: days[0],
    series: days.map((date) => ({ date, baseline: 2, latent: { low: 2, base: 3, high: 4 }, servable: { low: 1, base: 2, high: 3 } }))
  },
  trace: { outcome: 'Proposta dimostrativa generata; nessuna azione eseguita.', mode: 'replay', fallbackUsed: false, steps: [
    { tool: 'read_forecast', arguments: { horizonDays: 7 }, result: 'Baseline e scenari sintetici caricati.', durationMs: 18 },
    { tool: 'evaluate_options', arguments: { candidateCount: 2 }, result: 'Due opzioni sintetiche valutate.', durationMs: 31 }
  ] },
  options: [
    { id: 'demo-hold', kind: 'hold', recommended: false, rationale: 'Mantenere lo stock attuale nel caso dimostrativo.', checks: [{ name: 'Case review', status: 'pass', mandatory: true, detail: 'Revisione simulata completata.' }], blockers: [] },
    { id: 'demo-transfer', kind: 'transfer', recommended: true, rationale: 'Trasferimento dimostrativo soggetto a disponibilità.', checks: [{ name: 'Stock donatore', status: 'unknown', mandatory: true, detail: 'Disponibilità non verificata nel demo.' }, { name: 'Corsia logistica', status: 'fail', mandatory: true, detail: 'Corsia non confermata nel demo.' }], blockers: ['Stock donatore sconosciuto', 'Corsia logistica non confermata'] }
  ]
}, {
  runId: 'fixture', caseId: 'case-nyc01-unknown-20260906', caseVersion: 'v1',
  forecast: { status: 'not_estimable', reason: 'Il riferimento parla di un prodotto non identificato; nessuna corrispondenza SKU verificata.', horizonStart: '2026-09-07', series: [] },
  trace: { outcome: 'Astensione: identificazione SKU insufficiente.', mode: 'replay', fallbackUsed: false, steps: [
    { tool: 'resolve_product', arguments: { candidateCount: 0 }, result: 'Nessuna identificazione univoca.', durationMs: 12 }
  ] },
  options: []
}]

export function findCaseDetailFixture(runId: string, caseId: string, caseVersion: string, fixtureMode: boolean) {
  if (!fixtureMode || !runId) return undefined
  // `fixture` is the hand-authored example context. The caller supplies the active
  // run id at lookup time, so UI state never uses that shared example label as identity.
  return CASE_DETAIL_FIXTURES.find((item) => item.runId === 'fixture' && item.caseId === caseId && item.caseVersion === caseVersion)
}
