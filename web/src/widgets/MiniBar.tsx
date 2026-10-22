import { formatNumber } from '../ui'
import { motion, useReducedMotion } from 'motion/react'
import type { CategoryPoint } from '../demo/data'
import { fmt, messages } from '../i18n'
import './widgets.css'
export function MiniBar({
  items,
  unit,
  period
}: {
  items: CategoryPoint[]
  unit: string
  period: string
}) {
  const max = Math.max(...items.map((item) => item.value), 1)
  const reduceMotion = useReducedMotion()
  return (
    <div className="sd-mini-ranking">
      <p className="sd-mini-period">{period}</p>
      <ul className="sd-mini-list" aria-label={fmt(messages.dashboard.charts.ranking, { period })}>
        {items.map((item) => (
          <li key={item.label}>
            <div>
              <span>{item.label}</span>
              <strong>
                {formatNumber(item.value)} {unit}
              </strong>
            </div>
            <div className="sd-mini-track" aria-hidden="true">
              <motion.span
                style={{ width: `${(item.value / max) * 100}%`, transformOrigin: 'left center' }}
                initial={{ transform: reduceMotion ? 'scaleX(1)' : 'scaleX(0)' }}
                animate={{ transform: 'scaleX(1)' }}
                transition={{ duration: reduceMotion ? 0.16 : 0.38, ease: [0.23, 1, 0.32, 1] }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
export const StatProgress = MiniBar
