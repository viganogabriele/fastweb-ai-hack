import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { MotionConfig, motion, useReducedMotion } from 'motion/react'
import {
  Activity,
  ClipboardList,
  FileSearch,
  FileText,
  MessageCircleQuestion,
  Package,
  Workflow
} from 'lucide-react'
import { messages } from './i18n'
import { ModulesPage } from './sections/ModulesPage'
import { ReportsPage } from './sections/ReportsPage'
import { RunWorkspace } from './sections/RunWorkspace'
import type { Case } from './api/client'
import { DEFAULT_CASE_QUEUE_FILTERS } from './sections/caseUtils'
import type { CaseQueueFilters, CaseSelection } from './sections/caseUtils'
import { useRuns } from './api/useRuns'
import { AppShell, PageHeader, SidebarNav } from './shell'
import type { NavGroup } from './shell'
import { PendingSection } from './sections/PendingSection'
import { Select, StatusBadge } from './ui'
import { transition } from './ui/motion'

const NAV: NavGroup[] = [
  {
    id: 'overview',
    items: [
      { id: 'overview', label: messages.shell.nav.overview, icon: Activity }
    ]
  },
  {
    id: 'core',
    label: messages.shell.groups.core,
    items: [
      { id: 'cases', label: messages.shell.nav.cases, icon: ClipboardList },
      { id: 'sources', label: messages.shell.nav.sources, icon: FileSearch },
      { id: 'reports', label: messages.shell.nav.reports, icon: FileText },
      { id: 'modules', label: messages.shell.nav.modules, icon: Workflow }
    ]
  },
  {
    id: 'should',
    label: messages.shell.groups.should,
    items: [
      { id: 'products', label: messages.shell.nav.products, icon: Package },
      {
        id: 'clarifications',
        label: messages.shell.nav.clarifications,
        icon: MessageCircleQuestion
      }
    ]
  }
]

const ROUTES = {
  overview: 'panoramica',
  cases: 'casi',
  sources: 'fonti',
  reports: 'report',
  modules: 'pipeline',
  products: 'prodotti',
  clarifications: 'chiarimenti'
} as const

type SectionId = keyof typeof ROUTES
const idFromHash = (): SectionId => {
  const slug = window.location.hash.replace(/^#\/?/, '').split('/')[0]
  return (
    (Object.entries(ROUTES).find(([, route]) => route === slug)?.[0] as
      SectionId | undefined) ?? 'overview'
  )
}
const pathFor = (id: string) => ROUTES[id as SectionId] ?? ROUTES.overview
const caseSelectionFromHash = (): CaseSelection | null => {
  const [section, id, version] = window.location.hash
    .replace(/^#\/?/, '')
    .split('/')
  if (section !== ROUTES.cases || !id || !version) return null
  try {
    return { id: decodeURIComponent(id), version: decodeURIComponent(version) }
  } catch {
    return null
  }
}
const casePath = ({ id, version }: CaseSelection) =>
  `#/${pathFor('cases')}/${encodeURIComponent(id)}/${encodeURIComponent(version)}`
const titleOf = (id: string) =>
  NAV.flatMap((group) => group.items).find((item) => item.id === id)?.label ??
  messages.shell.nav.overview
function SectionView({
  currentId,
  focusOnMount,
  children
}: {
  currentId: SectionId
  focusOnMount: boolean
  children: ReactNode
}) {
  const reduceMotion = useReducedMotion()
  useEffect(() => {
    if (focusOnMount)
      document
        .querySelector<HTMLElement>('.sd-page-header__title')
        ?.focus({ preventScroll: true })
  }, [focusOnMount])
  const offset = reduceMotion ? 0 : 5
  return (
    // No exit: the old view leaves at once, so a click never shows an empty frame between views.
    <motion.div
      key={currentId}
      className="sd-shell__view"
      initial={{ opacity: 0, y: offset }}
      animate={{ opacity: 1, y: 0 }}
      transition={transition.view}
    >
      {children}
    </motion.div>
  )
}

export default function App() {
  const [currentId, setCurrentId] = useState<SectionId>(idFromHash)
  const [focusRouteId, setFocusRouteId] = useState<SectionId | null>(null)
  const [caseSelection, setCaseSelection] = useState<CaseSelection | null>(caseSelectionFromHash)
  const [caseQueueFilters, setCaseQueueFilters] = useState<CaseQueueFilters>(DEFAULT_CASE_QUEUE_FILTERS)
  const runs = useRuns()

  useEffect(() => {
    const syncRoute = () => {
      const nextId = idFromHash()
      const nextCaseSelection = caseSelectionFromHash()
      if (nextId !== currentId) setFocusRouteId(nextId)
      setCurrentId(nextId)
      setCaseSelection(nextCaseSelection)
    }
    if (!window.location.hash)
      window.history.replaceState(null, '', `#/${pathFor(currentId)}`)
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
    if (nextId === currentId && nextId === 'cases' && caseSelection) {
      window.history.pushState(null, '', `#/${pathFor('cases')}`)
      setCaseSelection(null)
      return
    }
    if (nextId !== currentId) {
      window.history.pushState(null, '', `#/${pathFor(nextId)}`)
      setFocusRouteId(nextId)
      setCaseSelection(null)
    }
    setCurrentId(nextId)
  }

  const openCase = (item: Case) => {
    const selection = { id: item.id, version: item.version }
    window.history.pushState(null, '', casePath(selection))
    setCaseSelection(selection)
  }
  const returnToQueue = () => {
    window.history.replaceState(null, '', `#/${pathFor('cases')}`)
    setCaseSelection(null)
  }

  const sectionKey = currentId === 'overview' ? null : currentId
  const section = sectionKey
    ? (messages.sections.items.find((item) => item.id === sectionKey) ?? null)
    : null

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
        topbar={
          <div className="sd-shell__view-controls">
            <Select
              label="Run e data di riferimento"
              hideLabel
              size="sm"
              disabled={!runs.items.length}
              value={runs.selectedId}
              options={
                runs.items.length
                  ? runs.items.map((run) => ({
                      value: run.spec.run_id,
                      label: `${run.spec.scenario_id} · ${new Date(run.spec.as_of).toLocaleString('it-IT')} · ${run.spec.run_id.slice(0, 8)} · ${run.status}`
                    }))
                  : [{ value: '', label: 'Nessun run disponibile' }]
              }
              onValueChange={runs.select}
            />
            <StatusBadge
              tone="neutral"
              label={
                runs.selected ? runs.selected.spec.mode : 'Non disponibile'
              }
            />
          </div>
        }
      >
        {/* Back/forward uses the same short entrance: navigation is occasional and the cue confirms the hash change. */}
        <SectionView
          key={currentId}
          currentId={currentId}
          focusOnMount={focusRouteId === currentId}
        >
          <PageHeader
            title={titleOf(currentId)}
            subtitle={
              currentId === 'overview'
                ? 'Dalle segnalazioni dei negozi alle decisioni su domanda e stock'
                : undefined
            }
            meta={
              runs.selected
                ? `Dati disponibili al ${new Date(runs.selected.spec.as_of).toLocaleString('it-IT')}`
                : undefined
            }
          />
          {currentId === 'modules' ? (
            <ModulesPage key={runs.selectedId} runs={runs} />
          ) : currentId === 'reports' ? (
            <ReportsPage runs={runs} />
          ) : ['overview', 'cases', 'sources'].includes(currentId) ? (
            <RunWorkspace
              key={`${currentId}-${runs.selectedId}`}
              section={currentId}
              runs={runs}
              caseSelection={caseSelection}
              onCaseSelect={openCase}
              onCaseReturn={returnToQueue}
              caseQueueFilters={caseQueueFilters}
              onCaseQueueFiltersChange={setCaseQueueFilters}
            />
          ) : section ? (
            <PendingSection section={section} />
          ) : null}
        </SectionView>
      </AppShell>
    </MotionConfig>
  )
}
