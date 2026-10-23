import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildModuleGraph, lineage, moduleDetailId, NODE_HEIGHT, NODE_WIDTH } from '../src/sections/moduleGraph.ts'

const module = (id, requires = [], optional_inputs = [], enabled = true) => ({
  id, requires, optional_inputs, enabled, version: '1', layer: 'sources',
  description: id, produces: ['SourceDocument'], mode: 'recorded', params_schema: {}
})

test('edges come from declared requirements and optional inputs, never matching artifact names', () => {
  const manifests = [module('src.email'), module('src.erp'),
    module('ing.extract', ['src.email']), module('int.cases', ['ing.extract'], ['src.erp']),
    module('disabled', [], [], false)]
  const before = structuredClone(manifests)
  const graph = buildModuleGraph(manifests)
  assert.equal(graph.valid, true)
  assert.deepEqual(graph.issues, [])
  assert.deepEqual(graph.edges, [
    { source: 'ing.extract', target: 'int.cases', optional: false },
    { source: 'src.email', target: 'ing.extract', optional: false },
    { source: 'src.erp', target: 'int.cases', optional: true }
  ])
  assert.equal(graph.nodes.find((n) => n.id === 'disabled').manifest.enabled, false)
  assert.deepEqual(manifests, before)
  assert.deepEqual(buildModuleGraph([...manifests].reverse()), graph)
})

test('missing dependencies stay explicit placeholders with warnings only for required inputs', () => {
  const graph = buildModuleGraph([module('consumer', ['missing'], ['optional'])])
  assert.equal(graph.valid, true)
  assert.deepEqual(graph.issues, ['Dipendenza richiesta assente dai manifest: missing.'])
  assert.equal(graph.nodes.find((n) => n.id === 'missing').manifest, null)
  assert.equal(graph.nodes.find((n) => n.id === 'missing').required, true)
  assert.equal(graph.nodes.find((n) => n.id === 'optional').required, false)
  assert.equal(graph.nodes.find((n) => n.id === 'optional').manifest, null)
})

test('cycles and ambiguous module identities do not produce a misleading graph', () => {
  for (const manifests of [
    [module('a', ['b']), module('b', [], ['a'])],
    [module('self', ['self'])], [module('duplicate'), module('duplicate')], [module(' ')]
  ]) {
    const graph = buildModuleGraph(manifests)
    assert.equal(graph.valid, false)
    assert.ok(graph.issues.length)
    assert.deepEqual(graph.nodes, [])
    assert.deepEqual(graph.edges, [])
  }
})

test('layout is bounded and every dependency precedes its consumer, including disconnected modules', () => {
  const graph = buildModuleGraph([
    module('root'), module('a', ['root']), module('b', ['root']),
    module('end', ['a', 'b']), module('separate')
  ])
  const nodes = new Map(graph.nodes.map((n) => [n.id, n]))
  for (const edge of graph.edges)
    assert.ok(nodes.get(edge.source).y + NODE_HEIGHT < nodes.get(edge.target).y)
  for (const node of graph.nodes) {
    assert.ok(node.x >= 0 && node.y >= 0)
    assert.ok(node.x + NODE_WIDTH <= graph.width)
    assert.ok(node.y + NODE_HEIGHT <= graph.height)
    for (const other of graph.nodes)
      if (node.id !== other.id && node.y === other.y)
        assert.ok(node.x + NODE_WIDTH <= other.x || other.x + NODE_WIDTH <= node.x)
  }
})

test('empty manifests are supported and repeated dependency declarations make one required edge', () => {
  assert.deepEqual(buildModuleGraph([]), {
    nodes: [], edges: [], routes: [], width: 0, height: 0, issues: [], valid: true
  })
  const graph = buildModuleGraph([module('a'), module('b', ['a', 'a'], ['a'])])
  assert.deepEqual(graph.edges, [{ source: 'a', target: 'b', optional: false }])
  assert.notEqual(moduleDetailId('a/b'), moduleDetailId('a%2Fb'))
})

test('rows avoid crossings that the barycenter order can remove', () => {
  // Declared so that alphabetical order would cross: a feeds z, b feeds y.
  const graph = buildModuleGraph([module('a'), module('b'), module('y', ['b']), module('z', ['a'])])
  const x = Object.fromEntries(graph.nodes.map((n) => [n.id, n.x]))
  assert.equal(x.a < x.b, x.z < x.y)
})

test('lineage follows dependencies both ways and leaves siblings out', () => {
  const graph = buildModuleGraph([
    module('src'), module('other'), module('mid', ['src']), module('sibling', ['src']),
    module('out', ['mid'], ['other'])
  ])
  assert.deepEqual([...lineage(graph, 'mid')].sort(), ['mid', 'out', 'src'])
  assert.deepEqual([...lineage(graph, 'out')].sort(), ['mid', 'other', 'out', 'src'])
})

test('edge routes leave the bottom of the dependency and reach the top of the consumer', () => {
  const graph = buildModuleGraph([module('a'), module('b', ['a']), module('c', ['a'])])
  const nodes = new Map(graph.nodes.map((n) => [n.id, n]))
  const routes = graph.routes
  assert.equal(routes.length, graph.edges.length)
  const starts = routes.map((route) => route.d.match(/^M ([\d.]+) ([\d.]+)/).slice(1).map(Number))
  assert.notEqual(starts[0][0], starts[1][0])
  for (const [i, route] of routes.entries()) {
    const from = nodes.get(route.source)
    assert.equal(starts[i][1], from.y + NODE_HEIGHT)
    assert.ok(starts[i][0] > from.x && starts[i][0] < from.x + NODE_WIDTH)
  }
})

test('an edge that skips rows runs down a trunk between nodes, shared by its source', () => {
  // far feeds both deep modules; the chain a → b → c → d pushes them three rows down.
  const graph = buildModuleGraph([
    module('far'), module('a'), module('b', ['a']), module('c', ['b']),
    module('d', ['c', 'far']), module('e', ['c'], ['far'])
  ])
  const nodes = new Map(graph.nodes.map((n) => [n.id, n]))
  const lanes = graph.routes.filter((route) => route.source === 'far').map((route) => route.d.match(/L ([\d.]+) /g))
  assert.equal(lanes.length, 2)
  assert.deepEqual(lanes[0].slice(0, 2), lanes[1].slice(0, 2))
  for (const route of graph.routes)
    for (const [, x, y] of route.d.matchAll(/L ([\d.]+) ([\d.]+)/g))
      for (const node of graph.nodes)
        if (Math.abs(Number(y) - (node.y + NODE_HEIGHT)) < 0.5)
          assert.ok(Number(x) < node.x || Number(x) > node.x + NODE_WIDTH, `${route.key} crosses ${node.id}`)
  assert.ok(nodes.get('far').y < nodes.get('d').y)
})
