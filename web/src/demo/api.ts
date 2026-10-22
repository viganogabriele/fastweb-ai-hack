import { buildDashboard } from './data'
import type { DashboardData, DashboardFilters } from './data'
import type { DemoScenario } from './scenario'
import { messages } from '../i18n'
export type DashboardResponse =
  { state: 'data'; data: DashboardData } | { state: 'loading' | 'empty' | 'error'; message: string }
export async function fetchDashboard(
  filters: DashboardFilters,
  scenario: DemoScenario
): Promise<DashboardResponse> {
  await new Promise((resolve) => setTimeout(resolve, 360))
  if (scenario === 'loading')
    return { state: 'loading', message: messages.dashboard.states.fetching }
  if (scenario === 'empty')
    return { state: 'empty', message: messages.dashboard.states.noMatch }
  if (scenario === 'error')
    return { state: 'error', message: messages.dashboard.states.unreachable }
  const data = buildDashboard(filters)
  return data.rows.length
    ? { state: 'data', data }
    : { state: 'empty', message: messages.dashboard.states.noMatch }
}
