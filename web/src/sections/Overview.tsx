import { useState } from 'react'
import { ArrowUpRight, Search } from 'lucide-react'
import type { Case, RunView, SourceDocument } from '../api/client'
import { Button, EmptyState, Input, Select, StatusBadge } from '../ui'
import type { StatusTone } from '../ui/StatusBadge'
import './overview.css'

const statuses: Record<string, string> = {
  open: 'Aperto',
  verify: 'Da verificare',
  monitor: 'Monitoraggio',
  action_proposed: 'Azione proposta',
  decided: 'Deciso',
  closed: 'Chiuso'
}
const priorities: Record<Case['priority'], string> = {
  critical: 'Critica',
  high: 'Alta',
  medium: 'Media',
  low: 'Bassa'
}
const priorityTone: Record<Case['priority'], StatusTone> = {
  critical: 'danger',
  high: 'warning',
  medium: 'info',
  low: 'neutral'
}
const priorityOrder: Record<Case['priority'], number> = { critical: 0, high: 1, medium: 2, low: 3 }
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
  demand_shift: 'Variazione della domanda',
  traffic_change: 'Variazione del traffico',
  operational_issue: 'Problema operativo',
  customer_profile: 'Profilo cliente'
}
const label = (map: Record<string, string>, key: string) => map[key] ?? key.replaceAll('_', ' ')
const HOUR = 3600_000

const dateTime = (value: string | null | undefined) =>
  value ? new Date(value).toLocaleString('it-IT', { dateStyle: 'medium', timeStyle: 'short' }) : 'Non disponibile'

/** Time left before a decision deadline, measured from the run cutoff (never from "now"). */
function untilDeadline(due: string | null | undefined, asOf: number) {
  if (!due) return { text: 'Senza scadenza', urgent: false, past: false }
  const hours = Math.round((Date.parse(due) - asOf) / HOUR)
  if (hours < 0) return { text: `Scaduta da ${Math.abs(hours)} h`, urgent: true, past: true }
  if (hours < 48) return { text: `Tra ${hours} h`, urgent: hours <= 24, past: false }
  return { text: `Tra ${Math.round(hours / 24)} giorni`, urgent: false, past: false }
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
  const asOf = Date.parse(run.spec.as_of)
  const active = cases.filter((item) => item.status !== 'closed' && item.status !== 'decided')
  const dueSoon = active
    .filter((item) => item.decision_due_at && Date.parse(item.decision_due_at) - asOf <= 48 * HOUR)
    .sort((a, b) => Date.parse(a.decision_due_at!) - Date.parse(b.decision_due_at!))
  const urgent = active.filter((item) => priorityOrder[item.priority] <= 1)
  const byPriority = (Object.keys(priorities) as Case['priority'][]).map((key) => ({
    key,
    count: active.filter((item) => item.priority === key).length
  }))
  const byOwner = Object.entries(
    active.reduce<Record<string, number>>((acc, item) => ({ ...acc, [item.owner]: (acc[item.owner] ?? 0) + 1 }), {})
  ).sort((a, b) => b[1] - a[1])
  const maxOwner = Math.max(1, ...byOwner.map(([, count]) => count))
  const stores = run.spec.stores
    .map((id) => {
      const own = active.filter((item) => item.store_id === id)
      const next = own
        .map((item) => item.decision_due_at)
        .filter((value): value is string => Boolean(value))
        .sort()[0]
      return {
        id,
        open: own.length,
        urgent: own.filter((item) => priorityOrder[item.priority] <= 1).length,
        verify: own.filter((item) => item.status === 'verify').length,
        next
      }
    })
    .sort((a, b) => b.urgent - a.urgent || b.open - a.open || a.id.localeCompare(b.id))

  const query = search.trim().toLocaleLowerCase('it-IT')
  const visible = cases
    .filter(
      (item) =>
        (store === 'all' || item.store_id === store) &&
        [item.store_id, item.scope_id, item.case_type, label(caseTypes, item.case_type), item.owner, item.priority_reason]
          .join(' ')
          .toLocaleLowerCase('it-IT')
          .includes(query)
    )
    .sort(
      (a, b) =>
        priorityOrder[a.priority] - priorityOrder[b.priority] ||
        (a.decision_due_at ?? '9999').localeCompare(b.decision_due_at ?? '9999')
    )

  const kpis: { label: string; value: number; note: string; tone?: 'signature' | 'warning' }[] = [
    { label: 'Casi aperti', value: active.length, note: `${cases.length - active.length} chiusi o decisi` },
    { label: 'Priorità alta', value: urgent.length, note: 'critica o alta', tone: urgent.length ? 'signature' : undefined },
    { label: 'In scadenza', value: dueSoon.length, note: 'entro 48 ore dal cutoff', tone: dueSoon.length ? 'warning' : undefined },
    { label: 'Da verificare', value: active.filter((item) => item.status === 'verify').length, note: 'incertezze bloccanti' },
    { label: 'Fonti', value: documents.length, note: 'email, note vocali, chat' },
    { label: 'Negozi', value: run.spec.stores.length, note: 'nel perimetro del run' }
  ]

  return (
    <div className="sd-overview">
      <dl className="sd-overview__kpis">
        {kpis.map((item) => (
          <div key={item.label} className={item.tone ? `sd-overview__kpi is-${item.tone}` : 'sd-overview__kpi'}>
            <dt>{item.label}</dt>
            <dd>
              <strong>{item.value}</strong>
              <span>{item.note}</span>
            </dd>
          </div>
        ))}
      </dl>

      <div className="sd-overview__grid">
        <section className="sd-overview__panel sd-overview__due" aria-labelledby="sd-overview-due">
          <header>
            <h2 id="sd-overview-due">Da decidere</h2>
            <p>Casi aperti con scadenza entro 48 ore dal cutoff del run</p>
          </header>
          {dueSoon.length ? (
            <ol>
              {dueSoon.slice(0, 6).map((item) => {
                const left = untilDeadline(item.decision_due_at, asOf)
                return (
                  <li key={`${item.id}-${item.version}`}>
                    <button type="button" onClick={() => onCaseSelect(item)}>
                      <span className={left.urgent ? 'sd-overview__clock is-urgent' : 'sd-overview__clock'}>{left.text}</span>
                      <span className="sd-overview__due-body">
                        <strong>
                          {item.store_id ?? 'Negozio da verificare'} · {label(caseTypes, item.case_type)}
                        </strong>
                        <span>{item.priority_reason}</span>
                      </span>
                      <StatusBadge label={priorities[item.priority]} tone={priorityTone[item.priority]} />
                      <ArrowUpRight className="sd-overview__go" aria-hidden="true" />
                    </button>
                  </li>
                )
              })}
            </ol>
          ) : (
            <p className="sd-overview__quiet">Nessuna decisione in scadenza nelle prossime 48 ore.</p>
          )}
        </section>

        <div className="sd-overview__side">
          <section className="sd-overview__panel" aria-labelledby="sd-overview-priority">
            <header>
              <h2 id="sd-overview-priority">Priorità</h2>
              <p>{active.length} casi aperti</p>
            </header>
            <div className="sd-overview__stack" aria-hidden="true">
              {byPriority.map(({ key, count }) =>
                count ? <span key={key} className={`is-${key}`} style={{ flexGrow: count }} /> : null
              )}
            </div>
            <ul className="sd-overview__legend">
              {byPriority.map(({ key, count }) => (
                <li key={key}>
                  <span className={`sd-overview__swatch is-${key}`} aria-hidden="true" />
                  {priorities[key]}
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          </section>

          <section className="sd-overview__panel" aria-labelledby="sd-overview-owner">
            <header>
              <h2 id="sd-overview-owner">Per ufficio</h2>
              <p>Chi riceve i casi aperti</p>
            </header>
            <ul className="sd-overview__bars">
              {byOwner.map(([owner, count]) => (
                <li key={owner}>
                  <span>{label(owners, owner)}</span>
                  <span className="sd-overview__bar" aria-hidden="true">
                    <span style={{ inlineSize: `${(count / maxOwner) * 100}%` }} />
                  </span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>

      <section className="sd-overview__panel" aria-labelledby="sd-overview-stores">
        <header>
          <h2 id="sd-overview-stores">Negozi</h2>
          <p>Ordinati per casi a priorità alta. Seleziona un negozio per filtrare le segnalazioni.</p>
        </header>
        <div className="sd-overview__table-wrap">
          <table className="sd-overview__table">
            <thead>
              <tr>
                <th scope="col">Negozio</th>
                <th scope="col">Aperti</th>
                <th scope="col">Priorità alta</th>
                <th scope="col">Da verificare</th>
                <th scope="col">Prossima scadenza</th>
              </tr>
            </thead>
            <tbody>
              {stores.map((row) => (
                <tr key={row.id} aria-selected={store === row.id}>
                  <th scope="row">
                    <button type="button" onClick={() => setStore(store === row.id ? 'all' : row.id)}>
                      {row.id}
                    </button>
                  </th>
                  <td>{row.open}</td>
                  <td className={row.urgent ? 'is-signature' : undefined}>{row.urgent}</td>
                  <td>{row.verify}</td>
                  <td>{row.next ? untilDeadline(row.next, asOf).text : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="sd-overview__cases" aria-labelledby="sd-overview-cases">
        <header className="sd-overview__cases-head">
          <h2 id="sd-overview-cases">Segnalazioni da valutare</h2>
          <form className="sd-overview__filters" role="search" onSubmit={(event) => event.preventDefault()}>
            <Input
              size="sm"
              label="Cerca caso"
              type="search"
              icon={<Search />}
              placeholder="Negozio, prodotto o motivo"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <Select
              size="sm"
              label="Negozio"
              value={store}
              onValueChange={setStore}
              options={[{ value: 'all', label: 'Tutti i negozi' }, ...run.spec.stores.map((id) => ({ value: id, label: id }))]}
            />
          </form>
        </header>
        {visible.length ? (
          <ul className="sd-overview__case-list">
            {visible.map((item) => {
              const settled = item.status === 'closed' || item.status === 'decided'
              const left = settled
                ? { text: statuses[item.status], past: false }
                : untilDeadline(item.decision_due_at, asOf)
              return (
                <li key={`${item.id}-${item.version}`}>
                  <details className="sd-overview__case">
                    <summary>
                      <span className={`sd-overview__rule is-${item.priority}`} aria-hidden="true" />
                      <span className="sd-overview__case-title">
                        <span className="sd-overview__eyebrow">
                          {item.store_id ?? 'Negozio da verificare'} · {label(caseTypes, item.case_type)}
                        </span>
                        <strong>{item.scope_id ?? 'Prodotto da identificare'}</strong>
                      </span>
                      <span className="sd-overview__case-meta">
                        <span className={left.past ? 'is-past' : undefined}>{left.text}</span>
                        <StatusBadge label={priorities[item.priority]} tone={priorityTone[item.priority]} />
                        <StatusBadge
                          label={statuses[item.status] ?? item.status}
                          tone={item.status === 'verify' ? 'warning' : 'neutral'}
                        />
                      </span>
                    </summary>
                    <div className="sd-overview__case-body">
                      <p className="sd-overview__reason">{item.priority_reason}</p>
                      <dl>
                        <div><dt>Ufficio</dt><dd>{label(owners, item.owner)}</dd></div>
                        <div><dt>Scadenza decisione</dt><dd>{dateTime(item.decision_due_at)}</dd></div>
                        <div><dt>Documenti / origini indipendenti</dt><dd>{item.n_documents} / {item.n_origin_groups}</dd></div>
                        <div><dt>Finestra</dt><dd>{dateTime(item.window_start)} – {dateTime(item.window_end)}</dd></div>
                      </dl>
                      {item.blocking_uncertainties.length ? (
                        <div className="sd-overview__uncertain">
                          <h3>Incertezze da risolvere</h3>
                          <ul>
                            {item.blocking_uncertainties.map((text) => <li key={text}>{text}</li>)}
                          </ul>
                        </div>
                      ) : null}
                      <Button size="sm" variant="primary" onClick={() => onCaseSelect(item)}>
                        Apri il caso
                      </Button>
                    </div>
                  </details>
                </li>
              )
            })}
          </ul>
        ) : (
          <EmptyState
            title="Nessun caso trovato"
            description="Non ci sono casi pubblicati per questa selezione. Le fonti acquisite non implicano automaticamente un caso."
          />
        )}
      </section>
    </div>
  )
}
