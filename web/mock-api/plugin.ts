import { readFileSync } from 'node:fs'
import type { IncomingMessage, ServerResponse } from 'node:http'
import type { Plugin } from 'vite'
import { CASES, DOCUMENTS, MODULES, RUNS, documentDetail, forRun } from './data.ts'

// Daily store KPIs from the synthetic ERP export (scripts/build-kpi-mock.mjs). Mock-only: the
// backend has no KPI endpoint yet, so the UI shows the series as unavailable there.
type KpiDay = { date: string; store_id: string; available_at: string; sales_eur: number; budget_eur: number; receipts: number; visitors: number; units: number; returns_units: number }
let kpi: KpiDay[] | undefined
const kpiDays = () => (kpi ??= JSON.parse(readFileSync(new URL('./kpi.json', import.meta.url), 'utf8')) as KpiDay[])
// Network market trends (scripts/build-market-mock.mjs), computed for a single cutoff.
let marketData: { available_at: string } | undefined
const market = () => (marketData ??= JSON.parse(readFileSync(new URL('./market.json', import.meta.url), 'utf8')) as { available_at: string })
// Catalog with stock and assortment (scripts/build-products-mock.mjs), for a single cutoff. Photos
// are the local reference images under data/catalog/images.
type CatalogColour = { stores: string[]; stock: Record<string, unknown> }
type Catalog = { available_at: string; products: { colours: CatalogColour[] }[] }
let catalogData: Catalog | undefined
const catalog = () => (catalogData ??= JSON.parse(readFileSync(new URL('./products.json', import.meta.url), 'utf8')) as Catalog)
const IMAGES = new URL('../../data/catalog/images/', import.meta.url)

/**
 * Dev-only fake backend: answers `/api/*` before the proxy, with the same paths and JSON shapes
 * as FastAPI. The UI code is unchanged, so switching back to the real backend is just running
 * `npm run dev` instead of `npm run dev:mock`. Unmocked routes return 404, never real data.
 */
export function mockApi(): Plugin {
  return {
    name: 'tesseract-mock-api',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/api', (req, res) => {
        void handle(req, res).catch(() => {
          if (!res.headersSent) send(res, 400, { detail: 'Richiesta mock non valida' })
          else res.end()
        })
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

  if (parts.length > 4) return notFound(res)
  const [root, runId, collection, itemId] = parts
  if (root === 'health' && parts.length === 1)
    return send(res, 200, { status: 'ok', version: 'mock', llm_mode: 'mock', sources_present: true, fastweb_models_configured: [] })
  if (root === 'modules' && parts.length === 1) return send(res, 200, MODULES)
  if (root === 'catalog' && runId === 'images' && collection && /^[\w-]+\.jpg$/.test(collection) && parts.length === 3) {
    res.setHeader('Content-Type', 'image/jpeg')
    res.setHeader('Cache-Control', 'max-age=3600')
    return res.end(readFileSync(new URL(collection, IMAGES)))
  }
  if (root !== 'runs') return notFound(res)
  if (!runId) return send(res, 200, RUNS)

  const run = RUNS.find((item) => item.spec.run_id === runId)
  if (!run) return notFound(res)
  if (!collection) return send(res, 200, run)
  if (!run.published) return send(res, 409, { detail: 'Run non ancora pubblicato' })

  if (collection === 'cases') {
    const cases = forRun(runId, CASES, (item) => item.store_id) ?? []
    if (!itemId) return send(res, 200, cases)
    const found = cases.find((item) => item.id === itemId)
    return found ? send(res, 200, found) : notFound(res)
  }
  if (collection === 'documents') {
    const documents = forRun(runId, DOCUMENTS, (item) => String(item.meta.store_id)) ?? []
    if (!itemId) return send(res, 200, documents)
    const detail = documents.some((item) => item.id === itemId) ? documentDetail(itemId, runId) : undefined
    return detail ? send(res, 200, detail) : notFound(res)
  }
  if (collection === 'kpi' && !itemId) return send(res, 200, forRun(runId, kpiDays(), (item) => item.store_id) ?? [])
  if (collection === 'market' && !itemId) {
    // Network-level aggregates exist for one cutoff only: earlier runs must not see them.
    const data = market()
    return Date.parse(data.available_at) <= Date.parse(run.spec.as_of)
      ? send(res, 200, data)
      : send(res, 404, { detail: 'Trend di mercato non disponibili a questo cutoff' })
  }
  if (collection === 'products' && !itemId) {
    const data = catalog()
    if (Date.parse(data.available_at) > Date.parse(run.spec.as_of))
      return send(res, 404, { detail: 'Stock non disponibile a questo cutoff' })
    // Only the run's stores: assortment and stock elsewhere are outside its selection.
    const stores = new Set(run.spec.stores)
    return send(res, 200, {
      ...data,
      products: data.products.map((product) => ({
        ...product,
        colours: product.colours.map((colour) => ({
          ...colour,
          stores: colour.stores.filter((store) => stores.has(store)),
          stock: Object.fromEntries(Object.entries(colour.stock).filter(([store]) => stores.has(store)))
        }))
      }))
    })
  }
  return notFound(res)
}

function send(res: ServerResponse, status: number, body: unknown) {
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json')
  res.setHeader('X-Tesseract-Mock', '1')
  res.end(JSON.stringify(body))
}

const notFound = (res: ServerResponse) => send(res, 404, { detail: 'Non presente nel mock' })
