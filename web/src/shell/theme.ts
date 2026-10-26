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

/**
 * Light-bulb timing, as in polinetwork/admin. Turning the light on is an entrance: it floods out of
 * the toggle fast and settles (ease-out). Turning it off is the exit: it retreats into the toggle,
 * slow then faster (ease-in), about 25% shorter.
 */
const LIGHT_ON = { duration: 700, easing: 'cubic-bezier(0.32, 0.72, 0, 1)' }
const LIGHT_OFF = { duration: 520, easing: 'cubic-bezier(0.55, 0.085, 0.68, 0.53)' }
let revealing = false

/**
 * Switches theme like a light bulb at the toggle: to light, the new (light) page grows as a circle
 * from the toggle's icon to the farthest corner; to dark, the old (light) page shrinks back into the
 * icon, uncovering the dark one beneath. CSS transitions stay off meanwhile so colours do not also
 * fade. Without View Transitions, or with reduced motion, the swap is instant. A press during a
 * reveal is ignored.
 */
export function switchTheme(theme: Theme, source?: Element | null) {
  if (revealing) return
  const root = document.documentElement
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (!('startViewTransition' in document) || reduceMotion) {
    root.setAttribute('data-theme-switching', '')
    setTheme(theme)
    requestAnimationFrame(() => requestAnimationFrame(() => root.removeAttribute('data-theme-switching')))
    return
  }

  const width = window.innerWidth
  const height = window.innerHeight
  const icon = source?.querySelector('svg') ?? source
  const box = icon?.getBoundingClientRect()
  const x = box ? box.left + box.width / 2 : width / 2
  const y = box ? box.top + box.height / 2 : height / 2
  const radius = Math.hypot(Math.max(x, width - x), Math.max(y, height - y))
  const lightOn = theme === 'light'
  // In % of the viewport, not px: under browser zoom Chrome scales px on the transition
  // pseudo-elements a second time. A circle's % radius is relative to the diagonal / √2.
  const bulb = (r: number) =>
    `circle(${(r / (Math.hypot(width, height) / Math.SQRT2)) * 100}% at ${(x / width) * 100}% ${(y / height) * 100}%)`

  revealing = true
  root.setAttribute('data-theme-switching', '')
  root.setAttribute('data-theme-reveal', lightOn ? 'on' : 'off')
  const transition = document.startViewTransition(() => setTheme(theme))
  transition.ready
    .then(() =>
      root.animate(
        { clipPath: lightOn ? [bulb(0), bulb(radius)] : [bulb(radius), bulb(0)] },
        {
          ...(lightOn ? LIGHT_ON : LIGHT_OFF),
          pseudoElement: lightOn ? '::view-transition-new(root)' : '::view-transition-old(root)',
          // Hold the end state until the snapshots go, or the other theme flashes for a frame.
          fill: 'both'
        }
      )
    )
    .catch(() => undefined)
  transition.finished.finally(() => {
    revealing = false
    root.removeAttribute('data-theme-switching')
    root.removeAttribute('data-theme-reveal')
  })
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function useTheme() {
  return useSyncExternalStore(subscribe, current, () => 'light' as Theme)
}
