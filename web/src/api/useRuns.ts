import { useEffect, useState } from 'react'
import { readApi } from './client'
import type { RunView } from './client'

export function useRuns() {
  const [items, setItems] = useState<RunView[]>([])
  const [selectedId, select] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    readApi<RunView[]>('/runs', controller.signal)
      .then((data) => {
        if (controller.signal.aborted) return
        const sorted = [...data].sort((a, b) =>
          b.spec.as_of.localeCompare(a.spec.as_of)
        )
        setItems(sorted)
        select((current) =>
          sorted.some((run) => run.spec.run_id === current)
            ? current
            : (sorted.find((run) => run.published)?.spec.run_id ??
              sorted[0]?.spec.run_id ??
              '')
        )
      })
      .catch((error) => {
        if (!controller.signal.aborted) setError(String(error.message))
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [revision])
  return {
    items,
    selectedId,
    select,
    selected: items.find((run) => run.spec.run_id === selectedId),
    loading,
    error,
    acceptRun: (run: RunView, originRunId?: string) => {
      setItems((current) => [
        run,
        ...current.filter((item) => item.spec.run_id !== run.spec.run_id)
      ])
      select((current) =>
        originRunId !== undefined && current === originRunId
          ? run.spec.run_id
          : current
      )
    },
    retry: () => {
      setLoading(true)
      setError('')
      setRevision((value) => value + 1)
    }
  }
}
