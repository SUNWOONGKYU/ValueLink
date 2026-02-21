/**
 * @task S2F2
 * @description 평가 신청 폼 공통 템플릿 (5개 방법론 공유)
 *
 * - 'use client': 인터랙티브 폼 (입력, 유효성 검사, 제출)
 * - 폼 헤더 (방법론명, 설명, 뱃지)
 * - 진행 단계 인디케이터 (multi-step)
 * - 제출/취소 버튼 + 로딩 상태
 * - 자동 임시 저장 표시
 * - 에러 요약 (상단)
 * - 반응형 모바일 우선 Tailwind CSS
 */

'use client'

import { type ReactNode, useCallback, useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import type { ValuationMethod } from '@/types/valuation'
import { METHOD_META_MAP, type FormStep } from '@/types/valuation-forms'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface SubmissionFormTemplateProps {
  /** 평가 방법론 */
  method: ValuationMethod
  /** 폼 단계 목록 */
  steps: FormStep[]
  /** 현재 단계 인덱스 (0-based) */
  currentStep: number
  /** 단계 이동 콜백 */
  onStepChange: (step: number) => void
  /** 폼 제출 콜백 */
  onSubmit: () => void | Promise<void>
  /** 제출 중 상태 */
  isSubmitting: boolean
  /** 에러 메시지 목록 (상단 요약) */
  errors?: string[]
  /** 마지막 자동 저장 시각 */
  lastSavedAt?: Date | null
  /** 자동 저장 트리거 콜백 (호출 시 임시 저장) */
  onAutoSave?: () => void
  /** 폼 본문 (각 방법론별 필드) */
  children: ReactNode
}

// ---------------------------------------------------------------------------
// 자동 저장 간격 (ms)
// ---------------------------------------------------------------------------

const AUTO_SAVE_INTERVAL = 30_000 // 30초

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SubmissionFormTemplate({
  method,
  steps,
  currentStep,
  onStepChange,
  onSubmit,
  isSubmitting,
  errors,
  lastSavedAt,
  onAutoSave,
  children,
}: SubmissionFormTemplateProps) {
  const meta = METHOD_META_MAP[method]
  const isLastStep = currentStep === steps.length - 1
  const isFirstStep = currentStep === 0

  // --- 자동 저장 ---
  const autoSaveTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [savedLabel, setSavedLabel] = useState<string | null>(null)

  useEffect(() => {
    if (!onAutoSave) return

    autoSaveTimerRef.current = setInterval(() => {
      onAutoSave()
    }, AUTO_SAVE_INTERVAL)

    return () => {
      if (autoSaveTimerRef.current) {
        clearInterval(autoSaveTimerRef.current)
      }
    }
  }, [onAutoSave])

  useEffect(() => {
    if (lastSavedAt) {
      const timeStr = lastSavedAt.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
      })
      setSavedLabel(`${timeStr} 자동 저장됨`)
    }
  }, [lastSavedAt])

  // --- 제출 핸들러 ---
  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault()
      if (isSubmitting) return
      await onSubmit()
    },
    [isSubmitting, onSubmit],
  )

  // --- 렌더 ---

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ================================================================= */}
      {/* 헤더                                                              */}
      {/* ================================================================= */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            {/* 좌측: 뒤로가기 + 제목 */}
            <div className="flex items-center gap-4">
              <Link
                href="/valuation/submissions"
                className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                aria-label="평가 신청 목록으로 돌아가기"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                <span className="hidden sm:inline">목록</span>
              </Link>

              <div className="border-l border-gray-300 pl-4">
                <div className="flex items-center gap-2.5">
                  <h1 className="text-lg sm:text-xl font-bold text-gray-900">
                    {meta.shortLabel} 평가 신청
                  </h1>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${meta.badgeColor}`}
                  >
                    {meta.shortLabel}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-0.5">
                  {meta.description}
                </p>
              </div>
            </div>

            {/* 우측: 자동 저장 표시 */}
            {savedLabel && (
              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>{savedLabel}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ================================================================= */}
      {/* 진행 단계 인디케이터                                              */}
      {/* ================================================================= */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <nav aria-label="폼 진행 단계">
            {/* 모바일: 텍스트 */}
            <p className="text-sm text-gray-500 sm:hidden">
              <span className="font-medium text-blue-700">
                {currentStep + 1}단계
              </span>{' '}
              / {steps.length}단계 &mdash; {steps[currentStep]?.label}
            </p>

            {/* 데스크톱: 스텝 바 */}
            <ol className="hidden sm:flex items-center gap-2" role="list">
              {steps.map((step, index) => {
                const isCompleted = index < currentStep
                const isCurrent = index === currentStep

                return (
                  <li key={step.id} className="flex items-center gap-2 flex-1">
                    <button
                      type="button"
                      onClick={() => onStepChange(index)}
                      disabled={isSubmitting}
                      className={`flex items-center gap-2 text-sm font-medium transition-colors ${
                        isCurrent
                          ? 'text-blue-700'
                          : isCompleted
                            ? 'text-green-600 hover:text-green-700'
                            : 'text-gray-400'
                      }`}
                      aria-current={isCurrent ? 'step' : undefined}
                      aria-label={`${index + 1}단계: ${step.label}${
                        isCompleted ? ' (완료)' : isCurrent ? ' (진행 중)' : ''
                      }`}
                    >
                      {/* 원형 인디케이터 */}
                      <span
                        className={`flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full text-xs font-bold border-2 ${
                          isCurrent
                            ? 'border-blue-700 bg-blue-700 text-white'
                            : isCompleted
                              ? 'border-green-500 bg-green-500 text-white'
                              : 'border-gray-300 text-gray-400'
                        }`}
                      >
                        {isCompleted ? (
                          <svg
                            className="w-3.5 h-3.5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            aria-hidden="true"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        ) : (
                          index + 1
                        )}
                      </span>
                      <span className="hidden lg:inline">{step.label}</span>
                    </button>

                    {/* 연결선 */}
                    {index < steps.length - 1 && (
                      <div
                        className={`flex-1 h-0.5 ${
                          isCompleted ? 'bg-green-400' : 'bg-gray-200'
                        }`}
                        aria-hidden="true"
                      />
                    )}
                  </li>
                )
              })}
            </ol>
          </nav>
        </div>
      </div>

      {/* ================================================================= */}
      {/* 메인: 폼                                                          */}
      {/* ================================================================= */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* 에러 요약 */}
        {errors && errors.length > 0 && (
          <div
            className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4"
            role="alert"
            aria-live="assertive"
          >
            <div className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <h2 className="text-sm font-semibold text-red-800">
                  입력 오류가 있습니다
                </h2>
                <ul className="mt-2 list-disc pl-5 text-sm text-red-700 space-y-1">
                  {errors.map((err, idx) => (
                    <li key={idx}>{err}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* 폼 */}
        <form onSubmit={handleSubmit} noValidate>
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="p-5 sm:p-6 lg:p-8">{children}</div>
          </div>

          {/* ============================================================= */}
          {/* 하단 버튼                                                      */}
          {/* ============================================================= */}
          <div className="mt-6 flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-3">
            {/* 좌측: 취소 / 이전 */}
            <div className="flex items-center gap-3">
              <Link
                href="/valuation/submissions"
                className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
              >
                취소
              </Link>
              {!isFirstStep && (
                <button
                  type="button"
                  onClick={() => onStepChange(currentStep - 1)}
                  disabled={isSubmitting}
                  className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  이전 단계
                </button>
              )}
            </div>

            {/* 우측: 다음 / 제출 */}
            <div>
              {isLastStep ? (
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <svg
                        className="animate-spin h-4 w-4"
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
                      <span>제출 중...</span>
                    </>
                  ) : (
                    <>
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <span>평가 신청 제출</span>
                    </>
                  )}
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => onStepChange(currentStep + 1)}
                  disabled={isSubmitting}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors disabled:opacity-50"
                >
                  <span>다음 단계</span>
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </form>
      </main>
    </div>
  )
}
