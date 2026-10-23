// Builds mock-api/kpi.json from the synthetic ERP export, for `npm run dev:mock` only.
// Run from web/: node scripts/build-kpi-mock.mjs
// Sales and budget are converted to EUR at the dataset's budget rate (net_sales_eur_bud /
// net_sales_lc, one median rate per currency), so stores in different currencies can be summed.
import { readFile, writeFile } from 'node:fs/promises'

const SOURCE = new URL('../../generated/sources/erp/kpi/store_daily_kpi.csv', import.meta.url)
const TARGET = new URL('../mock-api/kpi.json', import.meta.url)
// Same store list as mock-api/data.ts; from July the series covers 30- and 90-day views.
const STORES = new Set(['MIL01', 'ROM01', 'CRT01', 'PAR01', 'GVA01', 'LON01', 'NYC01', 'TYO01'])
const FROM = '2026-07-01'

const [header, ...lines] = (await readFile(SOURCE, 'utf8')).trim().split('\n')
const columns = header.split(',')
const rows = lines.map((line) => Object.fromEntries(line.split(',').map((value, index) => [columns[index], value])))

const median = (values) => values.sort((a, b) => a - b)[Math.floor(values.length / 2)]
const rates = {}
for (const currency of new Set(rows.map((row) => row.currency))) {
  const samples = rows
    .filter((row) => row.currency === currency && Number(row.net_sales_lc) > 0)
    .map((row) => Number(row.net_sales_eur_bud) / Number(row.net_sales_lc))
  rates[currency] = median(samples)
}

// A business day is known the next morning: available_at = D+1 06:00 UTC, so the mock can apply
// each run's as_of cutoff like every other record.
const nextMorning = (date) => {
  const day = new Date(`${date}T00:00:00Z`)
  day.setUTCDate(day.getUTCDate() + 1)
  return `${day.toISOString().slice(0, 10)}T06:00:00Z`
}

const out = rows
  .filter((row) => STORES.has(row.store_id) && row.business_date >= FROM)
  .map((row) => ({
    date: row.business_date,
    store_id: row.store_id,
    available_at: nextMorning(row.business_date),
    sales_eur: Math.round(Number(row.net_sales_lc) * rates[row.currency]),
    budget_eur: Math.round(Number(row.budget_lc) * rates[row.currency]),
    receipts: Number(row.receipts),
    visitors: Number(row.visitors_in),
    units: Number(row.units),
    returns_units: Number(row.returns_units)
  }))

await writeFile(TARGET, `${JSON.stringify(out)}\n`)
console.log(`kpi.json: ${out.length} store-days, ${STORES.size} stores, from ${FROM}`)
