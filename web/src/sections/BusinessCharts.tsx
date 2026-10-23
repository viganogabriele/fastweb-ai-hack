import { useId, useState } from 'react'
import type { KeyboardEvent, PointerEvent } from 'react'
import { motion } from 'motion/react'
import type { Case } from '../api/client'
import { formatChange, formatEuro, formatEuroCompact } from './businessData'
import type { DayPoint, StorePerformance } from './businessData'
import { useElementWidth } from './useElementWidth'

type Priority = Case['priority']

const dayLabel = (date: string) => new Date(`${date}T12:00:00Z`).toLocaleDateString('it-IT', { day: 'numeric', month: 'short', timeZone: 'UTC' })


export interface DaySignals {
  count: number
  top: Priority | null
}

/**
 * Sales against budget, one point per day, with the day each store signal arrived marked under
 * the axis: the chart ties what stores said to what the tills recorded.
 */
export function SalesTrend({
  points,
  pending,
  signals,
  replayKey
}: {
  points: DayPoint[]
  /** Days up to the run cutoff whose sales are not known yet: shaded, with their signals only. */
  pending: string[]
  signals: Map<string, DaySignals>
  replayKey: string
}) {
  const { ref, width } = useElementWidth<HTMLDivElement>(720)
  const gradient = useId()
  const [active, setActive] = useState<number | null>(null)
  const height = 260
  const pad = { top: 16, right: 16, bottom: 46, left: 64 }
  const plotW = width - pad.left - pad.right
  const plotH = height - pad.top - pad.bottom
  const max = Math.max(1, ...points.flatMap((point) => [point.sales, point.budget])) * 1.08
  const days = [...points.map((point) => point.date), ...pending]
  const x = (index: number) => pad.left + (days.length > 1 ? (index / (days.length - 1)) * plotW : plotW / 2)
  const step = days.length > 1 ? plotW / (days.length - 1) : plotW
  const y = (value: number) => pad.top + plotH - (value / max) * plotH
  const line = (key: 'sales' | 'budget') => points.map((point, index) => `${index ? 'L' : 'M'}${x(index).toFixed(1)} ${y(point[key]).toFixed(1)}`).join('')
  const area = `${line('sales')}L${x(points.length - 1).toFixed(1)} ${y(0)}L${x(0).toFixed(1)} ${y(0)}Z`
  const ticks = [0, 0.5, 1].map((share) => max * share / 1.08)
  const labelEvery = Math.ceil(days.length / 6)
  const markerY = height - pad.bottom + 22

  const pick = (event: PointerEvent<SVGRectElement>) => {
    const box = event.currentTarget.getBoundingClientRect()
    const share = (event.clientX - box.left) / box.width
    setActive(Math.round(Math.min(1, Math.max(0, share)) * (days.length - 1)))
  }
  const onKey = (event: KeyboardEvent<SVGSVGElement>) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return
    event.preventDefault()
    const step = event.key === 'ArrowLeft' ? -1 : 1
    setActive((current) => Math.min(days.length - 1, Math.max(0, (current ?? days.length - 1) + step)))
  }

  const activeDate = active === null ? null : days[active]
  const current = active === null ? null : (points[active] ?? null)
  const currentSignals = activeDate ? signals.get(activeDate) : undefined
  const below = points.filter((point) => point.budget > 0 && point.sales < point.budget).length

  return (
    <div className="sd-biz-trend" ref={ref}>
      <svg
        width={width}
        height={height}
        role="img"
        tabIndex={0}
        aria-label={`Vendite giornaliere contro budget su ${points.length} giorni: ${below} giorni sotto budget. Usa le frecce per leggere i singoli giorni.`}
        onKeyDown={onKey}
        onBlur={() => setActive(null)}
      >
        <defs>
          <linearGradient id={gradient} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" className="sd-biz-trend__fill-stop" stopOpacity="0.28" />
            <stop offset="100%" className="sd-biz-trend__fill-stop" stopOpacity="0" />
          </linearGradient>
        </defs>
        {ticks.map((value) => (
          <g key={value}>
            <line x1={pad.left} x2={width - pad.right} y1={y(value)} y2={y(value)} className="sd-biz-trend__grid" />
            <text x={pad.left - 10} y={y(value) + 4} textAnchor="end" className="sd-biz-trend__tick">{formatEuroCompact(value)}</text>
          </g>
        ))}
        {pending.length > 0 && (
          <g className="sd-biz-trend__pending">
            <rect x={x(points.length) - step / 2} y={pad.top} width={step * pending.length} height={plotH} />
            <text x={x(points.length) - step / 2 - 6} y={pad.top + 12} textAnchor="end">Vendite non ancora registrate</text>
          </g>
        )}
        {days.map((date, index) =>
          index % labelEvery === 0 || index === days.length - 1 ? (
            <text key={date} x={x(index)} y={height - pad.bottom + 42} textAnchor="middle" className="sd-biz-trend__tick">
              {dayLabel(date)}
            </text>
          ) : null
        )}

        {/* Replays when the scope changes, so a filter change is visible in the chart itself. */}
        <g key={replayKey}>
          <motion.path d={area} fill={`url(#${gradient})`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8, delay: 0.5 }} />
          <motion.path
            d={line('budget')}
            className="sd-biz-trend__budget"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.1, ease: [0.33, 1, 0.68, 1] }}
          />
          <motion.path
            d={line('sales')}
            className="sd-biz-trend__sales"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.3, ease: [0.33, 1, 0.68, 1], delay: 0.1 }}
          />
          {days.map((date, index) => {
            const day = signals.get(date)
            if (!day?.count) return null
            return (
              <motion.circle
                key={date}
                cx={x(index)}
                cy={markerY}
                r={3 + Math.min(day.count, 4) * 1.5}
                className={`sd-biz-trend__signal is-${day.top ?? 'low'}`}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
                transition={{ type: 'spring', duration: 0.5, bounce: 0.3, delay: 1 + index * 0.012 }}
              />
            )
          })}
        </g>
        <text x={pad.left - 10} y={markerY + 4} textAnchor="end" className="sd-biz-trend__tick">Segnali</text>

        {active !== null && (
          <g className="sd-biz-trend__cursor" pointerEvents="none">
            <line x1={x(active)} x2={x(active)} y1={pad.top} y2={markerY} />
            {current && <circle cx={x(active)} cy={y(current.budget)} r={4} className="sd-biz-trend__dot-budget" />}
            {current && <circle cx={x(active)} cy={y(current.sales)} r={5} className="sd-biz-trend__dot-sales" />}
          </g>
        )}
        <rect
          x={pad.left}
          y={pad.top}
          width={plotW}
          height={plotH + 30}
          fill="transparent"
          onPointerMove={pick}
          onPointerDown={pick}
          onPointerLeave={() => setActive(null)}
        />
      </svg>

      {activeDate && active !== null && (
        <div
          className="sd-biz-tooltip"
          style={{ left: Math.min(Math.max(x(active), 110), width - 110), top: 8 }}
          role="status"
        >
          <strong>{dayLabel(activeDate)}</strong>
          {current ? (
            <>
              <span><i className="is-sales" />Vendite {formatEuro(current.sales)}</span>
              <span><i className="is-budget" />Budget {formatEuro(current.budget)}</span>
              <span className={current.sales >= current.budget ? 'is-up' : 'is-down'}>
                {formatChange(current.budget > 0 ? current.sales / current.budget - 1 : null)} sul budget
              </span>
            </>
          ) : (
            <span>Vendite non ancora registrate</span>
          )}
          {currentSignals?.count ? <span>{currentSignals.count} {currentSignals.count === 1 ? 'segnale arrivato' : 'segnali arrivati'}</span> : null}
        </div>
      )}
    </div>
  )
}

/** Gap to budget per store, diverging from zero. Clicking a store selects it across the page. */
export function BudgetBars({ stores, selected, onSelect }: { stores: StorePerformance[]; selected: string; onSelect: (id: string) => void }) {
  const ranked = [...stores].filter((store) => store.vsBudget !== null).sort((a, b) => a.vsBudget! - b.vsBudget!)
  const reach = Math.max(0.05, ...ranked.map((store) => Math.abs(store.vsBudget!)))
  return (
    <ul className="sd-biz-bars">
      {ranked.map((store, index) => {
        const share = Math.abs(store.vsBudget!) / reach / 2
        const up = store.vsBudget! >= 0
        return (
          <li key={store.id}>
            <button type="button" aria-pressed={selected === store.id} onClick={() => onSelect(selected === store.id ? 'all' : store.id)}>
              <span className="sd-biz-bars__name">{store.id}</span>
              <span className="sd-biz-bars__track" aria-hidden="true">
                <motion.span
                  className={`sd-biz-bars__bar ${up ? 'is-up' : 'is-down'}`}
                  style={{ [up ? 'left' : 'right']: '50%', width: `${share * 100}%`, originX: up ? 0 : 1 }}
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ type: 'spring', duration: 0.7, bounce: 0, delay: 0.3 + index * 0.04 }}
                />
              </span>
              <span className={`sd-biz-bars__value ${up ? 'is-up' : 'is-down'}`}>{formatChange(store.vsBudget)}</span>
              <span className="sd-biz-bars__sales">{formatEuroCompact(store.sales)}</span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}

/** Tiny daily sales line for a store row. */
export function Sparkline({ values, tone }: { values: number[]; tone: 'up' | 'down' | 'flat' }) {
  const width = 72
  const height = 22
  const max = Math.max(1, ...values)
  const path = values
    .map((value, index) => `${index ? 'L' : 'M'}${((index / Math.max(1, values.length - 1)) * width).toFixed(1)} ${(height - 2 - (value / max) * (height - 4)).toFixed(1)}`)
    .join('')
  return (
    <svg className={`sd-biz-spark is-${tone}`} width={width} height={height} aria-hidden="true">
      <motion.path d={path} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.9, delay: 0.5 }} />
    </svg>
  )
}
