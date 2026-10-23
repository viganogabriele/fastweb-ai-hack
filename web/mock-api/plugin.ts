import type { IncomingMessage, ServerResponse } from 'node:http'
import type { Plugin } from 'vite'
import { CASES, DOCUMENTS, MODULES, RUNS, documentDetail, forRun } from './data.ts'

/**
 * Dev-only fake backend: answers `/api/*` before the proxy, with the same paths and JSON shapes
 * as FastAPI. The UI code is unchanged, so switching back to the real backend is just running
 * `npm run dev` instead of `npm run dev:mock`. Unmocked routes return 404, never real data.
 */
export function mockApi(): Plugin {
  return {
    name: 'tessera-mock-api',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/api', (req, res) => {
        void handle(req, res)
      })
    }
  }
}

async function handle(req: IncomingMessage, res: ServerResponse) {
  const url = new URL(req.url ?? '/', 'http://mock')
  const parts = url.pathname.split('/').filter(Boolean).map(decodeURIComponent)
  // A short delay keeps loading states visible, as with the real backend.
  await new Promise((resolve) => setTimeout(resolve, 250))

  if (req.method === 'POST' && parts.length === 1 && parts[0] === 'runs')
    return send(res, 409, { detail: 'Il mock non avvia nuovi run: usa il backend reale.' })
  if (req.method !== 'GET') return send(res, 405, { detail: 'Metodo non supportato dal mock' })

  const [root, runId, collection, itemId] = parts
  if (root === 'health')
    return send(res, 200, { status: 'ok', version: 'mock', llm_mode: 'mock', sources_present: true, fastweb_models_configured: [] })
  if (root === 'modules' && parts.length === 1) return send(res, 200, MODULES)
  if (root !== 'runs') return notFound(res)
  if (!runId) return send(res, 200, RUNS)

  const run = RUNS.find((item) => item.spec.run_id === runId)
  if (!run) return notFound(res)
  if (!collection) return send(res, 200, run)

  if (collection === 'cases') {
    const cases = forRun(runId, CASES, (item) => item.store_id) ?? []
    if (!itemId) return send(res, 200, cases)
    const found = cases.find((item) => item.id === itemId)
    return found ? send(res, 200, found) : notFound(res)
  }
  if (collection === 'documents') {
    const documents = forRun(runId, DOCUMENTS, (item) => String(item.meta.store_id)) ?? []
    if (!itemId) return send(res, 200, documents)
    const detail = documents.some((item) => item.id === itemId) ? documentDetail(itemId) : undefined
    return detail ? send(res, 200, detail) : notFound(res)
  }
  return notFound(res)
}

function send(res: ServerResponse, status: number, body: unknown) {
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json')
  res.setHeader('X-Tessera-Mock', '1')
  res.end(JSON.stringify(body))
}

const notFound = (res: ServerResponse) => send(res, 404, { detail: 'Non presente nel mock' })
