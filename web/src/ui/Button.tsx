import { useEffect, type ButtonHTMLAttributes, type ReactNode } from 'react'
import './Button.css'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: 'sm' | 'md'
  icon?: ReactNode
  iconOnly?: boolean
  loading?: boolean
  pressed?: boolean
}

export function Button({
  variant = 'secondary', size = 'md', icon, iconOnly, loading = false, pressed,
  children, className = '', disabled, type = 'button', 'aria-label': ariaLabel, ...rest
}: ButtonProps) {
  useEffect(() => {
    if (import.meta.env.DEV && iconOnly && !ariaLabel?.trim()) {
      console.warn('Signal Dark Button: iconOnly requires an aria-label')
    }
  }, [iconOnly, ariaLabel])

  return (
    <button
      {...rest}
      type={type}
      className={`sd-button sd-button--${variant} sd-button--${size}${iconOnly ? ' sd-button--icon-only' : ''} ${className}`}
      aria-label={ariaLabel}
      aria-pressed={pressed}
      aria-busy={loading || undefined}
      disabled={disabled || loading}
    >
      {loading ? <span className="sd-button__spinner" aria-hidden="true" /> : icon && <span className="sd-button__icon" aria-hidden="true">{icon}</span>}
      <span className={iconOnly ? 'sd-visually-hidden' : 'sd-button__label'}>{children}</span>
    </button>
  )
}
