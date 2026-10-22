import { useId } from 'react'
import { motion } from 'motion/react'
import { transition } from '../ui/motion'
import type { LucideIcon } from 'lucide-react'
import { useShell } from './ShellContext'
import './shell.css'

export interface NavItem {
  id: string
  label: string
  icon: LucideIcon
  badge?: string
  disabled?: boolean
}

export interface NavGroup {
  id: string
  label?: string
  items: NavItem[]
}

export interface SidebarNavProps {
  label: string
  groups: NavGroup[]
  currentId: string
  onNavigate: (id: string) => void
}

export function SidebarNav({ label, groups, currentId, onNavigate }: SidebarNavProps) {
  const { drawerOpen, closeDrawer } = useShell()
  const id = useId()
  // Even duplicate IDs in consumer data cannot produce two current-page announcements.
  const currentGroupIndex = groups.findIndex(group => group.items.some(item => item.id === currentId))
  const currentItemIndex = groups[currentGroupIndex]?.items.findIndex(item => item.id === currentId)

  return (
    <nav className="sd-sidebar-nav" aria-label={label}>
      {groups.map((group, index) => (
        <section className="sd-sidebar-nav__group" key={group.id} aria-labelledby={group.label ? `${id}-${index}` : undefined}>
          {group.label && <h2 className="sd-sidebar-nav__heading" id={`${id}-${index}`}>{group.label}</h2>}
          <ul className="sd-sidebar-nav__list">
            {group.items.map((item, itemIndex) => {
              const active = index === currentGroupIndex && itemIndex === currentItemIndex
              const Icon = item.icon
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className="sd-sidebar-nav__item"
                    aria-current={active ? 'page' : undefined}
                    disabled={item.disabled}
                    onClick={() => {
                      onNavigate(item.id)
                      if (drawerOpen) closeDrawer()
                    }}
                  >
                    {active && <motion.span className="sd-sidebar-nav__indicator" layoutId="sidebar-active-indicator" transition={transition.spring} style={{ borderRadius: 8 }} aria-hidden="true" />}
                    <Icon className="sd-sidebar-nav__icon" aria-hidden="true" />
                    <span className="sd-sidebar-nav__label">{item.label}</span>
                    {item.badge && <span className="sd-sidebar-nav__badge">{item.badge}</span>}
                  </button>
                </li>
              )
            })}
          </ul>
        </section>
      ))}
    </nav>
  )
}
