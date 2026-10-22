import { RotateCcw, Search } from 'lucide-react'
import { Button, Input, Select } from '../ui'
import { DEFAULT_FILTERS, SERVICES } from '../demo/data'
import type { DashboardFilters, Period } from '../demo/data'
import { fmt, messages } from '../i18n'
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
  const copy = messages.dashboard.filters

  return (
    <form
      className="sd-filterbar"
      role="search"
      aria-label={copy.ariaLabel}
      onSubmit={(event) => event.preventDefault()}
    >
      <Input
        className="sd-filterbar-search"
        type="search"
        label={copy.searchLabel}
        placeholder={copy.searchPlaceholder}
        icon={<Search />}
        value={filters.search}
        onChange={(event) => onChange({ ...filters, search: event.target.value })}
      />
      <Select
        className="sd-filterbar-select"
        size="sm"
        label={copy.period}
        value={filters.period}
        onValueChange={(value) => onChange({ ...filters, period: value as Period })}
        options={Object.entries(copy.periods).map(([value, label]) => ({ value, label }))}
      />
      <Select
        className="sd-filterbar-select"
        size="sm"
        label={copy.region}
        value={filters.region}
        onValueChange={(value) => onChange({ ...filters, region: value })}
        options={[
          { value: 'all', label: copy.allRegions },
          { value: copy.regions.europe, label: copy.regions.europe },
          { value: copy.regions.america, label: copy.regions.america },
          { value: copy.regions.asia, label: copy.regions.asia }
        ]}
      />
      <Select
        className="sd-filterbar-select"
        size="sm"
        label={copy.service}
        value={filters.service}
        onValueChange={(value) => onChange({ ...filters, service: value })}
        options={[
          { value: 'all', label: copy.allServices },
          ...SERVICES.map((service) => ({ value: service.id, label: service.name }))
        ]}
      />
      <Button
        className="sd-filterbar-reset"
        variant="ghost"
        size="sm"
        icon={<RotateCcw />}
        disabled={!active}
        onClick={() => onChange({ ...DEFAULT_FILTERS })}
      >
        {active ? fmt(copy.resetWithCount, { count: active }) : copy.reset}
      </Button>
    </form>
  )
}
