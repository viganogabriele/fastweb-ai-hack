export type Period = '24h' | '7d' | '30d'
export interface DashboardFilters {
  search: string
  period: Period
  region: string
  service: string
}
export const DEFAULT_FILTERS: DashboardFilters = {
  search: '',
  period: '30d',
  region: 'all',
  service: 'all'
}
import { LOCALE, fmt, messages } from '../i18n'
export const PERIOD_LABELS: Record<Period, string> = messages.dashboard.filters.periods
export const DEMO_UPDATED_AT = '2026-10-22T18:00:00Z'
export const DASHBOARD_META = fmt(messages.dashboard.context.updatedAt, {
  date: new Intl.DateTimeFormat(LOCALE, {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Europe/Rome'
  }).format(new Date(DEMO_UPDATED_AT))
})
export interface Service {
  id: string
  name: string
  region: string
  incidents: number
  previousIncidents: number
}
export const SERVICES: Service[] = [
  { id: 'gateway', name: 'API Gateway', region: messages.dashboard.filters.regions.europe, incidents: 0, previousIncidents: 1 },
  { id: 'identity', name: 'Identity', region: messages.dashboard.filters.regions.europe, incidents: 0, previousIncidents: 0 },
  { id: 'payments', name: 'Payments', region: messages.dashboard.filters.regions.europe, incidents: 1, previousIncidents: 2 },
  { id: 'storage', name: 'Object Storage', region: messages.dashboard.filters.regions.america, incidents: 0, previousIncidents: 0 },
  { id: 'search', name: 'Search', region: messages.dashboard.filters.regions.america, incidents: 1, previousIncidents: 1 },
  { id: 'notifications', name: 'Notifications', region: messages.dashboard.filters.regions.asia, incidents: 0, previousIncidents: 1 }
]
const LATENCIES = [60, 90, 120, 180, 240, 320, 480]
interface Observation {
  timestamp: number
  serviceId: string
  requests: number
  errors: number
  histogram: number[]
}
export interface Metrics {
  requests: number
  errors: number
  errorRate: number
  latency: number
  incidents: number
}
export interface ServiceRow extends Service, Metrics {
  status: 'success' | 'warning' | 'danger'
  statusLabel: string
}
export interface TimePoint {
  label: string
  fullLabel: string
  value: number
  comparison: number
}
export interface CategoryPoint {
  label: string
  value: number
}
export interface DashboardData {
  period: string
  metrics: Metrics
  previous: Metrics
  rows: ServiceRow[]
  timeline: TimePoint[]
  distribution: CategoryPoint[]
  comparison: CategoryPoint[]
}
const HOUR = 3_600_000
const END = Date.parse(DEMO_UPDATED_AT)
// Fixed integer seed: the same filters always produce the same observations.
const observations: Observation[] = Array.from({ length: 60 * 24 }, (_, hour) =>
  SERVICES.map((service, index) => {
    const seed = (hour * 173 + index * 997 + 41) % 1009
    const requests = 1800 + index * 310 + seed * 3 + Math.round(700 * (1 + Math.sin(hour / 24)))
    const errors = Math.floor(requests * (index === 2 ? 0.008 : 0.001 + index * 0.0003))
    // Per-service tail so services differ; the older 30 days are slower, so deltas are visible.
    const tail = (hour < 30 * 24 ? 0.065 : 0.022) + index * 0.006
    const weights = [0.15, 0.24, 0.28, 0.2 - tail, 0.11, tail, 0.02]
    const histogram = weights.map((weight) => Math.floor(requests * weight))
    histogram[0] += requests - histogram.reduce((sum, value) => sum + value, 0)
    return {
      timestamp: END - (60 * 24 - hour) * HOUR,
      serviceId: service.id,
      requests,
      errors,
      histogram
    }
  })
).flat()
function aggregate(records: Observation[], incidents: number): Metrics {
  const requests = records.reduce((sum, row) => sum + row.requests, 0)
  const errors = records.reduce((sum, row) => sum + row.errors, 0)
  const histogram = LATENCIES.map((_, index) =>
    records.reduce((sum, row) => sum + row.histogram[index], 0)
  )
  // p95 interpolated linearly inside the histogram bin that crosses 95% (bins are upper bounds).
  const target = requests * 0.95
  let cumulative = 0
  let p95 = 0
  for (const [index, count] of histogram.entries()) {
    if (count > 0 && cumulative + count >= target) {
      const lower = index ? LATENCIES[index - 1] : 0
      p95 = Math.round(lower + ((target - cumulative) / count) * (LATENCIES[index] - lower))
      break
    }
    cumulative += count
  }
  return { requests, errors, errorRate: requests ? errors / requests : 0, latency: p95, incidents }
}
export function buildDashboard(filters: DashboardFilters): DashboardData {
  const hours = filters.period === '24h' ? 24 : filters.period === '7d' ? 168 : 720
  const services = SERVICES.filter(
    (service) =>
      (filters.region === 'all' || service.region === filters.region) &&
      (filters.service === 'all' || service.id === filters.service) &&
      `${service.name} ${service.region}`
        .toLocaleLowerCase(LOCALE)
        .includes(filters.search.trim().toLocaleLowerCase(LOCALE))
  )
  const ids = new Set(services.map((service) => service.id))
  const selected = observations.filter((row) => ids.has(row.serviceId))
  const current = selected.filter((row) => row.timestamp >= END - hours * HOUR)
  const previous = selected.filter(
    (row) => row.timestamp >= END - 2 * hours * HOUR && row.timestamp < END - hours * HOUR
  )
  const rows: ServiceRow[] = services.map((service) => ({
    ...service,
    ...aggregate(
      current.filter((row) => row.serviceId === service.id),
      service.incidents
    ),
    status: service.incidents ? 'warning' : 'success',
    statusLabel: service.incidents ? messages.dashboard.statuses.warning : messages.dashboard.statuses.success
  }))
  const bins = filters.period === '24h' ? 24 : filters.period === '7d' ? 7 : 30
  const timeline = Array.from({ length: bins }, (_, index) => {
    const start = END - hours * HOUR + ((index * hours) / bins) * HOUR
    const finish = start + (hours / bins) * HOUR
    const date = new Date(start)
    return {
      label: new Intl.DateTimeFormat(
        LOCALE,
        filters.period === '24h'
          ? { hour: '2-digit', timeZone: 'Europe/Rome' }
          : { day: 'numeric', month: 'short', timeZone: 'Europe/Rome' }
      ).format(date),
      fullLabel: new Intl.DateTimeFormat(LOCALE, {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'Europe/Rome'
      }).format(date),
      value: current
        .filter((row) => row.timestamp >= start && row.timestamp < finish)
        .reduce((sum, row) => sum + row.requests, 0),
      comparison: previous
        .filter(
          (row) => row.timestamp >= start - hours * HOUR && row.timestamp < finish - hours * HOUR
        )
        .reduce((sum, row) => sum + row.requests, 0)
    }
  })
  return {
    period: PERIOD_LABELS[filters.period],
    rows,
    timeline,
    metrics: aggregate(
      current,
      services.reduce((sum, service) => sum + service.incidents, 0)
    ),
    previous: aggregate(
      previous,
      services.reduce((sum, service) => sum + service.previousIncidents, 0)
    ),
    distribution: [messages.dashboard.filters.regions.europe, messages.dashboard.filters.regions.america, messages.dashboard.filters.regions.asia]
      .map((label) => ({
        label,
        value: rows
          .filter((row) => row.region === label)
          .reduce((sum, row) => sum + row.requests, 0)
      }))
      .filter((row) => row.value > 0),
    comparison: rows
      .map((row) => ({ label: row.name, value: row.requests }))
      .sort((a, b) => b.value - a.value)
  }
}
