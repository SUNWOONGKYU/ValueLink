/**
 * @task S2F6
 * @description 프로젝트 생성(평가 요청) 페이지 - 3단계 스텝 폼
 *
 * - 'use client' (interactive form, multi-step)
 * - Supabase 브라우저 클라이언트로 evaluation_requests 테이블에 POST
 * - 3단계: 기업 정보 → 평가 상세 → 예산/확인
 * - 폼 유효성 검증 (한국어 에러 메시지)
 * - 반응형 Tailwind CSS, ARIA 접근성
 */

'use client'

import {
  type ChangeEvent,
  type FormEvent,
  useCallback,
  useMemo,
  useState,
} from 'react'
import { useRouter } from 'next/navigation'
import { createBrowserClient } from '@supabase/ssr'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'

interface FormData {
  // Step 1: Company Information
  company_name_kr: string
  company_name_en: string
  industry: string
  representative_name: string
  business_registration_number: string

  // Step 2: Valuation Details
  valuation_purpose: string
  requested_methods: ValuationMethod[]
  target_date: string
  requirements: string

  // Step 3: Budget
  budget_min: string
  budget_max: string
}

interface FormErrors {
  [key: string]: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TOTAL_STEPS = 3

const INITIAL_FORM_DATA: FormData = {
  company_name_kr: '',
  company_name_en: '',
  industry: '',
  representative_name: '',
  business_registration_number: '',
  valuation_purpose: '',
  requested_methods: [],
  target_date: '',
  requirements: '',
  budget_min: '',
  budget_max: '',
}

const PURPOSE_OPTIONS: { value: string; label: string }[] = [
  { value: 'investment', label: '투자 유치 (Investment)' },
  { value: 'ma', label: 'M&A (합병/인수)' },
  { value: 'ipo', label: 'IPO 준비' },
  { value: 'internal', label: '내부 가치 평가' },
  { value: 'tax', label: '세무 목적' },
  { value: 'litigation', label: '소송/분쟁' },
  { value: 'other', label: '기타' },
]

const METHOD_OPTIONS: { value: ValuationMethod; label: string; description: string }[] = [
  {
    value: 'dcf',
    label: 'DCF (현금흐름할인법)',
    description: '미래 현금흐름을 현재가치로 할인하여 기업가치 산출',
  },
  {
    value: 'relative',
    label: '상대가치평가법',
    description: '유사 기업의 시장 배수를 적용하여 기업가치 산출',
  },
  {
    value: 'asset',
    label: '자산가치평가법',
    description: '순자산가치를 기반으로 기업가치 산출',
  },
  {
    value: 'intrinsic',
    label: '본질가치평가법',
    description: '수익가치와 자산가치를 가중 평균하여 기업가치 산출',
  },
  {
    value: 'tax',
    label: '세무평가법',
    description: '세법 기준의 보충적 평가방법 적용',
  },
]

const INDUSTRY_OPTIONS: string[] = [
  'IT/소프트웨어',
  'AI/인공지능',
  '핀테크/금융',
  '바이오/헬스케어',
  '이커머스/유통',
  '제조/하드웨어',
  '콘텐츠/미디어',
  '교육/에듀테크',
  '부동산/프롭테크',
  '모빌리티/물류',
  '에너지/친환경',
  '식품/푸드테크',
  '기타',
]

const STEP_TITLES: string[] = [
  '기업 정보',
  '평가 상세',
  '예산 및 확인',
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createSupabase() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StepIndicator({
  currentStep,
  totalSteps,
}: {
  currentStep: number
  totalSteps: number
}) {
  return (
    <div className="mb-8">
      {/* Step labels */}
      <div className="mb-3 flex items-center justify-between">
        {STEP_TITLES.map((title, index) => {
          const stepNum = index + 1
          const isActive = stepNum === currentStep
          const isCompleted = stepNum < currentStep

          return (
            <div
              key={stepNum}
              className={`flex items-center gap-2 ${
                index < totalSteps - 1 ? 'flex-1' : ''
              }`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition-colors ${
                  isCompleted
                    ? 'bg-blue-600 text-white'
                    : isActive
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                }`}
                aria-current={isActive ? 'step' : undefined}
              >
                {isCompleted ? (
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2.5}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  stepNum
                )}
              </div>
              <span
                className={`hidden text-sm sm:inline ${
                  isActive || isCompleted
                    ? 'font-medium text-gray-900'
                    : 'text-gray-400'
                }`}
              >
                {title}
              </span>
              {index < totalSteps - 1 && (
                <div
                  className={`mx-2 h-0.5 flex-1 rounded-full transition-colors ${
                    isCompleted ? 'bg-blue-500' : 'bg-gray-200'
                  }`}
                  aria-hidden="true"
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div className="h-1 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-blue-500 transition-all duration-500"
          style={{
            width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%`,
          }}
        />
      </div>
    </div>
  )
}

function FieldLabel({
  htmlFor,
  required,
  children,
}: {
  htmlFor: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1.5 block text-sm font-medium text-gray-700"
    >
      {children}
      {required && (
        <span className="ml-0.5 text-red-500" aria-hidden="true">
          *
        </span>
      )}
    </label>
  )
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null
  return (
    <p className="mt-1.5 text-sm text-red-600" role="alert">
      {message}
    </p>
  )
}

function inputClassName(hasError: boolean): string {
  const base =
    'block w-full rounded-lg border px-3.5 py-2.5 text-sm text-gray-900 shadow-sm transition-colors placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500'
  return `${base} ${
    hasError
      ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500/20'
  }`
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function ProjectCreatePage() {
  const router = useRouter()

  // State
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM_DATA)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Supabase client (memoized)
  const supabase = useMemo(() => createSupabase(), [])

  // ---------------------------------------------------------------------------
  // Handlers
  // ---------------------------------------------------------------------------

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const { name, value } = e.target
      setFormData((prev) => ({ ...prev, [name]: value }))
      // Clear field error on change
      if (errors[name]) {
        setErrors((prev) => {
          const next = { ...prev }
          delete next[name]
          return next
        })
      }
    },
    [errors],
  )

  const handleMethodToggle = useCallback(
    (method: ValuationMethod) => {
      setFormData((prev) => {
        const methods = prev.requested_methods.includes(method)
          ? prev.requested_methods.filter((m) => m !== method)
          : [...prev.requested_methods, method]
        return { ...prev, requested_methods: methods }
      })
      // Clear method error on change
      if (errors.requested_methods) {
        setErrors((prev) => {
          const next = { ...prev }
          delete next.requested_methods
          return next
        })
      }
    },
    [errors],
  )

  // ---------------------------------------------------------------------------
  // Validation
  // ---------------------------------------------------------------------------

  const validateStep = useCallback(
    (step: number): boolean => {
      const newErrors: FormErrors = {}

      switch (step) {
        case 1:
          if (!formData.company_name_kr.trim()) {
            newErrors.company_name_kr = '회사명(한글)은 필수 입력 항목입니다.'
          }
          break

        case 2:
          if (!formData.valuation_purpose) {
            newErrors.valuation_purpose = '평가 목적을 선택해주세요.'
          }
          if (formData.requested_methods.length === 0) {
            newErrors.requested_methods =
              '최소 1개의 평가 방법을 선택해주세요.'
          }
          break

        case 3: {
          const min = formData.budget_min
            ? parseInt(formData.budget_min, 10)
            : null
          const max = formData.budget_max
            ? parseInt(formData.budget_max, 10)
            : null

          if (min !== null && isNaN(min)) {
            newErrors.budget_min = '유효한 숫자를 입력해주세요.'
          }
          if (max !== null && isNaN(max)) {
            newErrors.budget_max = '유효한 숫자를 입력해주세요.'
          }
          if (min !== null && max !== null && !isNaN(min) && !isNaN(max) && min > max) {
            newErrors.budget_max =
              '최대 예산은 최소 예산보다 크거나 같아야 합니다.'
          }
          break
        }
      }

      setErrors(newErrors)
      return Object.keys(newErrors).length === 0
    },
    [formData],
  )

  // ---------------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------------

  const handleNext = useCallback(() => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, TOTAL_STEPS))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [currentStep, validateStep])

  const handlePrev = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
    setErrors({})
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  // ---------------------------------------------------------------------------
  // Submit
  // ---------------------------------------------------------------------------

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault()

      if (!validateStep(currentStep)) return

      setIsSubmitting(true)
      setSubmitError(null)

      try {
        const {
          data: { user },
        } = await supabase.auth.getUser()

        if (!user) {
          setSubmitError('로그인이 필요합니다. 로그인 후 다시 시도해주세요.')
          return
        }

        const budgetMin = formData.budget_min
          ? parseInt(formData.budget_min, 10)
          : null
        const budgetMax = formData.budget_max
          ? parseInt(formData.budget_max, 10)
          : null

        const { error } = await supabase
          .from('evaluation_requests')
          .insert({
            user_id: user.id,
            company_name_kr: formData.company_name_kr.trim(),
            company_name_en: formData.company_name_en.trim() || null,
            business_registration_number:
              formData.business_registration_number.trim() || null,
            representative_name:
              formData.representative_name.trim() || null,
            industry: formData.industry || null,
            valuation_purpose: formData.valuation_purpose,
            requested_methods: formData.requested_methods,
            target_date: formData.target_date || null,
            requirements: formData.requirements.trim() || null,
            budget_min: budgetMin,
            budget_max: budgetMax,
            status: 'pending',
          })

        if (error) {
          console.error('[ProjectCreatePage] Insert error:', error.message)
          setSubmitError('평가 요청 제출에 실패했습니다. 다시 시도해주세요.')
          return
        }

        // Success -> redirect
        router.push('/projects/list?created=true')
      } catch (err) {
        console.error('[ProjectCreatePage] Unexpected error:', err)
        setSubmitError('예기치 않은 오류가 발생했습니다.')
      } finally {
        setIsSubmitting(false)
      }
    },
    [supabase, formData, currentStep, validateStep, router],
  )

  // ---------------------------------------------------------------------------
  // Render: Step 1 - Company Information
  // ---------------------------------------------------------------------------

  const renderStep1 = () => (
    <div className="space-y-5">
      <h2 className="text-lg font-semibold text-gray-900">기업 정보</h2>
      <p className="text-sm text-gray-500">
        평가 대상 기업의 기본 정보를 입력해주세요.
      </p>

      {/* Company Name (Korean) */}
      <div>
        <FieldLabel htmlFor="company_name_kr" required>
          회사명 (한글)
        </FieldLabel>
        <input
          type="text"
          id="company_name_kr"
          name="company_name_kr"
          value={formData.company_name_kr}
          onChange={handleInputChange}
          placeholder="예: 주식회사 밸류링크"
          className={inputClassName(!!errors.company_name_kr)}
          aria-required="true"
          aria-invalid={!!errors.company_name_kr}
          aria-describedby={
            errors.company_name_kr ? 'company_name_kr-error' : undefined
          }
          maxLength={200}
        />
        {errors.company_name_kr && (
          <p
            id="company_name_kr-error"
            className="mt-1.5 text-sm text-red-600"
            role="alert"
          >
            {errors.company_name_kr}
          </p>
        )}
      </div>

      {/* Company Name (English) */}
      <div>
        <FieldLabel htmlFor="company_name_en">회사명 (영문)</FieldLabel>
        <input
          type="text"
          id="company_name_en"
          name="company_name_en"
          value={formData.company_name_en}
          onChange={handleInputChange}
          placeholder="예: ValueLink Inc."
          className={inputClassName(false)}
          maxLength={200}
        />
      </div>

      {/* Industry */}
      <div>
        <FieldLabel htmlFor="industry">업종</FieldLabel>
        <select
          id="industry"
          name="industry"
          value={formData.industry}
          onChange={handleInputChange}
          className={inputClassName(false)}
          aria-label="업종 선택"
        >
          <option value="">선택해주세요</option>
          {INDUSTRY_OPTIONS.map((industry) => (
            <option key={industry} value={industry}>
              {industry}
            </option>
          ))}
        </select>
      </div>

      {/* Representative Name */}
      <div>
        <FieldLabel htmlFor="representative_name">대표자명</FieldLabel>
        <input
          type="text"
          id="representative_name"
          name="representative_name"
          value={formData.representative_name}
          onChange={handleInputChange}
          placeholder="예: 홍길동"
          className={inputClassName(false)}
          maxLength={100}
        />
      </div>

      {/* Business Registration Number */}
      <div>
        <FieldLabel htmlFor="business_registration_number">
          사업자등록번호
        </FieldLabel>
        <input
          type="text"
          id="business_registration_number"
          name="business_registration_number"
          value={formData.business_registration_number}
          onChange={handleInputChange}
          placeholder="예: 123-45-67890"
          className={inputClassName(false)}
          maxLength={20}
        />
        <p className="mt-1 text-xs text-gray-400">
          하이픈(-)을 포함하여 입력해주세요.
        </p>
      </div>
    </div>
  )

  // ---------------------------------------------------------------------------
  // Render: Step 2 - Valuation Details
  // ---------------------------------------------------------------------------

  const renderStep2 = () => (
    <div className="space-y-5">
      <h2 className="text-lg font-semibold text-gray-900">평가 상세</h2>
      <p className="text-sm text-gray-500">
        가치평가의 목적과 원하는 평가 방법을 선택해주세요.
      </p>

      {/* Valuation Purpose */}
      <div>
        <FieldLabel htmlFor="valuation_purpose" required>
          평가 목적
        </FieldLabel>
        <select
          id="valuation_purpose"
          name="valuation_purpose"
          value={formData.valuation_purpose}
          onChange={handleInputChange}
          className={inputClassName(!!errors.valuation_purpose)}
          aria-required="true"
          aria-invalid={!!errors.valuation_purpose}
          aria-describedby={
            errors.valuation_purpose ? 'valuation_purpose-error' : undefined
          }
        >
          <option value="">선택해주세요</option>
          {PURPOSE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <FieldError message={errors.valuation_purpose} />
      </div>

      {/* Requested Methods (multi-select checkboxes) */}
      <fieldset>
        <legend className="mb-1.5 block text-sm font-medium text-gray-700">
          평가 방법{' '}
          <span className="text-red-500" aria-hidden="true">
            *
          </span>
        </legend>
        <p className="mb-3 text-xs text-gray-400">
          하나 이상의 평가 방법을 선택해주세요.
        </p>
        <div className="space-y-2" role="group" aria-label="평가 방법 선택">
          {METHOD_OPTIONS.map((method) => {
            const isChecked = formData.requested_methods.includes(
              method.value,
            )
            return (
              <label
                key={method.value}
                className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3.5 transition-all ${
                  isChecked
                    ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500/20'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => handleMethodToggle(method.value)}
                  className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  aria-label={method.label}
                />
                <div>
                  <span className="text-sm font-medium text-gray-900">
                    {method.label}
                  </span>
                  <p className="mt-0.5 text-xs text-gray-500">
                    {method.description}
                  </p>
                </div>
              </label>
            )
          })}
        </div>
        {errors.requested_methods && (
          <p className="mt-2 text-sm text-red-600" role="alert">
            {errors.requested_methods}
          </p>
        )}
      </fieldset>

      {/* Target Date */}
      <div>
        <FieldLabel htmlFor="target_date">희망 완료일</FieldLabel>
        <input
          type="date"
          id="target_date"
          name="target_date"
          value={formData.target_date}
          onChange={handleInputChange}
          className={inputClassName(false)}
          min={new Date().toISOString().split('T')[0]}
        />
        <p className="mt-1 text-xs text-gray-400">
          평가 완료를 희망하는 날짜를 선택해주세요.
        </p>
      </div>

      {/* Requirements */}
      <div>
        <FieldLabel htmlFor="requirements">추가 요구사항</FieldLabel>
        <textarea
          id="requirements"
          name="requirements"
          value={formData.requirements}
          onChange={handleInputChange}
          rows={4}
          placeholder="평가에 대한 추가 요구사항이나 참고할 사항을 입력해주세요."
          className={`${inputClassName(false)} resize-y`}
          maxLength={2000}
        />
        <p className="mt-1 text-right text-xs text-gray-400">
          {formData.requirements.length}/2000
        </p>
      </div>
    </div>
  )

  // ---------------------------------------------------------------------------
  // Render: Step 3 - Budget & Confirmation
  // ---------------------------------------------------------------------------

  const renderStep3 = () => (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">예산 및 확인</h2>
      <p className="text-sm text-gray-500">
        예산 범위를 설정하고, 입력하신 내용을 확인해주세요.
      </p>

      {/* Budget */}
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="mb-4 text-sm font-semibold text-gray-700">
          예산 범위 (선택사항)
        </h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <FieldLabel htmlFor="budget_min">최소 예산 (원)</FieldLabel>
            <input
              type="number"
              id="budget_min"
              name="budget_min"
              value={formData.budget_min}
              onChange={handleInputChange}
              placeholder="예: 3000000"
              className={inputClassName(!!errors.budget_min)}
              min="0"
              step="100000"
              aria-invalid={!!errors.budget_min}
              aria-describedby={
                errors.budget_min ? 'budget_min-error' : undefined
              }
            />
            {formData.budget_min && !errors.budget_min && (
              <p className="mt-1 text-xs text-gray-500">
                {parseInt(formData.budget_min, 10).toLocaleString('ko-KR')}원
              </p>
            )}
            <FieldError message={errors.budget_min} />
          </div>
          <div>
            <FieldLabel htmlFor="budget_max">최대 예산 (원)</FieldLabel>
            <input
              type="number"
              id="budget_max"
              name="budget_max"
              value={formData.budget_max}
              onChange={handleInputChange}
              placeholder="예: 10000000"
              className={inputClassName(!!errors.budget_max)}
              min="0"
              step="100000"
              aria-invalid={!!errors.budget_max}
              aria-describedby={
                errors.budget_max ? 'budget_max-error' : undefined
              }
            />
            {formData.budget_max && !errors.budget_max && (
              <p className="mt-1 text-xs text-gray-500">
                {parseInt(formData.budget_max, 10).toLocaleString('ko-KR')}원
              </p>
            )}
            <FieldError message={errors.budget_max} />
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <h3 className="mb-4 text-sm font-semibold text-gray-700">
          입력 내용 확인
        </h3>

        <dl className="divide-y divide-gray-100">
          {/* Company Info */}
          <div className="py-3 sm:flex sm:gap-4">
            <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
              회사명
            </dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
              {formData.company_name_kr}
              {formData.company_name_en && (
                <span className="ml-2 text-gray-500">
                  ({formData.company_name_en})
                </span>
              )}
            </dd>
          </div>

          {formData.industry && (
            <div className="py-3 sm:flex sm:gap-4">
              <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
                업종
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
                {formData.industry}
              </dd>
            </div>
          )}

          {formData.representative_name && (
            <div className="py-3 sm:flex sm:gap-4">
              <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
                대표자
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
                {formData.representative_name}
              </dd>
            </div>
          )}

          {formData.business_registration_number && (
            <div className="py-3 sm:flex sm:gap-4">
              <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
                사업자등록번호
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
                {formData.business_registration_number}
              </dd>
            </div>
          )}

          <div className="py-3 sm:flex sm:gap-4">
            <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
              평가 목적
            </dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
              {PURPOSE_OPTIONS.find(
                (o) => o.value === formData.valuation_purpose,
              )?.label ?? formData.valuation_purpose}
            </dd>
          </div>

          <div className="py-3 sm:flex sm:gap-4">
            <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
              평가 방법
            </dt>
            <dd className="mt-1 sm:mt-0">
              <div className="flex flex-wrap gap-1.5">
                {formData.requested_methods.map((method) => {
                  const opt = METHOD_OPTIONS.find((o) => o.value === method)
                  return (
                    <span
                      key={method}
                      className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
                    >
                      {opt?.label ?? method}
                    </span>
                  )
                })}
              </div>
            </dd>
          </div>

          {formData.target_date && (
            <div className="py-3 sm:flex sm:gap-4">
              <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
                희망 완료일
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
                {new Date(formData.target_date).toLocaleDateString('ko-KR')}
              </dd>
            </div>
          )}

          {formData.requirements && (
            <div className="py-3 sm:flex sm:gap-4">
              <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
                추가 요구사항
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 whitespace-pre-wrap">
                {formData.requirements}
              </dd>
            </div>
          )}

          {(formData.budget_min || formData.budget_max) && (
            <div className="py-3 sm:flex sm:gap-4">
              <dt className="text-sm font-medium text-gray-500 sm:w-40 sm:shrink-0">
                예산 범위
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0">
                {formData.budget_min
                  ? `${parseInt(formData.budget_min, 10).toLocaleString('ko-KR')}원`
                  : '-'}{' '}
                ~{' '}
                {formData.budget_max
                  ? `${parseInt(formData.budget_max, 10).toLocaleString('ko-KR')}원`
                  : '-'}
              </dd>
            </div>
          )}
        </dl>
      </div>

      {/* Notice */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700">
        <div className="flex items-start gap-2">
          <svg
            className="mt-0.5 h-4 w-4 shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <p className="font-medium">안내사항</p>
            <p className="mt-1 text-blue-600">
              평가 요청이 제출되면 관리자 검토 후 프로젝트가 생성됩니다.
              검토 결과는 이메일로 안내드립니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  // ---------------------------------------------------------------------------
  // Render: Page
  // ---------------------------------------------------------------------------

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Back navigation */}
      <button
        type="button"
        onClick={() => router.push('/projects/list')}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-700"
        aria-label="프로젝트 목록으로 돌아가기"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        프로젝트 목록
      </button>

      {/* Page Title */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">새 프로젝트 요청</h1>
        <p className="mt-1 text-sm text-gray-500">
          기업 가치평가를 요청하려면 아래 양식을 작성해주세요.
        </p>
      </div>

      {/* Step Indicator */}
      <StepIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />

      {/* Form */}
      <form onSubmit={handleSubmit} noValidate>
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          {/* Step content */}
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}

          {/* Submit error */}
          {submitError && (
            <div
              className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
              role="alert"
            >
              <div className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
                <span>{submitError}</span>
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="mt-8 flex items-center justify-between border-t border-gray-100 pt-5">
            {currentStep > 1 ? (
              <button
                type="button"
                onClick={handlePrev}
                className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                disabled={isSubmitting}
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                이전
              </button>
            ) : (
              <div />
            )}

            {currentStep < TOTAL_STEPS ? (
              <button
                type="button"
                onClick={handleNext}
                className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                다음
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            ) : (
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSubmitting ? (
                  <>
                    <svg
                      className="h-4 w-4 animate-spin"
                      fill="none"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    제출 중...
                  </>
                ) : (
                  <>
                    평가 요청 제출
                    <svg
                      className="h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </form>
    </main>
  )
}
