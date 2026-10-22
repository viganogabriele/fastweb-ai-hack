import { ArrowDownRight, ArrowRight, ArrowUpRight } from 'lucide-react'
import { ErrorState, LoadingState, formatDelta } from '../ui'
import type { DemoScenario } from '../demo/scenario'
import { fmt, messages } from '../i18n'
import './widgets.css'
export interface KpiCardProps {
  label: string
  value: string
  unit: string
  period?: string
  delta: number
  higherIsBetter?: boolean
  sparkline?: number[]
  state?: DemoScenario
}
export function KpiCard({
  label,
  value,
  unit,
  period,
  delta,
  higherIsBetter = true,
  sparkline,
  state = 'data'
}: KpiCardProps) {
  // A delta that rounds to ±0,0% is shown as stable, not as an improvement or regression.
  const shown = Math.abs(delta) < 0.0005 ? 0 : delta
  const Direction = shown > 0 ? ArrowUpRight : shown < 0 ? ArrowDownRight : ArrowRight
  const tone = shown === 0 ? 'neutral' : shown > 0 === higherIsBetter ? 'positive' : 'negative'
  const points = sparkline
    ?.map(
      (point, index) =>
        `${(index / Math.max(sparkline.length - 1, 1)) * 120},${32 - ((point - Math.min(...sparkline)) / (Math.max(...sparkline) - Math.min(...sparkline) || 1)) * 28}`
    )
    .join(' ')
  return (
    <article className="sd-kpi sd-panel" aria-label={label}>
      <h2 className="sd-kpi-label">{label}</h2>
      {state === 'loading' ? (
          <LoadingState label={fmt(messages.dashboard.metrics.loading, { label })} lines={2} compact announce={false} />
      ) : state === 'error' ? (
        <ErrorState title={messages.dashboard.metrics.unavailable} compact announce={false} />
      ) : (
        <>
          <p className="sd-kpi-value">
            {state === 'empty' ? '—' : value} <span>{unit}</span>
          </p>
          {period && <p className="sd-kpi-period">{period}</p>}
          {state === 'data' && (
            <p className={`sd-kpi-delta sd-kpi-delta--${tone}`}>
              <Direction aria-hidden="true" />
              <strong>{formatDelta(shown)}</strong>
              <span>{messages.dashboard.metrics.vsPrevious}</span>
            </p>
          )}
          {state === 'data' && points && (
            <svg className="sd-sparkline" viewBox="0 0 120 36" aria-hidden="true">
              <polyline points={points} fill="none" />
            </svg>
          )}
        </>
      )}
    </article>
  )
}
