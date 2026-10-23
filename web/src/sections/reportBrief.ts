// Structured reading of the PLT-11 brief template (act.report). The markdown stays the source:
// lines that do not match a known template shape are kept as raw text, never dropped.
// Raw strings still go through briefTokens at render time, so nothing here produces HTML.

export type BriefSignal = { kind: string; amount: number | null; unit: string | null; quality: 'unknown' | 'vague' | null; citation: number | null }
export type BriefForecast = { sku: string; from: string; to: string; units: number; status: string; citation: number | null }
export type BriefOption = { kind: string; citation: number | null }
export type BriefEntry = {
  headline: string
  store: string | null
  product: string | null
  code: string | null
  status: string | null
  priority: string | null
  citation: number | null
  signals: BriefSignal[]
  forecasts: BriefForecast[]
  options: BriefOption[]
  open: string[]
  other: string[]
}
export type BriefSection = { title: string; notes: string[]; entries: BriefEntry[] }
export type Brief = { title: string | null; notes: string[]; sections: BriefSection[] }

const cite = /\s*\[(\d+)\]\.?\s*$/

// Trailing "[n]" as a zero-based citation index, plus the text before it.
function trailingCitation(text: string, count: number): [string, number | null] {
  const match = cite.exec(text)
  if (!match) return [text.trim(), null]
  const index = Number(match[1])
  return index >= 1 && index <= count ? [text.slice(0, match.index).trim(), index - 1] : [text.trim(), null]
}

function headline(text: string) {
  const [store, ...rest] = text.split(' · ')
  if (!rest.length) return { store: null, product: text, code: null }
  const name = rest.join(' · ')
  const coded = /^(.*?)\s*\(([^()]+)\)$/.exec(name)
  return { store, product: coded ? coded[1] : name, code: coded ? coded[2] : null }
}

function entry(line: string, count: number): BriefEntry {
  const base: BriefEntry = { headline: line, store: null, product: null, code: null, status: null, priority: null, citation: null, signals: [], forecasts: [], options: [], open: [], other: [] }
  const match = /^\*\*(.+?)\*\*:\s*(.+)$/.exec(line)
  if (!match) return base
  const [rest, citation] = trailingCitation(match[2], count)
  const state = /^([\w ]+?), priority (\w+)$/.exec(rest)
  return { ...base, ...headline(match[1]), headline: match[1], citation, status: state?.[1] ?? null, priority: state?.[2] ?? null }
}

function detail(target: BriefEntry, line: string, count: number) {
  if (line.startsWith('open: ')) return void target.open.push(line.slice(6))
  const [text, citation] = trailingCitation(line, count)
  const option = /^recommended option: (.+)$/.exec(text)
  if (option) return void target.options.push({ kind: option[1].replaceAll(' ', '_'), citation })
  const forecast = /^baseline (\S+) (\S+)\.\.(\S+) ([\d.]+) units, (.+)$/.exec(text)
  if (forecast) return void target.forecasts.push({ sku: forecast[1], from: forecast[2], to: forecast[3], units: Number(forecast[4]), status: forecast[5], citation })
  const signal = /^([a-z][a-z ]*?)(?:, quantity (unknown|vague)| ([\d.]+) ([a-z%]+))$/.exec(text)
  if (signal) return void target.signals.push({
    kind: signal[1].replaceAll(' ', '_'), quality: (signal[2] as BriefSignal['quality']) ?? null,
    amount: signal[3] ? Number(signal[3]) : null, unit: signal[4] ?? null, citation
  })
  target.other.push(line)
}

export function parseBrief(markdown: string, citationCount: number): Brief {
  const brief: Brief = { title: null, notes: [], sections: [] }
  let section: BriefSection | null = null
  let current: BriefEntry | null = null
  for (const raw of markdown.split('\n')) {
    const line = raw.trimEnd()
    if (!line.trim()) continue
    if (line.startsWith('# ')) { brief.title = line.slice(2); current = null; continue }
    if (line.startsWith('## ')) {
      section = { title: line.slice(3), notes: [], entries: [] }
      brief.sections.push(section)
      current = null
      continue
    }
    if (line.startsWith('- ')) {
      if (!section) { section = { title: '', notes: [], entries: [] }; brief.sections.push(section) }
      current = entry(line.slice(2), citationCount)
      section.entries.push(current)
      continue
    }
    if (/^\s+- /.test(line) && current) { detail(current, line.replace(/^\s+- /, ''), citationCount); continue }
    ;(current ? current.other : section ? section.notes : brief.notes).push(line.trim())
  }
  return brief
}
