// Builds mock-api/market.json: network-level market trends for the executive view of the
// overview, from the synthetic sources. Run from web/: node scripts/build-market-mock.mjs
//
// - Sales: whole network (all stores), EUR at the dataset's budget rate (one median rate per
//   currency). Year-on-year compares the same weekdays (364 days back) or, per month, the same
//   days of the month, so a partial month is never compared with a full one.
// - Categories: SKU sales joined to the catalogue category.
// - Social: Pulsewire exports. Records can span lines and some are malformed, and the schema
//   changed mid-September (sentiment string → {label}), so fields are extracted per record and
//   documents are de-duplicated by doc_id, as the vendor README asks.
import { readFile, readdir, writeFile } from 'node:fs/promises'

const SOURCES = new URL('../../generated/sources/', import.meta.url)
const TARGET = new URL('../mock-api/market.json', import.meta.url)
const DAY = 86_400_000

const csv = async (path) => {
  const [header, ...lines] = (await readFile(new URL(path, SOURCES), 'utf8')).trim().split('\n')
  const columns = header.split(',')
  return lines.map((line) => Object.fromEntries(line.split(',').map((value, index) => [columns[index], value])))
}
const shift = (date, days) => new Date(Date.parse(`${date}T00:00:00Z`) + days * DAY).toISOString().slice(0, 10)
const median = (values) => values.sort((a, b) => a - b)[Math.floor(values.length / 2)]

const stores = await csv('erp/master_data/stores.csv')
const regionOf = Object.fromEntries(stores.map((store) => [store.store_id, store.region]))
const REGIONS = ['EMEA', 'AMERICAS', 'APAC']

const kpi = await csv('erp/kpi/store_daily_kpi.csv')
const rates = {}
for (const currency of new Set(kpi.map((row) => row.currency))) {
  rates[currency] = median(
    kpi.filter((row) => row.currency === currency && Number(row.net_sales_lc) > 0).map((row) => Number(row.net_sales_eur_bud) / Number(row.net_sales_lc))
  )
}
const end = kpi.reduce((max, row) => (row.business_date > max ? row.business_date : max), '')
const euro = (row, field) => Number(row[field]) * rates[row.currency]

// Monthly sales per region, current year against last year on the same days of the month.
const months = []
for (let index = 11; index >= 0; index--) {
  const date = new Date(Date.UTC(Number(end.slice(0, 4)), Number(end.slice(5, 7)) - 1 - index, 1))
  months.push(date.toISOString().slice(0, 7))
}
const lastDayOfMonth = (month) => (month === end.slice(0, 7) ? Number(end.slice(8, 10)) : 31)
const monthly = months.map((month) => {
  const lastYear = `${Number(month.slice(0, 4)) - 1}${month.slice(4)}`
  const upTo = lastDayOfMonth(month)
  const regions = Object.fromEntries(REGIONS.map((region) => [region, { sales: 0, ly: 0, budget: 0 }]))
  for (const row of kpi) {
    const region = regions[regionOf[row.store_id]]
    if (!region || Number(row.business_date.slice(8, 10)) > upTo) continue
    if (row.business_date.startsWith(month)) {
      region.sales += euro(row, 'net_sales_lc')
      region.budget += euro(row, 'budget_lc')
    } else if (row.business_date.startsWith(lastYear)) region.ly += euro(row, 'net_sales_lc')
  }
  for (const value of Object.values(regions)) for (const key of Object.keys(value)) value[key] = Math.round(value[key])
  return { month, partial_until: upTo < 31 ? upTo : null, regions }
})

// 28-day windows: now, the 28 days before, and the same weekdays a year earlier.
const window = (from, to) => (date) => date >= from && date <= to
const now = window(shift(end, -27), end)
const before = window(shift(end, -55), shift(end, -28))
const lastYear = window(shift(end, -27 - 364), shift(end, -364))
const regions = REGIONS.map((region) => {
  const sum = (inWindow) =>
    Math.round(kpi.filter((row) => regionOf[row.store_id] === region && inWindow(row.business_date)).reduce((total, row) => total + euro(row, 'net_sales_lc'), 0))
  return { region, sales: sum(now), before: sum(before), ly: sum(lastYear) }
})

// Category momentum from SKU sales.
const catalogue = await csv('erp/master_data/sku_colour.csv')
const categoryOf = Object.fromEntries(catalogue.map((row) => [row.sku, row.category]))
const categories = {}
const salesDir = new URL('erp/sales/daily_store_sku/', SOURCES)
for (const file of (await readdir(salesDir)).filter((name) => name.endsWith('.csv')).sort()) {
  for (const row of await csv(`erp/sales/daily_store_sku/${file}`)) {
    const date = row.business_date
    const bucket = now(date) ? 'sales' : before(date) ? 'before' : lastYear(date) ? 'ly' : null
    if (!bucket) continue
    const category = categoryOf[row.sku] ?? 'Altro'
    categories[category] ??= { category, sales: 0, before: 0, ly: 0, units: 0 }
    categories[category][bucket] += Number(row.net_sales_lc) * rates[row.currency]
    if (bucket === 'sales') categories[category].units += Number(row.units_sold)
  }
}
const categoryList = Object.values(categories)
  .map((row) => ({ ...row, sales: Math.round(row.sales), before: Math.round(row.before), ly: Math.round(row.ly) }))
  .sort((a, b) => b.sales - a.sales)

// Social buzz: one record per doc_id, sentiment normalised, hashtags kept.
const socialDir = new URL('external/social/pulsewire/', SOURCES)
const posts = new Map()
for (const file of (await readdir(socialDir)).filter((name) => name.endsWith('.jsonl'))) {
  const text = await readFile(new URL(file, socialDir), 'utf8')
  for (const chunk of text.split(/(?=\{"doc_id")/)) {
    const id = chunk.match(/"doc_id":\s*"([^"]+)"/)?.[1]
    const published = chunk.match(/"published_at":\s*"([^"]+)"/)?.[1]
    if (!id || !published || posts.has(id)) continue
    const label = chunk.match(/"sentiment":\s*(?:\{\s*"label":\s*)?"([a-z]+)"/)?.[1] ?? 'neutral'
    const sentiment = label.startsWith('pos') ? 'pos' : label.startsWith('neg') ? 'neg' : 'neu'
    const tags = [...(chunk.match(/"hashtags":\s*\[([^\]]*)\]/)?.[1] ?? '').matchAll(/"([^"]+)"/g)].map((match) => match[1].toLowerCase())
    posts.set(id, { date: published.slice(0, 10), sentiment, tags })
  }
}
const known = [...posts.values()].filter((post) => post.date <= end)
const mondayOf = (date) => {
  const day = new Date(`${date}T00:00:00Z`).getUTCDay()
  return shift(date, -((day + 6) % 7))
}
const weeks = {}
for (const post of known) {
  const week = mondayOf(post.date)
  weeks[week] ??= { week, pos: 0, neu: 0, neg: 0 }
  weeks[week][post.sentiment] += 1
}
const recent = window(shift(end, -13), end)
const earlier = window(shift(end, -27), shift(end, -14))
const tagCounts = {}
for (const post of known) {
  const bucket = recent(post.date) ? 'now' : earlier(post.date) ? 'before' : null
  if (!bucket) continue
  for (const tag of new Set(post.tags)) {
    tagCounts[tag] ??= { tag, now: 0, before: 0 }
    tagCounts[tag][bucket] += 1
  }
}
const hashtags = Object.values(tagCounts)
  .filter((row) => row.now >= 5)
  .sort((a, b) => b.now - b.before - (a.now - a.before))
  .slice(0, 10)

const market = {
  last_day: end,
  available_at: `${shift(end, 1)}T06:00:00Z`,
  monthly,
  regions,
  categories: categoryList,
  social: { weeks: Object.values(weeks).sort((a, b) => a.week.localeCompare(b.week)), hashtags, posts: known.length }
}
await writeFile(TARGET, `${JSON.stringify(market)}\n`)
console.log(`market.json: last day ${end}, ${monthly.length} months, ${categoryList.length} categories, ${known.length} social posts, ${hashtags.length} rising hashtags`)
