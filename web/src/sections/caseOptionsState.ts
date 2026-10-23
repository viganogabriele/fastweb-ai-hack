import { loadCaseOptions, mandatoryBlockers, OptionsApiError, postCaseDecision } from '../api/caseOptions.ts'
import type { ActionOption, DecisionInput, LocalDraft, OptionsContext } from '../api/caseOptions.ts'

export type Intent = Pick<DecisionInput, 'option_id' | 'input_version_hash' | 'decision' | 'by' | 'note'>
export type Command = {
  readonly body: Readonly<DecisionInput>
  status: 'pending' | 'success' | 'retryable' | 'failed' | 'conflict'
  message?: string
  result?: LocalDraft
}
export type OptionsState = {
  options: ActionOption[]; loading: boolean; error?: string; reviewRequired: boolean
  pending: boolean; revision: number; commands: ReadonlyMap<string, Command>
}
export const intentKey = (intent: Intent) => JSON.stringify([
  intent.option_id, intent.input_version_hash, intent.decision, intent.by, intent.note ?? null
])

// One session per run/case/version/namespace. Disposal rejects all late reads and writes.
// The synchronous lock also protects against two clicks before React can rerender.
export function createOptionsSession(context: OptionsContext, dependencies = {
  load: loadCaseOptions, post: postCaseDecision, key: () => crypto.randomUUID()
}, previous?: OptionsState) {
  let state: OptionsState = { options: [], loading: true, reviewRequired: previous?.reviewRequired ?? false, pending: false,
    revision: previous?.revision ?? 0, commands: previous?.commands ?? new Map() }
  let active = true
  let generation = 0
  let read: AbortController | undefined
  const listeners = new Set<() => void>()
  const update = (patch: Partial<OptionsState>) => {
    if (!active) return
    state = { ...state, ...patch }
    listeners.forEach(listener => listener())
  }
  const setCommand = (key: string, command: Command) => {
    const commands = new Map(state.commands)
    commands.set(key, command)
    update({ commands })
  }
  async function load() {
    if (!active || state.pending) return
    read?.abort()
    read = new AbortController()
    const token = ++generation
    update({ loading: true, error: undefined, options: [] })
    try {
      const options = await dependencies.load(context, read.signal)
      if (active && token === generation) update({ options, loading: false })
    } catch (error) {
      if (active && token === generation) update({ loading: false, error: error instanceof OptionsApiError ? error.message : 'Opzioni non disponibili: errore di rete o timeout. Riprova il caricamento.' })
    }
  }
  async function submit(intent: Intent) {
    if (!active || state.pending || state.loading || state.error || state.reviewRequired || !intent.by.trim()) return
    const option = state.options.find(option => option.id === intent.option_id && option.input_version_hash === intent.input_version_hash)
    if (!option || (intent.decision === 'approved' && mandatoryBlockers(option).length)) return
    const key = intentKey(intent)
    const previous = state.commands.get(key)
    if (previous && previous.status !== 'retryable') return
    const body = previous?.body ?? Object.freeze({ ...intent, idempotency_key: dependencies.key() })
    update({ pending: true })
    setCommand(key, { body, status: 'pending' })
    try {
      const result = await dependencies.post(context, body)
      if (!active) return
      setCommand(key, { body, status: 'success', result })
    } catch (error) {
      if (!active) return
      const status = error instanceof OptionsApiError ? error.status : undefined
      const conflict = status === 409
      setCommand(key, { body, status: conflict ? 'conflict' : status === undefined || status >= 500 ? 'retryable' : 'failed',
        message: error instanceof OptionsApiError ? error.message : 'Rete interrotta o timeout: esito sconosciuto. Il server potrebbe aver salvato la decisione. Riprova con lo stesso comando.' })
      if (conflict) update({ reviewRequired: true })
    } finally {
      update({ pending: false })
    }
    if (active && state.reviewRequired) await load()
  }
  return {
    snapshot: () => state,
    // Leaving a selection cannot cancel a server commit. Keep the exact command
    // available for an explicit retry on return, without accepting late results.
    snapshotForResume: (): OptionsState => ({ ...state, pending: false,
      commands: new Map([...state.commands].map(([key, command]) => [key, command.status === 'pending'
        ? { ...command, status: 'retryable', message: 'Selezione cambiata durante il salvataggio: esito sconosciuto. Riprova lo stesso comando per verificarlo.' }
        : command])) }),
    subscribe(listener: () => void) { listeners.add(listener); return () => { listeners.delete(listener) } },
    load, submit,
    start() { active = true; void load() },
    reviewed() {
      if (!state.loading && !state.error && state.reviewRequired) {
        update({ reviewRequired: false, revision: state.revision + 1, commands: new Map() })
      }
    },
    dispose() { active = false; generation++; read?.abort() }
  }
}
export type OptionsSession = ReturnType<typeof createOptionsSession>
