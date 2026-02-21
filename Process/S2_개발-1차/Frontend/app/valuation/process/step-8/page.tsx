/**
 * @task S2F5
 * @description Step 8 - 수정 요청/반영 페이지 (draft_generated)
 *
 * 수정 요청 상세 내용 표시
 * 수정 진행 상태 트래킹
 * 수정된 초안 미리보기
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

interface RevisionRequest {
  id: string
  feedback: string
  status: 'pending' | 'in_progress' | 'completed'
  requested_at: string
  completed_at: string | null
  revision_notes: string | null
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
// 수정 상태 뱃지
// ---------------------------------------------------------------------------

function RevisionStatusBadge({ status }: { status: RevisionRequest['status'] }) {
  const configs = {
    pending: { label: '수정 대기', className: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
    in_progress: { label: '수정 중', className: 'bg-blue-50 text-blue-700 border-blue-200' },
    completed: { label: '수정 완료', className: 'bg-green-50 text-green-700 border-green-200' },
  }

  const config = configs[status]

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Step 8 콘텐츠
// ---------------------------------------------------------------------------

function Step8Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [revisions, setRevisions] = useState<RevisionRequest[]>([])
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
        const [projRes, revRes] = await Promise.all([
          fetch(`/api/projects/${projectId}`),
          fetch(`/api/projects/${projectId}/revisions`),
        ])

        if (!projRes.ok) throw new Error('프로젝트를 불러올 수 없습니다.')

        const projData: ProjectData = await projRes.json()
        setProject(projData)

        if (revRes.ok) {
          const revData: RevisionRequest[] = await revRes.json()
          setRevisions(revData)
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

    // 30초마다 상태 확인
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [projectId])

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={8}
        stepNumber={8}
        stepTitle="수정 요청/반영"
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
        currentStep={8}
        stepNumber={8}
        stepTitle="수정 요청/반영"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  const allCompleted = revisions.length > 0 && revisions.every((r) => r.status === 'completed')

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={8}
      stepTitle="수정 요청/반영"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 상태 안내 */}
      <div
        className={`rounded-xl border p-5 mb-6 ${
          allCompleted
            ? 'border-green-200 bg-green-50'
            : 'border-blue-200 bg-blue-50'
        }`}
      >
        <div className="flex items-start gap-3">
          <div
            className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full ${
              allCompleted ? 'bg-green-100' : 'bg-blue-100'
            }`}
          >
            {allCompleted ? (
              <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            ) : (
              <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
              </svg>
            )}
          </div>
          <div>
            <h3
              className={`text-sm font-semibold ${
                allCompleted ? 'text-green-800' : 'text-blue-800'
              }`}
            >
              {allCompleted ? '수정이 완료되었습니다' : '수정 사항을 반영 중입니다'}
            </h3>
            <p
              className={`mt-1 text-sm ${
                allCompleted ? 'text-green-700' : 'text-blue-700'
              }`}
            >
              {allCompleted
                ? '수정된 보고서를 다시 확인해 주세요. 이상이 없으면 최종 보고서 생성으로 진행됩니다.'
                : '요청하신 수정 사항을 검토하고 반영 중입니다. 완료 시 알림을 보내드립니다.'}
            </p>
          </div>
        </div>
      </div>

      {/* 수정 요청 이력 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
        <div className="border-b border-gray-100 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">수정 요청 내역</h2>
            <span className="text-sm text-gray-500">총 {revisions.length}건</span>
          </div>
        </div>

        {revisions.length > 0 ? (
          <ul className="divide-y divide-gray-100">
            {revisions.map((revision, idx) => (
              <li key={revision.id} className="px-6 py-5">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-900">
                      수정 요청 #{revisions.length - idx}
                    </span>
                    <RevisionStatusBadge status={revision.status} />
                  </div>
                  <span className="text-xs text-gray-500 flex-shrink-0">
                    {new Date(revision.requested_at).toLocaleDateString('ko-KR', {
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>

                {/* 고객 요청 내용 */}
                <div className="rounded-lg bg-gray-50 p-4 mb-3">
                  <p className="text-xs font-medium text-gray-500 mb-1">
                    고객 의견
                  </p>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {revision.feedback}
                  </p>
                </div>

                {/* 수정 결과 (완료 시) */}
                {revision.status === 'completed' && revision.revision_notes && (
                  <div className="rounded-lg bg-blue-50 p-4">
                    <p className="text-xs font-medium text-blue-600 mb-1">
                      수정 반영 결과
                    </p>
                    <p className="text-sm text-blue-800 whitespace-pre-wrap">
                      {revision.revision_notes}
                    </p>
                    {revision.completed_at && (
                      <p className="text-xs text-blue-500 mt-2">
                        완료:{' '}
                        {new Date(revision.completed_at).toLocaleDateString(
                          'ko-KR',
                          {
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          }
                        )}
                      </p>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <div className="px-6 py-12 text-center">
            <p className="text-sm text-gray-500">수정 요청 내역이 없습니다.</p>
          </div>
        )}
      </div>

      {/* 수정된 초안 확인 (수정 완료 시) */}
      {allCompleted && (
        <div className="flex flex-col items-center gap-4">
          <p className="text-sm text-gray-600">
            수정된 초안 보고서를 확인해 주세요.
          </p>
          <div className="flex flex-wrap gap-2">
            {(project.requested_methods ?? []).map((method) => (
              <Link
                key={method}
                href={`/valuation-results/${method}?project_id=${projectId}&draft=true&revision=latest`}
                className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <svg
                  className="h-4 w-4 text-gray-400"
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
                {METHOD_LABELS[method] ?? method} 수정본
              </Link>
            ))}
          </div>
        </div>
      )}
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step8Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step8Content />
    </Suspense>
  )
}
