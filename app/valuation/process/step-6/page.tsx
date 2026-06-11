/**
 * @task S2F5
 * @description Step 6 - 회계사 검토 페이지
 *
 * 회계사 검토 상태 표시
 * 검토 노트 (있는 경우) 표시
 * 고객 대기 메시지
 */

'use client'

import { useSearchParams } from 'next/navigation'
import { useState, useEffect, Suspense } from 'react'
import ProcessStepTemplate from '@/components/process-step-template'

// ---------------------------------------------------------------------------
// 타입
// ---------------------------------------------------------------------------

interface ProjectData {
  project_id: string
  company_name_kr: string
  accountant_id: string | null
  status: string
  current_step: number
}

interface ReviewData {
  accountant_name: string | null
  review_status: 'not_started' | 'in_progress' | 'completed'
  started_at: string | null
  completed_at: string | null
  review_notes: ReviewNote[]
}

interface ReviewNote {
  id: string
  method: string
  note: string
  created_at: string
}

// ---------------------------------------------------------------------------
// 상수
// ---------------------------------------------------------------------------

const METHOD_LABELS: Record<string, string> = {
  dcf: 'DCF',
  relative: '상대가치',
  asset: '자산가치',
  intrinsic: '본질가치',
  tax: '세법상 평가',
}

// ---------------------------------------------------------------------------
// 검토 상태 표시 컴포넌트
// ---------------------------------------------------------------------------

function ReviewStatusDisplay({ status }: { status: ReviewData['review_status'] }) {
  const configs = {
    not_started: {
      label: '검토 대기 중',
      description: '담당 회계사가 곧 검토를 시작합니다.',
      iconBg: 'bg-gray-100',
      iconColor: 'text-gray-500',
      borderColor: 'border-gray-200',
      bgColor: 'bg-gray-50',
    },
    in_progress: {
      label: '검토 진행 중',
      description: '담당 회계사가 AI 초안을 검토하고 있습니다.',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200',
      bgColor: 'bg-blue-50',
    },
    completed: {
      label: '검토 완료',
      description: '회계사 검토가 완료되었습니다. 다음 단계로 진행됩니다.',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200',
      bgColor: 'bg-green-50',
    },
  }

  const config = configs[status]

  return (
    <div className={`rounded-xl border ${config.borderColor} ${config.bgColor} p-5`}>
      <div className="flex items-start gap-3">
        <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${config.iconBg}`}>
          {status === 'in_progress' ? (
            <svg className={`h-5 w-5 ${config.iconColor} animate-pulse`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
          ) : status === 'completed' ? (
            <svg className={`h-5 w-5 ${config.iconColor}`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          ) : (
            <svg className={`h-5 w-5 ${config.iconColor}`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
        </div>
        <div>
          <h3 className="text-base font-semibold text-gray-900">
            {config.label}
          </h3>
          <p className="mt-1 text-sm text-gray-600">
            {config.description}
          </p>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Step 6 콘텐츠
// ---------------------------------------------------------------------------

function Step6Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams!.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [review, setReview] = useState<ReviewData | null>(null)
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
          fetch(`/api/projects/${projectId}/review`),
        ])

        if (!projRes.ok) throw new Error('프로젝트를 불러올 수 없습니다.')

        const projData: ProjectData = await projRes.json()
        setProject(projData)

        if (revRes.ok) {
          const revData: ReviewData = await revRes.json()
          setReview(revData)
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
        currentStep={6}
        stepNumber={6}
        stepTitle="회계사 검토"
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
        currentStep={6}
        stepNumber={6}
        stepTitle="회계사 검토"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  const reviewStatus = review?.review_status ?? 'not_started'

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={6}
      stepTitle="회계사 검토"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 검토 상태 */}
      <div className="mb-6">
        <ReviewStatusDisplay status={reviewStatus} />
      </div>

      {/* 검토 정보 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">검토 정보</h2>
        </div>
        <div className="px-6 py-5">
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">담당 회계사</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {review?.accountant_name ?? '배정 대기 중'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">검토 시작일</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {review?.started_at
                  ? new Date(review.started_at).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })
                  : '-'}
              </dd>
            </div>
            {review?.completed_at && (
              <div>
                <dt className="text-sm font-medium text-gray-500">검토 완료일</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(review.completed_at).toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* 검토 노트 (있는 경우) */}
      {review?.review_notes && review.review_notes.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
          <div className="border-b border-gray-100 px-6 py-4">
            <h2 className="text-lg font-semibold text-gray-900">검토 노트</h2>
          </div>
          <ul className="divide-y divide-gray-100">
            {review.review_notes.map((note) => (
              <li key={note.id} className="px-6 py-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                    {METHOD_LABELS[note.method] ?? note.method}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(note.created_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{note.note}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 프로세스 안내 */}
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">
          회계사 검토 프로세스
        </h3>
        <div className="space-y-3">
          {[
            { step: '1', title: 'AI 초안 검토', desc: '수치 정확성 및 방법론 적합성 확인' },
            { step: '2', title: '가정 검증', desc: '할인율, 성장률 등 주요 가정의 합리성 검증' },
            { step: '3', title: '수정 의견 작성', desc: '필요 시 수정 사항 반영' },
            { step: '4', title: '검토 완료', desc: '최종 검토 의견 첨부 후 고객 확인 요청' },
          ].map((item) => (
            <div key={item.step} className="flex items-start gap-3">
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-white border border-gray-300 text-xs font-semibold text-gray-600">
                {item.step}
              </span>
              <div>
                <p className="text-sm font-medium text-gray-900">{item.title}</p>
                <p className="text-xs text-gray-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 대기 안내 */}
      {reviewStatus !== 'completed' && (
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            검토가 완료되면 이메일 알림을 보내드립니다. 잠시만 기다려 주세요.
          </p>
        </div>
      )}
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step6Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step6Content />
    </Suspense>
  )
}
