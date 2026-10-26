export interface OverlapNote {
  store_id: string
  author: string
  facts: { sku: string | string[] | null; size?: string }[]
}

/** Ambiguous candidates are not evidence of a shared product. Size does not change a SKU. */
export function colleagueOverlap(notes: OverlapNote[]) {
  const groups = new Map<string, { store_id: string; sku: string; authors: Set<string> }>()
  for (const note of notes) {
    for (const fact of note.facts) {
      if (typeof fact.sku !== 'string') continue
      const key = `${note.store_id}:${fact.sku}`
      const group = groups.get(key) ?? { store_id: note.store_id, sku: fact.sku, authors: new Set<string>() }
      group.authors.add(note.author)
      groups.set(key, group)
    }
  }
  return [...groups.values()]
    .filter(group => group.authors.size >= 2)
    .map(group => ({ ...group, authors: [...group.authors].sort() }))
}
