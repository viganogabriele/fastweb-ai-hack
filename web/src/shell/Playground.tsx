import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Activity, Layers } from 'lucide-react'
import { AppShell, PageHeader, SidebarNav } from './index'
import { Button, Input, Select, StatusBadge } from '../ui'
import { fmt, messages } from '../i18n'
import '../design/tokens.css'
import '../design/local.css'

export function Playground() {
  const [currentId, setCurrentId] = useState('overview')
  return (
    <AppShell
      brand={messages.shell.brand}
      sidebar={<SidebarNav label={messages.shell.playground.navigationLabel} currentId={currentId} onNavigate={setCurrentId} groups={[
        { id: 'monitor', label: messages.shell.playground.group, items: [
          { id: 'overview', label: messages.shell.playground.overview, icon: Activity },
          { id: 'sources', label: messages.shell.playground.sources, icon: Layers },
        ] },
      ]} />}
      sidebarFooter={<span>{messages.shell.playground.footer}</span>}
      topbar={<Button>{messages.shell.playground.topbar}</Button>}
    >
      <PageHeader title={currentId === 'overview' ? messages.shell.playground.overview : messages.shell.playground.sources} subtitle={messages.shell.playground.subtitle} meta={<StatusBadge tone="neutral" label={messages.shell.playground.demoData} />} actions={<><Button>{messages.shell.playground.refresh}</Button><Button variant="primary">{messages.shell.playground.export}</Button></>}>
        <Input label={messages.shell.playground.search} placeholder={messages.shell.playground.searchPlaceholder} />
        <Select label={messages.shell.playground.period} options={[{ value: 'week', label: messages.shell.playground.periodLastWeek }]} onValueChange={() => undefined} />
      </PageHeader>
      {Array.from({ length: 24 }, (_, index) => <p key={index}>{fmt(messages.shell.playground.activity, { number: index + 1 })} {messages.shell.playground.periodLastWeek}</p>)}
    </AppShell>
  )
}

createRoot(document.getElementById('root')!).render(<StrictMode><Playground /></StrictMode>)
