import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { AnimatePresence, MotionConfig, motion, useReducedMotion } from 'motion/react'
import { Activity, ClipboardList, FileSearch, FileText, MessageCircleQuestion, Package, Workflow } from 'lucide-react'
import { fmt, messages } from './i18n'
import { DASHBOARD_META, DashboardPage } from './demo/DashboardPage'
import { DEMO_SCENARIOS } from './demo/scenario'
import type { DemoScenario } from './demo/scenario'
import { AppShell, PageHeader, SidebarNav } from './shell'
import type { NavGroup } from './shell'
import { PendingSection } from './sections/PendingSection'
import { Select, StatusBadge } from './ui'
import { transition } from './ui/motion'

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

function SectionView({ currentId, focusOnMount, children }: { currentId: SectionId; focusOnMount: boolean; children: ReactNode }) {
  const reduceMotion = useReducedMotion()
  useEffect(() => {
    if (focusOnMount) document.querySelector<HTMLElement>('.sd-page-header__title')?.focus({ preventScroll: true })
  }, [focusOnMount])
  const offset = reduceMotion ? 0 : 5
  return (
    // No exit: the old view leaves at once, so a click never shows an empty frame between views.
    <motion.div key={currentId} className="sd-shell__view" initial={{ opacity: 0, y: offset }} animate={{ opacity: 1, y: 0 }} transition={transition.view}>
      {children}
    </motion.div>
  )
}

export default function App() {
  const [currentId, setCurrentId] = useState<SectionId>(idFromHash)
  const [focusRouteId, setFocusRouteId] = useState<SectionId | null>(null)
  const [scenario, setScenario] = useState<DemoScenario>('data')

  useEffect(() => {
    const syncRoute = () => {
      const nextId = idFromHash()
      setCurrentId(nextId)
      setFocusRouteId(nextId)
    }
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
    if (nextId !== currentId) {
      window.history.pushState(null, '', `#/${pathFor(nextId)}`)
      setFocusRouteId(nextId)
    }
    setCurrentId(nextId)
  }

  const sectionKey = currentId === 'overview' ? null : currentId
  const section = sectionKey ? messages.sections.items.find(item => item.id === sectionKey) ?? null : null

  return (
    <MotionConfig reducedMotion="user">
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
          <AnimatePresence initial={false} mode="popLayout">
            {currentId === 'overview' && (
              <motion.div key="scenario" layout className="sd-shell__control-slot" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: transition.exit }} transition={transition.popover}>
                <Select
                  label={messages.shell.controls.scenarioLabel}
                  hideLabel
                  size="sm"
                  value={scenario}
                  options={SCENARIO_OPTIONS}
                  onValueChange={value => setScenario(value as DemoScenario)}
                />
              </motion.div>
            )}
          </AnimatePresence>
          <AnimatePresence initial={false} mode="popLayout">
            <motion.div key={currentId === 'overview' ? 'synthetic' : 'unavailable'} layout className="sd-shell__mode-slot" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: transition.exit }} transition={transition.popover}>
              <StatusBadge
                tone={currentId === 'overview' ? 'neutral' : 'info'}
                label={currentId === 'overview' ? messages.shell.controls.modeSynthetic : messages.shell.controls.modeUnavailable}
              />
            </motion.div>
          </AnimatePresence>
        </div>
      }
    >
      {/* Back/forward uses the same short entrance: navigation is occasional and the cue confirms the hash change. */}
      <SectionView key={currentId} currentId={currentId} focusOnMount={focusRouteId === currentId}>
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
      </SectionView>
    </AppShell>
    </MotionConfig>
  )
}
