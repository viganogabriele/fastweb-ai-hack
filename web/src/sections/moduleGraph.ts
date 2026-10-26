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
export const layers: Record<ModuleManifest['layer'], string> = {
  sources: 'Fonti',
  ingestion: 'Ingestione',
  integration: 'Integrazione',
  intelligence: 'Intelligenza',
  actions: 'Azioni',
  agents: 'Agenti',
  outputs: 'Output'
}
const LAYER_ORDER = Object.keys(layers)
// The RFC §0 story in six steps: who does the work at each step is the point of the page.
export const phases: { key: string; name: string; who: string; text: string; layers: ModuleManifest['layer'][] }[] = [
  { key: 'sources', name: 'Fonti', who: 'Dati', layers: ['sources'],
    text: 'Email di chiusura, note vocali, chat, report, ERP, meteo e magazzino entrano con negozio e data.' },
  { key: 'ingestion', name: 'Lettura', who: 'L’AI legge', layers: ['ingestion'],
    text: 'Il testo diventa osservazioni atomiche, ognuna con la citazione verificata nel documento.' },
  { key: 'integration', name: 'Collegamento', who: 'L’AI collega, il codice verifica', layers: ['integration'],
    text: 'Le osservazioni si legano a prodotti e negozi, i doppioni si uniscono e nascono i casi.' },
  { key: 'intelligence', name: 'Previsione', who: 'Il codice conta', layers: ['intelligence'],
    text: 'Baseline del forecast e scenari basso, base e alto per ogni caso di domanda.' },
  { key: 'decision', name: 'Opzioni', who: 'Il codice controlla, l’AI indaga', layers: ['actions', 'agents'],
    text: 'Trasferimenti, riassortimenti e verifiche fattibili; l’agente approfondisce i casi aperti.' },
  { key: 'outputs', name: 'Report', who: 'L’umano decide', layers: ['outputs'],
    text: 'Brief per ufficio con citazioni cliccabili: approvare o rifiutare resta a una persona.' }
]
// Top to bottom: sources first, outputs last. Rows are dependency depth, so every arrow points down.
export const NODE_WIDTH = 212
export const NODE_HEIGHT = 72
const GAP_X = 28
const GAP_Y = 52
const PADDING = 24
const SWEEPS = 6
// A trunk is the vertical line that carries one module's output past the rows in between.
const TRUNK_WIDTH = 8
// A lane keeps this much air from a module's side, and lanes keep twice LANE_SPACING apart.
const LANE_CLEARANCE = 10
const LANE_SPACING = 8

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
  routes: EdgeRoute[]
  width: number
  height: number
  issues: string[]
  valid: boolean
}
export type EdgeRoute = GraphEdge & { key: string; d: string }

// Use only the selected snapshot or the installed catalog; never infer dependencies
// from artifact names, execution order, or manifests belonging to another run.
export function buildModuleGraph(modules: readonly ModuleManifest[]): ModuleGraph {
  const empty: ModuleGraph = { nodes: [], edges: [], routes: [], width: 0, height: 0, issues: [], valid: true }
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
  // Layered layout (Sugiyama style). An edge that skips rows runs down its source's trunk: one
  // slot per skipped row, shared by every edge of that source, so long edges pass between the
  // nodes instead of through them and a module that feeds many rows draws one line, not many.
  type Item = { key: string; node?: GraphNode; source?: string; width: number; x: number }
  const rowOf = (id: string) => depth.get(id)!
  const rows: Item[][] = []
  const layerRank = (item: Item) => item.node?.manifest ? LAYER_ORDER.indexOf(item.node.manifest.layer) : -1
  for (const id of ids) (rows[rowOf(id)] ??= []).push({ key: id, node: nodes.get(id)!, width: NODE_WIDTH, x: 0 })
  for (const row of rows) row.sort((a, b) => layerRank(a) - layerRank(b) || a.key.localeCompare(b.key, 'en'))
  const trunk = (source: string, row: number) => `trunk:${source}:${row}`
  const reach = new Map(ids.map((id) => [id, Math.max(rowOf(id), ...outgoing.get(id)!.map(rowOf))]))
  for (const id of ids)
    for (let row = rowOf(id) + 1; row < reach.get(id)!; row++)
      rows[row].push({ key: trunk(id, row), source: id, width: TRUNK_WIDTH, x: 0 })
  // Links between consecutive rows: source → first hop, trunk → trunk, last hop → target.
  const up = new Map<string, Set<string>>()
  const down = new Map<string, Set<string>>()
  const link = (from: string, to: string) => {
    if (!down.has(from)) down.set(from, new Set())
    if (!up.has(to)) up.set(to, new Set())
    down.get(from)!.add(to)
    up.get(to)!.add(from)
  }
  const hopAbove = (edge: GraphEdge) =>
    rowOf(edge.target) - rowOf(edge.source) > 1 ? trunk(edge.source, rowOf(edge.target) - 1) : edge.source
  for (const edge of edges) {
    for (let row = rowOf(edge.source) + 1; row < rowOf(edge.target); row++)
      link(row === rowOf(edge.source) + 1 ? edge.source : trunk(edge.source, row - 1), trunk(edge.source, row))
    link(hopAbove(edge), edge.target)
  }
  // Barycenter sweeps: order each row by the mean slot of its links in the row above
  // (downward) or below (upward). Ties keep the previous order, so the result is deterministic.
  const slot = new Map<string, number>()
  const index = () => rows.forEach((row) => row.forEach((item, i) => slot.set(item.key, i)))
  index()
  for (let sweep = 0; sweep < SWEEPS; sweep++) {
    const downward = sweep % 2 === 0
    const order = downward ? rows.slice(1) : rows.slice(0, -1).reverse()
    for (const row of order) {
      const center = new Map(row.map((item) => {
        const near = [...((downward ? up : down).get(item.key) ?? [])]
        return [item.key, near.length ? near.reduce((sum, key) => sum + slot.get(key)!, 0) / near.length : slot.get(item.key)!]
      }))
      row.sort((a, b) => center.get(a.key)! - center.get(b.key)! || slot.get(a.key)! - slot.get(b.key)!)
      row.forEach((item, i) => slot.set(item.key, i))
    }
    index()
  }
  // Placement: only modules take room in a row; trunks only steered the order above.
  const placed = rows.map((row) => row.filter((item) => item.node))
  const rowWidth = (row: Item[]) => row.length * NODE_WIDTH + Math.max(0, row.length - 1) * GAP_X
  let width = rows.length ? PADDING * 2 + Math.max(...placed.map(rowWidth)) : 0
  const centers = new Map<string, number>()
  placed.forEach((row, y) => {
    let x = (width - rowWidth(row)) / 2
    for (const item of row) {
      item.node!.x = x
      item.node!.y = PADDING + y * (NODE_HEIGHT + GAP_Y)
      centers.set(item.key, x + NODE_WIDTH / 2)
      x += NODE_WIDTH + GAP_X
    }
  })
  const top = (row: number) => PADDING + row * (NODE_HEIGHT + GAP_Y)

  // Lanes: each source that skips rows gets one vertical line, straight through every row it
  // passes, at the free x nearest to the source. Free means clear of modules and of other lanes.
  // Longest spans choose first; if nothing fits, the lane goes past the right edge.
  const blocked = placed.map((row) => row.map((item) => [item.node!.x - LANE_CLEARANCE, item.node!.x + NODE_WIDTH + LANE_CLEARANCE]))
  const spans = ids.filter((id) => reach.get(id)! > rowOf(id) + 1)
    .map((id) => ({ id, from: rowOf(id) + 1, to: reach.get(id)! - 1 }))
    .sort((a, b) => b.to - b.from - (a.to - a.from) || centers.get(a.id)! - centers.get(b.id)!)
  const free = (x: number, from: number, to: number) => {
    for (let row = from; row <= to; row++)
      if (blocked[row].some(([left, right]) => x > left && x < right)) return false
    return true
  }
  let overflow = 0
  for (const span of spans) {
    const preferred = Math.round(centers.get(span.id)!)
    let lane: number | undefined
    for (let offset = 0; lane === undefined && offset <= width; offset++)
      for (const x of offset ? [preferred - offset, preferred + offset] : [preferred])
        if (x >= PADDING / 2 && x <= width - PADDING / 2 && free(x, span.from, span.to)) { lane = x; break }
    if (lane === undefined) lane = width - PADDING / 2 + LANE_SPACING * overflow++
    for (let row = span.from; row <= span.to; row++) {
      blocked[row].push([lane - LANE_SPACING, lane + LANE_SPACING])
      centers.set(trunk(span.id, row), lane)
    }
  }
  if (overflow) width += LANE_SPACING * overflow

  // Ports: one per distinct first hop on a node's bottom and per distinct last hop on its top,
  // ordered by where the hop sits, so curves fan out instead of meeting at one point.
  const ports = (groups: Map<string, string[]>) => {
    const at = new Map<string, number>()
    for (const [id, hops] of groups) {
      const unique = [...new Set(hops)].sort((a, b) => centers.get(a)! - centers.get(b)!)
      const node = nodes.get(id)!
      unique.forEach((hop, i) => at.set(`${id}>${hop}`, node.x + (NODE_WIDTH * (i + 1)) / (unique.length + 1)))
    }
    return at
  }
  const hopBelow = (edge: GraphEdge) =>
    rowOf(edge.target) - rowOf(edge.source) > 1 ? trunk(edge.source, rowOf(edge.source) + 1) : edge.target
  const firstHops = new Map<string, string[]>()
  const lastHops = new Map<string, string[]>()
  for (const edge of edges) {
    firstHops.set(edge.source, [...(firstHops.get(edge.source) ?? []), hopBelow(edge)])
    lastHops.set(edge.target, [...(lastHops.get(edge.target) ?? []), hopAbove(edge)])
  }
  const outPort = ports(firstHops)
  const inPort = ports(lastHops)
  const curve = (x1: number, y1: number, x2: number, y2: number) => {
    const bend = (y2 - y1) / 2
    return `C ${x1} ${y1 + bend}, ${x2} ${y2 - bend}, ${x2} ${y2}`
  }
  // Two bends at most: into the lane in the gap under the source, out of it in the gap above the target.
  const routes = edges.map((edge) => {
    const from = rowOf(edge.source)
    const to = rowOf(edge.target)
    const start = outPort.get(`${edge.source}>${hopBelow(edge)}`)!
    const end = inPort.get(`${edge.target}>${hopAbove(edge)}`)!
    let d = `M ${start} ${top(from) + NODE_HEIGHT}`
    let x = start
    let y = top(from) + NODE_HEIGHT
    if (to - from > 1) {
      const lane = centers.get(trunk(edge.source, from + 1))!
      d += ` ${curve(x, y, lane, top(from + 1))} L ${lane} ${top(to - 1) + NODE_HEIGHT}`
      x = lane
      y = top(to - 1) + NODE_HEIGHT
    }
    d += ` ${curve(x, y, end, top(to) - 4)}`
    return { ...edge, key: JSON.stringify([edge.source, edge.target]), d }
  })
  return {
    nodes: ids.map((id) => nodes.get(id)!), edges, routes, width, valid: true,
    height: rows.length ? PADDING * 2 + rows.length * NODE_HEIGHT + (rows.length - 1) * GAP_Y : 0,
    issues: ids.filter((id) => !known.has(id) && nodes.get(id)!.required)
      .map((id) => `Dipendenza richiesta assente dai manifest: ${id}.`)
  }
}
export const moduleDetailId = (id: string) => `pipeline-module-${encodeURIComponent(id)}`

/** The module, everything it depends on and everything that depends on it. */
export function lineage(graph: ModuleGraph, id: string): Set<string> {
  const found = new Set([id])
  for (const [from, to] of [['target', 'source'], ['source', 'target']] as const) {
    const queue = [id]
    while (queue.length) {
      const current = queue.shift()!
      for (const edge of graph.edges)
        if (edge[from] === current && !found.has(edge[to])) {
          found.add(edge[to])
          queue.push(edge[to])
        }
    }
  }
  return found
}
