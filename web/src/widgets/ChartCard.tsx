import { useId } from 'react'
import type { ReactNode } from 'react'
import { EmptyState, ErrorState, LoadingState } from '../ui'
import type { DemoScenario } from '../demo/scenario'
import './widgets.css'
export interface ChartLegend {
  label: string
  style: 'primary' | 'comparison' | 'third'
}
export interface ChartCardProps {
  title: string
  period: string
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
  period,
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
  return (
    <figure className={`sd-chart-card sd-panel ${className}`} aria-labelledby={id}>
      <figcaption className="sd-chart-heading">
        <div>
          <h2 id={id}>{title}</h2>
          <p>{period}</p>
        </div>
        {actions}
      </figcaption>
      <ul className="sd-chart-legend" aria-label="Legenda">
        {legend.map((item) => (
          <li key={item.label}>
            <span className={`sd-legend-mark sd-legend-mark--${item.style}`} aria-hidden="true" />
            {item.label}
          </li>
        ))}
      </ul>
      {state === 'loading' ? (
        <LoadingState label={`Caricamento: ${title}`} lines={5} announce={false} />
      ) : state === 'empty' ? (
        <EmptyState
          title="Nessun dato da mostrare"
          description="Prova a modificare i filtri."
          compact
        />
      ) : state === 'error' ? (
        <ErrorState
          title="Grafico non disponibile"
          description="Connessione demo interrotta."
          onRetry={onRetry}
          compact
          announce={false}
        />
      ) : (
        <>
          <div className="sd-chart-region">{children}</div>
          <p className="sd-chart-summary">{summary}</p>
          <details className="sd-chart-disclosure">
            <summary>Mostra dati</summary>
            <div className="sd-chart-data" role="region" aria-label={`Dati: ${title}`} tabIndex={0}>
              {table}
            </div>
          </details>
        </>
      )}
    </figure>
  )
}
