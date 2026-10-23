import { useEffect, useState, useSyncExternalStore } from 'react'
import type { Case } from '../api/client'
import { mandatoryBlockers, optionsContextKey } from '../api/caseOptions'
import type { ActionOption, OptionsContext } from '../api/caseOptions'
import { ArrowLeftRight, Check, ChevronRight, X } from 'lucide-react'
import { Button, Dialog, Input, StatusBadge } from '../ui'
import type { StatusTone } from '../ui'
import { shortDate } from './caseLabels'
import { optionKind } from './optionKinds'
import { createOptionsSession, intentKey } from './caseOptionsState'
import type { Command, Intent, OptionsSession, OptionsState } from './caseOptionsState'

// Tab-lifetime journal: revisiting a case keeps uncertain commands and their keys.
// Nothing is submitted on mount, and fixture/product commands never share a scope.
const retainedSessions = new Map<string, OptionsState>()

export function CaseOptionsPanel({ item, runId, fixtureMode }: { item: Case; runId: string; fixtureMode: boolean }) {
  const context = { runId, caseId: item.id, version: item.version, fixture: fixtureMode }
  return <ScopedOptions key={optionsContextKey(context)} context={context} closed={item.status === 'closed' || item.status === 'decided'} />
}

function ScopedOptions({ context, closed }: { context: OptionsContext; closed: boolean }) {
  const [scope] = useState(context)
  const [session] = useState(() => createOptionsSession(scope, undefined, retainedSessions.get(optionsContextKey(scope))))
  useEffect(() => {
    session.start()
    return () => {
      session.dispose()
      retainedSessions.set(optionsContextKey(scope), session.snapshotForResume())
    }
  }, [session, scope])
  return <PublishedOptions session={session} context={context} closed={closed} />
}

const scenarioLabels: Record<string, string> = { low: 'Bassa', base: 'Base', high: 'Alta' }
const units = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 1 })
const num = (value: number | null | undefined) => value == null ? '–' : units.format(value)
const eur = (value: number | null | undefined) => value == null ? 'sconosciuto' : `${units.format(value)} €`
const checkTone = (status: ActionOption['checks'][number]['status']) => status === 'pass' ? 'success' : status === 'not_applicable' ? 'neutral' : 'warning'
const checkLabels: Record<ActionOption['checks'][number]['status'], string> = { pass: 'ok', fail: 'non superato', unknown: 'da verificare', not_applicable: 'non applicabile' }

// Lost units at the destination as "base (low–high)"; null when the option has no quantified outcome.
function lostUnits(option: ActionOption) {
  const by = new Map((option.outcomes ?? []).map(outcome => [outcome.scenario_id, outcome.lost_units_dest]))
  if (by.get('base') == null) return null
  const low = num(by.get('low')), high = num(by.get('high'))
  return `${num(by.get('base'))}${low !== high ? ` (${low}–${high})` : ''}`
}
// Latest command this session sent for the option at its current input hash.
function latestCommand(state: OptionsState, option: ActionOption) {
  return [...state.commands.values()].filter(command => command.body.option_id === option.id && command.body.input_version_hash === option.input_version_hash).at(-1)
}
function commandBadge(command: Command | undefined): { tone: StatusTone; label: string } | null {
  if (!command) return null
  const verb = command.body.decision === 'approved' ? 'Approvata' : 'Respinta'
  return command.status === 'success' ? { tone: 'success', label: `${verb} · bozza salvata` }
    : command.status === 'pending' ? { tone: 'info', label: 'Salvataggio…' }
      : { tone: 'danger', label: 'Decisione non salvata' }
}

function PublishedOptions({ session, context, closed }: { session: OptionsSession; context: OptionsContext; closed: boolean }) {
  const state = useSyncExternalStore(session.subscribe, session.snapshot)
  const [openId, setOpenId] = useState<string | null>(null)
  // The reviewer types their name once per case, not once per option.
  const [by, setBy] = useState('')
  const open = state.options.find(option => option.id === openId)
  return <section className="sd-case-analysis__options" aria-label="Opzioni pubblicate sul server" aria-busy={state.loading || state.pending}>
    <header className="sd-case-options__head">
      <h4><ArrowLeftRight aria-hidden="true" />Opzioni di stock</h4>
      {context.fixture && <StatusBadge tone="warning" label="Namespace fixture · simulazione" />}
    </header>
    <p className="sd-case-analysis__tech">Scegli un’opzione per vederne i dettagli e decidere. Le decisioni restano bozze locali: nessun movimento di stock reale.</p>
    {state.reviewRequired && <p role="alert">Conflitto 409: input o proposta non più validi. Rileggi le opzioni ricaricate e i controlli prima di decidere nuovamente.</p>}
    {state.loading && <p role="status">Caricamento opzioni…</p>}
    {state.error && <div role="alert"><p>{state.error}</p><Button onClick={() => void session.load()}>Ricarica opzioni</Button></div>}
    {!state.loading && !state.error && <>
      {!state.options.length && <p>Nessuna opzione pubblicata per questo caso.</p>}
      {/* Recommended first; the rest keep the published order. */}
      <ul className="sd-case-options__list">{[...state.options].sort((a, b) => Number(b.recommended) - Number(a.recommended)).map(option => <li key={JSON.stringify([option.id, option.version, option.input_version_hash, state.revision])}>
        <OptionCard option={option} command={latestCommand(state, option)} onOpen={() => setOpenId(option.id)} />
      </li>)}</ul>
      {state.reviewRequired && <Button onClick={session.reviewed}>Ho riesaminato le opzioni e i controlli aggiornati</Button>}
    </>}
    {open && <OptionDialog key={JSON.stringify([open.id, open.input_version_hash, state.revision])} option={open} state={state} session={session}
      closed={closed} fixture={context.fixture} by={by} setBy={setBy} onClose={() => setOpenId(null)} />}
    <DecisionJournal state={state} session={session} />
  </section>
}

function OptionCard({ option, command, onOpen }: { option: ActionOption; command: Command | undefined; onOpen: () => void }) {
  const { label, icon: Icon } = optionKind(option.kind)
  const blockers = mandatoryBlockers(option)
  const lost = lostUnits(option)
  const pieces = option.legs.reduce((total, leg) => total + leg.qty, 0)
  const badge = commandBadge(command)
  return <button type="button" className={`sd-case-options__card${option.recommended ? ' is-recommended' : ''}`} onClick={onOpen} aria-haspopup="dialog">
    <span className="sd-case-options__icon" aria-hidden="true"><Icon /></span>
    <span className="sd-case-options__main">
      <span className="sd-case-options__title"><strong>{label}</strong>
        {option.recommended && <StatusBadge tone="info" label="Consigliata" />}
        {badge && <StatusBadge {...badge} />}
      </span>
      <span className="sd-case-options__rationale">{option.rationale}</span>
      <span className="sd-case-options__facts">
        {option.legs.length > 0 && <span>{option.legs.length === 1 ? '1 movimento' : `${option.legs.length} movimenti`} · {num(pieces)} pz</span>}
        {lost && <span>Vendite perse stimate {lost}</span>}
        {blockers.length > 0 && <span className="is-warn">{blockers.length === 1 ? '1 controllo bloccante' : `${blockers.length} controlli bloccanti`}</span>}
      </span>
    </span>
    <ChevronRight className="sd-case-options__chevron" aria-hidden="true" />
  </button>
}

function OptionDialog({ option, state, session, closed, fixture, by, setBy, onClose }: {
  option: ActionOption; state: OptionsState; session: OptionsSession; closed: boolean; fixture: boolean
  by: string; setBy: (value: string) => void; onClose: () => void
}) {
  const [note, setNote] = useState('')
  const [confirmation, setConfirmation] = useState<Intent | null>(null)
  const { label, icon: Icon } = optionKind(option.kind)
  const blockers = mandatoryBlockers(option)
  const disabled = closed || state.pending || state.reviewRequired
  const intent = (decision: Intent['decision']): Intent => ({ option_id: option.id, input_version_hash: option.input_version_hash, decision, by: by.trim(), note: note.trim() || null })
  const canAsk = (decision: Intent['decision']) => !disabled && by.trim().length > 0 && !state.commands.get(intentKey(intent(decision))) && (decision === 'rejected' || blockers.length === 0)
  const why = closed ? 'Il caso è già chiuso o deciso.' : state.reviewRequired ? 'Riesamina le opzioni aggiornate prima di decidere.'
    : !by.trim() ? 'Inserisci il tuo nome per decidere.' : blockers.length ? 'Approvazione bloccata da un controllo obbligatorio: puoi solo respingere.' : null
  const outcomes = option.outcomes ?? []
  const donor = outcomes.some(outcome => outcome.lost_units_donor != null || outcome.leftover_units_donor != null)
  const footer = confirmation
    ? <>
      <span className="sd-case-options__confirm">{confirmation.decision === 'approved' ? 'Approvi' : 'Respingi'} come <strong>{confirmation.by}</strong>? Verrà salvata una bozza locale.</span>
      <Button disabled={state.pending} onClick={() => setConfirmation(null)}>Indietro</Button>
      <Button variant="primary" disabled={disabled} onClick={() => { void session.submit(confirmation); onClose() }}>
        {confirmation.decision === 'approved' ? 'Conferma approvazione' : 'Conferma rifiuto'}
      </Button>
    </>
    : <>
      {why && <span className="sd-case-options__confirm">{why}</span>}
      <Button icon={<X />} disabled={!canAsk('rejected')} onClick={() => setConfirmation(intent('rejected'))}>Respingi</Button>
      <Button variant="primary" icon={<Check />} disabled={!canAsk('approved')} onClick={() => setConfirmation(intent('approved'))}>Approva</Button>
    </>
  return <Dialog open title={<><Icon aria-hidden="true" />{label}</>} onClose={onClose} dismissible={!state.pending} footer={footer}>
    {option.recommended && <StatusBadge tone="info" label="Opzione consigliata" />}
    <p>{option.rationale}</p>
    {option.legs.length > 0 && <section className="sd-case-options__block">
      <h3>Movimenti proposti</h3>
      <ul className="sd-case-options__legs">{option.legs.map((leg, index) => <li key={index}>
        <strong>{leg.origin} → {leg.dest}</strong> · taglia {leg.size} · {num(leg.qty)} pz
        <span>Arrivo {shortDate(leg.eta_at) ?? leg.eta_at} · vendibile {shortDate(leg.sellable_at) ?? leg.sellable_at} · trasporto {eur(leg.cost_eur)}</span>
      </li>)}</ul>
    </section>}
    {outcomes.length > 0 && <section className="sd-case-options__block">
      <h3>Esito atteso per scenario</h3>
      <div className="sd-case-analysis__table-wrap"><table>
        <thead><tr><th scope="col">Domanda</th><th scope="col">Vendite perse</th><th scope="col">Rimanenza</th>
          {donor && <><th scope="col">Perse donatore</th><th scope="col">Rimanenza donatore</th></>}<th scope="col">Trasporto</th></tr></thead>
        <tbody>{outcomes.map(outcome => <tr key={outcome.scenario_id}><th scope="row">{scenarioLabels[outcome.scenario_id] ?? outcome.scenario_id}</th>
          <td>{num(outcome.lost_units_dest)}</td><td>{num(outcome.leftover_units_dest)}</td>
          {donor && <><td>{num(outcome.lost_units_donor)}</td><td>{num(outcome.leftover_units_donor)}</td></>}<td>{eur(outcome.transport_cost_eur)}</td></tr>)}</tbody>
      </table></div>
    </section>}
    <section className="sd-case-options__block">
      <h3>Controlli</h3>
      {option.checks.length ? <ul className="sd-case-analysis__checks">{option.checks.map((check, index) => <li key={`${check.name}-${index}`}>
        <StatusBadge tone={checkTone(check.status)} label={`${check.name}: ${checkLabels[check.status]}`} />
        <span>{check.detail}{check.mandatory ? ' · obbligatorio' : ''}</span>
      </li>)}</ul> : <p className="sd-case-analysis__tech">Nessun controllo pubblicato: la fattibilità resta da validare.</p>}
    </section>
    <details className="sd-case-analysis__refs">
      <summary>Assunzioni e riferimenti</summary>
      <ul>{option.assumptions.map((assumption, index) => <li key={index}>{assumption}</li>)}</ul>
      <dl>
        <dt>Opzione</dt><dd>{option.id} · {option.version}</dd>
        <dt>Produttore</dt><dd>{option.producer} {option.producer_version} · {fixture ? 'fixture' : 'prodotto'}</dd>
        <dt>Disponibilità</dt><dd>{option.availability_basis}</dd>
        <dt>Hash input</dt><dd>{option.input_version_hash}</dd>
        <dt>Scadenza</dt><dd>{option.valid_until}</dd>
      </dl>
    </details>
    <div className="sd-case-options__form">
      <Input label="Il tuo nome" value={by} required disabled={disabled || Boolean(confirmation)} onChange={event => setBy(event.target.value)} hint="Identità dichiarata, non autenticata." />
      <Input label="Nota (facoltativa)" value={note} disabled={disabled || Boolean(confirmation)} onChange={event => setNote(event.target.value)} />
    </div>
  </Dialog>
}

function DecisionJournal({ state, session }: { state: OptionsState; session: OptionsSession }) {
  if (!state.commands.size) return null
  return <section aria-label="Registro dei comandi di questo caso">
    <h5>Comandi confermati in questa sessione</h5>
    {[...state.commands.values()].map(command => <div key={command.body.idempotency_key} role={command.status === 'failed' || command.status === 'retryable' || command.status === 'conflict' ? 'alert' : 'status'}>
      <p>Opzione {command.body.option_id} · hash <code>{command.body.input_version_hash}</code></p>
      <p>{command.body.decision === 'approved' ? 'Approvazione' : 'Rifiuto'} · revisore locale: {command.body.by} · nota: {command.body.note || 'nessuna'}</p>
      <p>Chiave comando: <code>{command.body.idempotency_key}</code></p>
      {command.status === 'pending' && <p>Salvataggio in corso…</p>}
      {command.result && <p>Decisione salvata sul server: {command.result.decision.decision === 'approved' ? 'approvata' : 'respinta'} · ID {command.result.decision.id} · stato {command.result.decision.dispatch_status} · bozza locale simulata, nessun invio esterno.</p>}
      {command.message && <p>{command.message}</p>}
      {command.status === 'retryable' && <Button disabled={state.pending || state.loading || Boolean(state.error) || state.reviewRequired} onClick={() => void session.submit(command.body)}>Riprova lo stesso comando</Button>}
    </div>)}
  </section>
}
