import { useId, useState } from 'react'
import type { ReactNode } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { EmptyState, ErrorState, LoadingState } from '../ui'
import type { DemoScenario } from '../demo/scenario'
import { fmt, messages } from '../i18n'
import './widgets.css'
export interface ChartLegend {
  label: string
  style: 'primary' | 'comparison' | 'third'
}
export interface ChartCardProps {
  title: string
  legend: ChartLegend[]
  summary: string
  children: ReactNode
  table: ReactNode
  actions?: ReactNode
  state?: DemoScenario
  onRetry?: () => void
  className?: string
}
export function ChartCard({
  title,
  legend,
  summary,
  children,
  table,
  actions,
  state = 'data',
  onRetry,
  className = ''
}: ChartCardProps) {
  const id = useId()
  const reduceMotion = useReducedMotion()
  const [showData, setShowData] = useState(false)
  return (
    <figure className={`sd-chart-card sd-panel ${className}`} aria-labelledby={id}>
      <figcaption className="sd-chart-heading">
        <div>
          <h2 id={id}>{title}</h2>
        </div>
        {actions}
      </figcaption>
      <ul className="sd-chart-legend" aria-label={messages.dashboard.charts.legend}>
        {legend.map((item) => (
          <li key={item.label}>
            <span className={`sd-legend-mark sd-legend-mark--${item.style}`} aria-hidden="true" />
            {item.label}
          </li>
        ))}
      </ul>
      {state === 'loading' ? (
        <LoadingState label={fmt(messages.dashboard.metrics.loading, { label: title })} lines={5} announce={false} />
      ) : state === 'empty' ? (
        <EmptyState
          title={messages.dashboard.charts.noData}
          description={messages.dashboard.charts.changeFilters}
          compact
        />
      ) : state === 'error' ? (
        <ErrorState
          title={messages.dashboard.charts.unavailable}
          description={messages.dashboard.charts.disconnected}
          onRetry={onRetry}
          compact
          announce={false}
        />
      ) : (
        <>
          <div className="sd-chart-region">{children}</div>
          <p className="sd-chart-summary">{summary}</p>
          <details className="sd-chart-disclosure" onToggle={(event) => setShowData(event.currentTarget.open)}>
            <summary aria-expanded={showData}>{messages.dashboard.charts.showData}</summary>
            <AnimatePresence initial={false}>
              {showData && (
                <motion.div
                  key="chart-data"
                  className="sd-chart-disclosure-content"
                  initial={reduceMotion ? { height: 'auto', opacity: 0 } : { height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={reduceMotion ? { height: 'auto', opacity: 0 } : { height: 0, opacity: 0 }}
                  transition={reduceMotion ? { opacity: { duration: 0.16, ease: [0.23, 1, 0.32, 1] } } : { height: { duration: 0.22, ease: [0.25, 1, 0.5, 1] }, opacity: { duration: 0.16, ease: [0.23, 1, 0.32, 1] } }}
                  style={{ overflow: 'hidden' }}
                >
                  <div className="sd-chart-data" role="region" aria-label={fmt(messages.dashboard.charts.dataFor, { title })} tabIndex={0}>
                    {table}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </details>
        </>
      )}
    </figure>
  )
}
