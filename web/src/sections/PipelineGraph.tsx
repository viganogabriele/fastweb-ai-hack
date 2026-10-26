import { useEffect, useId, useState } from 'react'
import type { CSSProperties } from 'react'
import type { LucideIcon } from 'lucide-react'
import { ArrowRight, Ban, ChevronRight, CircleCheck, CircleDashed, CircleX, LoaderCircle, TriangleAlert, X } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import type { ModuleManifest, RunView } from '../api/client'
import { ErrorState, StatusBadge, transition } from '../ui'
import {
  buildModuleGraph, layers, lineage, moduleDetailId, moduleStatuses, NODE_HEIGHT, NODE_WIDTH, phases
} from './moduleGraph'
import { moduleMetrics } from './moduleCounts'
import type { GraphNode } from './moduleGraph'
import { actorIcons, ModuleGlyph, moduleTitle, phaseIcons, phaseOf, phaseSlot } from './moduleCatalog'
import { useElementWidth } from './useElementWidth'
import './pipelineGraph.css'

type Execution = RunView['module_runs'][number]
// Shape plus colour, so the state never rests on colour alone.
const statusIcons: Record<string, LucideIcon> = {
  succeeded: CircleCheck,
  degraded: TriangleAlert,
  blocked: TriangleAlert,
  failed: CircleX,
  running: LoaderCircle,
  pending: CircleDashed
}
const statusPlurals: Record<string, string> = {
  pending: 'in attesa', running: 'in corso', succeeded: 'completati', degraded: 'parziali', blocked: 'bloccati', failed: 'con errore'
}
// Below this the labels get too small to read: the canvas scrolls instead of shrinking.
const MIN_SCALE = 0.72
/** Phase colour as a custom property, read by the icon tile and the phase strip. */
const phaseColor = (key: string) => ({ '--sd-pipeline-phase': `var(--sd-phase-${phaseSlot(key)})` }) as CSSProperties
const flows = (execution: Execution | undefined) => execution?.status === 'succeeded' || execution?.status === 'degraded'

export function PipelineGraph({ modules, run }: {
  modules: readonly ModuleManifest[]; run?: RunView
}) {
  const id = useId()
  const [selected, setSelected] = useState<string | null>(null)
  const [hovered, setHovered] = useState<string | null>(null)
  const [phase, setPhase] = useState<string | null>(null)
  // After the first interaction, dimming must react at once instead of waiting for the entrance delay.
  const entered = Boolean(hovered ?? selected ?? phase)
  const { ref, width } = useElementWidth<HTMLDivElement>(1100)
  const graph = buildModuleGraph(modules)

  useEffect(() => {
    if (!selected) return
    const close = (event: KeyboardEvent) => event.key === 'Escape' && setSelected(null)
    window.addEventListener('keydown', close)
    return () => window.removeEventListener('keydown', close)
  }, [selected])

  if (!graph.valid)
    return <ErrorState title="Grafo non verificabile" description={graph.issues.join(' ')} />
  if (!graph.nodes.length) return null

  const nodes = new Map(graph.nodes.map((node) => [node.id, node]))
  const executions = new Map(run?.module_runs.map((entry) => [entry.module_id, entry]))
  const routes = graph.routes
  const focus = hovered ?? selected
  const phaseLayers = phases.find((item) => item.key === phase)?.layers
  // A module's lineage wins over a phase: pointing at one module is the more specific question.
  const lit = focus && nodes.has(focus)
    ? lineage(graph, focus)
    : phaseLayers
      ? new Set(graph.nodes.filter((node) => node.manifest && phaseLayers.includes(node.manifest.layer)).map((node) => node.id))
      : null
  const current = selected ? nodes.get(selected) : undefined
  const scale = Math.min(1, Math.max(MIN_SCALE, width / graph.width))
  const marker = `${id}-arrow`

  const statusOf = (node: GraphNode) => {
    const execution = executions.get(node.id)
    return execution
      ? { key: execution.status, ...moduleStatuses[execution.status] }
      : { key: 'none', label: run ? 'Non eseguito nel run' : 'Non eseguito', tone: 'neutral' as const }
  }
  // The run's own mode is already in the header: a node names it only when it differs.
  const mode = (value: string) => (value === run?.spec.mode ? '' : ` · ${value}`)
  const total = (execution: Execution | undefined) =>
    execution?.result ? Object.values(execution.result.counts).reduce((sum, count) => sum + count, 0) : null
  const tally = graph.nodes.reduce<Record<string, number>>((counts, node) => {
    const key = node.manifest && !node.manifest.enabled ? 'disabled' : statusOf(node).key
    counts[key] = (counts[key] ?? 0) + 1
    return counts
  }, {})

  function openDetails(moduleId: string) {
    const card = document.getElementById(moduleDetailId(moduleId))
    card?.focus({ preventScroll: true })
    card?.scrollIntoView({ block: 'center' })
  }

  return (
    <section className="sd-run-card sd-pipeline" aria-labelledby={`${id}-title`}>
      <div className="sd-module-heading">
        <h2 id={`${id}-title`}>Grafo della pipeline</h2>
        <span className="sd-pipeline__source">
          {run ? 'Manifest dello snapshot selezionato' : 'Manifest del catalogo installato'}
        </span>
      </div>
      <p id={`${id}-help`}>
        Dalle fonti in alto ai report in basso: ogni freccia va dalla dipendenza al modulo che la usa.
        Passa sopra una fase o un modulo per vederne i moduli e la filiera, selezionalo per i dettagli.
      </p>
      <ol className="sd-pipeline__phases" aria-label="Fasi della pipeline" onMouseLeave={() => setPhase(null)}>
        {phases.map((item, index) => {
          const count = graph.nodes.filter((node) => node.manifest && item.layers.includes(node.manifest.layer)).length
          const PhaseIcon = phaseIcons[item.key]
          const Actor = actorIcons[item.key]
          return (
            <li key={item.key} style={phaseColor(item.key)}>
              <button type="button" className={phase === item.key ? 'is-active' : ''}
                onMouseEnter={() => setPhase(item.key)} onFocus={() => setPhase(item.key)} onBlur={() => setPhase(null)}>
                <span className="sd-pipeline__phase-head">
                  <span className="sd-pipeline__tile"><PhaseIcon aria-hidden="true" /></span>
                  <span className="sd-pipeline__step sd-num">{String(index + 1).padStart(2, '0')}</span>
                </span>
                <strong>{item.name}</strong>
                <span className="sd-pipeline__who"><Actor aria-hidden="true" />{item.who}</span>
                <span className="sd-pipeline__phase-text">{item.text}</span>
                <span className="sd-pipeline__phase-count">{count === 1 ? '1 modulo' : `${count} moduli`}</span>
              </button>
              {index < phases.length - 1 && <ChevronRight className="sd-pipeline__arrow" aria-hidden="true" />}
            </li>
          )
        })}
      </ol>
      <ul className="sd-pipeline__tally" aria-label="Moduli per stato">
        <li><strong className="sd-num">{graph.nodes.length}</strong> moduli</li>
        {Object.entries(moduleStatuses).map(([key, status]) => tally[key]
          ? <li key={key} className={`is-${key}`}><strong className="sd-num">{tally[key]}</strong> {statusPlurals[key] ?? status.label.toLowerCase()}</li>
          : null)}
        {tally.none ? <li><strong className="sd-num">{tally.none}</strong> non eseguiti</li> : null}
        {tally.disabled ? <li><strong className="sd-num">{tally.disabled}</strong> disattivi</li> : null}
      </ul>
      <div className="sd-pipeline__legend">
        <span><i aria-hidden="true" /> Dipendenza richiesta</span>
        <span><i className="sd-pipeline__optional" aria-hidden="true" /> Ingresso opzionale</span>
        {run && <span><i className="sd-pipeline__flowing" aria-hidden="true" /> Dati passati nel run</span>}
      </div>
      {graph.issues.length > 0 && (
        <ul className="sd-pipeline__issues" role="status">
          {graph.issues.map((issue) => <li key={issue}>{issue}</li>)}
        </ul>
      )}
      <div className="sd-pipeline__body">
        <div className="sd-pipeline__scroll" ref={ref} role="region" aria-label="Moduli e dipendenze"
          aria-describedby={`${id}-help`} tabIndex={0}>
          <div className="sd-pipeline__frame" style={{ width: graph.width * scale, height: graph.height * scale }}>
            <div className={`sd-pipeline__canvas${lit ? ' is-focused' : ''}`}
              style={{ width: graph.width, height: graph.height, transform: `scale(${scale})` }}
              onMouseLeave={() => setHovered(null)}>
              <svg className="sd-pipeline__edges" width={graph.width} height={graph.height}
                aria-hidden="true" focusable="false">
                <defs>
                  <marker id={marker} viewBox="0 0 10 10" refX="8" refY="5"
                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
                  </marker>
                </defs>
                {routes.map((route) => {
                  const on = lit ? lit.has(route.source) && lit.has(route.target) : false
                  const state = lit ? (on ? ' is-lit' : ' is-dim') : ''
                  // Edges draw in from the top, row by row, as the data would travel.
                  const delay = 0.15 + (nodes.get(route.source)!.y / graph.height) * 0.6
                  const moving = flows(executions.get(route.source)) && Boolean(executions.get(route.target))
                  return (
                    <g key={route.key} className={`sd-pipeline__route${state}`}>
                      <motion.path d={route.d} markerEnd={`url(#${marker})`}
                        className={route.optional ? 'sd-pipeline__edge sd-pipeline__edge--optional' : 'sd-pipeline__edge'}
                        initial={route.optional ? { opacity: 0 } : { pathLength: 0 }}
                        animate={route.optional ? { opacity: 1 } : { pathLength: 1 }}
                        transition={{ duration: 0.5, ease: transition.view.ease, delay }} />
                      {moving && <path d={route.d} className="sd-pipeline__flow" style={{ animationDelay: `${-delay * 3}s` }} />}
                    </g>
                  )
                })}
              </svg>
              {graph.nodes.map((node) => {
                const manifest = node.manifest
                const execution = executions.get(node.id)
                const status = statusOf(node)
                const Icon = manifest && !manifest.enabled ? Ban : statusIcons[status.key] ?? CircleDashed
                const count = total(execution)
                const classes = [
                  'sd-pipeline__node',
                  `is-${status.key}`,
                  manifest ? '' : 'sd-pipeline__node--missing',
                  manifest && !manifest.enabled ? 'sd-pipeline__node--disabled' : '',
                  lit ? (lit.has(node.id) ? 'is-lit' : 'is-dim') : '',
                  selected === node.id ? 'is-selected' : ''
                ].filter(Boolean).join(' ')
                return (
                  <motion.button key={node.id} type="button" className={classes}
                    style={{ left: node.x, top: node.y, width: NODE_WIDTH, height: NODE_HEIGHT, ...phaseColor(manifest ? phaseOf(manifest.layer) : 'sources') }}
                    // Opacity lives in motion, not CSS: motion's inline style would override a dimming class.
                    initial={{ opacity: 0, y: -6 }}
                    animate={{ opacity: lit && !lit.has(node.id) ? 0.35 : 1, y: 0 }}
                    transition={{ ...transition.view, delay: entered ? 0 : (node.y / graph.height) * 0.6 }}
                    aria-pressed={selected === node.id}
                    onMouseEnter={() => setHovered(node.id)}
                    onFocus={() => setHovered(node.id)}
                    onBlur={() => setHovered(null)}
                    onClick={() => setSelected((value) => (value === node.id ? null : node.id))}>
                    <span className="sd-pipeline__tile"><ModuleGlyph id={node.id} manifest={manifest} /></span>
                    <span className="sd-pipeline__text">
                      <strong>{moduleTitle(node.id)}</strong>
                      <span className="sd-pipeline__meta">
                        <Icon className="sd-pipeline__icon" aria-hidden="true" />
                        <span>
                          {node.id}
                          {manifest
                            ? <>{mode(execution?.mode ?? manifest.mode)}{manifest.boundary === 'simulated' ? ' · simulata' : ''}</>
                            : ' · manifest assente'}
                        </span>
                        {count !== null && <span className="sd-pipeline__count sd-num">{count.toLocaleString('it-IT')}</span>}
                      </span>
                    </span>
                    <span className="sd-visually-hidden">
                      {manifest && !manifest.enabled ? 'Disattivo. ' : ''}{status.label}.
                      {count !== null ? ` ${count} elementi prodotti.` : ''}
                    </span>
                  </motion.button>
                )
              })}
            </div>
          </div>
        </div>
        <AnimatePresence initial={false}>
          {current && (
            <motion.aside key="detail" className="sd-pipeline__detail" aria-label={`Dettagli di ${moduleTitle(current.id)}`}
              initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0, transition: transition.drawer }}
              exit={{ opacity: 0, x: 16, transition: transition.exit }}>
              <ModuleDetail node={current} graph={graph} execution={executions.get(current.id)} status={statusOf(current)}
                inRun={Boolean(run)} onSelect={setSelected} onClose={() => setSelected(null)} onOpen={openDetails} />
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}

function ModuleDetail({ node, graph, execution, status, inRun, onSelect, onClose, onOpen }: {
  node: GraphNode
  graph: ReturnType<typeof buildModuleGraph>
  execution: Execution | undefined
  status: { label: string; tone: Parameters<typeof StatusBadge>[0]['tone'] }
  inRun: boolean
  onSelect: (id: string) => void
  onClose: () => void
  onOpen: (id: string) => void
}) {
  const manifest = node.manifest
  const feeds = graph.edges.filter((edge) => edge.source === node.id)
  const counts = moduleMetrics(execution?.result?.counts ?? {})
  const chips = (ids: readonly string[], optional = false) => ids.length
    ? <ul className="sd-pipeline__chips">
        {ids.map((target) => (
          <li key={target}>
            <button type="button" className={optional ? 'is-optional' : ''} onClick={() => onSelect(target)} title={target}>{moduleTitle(target)}</button>
          </li>
        ))}
      </ul>
    : <span className="sd-pipeline__none">Nessuno</span>
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div key={node.id} className="sd-pipeline__detail-body"
        initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0, transition: transition.view }}
        exit={{ opacity: 0, transition: transition.exit }}>
        <header style={phaseColor(manifest ? phaseOf(manifest.layer) : 'sources')}>
          <span className="sd-pipeline__tile is-large"><ModuleGlyph id={node.id} manifest={manifest} /></span>
          <div>
            <span className="sd-pipeline__eyebrow">{manifest ? layers[manifest.layer] : 'Dipendenza'}</span>
            <h3>{moduleTitle(node.id)}</h3>
            <span className="sd-pipeline__id">{node.id}</span>
          </div>
          <button type="button" className="sd-pipeline__close" onClick={onClose} aria-label="Chiudi i dettagli">
            <X aria-hidden="true" />
          </button>
        </header>
        <StatusBadge label={status.label} tone={status.tone} />
        {manifest ? (
          <>
            <p>{manifest.description}</p>
            <dl>
              <div><dt>Versione</dt><dd>{manifest.version}</dd></div>
              <div><dt>Modalità</dt><dd>{execution?.mode ?? manifest.mode}{manifest.boundary === 'simulated' ? ' · simulata' : ''}</dd></div>
              <div><dt>{inRun ? 'Nello snapshot' : 'Nel catalogo'}</dt><dd>{manifest.enabled ? 'Attivo' : 'Disattivo'}</dd></div>
            </dl>
            <h4>Usa</h4>
            {chips(manifest.requires)}
            {manifest.optional_inputs.length > 0 && <><h4>Ingressi opzionali</h4>{chips(manifest.optional_inputs, true)}</>}
            <h4>Alimenta</h4>
            {chips(feeds.map((edge) => edge.target))}
            <h4>Produce</h4>
            {counts.length
              ? <ul className="sd-pipeline__counts">
                  {counts.map((metric) => (
                    <li key={metric.key} className={metric.value === 0 ? 'is-zero' : undefined}><span>{metric.label}</span>
                      <strong className="sd-num">{metric.value.toLocaleString('it-IT')}{metric.fresh !== null && <small> · {metric.fresh.toLocaleString('it-IT')} nuovi</small>}</strong></li>
                  ))}
                </ul>
              : <span className="sd-pipeline__none">{manifest.produces.join(', ') || 'Nulla'}{inRun ? ' · conteggi non disponibili' : ''}</span>}
            {execution?.result?.errors.length ? (
              <><h4>Errori</h4><ul className="sd-pipeline__notes is-error">{execution.result.errors.map((text, i) => <li key={i}>{text}</li>)}</ul></>
            ) : null}
            {execution?.result?.abstentions.length ? (
              <><h4>Astensioni</h4><ul className="sd-pipeline__notes">{execution.result.abstentions.map((text, i) => <li key={i}>{text}</li>)}</ul></>
            ) : null}
            <button type="button" className="sd-pipeline__open" onClick={() => onOpen(node.id)}>
              Apri la scheda completa <ArrowRight aria-hidden="true" />
            </button>
          </>
        ) : (
          <p>Manifest assente: {node.required ? 'dipendenza richiesta' : 'ingresso opzionale'} di un altro modulo.</p>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
