import { useId } from 'react'
import type { ModuleManifest, RunView } from '../api/client'
import { ErrorState, StatusBadge } from '../ui'
import {
  buildModuleGraph, moduleDetailId, moduleStatuses, NODE_HEIGHT, NODE_WIDTH
} from './moduleGraph'
import './pipelineGraph.css'

export function PipelineGraph({ modules, run }: {
  modules: readonly ModuleManifest[]; run?: RunView
}) {
  const id = useId()
  const graph = buildModuleGraph(modules)
  if (!graph.valid)
    return <ErrorState title="Grafo non verificabile" description={graph.issues.join(' ')} />
  if (!graph.nodes.length) return null
  const nodes = new Map(graph.nodes.map((node) => [node.id, node]))
  const marker = `${id}-arrow`
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
        Le frecce vanno dalla dipendenza al modulo che la usa. Seleziona un modulo
        per aprire i dettagli nell’elenco. Le modifiche per il prossimo run non
        cambiano questo grafo.
      </p>
      <div className="sd-pipeline__legend">
        <span><i aria-hidden="true" /> Dipendenza richiesta</span>
        <span><i className="sd-pipeline__optional" aria-hidden="true" /> Ingresso opzionale</span>
      </div>
      {graph.issues.length > 0 && (
        <ul className="sd-pipeline__issues" role="status">
          {graph.issues.map((issue) => <li key={issue}>{issue}</li>)}
        </ul>
      )}
      <div className="sd-pipeline__scroll" role="region" aria-label="Moduli e dipendenze"
        aria-describedby={`${id}-help`} tabIndex={0}>
        <div className="sd-pipeline__canvas" style={{ width: graph.width, height: graph.height }}>
          <svg className="sd-pipeline__edges" width={graph.width} height={graph.height}
            aria-hidden="true" focusable="false">
            <defs>
              <marker id={marker} viewBox="0 0 10 10" refX="9" refY="5"
                markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
              </marker>
            </defs>
            {graph.edges.map((edge) => {
              const from = nodes.get(edge.source)!
              const to = nodes.get(edge.target)!
              const x = from.x + NODE_WIDTH
              const y = from.y + NODE_HEIGHT / 2
              const endY = to.y + NODE_HEIGHT / 2
              const mid = (x + to.x) / 2
              return <path key={JSON.stringify([edge.source, edge.target])}
                d={`M ${x} ${y} C ${mid} ${y}, ${mid} ${endY}, ${to.x - 3} ${endY}`}
                className={edge.optional ? 'sd-pipeline__edge sd-pipeline__edge--optional' : 'sd-pipeline__edge'}
                markerEnd={`url(#${marker})`} />
            })}
          </svg>
          {graph.nodes.map((node) => {
            const style = { left: node.x, top: node.y, width: NODE_WIDTH, height: NODE_HEIGHT }
            const manifest = node.manifest
            if (!manifest)
              return <div key={node.id} className="sd-pipeline__node sd-pipeline__node--missing" style={style}>
                <strong>{node.id}</strong>
                <span>Manifest assente</span>
                <small>{node.required ? 'Dipendenza richiesta' : 'Ingresso opzionale'}</small>
              </div>
            const execution = run?.module_runs.find((entry) => entry.module_id === node.id)
            const status = execution ? moduleStatuses[execution.status] : {
              label: run ? 'Non eseguito nel run' : 'Non eseguito', tone: 'neutral' as const
            }
            return <button key={node.id} type="button" style={style}
              className={`sd-pipeline__node${manifest.enabled ? '' : ' sd-pipeline__node--disabled'}`}
              onClick={() => openDetails(node.id)}>
              <strong>{node.id}</strong>
              <span className="sd-pipeline__meta">
                {manifest.version} · {execution?.mode ?? manifest.mode}
                {manifest.boundary === 'simulated' ? ' · simulata' : ''}
              </span>
              <StatusBadge {...status} />
              <small>{manifest.enabled
                ? (run ? 'Attivo nello snapshot' : 'Attivo nel catalogo')
                : (run ? 'Disattivo nello snapshot' : 'Disattivo nel catalogo')}</small>
              <span className="sd-visually-hidden">
                Richiede: {manifest.requires.join(', ') || 'nessuna dipendenza'}.
                Ingressi opzionali: {manifest.optional_inputs.join(', ') || 'nessuno'}.
                Apri i dettagli di {node.id}.
              </span>
            </button>
          })}
        </div>
      </div>
    </section>
  )
}
