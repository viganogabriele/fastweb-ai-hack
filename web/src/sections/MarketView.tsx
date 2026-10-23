import { useState } from 'react'
import type { ReactNode } from 'react'
import { motion } from 'motion/react'
import { EmptyState, stagger, transition } from '../ui'
import { formatChange, formatEuro, formatEuroCompact } from './businessData'
import { useElementWidth } from './useElementWidth'
import { useRunData } from './useRunData'

type Region = 'EMEA' | 'AMERICAS' | 'APAC'
interface Market {
  last_day: string
  monthly: { month: string; partial_until: number | null; regions: Record<Region, { sales: number; ly: number; budget: number }> }[]
  regions: { region: Region; sales: number; before: number; ly: number }[]
  categories: { category: string; sales: number; before: number; ly: number; units: number }[]
  social: { weeks: { week: string; pos: number; neu: number; neg: number }[]; hashtags: { tag: string; now: number; before: number }[]; posts: number }
}

const REGIONS: Region[] = ['EMEA', 'APAC', 'AMERICAS']
const regionNames: Record<Region, string> = { EMEA: 'Europa e Medio Oriente', AMERICAS: 'Americhe', APAC: 'Asia-Pacifico' }
const categoryNames: Record<string, string> = {
  Outerwear: 'Capispalla',
  Knitwear: 'Maglieria',
  Jersey: 'Jersey',
  Accessories: 'Accessori',
  Footwear: 'Calzature',
  Bottoms: 'Pantaloni'
}
const yoy = (now: number, ly: number) => (ly > 0 ? now / ly - 1 : null)
const monthName = (month: string) => new Date(`${month}-15T12:00:00Z`).toLocaleDateString('it-IT', { month: 'short', timeZone: 'UTC' })
const dayName = (date: string) => new Date(`${date}T12:00:00Z`).toLocaleDateString('it-IT', { day: 'numeric', month: 'long', timeZone: 'UTC' })
const tone = (value: number | null) => (value === null ? '' : value >= 0 ? ' is-up' : ' is-down')
const rise = { type: 'spring', duration: 0.8, bounce: 0 } as const

function Section({ id, title, meta, children, className = '' }: { id: string; title: string; meta: string; children: ReactNode; className?: string }) {
  return (
    <motion.section
      className={`sd-ov-panel sd-mk-section ${className}`}
      aria-labelledby={id}
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ ...transition.view, duration: 0.5 }}
    >
      <header className="sd-ov-panel__head">
        <div>
          <h2 id={id}>{title}</h2>
          <p>{meta}</p>
        </div>
      </header>
      {children}
    </motion.section>
  )
}

/** Network sales per month, stacked by region, with last year on the same days as a marker. */
function MonthlyChart({ monthly }: { monthly: Market['monthly'] }) {
  const [active, setActive] = useState<number | null>(null)
  const { ref, width } = useElementWidth<HTMLDivElement>(720)
  const totals = monthly.map((month) => ({
    month,
    sales: REGIONS.reduce((sum, region) => sum + month.regions[region].sales, 0),
    ly: REGIONS.reduce((sum, region) => sum + month.regions[region].ly, 0)
  }))
  const max = Math.max(1, ...totals.flatMap((row) => [row.sales, row.ly])) * 1.1
  const height = 280
  const pad = { top: 12, right: 8, bottom: 30, left: 56 }
  const plotH = height - pad.top - pad.bottom
  const slot = (width - pad.left - pad.right) / monthly.length
  const barW = Math.min(40, slot * 0.55)
  const y = (value: number) => pad.top + plotH - (value / max) * plotH
  const current = active === null ? null : totals[active]

  return (
    <div className="sd-mk-monthly" ref={ref}>
      <svg width={width} height={height} role="img" aria-label={`Vendite mensili della rete negli ultimi ${monthly.length} mesi, con l'anno precedente a parità di giorni`}>
        {[0, 0.5, 1].map((share) => (
          <g key={share}>
            <line x1={pad.left} x2={width - pad.right} y1={y((max / 1.1) * share)} y2={y((max / 1.1) * share)} className="sd-biz-trend__grid" />
            <text x={pad.left - 8} y={y((max / 1.1) * share) + 4} textAnchor="end" className="sd-biz-trend__tick">{formatEuroCompact((max / 1.1) * share)}</text>
          </g>
        ))}
        {totals.map((row, index) => {
          const cx = pad.left + slot * index + slot / 2
          let base = y(0)
          return (
            <g key={row.month.month} onPointerEnter={() => setActive(index)} onPointerLeave={() => setActive(null)} className={active === index ? 'is-active' : undefined}>
              <rect x={cx - slot / 2} y={pad.top} width={slot} height={plotH} fill="transparent" />
              {REGIONS.map((region, layer) => {
                const value = row.month.regions[region].sales
                const h = (value / max) * plotH
                const top = base - h
                base = top
                return (
                  <motion.rect
                    key={region}
                    x={cx - barW / 2}
                    width={barW}
                    className={`sd-mk-region is-${region.toLowerCase()}`}
                    initial={{ y: y(0), height: 0 }}
                    animate={{ y: top, height: h }}
                    transition={{ ...rise, delay: 0.2 + index * stagger + layer * 0.08 }}
                  />
                )
              })}
              <motion.line
                x1={cx - barW / 2 - 4}
                x2={cx + barW / 2 + 4}
                y1={y(row.ly)}
                y2={y(row.ly)}
                className="sd-mk-ly"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.9 + index * stagger }}
              />
              {/* Narrow charts label every other month, always including the latest one. */}
              {(slot >= 44 || (monthly.length - 1 - index) % 2 === 0) && (
                <text x={cx} y={height - 10} textAnchor="middle" className="sd-biz-trend__tick">
                  {monthName(row.month.month)}
                  {row.month.partial_until && slot >= 56 ? ` 1–${row.month.partial_until}` : ''}
                </text>
              )}
            </g>
          )
        })}
      </svg>
      {current && active !== null && (
        <div className="sd-biz-tooltip sd-mk-tooltip" style={{ left: Math.min(Math.max(pad.left + slot * active + slot / 2, 110), width - 110) }} role="status">
          <strong>
            {monthName(current.month.month)} {current.month.month.slice(0, 4)}
            {current.month.partial_until ? `, giorni 1–${current.month.partial_until}` : ''}
          </strong>
          {REGIONS.map((region) => (
            <span key={region}><i className={`sd-mk-swatch is-${region.toLowerCase()}`} />{regionNames[region]} {formatEuroCompact(current.month.regions[region].sales)}</span>
          ))}
          <span>Totale {formatEuro(current.sales)}</span>
          <span className={tone(yoy(current.sales, current.ly)).trim()}>{formatChange(yoy(current.sales, current.ly))} sull'anno precedente</span>
        </div>
      )}
    </div>
  )
}

function SentimentChart({ weeks, last }: { weeks: Market['social']['weeks']; last: string }) {
  const max = Math.max(1, ...weeks.map((week) => week.pos + week.neu + week.neg))
  return (
    <div className="sd-mk-social" role="img" aria-label={`Post sul brand per settimana, divisi per sentiment, ${weeks.length} settimane`}>
      {weeks.map((week, index) => {
        const total = week.pos + week.neu + week.neg
        // The last week is partial when its Sunday falls after the last known day.
        const partial = index === weeks.length - 1 && Date.parse(`${week.week}T00:00:00Z`) + 6 * 86_400_000 > Date.parse(`${last}T00:00:00Z`)
        return (
          <div key={week.week} className="sd-mk-social__col" title={`Settimana del ${dayName(week.week)}: ${total} post, ${week.pos} positivi, ${week.neg} negativi${partial ? ' (settimana in corso)' : ''}`}>
            <motion.div
              className={`sd-mk-social__stack${partial ? ' is-partial' : ''}`}
              initial={{ height: 0 }}
              animate={{ height: `${(total / max) * 100}%` }}
              transition={{ ...rise, delay: 0.3 + index * 0.03 }}
            >
              <span className="is-neg" style={{ flexGrow: week.neg }} />
              <span className="is-neu" style={{ flexGrow: week.neu }} />
              <span className="is-pos" style={{ flexGrow: week.pos }} />
            </motion.div>
          </div>
        )
      })}
    </div>
  )
}

export function MarketView({ runId }: { runId: string }) {
  const market = useRunData<Market>(runId, 'market')
  if (market.status !== 'ready' || !market.data)
    return (
      <EmptyState
        title={market.status === 'loading' ? 'Carico i trend di mercato…' : 'Trend di mercato non disponibili'}
        description={
          market.status === 'unavailable'
            ? 'Questo run non ha trend di mercato: il backend non li espone ancora e il mock li calcola solo per il cutoff più recente.'
            : market.status === 'error'
              ? 'Richiesta non riuscita. Ricarica la pagina per riprovare.'
              : undefined
        }
      />
    )

  const data = market.data
  const thisMonth = data.monthly[data.monthly.length - 1]
  const monthNow = REGIONS.reduce((sum, region) => sum + thisMonth.regions[region].sales, 0)
  const monthLy = REGIONS.reduce((sum, region) => sum + thisMonth.regions[region].ly, 0)
  const monthBudget = REGIONS.reduce((sum, region) => sum + thisMonth.regions[region].budget, 0)
  const regionGrowth = data.regions.map((row) => ({ ...row, yoy: yoy(row.sales, row.ly), mom: yoy(row.sales, row.before) }))
  const leader = [...regionGrowth].sort((a, b) => (b.yoy ?? -1) - (a.yoy ?? -1))[0]
  const totalCategory = data.categories.reduce((sum, row) => sum + row.sales, 0)
  const categories = data.categories.map((row) => ({ ...row, share: totalCategory ? row.sales / totalCategory : 0, yoy: yoy(row.sales, row.ly), mom: yoy(row.sales, row.before) }))
  const main = categories[0]
  const fastest = [...categories].filter((row) => row.share >= 0.03).sort((a, b) => (b.yoy ?? -1) - (a.yoy ?? -1))[0]
  const lastWeeks = data.social.weeks.slice(-4)
  const positive = lastWeeks.reduce((sum, week) => sum + week.pos, 0) / Math.max(1, lastWeeks.reduce((sum, week) => sum + week.pos + week.neu + week.neg, 0))
  const topTag = data.social.hashtags[0]

  const insights = [
    {
      label: `Rete, ${monthName(thisMonth.month.slice(0, 7))} 1–${thisMonth.partial_until ?? 31}`,
      value: formatChange(yoy(monthNow, monthLy)),
      tone: tone(yoy(monthNow, monthLy)),
      text: `${formatEuroCompact(monthNow)} di vendite contro ${formatEuroCompact(monthLy)} negli stessi giorni dell'anno scorso. Budget del periodo ${formatChange(yoy(monthNow, monthBudget))}.`
    },
    {
      label: 'Regione che traina',
      value: formatChange(leader.yoy),
      tone: tone(leader.yoy),
      text: `${regionNames[leader.region]}: ${formatEuroCompact(leader.sales)} nelle ultime 4 settimane, sugli stessi giorni della settimana dell'anno scorso.`
    },
    {
      label: `${categoryNames[fastest.category] ?? fastest.category} in accelerazione`,
      value: formatChange(fastest.yoy),
      tone: tone(fastest.yoy),
      text: `${categoryNames[main.category] ?? main.category} resta il motore: ${Math.round(main.share * 100)}% delle vendite delle ultime 4 settimane, ${formatChange(main.yoy)} sull'anno scorso.`
    },
    {
      label: 'Conversazione social',
      value: topTag ? `#${topTag.tag}` : '–',
      tone: '',
      text: topTag
        ? `Da ${topTag.before} a ${topTag.now} post in due settimane. Sentiment positivo nel ${Math.round(positive * 100)}% dei post delle ultime 4 settimane.`
        : 'Nessun tema in crescita nelle ultime due settimane.'
    }
  ]

  return (
    <div className="sd-mk">
      <motion.p className="sd-mk-lead" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ ...transition.view, duration: 0.5 }}>
        Fino al {dayName(data.last_day)} i negozi del run vendono {formatChange(yoy(monthNow, monthLy))} sull'anno scorso a parità di giorni.{' '}
        {regionNames[leader.region]} guida la crescita e i {(categoryNames[main.category] ?? main.category).toLowerCase()} valgono{' '}
        {Math.round(main.share * 100)}% delle vendite.
        {topTag ? ` Sui social gli hashtag in maggiore crescita sono #${data.social.hashtags.slice(0, 3).map((row) => row.tag).join(', #')}.` : ''}
      </motion.p>

      <ul className="sd-mk-insights">
        {insights.map((card, index) => (
          <motion.li
            key={card.label}
            className="sd-mk-insight"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...transition.view, duration: 0.5, delay: 0.15 + index * 0.08 }}
          >
            <span className="sd-mk-insight__label">{card.label}</span>
            <strong className={`sd-mk-insight__value${card.tone}`}>{card.value}</strong>
            <span className="sd-mk-insight__text">{card.text}</span>
          </motion.li>
        ))}
      </ul>

      <div className="sd-mk-grid">
        <Section id="mk-monthly" title="Vendite della rete, mese per mese" meta="Negozi del run, euro al cambio di budget. Il trattino è l'anno precedente negli stessi giorni del mese." className="sd-mk-wide">
          <MonthlyChart monthly={data.monthly} />
          <ul className="sd-ov-legend" aria-hidden="true">
            {REGIONS.map((region) => (
              <li key={region}><span className={`sd-mk-swatch is-${region.toLowerCase()}`} />{regionNames[region]}</li>
            ))}
            <li><span className="sd-mk-ly-key" />Anno precedente</li>
          </ul>
        </Section>

        <Section id="mk-regions" title="Regioni, ultime 4 settimane" meta="Contro gli stessi giorni della settimana dell'anno scorso.">
          <ul className="sd-mk-regions">
            {[...regionGrowth].sort((a, b) => b.sales - a.sales).map((row, index) => {
              const peak = Math.max(row.sales, row.ly, 1)
              return (
                <li key={row.region}>
                  <div className="sd-mk-regions__head">
                    <span><i className={`sd-mk-swatch is-${row.region.toLowerCase()}`} />{regionNames[row.region]}</span>
                    <strong className={tone(row.yoy).trim()}>{formatChange(row.yoy)}</strong>
                  </div>
                  <div className="sd-mk-regions__bars">
                    <motion.span className={`is-now is-${row.region.toLowerCase()}`} style={{ originX: 0, width: `${(row.sales / peak) * 100}%` }} initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ ...rise, delay: 0.4 + index * 0.1 }} />
                    <motion.span className="is-ly" style={{ originX: 0, width: `${(row.ly / peak) * 100}%` }} initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ ...rise, delay: 0.5 + index * 0.1 }} />
                  </div>
                  <span className="sd-mk-regions__meta">{formatEuroCompact(row.sales)} contro {formatEuroCompact(row.ly)} · {formatChange(row.mom)} sulle 4 settimane prima</span>
                </li>
              )
            })}
          </ul>
        </Section>

        <Section id="mk-categories" title="Categorie, ultime 4 settimane" meta="Dettaglio vendite SKU e crescita sull'anno scorso. Gli scostamenti dai KPI regionali restano nei dati.">
          <ul className="sd-mk-categories">
            {categories.map((row, index) => (
              <li key={row.category}>
                <span className="sd-mk-categories__name">{categoryNames[row.category] ?? row.category}</span>
                <span className="sd-mk-categories__track">
                  <motion.span style={{ originX: 0, width: `${(row.share / Math.max(...categories.map((item) => item.share))) * 100}%` }} initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ ...rise, delay: 0.4 + index * stagger }} />
                </span>
                <span className="sd-mk-categories__share">{Math.round(row.share * 100)}%</span>
                <span className={`sd-mk-categories__yoy${tone(row.yoy)}`}>{formatChange(row.yoy)}</span>
              </li>
            ))}
          </ul>
        </Section>

        <Section id="mk-social" title="Il brand sui social" meta={`${data.social.posts.toLocaleString('it-IT')} post nell'ascolto globale del brand, per settimana e sentiment. Temi in crescita nelle ultime due settimane.`} className="sd-mk-wide">
          <div className="sd-mk-social-wrap">
            <div>
              <SentimentChart weeks={data.social.weeks} last={data.last_day} />
              <ul className="sd-ov-legend" aria-hidden="true">
                <li><span className="sd-mk-swatch is-pos" />Positivo</li>
                <li><span className="sd-mk-swatch is-neu" />Neutro</li>
                <li><span className="sd-mk-swatch is-neg" />Negativo</li>
              </ul>
            </div>
            <ol className="sd-mk-tags">
              {data.social.hashtags.map((row, index) => (
                <motion.li key={row.tag} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ ...transition.view, delay: 0.5 + index * 0.05 }}>
                  <span>#{row.tag}</span>
                  <strong>{row.now}</strong>
                  <span className="is-up">+{row.now - row.before}</span>
                </motion.li>
              ))}
            </ol>
          </div>
        </Section>
      </div>
    </div>
  )
}
