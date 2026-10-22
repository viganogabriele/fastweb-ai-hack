import { formatNumber } from '../ui'
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
              <span style={{ width: `${(item.value / max) * 100}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
export const StatProgress = MiniBar
