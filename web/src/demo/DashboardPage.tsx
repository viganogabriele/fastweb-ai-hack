import { useEffect, useState } from 'react'
import { CircleHelp } from 'lucide-react'
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
import { fmt, messages } from '../i18n'
import '../widgets/widgets.css'
export { DASHBOARD_META, DEMO_UPDATED_AT } from './data'
const delta = (value: number, previous: number) => (previous ? (value - previous) / previous : 0)
const columns: DataColumn<ServiceRow>[] = [
  {
    key: 'name',
    label: messages.dashboard.table.service,
    render: (row) => <strong>{row.name}</strong>,
    sortValue: (row) => row.name
  },
  { key: 'region', label: messages.dashboard.table.region, render: (row) => row.region, sortValue: (row) => row.region },
  {
    key: 'status',
    label: messages.dashboard.table.status,
    render: (row) => <StatusBadge tone={row.status} label={row.statusLabel} />,
    sortValue: (row) => row.incidents
  },
  {
    key: 'requests',
    label: messages.dashboard.table.requests,
    numeric: true,
    render: (row) => `${formatNumber(row.requests)} ${messages.dashboard.metrics.requestUnit}`,
    sortValue: (row) => row.requests
  },
  {
    key: 'latency',
    label: messages.dashboard.table.latency,
    numeric: true,
    render: (row) => `${formatNumber(row.latency)} ${messages.dashboard.metrics.milliseconds}`,
    sortValue: (row) => row.latency
  },
  {
    key: 'errors',
    label: messages.dashboard.table.errors,
    numeric: true,
    render: (row) => formatPercent(row.errorRate, 2),
    sortValue: (row) => row.errorRate
  },
  {
    key: 'incidents',
    label: messages.dashboard.table.incidents,
    numeric: true,
    render: (row) => formatNumber(row.incidents),
    sortValue: (row) => row.incidents
  }
]
export function DashboardPage({ scenario }: { scenario: DemoScenario }) {
  const [filters, setFilters] = useState<DashboardFilters>({ ...DEFAULT_FILTERS })
  const [response, setResponse] = useState<DashboardResponse>({
    state: 'loading',
    message: messages.dashboard.states.loading
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
          setResponse({ state: 'error', message: messages.dashboard.states.unexpectedError })
      })
    return () => {
      cancelled = true
    }
  }, [filters, scenario, attempt])
  const retry = () => {
    setResponse({ state: 'loading', message: messages.dashboard.states.loading })
    setAttempt((value) => value + 1)
  }
  const updateFilters = (next: DashboardFilters) => {
    setResponse({ state: 'loading', message: messages.dashboard.states.loading })
    setFilters(next)
  }
  const state = scenario === 'data' ? response.state : scenario
  const data = state === 'data' && response.state === 'data' ? response.data : null
  const period = PERIOD_LABELS[filters.period]
  const metrics = data?.metrics
  const previous = data?.previous
  const lineDelta = metrics && previous ? delta(metrics.requests, previous.requests) : 0
  const trend = lineDelta === 0 ? messages.dashboard.trend.stable : lineDelta > 0 ? messages.dashboard.trend.up : messages.dashboard.trend.down
  const common = { state, onRetry: retry }
  // One polite announcer for the whole page; widgets render their states silently. Errors are
  // announced once by the assertive alert below.
  const announcement =
    state === 'loading'
      ? messages.dashboard.states.loadingInProgress
      : state === 'empty'
        ? messages.dashboard.states.empty
        : state === 'data' && data
          ? fmt(messages.dashboard.states.updated, { count: formatNumber(data.rows.length), period })
          : ''
  return (
    <div className="sd-dashboard">
      <FilterBar filters={filters} onChange={updateFilters} />
      <p className="sd-visually-hidden" role="status" aria-live="polite">
        {announcement}
      </p>
      {state === 'error' && (
        <div className="sd-dashboard-alert" role="alert">
          <span>
            {response.state === 'error'
              ? response.message
              : messages.dashboard.states.unreachable}
          </span>
          <Button size="sm" onClick={retry}>{messages.dashboard.states.retry}</Button>
        </div>
      )}
      <div className="sd-dashboard-grid">
        <div className="sd-kpi-slot">
          <KpiCard
            label={messages.dashboard.metrics.requests}
            value={metrics ? formatNumber(metrics.requests) : '—'}
            unit={messages.dashboard.metrics.requestUnit}
            delta={metrics && previous ? delta(metrics.requests, previous.requests) : 0}
            sparkline={data?.timeline.map((point) => point.value)}
            state={state}
          />
        </div>
        <div className="sd-kpi-slot">
          <KpiCard
            label={messages.dashboard.metrics.latency}
            value={metrics ? formatNumber(metrics.latency) : '—'}
            unit={messages.dashboard.metrics.milliseconds}
            delta={metrics && previous ? delta(metrics.latency, previous.latency) : 0}
            higherIsBetter={false}
            state={state}
          />
        </div>
        <div className="sd-kpi-slot">
          <KpiCard
            label={messages.dashboard.metrics.errorRate}
            value={
              metrics
                ? formatNumber(metrics.errorRate * 100, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })
                : '—'
            }
            unit="%"
            delta={metrics && previous ? delta(metrics.errorRate, previous.errorRate) : 0}
            higherIsBetter={false}
            state={state}
          />
        </div>
        <div className="sd-kpi-slot">
          <KpiCard
            label={messages.dashboard.metrics.incidents}
            value={metrics ? formatNumber(metrics.incidents) : '—'}
            unit={messages.dashboard.metrics.incidentUnit}
            period={messages.dashboard.data.periodEnd}
            delta={metrics && previous ? delta(metrics.incidents, previous.incidents) : 0}
            higherIsBetter={false}
            state={state}
          />
        </div>
        <ChartCard
          {...common}
          className="sd-trend-slot"
          title={messages.dashboard.charts.traffic}
          legend={[
            { label: messages.dashboard.charts.selectedPeriod, style: 'primary' },
            { label: messages.dashboard.charts.previousPeriod, style: 'comparison' }
          ]}
          summary={fmt(messages.dashboard.charts.requestTrendSummary, {
            trend,
            delta: lineDelta ? fmt(messages.dashboard.charts.deltaSuffix, { value: formatPercent(Math.abs(lineDelta)) }) : '',
            total: formatNumber(metrics?.requests ?? 0)
          })}
          table={
            <table>
              <caption>
                {fmt(messages.dashboard.charts.timelineCaption, { period })}
              </caption>
              <thead>
                <tr>
                  <th scope="col">{messages.dashboard.charts.interval}</th>
                  <th scope="col">{messages.dashboard.charts.current}</th>
                  <th scope="col">{messages.dashboard.charts.previous}</th>
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
          title={messages.dashboard.charts.byRegion}
          legend={(
            data?.distribution ?? [
              { label: messages.dashboard.filters.regions.europe },
              { label: messages.dashboard.filters.regions.america },
              { label: messages.dashboard.filters.regions.asia }
            ]
          ).map((point, index) => ({
            label: point.label,
            style: (['primary', 'comparison', 'third'] as const)[index]
          }))}
          summary={fmt(messages.dashboard.charts.regionsSummary, { total: formatNumber(metrics?.requests ?? 0) })}
          table={
            <table>
              <caption>{fmt(messages.dashboard.charts.byRegionCaption, { period })}</caption>
              <thead>
                <tr>
                  <th scope="col">{messages.dashboard.charts.region}</th>
                  <th scope="col">{messages.dashboard.charts.requestUnit}</th>
                  <th scope="col">{messages.dashboard.charts.share}</th>
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
          title={messages.dashboard.charts.byService}
          legend={[{ label: messages.dashboard.charts.unitRequestsLegend, style: 'primary' }]}
          summary={fmt(messages.dashboard.charts.servicesInPeriod, { count: data?.rows.length ?? 0 })}
          table={
            <table>
              <caption>{fmt(messages.dashboard.charts.byServiceCaption, { period })}</caption>
              <thead>
                <tr>
                  <th scope="col">{messages.dashboard.table.service}</th>
                  <th scope="col">{messages.dashboard.charts.requestUnit}</th>
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
          <h2>{messages.dashboard.method.title}</h2>
          <p>{messages.dashboard.method.requests}</p>
          <p>{messages.dashboard.method.latency}</p>
          <p>{messages.dashboard.method.incidents}</p>
        </aside>
        <section className="sd-detail-slot sd-panel" aria-labelledby="sd-services-heading">
          <div className="sd-detail-heading">
            <div>
              <h2 id="sd-services-heading">{messages.dashboard.table.detailTitle}</h2>
              <p>{fmt(messages.dashboard.table.sameFilters, { period })}</p>
            </div>
          </div>
          <DataTable
            key={`${filters.search}-${filters.region}-${filters.service}-${filters.period}-${scenario}`}
            rows={data?.rows ?? []}
            columns={columns}
            rowKey={(row) => row.id}
            rowLabel={(row) => row.name}
            caption={fmt(messages.dashboard.table.caption, { period })}
            state={state}
            onRetry={retry}
          />
        </section>
      </div>
    </div>
  )
}
