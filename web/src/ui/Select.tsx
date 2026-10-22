import { createPortal } from 'react-dom'
import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { Check, CircleAlert, ChevronDown } from 'lucide-react'
import './Field.css'
import { LOCALE } from '../i18n'
import { transition } from './motion'

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

export interface SelectProps {
  label: string
  hideLabel?: boolean
  hint?: string
  error?: string
  options: SelectOption[]
  value?: string
  onValueChange: (value: string) => void
  disabled?: boolean
  id?: string
  className?: string
  size?: 'md' | 'sm'
}

interface PopoverPosition {
  left: number
  top: number
  width: number
  maxHeight: number
  placeAbove: boolean
}

export function Select({
  label, hideLabel, hint, error, options, value, onValueChange, disabled, id, className = '', size = 'md',
}: SelectProps) {
  const autoId = useId()
  const fieldId = id ?? autoId
  const listboxId = `${fieldId}-listbox`
  const descriptions = [hint && `${fieldId}-hint`, error && `${fieldId}-error`].filter(Boolean).join(' ') || undefined
  const valueIndex = options.findIndex(option => option.value === value)
  const selectedIndex = valueIndex >= 0 ? valueIndex : options.findIndex(option => !option.disabled)
  const selected = (valueIndex >= 0 ? options[valueIndex] : options[0])
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(selectedIndex)
  const [position, setPosition] = useState<PopoverPosition | null>(null)
  const reduceMotion = useReducedMotion()
  const triggerRef = useRef<HTMLButtonElement>(null)
  const listboxRef = useRef<HTMLDivElement>(null)
  const typeahead = useRef('')
  const typeaheadTimer = useRef<number | undefined>(undefined)

  const enabledFrom = (from: number, direction: 1 | -1) => {
    if (!options.length) return -1
    for (let step = 1; step <= options.length; step += 1) {
      const index = (from + step * direction + options.length) % options.length
      if (!options[index].disabled) return index
    }
    return -1
  }

  const updatePosition = useCallback(() => {
    const rect = triggerRef.current?.getBoundingClientRect()
    if (!rect) return
    const margin = 8
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')
    const triggerStyle = getComputedStyle(triggerRef.current!)
    if (context) context.font = triggerStyle.font
    const widestOption = options.reduce((widest, option) => Math.max(widest, context?.measureText(option.label).width ?? 0), 0)
    const desiredWidth = Math.max(rect.width, Math.ceil(widestOption + 56))
    const width = Math.min(desiredWidth, window.innerWidth - margin * 2)
    const left = Math.max(margin, Math.min(rect.left, window.innerWidth - width - margin))
    const below = window.innerHeight - rect.bottom - margin
    const above = rect.top - margin
    const maxHeight = Math.max(0, Math.min(288, Math.max(below, above)))
    const placeAbove = below < 176 && above > below
    const popoverHeight = Math.min(maxHeight, options.length * 44 + 10)
    setPosition({ left, top: placeAbove ? Math.max(margin, rect.top - popoverHeight - 4) : rect.bottom + 4, width, maxHeight, placeAbove })
  }, [options])

  useLayoutEffect(() => {
    if (!open) return
    updatePosition()
    const onViewportChange = () => updatePosition()
    window.addEventListener('resize', onViewportChange)
    window.addEventListener('scroll', onViewportChange, true)
    return () => {
      window.removeEventListener('resize', onViewportChange)
      window.removeEventListener('scroll', onViewportChange, true)
    }
  }, [open, updatePosition])

  useEffect(() => {
    if (!open) return
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node
      if (!triggerRef.current?.contains(target) && !listboxRef.current?.contains(target)) setOpen(false)
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        setOpen(false)
        triggerRef.current?.focus()
      } else if (event.key === 'Tab') {
        setOpen(false)
      }
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open, updatePosition])

  useEffect(() => () => window.clearTimeout(typeaheadTimer.current), [])

  useEffect(() => {
    const active = listboxRef.current?.querySelector<HTMLElement>(`[data-option-index="${activeIndex}"]`)
    active?.scrollIntoView({ block: 'nearest' })
    updatePosition()
  }, [activeIndex, updatePosition])

  const openAt = (index: number) => {
    setActiveIndex(index >= 0 ? index : enabledFrom(-1, 1))
    setOpen(true)
  }

  const choose = (index: number) => {
    const option = options[index]
    if (!option || option.disabled) return
    onValueChange(option.value)
    setOpen(false)
    triggerRef.current?.focus()
  }

  const onTriggerKeyDown = (event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (open && (event.key === 'Home' || event.key === 'End')) {
      event.preventDefault()
      const indexes = options.map((option, index) => option.disabled ? -1 : index).filter(index => index >= 0)
      if (indexes.length) setActiveIndex(event.key === 'Home' ? indexes[0] : indexes[indexes.length - 1])
      return
    }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault()
      if (!open) openAt(selectedIndex)
      else setActiveIndex(index => enabledFrom(index, event.key === 'ArrowDown' ? 1 : -1))
      return
    }
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      if (open) choose(activeIndex)
      else openAt(selectedIndex)
      return
    }
    if (!open || event.key.length !== 1 || event.ctrlKey || event.metaKey || event.altKey) return
    typeahead.current += event.key.toLocaleLowerCase(LOCALE)
    window.clearTimeout(typeaheadTimer.current)
    typeaheadTimer.current = window.setTimeout(() => { typeahead.current = '' }, 500)
    const start = options.findIndex(option => option.value === value)
    for (let offset = 1; offset <= options.length; offset += 1) {
      const index = (start + offset + options.length) % options.length
      if (!options[index].disabled && options[index].label.toLocaleLowerCase(LOCALE).startsWith(typeahead.current)) {
        setActiveIndex(index)
        break
      }
    }
  }

  return (
    <div className="sd-field">
      <span className={hideLabel ? 'sd-visually-hidden' : 'sd-field__label'} id={`${fieldId}-label`}>{label}</span>
      <div className="sd-field__wrap">
        <button
          ref={triggerRef}
          id={fieldId}
          type="button"
          className={`sd-field__control sd-field__select-trigger sd-field__control--${size} ${className}`}
          role="combobox"
          aria-labelledby={`${fieldId}-label`}
          aria-expanded={open}
          aria-controls={listboxId}
          aria-activedescendant={open && activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined}
          aria-invalid={error ? true : undefined}
          aria-describedby={descriptions}
          disabled={disabled}
          onClick={() => open ? setOpen(false) : openAt(selectedIndex)}
          onKeyDown={onTriggerKeyDown}
        >
          <span className="sd-field__select-value" title={selected?.label}>{selected?.label ?? ''}</span>
          <ChevronDown className="sd-field__chevron" aria-hidden="true" />
        </button>
        {position && createPortal(
          <AnimatePresence>
            {open && (
              <motion.div
                key="select-popover"
                ref={listboxRef}
                id={listboxId}
                role="listbox"
                aria-labelledby={`${fieldId}-label`}
                className="sd-select-popover"
                style={{ left: position.left, top: position.top, width: position.width, maxHeight: position.maxHeight, transformOrigin: position.placeAbove ? 'bottom center' : 'top center' }}
                initial={{ opacity: 0, ...(reduceMotion ? {} : { scale: 0.96, y: position.placeAbove ? 4 : -4 }) }}
                animate={{ opacity: 1, ...(reduceMotion ? {} : { scale: 1, y: 0 }) }}
                exit={{ opacity: 0, ...(reduceMotion ? {} : { scale: 0.98, y: position.placeAbove ? 2 : -2 }), transition: transition.exit }}
                transition={transition.popover}
              >
                {options.map((option, index) => (
                  <div
                    key={option.value}
                    id={`${listboxId}-option-${index}`}
                    role="option"
                    aria-selected={option.value === value}
                    aria-disabled={option.disabled || undefined}
                    data-option-index={index}
                    className={`sd-select-option${activeIndex === index ? ' is-active' : ''}${option.disabled ? ' is-disabled' : ''}`}
                    onMouseMove={() => !option.disabled && setActiveIndex(index)}
                    onClick={() => choose(index)}
                  >
                    <span className="sd-select-option__label">{option.label}</span>
                    <Check className="sd-select-option__check" aria-hidden="true" />
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>, document.body,
        )}
      </div>
      {hint && <p className="sd-field__hint" id={`${fieldId}-hint`}>{hint}</p>}
      {error && <p className="sd-field__error" id={`${fieldId}-error`}><CircleAlert aria-hidden="true" />{error}</p>}
    </div>
  )
}
