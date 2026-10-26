import { compareSizes } from './productsData.ts'
import type { ProductCatalog } from './productsData.ts'

export type OnlineProduct = {
  sku: string; styleName: string; colorName: string; category: string; launchDate: string | null
  isNew: boolean; totalRequests: number; bySize: { size: string; requests: number }[]
  topCountries: { country: string; requests: number }[]; pending: number; converted: number | null
}
export type OnlineData = {
  topRequested: OnlineProduct[]
  webStockouts: { sku: string; events: number }[]
  zeroResults: { country: string; terms: { term: string; searches: number }[] }[]
  meta: { cutoff: string; requestWindowStart: string; searchWindowStart: string; files: { path: string; sha256: string; rowsAfterCutoff: number }[] }
}

export const formatOnlineCount = (count: number) => count.toLocaleString('it-IT')
export const formatOnlineConversions = (count: number | null) => count === null ? 'n.d.' : formatOnlineCount(count)

/** UTC is explicit: the browser's locale must never shift the evidence cutoff. */
export function formatOnlineCutoff(cutoff: string) {
  const date = new Date(cutoff)
  if (!Number.isFinite(date.getTime())) return 'data non disponibile'
  const part = (value: number) => String(value).padStart(2, '0')
  return `${part(date.getUTCDate())}/${part(date.getUTCMonth() + 1)} ${part(date.getUTCHours())}:${part(date.getUTCMinutes())} UTC`
}
export const onlineLabel = (cutoff: string) => `E-commerce · dati sintetici · calcolato al ${formatOnlineCutoff(cutoff)}`
export const onlineProductHref = (sku: string) => `#/prodotti/${encodeURIComponent(sku)}`

export function onlineSkuFromHash(hash: string) {
  const [route, sku] = hash.replace(/^#\/?/, '').split('/')
  if (route !== 'prodotti' || !sku) return null
  try { return decodeURIComponent(sku) } catch { return null }
}

/** Exact SKU-colour lookup: style prefixes and another colour never match. */
export function onlineCatalogMatch(catalog: ProductCatalog, sku: string) {
  for (const product of catalog.products) {
    const colour = product.colours.find((entry) => entry.sku === sku)
    if (colour) return { product, colour }
  }
  return null
}

export function topOnlineProducts(products: readonly OnlineProduct[], limit = 5) {
  return [...products].sort((a, b) => b.totalRequests - a.totalRequests || a.sku.localeCompare(b.sku)).slice(0, Math.max(0, limit))
}
export function onlineForSku(data: OnlineData, sku: string | undefined) {
  return {
    product: data.topRequested.find((product) => product.sku === sku) ?? null,
    stockouts: data.webStockouts.filter((row) => row.sku === sku).reduce((sum, row) => sum + row.events, 0)
  }
}
export function onlineSizeBars(sizes: OnlineProduct['bySize']) {
  const peak = Math.max(1, ...sizes.map((row) => row.requests))
  return [...sizes].sort((a, b) => compareSizes(a.size, b.size)).map((row) => ({ ...row, percent: row.requests / peak * 100 }))
}
export function onlineCountries(countries: OnlineProduct['topCountries']) {
  return [...countries].sort((a, b) => b.requests - a.requests || a.country.localeCompare(b.country))
}
export function onlineSearches(groups: OnlineData['zeroResults']) {
  return groups.map((group) => ({ ...group, terms: [...group.terms].sort((a, b) => b.searches - a.searches || a.term.localeCompare(b.term)) }))
    .sort((a, b) => a.country.localeCompare(b.country))
}
