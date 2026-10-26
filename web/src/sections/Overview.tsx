import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { AlarmClock, ChevronRight } from 'lucide-react'
import { AnimatePresence, animate, motion, useMotionValue, useReducedMotion, useTransform } from 'motion/react'
import type { Case, RunView } from '../api/client'
import { Button, EmptyState, Select, StatusBadge, VisuallyHidden, stagger, transition } from '../ui'
import type { StatusTone } from '../ui/StatusBadge'
import { compareDeadlines, deadline } from './overviewLogic'
import { BudgetBars, SalesTrend, Sparkline } from './BusinessCharts'
import { countByDay, dailySeries, formatEuro, lastDay, nextDay, storePerformance, totals } from './businessData'
import type { KpiDay } from './businessData'
import { MarketView } from './MarketView'
import { OnlineDemand } from './OnlineDemand'
import { StoreMap } from './StoreMap'
import { useRunData } from './useRunData'
import { STORE_GEO } from './storeGeo'
import './overview.css'

type Priority = Case['priority']

const PRIORITIES: Priority[] = ['critical', 'high', 'medium', 'low']
const priorities: Record<Priority, string> = { critical: 'Critica', high: 'Alta', medium: 'Media', low: 'Bassa' }
const priorityTone: Record<Priority, StatusTone> = { critical: 'danger', high: 'warning', medium: 'info', low: 'neutral' }
const priorityOrder: Record<Priority, number> = { critical: 0, high: 1, medium: 2, low: 3 }
// Labels for the RFC §4.3 owner and case-type enums; unknown values fall back to the raw id.
const owners: Record<string, string> = {
  allocation: 'Allocazione',
  retail_ops: 'Retail operations',
  product_quality: 'Qualità prodotto',
  merchandising: 'Merchandising',
  marketing: 'Marketing'
}
const caseTypes: Record<string, string> = {
  unmet_demand: 'Domanda non servita',
  stock_discrepancy: 'Discrepanza di stock',
  product_feedback: 'Feedback prodotto',
  demand_shift: 'Variazione domanda',
  traffic_change: 'Variazione traffico',
  operational_issue: 'Problema operativo',
  customer_profile: 'Profilo cliente'
}

const label = (map: Record<string, string>, key: string) => map[key] ?? key.replaceAll('_', ' ')
const HOUR = 3600_000
const isActive = (item: Case) => item.status !== 'closed' && item.status !== 'decided'
const isVerify = (item: Case) => item.blocking_uncertainties.length > 0
// A case is ready to decide when no blocking uncertainty is open.
type Verification = 'all' | 'blocking' | 'ready'
const matchesVerification = (item: Case, filter: Verification) =>
  filter === 'all' || (filter === 'blocking' ? isVerify(item) : !isVerify(item))
const dateTime = (value: string) =>
  new Date(value).toLocaleString('it-IT', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
const HIST_HEIGHT = 140
const hoursFrom = (value: string, asOf: number) => (Date.parse(value) - asOf) / HOUR

// Deadline buckets for the histogram: hours after the cutoff. Overdue cases get their own bar.
const BUCKETS = [
  { key: 'overdue', name: 'Scadute', from: -Infinity, to: 0 },
  { key: 'h6', name: '0–6 h', from: 0, to: 6 },
  { key: 'h12', name: '6–12 h', from: 6, to: 12 },
  { key: 'h24', name: '12–24 h', from: 12, to: 24 },
  { key: 'h48', name: '24–48 h', from: 24, to: 48 },
  { key: 'h72', name: '48–72 h', from: 48, to: 72 },
  { key: 'later', name: 'Oltre 72 h', from: 72, to: Infinity }
]

function Countdown({ due, asOf }: { due: string | null | undefined; asOf: number }) {
  const left = deadline(due, asOf)
  return (
    <span className={`sd-ov-countdown is-${left.tone}`} title={due ? `Decisione entro ${dateTime(due)}` : undefined}>
      {left.tone !== 'none' && <AlarmClock aria-hidden="true" />}
      {left.text}
    </span>
  )
}

/** Counts from the previous value to the new one, so a filter change reads as a change. */
function AnimatedNumber({ value, format = (latest) => String(Math.round(latest)) }: { value: number; format?: (value: number) => string }) {
  const reduceMotion = useReducedMotion()
  const current = useMotionValue(0)
  const text = useTransform(current, format)
  useEffect(() => {
    if (reduceMotion) {
      current.set(value)
      return
    }
    // Cubic ease-out rather than ease.out: the steeper curve finishes the count before the eye sees it.
    const controls = animate(current, value, { duration: 1, ease: [0.33, 1, 0.68, 1] })
    return () => controls.stop()
  }, [current, value, reduceMotion])
  return (
    <>
      <motion.span aria-hidden="true">{text}</motion.span>
      <VisuallyHidden>{format(value)}</VisuallyHidden>
    </>
  )
}

// Page-load sequence for the KPIs: each card staggers by `stagger`.
const enter = (index: number, base = 0) => ({
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { ...transition.view, duration: 0.4, delay: base + index * stagger }
})
const grow = { type: 'spring', duration: 0.7, bounce: 0 } as const

/** Daily store KPIs for the run, as rows (empty until loaded or when unavailable). */
function useKpi(runId: string) {
  const state = useRunData<KpiDay[]>(runId, 'kpi')
  return { status: state.status, rows: state.data ?? [] }
}

function Panel({ id, title, meta, action, children }: { id: string; title: string; meta?: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="sd-ov-panel" aria-labelledby={id}>
      <header className="sd-ov-panel__head">
        <div>
          <h2 id={id}>{title}</h2>
          {meta && <p>{meta}</p>}
        </div>
        {action}
      </header>
      {children}
    </section>
  )
}

export function Overview({
  run,
  cases,
  onCaseSelect
}: {
  run: RunView
  cases: Case[]
  onCaseSelect: (item: Case) => void
}) {
  const [store, setStore] = useState('all')
  const [office, setOffice] = useState('all')
  const [priority, setPriority] = useState<'all' | Priority>('all')
  const [verification, setVerification] = useState<Verification>('all')
  const [view, setView] = useState<'market' | 'ops'>('ops')
  const [decisionsExpanded, setDecisionsExpanded] = useState(false)

  const asOf = Date.parse(run.spec.as_of)
  const active = cases.filter(isActive)
  const offices = [...new Set(active.map((item) => item.owner))].sort()

  // Every panel reads from the same filtered set, so the numbers always agree with the table.
  const scoped = active.filter(
    (item) =>
      (store === 'all' || item.store_id === store) &&
      (office === 'all' || item.owner === office) &&
      (priority === 'all' || item.priority === priority) &&
      matchesVerification(item, verification)
  )
  const queue = [...scoped].sort(
    (a, b) => priorityOrder[a.priority] - priorityOrder[b.priority] || compareDeadlines(a.decision_due_at, b.decision_due_at)
  )
  const dueSoon = scoped.filter((item) => item.decision_due_at && hoursFrom(item.decision_due_at, asOf) <= 48)
  const urgent = scoped.filter((item) => priorityOrder[item.priority] <= 1)
  const verify = scoped.filter(isVerify)
  const filtered = store !== 'all' || office !== 'all' || priority !== 'all' || verification !== 'all'

  const buckets = BUCKETS.map((bucket) => {
    const items = scoped.filter((item) => {
      if (!item.decision_due_at) return false
      const hours = hoursFrom(item.decision_due_at, asOf)
      return hours > bucket.from - (bucket.from === 0 ? 0.0001 : 0) && hours <= bucket.to
    })
    return { ...bucket, items }
  })
  const maxBucket = Math.max(1, ...buckets.map((bucket) => bucket.items.length))

  // The map and store list follow every filter except the store itself, so picking a store
  // never hides the others.
  const mapScope = active.filter(
    (item) =>
      (office === 'all' || item.owner === office) &&
      (priority === 'all' || item.priority === priority) &&
      matchesVerification(item, verification)
  )
  const stores = run.spec.stores
    .map((id) => {
      const own = mapScope.filter((item) => item.store_id === id)
      const counts = Object.fromEntries(PRIORITIES.map((key) => [key, own.filter((item) => item.priority === key).length])) as Record<Priority, number>
      const top = PRIORITIES.find((key) => counts[key] > 0) ?? null
      const next = own.map((item) => item.decision_due_at).filter((value): value is string => Boolean(value)).sort(compareDeadlines)[0]
      return { id, counts, top, next, total: own.length, verify: own.filter(isVerify).length }
    })
    .sort((a, b) => b.counts.critical - a.counts.critical || b.counts.high - a.counts.high || b.total - a.total || a.id.localeCompare(b.id))
  const current = stores.find((row) => row.id === store)
  const currentGeo = current ? STORE_GEO[current.id] : undefined

  // Business series: the store filter applies; office and priority describe cases, not tills.
  const kpi = useKpi(run.spec.run_id)
  const [range, setRange] = useState(30)
  const end = lastDay(kpi.rows)
  const salesScope = store === 'all' ? new Set(run.spec.stores) : new Set([store])
  const series = end ? dailySeries(kpi.rows, salesScope, range, end) : []
  const now = totals(series)
  const performance = end ? storePerformance(kpi.rows, run.spec.stores, range, end) : []
  const sparkOf = new Map(performance.map((row) => [row.id, row]))
  // Days between the last known sales day and the run cutoff: signals can already be there.
  const cutoffDay = run.spec.as_of.slice(0, 10)
  const pending: string[] = []
  if (end) for (let day = nextDay(end); day <= cutoffDay; day = nextDay(day)) pending.push(day)
  const signalCases = cases.filter((item) => store === 'all' || item.store_id === store)
  const signals = new Map(
    [...countByDay(signalCases, (item) => item.first_available_at, [...series.map((point) => point.date), ...pending])].map(([date, count]) => {
      const sameDay = signalCases.filter((item) => item.first_available_at.slice(0, 10) === date)
      return [date, { count, top: PRIORITIES.find((key) => sameDay.some((item) => item.priority === key)) ?? null }]
    })
  )

  const nothingLeft = queue.length === 0

  // The office row follows every filter except the office itself, so its counts agree with the
  // table and picking an office never hides the others.
  const officeScope = active.filter(
    (item) =>
      (store === 'all' || item.store_id === store) &&
      (priority === 'all' || item.priority === priority) &&
      matchesVerification(item, verification)
  )
  const resetFilters = () => {
    setStore('all')
    setOffice('all')
    setPriority('all')
    setVerification('all')
  }

  // Filters belong to the decision view: they sit on the tab row, right of the tabs, in one line.
  // An unset filter shows its field name; a set one shows its value and is highlighted.
  const filters = (
      <form className="sd-ov-filters" role="search" onSubmit={(event) => event.preventDefault()} aria-label="Filtra la panoramica">
        <Select
          size="sm"
          label="Negozio"
          hideLabel
          className={store !== 'all' ? 'is-set' : ''}
          value={store}
          onValueChange={setStore}
          options={[{ value: 'all', label: 'Negozio' }, ...run.spec.stores.map((id) => ({ value: id, label: id }))]}
        />
        <Select
          size="sm"
          label="Priorità"
          hideLabel
          className={priority !== 'all' ? 'is-set' : ''}
          value={priority}
          onValueChange={(value) => setPriority(value as 'all' | Priority)}
          options={[{ value: 'all', label: 'Priorità' }, ...PRIORITIES.map((key) => ({ value: key, label: priorities[key] }))]}
        />
        <Select
          size="sm"
          label="Verifica"
          hideLabel
          className={verification !== 'all' ? 'is-set' : ''}
          value={verification}
          onValueChange={(value) => setVerification(value as Verification)}
          options={[
            { value: 'all', label: 'Verifica' },
            { value: 'blocking', label: 'Con verifica bloccante' },
            { value: 'ready', label: 'Pronte da decidere' }
          ]}
        />
        {/* Always in the row, hidden when there is nothing to reset, so the row never shifts. */}
        <button
          type="button"
          className="sd-ov-reset"
          disabled={!filtered}
          aria-hidden={!filtered}
          onClick={resetFilters}
        >
          Azzera
        </button>
      </form>
  )


  return (
    <div className="sd-ov">
      {/* Two views of the same run: the decision desk for planners and offices, market trends for executives. */}
      {/* Tabs left, the active view's own controls right, on one row. */}
      <div className="sd-ov-viewbar">
        <div className="sd-ov-views" role="tablist" aria-label="Vista">
          {([['ops', 'Decisioni operative'], ['market', 'Mercato']] as const).map(([key, name]) => (
            <button key={key} type="button" role="tab" aria-selected={view === key} onClick={() => setView(key)}>
              {name}
              {view === key && <motion.span layoutId="sd-ov-view" className="sd-ov-views__indicator" transition={transition.spring} />}
            </button>
          ))}
        </div>
        <div className="sd-ov-viewbar__tools">
          {view === 'ops' ? filters : <p className="sd-ov-viewbar__scope">Negozi del run, confronto con l'anno scorso a parità di giorni</p>}
        </div>
      </div>
      {view === 'market' ? (
        <>
          <MarketView runId={run.spec.run_id} />
          <OnlineDemand runId={run.spec.run_id} />
        </>
      ) : (
      <>

      {/* Each office opens the page on its own cases; allocation is the planner's desk. */}
      <div className="sd-ov-offices">
        <span className="sd-ov-offices__label" id="ov-office">Ufficio</span>
        <div className="sd-ov-range" role="group" aria-labelledby="ov-office">
          {['all', ...offices].map((id) => (
            <button key={id} type="button" aria-pressed={office === id} onClick={() => setOffice(id)}>
              {id === 'all' ? 'Tutti' : label(owners, id)}
              <span className="sd-ov-offices__count">
                {id === 'all' ? officeScope.length : officeScope.filter((item) => item.owner === id).length}
              </span>
            </button>
          ))}
        </div>
      </div>

      <ul className="sd-ov-kpis" aria-label="Indicatori del filtro attuale">
        {[
          { name: 'Decisioni aperte', value: scoped.length, note: `di ${active.length} nel run`, tone: '' },
          { name: 'Entro 48 ore', value: dueSoon.length, note: 'dal cutoff del run', tone: '' },
          { name: 'Critiche o alte', value: urgent.length, note: 'da decidere per prime', tone: ' is-danger' },
          { name: 'Verifiche bloccanti', value: verify.length, note: 'senza verifica non si decide', tone: ' is-warning' }
        ].map((card, index) => (
          <motion.li key={card.name} className={`sd-ov-kpi${card.tone}`} {...enter(index)}>
            <span className="sd-ov-kpi__label">{card.name}</span>
            <strong className="sd-ov-kpi__value"><AnimatedNumber value={card.value} /></strong>
            <span className="sd-ov-kpi__note">{card.note}</span>
          </motion.li>
        ))}
      </ul>

      <Panel
        id="ov-queue"
        title="Decisioni"
        meta={`${queue.length} di ${active.length}${filtered ? ' · filtri attivi' : ''}. Ordinate per priorità, poi per scadenza.`}
        action={
          <Button size="sm" variant="secondary"
            aria-label={decisionsExpanded ? 'Nascondi decisioni' : 'Mostra decisioni'}
            aria-expanded={decisionsExpanded} aria-controls="ov-queue-content"
            onClick={() => setDecisionsExpanded((expanded) => !expanded)}>
            {decisionsExpanded ? 'Nascondi' : 'Mostra'}
          </Button>
        }
      >
        <div id="ov-queue-content" hidden={!decisionsExpanded}>
        {nothingLeft ? (
          <EmptyState
            title="Nessuna decisione con questi filtri"
            description="Il filtro non corrisponde a nessun caso aperto del run."
            action={filtered ? <Button variant="secondary" onClick={resetFilters}>Mostra tutte</Button> : undefined}
          />
        ) : (
          <div className="sd-ov-table-wrap">
            <table className="sd-ov-table">
              <thead>
                <tr>
                  <th scope="col">Scadenza</th>
                  <th scope="col">Priorità</th>
                  <th scope="col">Negozio</th>
                  <th scope="col">Prodotto</th>
                  <th scope="col">Motivo</th>
                  <th scope="col">Ufficio</th>
                  <th scope="col">Verifica</th>
                  <th scope="col"><span className="sd-visually-hidden">Apri</span></th>
                </tr>
              </thead>
              <tbody>
                <AnimatePresence initial={false}>
                {queue.map((item) => (
                  <motion.tr
                    key={`${item.id}-${item.version}`}
                    layout="position"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1, transition: transition.view }}
                    exit={{ opacity: 0, transition: transition.exit }}
                    transition={grow}
                  >
                    <td className="sd-ov-table__due"><Countdown due={item.decision_due_at} asOf={asOf} /></td>
                    <td><StatusBadge label={priorities[item.priority]} tone={priorityTone[item.priority]} /></td>
                    <th scope="row" className="sd-ov-table__store">{item.store_id ?? '—'}</th>
                    <td className="sd-ov-table__scope">{item.scope_id ?? 'Da identificare'}</td>
                    <td className="sd-ov-table__reason">
                      <span>{label(caseTypes, item.case_type)}</span>
                      <span>{item.priority_reason}</span>
                    </td>
                    <td>{label(owners, item.owner)}</td>
                    <td>{isVerify(item) ? <span className="sd-ov-verify">Da verificare</span> : <span className="sd-ov-muted">Pronta</span>}</td>
                    <td className="sd-ov-table__go">
                      <button type="button" onClick={() => onCaseSelect(item)} aria-label={`Apri il caso ${item.store_id ?? ''} ${item.scope_id ?? ''}`}>
                        Apri <ChevronRight aria-hidden="true" />
                      </button>
                    </td>
                  </motion.tr>
                ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        )}
        </div>
      </Panel>

      <Panel id="ov-when" title="Quando scadono" meta="Decisioni per finestra di scadenza, impilate per priorità.">
          {scoped.some((item) => item.decision_due_at) ? (
            <div className="sd-ov-hist" role="img" aria-label={buckets.map((bucket) => `${bucket.name}: ${bucket.items.length}`).join(', ')}>
              {buckets.map((bucket, index) => (
                <div className="sd-ov-hist__col" key={bucket.key}>
                  {/* Height carries the count: bars grow from the baseline on load and move to
                      the new count when the filters change. */}
                  <motion.div
                    className="sd-ov-hist__stack"
                    initial={{ height: 0 }}
                    animate={{ height: (bucket.items.length / maxBucket) * HIST_HEIGHT }}
                    transition={{ ...grow, delay: 0.25 + index * stagger }}
                  >
                    {PRIORITIES.map((key) => {
                      const count = bucket.items.filter((item) => item.priority === key).length
                      return count ? <span key={key} className={`is-${key}`} style={{ flexGrow: count }} title={`${priorities[key]}: ${count}`} /> : null
                    })}
                  </motion.div>
                  <span className="sd-ov-hist__count">{bucket.items.length ? <AnimatedNumber value={bucket.items.length} /> : '–'}</span>
                  <span className="sd-ov-hist__name">{bucket.name}</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Nessuna scadenza in questo filtro" description="Cambia i filtri per vedere le decisioni con una data." />
          )}
          <ul className="sd-ov-legend" aria-hidden="true">
            {PRIORITIES.map((key) => (
              <li key={key}><span className={`sd-ov-swatch is-${key}`} />{priorities[key]}</li>
            ))}
          </ul>
      </Panel>

      <Panel id="ov-where" title="Dove" meta="Dimensione per casi aperti, colore per la priorità più alta. Seleziona un negozio per filtrare la pagina.">
        <div className="sd-ov-where">
          <StoreMap stores={stores} selected={store} onSelect={setStore} />
          <aside className="sd-ov-where__aside" aria-live="polite">
            <AnimatePresence mode="wait" initial={false}>
            {current ? (
              <motion.div
                key={current.id}
                className="sd-ov-store"
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0, transition: transition.view }}
                exit={{ opacity: 0, x: -8, transition: transition.exit }}
              >
                <div className="sd-ov-store__head">
                  <div>
                    <h3>{current.id}</h3>
                    {currentGeo && <p>{currentGeo.name} · {currentGeo.city}, {currentGeo.country}</p>}
                  </div>
                  <button type="button" className="sd-ov-reset" onClick={() => setStore('all')}>Tutti i negozi</button>
                </div>
                <dl className="sd-ov-store__facts">
                  <div><dt>Casi aperti</dt><dd>{current.total}</dd></div>
                  <div><dt>Critici o alti</dt><dd>{current.counts.critical + current.counts.high}</dd></div>
                  <div><dt>Prossima scadenza</dt><dd>{current.next ? <Countdown due={current.next} asOf={asOf} /> : '–'}</dd></div>
                </dl>
                {queue.length ? (
                  <ol className="sd-ov-store__list">
                    {queue.slice(0, 4).map((item) => (
                      <li key={`${item.id}-${item.version}`}>
                        <span className={`sd-ov-swatch is-${item.priority}`} aria-hidden="true" />
                        <span className="sd-ov-store__case">
                          <strong>{item.scope_id ?? 'Prodotto da identificare'}</strong>
                          <span>{item.priority_reason}</span>
                        </span>
                        <Countdown due={item.decision_due_at} asOf={asOf} />
                        <button type="button" className="sd-ov-store__open" onClick={() => onCaseSelect(item)}>Apri</button>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="sd-ov-muted">Nessun caso aperto con questi filtri.</p>
                )}
              </motion.div>
            ) : (
              <motion.ul
                key="stores"
                className="sd-ov-stores"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0, transition: transition.view }}
                exit={{ opacity: 0, x: 12, transition: transition.exit }}
              >
                {stores.map((row, index) => (
                  <motion.li key={row.id} layout="position" transition={grow}>
                    <button type="button" aria-pressed={store === row.id} onClick={() => setStore(row.id)}>
                      <span className="sd-ov-stores__name">{row.id}</span>
                      <motion.span
                        className="sd-ov-stores__counts"
                        style={{ originX: 0 }}
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ ...grow, delay: 0.35 + index * stagger }}
                        aria-label={`${priorities.critical} ${row.counts.critical}, ${priorities.high} ${row.counts.high}, ${priorities.medium} ${row.counts.medium}, ${priorities.low} ${row.counts.low}`}
                      >
                        {PRIORITIES.map((key) => (
                          <span key={key} className={`sd-ov-stores__seg is-${key}`} style={{ flexGrow: row.counts[key] }} />
                        ))}
                      </motion.span>
                      {sparkOf.get(row.id) ? (
                        <Sparkline
                          values={sparkOf.get(row.id)!.daily}
                          tone={sparkOf.get(row.id)!.vsBudget === null ? 'flat' : sparkOf.get(row.id)!.vsBudget! >= 0 ? 'up' : 'down'}
                        />
                      ) : (
                        <span />
                      )}
                      <strong className="sd-ov-stores__total"><AnimatedNumber value={row.total} /></strong>
                      <span className="sd-ov-stores__verify">{row.verify ? `${row.verify} da verificare` : ''}</span>
                    </button>
                  </motion.li>
                ))}
              </motion.ul>
            )}
            </AnimatePresence>
          </aside>
        </div>
      </Panel>

      <Panel
        id="ov-sales"
        title="Vendite e budget"
        meta={
          kpi.status === 'ready' && end
            ? `Contesto, non decisione: dati certificati, arrivano il giorno dopo. ${store === 'all' ? `${run.spec.stores.length} negozi` : store}, euro al cambio di budget, ultimo giorno ${end.split('-').reverse().join('/')}. I punti sotto l'asse sono i giorni in cui sono arrivati i segnali dei negozi.`
            : 'Contesto: serie giornaliere di vendita certificate dei negozi.'
        }
        action={
          <div className="sd-ov-range" role="group" aria-label="Periodo">
            {[30, 90].map((days) => (
              <button key={days} type="button" aria-pressed={range === days} onClick={() => setRange(days)}>
                {days} giorni
              </button>
            ))}
          </div>
        }
      >
        {kpi.status === 'ready' && end ? (
          <div className="sd-ov-sales">
            <div className="sd-ov-sales__main">
              <dl className="sd-ov-sales__stats">
                <div><dt>Scontrini</dt><dd>{now.receipts.toLocaleString('it-IT')}</dd></div>
                <div><dt>Visitatori</dt><dd>{now.visitors?.toLocaleString('it-IT') ?? '–'}</dd></div>
                <div><dt>Conversione</dt><dd>{now.conversion === null ? '–' : `${(now.conversion * 100).toLocaleString('it-IT', { maximumFractionDigits: 1 })}%`}</dd></div>
                <div><dt>Scontrino medio</dt><dd>{now.receipts ? formatEuro(now.sales / now.receipts) : '–'}</dd></div>
              </dl>
              <SalesTrend points={series} pending={pending} signals={signals} replayKey={`${store}-${range}`} />
              <ul className="sd-ov-legend" aria-hidden="true">
                <li><span className="sd-ov-line is-sales" />Vendite</li>
                <li><span className="sd-ov-line is-budget" />Budget</li>
                <li><span className="sd-ov-swatch is-critical" />Segnale critico</li>
                <li><span className="sd-ov-swatch is-high" />Segnale alto</li>
              </ul>
            </div>
            <div className="sd-ov-sales__side">
              <h3>Scostamento dal budget</h3>
              <p>Ultimi {range} giorni per negozio. Seleziona per filtrare.</p>
              <BudgetBars stores={performance} selected={store} onSelect={setStore} />
            </div>
          </div>
        ) : (
          <EmptyState
            title={kpi.status === 'loading' ? 'Carico le vendite…' : 'Vendite non disponibili'}
            description={
              kpi.status === 'unavailable'
                ? 'Il backend non espone ancora le serie KPI dei negozi. In sviluppo le serve il mock (npm run dev:mock).'
                : kpi.status === 'error'
                  ? 'Richiesta delle vendite non riuscita. Ricarica la pagina per riprovare.'
                  : undefined
            }
          />
        )}
      </Panel>
      </>
      )}
    </div>
  )
}
