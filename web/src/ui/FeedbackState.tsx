import type { ReactNode } from 'react'
import { Inbox, CircleAlert, RotateCcw } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import { Button } from './Button'
import { VisuallyHidden } from './VisuallyHidden'
import { messages } from '../i18n'
import { transition } from './motion'
import './FeedbackState.css'

export interface EmptyStateProps {
  title: string
  description?: string
  action?: ReactNode
  compact?: boolean
}

export interface LoadingStateProps {
  label: string
  lines?: number
  compact?: boolean
  /** false when a page-level announcer already reports this state (avoids duplicate live regions). */
  announce?: boolean
}

export interface ErrorStateProps {
  title: string
  description?: string
  onRetry?: () => void
  compact?: boolean
  /** false when a page-level announcer already reports this state (avoids duplicate alerts). */
  announce?: boolean
}

export function EmptyState({ title, description, action, compact }: EmptyStateProps) {
  const reduceMotion = useReducedMotion()
  return (
    <motion.div
      className={`sd-feedback${compact ? ' sd-feedback--compact' : ''}`}
      initial={{ opacity: 0, ...(reduceMotion ? {} : { y: 4 }) }}
      animate={{ opacity: 1, y: 0 }}
      transition={transition.view}
    >
      <Inbox className="sd-feedback__icon" aria-hidden="true" />
      <p className="sd-feedback__title">{title}</p>
      {description && <p className="sd-feedback__description">{description}</p>}
      {action && <div className="sd-feedback__action">{action}</div>}
    </motion.div>
  )
}

export function LoadingState({ label, lines = 3, compact, announce = true }: LoadingStateProps) {
  const lineCount = Number.isFinite(lines) ? Math.max(1, Math.min(12, Math.floor(lines))) : 3
  return (
    <div role={announce ? 'status' : undefined} aria-live={announce ? 'polite' : undefined} className={`sd-feedback sd-feedback--loading${compact ? ' sd-feedback--compact' : ''}`}>
      <VisuallyHidden>{label}</VisuallyHidden>
      <div className="sd-skeleton" aria-hidden="true">
        {Array.from({ length: lineCount }, (_, index) => <span className="sd-skeleton__line" key={index} />)}
      </div>
    </div>
  )
}

export function ErrorState({ title, description, onRetry, compact, announce = true }: ErrorStateProps) {
  const reduceMotion = useReducedMotion()
  return (
    <motion.div
      role={announce ? 'alert' : undefined}
      className={`sd-feedback sd-feedback--error${compact ? ' sd-feedback--compact' : ''}`}
      initial={{ opacity: 0, ...(reduceMotion ? {} : { y: 4 }) }}
      animate={{ opacity: 1, y: 0 }}
      transition={transition.view}
    >
      <CircleAlert className="sd-feedback__icon" aria-hidden="true" />
      <p className="sd-feedback__title">{title}</p>
      {description && <p className="sd-feedback__description">{description}</p>}
      {onRetry && <Button onClick={onRetry} icon={<RotateCcw />}>{messages.common.retry}</Button>}
    </motion.div>
  )
}
