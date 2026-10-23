import type { Case } from '../api/client'
import { productIndex } from './productView.ts'

// Catalog served at /api/runs/{id}/products (dev mock today, scripts/build-products-mock.mjs).
// Photos are illustrative references matched by category (data/catalog/README.md), not the
// simulated items themselves; stock is the ERP end-of-day snapshot available by the cutoff.
export type StoreStock = { sizes: Record<string, number>; in_transit: number }
export type CatalogColour = { sku: string; colour: string; stores: string[]; stock: Record<string, StoreStock> }
export type CatalogProduct = {
  style_code: string
  name: string
  category: string
  subcategory: string
  gender: string
  price_eur: number
  image: string
  reference: { name: string; url: string }
  colours: CatalogColour[]
}
export type ProductCatalog = { available_at: string; snapshot_date: string; products: CatalogProduct[] }

export type Attention = 'now' | 'later' | 'none'
export type ProductCard = { product: CatalogProduct; cases: Case[]; attention: Attention; skus: Set<string> }

const priorityRank: Record<Case['priority'], number> = { critical: 0, high: 1, medium: 2, low: 3 }
const isActive = (item: Case) => item.status !== 'closed' && item.status !== 'decided'

/**
 * Links the run's cases to catalog products by exact scope only: a style by its code, a SKU by
 * its code, a SKU-size by its SKU followed by `-<size>`. Anything else stays unresolved, never
 * assigned to a product by guess. Immediate attention: an active critical or high case;
 * deferred: any other active case; none: no active case.
 */
export function productCards(catalog: ProductCatalog, cases: Case[], runId: string) {
  const index = productIndex(cases, runId)
  const linkOf = productLinker(catalog)
  const linked = new Map<string, { cases: Case[]; skus: Set<string> }>()
  const unresolved = index.unresolved.filter(isActive)
  for (const group of index.groups) {
    const link = linkOf(group.level, group.id)
    const style = link?.product.style_code
    const sku = link?.sku
    const active = group.cases.filter(isActive)
    if (!style) {
      unresolved.push(...active)
      continue
    }
    const entry = linked.get(style) ?? { cases: [], skus: new Set<string>() }
    entry.cases.push(...active)
    if (sku) entry.skus.add(sku)
    linked.set(style, entry)
  }
  const cards: ProductCard[] = catalog.products.map((product) => {
    const entry = linked.get(product.style_code)
    const own = (entry?.cases ?? []).sort(byUrgency)
    const attention: Attention = !own.length ? 'none' : priorityRank[own[0].priority] <= 1 ? 'now' : 'later'
    return { product, cases: own, attention, skus: entry?.skus ?? new Set() }
  })
  cards.sort((a, b) =>
    (a.cases.length && b.cases.length ? byUrgency(a.cases[0], b.cases[0]) : b.cases.length - a.cases.length) ||
    a.product.name.localeCompare(b.product.name, 'it'))
  return { cards, unresolved: unresolved.sort(byUrgency) }
}

/**
 * Exact catalog link for a case scope: a style by its code, a SKU by its code, a SKU-size by its
 * SKU followed by `-<size>`. Returns undefined for any other scope, never a guess.
 */
export function productLinker(catalog: ProductCatalog) {
  const styles = new Map(catalog.products.map((product) => [product.style_code, product]))
  const bySku = new Map(catalog.products.flatMap((product) => product.colours.map((colour) => [colour.sku, product] as const)))
  return (level: string, id: string | null | undefined): { product: CatalogProduct; sku?: string } | undefined => {
    if (!id) return undefined
    if (level === 'style') return styles.has(id) ? { product: styles.get(id)! } : undefined
    if (level !== 'sku' && level !== 'sku_size') return undefined
    const sku = level === 'sku_size' ? id.slice(0, Math.max(0, id.lastIndexOf('-'))) : id
    const product = bySku.get(sku)
    return product ? { product, sku } : undefined
  }
}

function byUrgency(a: Case, b: Case) {
  const due = (item: Case) => (item.decision_due_at ? Date.parse(item.decision_due_at) : Infinity)
  return priorityRank[a.priority] - priorityRank[b.priority] || due(a) - due(b) || a.id.localeCompare(b.id)
}

export type Availability = 'in' | 'out' | 'none'
export type StoreRow = { store: string; availability: Availability; units: number; inTransit: number; sizes: [string, number][] }

/** One row per run store for a colour: carried and in stock, carried but sold out, or not carried. */
export function storeRows(colour: CatalogColour, stores: readonly string[]): StoreRow[] {
  return stores.map((store) => {
    const stock = colour.stock[store]
    const sizes = Object.entries(stock?.sizes ?? {}).sort(([a], [b]) => compareSizes(a, b))
    const units = sizes.reduce((sum, [, count]) => sum + count, 0)
    const carried = colour.stores.includes(store)
    return {
      store,
      availability: !carried ? 'none' : units > 0 ? 'in' : 'out',
      units,
      inTransit: stock?.in_transit ?? 0,
      sizes
    }
  })
}

const LETTER_SIZES = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
/** Sizes in wearing order: letter sizes by scale, numeric ones by value with `00` below `0`. */
export function compareSizes(a: string, b: string) {
  const rank = (size: string) => {
    const letter = LETTER_SIZES.indexOf(size.toUpperCase())
    if (letter >= 0) return letter
    if (/^0\d+$/.test(size)) return -1 / size.length
    const number = Number(size.replace(',', '.'))
    return Number.isFinite(number) ? 100 + number : NaN
  }
  const [x, y] = [rank(a), rank(b)]
  if (Number.isNaN(x) || Number.isNaN(y)) return Number.isNaN(x) === Number.isNaN(y) ? a.localeCompare(b) : Number.isNaN(x) ? 1 : -1
  return x - y
}

/** Network view of a product across the run's stores and all its colours. */
export function productStock(product: CatalogProduct, stores: readonly string[]) {
  const rows = product.colours.flatMap((colour) => storeRows(colour, stores))
  const byStore = new Map<string, Availability>()
  for (const row of rows) {
    const current = byStore.get(row.store)
    if (row.availability === 'in' || (row.availability === 'out' && current !== 'in') || !current) byStore.set(row.store, row.availability)
  }
  const values = [...byStore.values()]
  return {
    units: rows.reduce((sum, row) => sum + row.units, 0),
    storesIn: values.filter((value) => value === 'in').length,
    storesOut: values.filter((value) => value === 'out').length
  }
}
