import { useEffect, useState } from 'react'

export type RunDataStatus = 'loading' | 'ready' | 'unavailable' | 'error'

/**
 * Reads `/api/runs/{runId}/{path}`. Business series are served only by the dev mock today: on the
 * real backend the route is missing (404), reported as `unavailable` so the UI can say so instead
 * of showing numbers it does not have.
 */
export function useRunData<T>(runId: string, path: string) {
  const [state, setState] = useState<{ key: string; status: RunDataStatus; data: T | null }>({ key: '', status: 'loading', data: null })
  const key = `${runId}/${path}`
  useEffect(() => {
    const controller = new AbortController()
    fetch(`/api/runs/${encodeURIComponent(runId)}/${path}`, { signal: controller.signal, headers: { Accept: 'application/json' } })
      .then(async (response) => {
        if (response.status === 404) return setState({ key, status: 'unavailable', data: null })
        if (!response.ok) return setState({ key, status: 'error', data: null })
        setState({ key, status: 'ready', data: (await response.json()) as T })
      })
      .catch(() => {
        if (!controller.signal.aborted) setState({ key, status: 'error', data: null })
      })
    return () => controller.abort()
  }, [runId, path, key])
  return state.key === key ? state : { key, status: 'loading' as const, data: null }
}
