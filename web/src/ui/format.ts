const LOCALE = 'it-IT'

export function formatNumber(n: number, opts?: Intl.NumberFormatOptions): string {
  return new Intl.NumberFormat(LOCALE, opts).format(n)
}

export function formatPercent(fraction: number, digits = 1): string {
  return new Intl.NumberFormat(LOCALE, {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(fraction)
}

export function formatDuration(ms: number): string {
  return ms < 1000 ? `${formatNumber(Math.round(ms))} ms` : `${formatNumber(ms / 1000, { maximumFractionDigits: 1 })} s`
}

export function formatDelta(fraction: number): string {
  const sign = fraction > 0 ? '+' : fraction < 0 ? '−' : '±'
  return `${sign}${formatPercent(Math.abs(fraction))}`
}
