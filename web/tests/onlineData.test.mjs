import assert from 'node:assert/strict'
import test from 'node:test'
import { readFileSync } from 'node:fs'
import {
  formatOnlineCutoff, formatOnlineConversions, onlineCatalogMatch, onlineCountries, onlineForSku, onlineLabel,
  onlineProductHref, onlineSearches, onlineSizeBars, onlineSkuFromHash, topOnlineProducts
} from '../src/sections/onlineData.ts'

const product = (sku, totalRequests) => ({ sku, totalRequests })

test('unknown historical conversions remain unknown rather than zero', () => {
  assert.equal(formatOnlineConversions(null), 'n.d.')
  assert.equal(formatOnlineConversions(0), '0')
})

test('committed snapshot reconciles size totals and withholds untimestamped conversions', () => {
  const data = JSON.parse(readFileSync(new URL('../src/demo/online.json', import.meta.url), 'utf8'))
  assert.equal(data.meta.cutoff, '2026-10-22T20:00:00Z')
  assert.ok(data.topRequested.length >= 5)
  for (const row of data.topRequested) {
    assert.equal(row.bySize.reduce((sum, size) => sum + size.requests, 0), row.totalRequests, row.sku)
    assert.ok(row.pending >= 0 && row.pending <= row.totalRequests, row.sku)
    assert.equal(row.converted, null, row.sku)
  }
})

test('cutoff labels use UTC across date boundaries and follow the data timestamp', () => {
  assert.equal(onlineLabel('2026-10-22T20:00:00Z'), 'E-commerce · dati sintetici · calcolato al 22/10 20:00 UTC')
  assert.equal(formatOnlineCutoff('2026-10-23T00:30:00+02:00'), '22/10 22:30 UTC')
  assert.equal(formatOnlineCutoff('invalid'), 'data non disponibile')
})

test('ranking selects five by demand with stable SKU ties without mutating data', () => {
  const products = [product('B-1', 7), product('A-2', 12), product('A-1', 12), product('C-1', 0), product('D-1', 3), product('E-1', 8)]
  const original = structuredClone(products)
  assert.deepEqual(topOnlineProducts(products).map((row) => row.sku), ['A-1', 'A-2', 'E-1', 'B-1', 'D-1'])
  assert.deepEqual(products, original)
  assert.deepEqual(topOnlineProducts(products, 0), [])
})

test('variants and stockouts never leak into another colour of the same style', () => {
  const data = {
    topRequested: [product('COAT-RED', 9), product('COAT-BLACK', 4)],
    webStockouts: [{ sku: 'COAT-RED', events: 3 }, { sku: 'COAT-BLACK', events: 8 }, { sku: 'COAT-RED', events: 2 }]
  }
  assert.deepEqual(onlineForSku(data, 'COAT-RED'), { product: data.topRequested[0], stockouts: 5 })
  assert.deepEqual(onlineForSku(data, 'COAT'), { product: null, stockouts: 0 })
  assert.deepEqual(onlineForSku(data, undefined), { product: null, stockouts: 0 })
})

test('catalog references require exact SKU-colour and preserve its image and name', () => {
  const item = { style_code: 'COAT', name: 'Catalog name', image: '/catalog.jpg', colours: [{ sku: 'COAT-RED', colour: 'Rosso' }, { sku: 'COAT-BLACK', colour: 'Nero' }] }
  const catalog = { products: [item] }
  assert.deepEqual(onlineCatalogMatch(catalog, 'COAT-BLACK'), { product: item, colour: item.colours[1] })
  for (const sku of ['COAT', 'COAT-BLACK-42', 'COAT-BLAC']) assert.equal(onlineCatalogMatch(catalog, sku), null)
})

test('product links round trip full SKUs and ignore malformed or unrelated routes', () => {
  for (const sku of ['COAT-RED', 'STYLE/COLOUR', 'SKU #1']) assert.equal(onlineSkuFromHash(onlineProductHref(sku)), sku)
  for (const hash of ['#/prodotti', '#/casi/COAT-RED', '#/prodotti/%E0%A4%A']) assert.equal(onlineSkuFromHash(hash), null)
})

test('size bars use wearing order and shared maximum, including zero demand', () => {
  const rows = [{ size: 'XL', requests: 2 }, { size: 'S', requests: 8 }, { size: 'M', requests: 0 }]
  assert.deepEqual(onlineSizeBars(rows), [{ size: 'S', requests: 8, percent: 100 }, { size: 'M', requests: 0, percent: 0 }, { size: 'XL', requests: 2, percent: 25 }])
  assert.equal(rows[0].size, 'XL')
  assert.deepEqual(onlineSizeBars([{ size: 'TU', requests: 0 }]), [{ size: 'TU', requests: 0, percent: 0 }])
  assert.deepEqual(onlineSizeBars([]), [])
})

test('country and search rankings preserve counts and multilingual terms', () => {
  const countries = [{ country: 'JP', requests: 3 }, { country: 'IT', requests: 7 }]
  assert.deepEqual(onlineCountries(countries).map((row) => row.country), ['IT', 'JP'])
  const groups = [{ country: 'JP', terms: [{ term: '赤いコート', searches: 2 }] }, { country: 'IT', terms: [{ term: 'sciarpa', searches: 1 }, { term: 'cappotto', searches: 9 }] }]
  const original = structuredClone(groups)
  const sorted = onlineSearches(groups)
  assert.deepEqual(sorted.map((row) => row.country), ['IT', 'JP'])
  assert.equal(sorted[0].terms[0].term, 'cappotto')
  assert.equal(sorted[1].terms[0].term, '赤いコート')
  assert.deepEqual(groups, original)
})
