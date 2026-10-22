import { useEffect, useState } from 'react'
import { Activity, ClipboardList, FileSearch, FileText, MessageCircleQuestion, Package, Workflow } from 'lucide-react'
import { fmt, messages } from './i18n'
import { DASHBOARD_META, DashboardPage } from './demo/DashboardPage'
import { DEMO_SCENARIOS } from './demo/scenario'
import type { DemoScenario } from './demo/scenario'
import { AppShell, PageHeader, SidebarNav } from './shell'
import type { NavGroup } from './shell'
import { PendingSection } from './sections/PendingSection'
import { Select, StatusBadge } from './ui'

const NAV: NavGroup[] = [
  {
    id: 'demo',
    label: messages.shell.groups.demo,
    items: [{ id: 'overview', label: messages.shell.nav.overview, icon: Activity }],
  },
  {
    id: 'core',
    label: messages.shell.groups.core,
    items: [
      { id: 'cases', label: messages.shell.nav.cases, icon: ClipboardList },
      { id: 'sources', label: messages.shell.nav.sources, icon: FileSearch },
      { id: 'reports', label: messages.shell.nav.reports, icon: FileText },
      { id: 'modules', label: messages.shell.nav.modules, icon: Workflow },
    ],
  },
  {
    id: 'should',
    label: messages.shell.groups.should,
    items: [
      { id: 'products', label: messages.shell.nav.products, icon: Package },
      { id: 'clarifications', label: messages.shell.nav.clarifications, icon: MessageCircleQuestion },
    ],
  },
]

const ROUTES = {
  overview: 'panoramica',
  cases: 'casi',
  sources: 'fonti',
  reports: 'report',
  modules: 'pipeline',
  products: 'prodotti',
  clarifications: 'chiarimenti',
} as const

type SectionId = keyof typeof ROUTES
const idFromHash = (): SectionId => {
  const slug = window.location.hash.replace(/^#\/?/, '')
  return (Object.entries(ROUTES).find(([, route]) => route === slug)?.[0] as SectionId | undefined) ?? 'overview'
}
const pathFor = (id: string) => ROUTES[id as SectionId] ?? ROUTES.overview
const titleOf = (id: string) => NAV.flatMap(group => group.items).find(item => item.id === id)?.label ?? messages.shell.nav.overview
const SCENARIO_OPTIONS = DEMO_SCENARIOS.map(option => ({
  ...option,
  label: fmt(messages.shell.controls.scenarioOption, { scenario: option.label }),
}))

export default function App() {
  const [currentId, setCurrentId] = useState<SectionId>(idFromHash)
  const [scenario, setScenario] = useState<DemoScenario>('data')

  useEffect(() => {
    const syncRoute = () => setCurrentId(idFromHash())
    if (!window.location.hash) window.history.replaceState(null, '', `#/${pathFor(currentId)}`)
    window.addEventListener('hashchange', syncRoute)
    window.addEventListener('popstate', syncRoute)
    return () => {
      window.removeEventListener('hashchange', syncRoute)
      window.removeEventListener('popstate', syncRoute)
    }
  }, [currentId])

  const navigate = (id: string) => {
    const nextId = id as SectionId
    if (!(nextId in ROUTES)) return
    if (nextId !== currentId) window.history.pushState(null, '', `#/${pathFor(nextId)}`)
    setCurrentId(nextId)
  }

  const sectionKey = currentId === 'overview' ? null : currentId
  const section = sectionKey ? messages.sections.items.find(item => item.id === sectionKey) ?? null : null

  return (
    <AppShell
      brand={messages.shell.brand}
      sidebar={
        <SidebarNav
          label={messages.shell.navigationLabel}
          groups={NAV}
          currentId={currentId}
          onNavigate={navigate}
        />
      }
      sidebarFooter={<span>{messages.shell.environment}</span>}
      topbar={
        <div className="sd-shell__view-controls">
          {/* Placeholder for the run / as_of selector (WEB-01); hidden on phones, where it only costs space. */}
          <div className="sd-shell__run">
            <Select
              label={messages.shell.controls.runLabel}
              hideLabel
              size="sm"
              disabled
              value=""
              options={[{ value: '', label: messages.shell.controls.runPlaceholder }]}
              onValueChange={() => undefined}
            />
          </div>
          {currentId === 'overview' && (
            <Select
              label={messages.shell.controls.scenarioLabel}
              hideLabel
              size="sm"
              value={scenario}
              options={SCENARIO_OPTIONS}
              onValueChange={value => setScenario(value as DemoScenario)}
            />
          )}
          <StatusBadge
            tone={currentId === 'overview' ? 'neutral' : 'info'}
            label={currentId === 'overview' ? messages.shell.controls.modeSynthetic : messages.shell.controls.modeUnavailable}
          />
        </div>
      }
    >
      {currentId === 'overview' ? (
        <>
          <PageHeader title={messages.shell.nav.overview} subtitle={messages.shell.overview.subtitle} meta={DASHBOARD_META} />
          <DashboardPage scenario={scenario} />
        </>
      ) : section ? (
        <>
          <PageHeader title={titleOf(currentId)} />
          <PendingSection section={section} />
        </>
      ) : null}
    </AppShell>
  )
}
