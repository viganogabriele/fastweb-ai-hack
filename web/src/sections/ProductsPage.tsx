import { createElement, useEffect, useRef, useState } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  AlarmClock, ArrowRight, CircleAlert, Clock, MessageSquareWarning, PackageCheck, PackageX, Search, ShieldCheck,
  Store, TrendingDown, TrendingUp, Truck, X
} from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import type { Case } from '../api/client'
import type { useRuns } from '../api/useRuns'
import { Button, EmptyState, ErrorState, LoadingState, StatusBadge, stagger, transition } from '../ui'
import type { StatusTone } from '../ui/StatusBadge'
import { deadline } from './overviewLogic'
import { caseTypeLabel } from './productView'
import { productCards, productStock, storeRows } from './productsData'
import type { Attention, CatalogProduct, ProductCard, ProductCatalog, StoreRow } from './productsData'
import { STORE_GEO } from './storeGeo'
import { useRunData } from './useRunData'
import './sections.css'
import './products.css'

const priorities: Record<Case['priority'], { label: string; tone: StatusTone }> = {
  critical: { label: 'Critica', tone: 'danger' },
  high: { label: 'Alta', tone: 'warning' },
  medium: { label: 'Media', tone: 'info' },
  low: { label: 'Bassa', tone: 'neutral' }
}
const tiers: { key: Attention; title: string; hint: string; icon: LucideIcon }[] = [
  { key: 'now', title: 'Attenzione immediata', hint: 'Casi critici o ad alta priorità aperti', icon: CircleAlert },
  { key: 'later', title: 'Attenzione differita', hint: 'Casi aperti da seguire nei prossimi giorni', icon: Clock },
  { key: 'none', title: 'Nessuna segnalazione', hint: 'Nessun caso aperto nel run', icon: ShieldCheck }
]
// One glyph per reported problem, so the card is read at a glance.
const caseIcons: Record<string, LucideIcon> = {
  unmet_demand: TrendingUp,
  demand_up: TrendingUp,
  demand_shift: TrendingUp,
  demand_down: TrendingDown,
  stockout: PackageX,
  low_stock: PackageX,
  stock_discrepancy: PackageX
}
const CaseGlyph = ({ type }: { type: string }) => createElement(caseIcons[type] ?? MessageSquareWarning, { 'aria-hidden': true })
// Swatches for the catalog's colour names; an unknown colour shows a neutral dot with its name.
const swatches: Record<string, string> = {
  nero: '#151515', bianco: '#f7f7f4', 'bianco latte': '#f1ece0', beige: '#d8c3a5', azzurro: '#8fb8de',
  rosso: '#b3202c', 'grigio melange': '#a3a3a3', 'rosa cipria': '#e8c4c0', 'blu notte': '#1d2742',
  'marrone cioccolato': '#4a2c21', 'verde oliva': '#6b6b3a'
}
const categories: Record<string, string> = {
  Outerwear: 'Capispalla', Accessories: 'Accessori', Bottoms: 'Pantaloni e gonne', Footwear: 'Calzature',
  Jersey: 'Jersey', Knitwear: 'Maglieria'
}
const storeName = (id: string) => STORE_GEO[id]?.name ?? id
const euro = (value: number) => value.toLocaleString('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
const day = (value: string) => new Date(value).toLocaleString('it-IT', { day: 'numeric', month: 'long' })

export function ProductsPage({ runs, onCaseSelect }: {
  runs: ReturnType<typeof useRuns>
  onCaseSelect: (item: Case) => void
}) {
  const run = runs.selected
  if (runs.loading) return <LoadingState label="Caricamento run" />
  if (runs.error) return <ErrorState title="Impossibile caricare i run" description={runs.error} onRetry={runs.retry} />
  if (!run) return <EmptyState title="Nessun run disponibile" description="I prodotti compariranno dopo la pubblicazione di un’elaborazione." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  if (!run.published) return <EmptyState title="Run non pubblicato" description="La vista prodotti sarà disponibile quando l’elaborazione sarà pubblicata." action={<Button onClick={runs.retry}>Aggiorna</Button>} />
  return <Gallery key={run.spec.run_id} runId={run.spec.run_id} stores={run.spec.stores} asOf={Date.parse(run.spec.as_of)} onCaseSelect={onCaseSelect} />
}

function Gallery({ runId, stores, asOf, onCaseSelect }: {
  runId: string
  stores: readonly string[]
  asOf: number
  onCaseSelect: (item: Case) => void
}) {
  const catalog = useRunData<ProductCatalog>(runId, 'products')
  const cases = useRunData<Case[]>(runId, 'cases')
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('all')
  const [open, setOpen] = useState<string | null>(null)

  if (catalog.status === 'loading' || cases.status === 'loading') return <LoadingState label="Caricamento prodotti" />
  if (catalog.status === 'unavailable')
    return <EmptyState title="Catalogo non disponibile" description="Il backend non espone ancora catalogo e stock per prodotto. In sviluppo li serve il mock (npm run dev:mock)." />
  if (!catalog.data || !cases.data)
    return <ErrorState title="Impossibile caricare i prodotti" description="Ricarica la pagina per riprovare." />

  const { cards, unresolved } = productCards(catalog.data, cases.data, runId)
  const text = query.trim().toLocaleLowerCase('it-IT')
  const visible = cards.filter((card) =>
    (category === 'all' || card.product.category === category) &&
    (!text || [card.product.name, card.product.subcategory, categories[card.product.category], ...card.product.colours.map((c) => c.colour)]
      .join(' ').toLocaleLowerCase('it-IT').includes(text)))
  const current = cards.find((card) => card.product.style_code === open)
  const categoryList = [...new Set(cards.map((card) => card.product.category))].sort()

  return (
    <div className="sd-shop">
      <div className="sd-shop__bar">
        <label className="sd-shop__search">
          <Search aria-hidden="true" />
          <span className="sd-visually-hidden">Cerca un prodotto</span>
          <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Cerca per nome, tipo o colore" />
        </label>
        <div className="sd-shop__chips" role="group" aria-label="Categoria">
          {['all', ...categoryList].map((key) => (
            <button key={key} type="button" aria-pressed={category === key} onClick={() => setCategory(key)}>
              {key === 'all' ? 'Tutto' : categories[key] ?? key}
            </button>
          ))}
        </div>
      </div>

      {tiers.map((tier) => {
        const items = visible.filter((card) => card.attention === tier.key)
        if (!items.length) return null
        const Icon = tier.icon
        return (
          <section key={tier.key} className={`sd-shop__tier is-${tier.key}`} aria-labelledby={`tier-${tier.key}`}>
            <header className="sd-shop__tier-head">
              <span className="sd-shop__tier-icon"><Icon aria-hidden="true" /></span>
              <h2 id={`tier-${tier.key}`}>{tier.title}</h2>
              <span className="sd-shop__tier-count sd-num">{items.length}</span>
              <p>{tier.hint}</p>
            </header>
            <ul className="sd-shop__grid">
              {items.map((card, index) => (
                <motion.li key={card.product.style_code}
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ ...transition.view, duration: 0.35, delay: Math.min(index, 10) * stagger }}>
                  <ProductTile card={card} stores={stores} onOpen={() => setOpen(card.product.style_code)} />
                </motion.li>
              ))}
            </ul>
          </section>
        )
      })}
      {!visible.length && <EmptyState title="Nessun prodotto" description="Nessun prodotto corrisponde alla ricerca." />}

      {unresolved.length > 0 && (
        <section className="sd-shop__unresolved" aria-labelledby="tier-unresolved">
          <h2 id="tier-unresolved">Segnalazioni senza prodotto identificato</h2>
          <p>Il testo non basta a riconoscere il prodotto: il caso resta da verificare, senza collegamenti indovinati.</p>
          <ul>
            {unresolved.map((item) => (
              <li key={`${item.id}-${item.version}`}>
                <StatusBadge {...priorities[item.priority]} />
                <span>{item.store_id ? storeName(item.store_id) : 'Rete'}</span>
                <span className="sd-shop__unresolved-reason">{item.priority_reason}</span>
                <button type="button" onClick={() => onCaseSelect(item)}>Apri il caso <ArrowRight aria-hidden="true" /></button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="sd-shop__note">
        Foto di riferimento dal catalogo pubblico Valentino, abbinate per categoria: possono differire dal capo simulato.
        Stock ERP a fine giornata del {day(catalog.data.snapshot_date)}.
      </p>

      <AnimatePresence>
        {current && <ProductSheet key={current.product.style_code} card={current} stores={stores} asOf={asOf}
          snapshot={catalog.data.snapshot_date} onClose={() => setOpen(null)} onCaseSelect={onCaseSelect} />}
      </AnimatePresence>
    </div>
  )
}

function Swatches({ product, selected, onSelect }: { product: CatalogProduct; selected?: string; onSelect?: (sku: string) => void }) {
  return (
    <span className="sd-shop__swatches">
      {product.colours.map((colour) => {
        const dot = <span className="sd-shop__swatch" style={{ background: swatches[colour.colour] ?? 'var(--sd-color-text-muted)' }} aria-hidden="true" />
        return onSelect
          ? <button key={colour.sku} type="button" aria-pressed={selected === colour.sku} onClick={() => onSelect(colour.sku)}>{dot}{colour.colour}</button>
          : <span key={colour.sku} title={colour.colour}>{dot}<span className="sd-visually-hidden">{colour.colour}</span></span>
      })}
    </span>
  )
}

function ProductTile({ card, stores, onOpen }: { card: ProductCard; stores: readonly string[]; onOpen: () => void }) {
  const { product } = card
  const stock = productStock(product, stores)
  const top = card.cases[0]
  return (
    <button type="button" className={`sd-shop__tile is-${card.attention}`} onClick={onOpen}
      aria-label={`${product.name}, ${product.subcategory}${top ? `: ${caseTypeLabel(top.case_type)}` : ''}`}>
      <motion.span className="sd-shop__photo" layoutId={`photo-${product.style_code}`} transition={transition.drawer}>
        <img src={product.image} alt="" loading="lazy" />
      </motion.span>
      {card.attention !== 'none' && (
        <span className="sd-shop__flag">
          {card.attention === 'now' ? <CircleAlert aria-hidden="true" /> : <Clock aria-hidden="true" />}
          {card.cases.length > 1 ? `${card.cases.length} casi` : card.attention === 'now' ? 'Subito' : 'Da seguire'}
        </span>
      )}
      {stock.storesOut > 0 && (
        <span className="sd-shop__out" title={`Esaurito in ${stock.storesOut} negozi del run`}>
          <PackageX aria-hidden="true" />Esaurito in <span className="sd-num">{stock.storesOut}</span>
        </span>
      )}
      <span className="sd-shop__caption">
        <motion.strong layoutId={`name-${product.style_code}`} transition={transition.drawer}>{product.name}</motion.strong>
        <span className="sd-shop__sub">{product.subcategory}</span>
        <Swatches product={product} />
        {top && (
          <span className="sd-shop__issue">
            <CaseGlyph type={top.case_type} />
            <span>{caseTypeLabel(top.case_type)}</span>
            {top.store_id && <span className="sd-shop__issue-store">{top.store_id}</span>}
          </span>
        )}
      </span>
    </button>
  )
}

function ProductSheet({ card, stores, asOf, snapshot, onClose, onCaseSelect }: {
  card: ProductCard
  stores: readonly string[]
  asOf: number
  snapshot: string
  onClose: () => void
  onCaseSelect: (item: Case) => void
}) {
  const { product } = card
  const panel = useRef<HTMLDivElement>(null)
  // Open on the colour the stores talked about, if any.
  const [sku, setSku] = useState(() => product.colours.find((colour) => card.skus.has(colour.sku))?.sku ?? product.colours[0]?.sku)
  const colour = product.colours.find((entry) => entry.sku === sku) ?? product.colours[0]
  const rows = colour ? storeRows(colour, stores) : []
  const groups: { key: StoreRow['availability']; title: string; icon: LucideIcon }[] = [
    { key: 'in', title: 'Lo hanno', icon: PackageCheck },
    { key: 'out', title: 'Esaurito', icon: PackageX },
    { key: 'none', title: 'Non in assortimento', icon: Store }
  ]

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    panel.current?.focus()
    const close = (event: KeyboardEvent) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', close)
    const overflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', close)
      document.body.style.overflow = overflow
      previous?.focus()
    }
  }, [onClose])

  return (
    <div className="sd-sheet">
      <motion.div className="sd-sheet__backdrop" onClick={onClose}
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={transition.view} />
      <motion.div ref={panel} className="sd-sheet__panel" role="dialog" aria-modal="true" aria-labelledby="sheet-title" tabIndex={-1}
        initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={transition.drawer}>
        <button type="button" className="sd-sheet__close" onClick={onClose} aria-label="Chiudi"><X aria-hidden="true" /></button>
        <div className="sd-sheet__hero">
          <motion.div className="sd-sheet__photo" layoutId={`photo-${product.style_code}`} transition={transition.drawer}>
            <img src={product.image} alt={`Foto di riferimento: ${product.reference.name}`} />
          </motion.div>
          <div className="sd-sheet__intro">
            <span className="sd-sheet__eyebrow">{categories[product.category] ?? product.category} · {product.subcategory}</span>
            <motion.h2 id="sheet-title" layoutId={`name-${product.style_code}`} transition={transition.drawer}>{product.name}</motion.h2>
            <span className="sd-sheet__price">{euro(product.price_eur)} <span>{product.style_code}</span></span>
            <Swatches product={product} selected={colour?.sku} onSelect={setSku} />
            <a className="sd-sheet__ref" href={product.reference.url} target="_blank" rel="noreferrer">
              Foto: {product.reference.name}, valentino.com
            </a>
          </div>
        </div>

        <motion.div className="sd-sheet__body" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ ...transition.view, duration: 0.35, delay: 0.15 }}>
          <section aria-labelledby="sheet-issues">
            <h3 id="sheet-issues">La segnalazione</h3>
            {card.cases.length ? (
              <ul className="sd-sheet__cases">
                {card.cases.map((item) => {
                  const due = deadline(item.decision_due_at, asOf)
                  return (
                    <li key={`${item.id}-${item.version}`} className={`is-${item.priority}`}>
                      <span className="sd-sheet__case-icon"><CaseGlyph type={item.case_type} /></span>
                      <div>
                        <div className="sd-sheet__case-head">
                          <strong>{caseTypeLabel(item.case_type)}</strong>
                          <StatusBadge {...priorities[item.priority]} />
                        </div>
                        <p>{item.priority_reason}</p>
                        <div className="sd-sheet__case-meta">
                          {item.store_id && <span><Store aria-hidden="true" />{storeName(item.store_id)}</span>}
                          {due.tone !== 'none' && <span className={`is-${due.tone}`}><AlarmClock aria-hidden="true" />{due.tone === 'past' ? due.text : `Decidere entro ${due.text}`}</span>}
                          {item.scope_level !== 'style' && item.scope_id && <span>{item.scope_id}</span>}
                        </div>
                      </div>
                      <button type="button" onClick={() => onCaseSelect(item)}>Apri il caso <ArrowRight aria-hidden="true" /></button>
                    </li>
                  )
                })}
              </ul>
            ) : (
              <p className="sd-sheet__calm"><ShieldCheck aria-hidden="true" />Nessun caso aperto su questo prodotto nel run.</p>
            )}
          </section>

          <section aria-labelledby="sheet-stock">
            <h3 id="sheet-stock">Stock nei negozi · {colour?.colour}</h3>
            <dl className="sd-sheet__totals">
              <div><dt>Pezzi</dt><dd className="sd-num">{rows.reduce((sum, row) => sum + row.units, 0)}</dd></div>
              <div><dt>Negozi con stock</dt><dd className="sd-num">{rows.filter((row) => row.availability === 'in').length}</dd></div>
              <div className={rows.some((row) => row.availability === 'out') ? 'is-out' : ''}><dt>Esaurito in</dt><dd className="sd-num">{rows.filter((row) => row.availability === 'out').length}</dd></div>
              <div><dt>In arrivo</dt><dd className="sd-num">{rows.reduce((sum, row) => sum + row.inTransit, 0)}</dd></div>
            </dl>
            {groups.map((group) => {
              const members = rows.filter((row) => row.availability === group.key)
              if (!members.length) return null
              const Icon = group.icon
              return (
                <div key={group.key} className={`sd-sheet__stores is-${group.key}`}>
                  <h4><Icon aria-hidden="true" />{group.title}<span className="sd-num">{members.length}</span></h4>
                  {group.key === 'none' ? (
                    <p className="sd-sheet__muted">{members.map((row) => storeName(row.store)).join(' · ')}</p>
                  ) : (
                    <ul>
                      {members.map((row) => (
                        <li key={row.store}>
                          <span className="sd-sheet__store">
                            <strong>{storeName(row.store)}</strong>
                            <span>{row.store}{STORE_GEO[row.store] ? ` · ${STORE_GEO[row.store].country}` : ''}</span>
                          </span>
                          <span className="sd-sheet__sizes" aria-label="Pezzi per taglia">
                            {row.sizes.map(([size, count]) => (
                              <span key={size} className={count ? '' : 'is-zero'} title={`Taglia ${size}: ${count}`}>
                                <span>{size}</span><strong className="sd-num">{count}</strong>
                              </span>
                            ))}
                          </span>
                          <span className="sd-sheet__units sd-num">
                            {row.units}
                            {row.inTransit > 0 && <span title="In arrivo"><Truck aria-hidden="true" />{row.inTransit}</span>}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )
            })}
            <p className="sd-sheet__muted">
              Stock ERP a fine giornata del {day(snapshot)}. Le segnalazioni dei negozi sopra sono testo non verificato:
              se non coincidono con lo stock, verifica prima di spostare merce.
            </p>
          </section>
        </motion.div>
      </motion.div>
    </div>
  )
}
