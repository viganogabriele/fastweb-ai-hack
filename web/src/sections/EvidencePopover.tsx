import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { ArrowRight } from 'lucide-react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import type { Case } from '../api/client'
import { StatusBadge, transition } from '../ui'
import { caseTypeLabel } from './productView'
import type { Reference, useEvidencePopover } from './useEvidencePopover'

type Placement = { left: number; top: number; above: boolean }

const WIDTH = 340
const MARGIN = 8

const relations: Record<Reference['relation'], { label: string; tone: 'success' | 'danger' }> = {
  supporting: { label: 'A supporto', tone: 'success' },
  contradicting: { label: 'In contrasto', tone: 'danger' }
}
const priorities: Record<Case['priority'], string> = { critical: 'Critica', high: 'Alta', medium: 'Media', low: 'Bassa' }

/** Hover card for highlighted evidence, listing the linked cases with a link to each. */
export function EvidencePopover({ state, cases, onCaseSelect }: {
  state: ReturnType<typeof useEvidencePopover>
  cases: ReadonlyMap<string, Case>
  onCaseSelect: (item: Case) => void
}) {
  const { active, close, cancelClose, scheduleClose } = state
  const ref = useRef<HTMLDivElement>(null)
  const [placement, setPlacement] = useState<Placement | null>(null)
  const reduceMotion = useReducedMotion()

  useLayoutEffect(() => {
    if (!active) return
    const place = () => {
      // A phrase can wrap over several lines: anchor to the line nearest the card.
      const rects = [...active.anchor.getClientRects()]
      if (!rects.length) return close()
      const height = ref.current?.offsetHeight ?? 160
      const last = rects[rects.length - 1]
      const first = rects[0]
      const above = last.bottom + height + MARGIN > window.innerHeight && first.top - height - MARGIN > 0
      const line = above ? first : last
      const width = Math.min(WIDTH, window.innerWidth - MARGIN * 2)
      const left = Math.max(MARGIN, Math.min(line.left, window.innerWidth - width - MARGIN))
      setPlacement({ left, top: above ? line.top - height - 6 : line.bottom + 6, above })
    }
    place()
    window.addEventListener('resize', place)
    window.addEventListener('scroll', place, true)
    return () => {
      window.removeEventListener('resize', place)
      window.removeEventListener('scroll', place, true)
    }
  }, [active, close])

  useEffect(() => {
    if (!active) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      active.anchor.focus()
      close()
    }
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node
      if (!ref.current?.contains(target) && !active.anchor.contains(target)) close()
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('pointerdown', onPointerDown)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('pointerdown', onPointerDown)
    }
  }, [active, close])

  let body: ReactNode = null
  if (active) {
    const count = active.references.length
    body = <>
      <p className="sd-evidence-popover__title">{count === 1 ? 'Evidenza di 1 caso' : `Evidenza di ${count} casi`}</p>
      <ul>
        {active.references.map((reference) => {
          const item = cases.get(reference.caseId)
          return (
            <li key={`${reference.caseId}-${reference.relation}`} className={`is-${reference.relation}`}>
              <div className="sd-evidence-popover__head">
                <strong>{item ? `${item.store_id ?? 'Negozio da verificare'} · ${item.scope_id ?? 'Prodotto da identificare'}` : reference.caseId}</strong>
                <StatusBadge {...relations[reference.relation]} />
              </div>
              <span className="sd-evidence-popover__meta">
                {caseTypeLabel(reference.caseType)}{item ? ` · Priorità ${priorities[item.priority].toLowerCase()}` : ''}
              </span>
              {item?.priority_reason && <p>{item.priority_reason}</p>}
              {item
                ? <button type="button" onClick={() => { close(); onCaseSelect(item) }}>Apri il caso <ArrowRight aria-hidden="true" /></button>
                : <span className="sd-evidence-popover__meta">Caso non presente nel run selezionato</span>}
            </li>
          )
        })}
      </ul>
    </>
  }

  return createPortal(
    <AnimatePresence>
      {active && (
        <motion.div key="evidence-popover" ref={ref} role="dialog" aria-label="Casi collegati all’evidenza"
          className="sd-evidence-popover"
          style={{ left: placement?.left ?? -9999, top: placement?.top ?? 0, width: Math.min(WIDTH, window.innerWidth - MARGIN * 2), transformOrigin: placement?.above ? 'bottom left' : 'top left' }}
          onMouseEnter={cancelClose} onMouseLeave={scheduleClose}
          onBlur={(event) => {
            if (!(event.relatedTarget instanceof Node && (ref.current?.contains(event.relatedTarget) || active.anchor === event.relatedTarget))) scheduleClose()
          }}
          initial={{ opacity: 0, ...(reduceMotion ? {} : { scale: 0.97, y: placement?.above ? 4 : -4 }) }}
          animate={{ opacity: 1, ...(reduceMotion ? {} : { scale: 1, y: 0 }) }}
          exit={{ opacity: 0, transition: transition.exit }}
          transition={transition.popover}>
          {body}
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  )
}
