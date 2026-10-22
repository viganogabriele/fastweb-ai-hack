import { createContext, useContext } from 'react'

export interface ShellContextValue {
  drawerOpen: boolean
  closeDrawer: () => void
}

export const ShellContext = createContext<ShellContextValue | null>(null)

export function useShell() {
  const context = useContext(ShellContext)
  if (!context) throw new Error('useShell must be used within AppShell')
  return context
}
