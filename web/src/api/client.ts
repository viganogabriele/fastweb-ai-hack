import type { components } from './schema'
export type RunView = components['schemas']['RunView']
export type Case = components['schemas']['Case']
export type SourceDocument = components['schemas']['SourceDocument']
export type ModuleManifest = components['schemas']['ModuleManifest']

export async function readApi<T>(
  path: string,
  signal: AbortSignal
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    signal: AbortSignal.any([signal, AbortSignal.timeout(15000)]),
    headers: { Accept: 'application/json' }
  })
  if (!response.ok)
    throw new Error(
      `Richiesta non riuscita (${response.status}). Riprova o verifica la connessione ai servizi dati.`
    )
  return response.json() as Promise<T>
}
