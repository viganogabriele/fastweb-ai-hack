import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Activity, Layers, Settings } from 'lucide-react'
import { AppShell, PageHeader, SidebarNav } from './index'
import { Button, Input, Select, StatusBadge } from '../ui'
import '../design/tokens.css'
import '../design/local.css'

export function Playground() {
  const [currentId, setCurrentId] = useState('overview')
  return (
    <AppShell
      brand="Signal Dark"
      sidebar={<SidebarNav label="Navigazione principale" currentId={currentId} onNavigate={setCurrentId} groups={[
        { id: 'monitor', label: 'Monitoraggio', items: [
          { id: 'overview', label: 'Panoramica', icon: Activity },
          { id: 'sources', label: 'Sorgenti', icon: Layers, badge: '12' },
        ] },
        { id: 'workspace', label: 'Area di lavoro', items: [{ id: 'settings', label: 'Impostazioni', icon: Settings, disabled: true }] },
      ]} />}
      sidebarFooter={<span>Ambiente dimostrativo</span>}
      topbar={<Button>Area demo</Button>}
    >
      <PageHeader title={currentId === 'overview' ? 'Panoramica' : 'Sorgenti'} subtitle="Metriche e attività del tuo ambiente, ultimi 7 giorni." meta={<StatusBadge tone="neutral" label="Dati demo" />} actions={<><Button>Aggiorna</Button><Button variant="primary">Esporta</Button></>}>
        <Input label="Cerca attività" placeholder="Nome o sorgente" />
        <Select label="Periodo" options={[{ value: 'week', label: 'Ultimi 7 giorni' }]} />
      </PageHeader>
      {Array.from({ length: 24 }, (_, index) => <p key={index}>Attività demo {index + 1} · Ultimi 7 giorni</p>)}
    </AppShell>
  )
}

createRoot(document.getElementById('root')!).render(<StrictMode><Playground /></StrictMode>)
