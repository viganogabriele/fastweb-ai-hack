import { CircleCheck, TriangleAlert, CircleX, Info, Minus } from 'lucide-react'
import { formatNumber } from './format'
import './StatusBadge.css'

export type StatusTone = 'success' | 'warning' | 'danger' | 'info' | 'neutral'

export interface StatusBadgeProps {
  tone: StatusTone
  label: string
  count?: number
  className?: string
}

const icons = { success: CircleCheck, warning: TriangleAlert, danger: CircleX, info: Info, neutral: Minus }

export function StatusBadge({ tone, label, count, className = '' }: StatusBadgeProps) {
  const Icon = icons[tone]
  return (
    <span className={`sd-status-badge sd-status-badge--${tone} ${className}`} data-tone={tone}>
      <Icon aria-hidden="true" />
      <span>{label}</span>
      {count !== undefined && <span className="sd-status-badge__count sd-num">{formatNumber(count)}</span>}
    </span>
  )
}
