// Curated display-only demo, independent of published runs. Run: npm run build:voice
import { createReadStream } from 'node:fs'
import { access, readFile, readdir, writeFile } from 'node:fs/promises'
import { createInterface } from 'node:readline'
import { DatabaseSync } from 'node:sqlite'
import { colleagueOverlap } from '../src/demo/voiceOverlap.ts'

const root = new URL('../../', import.meta.url)
const curated = {
  'mil01-melange-touch-belted-coat-fit': [
    { type: 'provato_non_comprato', sku: 'J10911A00213-90X', colour: 'grigio melange', reason: 'Rifiuto al tatto', quote: '4 clienti si sono avvicinati al piumino in lana grigio melange, ma una volta percepito al tatto si sono allontanati.' },
    { type: 'provato_non_comprato', sku: 'J20931A00622-23R', size: '2', colour: 'marrone cioccolato', reason: 'Troppo stretto in vita', quote: '3 clienti hanno provato il cappotto lungo in piumino con cintura, quello marrone cioccolato, in taglia 2, ma lo sentivano troppo stretto in vita.' },
    { type: 'operativo', sku: null, quote: 'la connessione oggi è saltata per 5 minuti' }
  ],
  'mil01-cashmere-scarf-vest-size': [
    { type: 'apprezzato', sku: 'I10913A00004-90X', colour: 'grigio melange', quote: "Oggi sei clienti hanno preso in mano la sciarpa in cashmere grigio melange, tre l'hanno apprezzata" },
    { type: 'richiesto_non_disponibile', sku: 'I10913A00004-034', colour: 'beige', quote: "una signora mi ha chiesto se c'è anche in beige, e in negozio non ce l'abbiamo." },
    { type: 'richiesto_non_disponibile', sku: 'J10911A00305-742', size: '3', colour: 'blu notte', quote: 'due clienti, che vestirebbero taglia 3, hanno guardato a lungo il gilet in piumino blu notte, ma in negozio avevamo solo la 2 e la 4, e se ne sono andati senza provare altro.' },
    { type: 'operativo', sku: null, quote: 'il lettore dei pagamenti si è bloccato un paio di volte nel primo pomeriggio, una cliente ha dovuto riprovare tre volte prima che passasse.' }
  ],
  'mil02-navy-long-down-lining': [
    { type: 'provato_non_comprato', sku: ['J20931A00087-742', 'J20931A00203-742'], colour: 'blu notte', reason: 'Fodera: «sembra di plastica»', quote: 'cinque clienti oggi hanno ispezionato il piumino lungo blu notte, però appena hanno visto la fodera interna hanno posato il capo, due addirittura facendo una faccia storta. Una signora mi ha detto che la fodera "sembra di plastica" e che per quel prezzo si aspettava qualcosa di più nobile.' },
    { type: 'richiesto_non_disponibile', sku: ['J20931A00087-742', 'J20931A00203-742'], colour: 'blu notte', reason: 'Richiesta senza cappuccio; disponibilità da verificare', caveat: 'Identità ambigua. J20931A00087 ha il cappuccio staccabile: la richiesta non certifica domanda insoddisfatta.', quote: "Un cliente invece ha chiesto se esiste lo stesso modello senza cappuccio, perché gli piaceva la linea ma lo trovava troppo sportivo per l'ufficio." },
    { type: 'apprezzato', sku: 'I10919B00042-999', colour: 'nero', quote: "il cardigan imbottito nero è piaciuto: due clienti l'hanno provato, uno l'ha preso." },
    { type: 'operativo', sku: null, quote: 'oggi poco passaggio, complice la pioggia dal pomeriggio.' },
    { type: 'operativo', sku: null, quote: 'Domani fascia pomeridiana con un collega in meno, ve lo segnalo.' }
  ]
}

const db = new DatabaseSync(new URL('data/catalog/products.sqlite', root).pathname, { readOnly: true })
const lookup = db.prepare(`SELECT p.name, p.local_image, p.reference_name, p.source_url FROM product_cards p
  JOIN variants v ON v.style_code = p.style_code WHERE v.sku = ?`)
const products = {}
async function product(sku) {
  if (products[sku]) return products[sku]
  const row = lookup.get(sku)
  if (!row) throw new Error(`Missing catalog SKU: ${sku}`)
  let image = null
  if (row.local_image) {
    await access(new URL(`data/catalog/${row.local_image}`, root))
    image = `/api/catalog/${row.local_image}`
  }
  return (products[sku] = { name: row.name, image, reference_name: row.reference_name, source_url: row.source_url })
}
const notes = []
for (const [id, facts] of Object.entries(curated)) {
  const dir = new URL(`data/fixtures/voice/${id}/`, root)
  const meta = JSON.parse(await readFile(new URL('note.json', dir), 'utf8'))
  const transcript = await readFile(new URL('transcript.txt', dir), 'utf8')
  for (const fact of facts) {
    if (!transcript.includes(fact.quote)) throw new Error(`Quote is not an exact transcript substring (${id}): ${fact.quote}`)
    const skus = fact.sku === null ? [] : Array.isArray(fact.sku) ? fact.sku : [fact.sku]
    fact.product = skus.length ? (await Promise.all(skus.map(product))).map(p => p.name).join(' / ') : null
  }
  notes.push({ note_id: meta.note_id, store_id: meta.store_id, sent_at: meta.sent_at, author: meta.author_ref.split('staff-')[1], duration_s: meta.duration_s, language: meta.language, transcript, facts })
}
db.close()

// Stream and stop after both exact keys are found; retain raw rows for provenance.
const stockFile = 'generated/sources/erp/inventory/store_stock_daily/stock_eod_2026-10-21.csv'
const targets = [
  { sku: 'J20931A00622-23R', size: '2', note_id: notes[0].note_id },
  { sku: 'J10911A00305-742', size: '3', note_id: notes[1].note_id }
]
const conflicts = []
const input = createReadStream(new URL(stockFile, root))
const lines = createInterface({ input, crlfDelay: Infinity })
try {
  for await (const row of lines) {
    const [snapshot_date, store_id, sku, size, on_hand, in_transit] = row.split(',')
    const target = targets.find(t => store_id === 'MIL01' && t.sku === sku && t.size === size)
    if (!target) continue
    if (conflicts.some(c => c.sku === sku)) throw new Error(`Duplicate stock row: ${sku}`)
    if (![on_hand, in_transit].every(v => /^\d+$/.test(v))) throw new Error(`Invalid stock row: ${row}`)
    const quote = notes.find(n => n.note_id === target.note_id).facts.find(f => f.sku === sku).quote
    conflicts.push({ ...target, store_id, snapshot_date, on_hand: Number(on_hand), in_transit: Number(in_transit), quote, provenance: { file: stockFile, row } })
    if (conflicts.length === targets.length) break
  }
} finally {
  lines.close()
  input.destroy()
}
if (conflicts.length !== targets.length) throw new Error(`Missing required stock rows in ${stockFile}`)

const stores = []
const storeLines = createInterface({ input: createReadStream(new URL('generated/sources/erp/master_data/stores.csv', root)), crlfDelay: Infinity })
for await (const line of storeLines) {
  const [store_id, name] = line.split(',')
  if (notes.some(n => n.store_id === store_id)) stores.push({ store_id, name })
}
if (stores.length !== 2) throw new Error('Missing demo stores in stores.csv')
// The empty evening email set is explicit; do not imply comparison with an existing closing email.
const closing_emails = {}
for (const store of stores) {
  const names = await readdir(new URL(`generated/sources/store_emails/${store.store_id}/`, root))
  closing_emails[store.store_id] = names.filter(name => name.startsWith('20261022_'))
  if (closing_emails[store.store_id].length) throw new Error(`Closing emails now exist for ${store.store_id}; review Solo nei vocali copy`)
}
const output = { stores, notes: notes.map(({ facts: _facts, ...note }) => note), products, facts: { curated: true, by_note: Object.fromEntries(notes.map(n => [n.note_id, n.facts])) }, conflicts, overlap: colleagueOverlap(notes), closing_emails }
await writeFile(new URL('web/src/demo/voiceStore.json', root), `${JSON.stringify(output, null, 2)}\n`)
console.log(`voiceStore.json: ${notes.length} notes, ${conflicts.length} stock conflicts, ${output.overlap.length} colleague overlaps; all quotes verified`)
