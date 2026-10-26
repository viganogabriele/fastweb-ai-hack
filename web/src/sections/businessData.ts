// Business series for the overview: daily store KPIs (EUR at budget rate) summed over the stores
// in scope. Pure functions, so the numbers on screen can be tested without rendering.

export interface KpiDay {
  date: string
  store_id: string
  available_at: string
  sales_eur: number
  budget_eur: number
  receipts: number
  visitors: number | null
  units: number
  returns_units: number
}

export interface DayPoint {
  date: string
  sales: number
  budget: number
  receipts: number
  visitors: number | null
}

export interface Totals {
  sales: number
  budget: number
  receipts: number
  visitors: number | null
  /** Sales over budget minus one; null without budget. */
  vsBudget: number | null
  /** Receipts over visitors; null without visitors. */
  conversion: number | null
}

const DAY = 86_400_000
const shift = (date: string, days: number) => new Date(Date.parse(`${date}T00:00:00Z`) + days * DAY).toISOString().slice(0, 10)

/** The calendar day after `date` (YYYY-MM-DD, UTC). */
export const nextDay = (date: string) => shift(date, 1)

/** Latest business day present in the rows, or null when there are none. */
export const lastDay = (rows: KpiDay[]) => rows.reduce<string | null>((max, row) => (max === null || row.date > max ? row.date : max), null)

/**
 * One point per calendar day for `days` days ending on `end`, summed over `stores` (all stores
 * when null). Days without rows are zero, not skipped, so the axis stays a real calendar.
 */
export function dailySeries(rows: KpiDay[], stores: Set<string> | null, days: number, end: string): DayPoint[] {
  const start = shift(end, -(days - 1))
  const byDate = new Map<string, DayPoint>()
  for (let index = 0; index < days; index++) {
    const date = shift(start, index)
    byDate.set(date, { date, sales: 0, budget: 0, receipts: 0, visitors: 0 })
  }
  for (const row of rows) {
    const point = byDate.get(row.date)
    if (!point || (stores && !stores.has(row.store_id))) continue
    point.sales += row.sales_eur
    point.budget += row.budget_eur
    point.receipts += row.receipts
    point.visitors = point.visitors === null || row.visitors === null ? null : point.visitors + row.visitors
  }
  return [...byDate.values()]
}

export function totals(points: DayPoint[]): Totals {
  const sum = points.reduce<{ sales: number; budget: number; receipts: number; visitors: number | null }>(
    (acc, point) => ({
      sales: acc.sales + point.sales,
      budget: acc.budget + point.budget,
      receipts: acc.receipts + point.receipts,
      visitors: acc.visitors === null || point.visitors === null ? null : acc.visitors + point.visitors
    }),
    { sales: 0, budget: 0, receipts: 0, visitors: 0 }
  )
  return {
    ...sum,
    vsBudget: sum.budget > 0 ? sum.sales / sum.budget - 1 : null,
    conversion: sum.visitors !== null && sum.visitors > 0 ? sum.receipts / sum.visitors : null
  }
}

/** Relative change from `before` to `after`; null when there is nothing to compare against. */
export const change = (after: number, before: number) => (before > 0 ? after / before - 1 : null)

export interface StorePerformance {
  id: string
  sales: number
  budget: number
  vsBudget: number | null
  /** Daily sales over the window, oldest first, for sparklines. */
  daily: number[]
}

export function storePerformance(rows: KpiDay[], stores: string[], days: number, end: string): StorePerformance[] {
  return stores.map((id) => {
    const series = dailySeries(rows, new Set([id]), days, end)
    const sum = totals(series)
    return { id, sales: sum.sales, budget: sum.budget, vsBudget: sum.vsBudget, daily: series.map((point) => point.sales) }
  })
}

/** Count of items per UTC day of their timestamp, for days inside the series. */
export function countByDay<T>(items: T[], timestampOf: (item: T) => string | null | undefined, dates: string[]) {
  const counts = new Map(dates.map((date) => [date, 0]))
  for (const item of items) {
    const timestamp = timestampOf(item)
    const date = timestamp ? timestamp.slice(0, 10) : null
    if (date && counts.has(date)) counts.set(date, counts.get(date)! + 1)
  }
  return counts
}

const euro = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
const euroCompact = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', notation: 'compact', maximumFractionDigits: 1 })
const percent = new Intl.NumberFormat('it-IT', { style: 'percent', maximumFractionDigits: 1, signDisplay: 'exceptZero' })
export const formatEuro = (value: number) => euro.format(value)
export const formatEuroCompact = (value: number) => euroCompact.format(value)
export const formatChange = (value: number | null) => (value === null ? '–' : percent.format(value))
