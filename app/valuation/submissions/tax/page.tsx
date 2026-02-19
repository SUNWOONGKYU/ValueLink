/**
 * @task S2F2
 * @description 상증세법 보충적 평가 (Tax Valuation) 평가 신청 페이지
 *
 * 입력 필드:
 * - Step 1: 기업 기본 정보 (공통)
 * - Step 2: 순자산가치, 최근 3년 순손익, 세법상 평가 목적
 * - Step 3: 주식 정보(액면가, 발행수), 주주 정보, 회사 유형/가중치
 *
 * 제출 → evaluation_requests 테이블 INSERT
 */

'use client'

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import SubmissionFormTemplate from '@/components/submission-form-template'
import FormField from '@/components/form-field'
import type {
  TaxFormData,
  YearlyEarningsInput,
  StockholderInput,
  FormStep,
} from '@/types/valuation-forms'
import { VALUATION_PURPOSES } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const STEPS: FormStep[] = [
  { id: 'company', label: '기업 정보', description: '기본 기업 정보를 입력합니다.' },
  { id: 'financials', label: '재무/손익', description: '순자산가치, 3년 순손익을 입력합니다.' },
  { id: 'shares', label: '주식/주주', description: '주식 정보와 주주 현황을 입력합니다.' },
]

const CURRENT_YEAR = new Date().getFullYear()

const TAX_PURPOSE_OPTIONS = [
  { value: 'inheritance', label: '상속세 신고' },
  { value: 'gift', label: '증여세 신고' },
  { value: 'transfer', label: '양도소득세 신고' },
  { value: 'merger', label: '합병/분할 시 평가' },
  { value: 'treasury', label: '자기주식 취득' },
  { value: 'other', label: '기타' },
]

const COMPANY_TYPE_OPTIONS = [
  { value: 'general', label: '일반법인 (수익 60% / 자산 40%)' },
  { value: 'realestate', label: '부동산과다법인 (수익 40% / 자산 60%)' },
]

function makeInitialEarnings(): YearlyEarningsInput[] {
  return [
    { year_label: `${CURRENT_YEAR - 1}년`, net_income: 0, weight: 3 },
    { year_label: `${CURRENT_YEAR - 2}년`, net_income: 0, weight: 2 },
    { year_label: `${CURRENT_YEAR - 3}년`, net_income: 0, weight: 1 },
  ]
}

function makeEmptyStockholder(): StockholderInput {
  return { name: '', shares: 0, ownership_percentage: 0, relationship: '' }
}

function makeInitialData(): TaxFormData {
  return {
    company_name_kr: '',
    valuation_purpose: 'tax',
    net_asset_value: 0,
    earnings_history: makeInitialEarnings(),
    tax_purpose: '',
    par_value_per_share: 5000,
    shares_outstanding: 0,
    stockholder_info: [makeEmptyStockholder()],
    company_type: 'general',
    asset_weight: 40,
    income_weight: 60,
  }
}

// ---------------------------------------------------------------------------
// 유효성 검사
// ---------------------------------------------------------------------------

function validate(data: TaxFormData, step: number): string[] {
  const errs: string[] = []

  if (step === 0) {
    if (!data.company_name_kr.trim()) errs.push('기업명(한글)은 필수입니다.')
    if (!data.valuation_purpose) errs.push('평가 목적을 선택해주세요.')
  }

  if (step === 1) {
    if (data.net_asset_value <= 0) errs.push('순자산가치는 0보다 커야 합니다.')
    if (!data.tax_purpose) errs.push('세법상 평가 목적을 선택해주세요.')
    const hasEarnings = data.earnings_history.some((e) => e.net_income !== 0)
    if (!hasEarnings) errs.push('최소 1개년 순손익을 입력해주세요.')
  }

  if (step === 2) {
    if (data.par_value_per_share <= 0) errs.push('액면가는 0보다 커야 합니다.')
    if (data.shares_outstanding <= 0) errs.push('발행주식수는 0보다 커야 합니다.')
    const validHolders = data.stockholder_info.filter((h) => h.name.trim())
    if (validHolders.length === 0) errs.push('최소 1명의 주주 정보를 입력해주세요.')
    const totalOwnership = validHolders.reduce((sum, h) => sum + h.ownership_percentage, 0)
    if (validHolders.length > 0 && Math.abs(totalOwnership - 100) > 0.01)
      errs.push(`지분율 합계가 100%여야 합니다. (현재: ${totalOwnership.toFixed(2)}%)`)
  }

  return errs
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function TaxSubmissionPage() {
  const router = useRouter()
  const [data, setData] = useState<TaxFormData>(makeInitialData)
  const [currentStep, setCurrentStep] = useState(0)
  const [errors, setErrors] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null)

  // --- 필드 변경 ---
  const updateField = useCallback(
    <K extends keyof TaxFormData>(key: K, value: TaxFormData[K]) => {
      setData((prev) => ({ ...prev, [key]: value }))
    },
    [],
  )

  const updateEarning = useCallback(
    (index: number, field: keyof YearlyEarningsInput, value: string | number) => {
      setData((prev) => {
        const next = [...prev.earnings_history]
        next[index] = { ...next[index], [field]: value }
        return { ...prev, earnings_history: next }
      })
    },
    [],
  )

  const updateStockholder = useCallback(
    (index: number, field: keyof StockholderInput, value: string | number) => {
      setData((prev) => {
        const next = [...prev.stockholder_info]
        next[index] = { ...next[index], [field]: value }
        return { ...prev, stockholder_info: next }
      })
    },
    [],
  )

  const addStockholder = useCallback(() => {
    setData((prev) => ({
      ...prev,
      stockholder_info: [...prev.stockholder_info, makeEmptyStockholder()],
    }))
  }, [])

  const removeStockholder = useCallback((index: number) => {
    setData((prev) => ({
      ...prev,
      stockholder_info: prev.stockholder_info.filter((_, i) => i !== index),
    }))
  }, [])

  // 회사 유형 변경 시 가중치 자동 설정
  const updateCompanyType = useCallback((type: 'general' | 'realestate') => {
    setData((prev) => ({
      ...prev,
      company_type: type,
      asset_weight: type === 'general' ? 40 : 60,
      income_weight: type === 'general' ? 60 : 40,
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
      sessionStorage.setItem('tax_draft', JSON.stringify(data))
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

    if (!window.confirm('상증세법 평가 신청을 제출하시겠습니까?')) return

    setIsSubmitting(true)
    setErrors([])

    try {
      // TODO: Supabase evaluation_requests INSERT
      await new Promise((resolve) => setTimeout(resolve, 1500))

      try {
        sessionStorage.removeItem('tax_draft')
      } catch {
        // 무시
      }

      router.push('/valuation/submissions?submitted=tax')
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
          id="representative_name"
          label="대표자명"
          value={data.representative_name ?? ''}
          onChange={(e) => updateField('representative_name', e.currentTarget.value)}
          placeholder="예: 홍길동"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
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
        <FormField
          id="target_date"
          label="평가 기준일"
          fieldType="date"
          value={data.target_date ?? ''}
          onChange={(e) => updateField('target_date', e.currentTarget.value)}
          helpText="상속개시일 또는 증여일"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="address"
          label="소재지"
          value={data.address ?? ''}
          onChange={(e) => updateField('address', e.currentTarget.value)}
          placeholder="예: 서울시 강남구 테헤란로 123"
        />
        <FormField
          id="industry"
          label="업종"
          value={data.industry ?? ''}
          onChange={(e) => updateField('industry', e.currentTarget.value)}
          placeholder="예: 소프트웨어 개발업"
        />
      </div>

      <FormField
        id="requirements"
        label="요구사항"
        fieldType="textarea"
        value={data.requirements ?? ''}
        onChange={(e) => updateField('requirements', e.currentTarget.value)}
        placeholder="세무 관련 특이사항이 있으시면 입력해주세요."
        rows={3}
      />
    </div>
  )

  const renderStep1 = () => {
    // 가중평균 순손익 자동 계산
    const totalWeight = data.earnings_history.reduce((s, e) => s + e.weight, 0)
    const weightedSum = data.earnings_history.reduce(
      (s, e) => s + e.net_income * e.weight,
      0,
    )
    const weightedAvg = totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0

    return (
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
          순자산가치 및 순손익
        </h2>

        <FormField
          id="net_asset_value"
          label="순자산가치 (원)"
          fieldType="number"
          required
          value={data.net_asset_value || ''}
          onChange={(e) =>
            updateField('net_asset_value', Number(e.currentTarget.value) || 0)
          }
          placeholder="0"
          min={0}
          helpText="상증세법 시행령 제55조에 따른 순자산가치"
        />

        <FormField
          id="tax_purpose"
          label="세법상 평가 목적"
          required
          fieldType="select"
          value={data.tax_purpose}
          onChange={(e) => updateField('tax_purpose', e.currentTarget.value)}
          options={TAX_PURPOSE_OPTIONS}
          placeholder="평가 목적을 선택해주세요"
        />

        {/* 3년 순손익 */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-base font-medium text-gray-800 mb-2">
            최근 3년 순손익
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            상증세법 시행령 제56조에 따른 가중평균 방식 (최근: 3, 전년: 2, 전전년: 1)
          </p>

          <div className="space-y-4">
            {data.earnings_history.map((earning, index) => (
              <div
                key={index}
                className="rounded-lg border border-gray-200 bg-gray-50/50 p-4"
              >
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
                  <FormField
                    id={`earning_${index}_year`}
                    label="연도"
                    value={earning.year_label}
                    onChange={(e) =>
                      updateEarning(index, 'year_label', e.currentTarget.value)
                    }
                    disabled
                  />
                  <FormField
                    id={`earning_${index}_income`}
                    label="순손익 (원)"
                    fieldType="number"
                    required={index === 0}
                    value={earning.net_income || ''}
                    onChange={(e) =>
                      updateEarning(index, 'net_income', Number(e.currentTarget.value) || 0)
                    }
                    placeholder="0"
                    helpText={`가중치: ${earning.weight}`}
                  />
                  <FormField
                    id={`earning_${index}_weight`}
                    label="가중치"
                    fieldType="number"
                    value={earning.weight}
                    onChange={(e) =>
                      updateEarning(index, 'weight', Number(e.currentTarget.value) || 0)
                    }
                    min={0}
                    max={10}
                    step={1}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* 가중평균 순손익 자동 표시 */}
          {weightedAvg !== 0 && (
            <div className="mt-4 rounded-lg bg-blue-50 border border-blue-200 p-4">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">가중평균 순손익:</span>{' '}
                {weightedAvg.toLocaleString('ko-KR')}원
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  const renderStep2 = () => {
    const totalOwnership = data.stockholder_info
      .filter((h) => h.name.trim())
      .reduce((sum, h) => sum + h.ownership_percentage, 0)

    return (
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
          주식 및 주주 정보
        </h2>

        {/* 회사 유형 */}
        <FormField
          id="company_type"
          label="회사 유형"
          required
          fieldType="select"
          value={data.company_type}
          onChange={(e) =>
            updateCompanyType(e.currentTarget.value as 'general' | 'realestate')
          }
          options={COMPANY_TYPE_OPTIONS}
          helpText="부동산과다법인: 부동산 등 비율이 80% 이상인 법인"
        />

        {/* 자동 설정된 가중치 표시 */}
        <div className="rounded-lg bg-gray-50 border border-gray-200 p-4">
          <p className="text-sm text-gray-700">
            <span className="font-medium">적용 가중치:</span>{' '}
            수익가치 {data.income_weight}% / 자산가치 {data.asset_weight}%
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FormField
            id="par_value_per_share"
            label="1주당 액면가 (원)"
            fieldType="number"
            required
            value={data.par_value_per_share || ''}
            onChange={(e) =>
              updateField('par_value_per_share', Number(e.currentTarget.value) || 0)
            }
            placeholder="5000"
            min={0}
            helpText="통상 5,000원 또는 500원"
          />
          <FormField
            id="shares_outstanding"
            label="발행주식수"
            fieldType="number"
            required
            value={data.shares_outstanding || ''}
            onChange={(e) =>
              updateField('shares_outstanding', Number(e.currentTarget.value) || 0)
            }
            placeholder="예: 100000"
            min={1}
          />
        </div>

        {/* 주주 정보 */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-base font-medium text-gray-800 mb-2">주주 현황</h3>
          <p className="text-sm text-gray-500 mb-4">
            최대주주 및 특수관계인 정보를 입력하세요. 지분율 합계는 100%가 되어야 합니다.
          </p>

          <div className="space-y-4">
            {data.stockholder_info.map((holder, index) => (
              <div
                key={index}
                className="rounded-lg border border-gray-200 bg-gray-50/50 p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-gray-700">
                    주주 #{index + 1}
                  </span>
                  {data.stockholder_info.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeStockholder(index)}
                      className="text-sm text-red-600 hover:text-red-800 transition-colors"
                      aria-label={`주주 #${index + 1} 삭제`}
                    >
                      삭제
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <FormField
                    id={`holder_${index}_name`}
                    label="주주명"
                    required={index === 0}
                    value={holder.name}
                    onChange={(e) =>
                      updateStockholder(index, 'name', e.currentTarget.value)
                    }
                    placeholder="예: 홍길동"
                  />
                  <FormField
                    id={`holder_${index}_shares`}
                    label="보유 주식수"
                    fieldType="number"
                    value={holder.shares || ''}
                    onChange={(e) =>
                      updateStockholder(index, 'shares', Number(e.currentTarget.value) || 0)
                    }
                    placeholder="0"
                    min={0}
                  />
                  <FormField
                    id={`holder_${index}_ownership`}
                    label="지분율 (%)"
                    fieldType="number"
                    value={holder.ownership_percentage || ''}
                    onChange={(e) =>
                      updateStockholder(
                        index,
                        'ownership_percentage',
                        Number(e.currentTarget.value) || 0,
                      )
                    }
                    placeholder="0"
                    min={0}
                    max={100}
                    step={0.01}
                  />
                  <FormField
                    id={`holder_${index}_relationship`}
                    label="관계"
                    value={holder.relationship ?? ''}
                    onChange={(e) =>
                      updateStockholder(index, 'relationship', e.currentTarget.value)
                    }
                    placeholder="예: 최대주주"
                    helpText="최대주주, 특수관계인 등"
                  />
                </div>
              </div>
            ))}
          </div>

          {/* 지분율 합계 */}
          <div
            className={`mt-3 flex items-center gap-2 text-sm font-medium ${
              Math.abs(totalOwnership - 100) < 0.01
                ? 'text-green-600'
                : totalOwnership > 0
                  ? 'text-red-600'
                  : 'text-gray-400'
            }`}
          >
            <span>지분율 합계: {totalOwnership.toFixed(2)}%</span>
            {Math.abs(totalOwnership - 100) < 0.01 && (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </div>

          <button
            type="button"
            onClick={addStockholder}
            className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-dashed border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-600 hover:border-blue-400 hover:text-blue-700 transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            주주 추가
          </button>
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
      method="tax"
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
