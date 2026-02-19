/**
 * @task S2F2
 * @description 상대가치평가 (Relative Valuation) 평가 신청 페이지
 *
 * 입력 필드:
 * - Step 1: 기업 기본 정보 (공통)
 * - Step 2: 유사기업 목록 (최소 3개), 산업 분류
 * - Step 3: 선택 멀티플(P/E, EV/EBITDA, P/B, P/S), 가중치, 재무 데이터
 *
 * 제출 → evaluation_requests 테이블 INSERT
 */

'use client'

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import SubmissionFormTemplate from '@/components/submission-form-template'
import FormField from '@/components/form-field'
import type {
  RelativeFormData,
  PeerCompanyInput,
  SelectedMultiple,
  MultipleType,
  FormStep,
} from '@/types/valuation-forms'
import { VALUATION_PURPOSES } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const STEPS: FormStep[] = [
  { id: 'company', label: '기업 정보', description: '기본 기업 정보를 입력합니다.' },
  { id: 'peers', label: '유사기업', description: '비교 대상 유사기업을 입력합니다.' },
  { id: 'multiples', label: '멀티플 설정', description: '적용할 멀티플과 가중치를 설정합니다.' },
]

const MULTIPLE_OPTIONS: { type: MultipleType; label: string; description: string }[] = [
  { type: 'per', label: 'P/E (주가수익비율)', description: '시가총액 / 순이익' },
  { type: 'ev_ebitda', label: 'EV/EBITDA', description: '기업가치 / EBITDA' },
  { type: 'pbr', label: 'P/B (주가순자산비율)', description: '시가총액 / 자기자본' },
  { type: 'psr', label: 'P/S (주가매출비율)', description: '시가총액 / 매출' },
]

function makeEmptyPeer(): PeerCompanyInput {
  return { name: '', market_cap: undefined, per: undefined, ev_ebitda: undefined, pbr: undefined, psr: undefined }
}

function makeInitialData(): RelativeFormData {
  return {
    company_name_kr: '',
    valuation_purpose: '',
    peer_companies: [makeEmptyPeer(), makeEmptyPeer(), makeEmptyPeer()],
    selected_multiples: [{ type: 'per', weight: 50 }, { type: 'ev_ebitda', weight: 50 }],
    industry_classification: '',
    shares_outstanding: 0,
  }
}

// ---------------------------------------------------------------------------
// 유효성 검사
// ---------------------------------------------------------------------------

function validate(data: RelativeFormData, step: number): string[] {
  const errs: string[] = []

  if (step === 0) {
    if (!data.company_name_kr.trim()) errs.push('기업명(한글)은 필수입니다.')
    if (!data.valuation_purpose) errs.push('평가 목적을 선택해주세요.')
  }

  if (step === 1) {
    const validPeers = data.peer_companies.filter((p) => p.name.trim())
    if (validPeers.length < 3) errs.push('유사기업을 최소 3개 이상 입력해주세요.')
    if (!data.industry_classification.trim()) errs.push('산업 분류를 입력해주세요.')
  }

  if (step === 2) {
    if (data.selected_multiples.length === 0) errs.push('최소 1개 이상의 멀티플을 선택해주세요.')
    const totalWeight = data.selected_multiples.reduce((sum, m) => sum + m.weight, 0)
    if (Math.abs(totalWeight - 100) > 0.01) errs.push(`가중치 합이 100%여야 합니다. (현재: ${totalWeight}%)`)
    if (data.shares_outstanding <= 0) errs.push('발행주식수는 0보다 커야 합니다.')
  }

  return errs
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function RelativeSubmissionPage() {
  const router = useRouter()
  const [data, setData] = useState<RelativeFormData>(makeInitialData)
  const [currentStep, setCurrentStep] = useState(0)
  const [errors, setErrors] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null)

  // --- 필드 변경 ---
  const updateField = useCallback(
    <K extends keyof RelativeFormData>(key: K, value: RelativeFormData[K]) => {
      setData((prev) => ({ ...prev, [key]: value }))
    },
    [],
  )

  const updatePeer = useCallback((index: number, field: keyof PeerCompanyInput, value: string | number | undefined) => {
    setData((prev) => {
      const next = [...prev.peer_companies]
      next[index] = { ...next[index], [field]: value }
      return { ...prev, peer_companies: next }
    })
  }, [])

  const addPeer = useCallback(() => {
    setData((prev) => ({
      ...prev,
      peer_companies: [...prev.peer_companies, makeEmptyPeer()],
    }))
  }, [])

  const removePeer = useCallback((index: number) => {
    setData((prev) => ({
      ...prev,
      peer_companies: prev.peer_companies.filter((_, i) => i !== index),
    }))
  }, [])

  const toggleMultiple = useCallback((type: MultipleType) => {
    setData((prev) => {
      const exists = prev.selected_multiples.find((m) => m.type === type)
      if (exists) {
        return {
          ...prev,
          selected_multiples: prev.selected_multiples.filter((m) => m.type !== type),
        }
      }
      return {
        ...prev,
        selected_multiples: [...prev.selected_multiples, { type, weight: 0 }],
      }
    })
  }, [])

  const updateMultipleWeight = useCallback((type: MultipleType, weight: number) => {
    setData((prev) => ({
      ...prev,
      selected_multiples: prev.selected_multiples.map((m) =>
        m.type === type ? { ...m, weight } : m,
      ),
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
      sessionStorage.setItem('relative_draft', JSON.stringify(data))
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

    if (!window.confirm('상대가치 평가 신청을 제출하시겠습니까?')) return

    setIsSubmitting(true)
    setErrors([])

    try {
      // TODO: Supabase evaluation_requests INSERT
      await new Promise((resolve) => setTimeout(resolve, 1500))

      try {
        sessionStorage.removeItem('relative_draft')
      } catch {
        // 무시
      }

      router.push('/valuation/submissions?submitted=relative')
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
          placeholder="예: AI / 소프트웨어"
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
        유사기업 목록
      </h2>
      <p className="text-sm text-gray-500">
        비교 대상 유사기업을 최소 3개 이상 입력하세요. 시가총액, 멀티플 등은 선택 사항입니다.
      </p>

      <FormField
        id="industry_classification"
        label="산업 분류"
        required
        value={data.industry_classification}
        onChange={(e) => updateField('industry_classification', e.currentTarget.value)}
        placeholder="예: GICS - 정보기술 / 소프트웨어"
        helpText="비교 대상 기업 선정의 기준이 되는 산업 분류"
      />

      <div className="space-y-6">
        {data.peer_companies.map((peer, index) => (
          <div
            key={index}
            className="rounded-lg border border-gray-200 bg-gray-50/50 p-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">
                유사기업 #{index + 1}
              </h3>
              {data.peer_companies.length > 3 && (
                <button
                  type="button"
                  onClick={() => removePeer(index)}
                  className="text-sm text-red-600 hover:text-red-800 transition-colors"
                  aria-label={`유사기업 #${index + 1} 삭제`}
                >
                  삭제
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <FormField
                id={`peer_${index}_name`}
                label="기업명"
                required={index < 3}
                value={peer.name}
                onChange={(e) => updatePeer(index, 'name', e.currentTarget.value)}
                placeholder="예: 삼성SDS"
              />
              <FormField
                id={`peer_${index}_market_cap`}
                label="시가총액 (원)"
                fieldType="number"
                value={peer.market_cap ?? ''}
                onChange={(e) =>
                  updatePeer(index, 'market_cap', Number(e.currentTarget.value) || undefined)
                }
                placeholder="0"
                min={0}
              />
              <FormField
                id={`peer_${index}_per`}
                label="PER (배)"
                fieldType="number"
                value={peer.per ?? ''}
                onChange={(e) =>
                  updatePeer(index, 'per', Number(e.currentTarget.value) || undefined)
                }
                placeholder="예: 15.2"
                min={0}
                step={0.1}
              />
              <FormField
                id={`peer_${index}_ev_ebitda`}
                label="EV/EBITDA (배)"
                fieldType="number"
                value={peer.ev_ebitda ?? ''}
                onChange={(e) =>
                  updatePeer(index, 'ev_ebitda', Number(e.currentTarget.value) || undefined)
                }
                placeholder="예: 10.5"
                min={0}
                step={0.1}
              />
              <FormField
                id={`peer_${index}_pbr`}
                label="PBR (배)"
                fieldType="number"
                value={peer.pbr ?? ''}
                onChange={(e) =>
                  updatePeer(index, 'pbr', Number(e.currentTarget.value) || undefined)
                }
                placeholder="예: 2.1"
                min={0}
                step={0.1}
              />
              <FormField
                id={`peer_${index}_psr`}
                label="PSR (배)"
                fieldType="number"
                value={peer.psr ?? ''}
                onChange={(e) =>
                  updatePeer(index, 'psr', Number(e.currentTarget.value) || undefined)
                }
                placeholder="예: 3.5"
                min={0}
                step={0.1}
              />
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={addPeer}
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
        유사기업 추가
      </button>
    </div>
  )

  const renderStep2 = () => {
    const totalWeight = data.selected_multiples.reduce((sum, m) => sum + m.weight, 0)

    return (
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-3">
          멀티플 선택 및 가중치
        </h2>
        <p className="text-sm text-gray-500">
          적용할 멀티플을 선택하고, 가중치 합이 100%가 되도록 설정하세요.
        </p>

        <div className="space-y-3">
          {MULTIPLE_OPTIONS.map((option) => {
            const selected = data.selected_multiples.find((m) => m.type === option.type)
            const isSelected = Boolean(selected)

            return (
              <div
                key={option.type}
                className={`rounded-lg border p-4 transition-colors ${
                  isSelected
                    ? 'border-blue-300 bg-blue-50/50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleMultiple(option.type)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`${option.label} 선택`}
                    />
                    <div>
                      <span className="text-sm font-medium text-gray-900">
                        {option.label}
                      </span>
                      <span className="ml-2 text-xs text-gray-500">{option.description}</span>
                    </div>
                  </label>

                  {isSelected && (
                    <div className="flex items-center gap-2">
                      <label
                        htmlFor={`weight_${option.type}`}
                        className="text-xs text-gray-500"
                      >
                        가중치
                      </label>
                      <input
                        id={`weight_${option.type}`}
                        type="number"
                        min={0}
                        max={100}
                        step={5}
                        value={selected?.weight ?? 0}
                        onChange={(e) =>
                          updateMultipleWeight(option.type, Number(e.target.value) || 0)
                        }
                        className="w-20 rounded-md border border-gray-300 px-2 py-1.5 text-sm text-right focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                        aria-label={`${option.label} 가중치 (%)`}
                      />
                      <span className="text-xs text-gray-500">%</span>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* 가중치 합계 */}
        <div
          className={`flex items-center gap-2 text-sm font-medium ${
            Math.abs(totalWeight - 100) < 0.01
              ? 'text-green-600'
              : 'text-red-600'
          }`}
        >
          <span>가중치 합계: {totalWeight}%</span>
          {Math.abs(totalWeight - 100) < 0.01 ? (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <span>(100%가 되어야 합니다)</span>
          )}
        </div>

        {/* 재무 데이터 */}
        <div className="border-t border-gray-200 pt-6 space-y-5">
          <h3 className="text-base font-medium text-gray-800">대상 기업 재무 데이터</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <FormField
              id="net_income"
              label="당기순이익 (원)"
              fieldType="number"
              value={data.net_income ?? ''}
              onChange={(e) =>
                updateField('net_income', Number(e.currentTarget.value) || undefined)
              }
              placeholder="0"
              helpText="PER 산출에 사용"
            />
            <FormField
              id="equity"
              label="자기자본 (원)"
              fieldType="number"
              value={data.equity ?? ''}
              onChange={(e) =>
                updateField('equity', Number(e.currentTarget.value) || undefined)
              }
              placeholder="0"
              helpText="PBR 산출에 사용"
            />
            <FormField
              id="ebitda"
              label="EBITDA (원)"
              fieldType="number"
              value={data.ebitda ?? ''}
              onChange={(e) =>
                updateField('ebitda', Number(e.currentTarget.value) || undefined)
              }
              placeholder="0"
              helpText="EV/EBITDA 산출에 사용"
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
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <SubmissionFormTemplate
      method="relative"
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
