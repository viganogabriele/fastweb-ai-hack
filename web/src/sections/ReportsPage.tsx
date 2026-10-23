import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { readApi } from '../api/client'
import type { Case, RunView } from '../api/client'
import type { useRuns } from '../api/useRuns'
import { Button, EmptyState, ErrorState, LoadingState, Select, StatusBadge } from '../ui'
import { briefTokens, citedValue, loadReports, reportOwners, resolveReportCitation } from './reportData'
import type { Report, ResolvedCitation } from './reportData'
import './reports.css'

const viewLabel = (view: string) => ({ by_office: 'Per ufficio', by_priority: 'Per priorità' })[view] ?? view
const date = (value: string) => `${new Date(value).toLocaleString('it-IT', { timeZone: 'UTC' })} UTC`

export function ReportsPage({ runs }: { runs: ReturnType<typeof useRuns> }) {
  if (runs.loading) return <LoadingState label="Caricamento run" />
  if (runs.error) return <ErrorState title="Impossibile caricare i run" description={runs.error} onRetry={runs.retry} />
  const run = runs.selected
  if (!run) return <EmptyState title="Nessun run disponibile" description="Il brief comparirà dopo la pubblicazione di un run." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  if (!run.published) return <EmptyState title="Brief in attesa di pubblicazione" description="I report saranno leggibili quando l’elaborazione sarà pubblicata." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  return <PublishedReports key={`${run.namespace}-${run.spec.run_id}-${run.spec.as_of}`} run={run} />
}

function PublishedReports({ run }: { run: RunView }) {
  const [data, setData] = useState<{ reports: Report[]; cases: Case[] } | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [owner, setOwner] = useState('')
  const [view, setView] = useState('')
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
  const reports = data.reports.filter((report) => (!owner || reportOwners(report, data.cases).includes(owner)) && (!view || report.view === view))
  return <div className="sd-reports">
    <div className="sd-reports__filters">
      <Select label="Ufficio destinatario" value={owner} onValueChange={setOwner} options={[{ value: '', label: 'Tutti gli uffici' }, ...owners.map((value) => ({ value, label: value }))]} />
      <Select label="Raggruppamento" value={view} onValueChange={setView} options={[{ value: '', label: 'Tutti i raggruppamenti' }, ...views.map((value) => ({ value, label: viewLabel(value) }))]} />
      <StatusBadge tone={run.namespace === 'fixture' ? 'warning' : 'neutral'} label={run.namespace === 'fixture' ? 'Fixture · dati sintetici' : run.spec.mode} />
    </div>
    <p className="sd-reports__notice">Le citazioni aprono i dati e la versione usati dal brief, nello stesso run.{owner && ' Il filtro seleziona i brief che riguardano l’ufficio; le altre sezioni del testo restano visibili.'}</p>
    {reports.length ? reports.map((report) => <ReportCard key={`${report.id}-${report.version}`} report={report} cases={data.cases} run={run} />) : <EmptyState title="Nessun brief per questa selezione" description="Prova un altro ufficio o raggruppamento." />}
  </div>
}

function ReportCard({ report, cases, run }: { report: Report; cases: Case[]; run: RunView }) {
  const [citation, selectCitation] = useState<number | null>(null)
  const citationButtons = useRef(new Map<number, HTMLButtonElement>())
  const returnFocus = () => {
    if (citation !== null) citationButtons.current.get(citation)?.focus()
    selectCitation(null)
  }
  const inline = (text: string): ReactNode => briefTokens(text, report.citations.length).map((token, i) =>
    token.kind === 'citation' ? <button key={i} type="button" className="sd-report__citation" aria-label={`Apri citazione ${token.index + 1}`} aria-pressed={citation === token.index} onClick={() => selectCitation(token.index)}>{token.value}</button>
      : token.kind === 'strong' ? <strong key={i}>{token.value}</strong> : token.value
  )
  return <article className="sd-report">
    <header className="sd-report__header"><h2>Brief {viewLabel(report.view).toLocaleLowerCase('it-IT')}</h2><span>{date(report.as_of)}</span></header>
    <div className="sd-report__text">{report.markdown.split(/\n\s*\n/).filter(Boolean).map((block, i) => {
      if (block.startsWith('# ')) return <h3 key={i}>{inline(block.slice(2))}</h3>
      if (block.startsWith('## ')) return <h4 key={i}>{inline(block.slice(3))}</h4>
      if (block.startsWith('- ')) {
        const items: { text: string; children: string[] }[] = []
        for (const line of block.split('\n')) {
          if (line.startsWith('  - ') && items.length) items.at(-1)!.children.push(line.slice(4))
          else items.push({ text: line.replace(/^- /, ''), children: [] })
        }
        return <ul key={i}>{items.map((item, index) => <li key={index}>{inline(item.text)}{item.children.length > 0 && <ul>{item.children.map((text, n) => <li key={n}>{inline(text)}</li>)}</ul>}</li>)}</ul>
      }
      return <p key={i}>{inline(block)}</p>
    })}</div>
    <section className="sd-report__references" aria-label="Citazioni del brief"><h3>Citazioni</h3>
      {report.citations.length ? <ol>{report.citations.map((item, index) => <li key={index}><button type="button" className="sd-report__citation" ref={(node) => { if (node) citationButtons.current.set(index, node); else citationButtons.current.delete(index) }} aria-pressed={citation === index} onClick={() => selectCitation(index)}>{item.ref.kind} · {item.ref.id} · {item.ref.version}{item.field ? ` · ${item.field}` : ''}</button></li>)}</ol> : <p>Il brief non contiene citazioni.</p>}
    </section>
    {citation !== null && <CitationPanel key={citation} run={run} report={report} cases={cases} index={citation} onClose={returnFocus} />}
    <details className="sd-report__provenance"><summary>Provenienza del brief</summary><dl><dt>Run</dt><dd>{report.run_id}</dd><dt>Report e versione</dt><dd>{report.id} · {report.version}</dd><dt>Generato da</dt><dd>{report.generated_by}</dd><dt>Hash degli input</dt><dd>{report.input_version_hash}</dd></dl></details>
  </article>
}

function CitationPanel({ run, report, cases, index, onClose }: { run: RunView; report: Report; cases: Case[]; index: number; onClose: () => void }) {
  const [data, setData] = useState<ResolvedCitation | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const heading = useRef<HTMLHeadingElement>(null)
  useEffect(() => { heading.current?.focus() }, [])
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
  return <section className="sd-report__detail" aria-label={`Dettaglio citazione ${index + 1}`}>
    <header><h3 ref={heading} tabIndex={-1}>Citazione {index + 1} · {ref.kind}</h3><Button variant="secondary" size="sm" onClick={onClose}>Chiudi citazione</Button></header>
    <p>{ref.id} · {ref.version} · run {run.spec.run_id}</p>
    {error ? <ErrorState compact title="Citazione non disponibile" description={error} onRetry={() => { setError(''); setRevision((value) => value + 1) }} /> : !data ? <LoadingState compact label="Caricamento del riferimento citato" /> : <>
      <dl><dt>Campo</dt><dd>{data.citation.field ?? 'Intero record'}</dd>
        {data.citation.field && <><dt>Valore citato</dt><dd><pre>{value === undefined ? 'Campo non disponibile nel record' : JSON.stringify(value, null, 2)}</pre></dd></>}
        <dt>Unità</dt><dd>{data.citation.unit ?? 'Non specificata'}</dd>
        <dt>Ambito</dt><dd>{data.citation.scope ? Object.entries(data.citation.scope).map(([key, value]) => `${key}: ${value}`).join(' · ') : 'Non specificato'}</dd>
        <dt>Periodo</dt><dd>{data.citation.period_start ? date(data.citation.period_start) : 'Inizio non specificato'} – {data.citation.period_end ? date(data.citation.period_end) : 'Fine non specificata'}</dd></dl>
      <details open><summary>Record citato e provenienza</summary><pre>{JSON.stringify(data.artifact, null, 2)}</pre></details>
    </>}
  </section>
}
