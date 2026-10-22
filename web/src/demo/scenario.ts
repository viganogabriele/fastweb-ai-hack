import { messages } from '../i18n'

export type DemoScenario = 'data' | 'loading' | 'empty' | 'error'

export const DEMO_SCENARIOS: { value: DemoScenario; label: string }[] = [
  { value: 'data', label: messages.dashboard.scenarios.data },
  { value: 'loading', label: messages.dashboard.scenarios.loading },
  { value: 'empty', label: messages.dashboard.scenarios.empty },
  { value: 'error', label: messages.dashboard.scenarios.error }
]
