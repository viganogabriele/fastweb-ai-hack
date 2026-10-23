const HOUR = 3600_000

/** Compare actual instants, including timestamps with different UTC offsets. */
export function compareDeadlines(a: string | null | undefined, b: string | null | undefined) {
  const time = (value: string | null | undefined) => value && Number.isFinite(Date.parse(value)) ? Date.parse(value) : Infinity
  const left = time(a)
  const right = time(b)
  return left === right ? 0 : left - right
}

/** Deadlines are relative to the selected run, never the wall clock. */
export function deadline(due: string | null | undefined, asOf: number) {
  if (!due || !Number.isFinite(Date.parse(due))) return { text: 'Nessuna', tone: 'none' as const }
  const delta = (Date.parse(due) - asOf) / HOUR
  if (delta < 0) return { text: `Scaduta ${Math.ceil(-delta)} h fa`, tone: 'past' as const }
  const hours = Math.ceil(delta)
  if (delta <= 48) return { text: `${hours} h`, tone: delta <= 24 ? ('urgent' as const) : ('soon' as const) }
  return { text: `${Math.ceil(delta / 24)} giorni`, tone: 'later' as const }
}
