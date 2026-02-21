/**
 * @task S2F5
 * @description Step 5 - AI 초안 생성 페이지
 *
 * 초안 보고서 요약 표시
 * 주요 발견 사항 미리보기
 * "초안 확인하기" 버튼
 */

'use client'

import { useSearchParams } from 'next/navigation'
import { useState, useEffect, Suspense } from 'react'
import Link from 'next/link'
import ProcessStepTemplate from '@/components/process-step-template'

// ---------------------------------------------------------------------------
// 타입
// ---------------------------------------------------------------------------

interface ProjectData {
  project_id: string
  company_name_kr: string
  requested_methods: string[] | null
  status: string
  current_step: number
}

interface DraftSummary {
  method: string
  enterprise_value: number
  equity_value: number
  value_per_share: number
  key_findings: string[]
  generated_at: string
}

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const METHOD_LABELS: Record<string, string> = {
  dcf: 'DCF (현금흐름할인법)',
  relative: '상대가치평가',
  asset: '자산가치평가',
  intrinsic: '본질가치평가',
  tax: '세법상 평가',
}

// ---------------------------------------------------------------------------
// 금액 포맷
// ---------------------------------------------------------------------------

function formatKRW(value: number): string {
  if (value >= 1_0000_0000) {
    return `${(value / 1_0000_0000).toFixed(1)}억원`
  }
  if (value >= 1_0000) {
    return `${(value / 1_0000).toFixed(0)}만원`
  }
  return `${value.toLocaleString('ko-KR')}원`
}

// ---------------------------------------------------------------------------
// Step 5 콘텐츠
// ---------------------------------------------------------------------------

function Step5Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [drafts, setDrafts] = useState<DraftSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setError('프로젝트 ID가 없습니다.')
      setLoading(false)
      return
    }

    async function fetchData() {
      try {
        const [projRes, draftRes] = await Promise.all([
          fetch(`/api/projects/${projectId}`),
          fetch(`/api/projects/${projectId}/drafts`),
        ])

        if (!projRes.ok) throw new Error('프로젝트를 불러올 수 없습니다.')

        const projData: ProjectData = await projRes.json()
        setProject(projData)

        if (draftRes.ok) {
          const draftData: DraftSummary[] = await draftRes.json()
          setDrafts(draftData)
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [projectId])

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={5}
        stepNumber={5}
        stepTitle="AI 초안 생성"
      >
        <div className="flex items-center justify-center py-16">
          <div className="flex items-center gap-3 text-gray-500">
            <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-sm">로딩 중...</span>
          </div>
        </div>
      </ProcessStepTemplate>
    )
  }

  if (error || !project) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={5}
        stepNumber={5}
        stepTitle="AI 초안 생성"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={5}
      stepTitle="AI 초안 생성"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 안내 메시지 */}
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100">
            <svg
              className="h-5 w-5 text-emerald-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-emerald-800">
              AI 초안 보고서가 생성되었습니다
            </h3>
            <p className="mt-1 text-sm text-emerald-700">
              아래 요약을 확인한 후, 상세 초안 보고서를 검토해 주세요.
              이 초안은 회계사 검토를 거친 후 최종 보고서로 완성됩니다.
            </p>
          </div>
        </div>
      </div>

      {/* 초안 요약 카드 */}
      <div className="space-y-4">
        {drafts.length > 0 ? (
          drafts.map((draft) => (
            <div
              key={draft.method}
              className="rounded-xl border border-gray-200 bg-white shadow-sm"
            >
              <div className="border-b border-gray-100 px-6 py-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold text-gray-900">
                    {METHOD_LABELS[draft.method] ?? draft.method}
                  </h2>
                  <span className="text-xs text-gray-500">
                    {new Date(draft.generated_at).toLocaleDateString('ko-KR')} 생성
                  </span>
                </div>
              </div>

              <div className="px-6 py-5">
                {/* 핵심 수치 */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <dt className="text-xs text-gray-500">기업가치 (EV)</dt>
                    <dd className="mt-1 text-lg font-bold text-gray-900">
                      {formatKRW(draft.enterprise_value)}
                    </dd>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <dt className="text-xs text-gray-500">자기자본가치</dt>
                    <dd className="mt-1 text-lg font-bold text-gray-900">
                      {formatKRW(draft.equity_value)}
                    </dd>
                  </div>
                  <div className="rounded-lg bg-blue-50 p-3 text-center">
                    <dt className="text-xs text-blue-600">주당 가치</dt>
                    <dd className="mt-1 text-lg font-bold text-blue-700">
                      {formatKRW(draft.value_per_share)}
                    </dd>
                  </div>
                </div>

                {/* 주요 발견 사항 */}
                {draft.key_findings.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      주요 발견 사항
                    </h4>
                    <ul className="space-y-1.5">
                      {draft.key_findings.map((finding, idx) => (
                        <li
                          key={idx}
                          className="flex items-start gap-2 text-sm text-gray-600"
                        >
                          <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-blue-400" />
                          {finding}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center">
            <p className="text-sm text-gray-500">
              초안 데이터를 불러올 수 없습니다.
            </p>
          </div>
        )}
      </div>

      {/* 초안 확인하기 버튼 */}
      <div className="mt-8 flex flex-col items-center gap-4">
        <p className="text-sm text-gray-600">
          상세 초안 보고서를 확인하고 검토를 요청하세요.
        </p>
        <Link
          href={`/valuation-results/draft?project_id=${projectId}`}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-700 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors"
        >
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
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
          초안 확인하기
        </Link>
      </div>

      {/* 안내 사항 */}
      <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">참고 사항</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            이 초안은 AI가 생성한 것으로, 회계사 검토를 거쳐 최종 확정됩니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            수치는 제출하신 서류를 기반으로 산출되었습니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            초안 확인 후 7단계에서 승인 또는 수정 요청이 가능합니다.
          </li>
        </ul>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step5Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step5Content />
    </Suspense>
  )
}
