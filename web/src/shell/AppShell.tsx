import { useCallback, useId, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from 'react'
import type { ReactNode } from 'react'
import { Menu, Moon, Sun, X } from 'lucide-react'
import { AnimatePresence, motion, useMotionValue, useReducedMotion, useTransform } from 'motion/react'
import { Button } from '../ui'
import { transition } from '../ui/motion'
import { messages } from '../i18n'
import { ShellContext } from './ShellContext'
import { setTheme, useTheme } from './theme'
import './shell.css'

export interface AppShellProps {
  brand: ReactNode
  sidebar: ReactNode
  sidebarFooter?: ReactNode
  topbar?: ReactNode
  children: ReactNode
}

// Keep this query aligned with shell.css: the breakpoint is our product decision.
const wideQuery = '(min-width: 1024px)'
function subscribeToWidth(callback: () => void) {
  const query = window.matchMedia(wideQuery)
  query.addEventListener('change', callback)
  return () => query.removeEventListener('change', callback)
}
const getWide = () => window.matchMedia(wideQuery).matches
const getServerWide = () => false
const focusableSelector = 'a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])'

export function AppShell({ brand, sidebar, sidebarFooter, topbar, children }: AppShellProps) {
  const reduceMotion = useReducedMotion()
  const [requestedOpen, setRequestedOpen] = useState(false)
  const drawerX = useMotionValue(0)
  const scrimOpacity = useTransform(drawerX, [-280, 0], [0, 1])
  const sidebarId = useId()
  const titleId = useId()
  const drawerRef = useRef<HTMLDivElement>(null)
  const menuRef = useRef<HTMLSpanElement>(null)
  const mainRef = useRef<HTMLElement>(null)
  const closeDrawer = useCallback(() => setRequestedOpen(false), [])
  const subscribe = useCallback((callback: () => void) => subscribeToWidth(() => {
    if (getWide()) closeDrawer()
    callback()
  }), [closeDrawer])
  const wide = useSyncExternalStore(subscribe, getWide, getServerWide)
  const drawerOpen = requestedOpen && !wide
  const context = useMemo(() => ({ drawerOpen, closeDrawer }), [drawerOpen, closeDrawer])

  useLayoutEffect(() => {
    if (!drawerOpen) return
    const drawer = drawerRef.current
    if (!drawer) return
    const main = mainRef.current
    const menu = menuRef.current?.querySelector('button')
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const getFocusable = () => Array.from(drawer.querySelectorAll<HTMLElement>(focusableSelector))
      .filter(element => element.getClientRects().length > 0 && !element.closest('[inert]'))
    const focusFirst = () => (getFocusable()[0] ?? drawer).focus()
    focusFirst()

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        event.stopPropagation()
        closeDrawer()
      }
      if (event.key !== 'Tab') return
      const focusable = getFocusable()
      const first = focusable[0]
      const last = focusable.at(-1)
      if (!first || !last) {
        event.preventDefault()
        drawer.focus()
      } else if (event.shiftKey && (document.activeElement === first || !drawer.contains(document.activeElement))) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && (document.activeElement === last || !drawer.contains(document.activeElement))) {
        event.preventDefault()
        first.focus()
      }
    }
    const handleFocus = (event: FocusEvent) => {
      if (!drawer.contains(event.target as Node)) focusFirst()
    }
    document.addEventListener('keydown', handleKeyDown, true)
    document.addEventListener('focusin', handleFocus)
    return () => {
      document.body.style.overflow = previousOverflow
      document.removeEventListener('keydown', handleKeyDown, true)
      document.removeEventListener('focusin', handleFocus)
      // Crossing to desktop removes the menu trigger, so focus the main landmark instead.
      if (getWide()) main?.focus()
      else menu?.focus()
    }
  }, [drawerOpen, closeDrawer])

  return (
    <ShellContext.Provider value={context}>
      <div className="sd-shell" data-drawer-open={drawerOpen || undefined}>
        <a className="sd-shell__skip" href="#main" inert={drawerOpen} onClick={() => mainRef.current?.focus()}>{messages.shell.skipToContent}</a>
        <AnimatePresence>
          {drawerOpen && <motion.div key="drawer-scrim" className="sd-shell__scrim" aria-hidden="true" onClick={closeDrawer} initial={{ opacity: 0 }} exit={{ opacity: 0, transition: transition.exit }} transition={transition.drawer} style={{ opacity: scrimOpacity }} />}
        </AnimatePresence>
        <motion.div
          ref={drawerRef}
          id={sidebarId}
          className="sd-shell__sidebar"
          drag={!wide && drawerOpen ? 'x' : false}
          dragConstraints={{ left: -280, right: 0 }}
          dragElastic={0.12}
          dragMomentum={false}
          onDragEnd={(_event, info) => {
            if (info.offset.x < -72 || info.velocity.x < -500) closeDrawer()
          }}
          animate={{ ...(reduceMotion ? {} : { x: wide || drawerOpen ? 0 : -280 }), opacity: !wide && !drawerOpen && reduceMotion ? 0 : 1 }}
          transition={reduceMotion ? transition.exit : transition.drawer}
          style={{ x: reduceMotion ? 0 : drawerX, touchAction: 'pan-y' }}
          role={drawerOpen ? 'dialog' : undefined}
          aria-modal={drawerOpen || undefined}
          aria-labelledby={drawerOpen ? titleId : undefined}
          aria-hidden={!wide && !drawerOpen ? true : undefined}
          inert={!wide && !drawerOpen}
          tabIndex={-1}
        >
          <div className="sd-shell__sidebar-heading">
            <div id={titleId} className="sd-shell__brand">{brand}</div>
            <Button className="sd-shell__close" variant="ghost" iconOnly aria-label={messages.shell.closeMenu} icon={<X aria-hidden="true" />} onClick={closeDrawer} />
          </div>
          <div className="sd-shell__navigation">{sidebar}</div>
          {sidebarFooter && <div className="sd-shell__sidebar-footer">{sidebarFooter}</div>}
        </motion.div>
        <div className="sd-shell__workspace" inert={drawerOpen} aria-hidden={drawerOpen || undefined}>
          <header className="sd-shell__topbar">
            <div className="sd-shell__mobile-identity">
              <span ref={menuRef}>
                <Button variant="ghost" iconOnly aria-label={messages.shell.openMenu} aria-expanded={drawerOpen} aria-controls={sidebarId} icon={<Menu aria-hidden="true" />} onClick={() => setRequestedOpen(true)} />
              </span>
              <div className="sd-shell__brand">{brand}</div>
            </div>
            {topbar && <div className="sd-shell__topbar-actions">{topbar}</div>}
            <ThemeToggle />
          </header>
          <main ref={mainRef} id="main" tabIndex={-1} className="sd-shell__main">{children}</main>
        </div>
      </div>
    </ShellContext.Provider>
  )
}

function ThemeToggle() {
  const theme = useTheme()
  const next = theme === 'dark' ? 'light' : 'dark'
  return (
    <Button
      className="sd-shell__theme"
      variant="ghost"
      iconOnly
      aria-label={next === 'dark' ? messages.shell.themeDark : messages.shell.themeLight}
      title={next === 'dark' ? messages.shell.themeDark : messages.shell.themeLight}
      icon={theme === 'dark' ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
      onClick={() => setTheme(next)}
    />
  )
}
