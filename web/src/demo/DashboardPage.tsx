import { useEffect, useState } from 'react'
import { Activity, CircleHelp } from 'lucide-react'
import { Button, StatusBadge, formatNumber, formatPercent } from '../ui'
import { ChartCard } from '../widgets/ChartCard'
import { DataTable } from '../widgets/DataTable'
import type { DataColumn } from '../widgets/DataTable'
import { FilterBar } from '../widgets/FilterBar'
import { KpiCard } from '../widgets/KpiCard'
import { BarChart, DistributionChart, LineChart } from '../widgets/charts'
import { fetchDashboard } from './api'
import type { DashboardResponse } from './api'
import { DEFAULT_FILTERS, PERIOD_LABELS } from './data'
import type { DashboardFilters, ServiceRow } from './data'
import type { DemoScenario } from './scenario'
import '../widgets/widgets.css'
export { DASHBOARD_META, DEMO_UPDATED_AT } from './data'
const delta = (value: number, previous: number) => (previous ? (value - previous) / previous : 0)
const columns: DataColumn<ServiceRow>[] = [
  {
    key: 'name',
    label: 'Servizio',
    render: (row) => <strong>{row.name}</strong>,
    sortValue: (row) => row.name
  },
  { key: 'region', label: 'Regione', render: (row) => row.region, sortValue: (row) => row.region },
  {
    key: 'status',
    label: 'Stato attuale',
    render: (row) => <StatusBadge tone={row.status} label={row.statusLabel} />,
    sortValue: (row) => row.incidents
  },
  {
    key: 'requests',
    label: 'Richieste (req)',
    numeric: true,
    render: (row) => `${formatNumber(row.requests)} req`,
    sortValue: (row) => row.requests
  },
  {
    key: 'latency',
    label: 'Latenza p95 (ms)',
    numeric: true,
    render: (row) => `${formatNumber(row.latency)} ms`,
    sortValue: (row) => row.latency
  },
  {
    key: 'errors',
    label: 'Errori (%)',
    numeric: true,
    render: (row) => formatPercent(row.errorRate, 2),
    sortValue: (row) => row.errorRate
  },
  {
    key: 'incidents',
    label: 'Incidenti aperti (n)',
    numeric: true,
    render: (row) => formatNumber(row.incidents),
    sortValue: (row) => row.incidents
  }
]
export function DashboardPage({ scenario }: { scenario: DemoScenario }) {
  const [filters, setFilters] = useState<DashboardFilters>({ ...DEFAULT_FILTERS })
  const [response, setResponse] = useState<DashboardResponse>({
    state: 'loading',
    message: 'Caricamento metriche'
  })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let cancelled = false
    fetchDashboard(filters, scenario)
      .then((result) => {
        if (!cancelled) setResponse(result)
      })
      .catch(() => {
        if (!cancelled)
          setResponse({ state: 'error', message: 'Errore imprevisto nel caricamento demo' })
      })
    return () => {
      cancelled = true
    }
  }, [filters, scenario, attempt])
  const retry = () => {
    setResponse({ state: 'loading', message: 'Caricamento metriche' })
    setAttempt((value) => value + 1)
  }
  const updateFilters = (next: DashboardFilters) => {
    setResponse({ state: 'loading', message: 'Caricamento metriche' })
    setFilters(next)
  }
  const state = scenario === 'data' ? response.state : scenario
  const data = state === 'data' && response.state === 'data' ? response.data : null
  const period = PERIOD_LABELS[filters.period]
  const metrics = data?.metrics
  const previous = data?.previous
  const lineDelta = metrics && previous ? delta(metrics.requests, previous.requests) : 0
  const trend = lineDelta === 0 ? 'stabili' : lineDelta > 0 ? 'in aumento' : 'in calo'
  const common = { period, state, onRetry: retry }
  // One polite announcer for the whole page; widgets render their states silently. Errors are
  // announced once by the assertive alert below.
  const announcement =
    state === 'loading'
      ? 'Caricamento metriche in corso'
      : state === 'empty'
        ? 'Nessun risultato per i filtri selezionati'
        : state === 'data' && data
          ? `Metriche aggiornate: ${formatNumber(data.rows.length)} servizi · ${period}`
          : ''
  return (
    <div className="sd-dashboard">
      <FilterBar filters={filters} onChange={updateFilters} />
      <p className="sd-visually-hidden" role="status" aria-live="polite">
        {announcement}
      </p>
      <div className="sd-demo-context">
        <span>
          <Activity aria-hidden="true" /> Dati demo · piattaforma SaaS fittizia
        </span>
        <span>Finestra fino al 22 ott 2026, 20:00 CEST</span>
      </div>
      {state === 'error' && (
        <div className="sd-dashboard-alert" role="alert">
          <span>
            {response.state === 'error'
              ? response.message
              : 'Il servizio demo non è raggiungibile. Riprova.'}
          </span>
          <Button onClick={retry}>Riprova</Button>
        </div>
      )}
      <div className="sd-dashboard-grid">
        <div className="sd-kpi-slot">
          <KpiCard
            label="Richieste"
            value={metrics ? formatNumber(metrics.requests) : '—'}
            unit="req"
            period={period}
            delta={metrics && previous ? delta(metrics.requests, previous.requests) : 0}
            sparkline={data?.timeline.map((point) => point.value)}
            state={state}
          />
        </div>
        <div className="sd-kpi-slot">
          <KpiCard
            label="Latenza p95"
            value={metrics ? formatNumber(metrics.latency) : '—'}
            unit="ms"
            period={period}
            delta={metrics && previous ? delta(metrics.latency, previous.latency) : 0}
            higherIsBetter={false}
            state={state}
          />
        </div>
        <div className="sd-kpi-slot">
          <KpiCard
            label="Tasso di errore"
            value={
              metrics
                ? formatNumber(metrics.errorRate * 100, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })
                : '—'
            }
            unit="%"
            period={period}
            delta={metrics && previous ? delta(metrics.errorRate, previous.errorRate) : 0}
            higherIsBetter={false}
            state={state}
          />
        </div>
        <div className="sd-kpi-slot">
          <KpiCard
            label="Incidenti aperti"
            value={metrics ? formatNumber(metrics.incidents) : '—'}
            unit="incidenti"
            period={`Al termine · ${period.toLocaleLowerCase('it-IT')}`}
            delta={metrics && previous ? delta(metrics.incidents, previous.incidents) : 0}
            higherIsBetter={false}
            state={state}
          />
        </div>
        <ChartCard
          {...common}
          className="sd-trend-slot"
          title="Traffico della piattaforma"
          legend={[
            { label: 'Periodo selezionato', style: 'primary' },
            { label: 'Periodo precedente', style: 'comparison' }
          ]}
          summary={`Richieste ${trend} ${lineDelta ? `del ${formatPercent(Math.abs(lineDelta))}` : ''} rispetto al periodo precedente. Totale: ${formatNumber(metrics?.requests ?? 0)} req.`}
          table={
            <table>
              <caption>
                Richieste · {period}. Date di inizio degli intervalli; confronto con intervalli
                corrispondenti del periodo precedente.
              </caption>
              <thead>
                <tr>
                  <th scope="col">Intervallo</th>
                  <th scope="col">Attuale (req)</th>
                  <th scope="col">Precedente (req)</th>
                </tr>
              </thead>
              <tbody>
                {data?.timeline.map((point) => (
                  <tr key={point.fullLabel}>
                    <th scope="row">{point.fullLabel}</th>
                    <td>{formatNumber(point.value)}</td>
                    <td>{formatNumber(point.comparison)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          }
        >
          <LineChart points={data?.timeline ?? []} />
        </ChartCard>
        <ChartCard
          {...common}
          className="sd-distribution-slot"
          title="Traffico per regione"
          legend={(
            data?.distribution ?? [{ label: 'Europa' }, { label: 'America' }, { label: 'Asia' }]
          ).map((point, index) => ({
            label: point.label,
            style: (['primary', 'comparison', 'third'] as const)[index]
          }))}
          summary={`Le regioni ripartiscono tutte le ${formatNumber(metrics?.requests ?? 0)} req del periodo selezionato.`}
          table={
            <table>
              <caption>Richieste per regione · {period}</caption>
              <thead>
                <tr>
                  <th scope="col">Regione</th>
                  <th scope="col">Richieste (req)</th>
                  <th scope="col">Quota (%)</th>
                </tr>
              </thead>
              <tbody>
                {data?.distribution.map((point) => (
                  <tr key={point.label}>
                    <th scope="row">{point.label}</th>
                    <td>{formatNumber(point.value)}</td>
                    <td>{formatPercent(metrics?.requests ? point.value / metrics.requests : 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          }
        >
          <DistributionChart points={data?.distribution ?? []} />
        </ChartCard>
        <ChartCard
          {...common}
          className="sd-comparison-slot"
          title="Richieste per servizio"
          legend={[{ label: 'Richieste · req', style: 'primary' }]}
          summary={`${data?.rows.length ?? 0} servizi nel periodo. I valori corrispondono alle righe della tabella di dettaglio.`}
          table={
            <table>
              <caption>Richieste per servizio · {period}</caption>
              <thead>
                <tr>
                  <th scope="col">Servizio</th>
                  <th scope="col">Richieste (req)</th>
                </tr>
              </thead>
              <tbody>
                {data?.comparison.map((point) => (
                  <tr key={point.label}>
                    <th scope="row">{point.label}</th>
                    <td>{formatNumber(point.value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          }
        >
          <BarChart points={data?.comparison ?? []} />
        </ChartCard>
        <aside className="sd-method-slot sd-panel">
          <CircleHelp aria-hidden="true" />
          <h2>Come leggere i segnali</h2>
          <p>
            Le richieste sono conteggi assoluti. Il tasso di errore è il rapporto tra richieste
            fallite e richieste totali.
          </p>
          <p>
            La latenza p95 è calcolata dall’istogramma aggregato delle richieste, senza mediare i
            percentili dei servizi.
          </p>
          <p>
            Gli incidenti aperti sono una fotografia a fine finestra. Il delta confronta la
            fotografia precedente.
          </p>
          <span className="sd-method-label">Simulazione deterministica · nessun dato reale</span>
        </aside>
        <section className="sd-detail-slot sd-panel" aria-labelledby="sd-services-heading">
          <div className="sd-detail-heading">
            <div>
              <h2 id="sd-services-heading">Dettaglio servizi</h2>
              <p>{period} · stessi filtri di KPI e grafici</p>
            </div>
            <StatusBadge tone="neutral" label="Dati demo" />
          </div>
          <DataTable
            key={`${filters.search}-${filters.region}-${filters.service}-${filters.period}-${scenario}`}
            rows={data?.rows ?? []}
            columns={columns}
            rowKey={(row) => row.id}
            rowLabel={(row) => row.name}
            caption={`Metriche per servizio · ${period}. Incidenti: fotografia al termine della finestra.`}
            state={state}
            onRetry={retry}
          />
        </section>
      </div>
    </div>
  )
}
