/**
 * @task S2F2
 * @description DCF (현금흐름할인법) 평가 신청 페이지
 *
 * 입력 필드:
 * - Step 1: 기업 기본 정보 (공통)
 * - Step 2: DCF 전용 - 매출 추정(5년), 영업이익률, 법인세율
 * - Step 3: DCF 전용 - WACC, 영구성장률, 순부채, 발행주식수
 *
 * 제출 → evaluation_requests 테이블 INSERT
 */

'use client'

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import SubmissionFormTemplate from '@/components/submission-form-template'
import FormField from '@/components/form-field'
import type {
  DCFFormData,
  FormErrors,
  FormStep,
  RevenueProjection,
} from '@/types/valuation-forms'
import { VALUATION_PURPOSES } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const STEPS: FormStep[] = [
  { id: 'company', label: '기업 정보', description: '기본 기업 정보를 입력합니다.' },
  { id: 'projections', label: '매출 추정', description: '5개년 매출 및 수익성을 입력합니다.' },
  { id: 'discount', label: '할인율 / 기타', description: 'WACC, 영구성장률 등을 입력합니다.' },
]

const CURRENT_YEAR = new Date().getFullYear()

function makeInitialProjections(): RevenueProjection[] {
  return Array.from({ length: 5 }, (_, i) => ({
    year: CURRENT_YEAR + 1 + i,
    revenue: 0,
  }))
}

function makeInitialData(): DCFFormData {
  return {
    company_name_kr: '',
    valuation_purpose: '',
    revenue_projections: makeInitialProjections(),
    operating_margin: 0,
    tax_rate: 22,
    wacc: 0,
    terminal_growth_rate: 1,
    net_debt: 0,
    shares_outstanding: 0,
  }
}

// ---------------------------------------------------------------------------
// 유효성 검사
// ---------------------------------------------------------------------------

function validate(data: DCFFormData, step: number): string[] {
  const errs: string[] = []

  if (step === 0) {
    if (!data.company_name_kr.trim()) errs.push('기업명(한글)은 필수입니다.')
    if (!data.valuation_purpose) errs.push('평가 목적을 선택해주세요.')
  }

  if (step === 1) {
    const hasRevenue = data.revenue_projections.some((r) => r.revenue > 0)
    if (!hasRevenue) errs.push('최소 1개년 매출 추정치를 입력해주세요.')
    if (data.operating_margin <= 0 || data.operating_margin > 100)
      errs.push('영업이익률은 0~100% 사이여야 합니다.')
    if (data.tax_rate < 0 || data.tax_rate > 100)
      errs.push('법인세율은 0~100% 사이여야 합니다.')
  }

  if (step === 2) {
    if (data.wacc <= 0) errs.push('WACC는 0보다 커야 합니다.')
    if (data.terminal_growth_rate < 0 || data.terminal_growth_rate >= data.wacc)
      errs.push('영구성장률은 0 이상이고 WACC 미만이어야 합니다.')
    if (data.shares_outstanding <= 0) errs.push('발행주식수는 0보다 커야 합니다.')
  }

  return errs
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function DCFSubmissionPage() {
  const router = useRouter()
  const [data, setData] = useState<DCFFormData>(makeInitialData)
  const [currentStep, setCurrentStep] = useState(0)
  const [errors, setErrors] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null)

  // --- 필드 변경 ---
  const updateField = useCallback(
    <K extends keyof DCFFormData>(key: K, value: DCFFormData[K]) => {
      setData((prev) => ({ ...prev, [key]: value }))
    },
    [],
  )

  const updateProjectionRevenue = useCallback((index: number, revenue: number) => {
    setData((prev) => {
      const next = [...prev.revenue_projections]
      next[index] = { ...next[index], revenue }
      return { ...prev, revenue_projections: next }
    })
  }, [])

  // --- 단계 이동 ---
  const handleStepChange = useCallback(
    (step: number) => {
      // 앞으로 이동 시 유효성 검사
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
      sessionStorage.setItem('dcf_draft', JSON.stringify(data))
      setLastSavedAt(new Date())
    } catch {
      // sessionStorage 불가 환경 무시
    }
  }, [data])

  // --- 제출 ---
  const handleSubmit = useCallback(async () => {
    const errs = validate(data, currentStep)
    if (errs.length > 0) {
      setErrors(errs)
      return
    }

    // 최종 확인
    if (!window.confirm('DCF 평가 신청을 제출하시겠습니까?')) return

    setIsSubmitting(true)
    setErrors([])

    try {
      // TODO: Supabase evaluation_requests INSERT
      // const { data: result, error } = await supabase
      //   .from('evaluation_requests')
      //   .insert({
      //     company_name_kr: data.company_name_kr,
      //     company_name_en: data.company_name_en || null,
      //     business_registration_number: data.business_registration_number || null,
      //     representative_name: data.representative_name || null,
      //     industry: data.industry || null,
      //     revenue: data.revenue || null,
      //     employees: data.employees || null,
      //     founded_date: data.founded_date || null,
      //     company_website: data.company_website || null,
      //     address: data.address || null,
      //     phone: data.phone || null,
      //     fax: data.fax || null,
      //     valuation_purpose: data.valuation_purpose,
      //     requested_methods: ['dcf'],
      //     target_date: data.target_date || null,
      //     requirements: data.requirements || null,
      //     budget_min: data.budget_min || null,
      //     budget_max: data.budget_max || null,
      //     status: 'pending',
      //   })
      //   .select('request_id')
      //   .single()

      // 임시: 성공 시뮬레이션
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // 임시 저장 삭제
      try {
        sessionStorage.removeItem('dcf_draft')
      } catch {
        // 무시
      }

      router.push('/valuation/submissions?submitted=dcf')
    } catch (err) {
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
          helpText="하이픈(-)을 포함하여 입력하세요."
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
          id="industry"
          label="업종"
          value={data.industry ?? ''}
          onChange={(e) => updateField('industry', e.currentTarget.value)}
          placeholder="예: AI / 소프트웨어"
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
          id="phone"
          label="전화번호"
          fieldType="tel"
          value={data.phone ?? ''}
          onChange={(e) => updateField('phone', e.currentTarget.value)}
          placeholder="02-000-0000"
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
        매출 추정 (5개년)
      </h2>
      <p className="text-sm text-gray-500">
        향후 5년간의 예상 매출액을 입력하세요. 단위는 원(KRW)입니다.
      </p>

      <div className="space-y-4">
        {data.revenue_projections.map((proj, index) => (
          <FormField
            key={proj.year}
            id={`revenue_${proj.year}`}
            label={`${proj.year}년 예상 매출`}
            fieldType="number"
            required={index === 0}
            value={proj.revenue || ''}
            onChange={(e) =>
              updateProjectionRevenue(index, Number(e.currentTarget.value) || 0)
            }
            placeholder="0"
            min={0}
            step={1000000}
            helpText={index === 0 ? '최소 1개년 입력 필수' : undefined}
          />
        ))}
      </div>

      <div className="border-t border-gray-200 pt-6 space-y-5">
        <h3 className="text-base font-medium text-gray-800">수익성 가정</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <FormField
            id="operating_margin"
            label="영업이익률 (%)"
            fieldType="number"
            required
            value={data.operating_margin || ''}
            onChange={(e) =>
              updateField('operating_margin', Number(e.currentTarget.value) || 0)
            }
            placeholder="예: 15"
            min={0}
            max={100}
            step={0.1}
            helpText="매출 대비 영업이익 비율"
          />
          <FormField
            id="tax_rate"
            label="법인세율 (%)"
            fieldType="number"
            required
            value={data.tax_rate || ''}
            onChange={(e) =>
              updateField('tax_rate', Number(e.currentTarget.value) || 0)
            }
            placeholder="예: 22"
            min={0}
            max={100}
            step={0.1}
            helpText="실효 법인세율 (기본 22%)"
          />
        </div>
      </div>

      <div className="border-t border-gray-200 pt-6 space-y-5">
        <h3 className="text-base font-medium text-gray-800">추가 항목 (선택)</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <FormField
            id="depreciation"
            label="감가상각비 (원)"
            fieldType="number"
            value={data.depreciation ?? ''}
            onChange={(e) =>
              updateField('depreciation', Number(e.currentTarget.value) || undefined)
            }
            placeholder="0"
            min={0}
          />
          <FormField
            id="capex"
            label="자본적지출 (원)"
            fieldType="number"
            value={data.capex ?? ''}
            onChange={(e) =>
              updateField('capex', Number(e.currentTarget.value) || undefined)
            }
            placeholder="0"
            min={0}
          />
          <FormField
            id="working_capital_change"
            label="순운전자본 변동 (원)"
            fieldType="number"
            value={data.working_capital_change ?? ''}
            onChange={(e) =>
              updateField('working_capital_change', Number(e.currentTarget.value) || undefined)
            }
            placeholder="0"
          />
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
        할인율 및 기타 가정
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="wacc"
          label="WACC - 가중평균자본비용 (%)"
          fieldType="number"
          required
          value={data.wacc || ''}
          onChange={(e) =>
            updateField('wacc', Number(e.currentTarget.value) || 0)
          }
          placeholder="예: 10.5"
          min={0}
          max={100}
          step={0.1}
          helpText="자기자본비용과 타인자본비용의 가중평균"
        />
        <FormField
          id="terminal_growth_rate"
          label="영구성장률 (%)"
          fieldType="number"
          required
          value={data.terminal_growth_rate || ''}
          onChange={(e) =>
            updateField('terminal_growth_rate', Number(e.currentTarget.value) || 0)
          }
          placeholder="예: 1.0"
          min={0}
          max={10}
          step={0.1}
          helpText="보수적으로 0~2% 권장 (GDP 성장률 이하)"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <FormField
          id="net_debt"
          label="순부채 (원)"
          fieldType="number"
          required
          value={data.net_debt || ''}
          onChange={(e) =>
            updateField('net_debt', Number(e.currentTarget.value) || 0)
          }
          placeholder="0"
          helpText="이자부부채 - 현금성 자산"
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

  return (
    <SubmissionFormTemplate
      method="dcf"
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
