import { useSyncExternalStore } from 'react'

export type Theme = 'light' | 'dark'

// Light is the default and the presentation mode: the OS preference is deliberately ignored so a
// dark-mode laptop never switches the demo by itself. index.html applies the stored choice
// before first paint.
const STORAGE_KEY = 'tesseract-theme'
const listeners = new Set<() => void>()

const current = (): Theme => (document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light')

export function setTheme(theme: Theme) {
  if (theme === 'dark') document.documentElement.dataset.theme = 'dark'
  else delete document.documentElement.dataset.theme
  try {
    localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // Private mode or blocked storage: the choice simply does not persist.
  }
  for (const listener of listeners) listener()
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function useTheme() {
  return useSyncExternalStore(subscribe, current, () => 'light' as Theme)
}
