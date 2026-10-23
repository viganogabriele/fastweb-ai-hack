import type { components, operations } from './schema'

export type ActionOption = components['schemas']['ActionOption']
type DecisionPost = operations['case_decision_api_runs__run_id__cases__case_id__decisions_post']
export type DecisionInput = DecisionPost['requestBody']['content']['application/json']
export type LocalDraft = DecisionPost['responses'][200]['content']['application/json']
export type OptionsContext = { runId: string; caseId: string; version: string; fixture: boolean }

export function optionsContextKey(context: OptionsContext) {
  return JSON.stringify([context.runId, context.caseId, context.version, context.fixture])
}

export function caseOptionsPath(context: OptionsContext) {
  return `/api/runs/${encodeURIComponent(context.runId)}/cases/${encodeURIComponent(context.caseId)}`
}

export class OptionsApiError extends Error {
  readonly status: number
  constructor(status: number) {
    super(status === 409 ? 'Conflitto: gli input o la proposta non sono più validi. Riesamina le opzioni aggiornate.'
      : status === 404 ? 'Caso o opzione non trovati nel namespace selezionato.'
        : status === 422 ? 'Decisione non valida: verifica identità locale e dati della proposta.'
          : status === 503 ? 'Registro occupato (503). Esito non confermato: riprova lo stesso comando.'
            : status >= 500 ? `Servizio non disponibile (${status}). Esito non confermato: riprova lo stesso comando.`
              : `Decisione rifiutata dal servizio (${status}). Verifica la richiesta prima di un nuovo comando.`)
    this.status = status
  }
}

async function jsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) throw new OptionsApiError(response.status)
  return response.json() as Promise<T>
}

export async function loadCaseOptions(context: OptionsContext, signal: AbortSignal): Promise<ActionOption[]> {
  return jsonResponse(await fetch(`${caseOptionsPath(context)}/options?fixture=${context.fixture}`, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.any([signal, AbortSignal.timeout(15000)])
  }))
}

export async function postCaseDecision(context: OptionsContext, body: Readonly<DecisionInput>): Promise<LocalDraft> {
  return jsonResponse(await fetch(`${caseOptionsPath(context)}/decisions?fixture=${context.fixture}`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15000)
  }))
}

export function mandatoryBlockers(option: ActionOption) {
  return option.checks.filter(check => check.mandatory && check.status !== 'pass' && check.status !== 'not_applicable')
}
