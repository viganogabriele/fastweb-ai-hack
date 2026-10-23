import type { components, operations } from './schema'
import type { Case } from './client'

export type AgentTrace = components['schemas']['AgentTrace']
export type TraceSelection = { item: Case; runId: string; fixtureMode: boolean }
export type TraceIdentity = Pick<AgentTrace, 'id' | 'version'>
export type TraceState<T> = { status: 'loading' | 'empty' | 'unavailable' | 'error'; message?: string } | { status: 'ready'; data: T }
export type TraceReader = <T>(path: string, signal: AbortSignal) => Promise<T>
type TraceQuery = NonNullable<operations['case_trace_api_runs__run_id__cases__case_id__traces__trace_id__get']['parameters']['query']>

export function tracePath({ item, runId, fixtureMode }: TraceSelection, exact?: TraceIdentity) {
  const query: TraceQuery = { fixture: fixtureMode, ...(exact ? { version: exact.version } : {}) }
  const params = new URLSearchParams({ fixture: String(query.fixture) })
  if (query.version !== undefined && query.version !== null) params.set('version', query.version)
  return `/runs/${encodeURIComponent(runId)}/cases/${encodeURIComponent(item.id)}/traces${exact ? `/${encodeURIComponent(exact.id)}` : ''}?${params}`
}
export function traceMatches(trace: AgentTrace, { item, runId }: TraceSelection, exact?: TraceIdentity) {
  const cases = trace.input_refs.filter((ref) => ref.kind === 'Case' && ref.id === item.id)
  return item.run_id === runId && trace.run_id === runId && trace.scenario_id === item.scenario_id && trace.case_id === item.id &&
    cases.length === 1 && cases[0].version === item.version &&
    (!exact || (trace.id === exact.id && trace.version === exact.version))
}

// Keep the endpoint's publication-order version selection. Never choose a
// lexical "latest", request an alternative version or fall back to mock traces.
export function requestCaseTraces(selection: TraceSelection, read: TraceReader, publish: (state: TraceState<AgentTrace[]>) => void) {
  return request(selection, read, publish, undefined)
}
export function requestCaseTrace(selection: TraceSelection, exact: TraceIdentity, read: TraceReader, publish: (state: TraceState<AgentTrace[]>) => void) {
  return request(selection, read, publish, exact)
}
function request(selection: TraceSelection, read: TraceReader, publish: (state: TraceState<AgentTrace[]>) => void, exact?: TraceIdentity) {
  const controller = new AbortController()
  if (selection.item.run_id !== selection.runId) {
    publish({ status: 'unavailable', message: 'Caso non disponibile nel run selezionato.' })
  } else {
    publish({ status: 'loading' })
    void read<AgentTrace[] | AgentTrace>(tracePath(selection, exact), controller.signal).then((response) => {
      if (controller.signal.aborted) return
      const records = Array.isArray(response) ? response : [response]
      // A detail endpoint must return exactly the requested identity.
      const data = records.filter((trace) => traceMatches(trace, selection, exact))
      if (data.length !== records.length || (exact && data.length !== 1)) {
        publish({ status: 'unavailable', message: 'Traccia o riferimento alla versione esatta del caso non disponibile. Nessuna versione alternativa sostituita.' })
      } else publish(data.length ? { status: 'ready', data } : { status: 'empty', message: 'Nessuna traccia pubblicata per questo caso.' })
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) publish({ status: 'error', message: error instanceof Error ? error.message : 'Errore API tracce.' })
    })
  }
  return () => controller.abort()
}
