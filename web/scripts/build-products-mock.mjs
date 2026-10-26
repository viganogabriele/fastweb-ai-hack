// Builds mock-api/products.json for `npm run dev:mock` only.
// Run from web/: node scripts/build-products-mock.mjs
// Catalog and reference photos come from data/catalog (display metadata, see its README); stock and
// assortment from the synthetic ERP export. Stock is the last end-of-day snapshot available by the
// mock run's cutoff: a snapshot for day D is available at D+1 06:00 UTC, as for the market series.
import { readFile, readdir, writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'

const CUTOFF = '2026-10-22T21:00:00Z'
const ERP = new URL('../../generated/sources/erp/', import.meta.url)
const db = new DatabaseSync(new URL('../../data/catalog/products.sqlite', import.meta.url).pathname, { readOnly: true })

const csv = async (url) => {
  const [header, ...lines] = (await readFile(url, 'utf8')).trim().split('\n')
  const keys = header.split(',')
  return lines.map((line) => Object.fromEntries(line.split(',').map((value, i) => [keys[i], value])))
}
const nextDay = (day) => new Date(Date.parse(`${day}T00:00:00Z`) + 86_400_000).toISOString().slice(0, 10)
const availableAt = (day) => `${nextDay(day)}T06:00:00Z`

const snapshots = (await readdir(new URL('inventory/store_stock_daily/', ERP)))
  .map((name) => name.match(/^stock_eod_(\d{4}-\d{2}-\d{2})\.csv$/)?.[1])
  .filter((day) => day && availableAt(day) <= CUTOFF)
  .sort()
const day = snapshots.at(-1)
if (!day) throw new Error(`No stock snapshot available by ${CUTOFF}`)

const products = db.prepare(`
  SELECT style_code, name, category, subcategory, gender, synthetic_price_eur, local_image,
         reference_name, source_url
  FROM product_cards ORDER BY style_code`).all()
const variants = db.prepare('SELECT sku, style_code, color_code, color FROM variants ORDER BY sku').all()
const skuInfo = new Map((await csv(new URL('master_data/sku_colour.csv', ERP))).map((row) => [row.sku, row]))

const assorted = new Map()
for (const row of await csv(new URL('master_data/store_assortment.csv', ERP)))
  assorted.set(row.sku, [...(assorted.get(row.sku) ?? []), row.store_id])

// stock[sku][store] = { sizes: { size: on_hand }, in_transit }
const stock = {}
for (const row of await csv(new URL(`inventory/store_stock_daily/stock_eod_${day}.csv`, ERP))) {
  const entry = ((stock[row.sku] ??= {})[row.store_id] ??= { sizes: {}, in_transit: 0 })
  entry.sizes[row.size] = Number(row.on_hand)
  entry.in_transit += Number(row.in_transit)
}

const out = {
  available_at: availableAt(day),
  snapshot_date: day,
  products: products.map((product) => ({
    style_code: product.style_code,
    name: product.name,
    category: product.category,
    subcategory: product.subcategory,
    gender: product.gender,
    price_eur: product.synthetic_price_eur,
    image: `/api/catalog/${product.local_image}`,
    reference: { name: product.reference_name, url: product.source_url },
    colours: variants.filter((variant) => variant.style_code === product.style_code).map((variant) => ({
      sku: variant.sku,
      colour: skuInfo.get(variant.sku)?.color_name_it ?? variant.color,
      stores: assorted.get(variant.sku) ?? [],
      stock: stock[variant.sku] ?? {}
    }))
  }))
}

await writeFile(new URL('../mock-api/products.json', import.meta.url), `${JSON.stringify(out)}\n`)
console.log(`products.json: ${out.products.length} styles, stock of ${day}, available ${out.available_at}`)
