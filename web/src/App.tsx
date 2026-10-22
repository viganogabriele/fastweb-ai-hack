import { useState } from 'react'
import { Activity, BellRing, FileText, Server, Settings } from 'lucide-react'
import { DASHBOARD_META, DashboardPage } from './demo/DashboardPage'
import { DEMO_SCENARIOS } from './demo/scenario'
import type { DemoScenario } from './demo/scenario'
import { AppShell, PageHeader, SidebarNav } from './shell'
import type { NavGroup } from './shell'
import { EmptyState, Select } from './ui'

// Signal Dark demo dashboard (docs/signal-dark/). Only "Panoramica" is a working view; the other
// entries show that navigation works and are labelled as outside the demo.
const NAV: NavGroup[] = [
  {
    id: 'monitor',
    label: 'Monitoraggio',
    items: [
      { id: 'overview', label: 'Panoramica', icon: Activity },
      { id: 'services', label: 'Servizi', icon: Server },
      { id: 'incidents', label: 'Incidenti', icon: BellRing, badge: '2' },
    ],
  },
  {
    id: 'workspace',
    label: 'Area di lavoro',
    items: [
      { id: 'reports', label: 'Report', icon: FileText },
      { id: 'settings', label: 'Impostazioni', icon: Settings, disabled: true },
    ],
  },
]

// The label is visually hidden in the compact top bar, so each option carries the context.
const SCENARIO_OPTIONS = DEMO_SCENARIOS.map((o) => ({ ...o, label: `Demo: ${o.label}` }))

const titleOf = (id: string) =>
  NAV.flatMap((g) => g.items).find((item) => item.id === id)?.label ?? 'Panoramica'

export default function App() {
  const [currentId, setCurrentId] = useState('overview')
  const [scenario, setScenario] = useState<DemoScenario>('data')

  return (
    <AppShell
      brand="Signal Dark"
      sidebar={
        <SidebarNav
          label="Navigazione principale"
          groups={NAV}
          currentId={currentId}
          onNavigate={setCurrentId}
        />
      }
      sidebarFooter={<span>Ambiente dimostrativo</span>}
      topbar={
        <Select
          label="Scenario demo"
          hideLabel
          value={scenario}
          options={SCENARIO_OPTIONS}
          onChange={(e) => setScenario(e.target.value as DemoScenario)}
        />
      }
    >
      {currentId === 'overview' ? (
        <>
          <PageHeader
            title="Panoramica"
            subtitle="Traffico, latenza ed errori dei servizi della piattaforma"
            meta={DASHBOARD_META}
          />
          <DashboardPage scenario={scenario} />
        </>
      ) : (
        <>
          <PageHeader title={titleOf(currentId)} meta="Dati demo" />
          <EmptyState
            title="Vista non inclusa nella demo"
            description="Questa sezione dimostra solo la navigazione. I dati sono nella Panoramica."
          />
        </>
      )}
    </AppShell>
  )
}
