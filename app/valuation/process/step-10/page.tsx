/**
 * @task S2F5
 * @description Step 10 - 잔금 결제 요청 페이지
 *
 * 결제 요약 (agreed_price, deposit, balance)
 * 계좌 정보 (우리은행, 계좌번호 복사 기능)
 * 결제 안내
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
  status: string
  current_step: number
  agreed_price: number | null
  deposit_amount: number | null
  deposit_paid_at: string | null
}

// ---------------------------------------------------------------------------
// 금액 포맷
// ---------------------------------------------------------------------------

function formatCurrency(value: number): string {
  return value.toLocaleString('ko-KR') + '원'
}

// ---------------------------------------------------------------------------
// 계좌번호 복사 버튼
// ---------------------------------------------------------------------------

function AccountCopyButton() {
  const [copied, setCopied] = useState(false)

  const accountNumber = '1005-404-483025'

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(accountNumber)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // 클립보드 API 미지원 시 대체 방법
      const textarea = document.createElement('textarea')
      textarea.value = accountNumber
      textarea.style.position = 'fixed'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch {
        // 복사 실패 무시
      }
      document.body.removeChild(textarea)
    }
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
        copied
          ? 'bg-green-100 text-green-700 border border-green-300'
          : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
      }`}
      aria-label="계좌번호 복사"
    >
      {copied ? (
        <>
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          복사됨
        </>
      ) : (
        <>
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
          </svg>
          복사
        </>
      )}
    </button>
  )
}

// ---------------------------------------------------------------------------
// Step 10 콘텐츠
// ---------------------------------------------------------------------------

function Step10Content() {
  const searchParams = useSearchParams()
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

  if (loading) {
    return (
      <ProcessStepTemplate
        projectId={projectId}
        currentStep={10}
        stepNumber={10}
        stepTitle="잔금 결제 요청"
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
        currentStep={10}
        stepNumber={10}
        stepTitle="잔금 결제 요청"
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
      stepNumber={10}
      stepTitle="잔금 결제 요청"
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
                d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-amber-800">
              잔금 결제가 필요합니다
            </h3>
            <p className="mt-1 text-sm text-amber-700">
              최종 보고서 전달을 위해 잔금 결제를 완료해 주세요.
              결제 확인 후 보고서가 전달됩니다.
            </p>
          </div>
        </div>
      </div>

      {/* 결제 요약 */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm mb-6">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">결제 요약</h2>
        </div>
        <div className="px-6 py-5">
          <dl className="space-y-4">
            <div className="flex items-center justify-between py-2">
              <dt className="text-sm text-gray-600">총 평가 금액</dt>
              <dd className="text-sm font-semibold text-gray-900">
                {formatCurrency(agreedPrice)}
              </dd>
            </div>
            <div className="flex items-center justify-between py-2">
              <dt className="text-sm text-gray-600">
                계약금 (납부 완료)
                {project.deposit_paid_at && (
                  <span className="ml-1 text-xs text-green-600">
                    {new Date(project.deposit_paid_at).toLocaleDateString('ko-KR')}
                  </span>
                )}
              </dt>
              <dd className="text-sm text-gray-600">
                -{formatCurrency(depositAmount)}
              </dd>
            </div>
            <div className="flex items-center justify-between border-t border-gray-200 pt-4">
              <dt className="text-base font-semibold text-gray-900">
                잔금 (결제 필요)
              </dt>
              <dd className="text-xl font-bold text-blue-700">
                {formatCurrency(balanceAmount)}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* 계좌 정보 */}
      <div className="rounded-xl border-2 border-blue-200 bg-blue-50 shadow-sm mb-6">
        <div className="border-b border-blue-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-blue-900">입금 계좌 정보</h2>
        </div>
        <div className="px-6 py-5">
          <dl className="space-y-4">
            <div className="flex items-center justify-between">
              <dt className="text-sm font-medium text-blue-800">은행</dt>
              <dd className="text-sm font-semibold text-blue-900">우리은행</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-sm font-medium text-blue-800">계좌번호</dt>
              <dd className="flex items-center gap-2">
                <span className="text-lg font-bold text-blue-900 tracking-wider tabular-nums">
                  1005-404-483025
                </span>
                <AccountCopyButton />
              </dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-sm font-medium text-blue-800">예금주</dt>
              <dd className="text-sm font-semibold text-blue-900">
                호수회계법인
              </dd>
            </div>
            <div className="flex items-center justify-between border-t border-blue-200 pt-4">
              <dt className="text-sm font-medium text-blue-800">입금액</dt>
              <dd className="text-lg font-bold text-blue-900">
                {formatCurrency(balanceAmount)}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* 입금 안내 */}
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">
          결제 안내
        </h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            입금자명은 <span className="font-semibold">회사명 또는 대표자명</span>으로
            입금해 주세요.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            입금 확인은 영업일 기준 <span className="font-semibold">1일 이내</span>에
            처리됩니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            입금 확인이 완료되면 자동으로 다음 단계로 진행됩니다.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gray-400" />
            세금계산서 발행이 필요하시면 별도 문의 바랍니다.
          </li>
        </ul>
      </div>

      {/* 문의 안내 */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          결제 관련 문의:{' '}
          <a
            href="mailto:support@valuelink.kr"
            className="font-medium text-blue-700 hover:text-blue-800 transition-colors"
          >
            support@valuelink.kr
          </a>
        </p>
      </div>
    </ProcessStepTemplate>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Step10Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <p className="text-sm text-gray-500">로딩 중...</p>
        </div>
      }
    >
      <Step10Content />
    </Suspense>
  )
}
