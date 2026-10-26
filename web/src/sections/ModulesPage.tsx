import { useEffect, useState } from 'react'
import type { CSSProperties } from 'react'
import { CircleX, Info } from 'lucide-react'
import { readApi } from '../api/client'
import type { ModuleManifest, RunView } from '../api/client'
import type { useRuns } from '../api/useRuns'
import { EmptyState, ErrorState, LoadingState, StatusBadge } from '../ui'
import { PipelineGraph } from './PipelineGraph'
import { moduleDetailId, moduleStatuses, phases } from './moduleGraph'
import { ModuleGlyph, moduleTitle, phaseIcons, phaseSlot } from './moduleCatalog'
import { moduleMetrics, splitMetrics } from './moduleCounts'
import type { ModuleMetric } from './moduleCounts'
import './sections.css'
import './modules.css'

export function ModulesPage({ runs }: { runs: ReturnType<typeof useRuns> }) {
  const run = runs.selected
  const [catalog, setCatalog] = useState<ModuleManifest[] | null>(null)
  const [catalogError, setCatalogError] = useState('')
  const [revision, setRevision] = useState(0)
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

  return (
    <div className="sd-run-workspace">
      {modules.length > 0 && <PipelineGraph modules={modules} run={run} />}
      {modules.length ? (
        phases.map((phase) => {
          const members = modules.filter((item) => phase.layers.includes(item.layer))
          const PhaseIcon = phaseIcons[phase.key]
          return members.length ? (
        <section className="sd-modules-phase" key={phase.key} aria-labelledby={`modules-phase-${phase.key}`}
          style={{ '--sd-pipeline-phase': `var(--sd-phase-${phaseSlot(phase.key)})` } as CSSProperties}>
          <header className="sd-modules-phase__head">
            <span className="sd-pipeline__tile"><PhaseIcon aria-hidden="true" /></span>
            <h2 id={`modules-phase-${phase.key}`}>{phase.name}</h2>
            <span>{phase.who} · {members.length === 1 ? '1 modulo' : `${members.length} moduli`}</span>
          </header>
        <div className="sd-modules-grid">
          {members.map((item) => <ModuleCard key={item.id} item={item} run={run} />)}
        </div>
        </section>
          ) : null
        })
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

// Plain-language names for what a module produces; unknown kinds keep their contract name.
const outputs: Record<string, [one: string, many: string]> = {
  SourceDocument: ['documento', 'documenti'],
  Segment: ['segmento', 'segmenti'],
  Observation: ['segnale', 'segnali'],
  MetricFact: ['metrica', 'metriche'],
  StockFact: ['dato di stock', 'dati di stock'],
  ContextEvent: ['evento', 'eventi'],
  EntityLink: ['collegamento', 'collegamenti'],
  EvidenceRelation: ['relazione', 'relazioni'],
  Case: ['caso', 'casi'],
  ProductInsight: ['insight', 'insight'],
  ForecastOverlay: ['scenario', 'scenari'],
  ForecastAdjustment: ['correzione', 'correzioni'],
  ActionOption: ['opzione', 'opzioni'],
  AgentTrace: ['indagine', 'indagini'],
  Clarification: ['chiarimento', 'chiarimenti'],
  Report: ['report', 'report']
}
const modes: Record<string, string> = { live: 'Dal vivo', recorded: 'Registrato', fixture: 'Dati demo' }
const outputLabel = (kind: string, count: number) => outputs[kind]?.[count === 1 ? 0 : 1] ?? kind

function openModule(id: string) {
  const card = document.getElementById(moduleDetailId(id))
  card?.focus({ preventScroll: true })
  card?.scrollIntoView({ block: 'center', behavior: 'smooth' })
}

function ModuleCard({ item, run }: { item: ModuleManifest; run: RunView | undefined }) {
  const execution = run?.module_runs.find((entry) => entry.module_id === item.id)
  const status = execution
    ? moduleStatuses[execution.status]
    : { label: run ? 'Non eseguito' : 'Mai eseguito', tone: 'neutral' as const }
  const { primary, rest } = splitMetrics(moduleMetrics(execution?.result?.counts ?? {}))
  const label = (metric: ModuleMetric) => outputs[metric.key] ? outputLabel(metric.key, metric.value) : metric.label
  const errors = execution?.result?.errors ?? []
  const abstentions = execution?.result?.abstentions ?? []
  const mode = execution?.mode ?? item.mode
  return (
    <article className={`sd-module${item.enabled ? '' : ' is-off'}`} id={moduleDetailId(item.id)} tabIndex={-1}>
      <header className="sd-module__head">
        <span className="sd-pipeline__tile"><ModuleGlyph id={item.id} manifest={item} /></span>
        <h3 title={`${item.id} · v${item.version}`}>{moduleTitle(item.id)}</h3>
        <StatusBadge {...status} />
      </header>
      <p className="sd-module__desc" title={item.description}>{item.description}</p>
      {primary.length > 0 && (
        <dl className="sd-module__stats" aria-label="Prodotto nel run">
          {primary.map((metric) => (
            <div key={metric.key}>
              <dt title={label(metric)}>{label(metric)}</dt>
              <dd className="sd-num">{metric.value.toLocaleString('it-IT')}{metric.fresh !== null && <small>{metric.fresh.toLocaleString('it-IT')} nuovi</small>}</dd>
            </div>
          ))}
        </dl>
      )}
      {errors.length > 0 && (
        <p className="sd-module__error" role="status"><CircleX aria-hidden="true" /><span>{errors[0]}{errors.length > 1 && <strong> · altri {errors.length - 1}</strong>}</span></p>
      )}
      {(rest.length > 0 || abstentions.length > 0 || errors.length > 1) && (
        <div className="sd-module__more">
          {rest.length > 0 && (
            <details>
              <summary>Altri {rest.length === 1 ? '1 conteggio' : `${rest.length} conteggi`}</summary>
              <dl className="sd-module__counts">
                {rest.map((metric) => (
                  <div key={metric.key} className={metric.value === 0 ? 'is-zero' : undefined}>
                    <dt title={label(metric)}>{label(metric)}</dt>
                    <dd className="sd-num">{metric.value.toLocaleString('it-IT')}{metric.fresh !== null && ` · ${metric.fresh.toLocaleString('it-IT')} nuovi`}</dd>
                  </div>
                ))}
              </dl>
            </details>
          )}
          {(abstentions.length > 0 || errors.length > 1) && (
            <details className="sd-module__notes">
              <summary><Info aria-hidden="true" />{[
                errors.length > 1 && `${errors.length} errori`,
                abstentions.length > 0 && (abstentions.length === 1 ? '1 nota' : `${abstentions.length} note`)
              ].filter(Boolean).join(' · ')}</summary>
              <ul>
                {errors.length > 1 && errors.map((text, index) => <li key={`e${index}`} className="is-error">{text}</li>)}
                {abstentions.map((text, index) => <li key={`a${index}`}>{text}</li>)}
              </ul>
            </details>
          )}
        </div>
      )}
      <footer className="sd-module__foot">
        <div className="sd-module__deps">
          {item.requires.length ? <>
            <span>Usa</span>
            {item.requires.map((id) => (
              <button key={id} type="button" className="sd-module__chip" onClick={() => openModule(id)}>{moduleTitle(id)}</button>
            ))}
          </> : <span>Punto di partenza</span>}
          {!item.enabled && <span className="sd-module__chip is-flag">Disattivo</span>}
          {item.boundary === 'simulated' && <span className="sd-module__chip is-flag">Simulato</span>}
          {mode === 'unavailable'
            ? <span className="sd-module__chip is-flag">Non disponibile</span>
            : run && mode !== run.spec.mode && <span className="sd-module__chip is-flag">{modes[mode] ?? mode}</span>}
        </div>
      </footer>
    </article>
  )
}
