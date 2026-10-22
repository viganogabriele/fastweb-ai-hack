import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Download, Search } from 'lucide-react'
import { Button } from './Button'
import { Input } from './Input'
import { Select } from './Select'
import { StatusBadge } from './StatusBadge'
import { EmptyState, LoadingState, ErrorState } from './FeedbackState'
import { formatDelta, formatDuration, formatNumber } from './format'
import '../design/index.css'
import './Playground.css'

export function Playground() {
  const [pressed, setPressed] = useState(false)
  const [retried, setRetried] = useState(false)
  return (
    <main className="sd-playground">
      <h1>Signal Dark · Primitivi</h1>
      <p>Dati demo · Stati e accessibilità dei controlli</p>
      <section className="sd-playground__section" aria-label="Pulsanti">
        <h2>Pulsanti</h2>
        <div className="sd-playground__row">
          {(['primary', 'secondary', 'ghost'] as const).map(variant => (
            <Button key={variant} variant={variant} icon={<Download />}>Esporta {{ primary: 'primario', secondary: 'secondario', ghost: 'discreto' }[variant]}</Button>
          ))}
          <Button size="sm">Compatto</Button>
          <Button icon={<Search />} iconOnly aria-label="Cerca eventi">Cerca eventi</Button>
          <Button pressed={pressed} onClick={() => setPressed(value => !value)}>Selezione</Button>
          <Button disabled>Non disponibile</Button>
          <Button loading>Esportazione</Button>
          <Button loading iconOnly aria-label="Aggiornamento in corso">Aggiornamento</Button>
        </div>
      </section>
      <section className="sd-playground__section" aria-label="Campi">
        <h2>Campi</h2>
        <div className="sd-playground__fields">
          <Input label="Cerca" placeholder="Cerca un evento" icon={<Search />} hint="Nome o identificativo" />
          <Input label="Soglia" defaultValue="abc" hint="Valore in millisecondi" error="Inserisci un numero valido" />
          <Input label="Identificativo" disabled defaultValue="DEMO-01" />
          <Input label="Filtro rapido" hideLabel placeholder="Filtro con etichetta nascosta" />
          <Select label="Periodo" hint="Intervallo dei dati demo" options={[{ value: 'week', label: 'Ultimi 7 giorni' }, { value: 'month', label: 'Ultimi 30 giorni' }]} />
          <Select label="Area" error="Seleziona un’area disponibile" options={[{ value: '', label: 'Seleziona area' }]} />
          <Select label="Fonte" disabled options={[{ value: 'demo', label: 'Dati demo' }]} />
        </div>
      </section>
      <section className="sd-playground__section" aria-label="Stati">
        <h2>Stati</h2>
        <div className="sd-playground__row">
          <StatusBadge tone="success" label="Operativo" count={1234} />
          <StatusBadge tone="warning" label="Attenzione" count={3} />
          <StatusBadge tone="danger" label="Errore" />
          <StatusBadge tone="info" label="In analisi" />
          <StatusBadge tone="neutral" label="Inattivo" count={0} />
        </div>
        <EmptyState title="Nessun evento" description="Modifica il periodo per trovare altri eventi." action={<Button>Azzera filtri</Button>} />
        <LoadingState label="Caricamento eventi" lines={4} />
        {retried ? <p role="status">Nuovo tentativo richiesto</p> : <ErrorState title="Dati non disponibili" description="Riprova tra qualche istante." onRetry={() => setRetried(true)} compact />}
      </section>
      <p className="sd-num">{formatNumber(12345)} eventi · {formatDuration(1240)} · {formatDelta(-0.013)}</p>
    </main>
  )
}

const root = document.getElementById('root')
if (root) createRoot(root).render(<Playground />)
