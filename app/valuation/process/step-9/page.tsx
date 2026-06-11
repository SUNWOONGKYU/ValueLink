/**
 * @task S2F5
 * @description Step 9 - 최종 보고서 생성 페이지
 *
 * 최종 보고서 생성 상태 표시
 * 보고서 미리보기
 * 다운로드 옵션 (준비 완료 시)
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

interface ReportStatus {
  method: string
  status: 'generating' | 'completed' | 'error'
  file_url: string | null
  generated_at: string | null
  page_count: number | null
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
// Step 9 콘텐츠
// ---------------------------------------------------------------------------

function Step9Content() {
  const searchParams = useSearchParams()
  const projectId = searchParams!.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [reports, setReports] = useState<ReportStatus[]>([])
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
        const [projRes, repRes] = await Promise.all([
          fetch(`/api/projects/${projectId}`),
          fetch(`/api/projects/${projectId}/final-reports`),
        ])

        if (!projRes.ok) throw new Error('프로젝트를 불러올 수 없습니다.')

        const projData: ProjectData = await projRes.json()
        setProject(projData)

        if (repRes.ok) {
          const repData: ReportStatus[] = await repRes.json()
          setReports(repData)
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

    // 생성 중일 때 10초마다 폴링
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [projectId])

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={9}
        stepNumber={9}
        stepTitle="최종 보고서 생성"
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
        currentStep={9}
        stepNumber={9}
        stepTitle="최종 보고서 생성"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  const allCompleted = reports.length > 0 && reports.every((r) => r.status === 'completed')
  const hasGenerating = reports.some((r) => r.status === 'generating')

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={9}
      stepTitle="최종 보고서 생성"
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
              <svg className="h-5 w-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
          </div>
          <div>
            <h3
              className={`text-sm font-semibold ${
                allCompleted ? 'text-green-800' : 'text-blue-800'
              }`}
            >
              {allCompleted
                ? '최종 보고서가 생성되었습니다'
                : '최종 보고서를 생성하고 있습니다'}
            </h3>
            <p
              className={`mt-1 text-sm ${
                allCompleted ? 'text-green-700' : 'text-blue-700'
              }`}
            >
              {allCompleted
                ? '아래에서 보고서를 미리보기하거나 다운로드할 수 있습니다.'
                : '고객 승인을 기반으로 최종 보고서를 생성 중입니다. 잠시만 기다려 주세요.'}
            </p>
          </div>
        </div>
      </div>

      {/* 보고서 목록 */}
      <div className="space-y-4">
        {reports.length > 0 ? (
          reports.map((report) => (
            <div
              key={report.method}
              className="rounded-xl border border-gray-200 bg-white shadow-sm"
            >
              <div className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center gap-3">
                  {/* 아이콘 */}
                  <div
                    className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg ${
                      report.status === 'completed'
                        ? 'bg-green-100'
                        : report.status === 'error'
                        ? 'bg-red-100'
                        : 'bg-blue-100'
                    }`}
                  >
                    {report.status === 'completed' ? (
                      <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                    ) : report.status === 'error' ? (
                      <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    )}
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-gray-900">
                      {METHOD_LABELS[report.method] ?? report.method}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {report.status === 'completed' && report.generated_at
                        ? `${new Date(report.generated_at).toLocaleDateString('ko-KR')} 생성${report.page_count ? ` | ${report.page_count}p` : ''}`
                        : report.status === 'error'
                        ? '생성 실패'
                        : '생성 중...'}
                    </p>
                  </div>
                </div>

                {/* 액션 버튼 */}
                {report.status === 'completed' && (
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/valuation-results/${report.method}?project_id=${projectId}&final=true`}
                      className="inline-flex items-center gap-1 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      미리보기
                    </Link>
                    {report.file_url && (
                      <a
                        href={report.file_url}
                        download
                        className="inline-flex items-center gap-1 rounded-lg bg-blue-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-800 transition-colors"
                      >
                        <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                        </svg>
                        PDF
                      </a>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center">
            <p className="text-sm text-gray-500">
              {hasGenerating
                ? '보고서를 생성하고 있습니다...'
                : '보고서 생성 대기 중입니다.'}
            </p>
          </div>
        )}
      </div>

      {/* 안내 */}
      <div className="mt-8 rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">안내 사항</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            최종 보고서는 회계사 검토 및 고객 승인이 완료된 내용을 포함합니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            보고서 생성 후 잔금 결제를 완료하시면 최종 보고서를 받으실 수 있습니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            PDF 파일로 다운로드 가능하며, 인쇄용으로 최적화되어 있습니다.
          </li>
        </ul>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step9Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step9Content />
    </Suspense>
  )
}
