/**
 * @task S2F2
 * @description 본질가치평가 (Intrinsic Value / 자본시장법) 평가 신청 페이지
 *
 * 입력 필드:
 * - Step 1: 기업 기본 정보 (공통)
 * - Step 2: 기대수익, 요구수익률, 성장률, 배당 정보
 * - Step 3: 장부가치, 가중치 설정, 발행주식수
 *
 * 제출 → evaluation_requests 테이블 INSERT
 */

'use client'

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import SubmissionFormTemplate from '@/components/submission-form-template'
import FormField from '@/components/form-field'
import type { IntrinsicFormData, FormStep } from '@/types/valuation-forms'
import { VALUATION_PURPOSES } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const STEPS: FormStep[] = [
  { id: 'company', label: '기업 정보', description: '기본 기업 정보를 입력합니다.' },
  { id: 'earnings', label: '수익/성장', description: '기대수익, 성장률, 배당 정보를 입력합니다.' },
  { id: 'value', label: '가치 산정', description: '장부가치, 가중치 등을 설정합니다.' },
]

function makeInitialData(): IntrinsicFormData {
  return {
    company_name_kr: '',
    valuation_purpose: '',
    expected_earnings: 0,
    required_return_rate: 0,
    growth_rate: 0,
    book_value: 0,
    asset_weight: 40,
    income_weight: 60,
    shares_outstanding: 0,
  }
}

// ---------------------------------------------------------------------------
// 유효성 검사
// ---------------------------------------------------------------------------

function validate(data: IntrinsicFormData, step: number): string[] {
  const errs: string[] = []

  if (step === 0) {
    if (!data.company_name_kr.trim()) errs.push('기업명(한글)은 필수입니다.')
    if (!data.valuation_purpose) errs.push('평가 목적을 선택해주세요.')
  }

  if (step === 1) {
    if (data.expected_earnings <= 0) errs.push('기대수익은 0보다 커야 합니다.')
    if (data.required_return_rate <= 0) errs.push('요구수익률은 0보다 커야 합니다.')
    if (data.growth_rate < 0) errs.push('성장률은 0 이상이어야 합니다.')
    if (data.growth_rate >= data.required_return_rate)
      errs.push('성장률은 요구수익률보다 작아야 합니다.')
  }

  if (step === 2) {
    if (data.book_value <= 0) errs.push('장부가치는 0보다 커야 합니다.')
    if (data.shares_outstanding <= 0) errs.push('발행주식수는 0보다 커야 합니다.')
    const totalWeight = data.asset_weight + data.income_weight
    if (Math.abs(totalWeight - 100) > 0.01)
      errs.push(`자산/수익 가중치 합이 100%여야 합니다. (현재: ${totalWeight}%)`)
  }

  return errs
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function IntrinsicSubmissionPage() {
  const router = useRouter()
  const [data, setData] = useState<IntrinsicFormData>(makeInitialData)
  const [currentStep, setCurrentStep] = useState(0)
  const [errors, setErrors] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null)

  // --- 필드 변경 ---
  const updateField = useCallback(
    <K extends keyof IntrinsicFormData>(key: K, value: IntrinsicFormData[K]) => {
      setData((prev) => ({ ...prev, [key]: value }))
    },
    [],
  )

  // 가중치 연동 업데이트 (asset + income = 100)
  const updateAssetWeight = useCallback((value: number) => {
    const clamped = Math.min(100, Math.max(0, value))
    setData((prev) => ({
      ...prev,
      asset_weight: clamped,
      income_weight: 100 - clamped,
    }))
  }, [])

  const updateIncomeWeight = useCallback((value: number) => {
    const clamped = Math.min(100, Math.max(0, value))
    setData((prev) => ({
      ...prev,
      income_weight: clamped,
      asset_weight: 100 - clamped,
    }))
  }, [])

  // --- 단계 이동 ---
  const handleStepChange = useCallback(
    (step: number) => {
      if (step > currentStep) {
        const errs = validate(data, currentStep)
        if (errs.length > 0) {
          setErrors(errs)
          return
        }
      }
      setErrors([])
      setCurrentStep(step)
    },
    [currentStep, data],
  )

  // --- 자동 저장 ---
  const handleAutoSave = useCallback(() => {
    try {
      sessionStorage.setItem('intrinsic_draft', JSON.stringify(data))
      setLastSavedAt(new Date())
    } catch {
      // 무시
    }
  }, [data])

  // --- 제출 ---
  const handleSubmit = useCallback(async () => {
    const errs = validate(data, currentStep)
    if (errs.length > 0) {
      setErrors(errs)
      return
    }

    if (!window.confirm('본질가치 평가 신청을 제출하시겠습니까?')) return

    setIsSubmitting(true)
    setErrors([])

    try {
      // TODO: Supabase evaluation_requests INSERT
      await new Promise((resolve) => setTimeout(resolve, 1500))

      try {
        sessionStorage.removeItem('intrinsic_draft')
      } catch {
        // 무시
      }

      router.push('/valuation/submissions?submitted=intrinsic')
    } catch {
      setErrors(['제출 중 오류가 발생했습니다. 다시 시도해주세요.'])
    } finally {
      setIsSubmitting(false)
    }
  }, [data, currentStep, router])

  // --- 렌더: 단계별 필드 ---

  const renderStep0 = () => (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
        기업 기본 정보
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="company_name_kr"
          label="기업명 (한글)"
          required
          value={data.company_name_kr}
          onChange={(e) => updateField('company_name_kr', e.currentTarget.value)}
          placeholder="예: 테크이노"
        />
        <FormField
          id="company_name_en"
          label="기업명 (영문)"
          value={data.company_name_en ?? ''}
          onChange={(e) => updateField('company_name_en', e.currentTarget.value)}
          placeholder="예: TechInno Inc."
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="business_registration_number"
          label="사업자등록번호"
          value={data.business_registration_number ?? ''}
          onChange={(e) => updateField('business_registration_number', e.currentTarget.value)}
          placeholder="000-00-00000"
        />
        <FormField
          id="valuation_purpose"
          label="평가 목적"
          required
          fieldType="select"
          value={data.valuation_purpose}
          onChange={(e) => updateField('valuation_purpose', e.currentTarget.value)}
          options={VALUATION_PURPOSES.map((p) => ({ value: p.value, label: p.label }))}
          placeholder="평가 목적을 선택해주세요"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="industry"
          label="업종"
          value={data.industry ?? ''}
          onChange={(e) => updateField('industry', e.currentTarget.value)}
          placeholder="예: 제조업"
          helpText="환원율 결정에 참고됩니다."
        />
        <FormField
          id="target_date"
          label="평가 기준일"
          fieldType="date"
          value={data.target_date ?? ''}
          onChange={(e) => updateField('target_date', e.currentTarget.value)}
        />
      </div>

      <FormField
        id="requirements"
        label="요구사항"
        fieldType="textarea"
        value={data.requirements ?? ''}
        onChange={(e) => updateField('requirements', e.currentTarget.value)}
        placeholder="평가 관련 추가 요구사항이 있으시면 입력해주세요."
        rows={3}
      />
    </div>
  )

  const renderStep1 = () => (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
        수익 및 성장 정보
      </h2>
      <p className="text-sm text-gray-500">
        자본시장법에 따른 본질가치 산정을 위한 수익 정보를 입력하세요.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="expected_earnings"
          label="기대수익 (원)"
          fieldType="number"
          required
          value={data.expected_earnings || ''}
          onChange={(e) =>
            updateField('expected_earnings', Number(e.currentTarget.value) || 0)
          }
          placeholder="0"
          min={0}
          helpText="향후 예상되는 연간 수익"
        />
        <FormField
          id="required_return_rate"
          label="요구수익률 (%)"
          fieldType="number"
          required
          value={data.required_return_rate || ''}
          onChange={(e) =>
            updateField('required_return_rate', Number(e.currentTarget.value) || 0)
          }
          placeholder="예: 10.0"
          min={0}
          max={100}
          step={0.1}
          helpText="투자자의 기대 수익률"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="growth_rate"
          label="성장률 (%)"
          fieldType="number"
          required
          value={data.growth_rate || ''}
          onChange={(e) =>
            updateField('growth_rate', Number(e.currentTarget.value) || 0)
          }
          placeholder="예: 3.0"
          min={0}
          max={100}
          step={0.1}
          helpText="장기 수익 성장률 (요구수익률 미만)"
        />
        <FormField
          id="capitalization_rate"
          label="환원율 (%)"
          fieldType="number"
          value={data.capitalization_rate ?? ''}
          onChange={(e) =>
            updateField('capitalization_rate', Number(e.currentTarget.value) || undefined)
          }
          placeholder="예: 10.0"
          min={0}
          max={100}
          step={0.1}
          helpText="선택사항 - 업종별 환원율 (미입력 시 자동 산정)"
        />
      </div>

      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-base font-medium text-gray-800 mb-4">배당 정보 (선택)</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FormField
            id="dividend_amount"
            label="배당금 (원)"
            fieldType="number"
            value={data.dividend_amount ?? ''}
            onChange={(e) =>
              updateField('dividend_amount', Number(e.currentTarget.value) || undefined)
            }
            placeholder="0"
            min={0}
            helpText="연간 총 배당금"
          />
          <FormField
            id="dividend_payout_ratio"
            label="배당성향 (%)"
            fieldType="number"
            value={data.dividend_payout_ratio ?? ''}
            onChange={(e) =>
              updateField('dividend_payout_ratio', Number(e.currentTarget.value) || undefined)
            }
            placeholder="예: 30"
            min={0}
            max={100}
            step={1}
            helpText="순이익 대비 배당금 비율"
          />
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => {
    const totalWeight = data.asset_weight + data.income_weight

    return (
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
          가치 산정 설정
        </h2>

        <FormField
          id="book_value"
          label="장부가치 (원)"
          fieldType="number"
          required
          value={data.book_value || ''}
          onChange={(e) =>
            updateField('book_value', Number(e.currentTarget.value) || 0)
          }
          placeholder="0"
          min={0}
          helpText="재무상태표 기준 자기자본 (순자산)"
        />

        {/* 가중치 설정 */}
        <div className="rounded-lg border border-gray-200 bg-gray-50/50 p-5 space-y-4">
          <h3 className="text-base font-medium text-gray-800">
            가중치 설정
          </h3>
          <p className="text-sm text-gray-500">
            자본시장법 기준: 수익가치 60% + 자산가치 40% (합계 100%)
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <FormField
              id="asset_weight"
              label="자산가치 가중치 (%)"
              fieldType="number"
              required
              value={data.asset_weight}
              onChange={(e) => updateAssetWeight(Number(e.currentTarget.value) || 0)}
              min={0}
              max={100}
              step={5}
              helpText="기본값: 40%"
            />
            <FormField
              id="income_weight"
              label="수익가치 가중치 (%)"
              fieldType="number"
              required
              value={data.income_weight}
              onChange={(e) => updateIncomeWeight(Number(e.currentTarget.value) || 0)}
              min={0}
              max={100}
              step={5}
              helpText="기본값: 60%"
            />
          </div>

          <div
            className={`flex items-center gap-2 text-sm font-medium ${
              Math.abs(totalWeight - 100) < 0.01
                ? 'text-green-600'
                : 'text-red-600'
            }`}
          >
            <span>가중치 합계: {totalWeight}%</span>
            {Math.abs(totalWeight - 100) < 0.01 && (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FormField
            id="shares_outstanding"
            label="발행주식수"
            fieldType="number"
            required
            value={data.shares_outstanding || ''}
            onChange={(e) =>
              updateField('shares_outstanding', Number(e.currentTarget.value) || 0)
            }
            placeholder="예: 1000000"
            min={1}
            helpText="총 발행 주식수"
          />
        </div>

        {/* 예산 범위 */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-base font-medium text-gray-800 mb-4">예산 범위 (선택)</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <FormField
              id="budget_min"
              label="예산 하한 (원)"
              fieldType="number"
              value={data.budget_min ?? ''}
              onChange={(e) =>
                updateField('budget_min', Number(e.currentTarget.value) || undefined)
              }
              placeholder="0"
              min={0}
            />
            <FormField
              id="budget_max"
              label="예산 상한 (원)"
              fieldType="number"
              value={data.budget_max ?? ''}
              onChange={(e) =>
                updateField('budget_max', Number(e.currentTarget.value) || undefined)
              }
              placeholder="0"
              min={0}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <SubmissionFormTemplate
      method="intrinsic"
      steps={STEPS}
      currentStep={currentStep}
      onStepChange={handleStepChange}
      onSubmit={handleSubmit}
      isSubmitting={isSubmitting}
      errors={errors}
      lastSavedAt={lastSavedAt}
      onAutoSave={handleAutoSave}
    >
      {currentStep === 0 && renderStep0()}
      {currentStep === 1 && renderStep1()}
      {currentStep === 2 && renderStep2()}
    </SubmissionFormTemplate>
  )
}
