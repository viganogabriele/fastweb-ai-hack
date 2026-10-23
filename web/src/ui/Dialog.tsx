import { useEffect, useRef, type ReactNode } from 'react'
import { X } from 'lucide-react'
import { Button } from './Button'
import './Dialog.css'

export interface DialogProps {
  open: boolean
  title: ReactNode
  onClose: () => void
  children: ReactNode
  footer?: ReactNode
  /** Blocks Esc, backdrop and close button while a write is in flight. */
  dismissible?: boolean
}

// Native modal <dialog>: focus trap, Esc and top layer come from the browser.
export function Dialog({ open, title, onClose, children, footer, dismissible = true }: DialogProps) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])
  return (
    <dialog
      ref={ref}
      className="sd-dialog"
      aria-labelledby="sd-dialog-title"
      onCancel={(event) => { event.preventDefault(); if (dismissible) onClose() }}
      onClick={(event) => { if (dismissible && event.target === event.currentTarget) onClose() }}
    >
      {open && <div className="sd-dialog__panel">
        <header className="sd-dialog__header">
          <h2 id="sd-dialog-title">{title}</h2>
          <Button variant="ghost" size="sm" iconOnly icon={<X />} aria-label="Chiudi" disabled={!dismissible} onClick={onClose}>Chiudi</Button>
        </header>
        <div className="sd-dialog__body">{children}</div>
        {footer && <footer className="sd-dialog__footer">{footer}</footer>}
      </div>}
    </dialog>
  )
}
