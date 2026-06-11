/**
 * @task S2F5
 * @description Step 7 - 고객 확인 요청 페이지 (human_approval)
 *
 * 초안 보고서 고객 검토
 * 승인/수정 요청 버튼
 * 의견 및 피드백 입력
 */

'use client'

import { useSearchParams, useRouter } from 'next/navigation'
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
  current_step: number | null   // DB는 DEFAULT 1이지만 nullable — 사용처에서 ?? 1 방어
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
// Step 7 콘텐츠
// ---------------------------------------------------------------------------

function Step7Content() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const projectId = searchParams!.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [feedback, setFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

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

  // 승인 처리
  const handleApprove = async () => {
    setSubmitting(true)
    setSubmitError(null)

    try {
      const res = await fetch(`/api/projects/${projectId}/approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'approve',
          feedback: feedback.trim() || null,
        }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.message ?? '승인 처리에 실패했습니다.')
      }

      router.push(`/valuation/process/step-9?project_id=${projectId}`)
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  // 수정 요청 처리
  const handleRequestRevision = async () => {
    if (!feedback.trim()) {
      setSubmitError('수정 요청 시 의견을 입력해 주세요.')
      return
    }

    setSubmitting(true)
    setSubmitError(null)

    try {
      const res = await fetch(`/api/projects/${projectId}/approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'request_revision',
          feedback: feedback.trim(),
        }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.message ?? '수정 요청에 실패했습니다.')
      }

      router.push(`/valuation/process/step-8?project_id=${projectId}`)
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={7}
        stepNumber={7}
        stepTitle="고객 확인 요청"
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
        currentStep={7}
        stepNumber={7}
        stepTitle="고객 확인 요청"
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
      currentStep={project.current_step ?? 1}
      stepNumber={7}
      stepTitle="고객 확인 요청"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 안내 메시지 */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-amber-100">
            <svg
              className="h-5 w-5 text-amber-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-amber-800">
              고객님의 확인이 필요합니다
            </h3>
            <p className="mt-1 text-sm text-amber-700">
              회계사가 검토를 완료한 초안 보고서를 확인해 주세요.
              승인하시면 최종 보고서 생성으로 진행되며,
              수정이 필요하시면 의견을 남겨주세요.
            </p>
          </div>
        </div>
      </div>

      {/* 초안 보고서 링크 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">
            검토 완료된 초안 보고서
          </h2>
        </div>
        <div className="px-6 py-5">
          <p className="text-sm text-gray-600 mb-4">
            아래 링크에서 평가 방법별 초안 보고서를 확인하실 수 있습니다.
          </p>
          <div className="flex flex-wrap gap-2">
            {(project.requested_methods ?? []).map((method) => (
              <Link
                key={method}
                href={`/valuation-results/${method}?project_id=${projectId}&draft=true`}
                className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
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
                {METHOD_LABELS[method] ?? method}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* 의견/피드백 입력 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">의견 및 피드백</h2>
        </div>
        <div className="px-6 py-5">
          <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-2">
            검토 의견 (수정 요청 시 필수)
          </label>
          <textarea
            id="feedback"
            rows={5}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="수정이 필요한 부분이나 의견을 자유롭게 작성해 주세요..."
            className="block w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-colors resize-y"
            disabled={submitting}
          />
          <p className="mt-2 text-xs text-gray-500">
            승인 시에도 참고 의견을 남기실 수 있습니다.
          </p>
        </div>
      </div>

      {/* 에러 메시지 */}
      {submitError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 mb-6">
          <p className="text-sm text-red-700">{submitError}</p>
        </div>
      )}

      {/* 액션 버튼 */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
        <button
          type="button"
          onClick={handleRequestRevision}
          disabled={submitting}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
              d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
            />
          </svg>
          수정 요청
        </button>
        <button
          type="button"
          onClick={handleApprove}
          disabled={submitting}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg bg-blue-700 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? (
            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
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
                d="M4.5 12.75l6 6 9-13.5"
              />
            </svg>
          )}
          승인하기
        </button>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step7Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step7Content />
    </Suspense>
  )
}
