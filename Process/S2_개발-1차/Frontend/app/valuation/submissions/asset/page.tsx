/**
 * @task S2F2
 * @description 자산가치평가 (Asset Valuation / NAV) 평가 신청 페이지
 *
 * 입력 필드:
 * - Step 1: 기업 기본 정보 (공통)
 * - Step 2: 총자산, 총부채, 유형/무형 자산 상세
 * - Step 3: 부동산, 설비, 재고, 발행주식수
 *
 * 제출 → evaluation_requests 테이블 INSERT
 */

'use client'

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import SubmissionFormTemplate from '@/components/submission-form-template'
import FormField from '@/components/form-field'
import type {
  AssetFormData,
  AssetDetailItem,
  FormStep,
} from '@/types/valuation-forms'
import { VALUATION_PURPOSES } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const STEPS: FormStep[] = [
  { id: 'company', label: '기업 정보', description: '기본 기업 정보를 입력합니다.' },
  { id: 'assets', label: '자산/부채', description: '총자산, 총부채 및 상세 내역을 입력합니다.' },
  { id: 'details', label: '세부 자산', description: '부동산, 설비, 재고 등 세부 자산을 입력합니다.' },
]

function makeEmptyAssetItem(): AssetDetailItem {
  return { name: '', book_value: 0, market_value: undefined, note: '' }
}

function makeInitialData(): AssetFormData {
  return {
    company_name_kr: '',
    valuation_purpose: '',
    total_assets: 0,
    total_liabilities: 0,
    tangible_assets: [makeEmptyAssetItem()],
    intangible_assets: [makeEmptyAssetItem()],
    shares_outstanding: 0,
  }
}

// ---------------------------------------------------------------------------
// 유효성 검사
// ---------------------------------------------------------------------------

function validate(data: AssetFormData, step: number): string[] {
  const errs: string[] = []

  if (step === 0) {
    if (!data.company_name_kr.trim()) errs.push('기업명(한글)은 필수입니다.')
    if (!data.valuation_purpose) errs.push('평가 목적을 선택해주세요.')
  }

  if (step === 1) {
    if (data.total_assets <= 0) errs.push('총자산은 0보다 커야 합니다.')
    if (data.total_liabilities < 0) errs.push('총부채는 0 이상이어야 합니다.')
    if (data.total_liabilities > data.total_assets)
      errs.push('총부채가 총자산을 초과할 수 없습니다.')
  }

  if (step === 2) {
    if (data.shares_outstanding <= 0) errs.push('발행주식수는 0보다 커야 합니다.')
  }

  return errs
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function AssetSubmissionPage() {
  const router = useRouter()
  const [data, setData] = useState<AssetFormData>(makeInitialData)
  const [currentStep, setCurrentStep] = useState(0)
  const [errors, setErrors] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null)

  // --- 필드 변경 ---
  const updateField = useCallback(
    <K extends keyof AssetFormData>(key: K, value: AssetFormData[K]) => {
      setData((prev) => ({ ...prev, [key]: value }))
    },
    [],
  )

  const updateAssetItem = useCallback(
    (
      category: 'tangible_assets' | 'intangible_assets',
      index: number,
      field: keyof AssetDetailItem,
      value: string | number | undefined,
    ) => {
      setData((prev) => {
        const items = [...prev[category]]
        items[index] = { ...items[index], [field]: value }
        return { ...prev, [category]: items }
      })
    },
    [],
  )

  const addAssetItem = useCallback(
    (category: 'tangible_assets' | 'intangible_assets') => {
      setData((prev) => ({
        ...prev,
        [category]: [...prev[category], makeEmptyAssetItem()],
      }))
    },
    [],
  )

  const removeAssetItem = useCallback(
    (category: 'tangible_assets' | 'intangible_assets', index: number) => {
      setData((prev) => ({
        ...prev,
        [category]: prev[category].filter((_, i) => i !== index),
      }))
    },
    [],
  )

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
      sessionStorage.setItem('asset_draft', JSON.stringify(data))
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

    if (!window.confirm('자산가치 평가 신청을 제출하시겠습니까?')) return

    setIsSubmitting(true)
    setErrors([])

    try {
      // TODO: Supabase evaluation_requests INSERT
      await new Promise((resolve) => setTimeout(resolve, 1500))

      try {
        sessionStorage.removeItem('asset_draft')
      } catch {
        // 무시
      }

      router.push('/valuation/submissions?submitted=asset')
    } catch {
      setErrors(['제출 중 오류가 발생했습니다. 다시 시도해주세요.'])
    } finally {
      setIsSubmitting(false)
    }
  }, [data, currentStep, router])

  // --- 자산 항목 렌더 ---
  const renderAssetItems = (
    category: 'tangible_assets' | 'intangible_assets',
    title: string,
  ) => {
    const items = data[category]
    const categoryLabel = category === 'tangible_assets' ? '유형자산' : '무형자산'

    return (
      <div className="space-y-4">
        <h3 className="text-base font-medium text-gray-800">{title}</h3>

        {items.map((item, index) => (
          <div
            key={index}
            className="rounded-lg border border-gray-200 bg-gray-50/50 p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-gray-700">
                {categoryLabel} #{index + 1}
              </span>
              {items.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeAssetItem(category, index)}
                  className="text-sm text-red-600 hover:text-red-800 transition-colors"
                  aria-label={`${categoryLabel} #${index + 1} 삭제`}
                >
                  삭제
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <FormField
                id={`${category}_${index}_name`}
                label="항목명"
                value={item.name}
                onChange={(e) => updateAssetItem(category, index, 'name', e.currentTarget.value)}
                placeholder="예: 토지, 건물, 특허권"
              />
              <FormField
                id={`${category}_${index}_book_value`}
                label="장부가 (원)"
                fieldType="number"
                value={item.book_value || ''}
                onChange={(e) =>
                  updateAssetItem(category, index, 'book_value', Number(e.currentTarget.value) || 0)
                }
                placeholder="0"
                min={0}
              />
              <FormField
                id={`${category}_${index}_market_value`}
                label="시가 (원)"
                fieldType="number"
                value={item.market_value ?? ''}
                onChange={(e) =>
                  updateAssetItem(category, index, 'market_value', Number(e.currentTarget.value) || undefined)
                }
                placeholder="감정평가액"
                min={0}
              />
              <FormField
                id={`${category}_${index}_note`}
                label="비고"
                value={item.note ?? ''}
                onChange={(e) => updateAssetItem(category, index, 'note', e.currentTarget.value)}
                placeholder="참고 사항"
              />
            </div>
          </div>
        ))}

        <button
          type="button"
          onClick={() => addAssetItem(category)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-dashed border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-600 hover:border-blue-400 hover:text-blue-700 transition-colors"
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
          {categoryLabel} 항목 추가
        </button>
      </div>
    )
  }

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
          placeholder="예: 제조업 / 부동산"
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
        자산 및 부채 현황
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="total_assets"
          label="총자산 (원)"
          fieldType="number"
          required
          value={data.total_assets || ''}
          onChange={(e) => updateField('total_assets', Number(e.currentTarget.value) || 0)}
          placeholder="0"
          min={0}
          helpText="재무상태표 기준 총자산"
        />
        <FormField
          id="total_liabilities"
          label="총부채 (원)"
          fieldType="number"
          required
          value={data.total_liabilities || ''}
          onChange={(e) => updateField('total_liabilities', Number(e.currentTarget.value) || 0)}
          placeholder="0"
          min={0}
          helpText="재무상태표 기준 총부채"
        />
      </div>

      {/* 순자산가치 자동 계산 표시 */}
      {data.total_assets > 0 && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">순자산가치 (NAV):</span>{' '}
            {(data.total_assets - data.total_liabilities).toLocaleString('ko-KR')}원
          </p>
        </div>
      )}

      <div className="border-t border-gray-200 pt-6">
        {renderAssetItems('tangible_assets', '유형자산 상세')}
      </div>

      <div className="border-t border-gray-200 pt-6">
        {renderAssetItems('intangible_assets', '무형자산 상세')}
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
        세부 자산 및 기타
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <FormField
          id="real_estate_value"
          label="부동산 평가금액 (원)"
          fieldType="number"
          value={data.real_estate_value ?? ''}
          onChange={(e) =>
            updateField('real_estate_value', Number(e.currentTarget.value) || undefined)
          }
          placeholder="0"
          min={0}
          helpText="감정평가 기준 시가"
        />
        <FormField
          id="equipment_value"
          label="기계장치/설비 (원)"
          fieldType="number"
          value={data.equipment_value ?? ''}
          onChange={(e) =>
            updateField('equipment_value', Number(e.currentTarget.value) || undefined)
          }
          placeholder="0"
          min={0}
        />
        <FormField
          id="inventory_value"
          label="재고자산 (원)"
          fieldType="number"
          value={data.inventory_value ?? ''}
          onChange={(e) =>
            updateField('inventory_value', Number(e.currentTarget.value) || undefined)
          }
          placeholder="0"
          min={0}
        />
      </div>

      <div className="border-t border-gray-200 pt-6">
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

  return (
    <SubmissionFormTemplate
      method="asset"
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
