/**
 * @task S2F2
 * @description 재사용 가능한 폼 필드 컴포넌트
 *
 * - input / select / textarea 지원
 * - 에러 메시지 표시 (role="alert")
 * - 도움말 텍스트
 * - ARIA 속성 (aria-invalid, aria-describedby, aria-required)
 * - 반응형 Tailwind CSS 스타일링
 */

'use client'

import { forwardRef, type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes } from 'react'
import type { FormFieldType } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface BaseFieldProps {
  /** 필드 ID (label htmlFor 및 aria 연결용) */
  id: string
  /** 라벨 텍스트 */
  label: string
  /** 필수 입력 여부 */
  required?: boolean
  /** 에러 메시지 */
  error?: string
  /** 도움말 텍스트 */
  helpText?: string
  /** 필드 타입 */
  fieldType?: FormFieldType
  /** 전체 너비 사용 여부 */
  fullWidth?: boolean
  /** 추가 CSS 클래스 (wrapper) */
  className?: string
}

type InputFieldProps = BaseFieldProps &
  Omit<InputHTMLAttributes<HTMLInputElement>, 'id' | 'className'> & {
    fieldType?: Exclude<FormFieldType, 'select' | 'textarea'>
  }

type SelectFieldProps = BaseFieldProps &
  Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id' | 'className'> & {
    fieldType: 'select'
    options: { value: string; label: string }[]
    placeholder?: string
  }

type TextareaFieldProps = BaseFieldProps &
  Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'id' | 'className'> & {
    fieldType: 'textarea'
  }

export type FormFieldProps = InputFieldProps | SelectFieldProps | TextareaFieldProps

// ---------------------------------------------------------------------------
// 스타일 유틸
// ---------------------------------------------------------------------------

const baseInputStyles =
  'block w-full rounded-lg border px-3.5 py-2.5 text-sm text-gray-900 shadow-sm transition-colors placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500'

const normalBorderStyles = 'border-gray-300 focus:border-blue-500 focus:ring-blue-500/20'
const errorBorderStyles = 'border-red-400 focus:border-red-500 focus:ring-red-500/20'

function getInputClassName(hasError: boolean): string {
  return `${baseInputStyles} ${hasError ? errorBorderStyles : normalBorderStyles}`
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

function isSelectField(props: FormFieldProps): props is SelectFieldProps {
  return props.fieldType === 'select'
}

function isTextareaField(props: FormFieldProps): props is TextareaFieldProps {
  return props.fieldType === 'textarea'
}

const FormField = forwardRef<
  HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement,
  FormFieldProps
>(function FormField(props, ref) {
  const {
    id,
    label,
    required = false,
    error,
    helpText,
    fullWidth = true,
    className = '',
  } = props

  const hasError = Boolean(error)
  const errorId = `${id}-error`
  const helpId = `${id}-help`

  // aria-describedby 조립
  const describedByParts: string[] = []
  if (hasError) describedByParts.push(errorId)
  if (helpText) describedByParts.push(helpId)
  const ariaDescribedBy = describedByParts.length > 0 ? describedByParts.join(' ') : undefined

  // 공통 aria 속성
  const sharedAriaProps = {
    'aria-invalid': hasError ? true as const : undefined,
    'aria-describedby': ariaDescribedBy,
    'aria-required': required ? true as const : undefined,
  }

  // --- 렌더 ---

  return (
    <div className={`${fullWidth ? 'w-full' : ''} ${className}`}>
      {/* 라벨 */}
      <label
        htmlFor={id}
        className="mb-1.5 block text-sm font-medium text-gray-700"
      >
        {label}
        {required && (
          <span className="ml-0.5 text-red-500" aria-hidden="true">
            *
          </span>
        )}
      </label>

      {/* 입력 요소 */}
      {isSelectField(props) ? (
        <select
          ref={ref as React.Ref<HTMLSelectElement>}
          id={id}
          name={props.name ?? id}
          required={required}
          disabled={props.disabled}
          value={props.value}
          defaultValue={props.defaultValue}
          onChange={props.onChange}
          onBlur={props.onBlur}
          className={getInputClassName(hasError)}
          {...sharedAriaProps}
        >
          {props.placeholder && (
            <option value="" disabled>
              {props.placeholder}
            </option>
          )}
          {props.options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : isTextareaField(props) ? (
        <textarea
          ref={ref as React.Ref<HTMLTextAreaElement>}
          id={id}
          name={props.name ?? id}
          required={required}
          disabled={props.disabled}
          placeholder={props.placeholder}
          value={props.value}
          defaultValue={props.defaultValue}
          rows={props.rows ?? 4}
          onChange={props.onChange}
          onBlur={props.onBlur}
          className={`${getInputClassName(hasError)} resize-y`}
          {...sharedAriaProps}
        />
      ) : (
        <input
          ref={ref as React.Ref<HTMLInputElement>}
          id={id}
          name={props.name ?? id}
          type={props.fieldType ?? props.type ?? 'text'}
          required={required}
          disabled={props.disabled}
          placeholder={props.placeholder}
          value={props.value}
          defaultValue={props.defaultValue}
          min={props.min}
          max={props.max}
          step={props.step}
          pattern={props.pattern}
          onChange={props.onChange}
          onBlur={props.onBlur}
          className={getInputClassName(hasError)}
          {...sharedAriaProps}
        />
      )}

      {/* 에러 메시지 */}
      {hasError && (
        <p
          id={errorId}
          role="alert"
          className="mt-1.5 text-sm text-red-600"
        >
          {error}
        </p>
      )}

      {/* 도움말 */}
      {helpText && !hasError && (
        <p id={helpId} className="mt-1.5 text-sm text-gray-500">
          {helpText}
        </p>
      )}
    </div>
  )
})

FormField.displayName = 'FormField'
export default FormField
