import { useId, useState } from 'react'
import type { ReactNode } from 'react'
import { ArrowDown, ArrowUp, ArrowUpDown, CheckCheck } from 'lucide-react'
import { Button, EmptyState, ErrorState, LoadingState, formatNumber } from '../ui'
import type { DemoScenario } from '../demo/scenario'
import { LOCALE, fmt, messages } from '../i18n'
import './widgets.css'
export interface DataColumn<T> {
  key: string
  label: string
  numeric?: boolean
  render: (row: T) => ReactNode
  sortValue?: (row: T) => string | number
}
export interface DataTableProps<T> {
  rows: T[]
  columns: DataColumn<T>[]
  rowKey: (row: T) => string
  rowLabel: (row: T) => string
  caption: string
  state?: DemoScenario
  onRetry?: () => void
}
export function DataTable<T>({
  rows,
  columns,
  rowKey,
  rowLabel,
  caption,
  state = 'data',
  onRetry
}: DataTableProps<T>) {
  const [sort, setSort] = useState<{ key: string; ascending: boolean } | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [message, setMessage] = useState('')
  const id = useId()
  const visibleSelected = rows.filter((row) => selected.has(rowKey(row)))
  const selectedCount = visibleSelected.length
  const column = columns.find((item) => item.key === sort?.key)
  const sorted =
    column?.sortValue && sort
      ? [...rows].sort((a, b) => {
          const av = column.sortValue!(a)
          const bv = column.sortValue!(b)
          return (
            (typeof av === 'number' && typeof bv === 'number'
              ? av - bv
              : String(av).localeCompare(String(bv), LOCALE)) * (sort.ascending ? 1 : -1)
          )
        })
      : rows
  function toggle(key: string) {
    setMessage('')
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }
  if (state === 'loading') return <LoadingState label={messages.dashboard.table.loading} lines={6} announce={false} />
  if (state === 'error')
    return <ErrorState title={messages.dashboard.table.error} onRetry={onRetry} announce={false} />
  if (state === 'empty' || !rows.length)
    return (
      <EmptyState
        title={messages.dashboard.table.empty}
        description={messages.dashboard.table.emptyDescription}
      />
    )
  return (
    <div className="sd-data-table">
      {selectedCount > 0 && (
        <div className="sd-table-toolbar">
          <span>{fmt(messages.dashboard.table.selected, { count: formatNumber(selectedCount) })}</span>
          <Button
            size="sm"
            icon={<CheckCheck />}
            onClick={() => {
              setMessage(fmt(messages.dashboard.table.actionResult, { count: selectedCount }))
              setSelected(new Set())
            }}
          >
            {messages.dashboard.table.actionDemo}
          </Button>
        </div>
      )}
      <p className="sd-table-message">
        {message}
      </p>
      <div
        className="sd-table-scroll"
        role="region"
        aria-label={messages.dashboard.table.scrollLabel}
        tabIndex={0}
      >
        <table>
          <caption>{caption}</caption>
          <thead>
            <tr>
              <th scope="col">
                <label className="sd-row-check">
                <input
                  className="sd-row-checkbox"
                  type="checkbox"
                  aria-label={messages.dashboard.table.selectAll}
                  checked={selectedCount === rows.length}
                  ref={(element) => {
                    if (element)
                      element.indeterminate = selectedCount > 0 && selectedCount < rows.length
                  }}
                  onChange={(event) => {
                    setMessage('')
                    setSelected(event.target.checked ? new Set(rows.map(rowKey)) : new Set())
                  }}
                />
                </label>
              </th>
              {columns.map((item) => {
                const sortedColumn = sort?.key === item.key
                const Icon = sortedColumn ? (sort.ascending ? ArrowUp : ArrowDown) : ArrowUpDown
                return (
                  <th
                    id={`${id}-${item.key}`}
                    key={item.key}
                    scope="col"
                    className={item.numeric ? 'sd-numeric' : undefined}
                    aria-sort={
                      item.sortValue
                        ? sortedColumn
                          ? sort.ascending
                            ? 'ascending'
                            : 'descending'
                          : 'none'
                        : undefined
                    }
                  >
                    {item.sortValue ? (
                      <button
                        className="sd-sort-button"
                        onFocus={(event) =>
                          event.currentTarget.scrollIntoView({ block: 'nearest', inline: 'nearest' })
                        }
                        onClick={() =>
                          setSort({
                            key: item.key,
                            ascending: sortedColumn ? !sort.ascending : true
                          })
                        }
                      >
                        {item.label}
                        <Icon aria-hidden="true" />
                      </button>
                    ) : (
                      item.label
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => (
              <tr key={rowKey(row)} data-selected={selected.has(rowKey(row)) || undefined}>
                <td>
                  <label className="sd-row-check">
                    <input
                      className="sd-row-checkbox"
                      type="checkbox"
                      aria-label={fmt(messages.dashboard.table.selectRow, { service: rowLabel(row) })}
                      checked={selected.has(rowKey(row))}
                      onChange={() => toggle(rowKey(row))}
                    />
                  </label>
                </td>
                {columns.map((item) => (
                  <td key={item.key} className={item.numeric ? 'sd-numeric' : undefined}>
                    {item.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="sd-table-footnote">
        {fmt(messages.dashboard.table.footnote, { count: formatNumber(rows.length) })}
      </p>
    </div>
  )
}
