import type { ReactNode } from 'react'

export function VisuallyHidden({ children }: { children: ReactNode }) {
  return <span className="sd-visually-hidden">{children}</span>
}
