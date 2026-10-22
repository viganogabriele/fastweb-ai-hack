import { useEffect, useRef, useState } from 'react'
import { readApi } from '../api/client'
import type { ModuleManifest } from '../api/client'
import type { useRuns } from '../api/useRuns'
import {
  nextRunRequest,
  selectionIssues,
  submitModuleRun
} from '../api/moduleSelection'
import {
  Button,
  EmptyState,
  ErrorState,
  LoadingState,
  StatusBadge
} from '../ui'
import type { StatusTone } from '../ui/StatusBadge'
import './sections.css'
import './modules.css'

const statuses: Record<string, { label: string; tone: StatusTone }> = {
  pending: { label: 'In attesa', tone: 'neutral' },
  running: { label: 'In corso', tone: 'info' },
  succeeded: { label: 'Completato', tone: 'success' },
  degraded: { label: 'Parziale', tone: 'warning' },
  blocked: { label: 'Bloccato', tone: 'warning' },
  failed: { label: 'Errore', tone: 'danger' }
}

export function ModulesPage({ runs }: { runs: ReturnType<typeof useRuns> }) {
  const run = runs.selected
  const [catalog, setCatalog] = useState<ModuleManifest[] | null>(null)
  const [catalogError, setCatalogError] = useState('')
  const [revision, setRevision] = useState(0)
  const [selection, setSelection] = useState<Record<string, boolean>>({})
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const inFlight = useRef(false)
  const mounted = useRef(true)
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])
  useEffect(() => {
    if (run) return
    const controller = new AbortController()
    readApi<ModuleManifest[]>('/modules', controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setCatalog(data)
      })
      .catch((error: Error) => {
        if (!controller.signal.aborted) setCatalogError(error.message)
      })
    return () => controller.abort()
  }, [run, revision])

  if (runs.loading) return <LoadingState label="Caricamento run" />
  if (runs.error)
    return (
      <ErrorState
        title="Impossibile caricare i run"
        description={runs.error}
        onRetry={runs.retry}
      />
    )
  if (!run && catalogError)
    return (
      <ErrorState
        title="Impossibile caricare i moduli"
        description={catalogError}
        onRetry={() => {
          setCatalogError('')
          setCatalog(null)
          setRevision((value) => value + 1)
        }}
      />
    )
  if (!run && !catalog) return <LoadingState label="Caricamento moduli" />

  const modules = run
    ? run.spec.modules.map((item) => item.manifest)
    : (catalog ?? [])
  const issues = run ? selectionIssues(run, selection) : []
  const canConfigure =
    !!run &&
    run.namespace === 'product' &&
    run.spec.mode !== 'fixture' &&
    run.spec.mode !== 'unavailable'
  const changed = modules.some(
    (item) => (selection[item.id] ?? item.enabled) !== item.enabled
  )

  async function startRun() {
    if (!run || !canConfigure || !changed || issues.length || inFlight.current)
      return
    inFlight.current = true
    setSubmitting(true)
    setSubmitError('')
    try {
      const created = await submitModuleRun(
        await nextRunRequest(run, selection)
      )
      // The server has accepted the snapshot, even if the user navigated away.
      runs.acceptRun(created, mounted.current ? run.spec.run_id : undefined)
    } catch (error) {
      if (mounted.current)
        setSubmitError(
          error instanceof Error
            ? error.message
            : 'Impossibile creare il run. Aggiorna i run prima di riprovare.'
        )
    } finally {
      inFlight.current = false
      if (mounted.current) setSubmitting(false)
    }
  }

  return (
    <div className="sd-run-workspace">
      <section
        className="sd-run-card sd-modules-intro"
        aria-label="Configurazione del prossimo run"
      >
        <h2>
          {run
            ? 'Moduli del run selezionato'
            : 'Catalogo dei moduli installati'}
        </h2>
        <p>
          {run
            ? `Run: ${run.spec.run_id}. Stato e conteggi si riferiscono esclusivamente a questo snapshot.`
            : 'Nessun run selezionato: stato di esecuzione e conteggi non sono disponibili.'}
        </p>
        <p id="module-selection-help">
          {canConfigure
            ? 'Gli interruttori preparano una selezione locale. Avvia un nuovo run per salvarla e applicarla agli stessi negozi e alla stessa data di riferimento; il run selezionato resta invariato.'
            : 'Per configurare i moduli serve uno snapshot di run prodotto eseguibile, completo di parametri. Il catalogo da solo non consente di avviare un run.'}
        </p>
        <p>
          Disattivare una dipendenza richiede di disattivare anche i moduli che
          la usano. Le modalità restano quelle dello snapshot.
        </p>
        {run && (
          <p>
            Negozi: {run.spec.stores.join(', ')} · Data di riferimento:{' '}
            {new Date(run.spec.as_of).toLocaleString('it-IT')}
          </p>
        )}
        <div className="sd-modules-actions">
          <Button
            onClick={() => {
              if (!run) {
                setCatalog(null)
                setCatalogError('')
                setRevision((value) => value + 1)
              }
              runs.retry()
            }}
            disabled={submitting}
          >
            Aggiorna stato
          </Button>
          {canConfigure && (
            <>
              <Button
                onClick={() => {
                  setSelection({})
                  setSubmitError('')
                }}
                disabled={!changed || submitting}
              >
                Annulla modifiche
              </Button>
              <Button
                variant="primary"
                onClick={startRun}
                disabled={!changed || issues.length > 0 || submitting}
                loading={submitting}
              >
                Avvia nuovo run con la selezione
              </Button>
            </>
          )}
        </div>
        <p role="status">
          {submitting
            ? 'Invio del nuovo run in corso…'
            : changed
              ? 'Selezione locale modificata, non ancora salvata.'
              : 'Nessuna modifica locale.'}
        </p>
        {changed && issues.length > 0 && (
          <ul>
            {issues.map((issue) => (
              <li key={issue}>{issue}</li>
            ))}
          </ul>
        )}
        {submitError && (
          <p role="alert">
            {submitError} Se la connessione si è interrotta, verifica prima se
            il nuovo run compare nell’elenco.
          </p>
        )}
      </section>
      {modules.length ? (
        <div className="sd-run-list">
          {modules.map((item) => {
            const execution = run?.module_runs.find(
              (entry) => entry.module_id === item.id
            )
            const status = execution
              ? statuses[execution.status]
              : {
                  label: run ? 'Non eseguito nel run' : 'Non eseguito',
                  tone: 'neutral' as const
                }
            const counts = Object.entries(execution?.result?.counts ?? {})
            return (
              <article className="sd-run-card sd-module" key={item.id}>
                <div className="sd-module-heading">
                  <h2>
                    {item.id} · {item.version}
                  </h2>
                  <StatusBadge {...status} />
                </div>
                <p>{item.description}</p>
                <dl>
                  <dt>Modalità</dt>
                  <dd>
                    {execution?.mode ?? item.mode}
                    {item.boundary === 'simulated' ? ' · simulata' : ''}
                  </dd>
                  <dt>
                    {run
                      ? 'Abilitazione nello snapshot'
                      : 'Abilitazione nel catalogo'}
                  </dt>
                  <dd>{item.enabled ? 'Attivo' : 'Disattivo'}</dd>
                  <dt>Conteggi del risultato</dt>
                  <dd>
                    {counts.length ? (
                      <ul>
                        {counts.map(([kind, count]) => (
                          <li key={kind}>
                            {kind}:{' '}
                            <span className="sd-num">
                              {count.toLocaleString('it-IT')}
                            </span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      'Non disponibili'
                    )}
                  </dd>
                  <dt>Dipendenze richieste</dt>
                  <dd>{item.requires.join(', ') || 'Nessuna'}</dd>
                </dl>
                {execution?.result?.errors.length ? (
                  <div>
                    <h3>Errori</h3>
                    <ul>
                      {execution.result.errors.map((text, index) => (
                        <li key={index}>{text}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {execution?.result?.abstentions.length ? (
                  <div>
                    <h3>Astensioni</h3>
                    <ul>
                      {execution.result.abstentions.map((text, index) => (
                        <li key={index}>{text}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                <label className="sd-module-toggle">
                  <input
                    type="checkbox"
                    checked={selection[item.id] ?? item.enabled}
                    disabled={
                      !canConfigure || item.mode === 'unavailable' || submitting
                    }
                    aria-describedby="module-selection-help"
                    onChange={(event) => {
                      setSelection((current) => ({
                        ...current,
                        [item.id]: event.target.checked
                      }))
                      setSubmitError('')
                    }}
                  />
                  {item.id}: attivo nel prossimo run
                </label>
                {item.mode === 'unavailable' && (
                  <p>Modulo non disponibile: attivazione non consentita.</p>
                )}
              </article>
            )
          })}
        </div>
      ) : (
        <EmptyState
          title="Nessun modulo disponibile"
          description={
            run
              ? 'Lo snapshot selezionato non contiene moduli.'
              : 'Il catalogo installato è vuoto.'
          }
        />
      )}
    </div>
  )
}
