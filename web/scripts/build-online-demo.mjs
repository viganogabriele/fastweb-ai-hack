// Offline source-only demo. Run from any directory: node web/scripts/build-online-demo.mjs
import { createHash } from 'node:crypto'
import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'

export const CUTOFF = '2026-10-22T20:00:00Z'
const DAY = 86_400_000
export const SOURCE_PATHS = [
  'systems/ecommerce/back_in_stock_requests.csv',
  'systems/ecommerce/site_search_queries_daily.csv',
  'systems/ecommerce/inventory_availability_log.csv',
  'erp/master_data/sku_colour.csv',
]
const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0

// RFC 4180 quoting, embedded newlines, CRLF, BOM and missing final newline.
// Reject malformed records rather than silently shifting columns.
export function parseCsv(text) {
  text = text.replace(/^\uFEFF/, '')
  const records = []
  let record = [], field = '', quoted = false, closed = false
  const cell = () => { record.push(field); field = ''; closed = false }
  const row = () => { cell(); records.push(record); record = [] }
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++ }
      else if (c === '"') { quoted = false; closed = true }
      else field += c
    } else if (c === ',') cell()
    else if (c === '\r' || c === '\n') {
      if (c === '\r' && text[i + 1] === '\n') i++
      row()
    } else if (c === '"' && field === '' && !closed) quoted = true
    else {
      if (closed || c === '"') throw new Error('Malformed CSV quoting')
      field += c
    }
  }
  if (quoted) throw new Error('Unterminated CSV quote')
  if (field !== '' || record.length || closed) row()
  if (!records.length) return []
  const headers = records.shift()
  if (headers.some((h) => !h) || new Set(headers).size !== headers.length) throw new Error('Invalid CSV headers')
  return records.map((values, index) => {
    if (values.length !== headers.length) throw new Error(`CSV row ${index + 2}: expected ${headers.length} columns, got ${values.length}`)
    return Object.fromEntries(headers.map((h, i) => [h, values[i]]))
  })
}

export function timestamp(value) {
  // Inventory exports use an explicitly UTC column with a timezone-free SQL format.
  const normalized = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(value)
    ? `${value.replace(' ', 'T')}Z` : value
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(normalized)) throw new Error(`Invalid timestamp: ${value}`)
  const result = Date.parse(normalized)
  if (!Number.isFinite(result)) throw new Error(`Invalid timestamp: ${value}`)
  return result
}
const dateStart = (date) => {
  const ms = timestamp(`${date}T00:00:00Z`)
  if (new Date(ms).toISOString().slice(0, 10) !== date) throw new Error(`Invalid date: ${date}`)
  return ms
}
export function windows(cutoff = CUTOFF) {
  const end = timestamp(cutoff)
  const completeDayEnd = Math.floor(end / DAY) * DAY
  return { end, requestStart: end - 28 * DAY, searchStart: completeDayEnd - 7 * DAY, searchEnd: completeDayEnd }
}
export function compareSizes(a, b) {
  if (a === b) return 0
  const letters = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'TU']
  if (/^\d+(?:\.\d+)?$/.test(a) && /^\d+(?:\.\d+)?$/.test(b)) return Number(a) - Number(b) || b.length - a.length || compare(a, b)
  const ai = letters.indexOf(a), bi = letters.indexOf(b)
  return ai >= 0 && bi >= 0 ? ai - bi : compare(a, b)
}
const increment = (map, key, amount = 1) => map.set(key, (map.get(key) ?? 0) + amount)
export const normalizeSearchTerm = (term) => term.normalize('NFC').trim().replace(/\s+/gu, ' ').toLowerCase()
const ranked = (map, key, count) => [...map].map(([name, value]) => ({ [key]: name, [count]: value }))
  .sort((a, b) => b[count] - a[count] || compare(a[key], b[key]))

export function buildOnline({ requests, searches, inventory, catalog }, cutoff = CUTOFF) {
  const { end, requestStart, searchStart, searchEnd } = windows(cutoff)
  const catalogBySku = new Map(catalog.map((r) => [r.sku, r]))
  const groups = new Map()
  let futureNotifications = 0, unverifiedConversions = 0
  for (const row of requests) {
    const created = timestamp(row.created_at)
    if (created <= requestStart || created > end) continue
    const item = catalogBySku.get(row.product_id)
    if (!item || row.variant_sku !== `${row.product_id}-${row.size}`) throw new Error(`Unmatched request SKU: ${row.product_id}`)
    let group = groups.get(item.sku)
    if (!group) {
      group = { item, totalRequests: 0, sizes: new Map(), countries: new Map(), pending: 0 }
      groups.set(item.sku, group)
    }
    group.totalRequests++
    increment(group.sizes, row.size)
    increment(group.countries, row.country)
    const notified = row.notified_at ? timestamp(row.notified_at) : Infinity
    if (notified > end) group.pending++
    if (row.notified_at && notified > end) futureNotifications++
    // No conversion/unsubscribe timestamp exists: never project final snapshot state backwards.
    if (row.converted_order) unverifiedConversions++
  }
  const topRequested = [...groups.values()]
    .sort((a, b) => b.totalRequests - a.totalRequests || compare(a.item.sku, b.item.sku)).slice(0, 5)
    .map(({ item, totalRequests, sizes, countries, pending }) => ({
      sku: item.sku, styleName: item.style_name, colorName: item.color_name_en,
      category: item.category, launchDate: item.launch_date || null,
      isNew: !!item.launch_date && dateStart(item.launch_date) <= end && dateStart(item.launch_date) >= end - 60 * DAY,
      totalRequests, bySize: [...sizes].sort(([a], [b]) => compareSizes(a, b)).map(([size, requests]) => ({ size, requests })),
      topCountries: ranked(countries, 'country', 'requests').slice(0, 3), pending, converted: null,
    }))
  const events = new Map(topRequested.map(({ sku }) => [sku, 0]))
  for (const row of inventory) {
    const time = timestamp(row.changed_at_utc)
    if (time <= requestStart || time > end || row.availability_event !== 'OUT_OF_STOCK') continue
    const sku = row.variant_sku.slice(0, row.variant_sku.lastIndexOf('-'))
    if (events.has(sku)) increment(events, sku)
  }
  const countries = new Map()
  for (const row of searches) {
    const day = dateStart(row.date_utc)
    if (day < searchStart || day >= searchEnd || row.zero_result !== 'Y') continue
    const count = Number(row.searches)
    if (!/^\d+$/.test(row.searches) || !Number.isSafeInteger(count)) throw new Error('Invalid search count')
    if (!countries.has(row.country)) countries.set(row.country, new Map())
    const term = normalizeSearchTerm(row.search_term)
    if (!term) throw new Error('Empty search term')
    increment(countries.get(row.country), term, count)
  }
  return {
    topRequested, webStockouts: [...events].map(([sku, events]) => ({ sku, events })),
    zeroResults: [...countries].sort(([a], [b]) => compare(a, b)).map(([country, terms]) => ({ country, terms: ranked(terms, 'term', 'searches').slice(0, 5) })),
    meta: {
      cutoff, requestWindowStart: new Date(requestStart).toISOString().replace('.000Z', 'Z'),
      searchWindowStart: new Date(searchStart).toISOString().slice(0, 10),
      searchWindowEndExclusive: new Date(searchEnd).toISOString().slice(0, 10),
      requestWindowConvention: '(cutoff - 28 days, cutoff]; inventory uses the same window; events count rows, not durations or units.',
      dateOnlyConvention: 'Search date_utc denotes the full UTC day, available at next midnight. Use the last 7 fully complete UTC days; exclude the cutoff day until complete. Launch dates denote UTC midnight; isNew means launched in [cutoff - 60 days, cutoff].',
      searchTermConvention: 'Aggregate exact terms after Unicode NFC normalization, whitespace trimming/collapse and Unicode lowercase; no translation, fuzzy matching or intent inference.',
      pendingConvention: 'Requests with no notification observed by cutoff, including future notifications rewound to pending. Final UNSUBSCRIBED status has no timestamp and is ignored; pending is an upper bound on active subscriptions.',
      convertedConvention: 'null means unknown at cutoff. converted_order has no conversion timestamp; all snapshot conversions are withheld. Final status is never used for historical counts.',
      futureNotificationsRewound: futureNotifications, snapshotConversionsWithheld: unverifiedConversions,
    },
  }
}

export async function main() {
  const sources = new URL('../../generated/sources/', import.meta.url)
  const inputs = await Promise.all(SOURCE_PATHS.map(async (path) => {
    const bytes = await readFile(new URL(path, sources))
    return { path, sha256: createHash('sha256').update(bytes).digest('hex'), rows: parseCsv(bytes.toString('utf8')) }
  }))
  const [requests, searches, inventory, catalog] = inputs.map((input) => input.rows)
  const result = buildOnline({ requests, searches, inventory, catalog })
  const { end } = windows()
  const availability = [
    (r) => timestamp(r.created_at),
    (r) => dateStart(r.date_utc) + DAY,
    (r) => timestamp(r.changed_at_utc),
    (r) => r.launch_date ? dateStart(r.launch_date) : -Infinity,
  ]
  result.meta.files = inputs.map(({ path, sha256, rows }, i) => ({
    path: `generated/sources/${path}`, sha256,
    rowsAfterCutoff: rows.filter((row) => availability[i](row) > end).length,
  }))
  result.meta.fileCutoffConvention = 'rowsAfterCutoff: request creation, search next UTC midnight, inventory event, catalog launch respectively. Catalog is static descriptive metadata; no version history is available.'
  const target = new URL('../src/demo/online.json', import.meta.url)
  await mkdir(new URL('.', target), { recursive: true })
  await writeFile(target, `${JSON.stringify(result, null, 2)}\n`)
  const iridia = result.topRequested.filter((r) => r.styleName === 'IRIDIA').map((r) => ({
    sku: r.sku, totalRequests: r.totalRequests, pending: r.pending, converted: r.converted,
    bySize: r.bySize, topCountries: r.topCountries, stockoutEvents: result.webStockouts.find((s) => s.sku === r.sku).events,
  }))
  console.log(JSON.stringify({ cutoff: CUTOFF, topRequested: result.topRequested.map(({ sku, totalRequests }) => ({ sku, totalRequests })), iridia }))
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main()
