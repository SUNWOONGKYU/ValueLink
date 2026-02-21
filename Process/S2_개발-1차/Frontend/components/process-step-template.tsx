/**
 * @task S2F5
 * @description 평가 프로세스 단계 템플릿 - 14단계 워크플로우 공통 레이아웃
 *
 * - 'use client': 단계 상태 표시, 네비게이션 등 인터랙티브 기능
 * - 좌측 사이드바: 14단계 진행 상태 시각 표시
 * - 프로젝트 정보 요약 헤더
 * - 이전/다음 단계 네비게이션
 * - 반응형: 모바일에서 사이드바 축소
 */

'use client'

import { ReactNode, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

// ---------------------------------------------------------------------------
// 14단계 워크플로우 정의
// ---------------------------------------------------------------------------

interface WorkflowStep {
  number: number
  title: string
  shortTitle: string
}

const WORKFLOW_STEPS: WorkflowStep[] = [
  { number: 1, title: '프로젝트 생성', shortTitle: '프로젝트 생성' },
  { number: 2, title: '서류 제출 요청', shortTitle: '서류 요청' },
  { number: 3, title: '서류 제출 완료', shortTitle: '서류 완료' },
  { number: 4, title: '평가 진행 중', shortTitle: '평가 진행' },
  { number: 5, title: 'AI 초안 생성', shortTitle: 'AI 초안' },
  { number: 6, title: '회계사 검토', shortTitle: '회계사 검토' },
  { number: 7, title: '고객 확인 요청', shortTitle: '고객 확인' },
  { number: 8, title: '수정 요청/반영', shortTitle: '수정 반영' },
  { number: 9, title: '최종 보고서 생성', shortTitle: '최종 보고서' },
  { number: 10, title: '잔금 결제 요청', shortTitle: '잔금 요청' },
  { number: 11, title: '잔금 결제 완료', shortTitle: '잔금 완료' },
  { number: 12, title: '보고서 전달', shortTitle: '보고서 전달' },
  { number: 13, title: '프로젝트 완료', shortTitle: '프로젝트 완료' },
  { number: 14, title: '아카이브', shortTitle: '아카이브' },
]

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface ProcessStepTemplateProps {
  /** 프로젝트 ID */
  projectId: string
  /** 프로젝트의 현재 진행 단계 (1-14, DB의 current_step) */
  currentStep: number
  /** 현재 표시 중인 단계 번호 (1-14) */
  stepNumber: number
  /** 현재 표시 중인 단계 제목 */
  stepTitle: string
  /** 회사명 (한글) */
  companyName?: string
  /** 평가 방법 */
  valuationMethod?: string
  /** 프로젝트 상태 */
  projectStatus?: string
  /** 페이지 본문 */
  children: ReactNode
}

// ---------------------------------------------------------------------------
// 단계 상태 판별 헬퍼
// ---------------------------------------------------------------------------

type StepState = 'completed' | 'current' | 'accessible' | 'upcoming'

function getStepState(
  stepNumber: number,
  currentStep: number,
  viewingStep: number
): StepState {
  if (stepNumber < currentStep) return 'completed'
  if (stepNumber === currentStep && stepNumber === viewingStep) return 'current'
  if (stepNumber === currentStep) return 'current'
  if (stepNumber <= currentStep + 1) return 'accessible'
  return 'upcoming'
}

// ---------------------------------------------------------------------------
// SVG 아이콘 컴포넌트
// ---------------------------------------------------------------------------

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth={2.5}
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4.5 12.75l6 6 9-13.5"
      />
    </svg>
  )
}

function ChevronLeftIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
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
  )
}

function ChevronRightIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
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
  )
}

function MenuIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
      />
    </svg>
  )
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  )
}

// ---------------------------------------------------------------------------
// 사이드바 단계 아이템 컴포넌트
// ---------------------------------------------------------------------------

interface StepItemProps {
  step: WorkflowStep
  state: StepState
  isViewing: boolean
  projectId: string
  onClick?: () => void
}

function StepItem({ step, state, isViewing, projectId, onClick }: StepItemProps) {
  const isClickable = state === 'completed' || state === 'current' || state === 'accessible'

  const baseClasses = 'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors w-full text-left'

  let stateClasses: string
  if (isViewing) {
    stateClasses = 'bg-blue-700 text-white shadow-sm'
  } else if (state === 'completed') {
    stateClasses = 'text-green-700 hover:bg-green-50'
  } else if (state === 'current') {
    stateClasses = 'text-blue-700 hover:bg-blue-50'
  } else if (state === 'accessible') {
    stateClasses = 'text-gray-600 hover:bg-gray-100'
  } else {
    stateClasses = 'text-gray-400 cursor-not-allowed'
  }

  // 단계 번호/아이콘 인디케이터
  let indicator: ReactNode
  if (state === 'completed') {
    indicator = (
      <span
        className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full ${
          isViewing ? 'bg-white/20' : 'bg-green-100'
        }`}
      >
        <CheckIcon
          className={`h-4 w-4 ${isViewing ? 'text-white' : 'text-green-600'}`}
        />
      </span>
    )
  } else if (state === 'current') {
    indicator = (
      <span
        className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold ${
          isViewing
            ? 'bg-white text-blue-700'
            : 'bg-blue-100 text-blue-700 ring-2 ring-blue-300'
        }`}
      >
        {step.number}
      </span>
    )
  } else {
    indicator = (
      <span
        className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-medium ${
          isViewing ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-500'
        }`}
      >
        {step.number}
      </span>
    )
  }

  const content = (
    <>
      {indicator}
      <span className="truncate">{step.title}</span>
    </>
  )

  if (isClickable) {
    // step-13, step-14는 별도 페이지가 없으므로 12단계까지만 링크
    if (step.number <= 12) {
      return (
        <Link
          href={`/valuation/process/step-${step.number}?project_id=${projectId}`}
          className={`${baseClasses} ${stateClasses}`}
          aria-current={isViewing ? 'step' : undefined}
          onClick={onClick}
        >
          {content}
        </Link>
      )
    }
    return (
      <button
        type="button"
        className={`${baseClasses} ${stateClasses}`}
        aria-current={isViewing ? 'step' : undefined}
        disabled
      >
        {content}
      </button>
    )
  }

  return (
    <div className={`${baseClasses} ${stateClasses}`} aria-disabled="true">
      {content}
    </div>
  )
}

// ---------------------------------------------------------------------------
// 메인 컴포넌트
// ---------------------------------------------------------------------------

export default function ProcessStepTemplate({
  projectId,
  currentStep,
  stepNumber,
  stepTitle,
  companyName,
  valuationMethod,
  projectStatus,
  children,
}: ProcessStepTemplateProps) {
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // 진행률 계산 (완료된 단계 / 전체 14단계)
  const completedSteps = Math.max(0, currentStep - 1)
  const progressPercent = Math.round((completedSteps / 14) * 100)

  // 이전/다음 네비게이션 가능 여부
  const canGoPrev = stepNumber > 1
  const canGoNext = stepNumber < 12 && stepNumber < currentStep + 1

  const handlePrev = () => {
    if (canGoPrev) {
      router.push(
        `/valuation/process/step-${stepNumber - 1}?project_id=${projectId}`
      )
    }
  }

  const handleNext = () => {
    if (canGoNext) {
      router.push(
        `/valuation/process/step-${stepNumber + 1}?project_id=${projectId}`
      )
    }
  }

  // 접근 불가 단계 체크 (현재 단계 + 1 초과는 접근 불가)
  const isAccessible = stepNumber <= currentStep + 1

  if (!isAccessible) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100 mb-4">
            <svg
              className="h-8 w-8 text-yellow-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            아직 접근할 수 없는 단계입니다
          </h2>
          <p className="text-gray-600 mb-6">
            현재 <span className="font-semibold">{currentStep}단계</span>까지
            진행되었습니다. 이전 단계를 먼저 완료해 주세요.
          </p>
          <Link
            href={`/valuation/process/step-${Math.min(currentStep, 12)}?project_id=${projectId}`}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors"
          >
            현재 단계로 이동
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ================================================================= */}
      {/* 모바일 사이드바 오버레이                                           */}
      {/* ================================================================= */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          {/* 배경 오버레이 */}
          <div
            className="fixed inset-0 bg-gray-900/50 transition-opacity"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
          {/* 사이드바 패널 */}
          <div className="fixed inset-y-0 left-0 z-50 w-80 max-w-[85vw] bg-white shadow-xl overflow-y-auto">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                평가 프로세스
              </h2>
              <button
                type="button"
                onClick={() => setSidebarOpen(false)}
                className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 transition-colors"
                aria-label="메뉴 닫기"
              >
                <CloseIcon className="h-5 w-5" />
              </button>
            </div>
            <nav className="p-3" aria-label="평가 단계 목록">
              <ul className="space-y-0.5" role="list">
                {WORKFLOW_STEPS.map((step) => (
                  <li key={step.number}>
                    <StepItem
                      step={step}
                      state={getStepState(step.number, currentStep, stepNumber)}
                      isViewing={step.number === stepNumber}
                      projectId={projectId}
                      onClick={() => setSidebarOpen(false)}
                    />
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </div>
      )}

      {/* ================================================================= */}
      {/* 상단 헤더                                                         */}
      {/* ================================================================= */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-3">
            {/* 좌측: 메뉴 버튼 + 프로젝트 정보 */}
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden rounded-lg p-2 text-gray-500 hover:bg-gray-100 transition-colors"
                aria-label="프로세스 메뉴 열기"
              >
                <MenuIcon className="h-5 w-5" />
              </button>
              <Link
                href={`/projects/${projectId}`}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
                aria-label="프로젝트로 돌아가기"
              >
                <ChevronLeftIcon className="h-4 w-4" />
                <span className="hidden sm:inline">프로젝트</span>
              </Link>
              <div className="hidden sm:block border-l border-gray-300 pl-3">
                <div className="flex items-center gap-2">
                  {companyName && (
                    <span className="text-sm font-semibold text-gray-900">
                      {companyName}
                    </span>
                  )}
                  {valuationMethod && (
                    <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                      {valuationMethod}
                    </span>
                  )}
                  {projectStatus && (
                    <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                      {projectStatus}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* 우측: 진행률 표시 */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500 hidden sm:inline">
                진행률
              </span>
              <div className="flex items-center gap-2">
                <div className="w-24 sm:w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 rounded-full transition-all duration-500"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-700 tabular-nums">
                  {progressPercent}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ================================================================= */}
      {/* 본문 영역: 사이드바 + 메인 콘텐츠                                  */}
      {/* ================================================================= */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-8">
          {/* 데스크톱 사이드바 */}
          <aside
            className="hidden lg:block w-64 flex-shrink-0"
            aria-label="평가 단계 네비게이션"
          >
            <div className="sticky top-6">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3 px-3">
                평가 프로세스 ({completedSteps}/14 완료)
              </h2>
              <nav aria-label="평가 단계 목록">
                <ul className="space-y-0.5" role="list">
                  {WORKFLOW_STEPS.map((step) => (
                    <li key={step.number}>
                      <StepItem
                        step={step}
                        state={getStepState(
                          step.number,
                          currentStep,
                          stepNumber
                        )}
                        isViewing={step.number === stepNumber}
                        projectId={projectId}
                      />
                    </li>
                  ))}
                </ul>
              </nav>
            </div>
          </aside>

          {/* 메인 콘텐츠 */}
          <main className="flex-1 min-w-0">
            {/* 단계 헤더 */}
            <div className="mb-6">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <span className="tabular-nums">STEP {stepNumber}</span>
                <span>/</span>
                <span>14</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                {stepTitle}
              </h1>
            </div>

            {/* 페이지 본문 */}
            <div className="mb-8">{children}</div>

            {/* 하단 네비게이션 */}
            <div className="flex items-center justify-between border-t border-gray-200 pt-6 mt-8">
              {canGoPrev ? (
                <button
                  type="button"
                  onClick={handlePrev}
                  className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
                >
                  <ChevronLeftIcon className="h-4 w-4" />
                  <span>이전 단계</span>
                </button>
              ) : (
                <div />
              )}

              {canGoNext ? (
                <button
                  type="button"
                  onClick={handleNext}
                  className="inline-flex items-center gap-2 rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors"
                >
                  <span>다음 단계</span>
                  <ChevronRightIcon className="h-4 w-4" />
                </button>
              ) : (
                <div />
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
