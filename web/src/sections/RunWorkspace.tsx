import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Search } from 'lucide-react'
import { readApi } from '../api/client'
import type { Case, DocumentDetail, SourceDocument } from '../api/client'
import {
  Button,
  EmptyState,
  ErrorState,
  Input,
  LoadingState,
  StatusBadge
} from '../ui'
import { useRuns } from '../api/useRuns'
import { CaseQueue } from './CaseQueue'
import { Overview } from './Overview'
import { latestCaseVersions } from './caseUtils'
import type { CaseQueueFilters, CaseSelection } from './caseUtils'
import './sections.css'
import '../widgets/widgets.css'
import { evidenceRanges, refKey } from './sourceEvidence'
import type { CaseEvidence } from './sourceEvidence'

const statuses: Record<string, string> = {
  open: 'Aperto',
  verify: 'Da verificare',
  monitor: 'Monitoraggio',
  action_proposed: 'Azione proposta',
  decided: 'Deciso',
  closed: 'Chiuso',
  succeeded: 'Completato',
  degraded: 'Parziale',
  blocked: 'Bloccato',
  failed: 'Errore',
  running: 'In corso',
  pending: 'In attesa'
}
const date = (value: string | null | undefined) =>
  value ? new Date(value).toLocaleString('it-IT') : 'Non disponibile'

export function RunWorkspace({
  section,
  runs,
  caseSelection,
  onCaseSelect,
  onCaseReturn,
  caseQueueFilters,
  onCaseQueueFiltersChange
}: {
  section: string
  runs: ReturnType<typeof useRuns>
  caseSelection: CaseSelection | null
  onCaseSelect: (item: Case) => void
  onCaseReturn: () => void
  caseQueueFilters: CaseQueueFilters
  onCaseQueueFiltersChange: (filters: CaseQueueFilters) => void
}) {
  const [data, setData] = useState<{
    cases: Case[]
    documents: SourceDocument[]
    caseRefs: Record<string, Omit<CaseEvidence, 'evidence'>[]>
  } | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [search, setSearch] = useState('')
  const run = runs.selected
  const runId = run?.spec.run_id
  const published = run?.published
  useEffect(() => {
    const controller = new AbortController()
    const base = `/runs/${encodeURIComponent(runId ?? '')}`
    const request =
      published && runId
        ? Promise.all([
            section === 'sources' || section === 'cases' || section === 'overview'
              ? readApi<Case[]>(`${base}/cases`, controller.signal)
              : Promise.resolve([] as Case[]),
            section === 'cases'
              ? Promise.resolve([] as SourceDocument[])
              : readApi<SourceDocument[]>(
                  `${base}/documents`,
                  controller.signal
                )
          ]).then(([cases, documents]) => {
              const caseRefs: Record<string, Omit<CaseEvidence, 'evidence'>[]> = {}
              const latest = new Map<string, Case>()
              for (const item of cases) {
                const seen = latest.get(item.id)
                if (!seen || versionNumber(item.version) > versionNumber(seen.version)) latest.set(item.id, item)
              }
              for (const item of latest.values()) {
                for (const [relation, refs] of [
                  ['supporting', item.supporting],
                  ['contradicting', item.contradicting]
                ] as const) {
                  for (const ref of refs) {
                    const key = refKey(ref)
                    caseRefs[key] = [...(caseRefs[key] ?? []), { caseId: item.id, caseType: item.case_type, relation }]
                  }
                }
              }
              return {
                cases,
                documents,
                caseRefs
              }
            })
        : null
    request
      ?.then((result) => {
        if (!controller.signal.aborted) setData(result)
      })
      .catch((error) => {
        if (!controller.signal.aborted) setError(String(error.message))
      })
    return () => controller.abort()
  }, [section, runId, published, revision, run])
  if (runs.loading) return <LoadingState label="Caricamento run" />
  if (runs.error)
    return (
      <ErrorState
        title="Impossibile caricare i run"
        description={runs.error}
        onRetry={runs.retry}
      />
    )
  if (section !== 'modules') {
    if (!run)
      return (
        <EmptyState
          title="Nessun run disponibile"
          description="I casi e le fonti compariranno dopo la pubblicazione di un’elaborazione dei dati dei negozi."
          action={<Button onClick={runs.retry}>Aggiorna</Button>}
        />
      )
    if (!run.published)
      return (
        <EmptyState
          title={`Elaborazione ${statuses[run.status]?.toLowerCase() ?? run.status}`}
          description="I risultati saranno disponibili quando il run sarà pubblicato."
          action={<Button onClick={runs.retry}>Aggiorna</Button>}
        />
      )
  }
  if (error)
    return (
      <ErrorState
        title="Impossibile caricare i dati"
        description={error}
        onRetry={() => {
          setData(null)
          setError('')
          setRevision((value) => value + 1)
        }}
      />
    )
  if (!data) return <LoadingState label="Caricamento dati" />
  const query = search.trim().toLocaleLowerCase('it-IT')
  const currentCases = latestCaseVersions(data.cases)
  const documents = data.documents.filter(
    (item) =>
      query === '' ||
      `${item.id} ${item.text}`.toLocaleLowerCase('it-IT').includes(query)
  )
  return (
    <div className="sd-run-workspace">
      {section === 'overview' && run && (
        <Overview
          run={run}
          cases={currentCases}
          documents={data.documents}
          onCaseSelect={onCaseSelect}
        />
      )}
      {section === 'sources' && (
        <form
          className="sd-filterbar"
          role="search"
          onSubmit={(event) => event.preventDefault()}
        >
          <Input
            size="sm"
            label="Cerca nelle fonti"
            type="search"
            icon={<Search />}
            placeholder="Testo o identificativo"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </form>
      )}
      {section === 'cases' && (
        <CaseQueue
          cases={currentCases}
          stores={run?.spec.stores ?? []}
          asOf={run?.spec.as_of ?? ''}
          runId={runId ?? ''}
          fixtureMode={run?.namespace === 'fixture'}
          selection={caseSelection}
          onSelect={onCaseSelect}
          onReturn={onCaseReturn}
          filters={caseQueueFilters}
          onFiltersChange={onCaseQueueFiltersChange}
        />
      )}
      {section === 'sources' &&
        (documents.length ? (
          <div className="sd-run-list">
            {documents.map((item) => (
              <SourceDocumentCard
                item={item}
                runId={run?.spec.run_id ?? ''}
                caseRefs={data.caseRefs}
                key={`${item.id}-${item.version}`}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            title="Nessuna fonte trovata"
            description="Nessun documento pubblicato corrisponde alla selezione."
          />
        ))}
    </div>
  )
}

// Versions are opaque strings like "v2"; compare by their numeric part.
const versionNumber = (version: string) =>
  Number(/\d+/.exec(version)?.[0] ?? 0)

function SourceDocumentCard({
  item,
  runId,
  caseRefs
}: {
  item: SourceDocument
  runId: string
  caseRefs: Record<string, Omit<CaseEvidence, 'evidence'>[]>
}) {
  const [open, setOpen] = useState(false)
  const [detail, setDetail] = useState<DocumentDetail | null>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    if (!open || detail) return
    const controller = new AbortController()
    readApi<DocumentDetail>(
      `/runs/${encodeURIComponent(runId)}/documents/${encodeURIComponent(item.id)}?version=${encodeURIComponent(item.version)}`,
      controller.signal
    )
      .then((result) => {
        if (!controller.signal.aborted) setDetail(result)
      })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(String(reason.message))
      })
    return () => controller.abort()
  }, [open, detail, item.id, item.version, runId])

  const caseEvidence = (detail?.observations ?? []).flatMap((observation) => {
    const refs =
      caseRefs[`Observation:${observation.id}:${observation.version}`] ?? []
    return refs.flatMap((ref) =>
      observation.evidence.map((evidence) => ({ ...ref, evidence }))
    )
  })
  const ranges = evidenceRanges(item.text, item, caseEvidence)
  const parts: ReactNode[] = []
  let cursor = 0
  for (const [index, range] of ranges.entries()) {
    if (range.start < cursor) continue
    if (range.start > cursor) parts.push(item.text.slice(cursor, range.start))
    parts.push(
      <mark
        className={`sd-source-evidence sd-source-evidence--${range.relation}`}
        key={`${range.references.map(({ caseId }) => caseId).join('-')}-${range.start}-${index}`}
        title={range.references
          .map(({ caseId, caseType, relation }) =>
            `${caseId} · ${caseType} · ${relation === 'supporting' ? 'A supporto' : 'In contrasto'}`
          )
          .join(' | ')}
        aria-label={range.references
          .map(({ caseId, caseType, relation }) =>
            `${caseId}, ${caseType}, ${relation === 'supporting' ? 'a supporto' : 'in contrasto'}`
          )
          .join('; ')}
      >
        {item.text.slice(range.start, range.end)}
      </mark>
    )
    cursor = range.end
  }
  if (cursor < item.text.length) parts.push(item.text.slice(cursor))

  return (
    <details
      className="sd-run-card"
      onToggle={(event) => {
        setOpen(event.currentTarget.open)
        if (event.currentTarget.open) setError('')
      }}
    >
      <summary>
        <span>{item.id}</span>
        <StatusBadge label={item.source_type} tone="neutral" />
      </summary>
      <p>
        {item.language ?? 'Lingua non disponibile'} · Disponibile dal{' '}
        {date(item.available_at)}
      </p>
      {open && !detail && !error && <p>Caricamento evidenze…</p>}
      {error && <p role="status">Evidenze non disponibili: {error}</p>}
      {ranges.length > 0 && (
        <p className="sd-source-evidence-label">
          Evidenze collegate al caso · passa sul testo evidenziato per i riferimenti
        </p>
      )}
      <pre className="sd-source-text">{detail ? parts : item.text}</pre>
    </details>
  )
}
