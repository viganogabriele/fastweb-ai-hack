import type { ReactNode } from 'react'
import './shell.css'

export interface PageHeaderProps {
  title: string
  subtitle?: string
  meta?: ReactNode
  actions?: ReactNode
  children?: ReactNode
}

export function PageHeader({ title, subtitle, meta, actions, children }: PageHeaderProps) {
  return (
    <header className="sd-page-header">
      <div className="sd-page-header__row">
        <div className="sd-page-header__intro">
          <h1 className="sd-page-header__title">{title}</h1>
          {subtitle && <p className="sd-page-header__subtitle">{subtitle}</p>}
          {meta && <div className="sd-page-header__meta">{meta}</div>}
        </div>
        {actions && <div className="sd-page-header__actions">{actions}</div>}
      </div>
      {children && <div className="sd-page-header__filters">{children}</div>}
    </header>
  )
}
