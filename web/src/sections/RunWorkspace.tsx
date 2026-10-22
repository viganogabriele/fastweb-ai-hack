import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import { readApi } from '../api/client'
import type { Case, ModuleManifest, SourceDocument } from '../api/client'
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
import { CaseQueue } from './CaseQueue'
import { latestCaseVersions } from './caseUtils'
import type { CaseQueueFilters, CaseSelection } from './caseUtils'
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
          ).then((modules) => ({ cases: [], documents: [], modules }))
        : published && runId
          ? Promise.all([
              section === 'sources'
                ? Promise.resolve([] as Case[])
                : readApi<Case[]>(`${base}/cases`, controller.signal),
              section === 'cases'
                ? Promise.resolve([] as SourceDocument[])
                : readApi<SourceDocument[]>(
                    `${base}/documents`,
                    controller.signal
                  )
            ]).then(([cases, documents]) => ({ cases, documents, modules: [] }))
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
  const cases = currentCases
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
  const active = currentCases.filter(
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
      {(section === 'overview' || section === 'sources') && (
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
          {section === 'overview' && (
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
      {section === 'cases' && (
        <CaseQueue
          cases={currentCases}
          stores={run?.spec.stores ?? []}
          asOf={run?.spec.as_of ?? ''}
          selection={caseSelection}
          onSelect={onCaseSelect}
          onReturn={onCaseReturn}
          filters={caseQueueFilters}
          onFiltersChange={onCaseQueueFiltersChange}
        />
      )}
      {section === 'overview' &&
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
              <details
                className="sd-run-card"
                key={`${item.id}-${item.version}`}
              >
                <summary>
                  <span>{item.id}</span>
                  <StatusBadge label={item.source_type} tone="neutral" />
                </summary>
                <p>
                  {item.language ?? 'Lingua non disponibile'} · Disponibile dal{' '}
                  {date(item.available_at)}
                </p>
                <pre className="sd-source-text">{item.text}</pre>
              </details>
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
