/**
 * @task S2F5
 * @description Step 11 - 잔금 결제 완료 페이지
 *
 * 결제 확인 메시지
 * 영수증/확인 정보 표시
 * "보고서 전달 요청" 버튼
 */

'use client'

import { useSearchParams, useRouter } from 'next/navigation'
import { useState, useEffect, Suspense } from 'react'
import ProcessStepTemplate from '@/components/process-step-template'

// ---------------------------------------------------------------------------
// 타입
// ---------------------------------------------------------------------------

interface ProjectData {
  project_id: string
  company_name_kr: string
  status: string
  current_step: number
  agreed_price: number | null
  deposit_amount: number | null
  deposit_paid_at: string | null
  balance_paid_at: string | null
}

// ---------------------------------------------------------------------------
// 금액 포맷
// ---------------------------------------------------------------------------

function formatCurrency(value: number): string {
  return value.toLocaleString('ko-KR') + '원'
}

// ---------------------------------------------------------------------------
// Step 11 콘텐츠
// ---------------------------------------------------------------------------

function Step11Content() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const projectId = searchParams.get('project_id') ?? ''

  const [project, setProject] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [requesting, setRequesting] = useState(false)

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

  const handleRequestDelivery = async () => {
    setRequesting(true)
    try {
      const res = await fetch(`/api/projects/${projectId}/request-delivery`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error('보고서 전달 요청에 실패했습니다.')
      router.push(`/valuation/process/step-12?project_id=${projectId}`)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      )
    } finally {
      setRequesting(false)
    }
  }

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={11}
        stepNumber={11}
        stepTitle="잔금 결제 완료"
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
        currentStep={11}
        stepNumber={11}
        stepTitle="잔금 결제 완료"
      >
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm text-red-700">{error ?? '프로젝트를 찾을 수 없습니다.'}</p>
        </div>
      </ProcessStepTemplate>
    )
  }

  const agreedPrice = project.agreed_price ?? 0
  const depositAmount = project.deposit_amount ?? 0
  const balanceAmount = agreedPrice - depositAmount

  return (
    <ProcessStepTemplate
      projectId={projectId}
      currentStep={project.current_step}
      stepNumber={11}
      stepTitle="잔금 결제 완료"
      companyName={project.company_name_kr}
      projectStatus={project.status}
    >
      {/* 결제 완료 안내 */}
      <div className="rounded-xl border border-green-200 bg-green-50 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-green-100">
            <svg
              className="h-6 w-6 text-green-600"
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
            <h3 className="text-base font-semibold text-green-800">
              잔금 결제가 확인되었습니다
            </h3>
            <p className="mt-1 text-sm text-green-700">
              결제가 정상적으로 처리되었습니다. 보고서 전달을 요청해 주세요.
            </p>
          </div>
        </div>
      </div>

      {/* 결제 확인서 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">결제 확인서</h2>
        </div>
        <div className="px-6 py-5">
          <dl className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <dt className="text-sm text-gray-600">프로젝트</dt>
              <dd className="text-sm font-medium text-gray-900">
                {project.company_name_kr} 기업가치 평가
              </dd>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <dt className="text-sm text-gray-600">총 평가 금액</dt>
              <dd className="text-sm font-medium text-gray-900">
                {formatCurrency(agreedPrice)}
              </dd>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <dt className="text-sm text-gray-600">계약금</dt>
              <dd className="text-sm text-gray-900">
                {formatCurrency(depositAmount)}
                {project.deposit_paid_at && (
                  <span className="ml-2 text-xs text-gray-500">
                    ({new Date(project.deposit_paid_at).toLocaleDateString('ko-KR')})
                  </span>
                )}
              </dd>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <dt className="text-sm text-gray-600">잔금</dt>
              <dd className="text-sm text-gray-900">
                {formatCurrency(balanceAmount)}
                {project.balance_paid_at && (
                  <span className="ml-2 text-xs text-gray-500">
                    ({new Date(project.balance_paid_at).toLocaleDateString('ko-KR')})
                  </span>
                )}
              </dd>
            </div>
            <div className="flex items-center justify-between py-2">
              <dt className="text-sm font-semibold text-gray-900">결제 상태</dt>
              <dd>
                <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-800">
                  결제 완료
                </span>
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* 보고서 전달 요청 */}
      <div className="flex flex-col items-center gap-4">
        <p className="text-sm text-gray-600 text-center">
          결제가 완료되었습니다. 아래 버튼을 눌러 보고서 전달을 요청해 주세요.
        </p>
        <button
          type="button"
          onClick={handleRequestDelivery}
          disabled={requesting}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-700 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {requesting ? (
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
                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
              />
            </svg>
          )}
          보고서 전달 요청
        </button>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step11Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step11Content />
    </Suspense>
  )
}
