/**
 * @task S2F5
 * @description Step 1 - 프로젝트 생성 페이지
 *
 * 프로젝트 기본 정보 표시 (회사명, 평가 방법, 상태)
 * "서류 제출하기" 버튼으로 2단계 진행
 */

'use client'

import { useSearchParams, useRouter } from 'next/navigation'
import { useState, useEffect, Suspense } from 'react'
import ProcessStepTemplate from '@/components/process-step-template'

// ---------------------------------------------------------------------------
// 프로젝트 데이터 타입
// ---------------------------------------------------------------------------

interface ProjectData {
  project_id: string
  company_name_kr: string
  company_name_en: string | null
  valuation_purpose: string | null
  requested_methods: string[] | null
  status: string
  current_step: number
  created_at: string
}

// ---------------------------------------------------------------------------
// 평가 목적 한글 매핑
// ---------------------------------------------------------------------------

const PURPOSE_LABELS: Record<string, string> = {
  ma: '인수합병 (M&A)',
  investment: '투자 유치',
  tax: '세무 목적',
  litigation: '소송/분쟁',
  ipo: '상장 준비 (IPO)',
  internal: '내부 경영 목적',
  other: '기타',
}

const METHOD_LABELS: Record<string, string> = {
  dcf: 'DCF (현금흐름할인법)',
  relative: '상대가치평가',
  asset: '자산가치평가',
  intrinsic: '본질가치평가 (자본시장법)',
  tax: '세법상 평가 (상증세법)',
}

// ---------------------------------------------------------------------------
// Step 1 콘텐츠 컴포넌트
// ---------------------------------------------------------------------------

function Step1Content() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const projectId = searchParams!.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchProject() {
      try {
        const res = await fetch(`/api/projects/${projectId}`)
        if (!res.ok) throw new Error('프로젝트를 불러올 수 없습니다.')
        const data: ProjectData = await res.json()
        setProject(data)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchProject()
  }, [projectId])

  // 서류 제출 단계로 이동
  const handleSubmitDocuments = () => {
    router.push(`/valuation/process/step-2?project_id=${projectId}`)
  }

  // --- 로딩 ---
  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={1}
        stepNumber={1}
        stepTitle="프로젝트 생성"
      >
        <div className="flex items-center justify-center py-16">
          <div className="flex items-center gap-3 text-gray-500">
            <svg
              className="h-5 w-5 animate-spin"
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
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span className="text-sm">프로젝트 정보를 불러오는 중...</span>
          </div>
        </div>
      </ProcessStepTemplate>
    )
  }

  // --- 에러 ---
  if (error || !project) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={1}
        stepNumber={1}
        stepTitle="프로젝트 생성"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  // --- 정상 렌더링 ---
  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={1}
      stepTitle="프로젝트 생성"
      companyName={project.company_name_kr}
      valuationMethod={
        project.requested_methods?.[0]
          ? METHOD_LABELS[project.requested_methods[0]] ?? project.requested_methods[0]
          : undefined
      }
      projectStatus={project.status}
    >
      {/* 프로젝트 생성 완료 안내 */}
      <div className="rounded-xl border border-green-200 bg-green-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-100">
            <svg
              className="h-5 w-5 text-green-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4.5 12.75l6 6 9-13.5"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-green-800">
              프로젝트가 생성되었습니다
            </h3>
            <p className="mt-1 text-sm text-green-700">
              아래 프로젝트 정보를 확인한 후 서류 제출을 진행해 주세요.
            </p>
          </div>
        </div>
      </div>

      {/* 프로젝트 정보 카드 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">프로젝트 정보</h2>
        </div>
        <div className="px-6 py-5">
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
            <div>
              <dt className="text-sm font-medium text-gray-500">회사명 (한글)</dt>
              <dd className="mt-1 text-sm text-gray-900 font-semibold">
                {project.company_name_kr}
              </dd>
            </div>
            {project.company_name_en && (
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  회사명 (영문)
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {project.company_name_en}
                </dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500">평가 목적</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {project.valuation_purpose
                  ? PURPOSE_LABELS[project.valuation_purpose] ?? project.valuation_purpose
                  : '-'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">평가 방법</dt>
              <dd className="mt-1 flex flex-wrap gap-1.5">
                {project.requested_methods?.map((method) => (
                  <span
                    key={method}
                    className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
                  >
                    {METHOD_LABELS[method] ?? method}
                  </span>
                )) ?? (
                  <span className="text-sm text-gray-400">-</span>
                )}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">프로젝트 상태</dt>
              <dd className="mt-1">
                <span className="inline-flex items-center rounded-full bg-yellow-50 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
                  {project.status}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">생성일</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(project.created_at).toLocaleDateString('ko-KR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* 다음 단계 안내 */}
      <div className="mt-8 flex flex-col items-center gap-4">
        <p className="text-sm text-gray-600">
          프로젝트 정보 확인이 완료되면 서류를 제출해 주세요.
        </p>
        <button
          type="button"
          onClick={handleSubmitDocuments}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-700 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors"
        >
          서류 제출하기
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"
            />
          </svg>
        </button>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page (with Suspense boundary for useSearchParams)
// ---------------------------------------------------------------------------

export default function Step1Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step1Content />
    </Suspense>
  )
}
