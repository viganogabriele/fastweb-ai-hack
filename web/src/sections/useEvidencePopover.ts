import { useCallback, useEffect, useRef, useState } from 'react'
import type { FocusEvent, KeyboardEvent, MouseEvent } from 'react'
import type { CaseEvidence } from './sourceEvidence'

export type Reference = Omit<CaseEvidence, 'evidence'>

// Time to travel from the phrase to the card without it closing under the pointer.
const CLOSE_DELAY = 180

/**
 * State for the evidence hover card: opens on hover or focus of a phrase, stays open while the
 * pointer is over the card, and lists the linked cases with a link to each.
 */
export function useEvidencePopover() {
  const [active, setActive] = useState<{ key: string; anchor: HTMLElement; references: Reference[] } | null>(null)
  const timer = useRef<number | undefined>(undefined)
  const cancelClose = useCallback(() => window.clearTimeout(timer.current), [])
  const close = useCallback(() => { cancelClose(); setActive(null) }, [cancelClose])
  const scheduleClose = useCallback(() => {
    cancelClose()
    timer.current = window.setTimeout(() => setActive(null), CLOSE_DELAY)
  }, [cancelClose])
  useEffect(() => cancelClose, [cancelClose])

  const triggerProps = (key: string, references: Reference[]) => {
    const open = (anchor: HTMLElement) => { cancelClose(); setActive({ key, anchor, references }) }
    return {
      tabIndex: 0,
      role: 'button',
      'aria-haspopup': 'dialog' as const,
      'aria-expanded': active?.key === key,
      'data-active': active?.key === key || undefined,
      onMouseEnter: (event: MouseEvent<HTMLElement>) => open(event.currentTarget),
      onMouseLeave: scheduleClose,
      onFocus: (event: FocusEvent<HTMLElement>) => open(event.currentTarget),
      onBlur: (event: FocusEvent<HTMLElement>) => {
        // Tabbing into the card keeps it open.
        if (!(event.relatedTarget instanceof Node && document.querySelector('.sd-evidence-popover')?.contains(event.relatedTarget))) scheduleClose()
      },
      onClick: (event: MouseEvent<HTMLElement>) => open(event.currentTarget),
      onKeyDown: (event: KeyboardEvent<HTMLElement>) => { if (event.key === 'Escape') close() }
    }
  }
  return { active, triggerProps, close, cancelClose, scheduleClose }
}

