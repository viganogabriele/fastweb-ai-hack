import { buildDashboard } from './data'
import type { DashboardData, DashboardFilters } from './data'
import type { DemoScenario } from './scenario'
export type DashboardResponse =
  { state: 'data'; data: DashboardData } | { state: 'loading' | 'empty' | 'error'; message: string }
export async function fetchDashboard(
  filters: DashboardFilters,
  scenario: DemoScenario
): Promise<DashboardResponse> {
  await new Promise((resolve) => setTimeout(resolve, 360))
  if (scenario === 'loading')
    return { state: 'loading', message: 'Recupero delle metriche demo in corso' }
  if (scenario === 'empty')
    return { state: 'empty', message: 'Nessun servizio corrisponde ai filtri' }
  if (scenario === 'error')
    return { state: 'error', message: 'Il servizio demo non è raggiungibile. Riprova.' }
  const data = buildDashboard(filters)
  return data.rows.length
    ? { state: 'data', data }
    : { state: 'empty', message: 'Nessun servizio corrisponde ai filtri' }
}
