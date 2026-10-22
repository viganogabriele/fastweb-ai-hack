import { useMemo, useState } from 'react'
import { ArrowLeft, CircleAlert, Clock3, Search } from 'lucide-react'
import type { Case } from '../api/client'
import { Button, EmptyState, Input, Select, StatusBadge } from '../ui'
import './sections.css'

const statuses: Record<Case['status'], string> = {
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

const priorityOrder: Record<Case['priority'], number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3
}

const date = (value: string | null | undefined) =>
  value ? new Date(value).toLocaleString('it-IT') : 'Non disponibile'

type Props = {
  cases: Case[]
  stores: string[]
  asOf: string
}

export function CaseQueue({ cases, stores, asOf }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [store, setStore] = useState('all')
  const [priority, setPriority] = useState('all')
  const [deadline, setDeadline] = useState('all')
  const [uncertainty, setUncertainty] = useState('all')
  const [sort, setSort] = useState('priority')

  const selected = cases.find((item) => item.id === selectedId) ?? null
  const visibleCases = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('it-IT')
    return cases
      .filter((item) => {
        const hasDeadline = Boolean(item.decision_due_at)
        const isPastCutoff = Boolean(
          item.decision_due_at && item.decision_due_at < asOf
        )
        return (
          (store === 'all' || item.store_id === store) &&
          (priority === 'all' || item.priority === priority) &&
          (deadline === 'all' ||
            (deadline === 'dated' && hasDeadline) ||
            (deadline === 'undated' && !hasDeadline) ||
            (deadline === 'past' && isPastCutoff)) &&
          (uncertainty === 'all' ||
            (uncertainty === 'open' && item.blocking_uncertainties.length > 0) ||
            (uncertainty === 'clear' && item.blocking_uncertainties.length === 0)) &&
          (query === '' ||
            [
              item.id,
              item.store_id,
              item.scope_id,
              item.case_type,
              item.owner,
              item.priority_reason,
              ...item.blocking_uncertainties,
              ...item.source_refs.flatMap((source) => [
                source.uri,
                source.locator
              ])
            ]
              .join(' ')
              .toLocaleLowerCase('it-IT')
              .includes(query))
        )
      })
      .sort((a, b) =>
        sort === 'deadline'
          ? (a.decision_due_at ?? '9999').localeCompare(
              b.decision_due_at ?? '9999'
            ) || priorityOrder[a.priority] - priorityOrder[b.priority]
          : priorityOrder[a.priority] - priorityOrder[b.priority] ||
            (a.decision_due_at ?? '9999').localeCompare(
              b.decision_due_at ?? '9999'
            )
      )
  }, [asOf, cases, deadline, priority, search, sort, store, uncertainty])

  if (selected) {
    const overdue = Boolean(
      selected.decision_due_at && selected.decision_due_at < asOf
    )
    return (
      <article className="sd-case-detail" aria-labelledby="sd-case-detail-title">
        <Button
          variant="ghost"
          size="sm"
          icon={<ArrowLeft />}
          onClick={() => setSelectedId(null)}
        >
          Torna alla coda
        </Button>
        <header className="sd-case-detail__header">
          <div>
            <p className="sd-case-detail__eyebrow">
              {selected.store_id ?? 'Negozio da verificare'} · {selected.case_type}
            </p>
            <h2 id="sd-case-detail-title">
              {selected.scope_id ?? 'Prodotto da identificare'}
            </h2>
            <p>{selected.priority_reason}</p>
          </div>
          <div className="sd-case-detail__badges">
            <StatusBadge
              tone={selected.priority === 'critical' || selected.priority === 'high' ? 'warning' : 'neutral'}
              label={priorities[selected.priority]}
            />
            <StatusBadge
              tone={selected.status === 'verify' ? 'warning' : 'neutral'}
              label={statuses[selected.status]}
            />
          </div>
        </header>

        <dl className="sd-case-detail__facts">
          <div><dt>Responsabile</dt><dd>{selected.owner}</dd></div>
          <div><dt>Scadenza decisione</dt><dd>{date(selected.decision_due_at)}</dd></div>
          <div><dt>Finestra del caso</dt><dd>{date(selected.window_start)} – {date(selected.window_end)}</dd></div>
          <div><dt>Documenti / origini note</dt><dd>{selected.n_documents} / {selected.n_origin_groups}</dd></div>
          <div><dt>Origini sconosciute</dt><dd>{selected.n_unknown_origins}</dd></div>
          <div><dt>Ultima evidenza indipendente</dt><dd>{date(selected.last_independent_evidence_at)}</dd></div>
        </dl>

        <div className="sd-case-detail__sections">
          <section aria-labelledby="sd-case-verifications">
            <h3 id="sd-case-verifications"><CircleAlert aria-hidden="true" /> Verifiche aperte</h3>
            {selected.blocking_uncertainties.length ? (
              <ul className="sd-case-detail__uncertainties">
                {selected.blocking_uncertainties.map((item) => <li key={item}>{item}</li>)}
              </ul>
            ) : <p>Nessuna incertezza bloccante registrata.</p>}
            {overdue && <p className="sd-case-detail__note"><Clock3 aria-hidden="true" /> Scadenza precedente al cutoff del run ({date(asOf)}).</p>}
          </section>
          <section aria-labelledby="sd-case-evidence">
            <h3 id="sd-case-evidence">Evidenze collegate</h3>
            <RefList title="A supporto" refs={selected.supporting} />
            <RefList title="In conflitto" refs={selected.contradicting} />
            <RefList title="Contesto e link" refs={selected.context_refs} />
          </section>
          <section aria-labelledby="sd-case-sources">
            <h3 id="sd-case-sources">Fonti del caso</h3>
            {selected.source_refs.length ? (
              <ul className="sd-case-detail__sources">
                {selected.source_refs.map((source, index) => (
                  <li key={`${source.uri}-${source.locator ?? index}`}>
                    <code>{source.uri}</code>
                    {source.locator && <span>{source.locator}</span>}
                  </li>
                ))}
              </ul>
            ) : <p>Nessun riferimento di fonte disponibile.</p>}
          </section>
        </div>
        <p className="sd-case-detail__provenance">Caso {selected.id} · {selected.version} · disponibile dal {date(selected.available_at)}</p>
      </article>
    )
  }

  return (
    <div className="sd-case-queue">
      <form className="sd-case-queue__filters" role="search" onSubmit={(event) => event.preventDefault()}>
        <Input size="sm" label="Cerca casi" type="search" icon={<Search />} placeholder="Negozio, prodotto, fonte o incertezza" value={search} onChange={(event) => setSearch(event.target.value)} />
        <Select size="sm" label="Negozio" value={store} onValueChange={setStore} options={[{ value: 'all', label: 'Tutti i negozi' }, ...stores.map((id) => ({ value: id, label: id }))]} />
        <Select size="sm" label="Priorità" value={priority} onValueChange={setPriority} options={[{ value: 'all', label: 'Tutte le priorità' }, ...Object.entries(priorities).map(([value, label]) => ({ value, label }))]} />
        <Select size="sm" label="Scadenza" value={deadline} onValueChange={setDeadline} options={[{ value: 'all', label: 'Tutte le scadenze' }, { value: 'dated', label: 'Con scadenza' }, { value: 'past', label: 'Scaduta al cutoff' }, { value: 'undated', label: 'Senza scadenza' }]} />
        <Select size="sm" label="Incertezza" value={uncertainty} onValueChange={setUncertainty} options={[{ value: 'all', label: 'Tutte' }, { value: 'open', label: 'Da verificare' }, { value: 'clear', label: 'Nessun blocco' }]} />
        <Select size="sm" label="Ordina per" value={sort} onValueChange={setSort} options={[{ value: 'priority', label: 'Priorità' }, { value: 'deadline', label: 'Scadenza più vicina' }]} />
      </form>
      <p className="sd-case-queue__count" role="status">{visibleCases.length} {visibleCases.length === 1 ? 'caso' : 'casi'} · scadenze valutate al cutoff del run</p>
      {visibleCases.length ? (
        <ul className="sd-case-queue__list" aria-label="Coda dei casi">
          {visibleCases.map((item) => (
            <li key={`${item.id}-${item.version}`}>
              <button className="sd-case-queue__item" type="button" onClick={() => setSelectedId(item.id)}>
                <span className="sd-case-queue__identity">
                  <strong>{item.store_id ?? 'Negozio da verificare'} · {item.scope_id ?? 'Prodotto da identificare'}</strong>
                  <span>{item.case_type} · {item.owner}</span>
                </span>
                <span className="sd-case-queue__summary">
                  <StatusBadge tone={item.priority === 'critical' || item.priority === 'high' ? 'warning' : 'neutral'} label={priorities[item.priority]} />
                  <span className={item.decision_due_at && item.decision_due_at < asOf ? 'sd-case-queue__deadline is-past' : 'sd-case-queue__deadline'}>
                    <Clock3 aria-hidden="true" /> {date(item.decision_due_at)}
                  </span>
                  <StatusBadge tone={item.blocking_uncertainties.length ? 'warning' : 'success'} label={item.blocking_uncertainties.length ? `${item.blocking_uncertainties.length} verifiche aperte` : 'Nessun blocco'} />
                </span>
                <span className="sd-case-queue__reason">{item.priority_reason}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState title="Nessun caso trovato" description="Modifica o azzera i filtri. Le fonti acquisite non implicano automaticamente un caso." />
      )}
    </div>
  )
}

function RefList({ title, refs }: { title: string; refs: Case['supporting'] }) {
  return (
    <div className="sd-case-detail__ref-group">
      <h4>{title}</h4>
      {refs.length ? (
        <ul>{refs.map((ref) => <li key={`${ref.kind}-${ref.id}-${ref.version}`}><code>{ref.kind}</code> · {ref.id} · {ref.version}</li>)}</ul>
      ) : <p>Nessuna registrata.</p>}
    </div>
  )
}
