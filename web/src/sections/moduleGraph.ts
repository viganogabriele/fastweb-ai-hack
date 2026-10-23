import type { ModuleManifest } from '../api/client'
import type { StatusTone } from '../ui/StatusBadge'

export const moduleStatuses: Record<string, { label: string; tone: StatusTone }> = {
  pending: { label: 'In attesa', tone: 'neutral' },
  running: { label: 'In corso', tone: 'info' },
  succeeded: { label: 'Completato', tone: 'success' },
  degraded: { label: 'Parziale', tone: 'warning' },
  blocked: { label: 'Bloccato', tone: 'warning' },
  failed: { label: 'Errore', tone: 'danger' }
}
export const NODE_WIDTH = 232
export const NODE_HEIGHT = 148
const GAP_X = 64
const GAP_Y = 28
const PADDING = 24

export type GraphNode = {
  id: string
  manifest: ModuleManifest | null
  x: number
  y: number
  required: boolean
}
export type GraphEdge = { source: string; target: string; optional: boolean }
export type ModuleGraph = {
  nodes: GraphNode[]
  edges: GraphEdge[]
  width: number
  height: number
  issues: string[]
  valid: boolean
}

// Use only the selected snapshot or the installed catalog; never infer dependencies
// from artifact names, execution order, or manifests belonging to another run.
export function buildModuleGraph(modules: readonly ModuleManifest[]): ModuleGraph {
  const empty: ModuleGraph = { nodes: [], edges: [], width: 0, height: 0, issues: [], valid: true }
  const known = new Map<string, ModuleManifest>()
  for (const module of modules) {
    if (!module.id.trim() || known.has(module.id))
      return { ...empty, valid: false, issues: ['I manifest contengono ID vuoti o duplicati.'] }
    known.set(module.id, module)
  }
  const nodes = new Map<string, GraphNode>(
    [...known].map(([id, manifest]) => [id, { id, manifest, x: 0, y: 0, required: false }])
  )
  const edges: GraphEdge[] = []
  for (const module of modules) {
    for (const [optional, ids] of [[false, module.requires], [true, module.optional_inputs]] as const) {
      for (const source of new Set(ids)) {
        if (optional && module.requires.includes(source)) continue
        if (!nodes.has(source))
          nodes.set(source, { id: source, manifest: null, x: 0, y: 0, required: false })
        if (!optional) nodes.get(source)!.required = true
        edges.push({ source, target: module.id, optional })
      }
    }
  }
  edges.sort((a, b) => a.source.localeCompare(b.source, 'en') || a.target.localeCompare(b.target, 'en'))
  const ids = [...nodes.keys()].sort((a, b) => a.localeCompare(b, 'en'))
  const incoming = new Map(ids.map((id) => [id, 0]))
  const outgoing = new Map(ids.map((id) => [id, [] as string[]]))
  const depth = new Map(ids.map((id) => [id, 0]))
  for (const edge of edges) {
    incoming.set(edge.target, incoming.get(edge.target)! + 1)
    outgoing.get(edge.source)!.push(edge.target)
  }
  const ready = ids.filter((id) => incoming.get(id) === 0)
  let visited = 0
  while (ready.length) {
    const id = ready.shift()!
    visited++
    for (const target of outgoing.get(id)!) {
      depth.set(target, Math.max(depth.get(target)!, depth.get(id)! + 1))
      incoming.set(target, incoming.get(target)! - 1)
      if (incoming.get(target) === 0) ready.push(target)
    }
  }
  if (visited !== ids.length)
    return { ...empty, valid: false, issues: ['I manifest dichiarano dipendenze cicliche: il grafo non può essere verificato.'] }
  const columns: GraphNode[][] = []
  for (const id of ids) (columns[depth.get(id)!] ??= []).push(nodes.get(id)!)
  const rows = Math.max(0, ...columns.map((column) => column.length))
  const height = rows ? PADDING * 2 + rows * NODE_HEIGHT + (rows - 1) * GAP_Y : 0
  columns.forEach((column, x) => {
    const columnHeight = column.length * NODE_HEIGHT + (column.length - 1) * GAP_Y
    column.forEach((node, y) => {
      node.x = PADDING + x * (NODE_WIDTH + GAP_X)
      node.y = (height - columnHeight) / 2 + y * (NODE_HEIGHT + GAP_Y)
    })
  })
  return {
    nodes: ids.map((id) => nodes.get(id)!), edges, height, valid: true,
    width: columns.length ? PADDING * 2 + columns.length * NODE_WIDTH + (columns.length - 1) * GAP_X : 0,
    issues: ids.filter((id) => !known.has(id) && nodes.get(id)!.required)
      .map((id) => `Dipendenza richiesta assente dai manifest: ${id}.`)
  }
}
export const moduleDetailId = (id: string) => `pipeline-module-${encodeURIComponent(id)}`
