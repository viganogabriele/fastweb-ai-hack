import { useEffect, useId, useRef, useState } from 'react'
import { formatNumber, formatPercent } from '../ui'
import type { CategoryPoint, TimePoint } from '../demo/data'
import { fmt, messages } from '../i18n'
import './widgets.css'
function usePlotWidth() {
  const ref = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(600)
  useEffect(() => {
    const element = ref.current
    if (!element) return
    const observer = new ResizeObserver((entries) =>
      setWidth(Math.max(200, entries[0].contentRect.width))
    )
    observer.observe(element)
    return () => observer.disconnect()
  }, [])
  return { ref, width }
}
const compactNumber = (value: number) =>
  formatNumber(value, { notation: 'compact', maximumFractionDigits: 1 })
export function LineChart({ points, unit = messages.dashboard.metrics.requestUnit }: { points: TimePoint[]; unit?: string }) {
  const { ref, width } = usePlotWidth()
  const [active, setActive] = useState<number | null>(null)
  const tooltipId = useId()
  const selected = active === null ? null : points[Math.min(active, points.length - 1)]
  const w = width
  const left = 58
  const plotWidth = w - left - 18
  const top = 24
  const plotHeight = 170
  const max = Math.max(...points.flatMap((point) => [point.value, point.comparison]), 1) * 1.12
  const x = (index: number) => left + (index / Math.max(points.length - 1, 1)) * plotWidth
  const y = (value: number) => top + plotHeight - (value / max) * plotHeight
  const path = (key: 'value' | 'comparison') =>
    points.map((point, index) => `${index ? 'L' : 'M'}${x(index)},${y(point[key])}`).join(' ')
  const ticks = new Set([
    0,
    Math.round((points.length - 1) / 2),
    points.length - 1,
    ...(width > 520
      ? [Math.round((points.length - 1) / 4), Math.round(((points.length - 1) * 3) / 4)]
      : [])
  ])
  return (
    <div ref={ref} className="sd-line-chart">
      <div
        className="sd-focus-plot"
        tabIndex={0}
        role="group"
        aria-label={messages.dashboard.charts.trendA11y}
        aria-describedby={tooltipId}
        onFocus={() => setActive(0)}
        onBlur={() => setActive(null)}
        onKeyDown={(event) => {
          if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
          event.preventDefault()
          setActive((index) =>
            event.key === 'Home'
              ? 0
              : event.key === 'End'
                ? points.length - 1
                : Math.min(
                    points.length - 1,
                    Math.max(0, (index ?? 0) + (event.key === 'ArrowRight' ? 1 : -1))
                  )
          )
        }}
      >
        <svg
          viewBox={`0 0 ${w} 238`}
          aria-hidden="true"
          onMouseLeave={() => {
            if (document.activeElement !== ref.current?.firstElementChild) setActive(null)
          }}
        >
          {[0, 1, 2, 3].map((tick) => {
            const value = (max * tick) / 3
            return (
              <g key={tick}>
                <line className="sd-gridline" x1={left} x2={w - 18} y1={y(value)} y2={y(value)} />
                <text x={left - 8} y={y(value) + 4} textAnchor="end">
                  {compactNumber(value)}
                </text>
              </g>
            )
          })}
          <text x={left} y={12}>
            {unit}
          </text>
          <path className="sd-line-comparison" d={path('comparison')} />
          <path className="sd-line-primary" d={path('value')} />
          {points.map((point, index) => (
            <g key={point.fullLabel} onMouseEnter={() => setActive(index)}>
              <circle
                className="sd-line-point"
                cx={x(index)}
                cy={y(point.value)}
                r={active === index ? 5 : 2.5}
              />
              <rect
                className="sd-point-hit"
                x={x(index) - plotWidth / Math.max(points.length - 1, 1) / 2}
                y={top}
                width={plotWidth / Math.max(points.length - 1, 1)}
                height={plotHeight}
              />
              {ticks.has(index) && (
                <text
                  x={x(index)}
                  y={222}
                  textAnchor={
                    index === 0 ? 'start' : index === points.length - 1 ? 'end' : 'middle'
                  }
                >
                  {point.label}
                </text>
              )}
            </g>
          ))}
          {active !== null && points[active] && (
            <line
              className="sd-crosshair"
              x1={x(active)}
              x2={x(active)}
              y1={top}
              y2={top + plotHeight}
            />
          )}
        </svg>
      </div>
      <p id={tooltipId} className="sd-chart-tooltip">
        {selected
          ? fmt(messages.dashboard.charts.tooltip, {
              date: selected.fullLabel,
              value: formatNumber(selected.value),
              previous: formatNumber(selected.comparison),
              unit
            })
          : messages.dashboard.charts.explore}
      </p>
    </div>
  )
}
export function BarChart({ points, unit = messages.dashboard.metrics.requestUnit }: { points: CategoryPoint[]; unit?: string }) {
  const max = Math.max(...points.map((point) => point.value), 1)
  return (
    <ul className="sd-comparison-bars" aria-label={fmt(messages.dashboard.charts.requestsByService, { unit })}>
      {points.map((point) => (
        <li key={point.label}>
          <span>{point.label}</span>
          <strong>
            {formatNumber(point.value)} {unit}
          </strong>
          <svg viewBox="0 0 500 12" preserveAspectRatio="none" aria-hidden="true">
            <rect className="sd-bar-track" width="500" height="12" rx="2" />
            <rect className="sd-bar-fill" width={(point.value / max) * 500} height="12" rx="2" />
          </svg>
        </li>
      ))}
    </ul>
  )
}
export function DistributionChart({
  points,
  unit = messages.dashboard.metrics.requestUnit
}: {
  points: CategoryPoint[]
  unit?: string
}) {
  const id = useId().replaceAll(':', '')
  const total = points.reduce((sum, point) => sum + point.value, 0)
  const styles = ['primary', 'comparison', 'third']
  return (
    <div className="sd-distribution">
      <svg
        viewBox="0 0 360 80"
        role="img"
        aria-label={fmt(messages.dashboard.charts.regionalDistribution, { total: formatNumber(total), unit })}
      >
        <defs>
          <pattern id={`${id}-stripe`} patternUnits="userSpaceOnUse" width="8" height="8">
            <path className="sd-pattern-line" d="M0 8L8 0" />
          </pattern>
          <pattern id={`${id}-dot`} patternUnits="userSpaceOnUse" width="8" height="8">
            <circle className="sd-pattern-dot" cx="4" cy="4" r="1.5" />
          </pattern>
        </defs>
        {points.map((point, index) => {
          const start = total
            ? (points.slice(0, index).reduce((sum, item) => sum + item.value, 0) / total) * 360
            : 0
          const length = total ? (point.value / total) * 360 : 0
          return (
            <g key={point.label}>
              <rect
                className={`sd-distribution-segment sd-distribution-segment--${styles[index]}`}
                x={start}
                y={8}
                width={length}
                height={56}
              />
              {index > 0 && (
                <rect
                  x={start}
                  y={8}
                  width={length}
                  height={56}
                  fill={`url(#${id}-${index === 1 ? 'stripe' : 'dot'})`}
                />
              )}
            </g>
          )
        })}
      </svg>
      <ul className="sd-distribution-labels">
        {points.map((point, index) => (
          <li key={point.label}>
            <span>
              <span
                className={`sd-legend-mark sd-legend-mark--${styles[index]}`}
                aria-hidden="true"
              />
              {point.label}
            </span>
            <strong>{formatPercent(total ? point.value / total : 0)}</strong>
            <small>
              {formatNumber(point.value)} {unit}
            </small>
          </li>
        ))}
      </ul>
    </div>
  )
}
