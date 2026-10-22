import { RotateCcw, Search } from 'lucide-react'
import { Button, Input, Select } from '../ui'
import { DEFAULT_FILTERS, SERVICES } from '../demo/data'
import type { DashboardFilters, Period } from '../demo/data'
import './widgets.css'
export function FilterBar({
  filters,
  onChange
}: {
  filters: DashboardFilters
  onChange: (filters: DashboardFilters) => void
}) {
  const active =
    Number(Boolean(filters.search.trim())) +
    Number(filters.period !== '30d') +
    Number(filters.region !== 'all') +
    Number(filters.service !== 'all')
  return (
    <form
      className="sd-filterbar"
      role="search"
      aria-label="Filtra metriche demo"
      onSubmit={(event) => event.preventDefault()}
    >
      <Input
        type="search"
        label="Cerca servizio"
        placeholder="Nome o regione…"
        icon={<Search />}
        value={filters.search}
        onChange={(event) => onChange({ ...filters, search: event.target.value })}
      />
      <Select
        label="Periodo"
        value={filters.period}
        onChange={(event) => onChange({ ...filters, period: event.target.value as Period })}
        options={[
          { value: '24h', label: 'Ultime 24 ore' },
          { value: '7d', label: 'Ultimi 7 giorni' },
          { value: '30d', label: 'Ultimi 30 giorni' }
        ]}
      />
      <Select
        label="Regione"
        value={filters.region}
        onChange={(event) => onChange({ ...filters, region: event.target.value })}
        options={[
          { value: 'all', label: 'Tutte le regioni' },
          ...['Europa', 'America', 'Asia'].map((value) => ({ value, label: value }))
        ]}
      />
      <Select
        label="Servizio"
        value={filters.service}
        onChange={(event) => onChange({ ...filters, service: event.target.value })}
        options={[
          { value: 'all', label: 'Tutti i servizi' },
          ...SERVICES.map((service) => ({ value: service.id, label: service.name }))
        ]}
      />
      <Button
        icon={<RotateCcw />}
        disabled={!active}
        onClick={() => onChange({ ...DEFAULT_FILTERS })}
      >
        Reimposta
      </Button>
      {/* Not a live region: the dashboard announcer reports the filtered result instead. */}
      <span className="sd-filter-count">
        {active} filtri attivi
      </span>
    </form>
  )
}
