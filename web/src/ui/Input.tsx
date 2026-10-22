import { useId, type InputHTMLAttributes, type ReactNode } from 'react'
import { CircleAlert } from 'lucide-react'
import './Field.css'

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label: string
  hideLabel?: boolean
  hint?: string
  error?: string
  icon?: ReactNode
}

export function Input({
  label, hideLabel, hint, error, icon, id, className = '',
  'aria-describedby': describedBy, 'aria-invalid': invalid, ...rest
}: InputProps) {
  const autoId = useId()
  const fieldId = id ?? autoId
  const descriptions = [describedBy, hint && `${fieldId}-hint`, error && `${fieldId}-error`].filter(Boolean).join(' ') || undefined

  return (
    <div className="sd-field">
      <label className={hideLabel ? 'sd-visually-hidden' : 'sd-field__label'} htmlFor={fieldId}>{label}</label>
      <div className={`sd-field__wrap${icon ? ' sd-field__wrap--has-icon' : ''}`}>
        {icon && <span className="sd-field__icon" aria-hidden="true">{icon}</span>}
        <input
          {...rest}
          id={fieldId}
          className={`sd-field__control ${className}`}
          aria-invalid={error ? true : invalid}
          aria-describedby={descriptions}
        />
      </div>
      {hint && <p className="sd-field__hint" id={`${fieldId}-hint`}>{hint}</p>}
      {error && <p className="sd-field__error" id={`${fieldId}-error`}><CircleAlert aria-hidden="true" />{error}</p>}
    </div>
  )
}
