import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import { readApi } from '../api/client'
import type { Case } from '../api/client'
import type { useRuns } from '../api/useRuns'
import { Button, EmptyState, ErrorState, Input, LoadingState, Select, StatusBadge } from '../ui'
import { caseStatuses, caseTypeLabel, filterProductCases, productIndex, productScopes } from './productView'
import type { ProductFilters } from './productView'
import './sections.css'
import './products.css'

const initialFilters: ProductFilters = { search: '', store: 'all', status: 'all', type: 'all' }

export function ProductsPage({ runs, onCaseSelect }: {
  runs: ReturnType<typeof useRuns>
  onCaseSelect: (item: Case) => void
}) {
  const run = runs.selected
  if (runs.loading) return <LoadingState label="Caricamento run" />
  if (runs.error) return <ErrorState title="Impossibile caricare i run" description={runs.error} onRetry={runs.retry} />
  if (!run) return <EmptyState title="Nessun run disponibile" description="I prodotti compariranno dopo la pubblicazione di un’elaborazione." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  if (!run.published) return <EmptyState title="Run non pubblicato" description="La vista prodotti sarà disponibile quando l’elaborazione sarà pubblicata." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  return <PublishedProducts key={run.spec.run_id} runId={run.spec.run_id} mode={run.spec.mode} onCaseSelect={onCaseSelect} />
}

function PublishedProducts({ runId, mode, onCaseSelect }: {
  runId: string
  mode: string
  onCaseSelect: (item: Case) => void
}) {
  const [data, setData] = useState<Case[] | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [filters, setFilters] = useState(initialFilters)
  useEffect(() => {
    const controller = new AbortController()
    readApi<Case[]>(`/runs/${encodeURIComponent(runId)}/cases`, controller.signal)
      .then((result) => { if (!controller.signal.aborted) setData(result) })
      .catch((failure: Error) => { if (!controller.signal.aborted) setError(failure.message) })
    return () => controller.abort()
  }, [runId, revision])

  if (error) return <ErrorState title="Impossibile caricare i prodotti" description={error} onRetry={() => {
    setData(null)
    setError('')
    setRevision((value) => value + 1)
  }} />
  if (!data) return <LoadingState label="Caricamento prodotti" />

  const index = productIndex(data, runId)
  const allCases = [...index.groups.flatMap((group) => group.cases), ...index.unresolved]
  const groups = index.groups.map((group) => ({ ...group, cases: filterProductCases(group.cases, filters) }))
    .filter((group) => group.cases.length > 0)
  const unresolved = filterProductCases(index.unresolved, filters)
  const stores = [...new Set(allCases.flatMap((item) => item.store_id ? [item.store_id] : []))].sort()
  const types = [...new Set(allCases.map((item) => item.case_type))].sort()
  const update = (name: keyof ProductFilters, value: string) => setFilters((current) => ({ ...current, [name]: value }))
  const filteredCount = groups.reduce((count, group) => count + group.cases.length, 0) + unresolved.length

  return (
    <div className="sd-products">
      <section className="sd-run-card" aria-labelledby="sd-products-summary">
        <h2 id="sd-products-summary">Segnali per prodotto</h2>
        <p>Prodotti identificati nei casi del run selezionato, con negozi, motivazioni e fonti consultabili nel dettaglio del caso.</p>
        <p>I conteggi indicano casi, non clienti, unità richieste o vendite perse. I motivi riportati non dimostrano un rapporto di causa ed effetto.</p>
        {mode === 'fixture' && <StatusBadge tone="warning" label="Dati fixture · esempi dimostrativi" />}
        <dl className="sd-products__metrics">
          <div><dt>Prodotti identificati</dt><dd>{index.groups.length}</dd></div>
          <div><dt>Casi collegati a prodotti</dt><dd>{allCases.length - index.unresolved.length}</dd></div>
          <div><dt>Casi senza prodotto identificato</dt><dd>{index.unresolved.length}</dd></div>
        </dl>
      </section>
      <aside className="sd-products__availability" aria-label="Disponibilità dei dati">
        <strong>Vendite e resi quantitativi: non disponibili</strong>
        <p>Questi dati non sono esposti nei risultati di questo run. Non è possibile calcolare conversioni o confrontare vendite e motivi riportati. Assenza di casi non significa assenza di domanda.</p>
      </aside>
      {allCases.length === 0 ? <EmptyState title="Nessun caso nel run" description="Non ci sono segnali da mostrare per prodotto in questa elaborazione." /> : <>
        <div className="sd-case-queue__filters" role="search" aria-label="Filtra prodotti e casi">
          <Input label="Cerca prodotto o motivo" type="search" icon={<Search />} value={filters.search} onChange={(event) => update('search', event.target.value)} />
          <Select label="Negozio" value={filters.store} options={[{ value: 'all', label: 'Tutti i negozi' }, ...stores.map((value) => ({ value, label: value }))]} onValueChange={(value) => update('store', value)} />
          <Select label="Stato del caso" value={filters.status} options={[{ value: 'all', label: 'Tutti gli stati' }, ...Object.entries(caseStatuses).map(([value, label]) => ({ value, label }))]} onValueChange={(value) => update('status', value)} />
          <Select label="Tipo di segnale" value={filters.type} options={[{ value: 'all', label: 'Tutti i segnali' }, ...types.map((value) => ({ value, label: caseTypeLabel(value) }))]} onValueChange={(value) => update('type', value)} />
          <Button variant="ghost" onClick={() => setFilters(initialFilters)}>Azzera filtri</Button>
        </div>
        <p className="sd-case-queue__count" role="status">{groups.length} prodotti · {filteredCount} casi nei filtri · {unresolved.length} senza prodotto identificato</p>
        {filteredCount === 0 && <EmptyState title="Nessun risultato" description="Modifica o azzera i filtri per vedere gli altri prodotti e casi del run." action={<Button onClick={() => setFilters(initialFilters)}>Azzera filtri</Button>} />}
        <div className="sd-products__list">
          {groups.map((group) => <article className="sd-run-card sd-products__product" key={group.key} aria-label={`${productScopes[group.level]} ${group.id}`}>
            <header><h2>{group.id}</h2><StatusBadge tone="neutral" label={productScopes[group.level]} /></header>
            <p>{group.cases.length} casi · {[...new Set(group.cases.map((item) => item.store_id ?? 'Negozio da verificare'))].join(', ')}</p>
            <ProductCases cases={group.cases} onSelect={onCaseSelect} />
          </article>)}
        </div>
        {unresolved.length > 0 && <section className="sd-run-card" aria-labelledby="sd-products-unresolved">
          <h2 id="sd-products-unresolved">Prodotto da identificare</h2>
          <p>Questi casi riguardano categorie, negozi o riferimenti non risolti. Restano consultabili senza attribuirli a uno SKU.</p>
          <ProductCases cases={unresolved} onSelect={onCaseSelect} />
        </section>}
      </>}
    </div>
  )
}

function ProductCases({ cases, onSelect }: { cases: Case[]; onSelect: (item: Case) => void }) {
  return <ul className="sd-products__cases">{cases.map((item) => <li key={item.id}>
    <div className="sd-products__case-header"><strong>{item.store_id ?? 'Negozio da verificare'} · {caseTypeLabel(item.case_type)}</strong><StatusBadge tone={item.status === 'verify' ? 'warning' : 'neutral'} label={caseStatuses[item.status]} /></div>
    <p><strong>Motivazione del caso:</strong> {item.priority_reason || 'Non disponibile'}</p>
    {item.blocking_uncertainties.length > 0 && <p>Da verificare: {item.blocking_uncertainties.join(' · ')}</p>}
    <p className="sd-products__provenance">{item.id} · {item.version} · {item.scope_level}{item.scope_id ? ` · ${item.scope_id}` : ''}</p>
    <Button size="sm" onClick={() => onSelect(item)} aria-label={`Apri caso ${item.id} e fonti`}>Apri caso e fonti</Button>
  </li>)}</ul>
}
