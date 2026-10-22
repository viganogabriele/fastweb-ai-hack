import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Search } from 'lucide-react'
import { readApi } from '../api/client'
import type { Case, DocumentDetail, ModuleManifest, SourceDocument } from '../api/client'
import {
  Button,
  EmptyState,
  ErrorState,
  Input,
  LoadingState,
  Select,
  StatusBadge
} from '../ui'
import { useRuns } from '../api/useRuns'
import { evidenceRanges, refKey } from './sourceEvidence'
import type { CaseEvidence } from './sourceEvidence'
import './sections.css'
import '../widgets/widgets.css'

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
const priorities: Record<string, string> = {
  critical: 'Critica',
  high: 'Alta',
  medium: 'Media',
  low: 'Bassa'
}
const priorityOrder: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3
}
const date = (value: string | null | undefined) =>
  value ? new Date(value).toLocaleString('it-IT') : 'Non disponibile'

export function RunWorkspace({
  section,
  runs
}: {
  section: string
  runs: ReturnType<typeof useRuns>
}) {
  const [data, setData] = useState<{
    cases: Case[]
    documents: SourceDocument[]
    caseRefs: Record<string, Omit<CaseEvidence, 'evidence'>[]>
    modules: ModuleManifest[]
  } | null>(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [search, setSearch] = useState('')
  const [store, setStore] = useState('all')
  const run = runs.selected
  const runId = run?.spec.run_id
  const published = run?.published
  useEffect(() => {
    const controller = new AbortController()
    const base = `/runs/${encodeURIComponent(runId ?? '')}`
    const request =
      section === 'modules'
        ? (run
            ? Promise.resolve(
                run.spec.modules.map((snapshot) => snapshot.manifest)
              )
            : readApi<ModuleManifest[]>('/modules', controller.signal)
          ).then((modules) => ({ cases: [], documents: [], caseRefs: {}, modules }))
        : published && runId
          ? Promise.all([
              section === 'sources' || section === 'overview'
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
              for (const item of cases) {
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
                caseRefs,
                modules: []
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
  const cases = data.cases
    .filter(
      (item) =>
        (store === 'all' || item.store_id === store) &&
        [
          item.store_id,
          item.scope_id,
          item.case_type,
          item.owner,
          item.priority_reason
        ]
          .join(' ')
          .toLocaleLowerCase('it-IT')
          .includes(query)
    )
    .sort(
      (a, b) =>
        priorityOrder[a.priority] - priorityOrder[b.priority] ||
        (a.decision_due_at ?? '9999').localeCompare(b.decision_due_at ?? '9999')
    )
  const documents = data.documents.filter(
    (item) =>
      query === '' ||
      `${item.id} ${item.text}`.toLocaleLowerCase('it-IT').includes(query)
  )
  const active = data.cases.filter(
    (item) => item.status !== 'closed' && item.status !== 'decided'
  )
  return (
    <div className="sd-run-workspace">
      {section === 'overview' ? (
        <>
          <div className="sd-run-metrics">
            {[
              ['Casi aperti', active.length],
              [
                'Da verificare',
                active.filter((item) => item.status === 'verify').length
              ],
              ['Fonti acquisite', data.documents.length],
              ['Negozi nel run', run?.spec.stores.length ?? 0]
            ].map(([label, count]) => (
              <article className="sd-run-card" key={label}>
                <h2>{label}</h2>
                <strong>{count}</strong>
              </article>
            ))}
          </div>
          <h2>Segnalazioni da valutare</h2>
        </>
      ) : null}
      {(section === 'cases' ||
        section === 'overview' ||
        section === 'sources') && (
        <form
          className="sd-filterbar"
          role="search"
          onSubmit={(event) => event.preventDefault()}
        >
          <Input
            size="sm"
            label={section === 'sources' ? 'Cerca nelle fonti' : 'Cerca caso'}
            type="search"
            icon={<Search />}
            placeholder={
              section === 'sources'
                ? 'Testo o identificativo'
                : 'Negozio, prodotto o motivo'
            }
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          {section !== 'sources' && (
            <Select
              size="sm"
              label="Negozio"
              value={store}
              onValueChange={setStore}
              options={[
                { value: 'all', label: 'Tutti i negozi' },
                ...(run?.spec.stores ?? []).map((id) => ({
                  value: id,
                  label: id
                }))
              ]}
            />
          )}
        </form>
      )}
      {(section === 'cases' || section === 'overview') &&
        (cases.length ? (
          <div className="sd-run-list">
            {cases.map((item) => (
              <details
                className="sd-run-card"
                key={`${item.id}-${item.version}`}
              >
                <summary>
                  <span>
                    {item.store_id ?? 'Negozio da verificare'} ·{' '}
                    {item.scope_id ?? 'Prodotto da identificare'}
                  </span>
                  <StatusBadge
                    label={statuses[item.status]}
                    tone={item.status === 'verify' ? 'warning' : 'neutral'}
                  />
                </summary>
                <p>
                  {priorities[item.priority]} · {item.case_type} · {item.owner}
                </p>
                <p>{item.priority_reason}</p>
                <dl>
                  <dt>Scadenza decisione</dt>
                  <dd>{date(item.decision_due_at)}</dd>
                  <dt>Documenti / origini indipendenti</dt>
                  <dd>
                    {item.n_documents} / {item.n_origin_groups}
                  </dd>
                </dl>
                {item.blocking_uncertainties.length ? (
                  <>
                    <h3>Incertezze da risolvere</h3>
                    <ul>
                      {item.blocking_uncertainties.map((text) => (
                        <li key={text}>{text}</li>
                      ))}
                    </ul>
                  </>
                ) : null}
                <p>
                  Finestra: {date(item.window_start)} – {date(item.window_end)}
                </p>
              </details>
            ))}
          </div>
        ) : (
          <EmptyState
            title="Nessun caso trovato"
            description="Non ci sono casi pubblicati per questa selezione. Le fonti acquisite non implicano automaticamente un caso."
          />
        ))}
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
      {section === 'modules' &&
        (data.modules.length ? (
          <div className="sd-run-list">
            {data.modules.map((item) => {
              const execution = run?.module_runs.find(
                (value) => value.module_id === item.id
              )
              return (
                <article className="sd-run-card" key={item.id}>
                  <h2>{item.id}</h2>
                  <p>{item.description}</p>
                  <StatusBadge
                    label={
                      execution
                        ? statuses[execution.status]
                        : 'Non eseguito nel run'
                    }
                    tone="neutral"
                  />
                  <p>Modalità: {execution?.mode ?? item.mode}</p>
                  {execution?.result && (
                    <>
                      <p>
                        {Object.entries(execution.result.counts)
                          .map(([key, count]) => `${key}: ${count}`)
                          .join(' · ')}
                      </p>
                      {[
                        ...execution.result.errors,
                        ...execution.result.abstentions
                      ].map((text) => (
                        <p key={text}>{text}</p>
                      ))}
                    </>
                  )}
                </article>
              )
            })}
          </div>
        ) : (
          <EmptyState title="Nessun modulo disponibile" />
        ))}
    </div>
  )
}

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
        key={`${range.caseId}-${range.evidence.segment_id}-${range.start}-${index}`}
        title={`${range.caseId} · ${range.caseType} · ${range.relation === 'supporting' ? 'A supporto' : 'In contrasto'}`}
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
