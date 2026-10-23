import { useEffect, useMemo, useRef } from 'react'
import { Clock3, Search } from 'lucide-react'
import type { Case } from '../api/client'
import { Button, EmptyState, Input, Select, StatusBadge } from '../ui'
import {
  caseKey,
  DEFAULT_CASE_QUEUE_FILTERS,
  isPastDeadline,
  uncertaintyReasons
} from './caseUtils'
import type { CaseQueueFilters, CaseSelection } from './caseUtils'
import { CaseDetail } from './CaseDetail'
import { ownerLabel } from './caseLabels'
import { caseTypeLabel } from './productView'
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
  value
    ? `${new Date(value).toLocaleString('it-IT', { timeZone: 'UTC', dateStyle: 'short', timeStyle: 'short' })} UTC`
    : 'Non disponibile'

const dueTime = (item: Case) => {
  const time = item.decision_due_at ? Date.parse(item.decision_due_at) : NaN
  return Number.isFinite(time) ? time : Infinity
}

const deadlineLabel = (value: string | null | undefined) =>
  value ? date(value) : 'Senza scadenza'

type Props = {
  cases: Case[]
  stores: string[]
  asOf: string
  runId: string
  fixtureMode: boolean
  selection: CaseSelection | null
  onSelect: (item: Case) => void
  onReturn: () => void
  filters: CaseQueueFilters
  onFiltersChange: (filters: CaseQueueFilters) => void
}

export function CaseQueue({
  cases,
  stores,
  asOf,
  runId,
  fixtureMode,
  selection,
  onSelect,
  onReturn,
  filters,
  onFiltersChange
}: Props) {
  const selected = selection
    ? cases.find(
        (item) => item.id === selection.id && item.version === selection.version
      ) ?? null
    : null
  const detailHeading = useRef<HTMLHeadingElement>(null)
  const queueHeading = useRef<HTMLHeadingElement>(null)
  const rowButtons = useRef(new Map<string, HTMLButtonElement>())
  const previousSelection = useRef<string | null>(
    selection ? `${selection.id}\u0000${selection.version}` : null
  )
  const returnFocusKey = useRef<string | null>(null)
  const savedScrollTop = useRef(0)

  useEffect(() => {
    const currentKey = selected ? caseKey(selected) : null
    const main = document.querySelector<HTMLElement>('.sd-shell__main')
    if (currentKey) {
      requestAnimationFrame(() => {
        main?.scrollTo({ top: 0 })
        detailHeading.current?.focus({ preventScroll: true })
      })
    } else if (previousSelection.current) {
      requestAnimationFrame(() => {
        if (main) main.scrollTop = savedScrollTop.current
        const button = returnFocusKey.current
          ? rowButtons.current.get(returnFocusKey.current)
          : null
        ;(button ?? queueHeading.current)?.focus({ preventScroll: true })
        returnFocusKey.current = null
      })
    }
    previousSelection.current = currentKey
  }, [selected])

  const visibleCases = useMemo(() => {
    const query = filters.search.trim().toLocaleLowerCase('it-IT')
    return cases
      .filter((item) => {
        const hasUncertainty = uncertaintyReasons(item).length > 0
        const pastDeadline = isPastDeadline(item.decision_due_at, asOf)
        return (
          (filters.store === 'all' || item.store_id === filters.store) &&
          (filters.owner === 'all' || item.owner === filters.owner) &&
          (filters.product === 'all' ||
            (filters.product === 'unknown'
              ? !item.scope_id
              : item.scope_id === filters.product)) &&
          (filters.priority === 'all' || item.priority === filters.priority) &&
          (filters.status === 'all' || item.status === filters.status) &&
          (filters.deadline === 'all' ||
            (filters.deadline === 'dated' && Boolean(item.decision_due_at)) ||
            (filters.deadline === 'undated' && !item.decision_due_at) ||
            (filters.deadline === 'past' && pastDeadline)) &&
          (filters.uncertainty === 'all' ||
            (filters.uncertainty === 'open' && hasUncertainty) ||
            (filters.uncertainty === 'clear' && !hasUncertainty)) &&
          (query === '' ||
            [
              item.id,
              item.store_id,
              item.scope_id,
              item.case_type,
              item.owner,
              item.status,
              item.priority_reason,
              ...uncertaintyReasons(item),
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
      .sort((a, b) => {
        const byPriority = priorityOrder[a.priority] - priorityOrder[b.priority]
        const byDeadline = dueTime(a) - dueTime(b)
        return filters.sort === 'deadline'
          ? byDeadline || byPriority
          : byPriority || byDeadline
      })
  }, [asOf, cases, filters])

  const updateFilter = (key: keyof CaseQueueFilters, value: string) =>
    onFiltersChange({ ...filters, [key]: value })
  const returnToQueue = () => {
    onReturn()
  }
  const resetFilters = () => onFiltersChange(DEFAULT_CASE_QUEUE_FILTERS)

  if (selected) {
    return (
      <CaseDetail item={selected} runId={runId} asOf={asOf} fixtureMode={fixtureMode}
        onReturn={returnToQueue} headingRef={detailHeading} />
    )
  }

  const owners = [...new Set(cases.map((item) => item.owner))].sort()
  const products = [...new Set(cases.flatMap((item) => item.scope_id ? [item.scope_id] : []))].sort()
  if (!cases.length) {
    return (
      <div className="sd-case-queue">
        <h2 id="sd-case-queue-title" className="sd-case-queue__title" tabIndex={-1} ref={queueHeading}>Coda dei casi</h2>
        <EmptyState title="Nessun caso pubblicato" description="Il run selezionato non contiene casi." />
      </div>
    )
  }

  return (
    <div className="sd-case-queue">
      <h2 id="sd-case-queue-title" className="sd-case-queue__title" tabIndex={-1} ref={queueHeading}>Coda dei casi</h2>
      <form className="sd-case-queue__filters" role="search" onSubmit={(event) => event.preventDefault()}>
        <Input size="sm" label="Cerca casi" type="search" icon={<Search />} placeholder="Negozio, prodotto, fonte o incertezza" value={filters.search} onChange={(event) => updateFilter('search', event.target.value)} />
        <Select size="sm" label="Negozio" value={filters.store} onValueChange={(value) => updateFilter('store', value)} options={[{ value: 'all', label: 'Tutti i negozi' }, ...stores.map((id) => ({ value: id, label: id }))]} />
        <Select size="sm" label="Ufficio" value={filters.owner} onValueChange={(value) => updateFilter('owner', value)} options={[{ value: 'all', label: 'Tutti gli uffici' }, ...owners.map((owner) => ({ value: owner, label: ownerLabel(owner) }))]} />
        <Select size="sm" label="Prodotto" value={filters.product} onValueChange={(value) => updateFilter('product', value)} options={[{ value: 'all', label: 'Tutti i prodotti' }, { value: 'unknown', label: 'Prodotto da identificare' }, ...products.map((product) => ({ value: product, label: product }))]} />
        <Select size="sm" label="Priorità" value={filters.priority} onValueChange={(value) => updateFilter('priority', value)} options={[{ value: 'all', label: 'Tutte le priorità' }, ...Object.entries(priorities).map(([value, label]) => ({ value, label }))]} />
        <Select size="sm" label="Scadenza" value={filters.deadline} onValueChange={(value) => updateFilter('deadline', value)} options={[{ value: 'all', label: 'Tutte le scadenze' }, { value: 'dated', label: 'Con scadenza' }, { value: 'past', label: 'Scaduta al cutoff' }, { value: 'undated', label: 'Senza scadenza' }]} />
        <Select size="sm" label="Incertezza" value={filters.uncertainty} onValueChange={(value) => updateFilter('uncertainty', value)} options={[{ value: 'all', label: 'Tutte' }, { value: 'open', label: 'Con incertezze bloccanti' }, { value: 'clear', label: 'Senza incertezze' }]} />
        <Select size="sm" label="Stato" value={filters.status} onValueChange={(value) => updateFilter('status', value)} options={[{ value: 'all', label: 'Tutti gli stati' }, ...Object.entries(statuses).map(([value, label]) => ({ value, label }))]} />
        <Select size="sm" label="Ordina per" value={filters.sort} onValueChange={(value) => updateFilter('sort', value)} options={[{ value: 'priority', label: 'Priorità' }, { value: 'deadline', label: 'Scadenza più vicina' }]} />
      </form>
      <p className="sd-case-queue__count" role="status">{visibleCases.length} {visibleCases.length === 1 ? 'caso' : 'casi'} · scadenze valutate al cutoff del run</p>
      {visibleCases.length ? (
        <ul className="sd-case-queue__list" aria-labelledby="sd-case-queue-title">
          {visibleCases.map((item) => {
            const itemKey = caseKey(item)
            const uncertainties = uncertaintyReasons(item)
            const overdue = isPastDeadline(item.decision_due_at, asOf)
            const deadline = overdue
              ? `Scaduta · ${deadlineLabel(item.decision_due_at)}`
              : deadlineLabel(item.decision_due_at)
            const uncertaintyLabel = uncertainties.length === 1
              ? '1 verifica aperta'
              : `${uncertainties.length} verifiche aperte`
            return (
              <li key={itemKey}>
                <button
                  ref={(node) => {
                    if (node) rowButtons.current.set(itemKey, node)
                    else rowButtons.current.delete(itemKey)
                  }}
                  className="sd-case-queue__item"
                  type="button"
                  aria-label={`Apri caso ${item.id}. Priorità: ${priorities[item.priority]}. Stato: ${statuses[item.status]}. Scadenza: ${deadline}. Incertezze: ${uncertainties.length}.`}
                  onClick={() => {
                    returnFocusKey.current = itemKey
                    savedScrollTop.current = document.querySelector<HTMLElement>('.sd-shell__main')?.scrollTop ?? 0
                    onSelect(item)
                  }}
                >
                  <span className="sd-case-queue__identity">
                    <strong>{item.store_id ?? 'Negozio da verificare'} · {item.scope_id ?? 'Prodotto da identificare'}</strong>
                    <span>{caseTypeLabel(item.case_type)} · {ownerLabel(item.owner)}</span>
                  </span>
                  <span className="sd-case-queue__summary">
                    <StatusBadge tone={item.priority === 'critical' ? 'danger' : item.priority === 'high' ? 'warning' : 'neutral'} label={priorities[item.priority]} />
                    <StatusBadge tone={item.status === 'verify' ? 'warning' : 'neutral'} label={statuses[item.status]} />
                    <StatusBadge tone={uncertainties.length ? 'warning' : 'success'} label={uncertainties.length ? uncertaintyLabel : 'Senza incertezze'} />
                  </span>
                  <span className={overdue ? 'sd-case-queue__deadline is-past' : 'sd-case-queue__deadline'}>
                    {item.decision_due_at ? <>
                      <span><Clock3 aria-hidden="true" />{overdue ? 'Scaduta' : 'Scadenza'}</span>
                      <strong className="sd-num">{deadlineLabel(item.decision_due_at)}</strong>
                    </> : <span>Senza scadenza</span>}
                  </span>
                  <span className="sd-case-queue__reason">{item.priority_reason}</span>
                </button>
              </li>
            )
          })}
        </ul>
      ) : (
        <EmptyState
          title="Nessun caso trovato"
          description="Nessun caso corrisponde ai filtri selezionati."
          action={<Button onClick={resetFilters}>Azzera filtri</Button>}
        />
      )}
    </div>
  )
}
