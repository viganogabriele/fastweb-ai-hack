import { it } from './it'

// Single UI locale for now. Every user-facing string lives in `./it/<namespace>.ts`; a new
// locale adds a sibling folder with the same shape (`Messages`) and switches `messages` here.
export const LOCALE = 'it-IT'
export type Messages = typeof it
export const messages: Messages = it

/** Fills `{name}` placeholders: `fmt(messages.dashboard.rows, { count: 3 })`. */
export function fmt(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) =>
    key in values ? String(values[key]) : match
  )
}
