import { useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { ArrowDown, ArrowRight, ArrowUp, ChartSpline, Flame, Lightbulb, Minus, Radio, Store, TriangleAlert } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { readApi } from '../api/client'
import type { Case, RunView } from '../api/client'
import type { useRuns } from '../api/useRuns'
import { Button, Dialog, EmptyState, ErrorState, LoadingState, Select, StatusBadge } from '../ui'
import { ownerLabel } from './caseLabels'
import { closeCitationAndRestoreFocus } from './citationFocus'
import { optionKind } from './optionKinds'
import { productLinker } from './productsData'
import type { ProductCatalog } from './productsData'
import { caseStatuses, caseTypeLabel } from './productView'
import { parseBrief } from './reportBrief'
import type { BriefEntry, BriefSignal } from './reportBrief'
import { briefTokens, citedValue, loadReports, reportOwners, resolveReportCitation } from './reportData'
import type { Report, ResolvedCitation } from './reportData'
import { STORE_GEO } from './storeGeo'
import { useRunData } from './useRunData'
import './reports.css'

const viewLabel = (view: string) => ({ by_office: 'Per ufficio', by_priority: 'Per priorità' })[view] ?? view
const date = (value: string) => `${new Date(value).toLocaleString('it-IT', { timeZone: 'UTC' })} UTC`
const longDate = (value: string) => `${new Date(value).toLocaleString('it-IT', { timeZone: 'UTC', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })} UTC`
const units = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 1 })
const priorities: Record<string, { label: string; icon: LucideIcon }> = {
  critical: { label: 'Critica', icon: Flame },
  high: { label: 'Alta', icon: ArrowUp },
  medium: { label: 'Media', icon: Minus },
  low: { label: 'Bassa', icon: ArrowDown }
}
const unitLabels: Record<string, string> = { units: 'unità', customers: 'clienti', requests: 'richieste', visitors: 'visitatori', percent: '%' }
const forecastStatus: Record<string, string> = { unchanged: 'invariata', computed: 'corretta', not_estimable: 'non stimabile' }

export function ReportsPage({ runs, onCaseSelect }: { runs: ReturnType<typeof useRuns>; onCaseSelect?: (item: Case) => void }) {
  if (runs.loading) return <LoadingState label="Caricamento run" />
  if (runs.error) return <ErrorState title="Impossibile caricare i run" description={runs.error} onRetry={runs.retry} />
  const run = runs.selected
  if (!run) return <EmptyState title="Nessun run disponibile" description="Il brief comparirà dopo la pubblicazione di un run." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  if (!run.published) return <EmptyState title="Brief in attesa di pubblicazione" description="I report saranno leggibili quando l’elaborazione sarà pubblicata." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  return <PublishedReports key={`${run.namespace}-${run.spec.run_id}-${run.spec.as_of}`} run={run} onCaseSelect={onCaseSelect} />
}

function PublishedReports({ run, onCaseSelect }: { run: RunView; onCaseSelect?: (item: Case) => void }) {
  const [data, setData] = useState<{ reports: Report[]; cases: Case[] } | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [owner, setOwner] = useState('')
  const [view, setView] = useState('')
  const catalog = useRunData<ProductCatalog>(run.spec.run_id, 'products')
  useEffect(() => {
    const controller = new AbortController()
    loadReports(run, controller.signal, readApi).then((result) => {
      if (!controller.signal.aborted) setData(result)
    }).catch((reason: Error) => {
      if (!controller.signal.aborted) setError(reason.message)
    })
    return () => controller.abort()
  }, [run, revision])
  if (error) return <ErrorState title="Impossibile caricare il brief" description={error} onRetry={() => { setError(''); setData(null); setRevision((value) => value + 1) }} />
  if (!data) return <LoadingState label="Caricamento brief del run selezionato" />
  if (!data.reports.length) return <EmptyState title="Nessun brief pubblicato" description="Il run selezionato non contiene report. Le fonti acquisite non implicano automaticamente un brief." />
  const owners = [...new Set(data.reports.flatMap((report) => reportOwners(report, data.cases)))].sort()
  const views = [...new Set(data.reports.map((report) => report.view))].sort()
  // The views are two groupings of the same cases: show one at a time, office first.
  const activeView = views.includes(view) ? view : views.includes('by_office') ? 'by_office' : views[0]
  const reports = data.reports.filter((report) => report.view === activeView && (!owner || reportOwners(report, data.cases).includes(owner)))
  return <div className="sd-reports">
    <div className="sd-reports__filters">
      <div className="sd-reports__views" role="group" aria-label="Raggruppamento">
        {views.map((value) => <Button key={value} size="sm" variant={value === activeView ? 'primary' : 'ghost'} pressed={value === activeView} onClick={() => setView(value)}>{viewLabel(value)}</Button>)}
      </div>
      <Select label="Ufficio" value={owner} onValueChange={setOwner} options={[{ value: '', label: 'Tutti gli uffici' }, ...owners.map((value) => ({ value, label: ownerLabel(value) }))]} />
      {run.namespace === 'fixture' && <StatusBadge tone="warning" label="Fixture · dati sintetici" />}
    </div>
    {reports.length ? reports.map((report) => <ReportDocument key={`${report.id}-${report.version}`} report={report} cases={data.cases} run={run}
      catalog={catalog.data} owner={owner} onCaseSelect={onCaseSelect} />)
      : <EmptyState title="Nessun brief per questa selezione" description="Prova un altro ufficio o raggruppamento." />}
  </div>
}

type CiteFn = (index: number | null) => ReactNode

function ReportDocument({ report, cases, run, catalog, owner, onCaseSelect }: {
  report: Report; cases: Case[]; run: RunView; catalog: ProductCatalog | null; owner: string; onCaseSelect?: (item: Case) => void
}) {
  const [citation, selectCitation] = useState<number | null>(null)
  const citationTrigger = useRef<HTMLButtonElement | null>(null)
  const sectionRefs = useRef(new Map<number, HTMLElement>())
  const brief = useMemo(() => parseBrief(report.markdown, report.citations.length), [report])
  const link = useMemo(() => catalog ? productLinker(catalog) : null, [catalog])
  const caseOf = (entry: BriefEntry) => {
    const ref = entry.citation === null ? undefined : report.citations[entry.citation]?.ref
    return ref?.kind === 'Case' ? cases.find((item) => item.id === ref.id && item.version === ref.version) : undefined
  }
  // An office filter narrows the document to that office's cases, whatever the grouping.
  const sections = brief.sections.map((section) => ({
    ...section, entries: section.entries.filter((entry) => !owner || caseOf(entry)?.owner === owner)
  })).filter((section) => section.entries.length || section.notes.length)
  const entries = sections.flatMap((section) => section.entries)
  const openCitation = (index: number, trigger: HTMLButtonElement) => {
    citationTrigger.current = trigger
    selectCitation(index)
  }
  const closeCitation = () => closeCitationAndRestoreFocus(citationTrigger.current, () => selectCitation(null))
  const cite: CiteFn = (index) => index === null ? null
    : <button type="button" className="sd-brief__cite" aria-label={`Apri citazione ${index + 1}`} aria-pressed={citation === index} onClick={(event) => openCitation(index, event.currentTarget)}>{index + 1}</button>
  const inline = (text: string): ReactNode => briefTokens(text, report.citations.length).map((token, i) =>
    token.kind === 'citation' ? <span key={i}>{cite(token.index)}</span>
      : token.kind === 'strong' ? <strong key={i}>{token.value}</strong> : token.value
  )
  const sectionTitle = (title: string) => report.view === 'by_priority' && priorities[title] ? `Priorità ${priorities[title].label.toLowerCase()}` : ownerLabel(title)
  const kpis = [
    { label: 'Casi nel brief', value: entries.length },
    { label: 'Priorità alta', value: entries.filter((entry) => entry.priority === 'high' || entry.priority === 'critical').length, tone: 'is-high' },
    { label: 'Da verificare', value: entries.filter((entry) => entry.status === 'verify').length, tone: 'is-verify' },
    { label: 'Negozi coinvolti', value: new Set(entries.map((entry) => entry.store).filter(Boolean)).size },
    { label: 'Punti aperti', value: entries.reduce((total, entry) => total + entry.open.length, 0) }
  ]

  return <article className="sd-brief" aria-labelledby={`brief-${report.id}`}>
    <header className="sd-brief__masthead">
      <p className="sd-brief__eyebrow">Brief operativo · {viewLabel(report.view).toLowerCase()}</p>
      <h2 id={`brief-${report.id}`}>{owner ? ownerLabel(owner) : 'Situazione della rete'}</h2>
      <p className="sd-brief__asof">Dati disponibili al {longDate(report.as_of)}</p>
      {brief.notes.map((note, i) => <p key={i}>{inline(note)}</p>)}
      <dl className="sd-brief__kpis">{kpis.map((kpi) => <div key={kpi.label} className={kpi.tone}><dt>{kpi.label}</dt><dd>{kpi.value}</dd></div>)}</dl>
      {sections.length > 1 && <nav className="sd-brief__toc" aria-label="Sezioni del brief">
        {sections.map((section, index) => <button key={index} type="button" onClick={() => sectionRefs.current.get(index)?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
          {sectionTitle(section.title)}<span>{section.entries.length}</span>
        </button>)}
      </nav>}
    </header>

    {sections.map((section, index) => <section key={index} className="sd-brief__section" ref={(node) => { if (node) sectionRefs.current.set(index, node); else sectionRefs.current.delete(index) }}
      aria-labelledby={`brief-${report.id}-s${index}`}>
      <header className="sd-brief__section-head">
        <h3 id={`brief-${report.id}-s${index}`}>{sectionTitle(section.title)}</h3>
        <span>{section.entries.length === 1 ? '1 caso' : `${section.entries.length} casi`}</span>
      </header>
      {section.notes.map((note, i) => <p key={i}>{inline(note)}</p>)}
      <div className="sd-brief__cases">{section.entries.map((entry, i) => <BriefCase key={i} entry={entry} item={caseOf(entry)} asOf={report.as_of}
        product={(() => { const item = caseOf(entry); return item && link ? link(item.scope_level, item.scope_id) : undefined })()}
        cite={cite} inline={inline} onCaseSelect={onCaseSelect} />)}</div>
    </section>)}

    <footer className="sd-brief__footer">
      <details>
        <summary>Fonti e citazioni ({report.citations.length})</summary>
        {report.citations.length ? <ol>{report.citations.map((item, index) => <li key={index}><button type="button" className="sd-brief__ref" aria-pressed={citation === index} onClick={(event) => openCitation(index, event.currentTarget)}>
          {item.ref.kind} · {item.ref.id} · {item.ref.version}{item.field ? ` · ${item.field}` : ''}</button></li>)}</ol> : <p>Il brief non contiene citazioni.</p>}
      </details>
      <details>
        <summary>Provenienza del brief</summary>
        <dl><dt>Run</dt><dd>{report.run_id}</dd><dt>Report e versione</dt><dd>{report.id} · {report.version}</dd><dt>Generato da</dt><dd>{report.generated_by}</dd><dt>Hash degli input</dt><dd>{report.input_version_hash}</dd></dl>
      </details>
      <p>Ogni numero cerchiato apre il dato citato, nella stessa versione usata dal brief.</p>
    </footer>

    {citation !== null && <Dialog open title={`Citazione ${citation + 1} · ${report.citations[citation].ref.kind}`} onClose={closeCitation}>
      <CitationBody key={citation} run={run} report={report} cases={cases} index={citation} />
    </Dialog>}
  </article>
}

function signalText(signal: BriefSignal) {
  if (signal.amount !== null) return `${units.format(signal.amount)}${signal.unit === 'percent' ? '%' : ` ${unitLabels[signal.unit ?? ''] ?? signal.unit ?? ''}`}`
  return signal.quality === 'vague' ? 'quantità vaga' : 'quantità non nota'
}

function BriefCase({ entry, item, product, asOf, cite, inline, onCaseSelect }: {
  entry: BriefEntry; item: Case | undefined; product: ReturnType<ReturnType<typeof productLinker>> | undefined; asOf: string
  cite: CiteFn; inline: (text: string) => ReactNode; onCaseSelect?: (item: Case) => void
}) {
  const priority = entry.priority ? priorities[entry.priority] : undefined
  const store = entry.store ? STORE_GEO[entry.store] : undefined
  const storeWide = entry.product === entry.store
  const unidentified = entry.product === 'product not identified'
  const name = product?.product.name ?? (storeWide ? 'Intero negozio' : unidentified ? 'Prodotto da identificare' : entry.product)
  const year = asOf.slice(0, 4)
  const day = (monthDay: string, month = true) => new Date(`${year}-${monthDay}T00:00:00Z`).toLocaleDateString('it-IT', month ? { day: 'numeric', month: 'short', timeZone: 'UTC' } : { day: 'numeric', timeZone: 'UTC' })
  const first = entry.forecasts[0]
  const horizon = first ? `${day(first.from, first.from.slice(0, 2) !== first.to.slice(0, 2))}–${day(first.to)}` : null
  // Colour rows read "Colore 742"; a forecast on the case's own SKU needs no label.
  const variant = (sku: string) => sku === entry.code ? 'Domanda base' : entry.code && sku.startsWith(`${entry.code}-`) ? `Colore ${sku.slice(entry.code.length + 1)}` : sku
  const structured = entry.signals.length + entry.forecasts.length + entry.options.length > 0
  return <article className={`sd-brief__case is-${entry.priority ?? 'unknown'}`}>
    <div className="sd-brief__thumb" aria-hidden="true">{product ? <img src={product.product.image} alt="" /> : <Store />}</div>
    <div className="sd-brief__case-main">
      <header className="sd-brief__case-head">
        <div className="sd-brief__tags">
          {priority && <span className="sd-brief__tag is-priority"><priority.icon aria-hidden="true" />Priorità {priority.label.toLowerCase()}</span>}
          {entry.status && <span className={`sd-brief__tag${entry.status === 'verify' ? ' is-verify' : ''}`}>{caseStatuses[entry.status as Case['status']] ?? entry.status}</span>}
          {item && <span className="sd-brief__tag is-quiet">{caseTypeLabel(item.case_type)}</span>}
          {item && onCaseSelect && <Button className="sd-brief__open-case" size="sm" variant="ghost" icon={<ArrowRight />} onClick={() => onCaseSelect(item)}>Apri caso</Button>}
        </div>
        <h4>{name ? inline(name) : inline(entry.headline)}{cite(entry.citation)}</h4>
        <p className="sd-brief__where">
          {entry.store && <span><Store aria-hidden="true" />{store ? `${store.name} · ${entry.store}` : entry.store}</span>}
          {entry.code && <code>{entry.code}</code>}
        </p>
      </header>
      {structured && <div className="sd-brief__facts">
        {entry.signals.length > 0 && <section>
          <h5><Radio aria-hidden="true" />Segnali dai negozi</h5>
          <ul>{entry.signals.map((signal, i) => <li key={i}><span>{caseTypeLabel(signal.kind)}</span><strong className={signal.amount === null ? 'is-unknown' : ''}>{signalText(signal)}</strong>{cite(signal.citation)}</li>)}</ul>
        </section>}
        {entry.forecasts.length > 0 && <section>
          <h5><ChartSpline aria-hidden="true" />Previsione<small>{horizon}</small></h5>
          <ul>{entry.forecasts.map((forecast, i) => <li key={i}><span>{variant(forecast.sku)}</span>
            <strong>{units.format(forecast.units)} unità</strong><em>{forecastStatus[forecast.status] ?? forecast.status}</em>{cite(forecast.citation)}</li>)}</ul>
        </section>}
        {entry.options.length > 0 && <section>
          <h5><Lightbulb aria-hidden="true" />Azione consigliata</h5>
          <ul>{entry.options.map((option, i) => { const { label, icon: Icon } = optionKind(option.kind)
            return <li key={i} className="sd-brief__action"><Icon aria-hidden="true" /><span>{label}</span>{cite(option.citation)}</li> })}</ul>
        </section>}
      </div>}
      {entry.other.map((line, i) => <p key={i} className="sd-brief__other">{inline(line)}</p>)}
      {entry.open.length > 0 && <details className="sd-brief__open">
        <summary><TriangleAlert aria-hidden="true" />{entry.open.length === 1 ? '1 punto da verificare' : `${entry.open.length} punti da verificare`}</summary>
        <ul>{entry.open.map((line, i) => <li key={i}>{inline(line)}</li>)}</ul>
      </details>}
    </div>
  </article>
}

function CitationBody({ run, report, cases, index }: { run: RunView; report: Report; cases: Case[]; index: number }) {
  const [data, setData] = useState<ResolvedCitation | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    resolveReportCitation(run, report, cases, index, controller.signal, readApi).then((result) => {
      if (!controller.signal.aborted) setData(result)
    }).catch((reason: Error) => {
      if (!controller.signal.aborted) setError(reason.message)
    })
    return () => controller.abort()
  }, [run, report, cases, index, revision])
  const ref = report.citations[index].ref
  const value = data && citedValue(data.artifact, data.citation.field)
  return <div className="sd-brief__citation">
    <p className="sd-brief__muted">{ref.id} · {ref.version} · run {run.spec.run_id}</p>
    {error ? <ErrorState compact title="Citazione non disponibile" description={error} onRetry={() => { setError(''); setRevision((value) => value + 1) }} /> : !data ? <LoadingState compact label="Caricamento del riferimento citato" /> : <>
      <dl><dt>Campo</dt><dd>{data.citation.field ?? 'Intero record'}</dd>
        {data.citation.field && <><dt>Valore citato</dt><dd><pre>{value === undefined ? 'Campo non disponibile nel record' : JSON.stringify(value, null, 2)}</pre></dd></>}
        <dt>Unità</dt><dd>{data.citation.unit ?? 'Non specificata'}</dd>
        <dt>Ambito</dt><dd>{data.citation.scope ? Object.entries(data.citation.scope).map(([key, value]) => `${key}: ${value}`).join(' · ') : 'Non specificato'}</dd>
        <dt>Periodo</dt><dd>{data.citation.period_start ? date(data.citation.period_start) : 'Inizio non specificato'} – {data.citation.period_end ? date(data.citation.period_end) : 'Fine non specificata'}</dd></dl>
      <ArtifactEvidence artifact={data.artifact} />
      <details className="sd-case-analysis__refs"><summary>Record completo e provenienza</summary><pre>{JSON.stringify(data.artifact, null, 2)}</pre></details>
    </>}
  </div>
}

function ArtifactEvidence({ artifact }: { artifact: Record<string, unknown> }) {
  const evidence = Array.isArray(artifact.evidence) ? artifact.evidence : []
  const sources = Array.isArray(artifact.source_refs) ? artifact.source_refs : []
  return <>
    {typeof artifact.priority_reason === 'string' && <p>{artifact.priority_reason}</p>}
    {evidence.length > 0 && <section aria-label="Evidenze citate"><h4>Evidenze</h4>{evidence.map((item, i) =>
      item && typeof item.quote === 'string' ? <blockquote key={i}><p>{item.quote}</p><cite>{item.document_id} · {item.document_version}</cite></blockquote> : null
    )}</section>}
    {sources.length > 0 && <section aria-label="Fonti del riferimento"><h4>Fonti</h4><ul>{sources.map((source, i) =>
      source && typeof source.uri === 'string' ? <li key={i}>{source.uri}{typeof source.locator === 'string' ? ` · ${source.locator}` : ''}</li> : null
    )}</ul></section>}
  </>
}
