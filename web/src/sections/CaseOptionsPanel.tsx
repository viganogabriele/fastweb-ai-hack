import { useEffect, useState, useSyncExternalStore } from 'react'
import type { Case } from '../api/client'
import { mandatoryBlockers, optionsContextKey } from '../api/caseOptions'
import type { ActionOption, OptionsContext } from '../api/caseOptions'
import { Button, Input, StatusBadge } from '../ui'
import { createOptionsSession, intentKey } from './caseOptionsState'
import type { Intent, OptionsSession, OptionsState } from './caseOptionsState'

export function CaseOptionsPanel({ item, runId, fixtureMode }: { item: Case; runId: string; fixtureMode: boolean }) {
  const context = { runId, caseId: item.id, version: item.version, fixture: fixtureMode }
  return <ScopedOptions key={optionsContextKey(context)} context={context} closed={item.status === 'closed' || item.status === 'decided'} />
}

function ScopedOptions({ context, closed }: { context: OptionsContext; closed: boolean }) {
  const [session] = useState(() => createOptionsSession(context))
  useEffect(() => {
    session.start()
    return () => session.dispose()
  }, [session])
  return <PublishedOptions session={session} context={context} closed={closed} />
}

function PublishedOptions({ session, context, closed }: { session: OptionsSession; context: OptionsContext; closed: boolean }) {
  const state = useSyncExternalStore(session.subscribe, session.snapshot)
  return <section className="sd-case-analysis__options" aria-label="Opzioni pubblicate sul server" aria-busy={state.loading || state.pending}>
    <h4>Opzioni pubblicate sul server</h4>
    <StatusBadge tone={context.fixture ? 'warning' : 'neutral'} label={context.fixture ? 'Namespace fixture · simulazione' : 'Namespace prodotto · bozza locale'} />
    <p>Le decisioni sono salvate dal backend come bozze locali simulate. Nessun invio esterno o movimento di stock. L’identità del revisore è dichiarata localmente, non autenticata.</p>
    {state.reviewRequired && <p role="alert">Conflitto 409: input o proposta non più validi. Rileggi le opzioni ricaricate e i controlli prima di decidere nuovamente.</p>}
    {state.loading && <p role="status">Caricamento opzioni…</p>}
    {state.error && <div role="alert"><p>{state.error}</p><Button onClick={() => void session.load()}>Ricarica opzioni</Button></div>}
    {!state.loading && !state.error && <>
      {!state.options.length && <p>Nessuna opzione pubblicata per questo caso.</p>}
      {state.options.map(option => <PublishedOption key={JSON.stringify([option.id, option.version, option.input_version_hash, state.revision])}
        option={option} state={state} session={session} closed={closed} fixture={context.fixture} />)}
      {state.reviewRequired && <Button onClick={session.reviewed}>Ho riesaminato le opzioni e i controlli aggiornati</Button>}
    </>}
  </section>
}

function PublishedOption({ option, state, session, closed, fixture }: {
  option: ActionOption; state: OptionsState; session: OptionsSession; closed: boolean; fixture: boolean
}) {
  const [by, setBy] = useState('')
  const [note, setNote] = useState('')
  const [confirmation, setConfirmation] = useState<Intent | null>(null)
  const blockers = mandatoryBlockers(option)
  const disabled = closed || state.pending || state.reviewRequired
  const commands = [...state.commands.values()].filter(command => command.body.option_id === option.id && command.body.input_version_hash === option.input_version_hash)
  const intent = (decision: Intent['decision']): Intent => ({ option_id: option.id, input_version_hash: option.input_version_hash, decision, by, note: note || null })
  const canAsk = (decision: Intent['decision']) => {
    const command = state.commands.get(intentKey(intent(decision)))
    return !disabled && !confirmation && by.trim().length > 0 && !command && (decision === 'rejected' || blockers.length === 0)
  }
  return <article className="sd-case-analysis__option">
    <header><div><strong>{option.kind}</strong>{option.recommended && <span> · raccomandata</span>}<p>{option.rationale}</p></div>
      <StatusBadge tone={blockers.length ? 'warning' : 'neutral'} label={blockers.length ? `${blockers.length} controlli obbligatori non superati` : 'Nessun blocco obbligatorio pubblicato'} />
    </header>
    <p>Opzione {option.id} · versione {option.version} · produttore {option.producer} {option.producer_version} · {fixture ? 'fixture' : 'prodotto'} · scadenza {option.valid_until}</p>
    <details><summary>Input e assunzioni della proposta</summary><p>Hash input: <code>{option.input_version_hash}</code></p>
      <ul>{option.assumptions.map((assumption, index) => <li key={index}>{assumption}</li>)}</ul>
      <p>Base disponibilità: {option.availability_basis}</p>
    </details>
    <ul className="sd-case-analysis__checks">{option.checks.map((check, index) => <li key={`${check.name}-${index}`}>
      <StatusBadge tone={check.status === 'pass' ? 'success' : check.status === 'not_applicable' ? 'neutral' : 'warning'} label={`${check.name}: ${check.status}`} />
      <span>{check.detail} · {check.mandatory ? 'obbligatorio' : 'facoltativo'}</span>
    </li>)}</ul>
    {!option.checks.length && <p>Nessun controllo pubblicato. La validazione di fattibilità resta al backend.</p>}
    {blockers.length > 0 && <p>Approvazione bloccata: un controllo obbligatorio fallito o sconosciuto richiede verifica.</p>}
    <Input label="Identità locale del revisore" value={by} required disabled={disabled || Boolean(confirmation)} onChange={event => setBy(event.target.value)} hint="Inserisci esplicitamente il tuo nome; non è un accesso autenticato." />
    <Input label="Nota facoltativa" value={note} disabled={disabled || Boolean(confirmation)} onChange={event => setNote(event.target.value)} />
    {confirmation && !state.reviewRequired && <div className="sd-case-decision__confirm" role="group" aria-label={`Conferma decisione su ${option.id}`}>
      <p>Confermi {confirmation.decision === 'approved' ? 'approvazione' : 'rifiuto'} di {option.id} con gli input visualizzati, come {confirmation.by}? Nota: {confirmation.note || 'nessuna'}. Verrà salvata una bozza locale sul server.</p>
      <Button disabled={disabled} onClick={() => { void session.submit(confirmation); setConfirmation(null) }}>Conferma e salva sul server</Button>
      <Button disabled={state.pending} onClick={() => setConfirmation(null)}>Annulla</Button>
    </div>}
    <div className="sd-case-decision__actions">
      <Button disabled={!canAsk('approved')} onClick={() => setConfirmation(intent('approved'))}>Approva opzione pubblicata</Button>
      <Button disabled={!canAsk('rejected')} onClick={() => setConfirmation(intent('rejected'))}>Respingi opzione pubblicata</Button>
    </div>
    {commands.map(command => <div key={command.body.idempotency_key} role={command.status === 'failed' || command.status === 'retryable' || command.status === 'conflict' ? 'alert' : 'status'}>
      <p>{command.body.decision === 'approved' ? 'Approvazione' : 'Rifiuto'} · revisore locale: {command.body.by} · nota: {command.body.note || 'nessuna'}</p>
      <p>Chiave comando: <code>{command.body.idempotency_key}</code></p>
      {command.status === 'pending' && <p>Salvataggio in corso…</p>}
      {command.result && <p>Decisione salvata sul server: {command.result.decision.decision === 'approved' ? 'approvata' : 'respinta'} · ID {command.result.decision.id} · stato {command.result.decision.dispatch_status} · bozza locale simulata, nessun invio esterno.</p>}
      {command.message && <p>{command.message}</p>}
      {command.status === 'retryable' && <Button disabled={disabled} onClick={() => void session.submit(command.body)}>Riprova lo stesso comando</Button>}
    </div>)}
  </article>
}
