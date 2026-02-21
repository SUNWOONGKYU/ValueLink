/**
 * @task S2F5
 * @description Step 4 - 평가 진행 중 페이지
 *
 * AI 평가 진행 상태 표시
 * 방법별 진행 세부사항 및 예상 완료 시간
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
  requested_methods: string[] | null
  status: string
  current_step: number
}

interface EvaluationProgress {
  method: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  progress: number
  started_at: string | null
  estimated_completion: string | null
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

const METHOD_DESCRIPTIONS: Record<string, string> = {
  dcf: '미래 현금흐름을 추정하고 할인율을 적용하여 기업가치를 산출합니다.',
  relative: '유사 상장기업의 멀티플을 기반으로 기업가치를 산출합니다.',
  asset: '순자산가치를 시가 기준으로 재평가하여 기업가치를 산출합니다.',
  intrinsic: '수익가치와 자산가치를 가중평균하여 본질가치를 산출합니다.',
  tax: '상속세 및 증여세법상 보충적 평가방법으로 주당 가치를 산출합니다.',
}

// ---------------------------------------------------------------------------
// 진행률 바 컴포넌트
// ---------------------------------------------------------------------------

function ProgressBar({ progress, status }: { progress: number; status: EvaluationProgress['status'] }) {
  let barColor = 'bg-blue-600'
  if (status === 'completed') barColor = 'bg-green-600'
  if (status === 'error') barColor = 'bg-red-500'

  return (
    <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-700 ${barColor}`}
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  )
}

function StatusIcon({ status }: { status: EvaluationProgress['status'] }) {
  switch (status) {
    case 'completed':
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100">
          <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </div>
      )
    case 'in_progress':
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
          <svg className="h-5 w-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
      )
    case 'error':
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-100">
          <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
      )
    default:
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      )
  }
}

// ---------------------------------------------------------------------------
// Step 4 콘텐츠
// ---------------------------------------------------------------------------

function Step4Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [progressData, setProgressData] = useState<EvaluationProgress[]>([])
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
        const [projRes, progRes] = await Promise.all([
          fetch(`/api/projects/${projectId}`),
          fetch(`/api/projects/${projectId}/evaluation-progress`),
        ])

        if (!projRes.ok) throw new Error('프로젝트를 불러올 수 없습니다.')

        const projData: ProjectData = await projRes.json()
        setProject(projData)

        if (progRes.ok) {
          const progData: EvaluationProgress[] = await progRes.json()
          setProgressData(progData)
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

    // 10초마다 진행률 폴링
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [projectId])

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={4}
        stepNumber={4}
        stepTitle="평가 진행 중"
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
        currentStep={4}
        stepNumber={4}
        stepTitle="평가 진행 중"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  // 전체 진행률 계산
  const overallProgress =
    progressData.length > 0
      ? Math.round(
          progressData.reduce((sum, p) => sum + p.progress, 0) /
            progressData.length
        )
      : 0

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={4}
      stepTitle="평가 진행 중"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 전체 진행 상태 */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-100">
            <svg className="h-5 w-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-blue-800">
              AI 기업가치 평가가 진행 중입니다
            </h3>
            <p className="mt-1 text-sm text-blue-700">
              제출하신 서류를 기반으로 평가를 수행하고 있습니다.
              평가가 완료되면 초안 보고서를 확인하실 수 있습니다.
            </p>
            <div className="mt-3 flex items-center gap-3">
              <ProgressBar progress={overallProgress} status="in_progress" />
              <span className="flex-shrink-0 text-sm font-semibold text-blue-800 tabular-nums">
                {overallProgress}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 방법별 진행 상세 */}
      <div className="space-y-4">
        {progressData.length > 0 ? (
          progressData.map((item) => (
            <div
              key={item.method}
              className="rounded-xl border border-gray-200 bg-white shadow-sm p-5"
            >
              <div className="flex items-start gap-3">
                <StatusIcon status={item.status} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-gray-900">
                      {METHOD_LABELS[item.method] ?? item.method}
                    </h3>
                    <span className="flex-shrink-0 text-xs font-medium text-gray-500 tabular-nums">
                      {item.progress}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {METHOD_DESCRIPTIONS[item.method] ?? ''}
                  </p>
                  <div className="mt-3">
                    <ProgressBar progress={item.progress} status={item.status} />
                  </div>
                  {item.estimated_completion && (
                    <p className="text-xs text-gray-400 mt-2">
                      예상 완료:{' '}
                      {new Date(item.estimated_completion).toLocaleString(
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
              </div>
            </div>
          ))
        ) : (
          /* 진행 데이터가 없을 때 기본 표시 */
          (project.requested_methods ?? []).map((method) => (
            <div
              key={method}
              className="rounded-xl border border-gray-200 bg-white shadow-sm p-5"
            >
              <div className="flex items-start gap-3">
                <StatusIcon status="pending" />
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900">
                    {METHOD_LABELS[method] ?? method}
                  </h3>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {METHOD_DESCRIPTIONS[method] ?? ''}
                  </p>
                  <div className="mt-3">
                    <ProgressBar progress={0} status="pending" />
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    평가 대기 중
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 예상 소요 시간 안내 */}
      <div className="mt-8 rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">
          예상 소요 시간
        </h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            AI 평가: 평가 방법 1건당 약 10~30분 소요
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            복수 평가 방법을 선택하신 경우 병렬로 동시 진행됩니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            평가 완료 시 이메일 알림을 보내드립니다.
          </li>
        </ul>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step4Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step4Content />
    </Suspense>
  )
}
