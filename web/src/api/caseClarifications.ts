import type { components, operations } from './schema'
import type { ArtifactRef, Case, DocumentDetail } from './client'

export type Clarification = components['schemas']['Clarification']
export type ClarificationSelection = { item: Case; runId: string; fixtureMode: boolean }
export type ClarificationRef = Pick<ArtifactRef, 'id' | 'version'>
export type ClarificationState<T> = { status: 'loading' | 'empty' | 'unavailable' | 'error'; message?: string } | { status: 'ready'; data: T }
export type ClarificationReader = <T>(path: string, signal: AbortSignal) => Promise<T>
type DetailQuery = NonNullable<operations['clarification_api_runs__run_id__cases__case_id__clarifications__clarification_id__get']['parameters']['query']>

export const clarificationSelectionKey = (selection: ClarificationSelection) => JSON.stringify([selection.runId, selection.fixtureMode, selection.item])
export function clarificationsPath(selection: ClarificationSelection, ref?: ClarificationRef) {
  const query: DetailQuery = { fixture: selection.fixtureMode, version: ref?.version }
  const params = new URLSearchParams({ fixture: String(query.fixture) })
  if (query.version != null) params.set('version', query.version)
  return `/runs/${encodeURIComponent(selection.runId)}/cases/${encodeURIComponent(selection.item.id)}/clarifications${ref ? `/${encodeURIComponent(ref.id)}` : ''}?${params}`
}
export function clarificationMatches(record: Clarification, { item, runId }: ClarificationSelection) {
  const refs = record.input_refs.filter(ref => ref.kind === 'Case')
  return item.run_id === runId && record.run_id === runId && record.scenario_id === item.scenario_id && record.case_id === item.id &&
    refs.length === 1 && refs[0].id === item.id && refs[0].version === item.version
}

// Each request owns its cancellation guard, including readers that ignore AbortSignal.
export function requestClarifications(selection: ClarificationSelection, read: ClarificationReader,
  publish: (state: ClarificationState<Clarification[]>) => void) {
  const controller = new AbortController()
  if (selection.item.run_id !== selection.runId) {
    publish({ status: 'unavailable', message: 'Il caso non appartiene al run selezionato.' })
  } else {
    publish({ status: 'loading' })
    void read<Clarification[]>(clarificationsPath(selection), controller.signal).then(records => {
      if (controller.signal.aborted) return
      // Do not sort or deduplicate versions: latest-visible selection belongs to the API.
      const data = records.filter(record => clarificationMatches(record, selection))
      publish(data.length ? { status: 'ready', data } : records.length
        ? { status: 'unavailable', message: 'I chiarimenti pubblicati non riferiscono la versione esatta del caso selezionato.' }
        : { status: 'empty', message: 'Nessun chiarimento pubblicato per questo caso.' })
    }).catch(error => {
      if (!controller.signal.aborted) publish({ status: 'error', message: error instanceof Error ? error.message : 'Errore API chiarimenti.' })
    })
  }
  return () => controller.abort()
}
export function requestClarification(selection: ClarificationSelection, ref: ClarificationRef, read: ClarificationReader,
  publish: (state: ClarificationState<Clarification>) => void) {
  const controller = new AbortController()
  publish({ status: 'loading' })
  void read<Clarification>(clarificationsPath(selection, ref), controller.signal).then(data => {
    if (controller.signal.aborted) return
    publish(clarificationMatches(data, selection) && data.id === ref.id && data.version === ref.version
      ? { status: 'ready', data } : { status: 'unavailable', message: 'La versione esatta del chiarimento non è disponibile in questo contesto.' })
  }).catch(error => {
    if (!controller.signal.aborted) publish({ status: 'error', message: error instanceof Error ? error.message : 'Errore dettaglio chiarimento.' })
  })
  return () => controller.abort()
}
export const clarificationStatus: Record<Clarification['status'], string> = {
  draft: 'Bozza', asked: 'Domanda registrata (asked)', answered: 'Risposta registrata', cancelled: 'Annullato'
}
export function clarificationTimestamp(value: string | null | undefined) {
  if (!value) return 'Non disponibile'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? `${value} · fuso non verificabile` : `${date.toISOString()} · UTC`
}
export function answerDocumentPath(selection: ClarificationSelection, id: string) {
  return `/runs/${encodeURIComponent(selection.runId)}/documents/${encodeURIComponent(id)}?fixture=${selection.fixtureMode}`
}
// SourceDocument has no run/scenario fields: the published, namespace-scoped
// document route enforces snapshot visibility. Never resolve its raw URI.
export function answerDocumentMatches(detail: DocumentDetail, id: string) {
  return detail.document.id === id
}
