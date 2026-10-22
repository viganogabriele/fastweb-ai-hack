import type { Transition } from 'motion/react'

// Shared motion vocabulary (motion/react). One feel across the app: custom ease-out curves, short
// product durations, springs without bounce. CSS mirrors these in local.css (`--sd-local-ease-*`).
// Reduced motion is handled once by `<MotionConfig reducedMotion="user">` at the app root.
export const ease = {
  out: [0.23, 1, 0.32, 1],
  outQuad: [0.25, 0.46, 0.45, 0.94],
  inOut: [0.645, 0.045, 0.355, 1],
  drawer: [0.32, 0.72, 0, 1],
} as const

export const duration = {
  press: 0.15,
  hover: 0.12,
  popover: 0.18,
  exit: 0.12,
  view: 0.22,
  drawer: 0.3,
} as const

export const transition = {
  popover: { duration: duration.popover, ease: ease.out },
  exit: { duration: duration.exit, ease: ease.outQuad },
  view: { duration: duration.view, ease: ease.out },
  drawer: { duration: duration.drawer, ease: ease.drawer },
  spring: { type: 'spring', duration: 0.3, bounce: 0 },
} satisfies Record<string, Transition>

/** Stagger step for group entrances (keep total under ~200ms). */
export const stagger = 0.04
