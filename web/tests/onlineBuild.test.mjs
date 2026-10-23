import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { buildOnline, CUTOFF, compareSizes, parseCsv, SOURCE_PATHS, timestamp, windows } from '../scripts/build-online-demo.mjs'

const catalog = (sku, launch_date = '') => ({ sku, style_name: sku, color_name_en: 'pink', category: 'Outerwear', launch_date })
const request = (product_id, created_at, extra = {}) => ({
  product_id, created_at, variant_sku: `${product_id}-M`, size: 'M', country: 'JP',
  status: 'PENDING', notified_at: '', converted_order: '', ...extra,
})
const build = (extra) => buildOnline({ requests: [], searches: [], inventory: [], catalog: [catalog('A-510')], ...extra })

test('CSV preserves quoted commas, escaped quotes, multiline fields, Unicode, empty cells and BOM', () => {
  assert.deepEqual(parseCsv('\uFEFFa,b,c\r\n"粉紅, pink","a""b","line1\r\nline2"\r\nx,,\r\n'), [
    { a: '粉紅, pink', b: 'a"b', c: 'line1\r\nline2' }, { a: 'x', b: '', c: '' },
  ])
  assert.deepEqual(parseCsv('a,b\n"",x'), [{ a: '', b: 'x' }])
  assert.deepEqual(parseCsv('a,b\n'), [])
  for (const text of ['a,a\nx,y', 'a,b\nx', 'a,b\n"x,y', 'a,b\n"x"bad,y', 'a,b\nx"z,y']) {
    assert.throws(() => parseCsv(text))
  }
})

test('rolling requests exclude lower boundary and future rows but include cutoff; pending rewinds future state', () => {
  const output = build({ requests: [
    request('A-510', '2026-09-24T20:00:00Z'),
    request('A-510', '2026-09-24T20:00:01Z', { status: 'CONVERTED', notified_at: '2026-10-23T00:00:00Z', converted_order: 'future-order' }),
    request('A-510', CUTOFF, { status: 'SENT', notified_at: CUTOFF }),
    request('A-510', '2026-10-21T10:00:00Z', { status: 'CONVERTED', notified_at: '2026-10-21T12:00:00Z', converted_order: 'undated-order' }),
    request('A-510', '2026-10-21T11:00:00Z', { status: 'UNSUBSCRIBED' }),
    request('A-510', '2026-10-22T20:00:01Z'),
  ] })
  assert.equal(output.topRequested[0].totalRequests, 4)
  assert.equal(output.topRequested[0].pending, 2)
  assert.equal(output.topRequested[0].converted, null)
  assert.equal(output.meta.futureNotificationsRewound, 1)
  assert.equal(output.meta.snapshotConversionsWithheld, 2)
})

test('rank top5 SKU colours independently, aggregate sizes and top3 countries with lexical ties', () => {
  const skus = ['G-510', 'F-510', 'E-510', 'D-510', 'C-510', 'B-510', 'A-510']
  const output = build({ catalog: skus.map((s) => catalog(s)), requests: [
    ...skus.map((s) => request(s, CUTOFF)),
    ...['XL', 'XS', 'S', 'M', 'L', 'XXL'].map((size, i) => request('G-510', CUTOFF, { size, variant_sku: `G-510-${size}`, country: ['US', 'GB', 'KR', 'FR', 'CN', 'DE'][i] })),
  ] })
  assert.deepEqual(output.topRequested.map((r) => r.sku), ['G-510', 'A-510', 'B-510', 'C-510', 'D-510'])
  assert.equal(output.topRequested[0].totalRequests, 7)
  assert.deepEqual(output.topRequested[0].bySize, [
    { size: 'XS', requests: 1 }, { size: 'S', requests: 1 }, { size: 'M', requests: 2 },
    { size: 'L', requests: 1 }, { size: 'XL', requests: 1 }, { size: 'XXL', requests: 1 },
  ])
  assert.deepEqual(output.topRequested[0].topCountries.map((r) => r.country), ['CN', 'DE', 'FR'])
  assert.deepEqual(['2', '00', '0', '1'].sort(compareSizes), ['00', '0', '1', '2'])
})

test('launch dates use a bounded historical 60-day interval; missing and future launches are not new', () => {
  const skus = [catalog('A-510', '2026-08-24'), catalog('B-510', '2026-08-23'), catalog('C-510', '2026-10-23'), catalog('D-510')]
  const output = build({ catalog: skus, requests: skus.map((r) => request(r.sku, CUTOFF)) })
  assert.deepEqual(output.topRequested.map((r) => r.isNew), [true, false, false, false])
  assert.equal(output.topRequested[3].launchDate, null)
})

test('inventory counts only exact SKU OUT_OF_STOCK events in the rolling window, including SQL UTC timestamps', () => {
  const event = (changed_at_utc, availability_event = 'OUT_OF_STOCK', variant_sku = 'A-510-M') => ({ changed_at_utc, availability_event, variant_sku })
  const output = build({ requests: [request('A-510', CUTOFF)], inventory: [
    event('2026-09-24 20:00:00'), event('2026-09-24 20:00:01'), event('2026-10-22 20:00:00'),
    event('2026-10-22 20:00:01'), event('2026-10-21 12:00:00', 'BACK_IN_STOCK'),
    event('2026-10-21 12:00:00', 'OUT_OF_STOCK', 'A-5100-M'),
  ] })
  assert.deepEqual(output.webStockouts, [{ sku: 'A-510', events: 2 }])
  assert.equal(timestamp('2026-10-22 20:00:00'), timestamp(CUTOFF))
})

test('searches include seven fully available UTC days, sum sites, filter zero_result and order countries/terms deterministically', () => {
  const search = (date_utc, country, search_term, searches, zero_result = 'Y') => ({ date_utc, country, search_term, searches: String(searches), zero_result })
  const output = build({ searches: [
    search('2026-10-14', 'JP', 'too early', 999), search('2026-10-15', 'JP', 'pink', 3),
    search('2026-10-21', 'JP', ' PINK ', 4), search('2026-10-22', 'JP', 'partial', 999),
    search('2026-10-23', 'JP', 'future', 999), search('2026-10-20', 'JP', 'results', 999, 'N'),
    ...['z', 'f', 'e', 'd', 'c', 'b', 'a'].map((s) => search('2026-10-20', 'GB', s, 2)),
  ] })
  assert.deepEqual(output.zeroResults, [
    { country: 'GB', terms: ['a', 'b', 'c', 'd', 'e'].map((term) => ({ term, searches: 2 })) },
    { country: 'JP', terms: [{ term: 'pink', searches: 7 }] },
  ])
  assert.equal(output.meta.searchWindowStart, '2026-10-15')
  assert.equal(output.meta.searchWindowEndExclusive, '2026-10-22')
  assert.equal(windows('2026-10-23T00:00:00Z').searchEnd, Date.parse('2026-10-23T00:00:00Z'))
})

test('bad input fails explicitly instead of silently producing misleading totals', () => {
  assert.throws(() => build({ requests: [request('unknown', CUTOFF)] }), /Unmatched/)
  assert.throws(() => timestamp('2026-10-22'), /Invalid timestamp/)
  assert.throws(() => build({ searches: [{ date_utc: '2026-10-20', zero_result: 'Y', searches: '-1' }] }), /Invalid search/)
  assert.throws(() => build({ searches: [{ date_utc: '2026-02-30' }] }), /Invalid date/)
})

test('pure builder does not mutate inputs; ordering is independent of source row order; private identity never escapes', () => {
  const requests = [request('A-510', CUTOFF, { email_sha1_10: 'private', size: 'S', variant_sku: 'A-510-S' }), request('A-510', CUTOFF)]
  const before = JSON.stringify(requests)
  const output = build({ requests })
  assert.deepEqual(output, build({ requests: [...requests].reverse() }))
  assert.equal(JSON.stringify(requests), before)
  assert.ok(!JSON.stringify(output).includes('email_sha1_10'))
  assert.ok(!JSON.stringify(output).includes('private'))
})

test('committed artifact reproduces source calculations and records exact file fingerprints', async () => {
  const inputs = await Promise.all(SOURCE_PATHS.map(async (path) => {
    const bytes = await readFile(new URL(`../../generated/sources/${path}`, import.meta.url))
    return { bytes, rows: parseCsv(bytes.toString('utf8')) }
  }))
  const [requests, searches, inventory, catalog] = inputs.map((i) => i.rows)
  const expected = buildOnline({ requests, searches, inventory, catalog })
  const actual = JSON.parse(await readFile(new URL('../src/demo/online.json', import.meta.url), 'utf8'))
  for (const field of ['topRequested', 'webStockouts', 'zeroResults']) assert.deepEqual(actual[field], expected[field])
  for (const [key, value] of Object.entries(expected.meta)) assert.deepEqual(actual.meta[key], value)
  assert.deepEqual(actual.meta.files.map((f) => f.sha256), inputs.map(({ bytes }) => createHash('sha256').update(bytes).digest('hex')))
  const end = timestamp(CUTOFF)
  assert.deepEqual(actual.meta.files.map((f) => f.rowsAfterCutoff), [
    requests.filter((r) => timestamp(r.created_at) > end).length,
    searches.filter((r) => Date.parse(`${r.date_utc}T00:00:00Z`) + 86_400_000 > end).length,
    inventory.filter((r) => timestamp(r.changed_at_utc) > end).length,
    catalog.filter((r) => r.launch_date && Date.parse(`${r.launch_date}T00:00:00Z`) > end).length,
  ])
  assert.equal(actual.meta.files.length, 4)
})
