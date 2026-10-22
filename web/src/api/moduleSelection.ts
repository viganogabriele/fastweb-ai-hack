import type { components } from './schema'
import type { RunView } from './client'

type CreateRun = components['schemas']['CreateRun']

// Object key order must not change configuration identity (including nested params).
function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical)
  if (value !== null && typeof value === 'object')
    return Object.fromEntries(
      Object.entries(value)
        .sort(([a], [b]) => a.localeCompare(b, 'en'))
        .map(([key, entry]) => [key, canonical(entry)])
    )
  return value
}

// Reuse the selected immutable snapshot; only enabled flags and their hash change.
export async function nextRunRequest(
  run: RunView,
  selection: Record<string, boolean>
): Promise<CreateRun> {
  const { run_id: _runId, config_hash: _previousHash, ...spec } = run.spec
  const modules = spec.modules.map((snapshot) => ({
    ...snapshot,
    manifest: {
      ...snapshot.manifest,
      enabled: selection[snapshot.manifest.id] ?? snapshot.manifest.enabled
    }
  }))
  // CreateRun content excluding server identity and the previous hash; no lineage chaining.
  const fingerprint = JSON.stringify(canonical({ ...spec, modules }))
  const digest = await crypto.subtle.digest(
    'SHA-256',
    new TextEncoder().encode(fingerprint)
  )
  const config_hash = Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, '0')
  ).join('')
  return { ...spec, modules, config_hash }
}

export function selectionIssues(
  run: RunView,
  selection: Record<string, boolean>
): string[] {
  const modules = run.spec.modules.map(({ manifest }) => ({
    ...manifest,
    enabled: selection[manifest.id] ?? manifest.enabled
  }))
  const available = new Set(
    modules
      .filter((item) => item.enabled && item.mode !== 'unavailable')
      .map((item) => item.id)
  )
  if (!available.size) return ['Attiva almeno un modulo disponibile.']
  return modules
    .filter((item) => available.has(item.id))
    .flatMap((item) =>
      item.requires
        .filter((id) => !available.has(id))
        .map(
          (id) => `${item.id} richiede ${id}: attivalo prima di avviare il run.`
        )
    )
}

export async function submitModuleRun(body: CreateRun): Promise<RunView> {
  const response = await fetch('/api/runs', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!response.ok)
    throw new Error(
      `Creazione del run non riuscita (${response.status}). Aggiorna i run e verifica che i moduli siano ancora disponibili.`
    )
  return response.json() as Promise<RunView>
}
