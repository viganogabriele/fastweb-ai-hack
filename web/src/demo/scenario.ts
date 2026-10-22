export type DemoScenario = 'data' | 'loading' | 'empty' | 'error'

export const DEMO_SCENARIOS: { value: DemoScenario; label: string }[] = [
  { value: 'data', label: 'Dati disponibili' },
  { value: 'loading', label: 'Caricamento' },
  { value: 'empty', label: 'Nessun risultato' },
  { value: 'error', label: 'Errore' }
]
