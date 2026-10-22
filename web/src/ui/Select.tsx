import { useId, type SelectHTMLAttributes } from 'react'
import { CircleAlert, ChevronDown } from 'lucide-react'
import './Field.css'

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  label: string
  hideLabel?: boolean
  hint?: string
  error?: string
  options: SelectOption[]
}

export function Select({
  label, hideLabel, hint, error, options, id, className = '',
  'aria-describedby': describedBy, 'aria-invalid': invalid, ...rest
}: SelectProps) {
  const autoId = useId()
  const fieldId = id ?? autoId
  const descriptions = [describedBy, hint && `${fieldId}-hint`, error && `${fieldId}-error`].filter(Boolean).join(' ') || undefined

  return (
    <div className="sd-field">
      <label className={hideLabel ? 'sd-visually-hidden' : 'sd-field__label'} htmlFor={fieldId}>{label}</label>
      <div className={`sd-field__wrap`}>
        
        <select
          {...rest}
          id={fieldId}
          className={`sd-field__control sd-field__select ${className}`}
          aria-invalid={error ? true : invalid}
          aria-describedby={descriptions}
        >
          {options.map(option => (
            <option key={option.value} value={option.value} disabled={option.disabled}>{option.label}</option>
          ))}
        </select>
        <ChevronDown className="sd-field__chevron" aria-hidden="true" />
      </div>
      {hint && <p className="sd-field__hint" id={`${fieldId}-hint`}>{hint}</p>}
      {error && <p className="sd-field__error" id={`${fieldId}-error`}><CircleAlert aria-hidden="true" />{error}</p>}
    </div>
  )
}
