import assert from 'node:assert/strict'
import { test } from 'node:test'
import { buildModuleGraph, moduleDetailId, NODE_HEIGHT, NODE_WIDTH } from '../src/sections/moduleGraph.ts'

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
    assert.ok(nodes.get(edge.source).x + NODE_WIDTH < nodes.get(edge.target).x)
  for (const node of graph.nodes) {
    assert.ok(node.x >= 0 && node.y >= 0)
    assert.ok(node.x + NODE_WIDTH <= graph.width)
    assert.ok(node.y + NODE_HEIGHT <= graph.height)
    for (const other of graph.nodes)
      if (node.id !== other.id && node.x === other.x)
        assert.ok(node.y + NODE_HEIGHT <= other.y || other.y + NODE_HEIGHT <= node.y)
  }
})

test('empty manifests are supported and repeated dependency declarations make one required edge', () => {
  assert.deepEqual(buildModuleGraph([]), {
    nodes: [], edges: [], width: 0, height: 0, issues: [], valid: true
  })
  const graph = buildModuleGraph([module('a'), module('b', ['a', 'a'], ['a'])])
  assert.deepEqual(graph.edges, [{ source: 'a', target: 'b', optional: false }])
  assert.notEqual(moduleDetailId('a/b'), moduleDetailId('a%2Fb'))
})
