import { useState } from 'react'
import type { ReactNode } from 'react'
import {
  AlarmClock,
  ArrowRight,
  ChevronRight,
  ClipboardList,
  FileText,
  Flame,
  Search,
  ShieldQuestion,
  Store
} from 'lucide-react'
import type { Case, RunView, SourceDocument } from '../api/client'
import { Button, EmptyState, Input, Select, StatusBadge, formatPercent } from '../ui'
import type { StatusTone } from '../ui/StatusBadge'
import { compareDeadlines, deadline } from './overviewLogic'
import './overview.css'

type Priority = Case['priority']

const statuses: Record<string, string> = {
  open: 'Aperto',
  verify: 'Da verificare',
  monitor: 'Monitoraggio',
  action_proposed: 'Azione proposta',
  decided: 'Deciso',
  closed: 'Chiuso'
}
const statusTone: Record<string, StatusTone> = {
  verify: 'warning',
  action_proposed: 'info',
  decided: 'success'
}
const PRIORITIES: Priority[] = ['critical', 'high', 'medium', 'low']
const priorities: Record<Priority, string> = { critical: 'Critica', high: 'Alta', medium: 'Media', low: 'Bassa' }
const priorityTone: Record<Priority, StatusTone> = { critical: 'danger', high: 'warning', medium: 'info', low: 'neutral' }
const priorityOrder: Record<Priority, number> = { critical: 0, high: 1, medium: 2, low: 3 }
// Labels for the RFC §4.3 owner and case-type enums; unknown values fall back to the raw id.
const owners: Record<string, string> = {
  allocation: 'Allocazione',
  retail_ops: 'Retail operations',
  product_quality: 'Qualità prodotto',
  merchandising: 'Merchandising',
  marketing: 'Marketing'
}
const caseTypes: Record<string, string> = {
  unmet_demand: 'Domanda non servita',
  stock_discrepancy: 'Discrepanza di stock',
  product_feedback: 'Feedback prodotto',
  demand_shift: 'Variazione domanda',
  traffic_change: 'Variazione traffico',
  operational_issue: 'Problema operativo',
  customer_profile: 'Profilo cliente'
}
const label = (map: Record<string, string>, key: string) => map[key] ?? key.replaceAll('_', ' ')
const HOUR = 3600_000
const isActive = (item: Case) => item.status !== 'closed' && item.status !== 'decided'
const dateTime = (value: string) =>
  new Date(value).toLocaleString('it-IT', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })

function Deadline({ due, asOf }: { due: string | null | undefined; asOf: number }) {
  const left = deadline(due, asOf)
  return (
    <span className={`sd-ov-deadline is-${left.tone}`} title={due ? `Scadenza: ${dateTime(due)}` : undefined}>
      {left.tone !== 'none' && <AlarmClock aria-hidden="true" />}
      {left.text}
    </span>
  )
}

function Card({ title, meta, action, className = '', children }: {
  title: string
  meta?: ReactNode
  action?: ReactNode
  className?: string
  children: ReactNode
}) {
  return (
    <section className={`sd-ov-card ${className}`} aria-label={title}>
      <header className="sd-ov-card__head">
        <div>
          <h2>{title}</h2>
          {meta && <p>{meta}</p>}
        </div>
        {action}
      </header>
      {children}
    </section>
  )
}

export function Overview({
  run,
  cases,
  documents,
  onCaseSelect
}: {
  run: RunView
  cases: Case[]
  documents: SourceDocument[]
  onCaseSelect: (item: Case) => void
}) {
  const [search, setSearch] = useState('')
  const [store, setStore] = useState('all')
  const [priority, setPriority] = useState<'all' | Priority>('all')
  const asOf = Date.parse(run.spec.as_of)
  const active = cases.filter(isActive)
  const dueSoon = active
    .filter((item) => item.decision_due_at && Date.parse(item.decision_due_at) - asOf <= 48 * HOUR)
    .sort((a, b) => Date.parse(a.decision_due_at!) - Date.parse(b.decision_due_at!))
  const urgent = active.filter((item) => priorityOrder[item.priority] <= 1)
  const verify = active.filter((item) => item.status === 'verify')
  const byPriority = PRIORITIES.map((key) => ({ key, count: active.filter((item) => item.priority === key).length }))
  const byOwner = Object.entries(
    active.reduce<Record<string, number>>((acc, item) => ({ ...acc, [item.owner]: (acc[item.owner] ?? 0) + 1 }), {})
  ).sort((a, b) => b[1] - a[1])
  const maxOwner = Math.max(1, ...byOwner.map(([, count]) => count))
  const stores = run.spec.stores
    .map((id) => {
      const own = active.filter((item) => item.store_id === id)
      return {
        id,
        open: own.length,
        urgent: own.filter((item) => priorityOrder[item.priority] <= 1).length,
        verify: own.filter((item) => item.status === 'verify').length,
        next: own.map((item) => item.decision_due_at).filter((value): value is string => Boolean(value)).sort(compareDeadlines)[0]
      }
    })
    .sort((a, b) => b.urgent - a.urgent || b.open - a.open || a.id.localeCompare(b.id))
  const maxStore = Math.max(1, ...stores.map((row) => row.open))

  const query = search.trim().toLocaleLowerCase('it-IT')
  const visible = cases
    .filter(
      (item) =>
        (store === 'all' || item.store_id === store) &&
        (priority === 'all' || item.priority === priority) &&
        [item.store_id, item.scope_id, label(caseTypes, item.case_type), label(owners, item.owner), item.priority_reason]
          .join(' ')
          .toLocaleLowerCase('it-IT')
          .includes(query)
    )
    .sort(
      (a, b) =>
        Number(isActive(b)) - Number(isActive(a)) ||
        priorityOrder[a.priority] - priorityOrder[b.priority] ||
        compareDeadlines(a.decision_due_at, b.decision_due_at)
    )
  const filtered = store !== 'all' || priority !== 'all' || query !== ''

  const kpis = [
    { label: 'Casi aperti', value: active.length, note: `${cases.length - active.length} chiusi o decisi`, icon: ClipboardList, tone: 'neutral' },
    { label: 'Priorità alta', value: urgent.length, note: 'critica o alta', icon: Flame, tone: urgent.length ? 'danger' : 'neutral' },
    { label: 'In scadenza', value: dueSoon.length, note: 'entro 48 h', icon: AlarmClock, tone: dueSoon.length ? 'warning' : 'neutral' },
    { label: 'Da verificare', value: verify.length, note: 'incertezze bloccanti', icon: ShieldQuestion, tone: verify.length ? 'info' : 'neutral' },
    { label: 'Fonti acquisite', value: documents.length, note: 'documenti nel run', icon: FileText, tone: 'neutral' },
    { label: 'Negozi', value: run.spec.stores.length, note: 'nel perimetro', icon: Store, tone: 'neutral' }
  ]

  // The most urgent open case: earliest deadline among critical/high, else the earliest overall.
  const nextUp = [...(urgent.length ? urgent : active)].sort(
    (a, b) => compareDeadlines(a.decision_due_at, b.decision_due_at) || priorityOrder[a.priority] - priorityOrder[b.priority]
  )[0]

  return (
    <div className="sd-ov">
      <section className="sd-ov-brief" aria-label="Sintesi del run">
        <div>
          <p className="sd-ov-brief__eyebrow">Sintesi al cutoff · {run.spec.stores.length} negozi</p>
          <p className="sd-ov-brief__text">
            <strong>{active.length} casi aperti</strong>, di cui <strong className="is-danger">{urgent.length} ad alta priorità</strong>.{' '}
            {dueSoon.length ? (
              <>
                {dueSoon.length} {dueSoon.length === 1 ? 'caso richiede' : 'casi richiedono'} una decisione entro 48 ore dal cutoff
                {dueSoon[0]?.decision_due_at ? <>, prima scadenza: <strong>{deadline(dueSoon[0].decision_due_at, asOf).text}</strong></> : null}.
              </>
            ) : (
              'Nessuna decisione in scadenza nelle prossime 48 ore.'
            )}
          </p>
        </div>
        {nextUp && (
          <Button variant="primary" icon={<ArrowRight aria-hidden="true" />} onClick={() => onCaseSelect(nextUp)}>
            Apri il caso più urgente
          </Button>
        )}
      </section>

      <ul className="sd-ov-kpis" aria-label="Indicatori principali">
        {kpis.map(({ label: name, value, note, icon: Icon, tone }) => (
          <li key={name} className={`sd-ov-kpi is-${tone}`}>
            <span className="sd-ov-kpi__icon" aria-hidden="true"><Icon /></span>
            <span className="sd-ov-kpi__label">{name}</span>
            <strong className="sd-ov-kpi__value">{value}</strong>
            <span className="sd-ov-kpi__note">{note}</span>
          </li>
        ))}
      </ul>

      <div className="sd-ov-row">
        <Card
          title="Da decidere"
          meta="Casi aperti con scadenza entro 48 ore dal cutoff del run"
          action={<span className="sd-ov-count">{dueSoon.length}</span>}
          className="sd-ov-due"
        >
          {dueSoon.length ? (
            <ul className="sd-ov-due__list">
              {dueSoon.slice(0, 6).map((item) => (
                <li key={`${item.id}-${item.version}`}>
                  <button type="button" onClick={() => onCaseSelect(item)}>
                    <Deadline due={item.decision_due_at} asOf={asOf} />
                    <span className="sd-ov-due__body">
                      <span className="sd-ov-due__title">
                        <strong>{item.store_id ?? 'Negozio da verificare'}</strong>
                        <span>{label(caseTypes, item.case_type)}</span>
                      </span>
                      <span className="sd-ov-due__reason">{item.priority_reason}</span>
                    </span>
                    <StatusBadge label={priorities[item.priority]} tone={priorityTone[item.priority]} />
                    <ChevronRight className="sd-ov-chevron" aria-hidden="true" />
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="sd-ov-quiet">Nessuna decisione in scadenza nelle prossime 48 ore.</p>
          )}
        </Card>

        <div className="sd-ov-stack">
          <Card title="Casi aperti per priorità" meta={`${active.length} casi`}>
            <div className="sd-ov-segments" role="img" aria-label={byPriority.map(({ key, count }) => `${priorities[key]} ${count}`).join(', ')}>
              {byPriority.map(({ key, count }) =>
                count ? <span key={key} className={`is-${key}`} style={{ flexGrow: count }} /> : null
              )}
            </div>
            <ul className="sd-ov-legend">
              {byPriority.map(({ key, count }) => (
                <li key={key}>
                  <span className={`sd-ov-swatch is-${key}`} aria-hidden="true" />
                  <span>{priorities[key]}</span>
                  <strong>{count}</strong>
                  <span className="sd-ov-legend__share">{active.length ? formatPercent(count / active.length, 0) : '—'}</span>
                </li>
              ))}
            </ul>
          </Card>
          <Card title="Casi aperti per ufficio" meta="Chi riceve la decisione">
            <ul className="sd-ov-bars">
              {byOwner.map(([owner, count]) => (
                <li key={owner}>
                  <span className="sd-ov-bars__label">{label(owners, owner)}</span>
                  <span className="sd-ov-bars__track" aria-hidden="true">
                    <span style={{ inlineSize: `${(count / maxOwner) * 100}%` }} />
                  </span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </div>

      <Card
        title="Negozi"
        meta="Ordinati per casi a priorità alta. Seleziona un negozio per filtrare le segnalazioni."
        action={
          store !== 'all' ? (
            <button type="button" className="sd-ov-link" onClick={() => setStore('all')}>Mostra tutti</button>
          ) : undefined
        }
      >
        <div className="sd-ov-table-wrap">
          <table className="sd-ov-table">
            <thead>
              <tr>
                <th scope="col">Negozio</th>
                <th scope="col">Casi aperti</th>
                <th scope="col" className="is-num">Priorità alta</th>
                <th scope="col" className="is-num">Da verificare</th>
                <th scope="col" className="is-num">Prossima scadenza</th>
              </tr>
            </thead>
            <tbody>
              {stores.map((row) => (
                <tr key={row.id} className={store === row.id ? 'is-selected' : undefined}>
                  <th scope="row">
                    <button type="button" className="sd-ov-store" aria-pressed={store === row.id} onClick={() => setStore(store === row.id ? 'all' : row.id)}>
                      {row.id}
                    </button>
                  </th>
                  <td>
                    <span className="sd-ov-inline-bar">
                      <span className="sd-ov-inline-bar__track" aria-hidden="true"><span style={{ inlineSize: `${(row.open / maxStore) * 100}%` }} /></span>
                      <strong>{row.open}</strong>
                    </span>
                  </td>
                  <td className="is-num">{row.urgent ? <span className="sd-ov-pill is-danger">{row.urgent}</span> : <span className="sd-ov-zero">0</span>}</td>
                  <td className="is-num">{row.verify ? <span className="sd-ov-pill is-warning">{row.verify}</span> : <span className="sd-ov-zero">0</span>}</td>
                  <td className="is-num">{row.next ? <Deadline due={row.next} asOf={asOf} /> : <span className="sd-ov-zero">—</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card
        title="Segnalazioni"
        meta={`${visible.length} di ${cases.length} casi${filtered ? ' · filtri attivi' : ''}`}
        className="sd-ov-cases"
      >
        <form className="sd-ov-toolbar" role="search" onSubmit={(event) => event.preventDefault()}>
          <Input
            size="sm"
            label="Cerca caso"
            hideLabel
            type="search"
            icon={<Search />}
            placeholder="Cerca per negozio, prodotto o motivo"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select
            size="sm"
            label="Negozio"
            hideLabel
            value={store}
            onValueChange={setStore}
            options={[{ value: 'all', label: 'Tutti i negozi' }, ...run.spec.stores.map((id) => ({ value: id, label: id }))]}
          />
          <div className="sd-ov-segmented" role="group" aria-label="Filtra per priorità">
            {(['all', ...PRIORITIES] as const).map((key) => (
              <button key={key} type="button" aria-pressed={priority === key} onClick={() => setPriority(key)}>
                {key !== 'all' && <span className={`sd-ov-swatch is-${key}`} aria-hidden="true" />}
                {key === 'all' ? 'Tutte' : priorities[key]}
              </button>
            ))}
          </div>
        </form>
        {visible.length ? (
          <div className="sd-ov-table-wrap">
            <table className="sd-ov-table sd-ov-cases__table">
              <thead>
                <tr>
                  <th scope="col">Priorità</th>
                  <th scope="col">Prodotto</th>
                  <th scope="col">Negozio</th>
                  <th scope="col">Tipo e motivo</th>
                  <th scope="col">Stato</th>
                  <th scope="col" className="is-num">Scadenza</th>
                  <th scope="col"><span className="sd-visually-hidden">Apri</span></th>
                </tr>
              </thead>
              <tbody>
                {visible.map((item) => (
                  <tr
                    key={`${item.id}-${item.version}`}
                    className={isActive(item) ? undefined : 'is-settled'}
                    onClick={() => onCaseSelect(item)}
                  >
                    <td><StatusBadge label={priorities[item.priority]} tone={priorityTone[item.priority]} /></td>
                    <th scope="row">
                      <button
                        type="button"
                        className="sd-ov-case-link"
                        onClick={(event) => {
                          event.stopPropagation()
                          onCaseSelect(item)
                        }}
                      >
                        {item.scope_id ?? 'Da identificare'}
                      </button>
                    </th>
                    <td className="sd-ov-strong">{item.store_id ?? '—'}</td>
                    <td>
                      <div className="sd-ov-type">
                        <span>{label(caseTypes, item.case_type)}</span>
                        <span>{item.priority_reason}</span>
                      </div>
                    </td>
                    <td><StatusBadge label={statuses[item.status] ?? item.status} tone={statusTone[item.status] ?? 'neutral'} /></td>
                    <td className="is-num">
                      {isActive(item) ? <Deadline due={item.decision_due_at} asOf={asOf} /> : <span className="sd-ov-zero">—</span>}
                    </td>
                    <td className="sd-ov-go"><ChevronRight aria-hidden="true" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="Nessun caso trovato"
            description="Nessun caso pubblicato corrisponde ai filtri. Le fonti acquisite non implicano automaticamente un caso."
          />
        )}
      </Card>
    </div>
  )
}
