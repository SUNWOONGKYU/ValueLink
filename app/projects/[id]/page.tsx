/**
 * @task S2F6
 * @description 프로젝트 상세 페이지 - 프로젝트 정보, 진행 상태, 퀵 액션
 *
 * - 'use client' (dynamic route, interactive)
 * - useParams()로 project_id 획득
 * - Supabase 브라우저 클라이언트 사용
 * - 14단계 진행률 시각화
 * - 반응형 Tailwind CSS, ARIA 접근성
 */

'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { createBrowserClient } from '@supabase/ssr'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ProjectStatus =
  | 'in_progress'
  | 'human_approval'
  | 'draft_generated'
  | 'completed'
  | 'archived'

type UserRole = 'customer' | 'accountant' | 'admin'

interface AccountantInfo {
  user_id: string
  email: string
  name: string | null
}

interface Project {
  project_id: string
  request_id: string
  user_id: string
  accountant_id: string | null
  company_name_kr: string
  company_name_en: string | null
  business_registration_number: string | null
  representative_name: string | null
  industry: string | null
  valuation_purpose: string
  requested_methods: string[]
  target_date: string | null
  requirements: string | null
  budget_min: number | null
  budget_max: number | null
  agreed_price: number | null
  deposit_amount: number | null
  deposit_paid_at: string | null
  balance_paid_at: string | null
  status: ProjectStatus
  current_step: number | null   // DB는 DEFAULT 1이지만 nullable — 사용처에서 ?? 1 방어
  accountant: AccountantInfo | null
  created_at: string
  updated_at: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STATUS_CONFIG: Record<
  ProjectStatus,
  { label: string; bgClass: string; textClass: string; dotClass: string }
> = {
  in_progress: {
    label: '진행 중',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
    dotClass: 'bg-blue-500',
  },
  human_approval: {
    label: '검토 중',
    bgClass: 'bg-yellow-100',
    textClass: 'text-yellow-800',
    dotClass: 'bg-yellow-500',
  },
  draft_generated: {
    label: '초안 생성',
    bgClass: 'bg-purple-100',
    textClass: 'text-purple-800',
    dotClass: 'bg-purple-500',
  },
  completed: {
    label: '완료',
    bgClass: 'bg-green-100',
    textClass: 'text-green-800',
    dotClass: 'bg-green-500',
  },
  archived: {
    label: '아카이브',
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-800',
    dotClass: 'bg-gray-500',
  },
}

const METHOD_LABELS: Record<string, string> = {
  dcf: 'DCF (현금흐름할인법)',
  relative: '상대가치평가법',
  asset: '자산가치평가법',
  intrinsic: '본질가치평가법',
  tax: '세무평가법',
}

const PURPOSE_LABELS: Record<string, string> = {
  investment: '투자 유치',
  ma: 'M&A (합병/인수)',
  ipo: 'IPO 준비',
  internal: '내부 가치 평가',
  tax: '세무 목적',
  litigation: '소송/분쟁',
  other: '기타',
}

const STEP_LABELS: string[] = [
  '프로젝트 생성',          // 1
  '기업 기본정보 확인',      // 2
  '재무제표 수집',          // 3
  '재무제표 분석',          // 4
  '산업/시장 분석',         // 5
  '평가 방법론 설정',       // 6
  '중간 검토 (사람 승인)',   // 7
  '가치평가 초안 생성',     // 8
  '보고서 초안 작성',       // 9
  '민감도 분석',            // 10
  '보고서 검토/수정',       // 11
  '최종 보고서 생성',       // 12
  '품질 검증',              // 13
  '납품 완료',              // 14
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createSupabase() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatCurrency(amount: number | null): string {
  if (amount === null || amount === undefined) return '-'
  return `${amount.toLocaleString('ko-KR')}원`
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: ProjectStatus }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.in_progress
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ${config.bgClass} ${config.textClass}`}
      role="status"
      aria-label={`프로젝트 상태: ${config.label}`}
    >
      <span className={`h-2 w-2 rounded-full ${config.dotClass}`} aria-hidden="true" />
      {config.label}
    </span>
  )
}

function ProgressTracker({ currentStep }: { currentStep: number }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">진행 단계</h2>
      <div className="mb-4 flex items-center gap-3">
        <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-blue-500 transition-all duration-500"
            style={{ width: `${Math.round((currentStep / 14) * 100)}%` }}
          />
        </div>
        <span className="text-sm font-medium text-gray-700">
          {currentStep}/14 ({Math.round((currentStep / 14) * 100)}%)
        </span>
      </div>

      {/* Step list */}
      <div className="space-y-1" role="list" aria-label="평가 프로세스 단계">
        {STEP_LABELS.map((label, index) => {
          const stepNumber = index + 1
          const isCompleted = stepNumber < currentStep
          const isCurrent = stepNumber === currentStep
          const isFuture = stepNumber > currentStep

          return (
            <div
              key={stepNumber}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                isCurrent
                  ? 'bg-blue-50 font-medium text-blue-700'
                  : isCompleted
                    ? 'text-gray-500'
                    : 'text-gray-400'
              }`}
              role="listitem"
              aria-current={isCurrent ? 'step' : undefined}
            >
              {/* Step indicator */}
              <div className="flex h-6 w-6 shrink-0 items-center justify-center">
                {isCompleted ? (
                  <svg
                    className="h-5 w-5 text-green-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                ) : isCurrent ? (
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                    {stepNumber}
                  </span>
                ) : (
                  <span className="flex h-5 w-5 items-center justify-center rounded-full border border-gray-300 text-xs text-gray-400">
                    {stepNumber}
                  </span>
                )}
              </div>

              <span className={isFuture ? 'opacity-60' : ''}>{label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function InfoCard({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">{title}</h2>
      <dl className="space-y-3">{children}</dl>
    </div>
  )
}

function InfoRow({
  label,
  value,
  children,
}: {
  label: string
  value?: string | null
  children?: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1 sm:flex-row sm:gap-4">
      <dt className="shrink-0 text-sm font-medium text-gray-500 sm:w-36">
        {label}
      </dt>
      <dd className="text-sm text-gray-900">
        {children ?? (value || '-')}
      </dd>
    </div>
  )
}

function QuickActionButton({
  label,
  description,
  href,
  icon,
  disabled = false,
}: {
  label: string
  description: string
  href: string
  icon: React.ReactNode
  disabled?: boolean
}) {
  const content = (
    <>
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
        {icon}
      </div>
      <div>
        <h3 className="text-sm font-semibold text-gray-900">{label}</h3>
        <p className="mt-0.5 text-xs text-gray-500">{description}</p>
      </div>
    </>
  )

  if (disabled) {
    return (
      <div
        className="flex w-full cursor-not-allowed items-start gap-4 rounded-xl border border-gray-200 bg-gray-50 p-4 text-left opacity-50 transition-all"
        aria-label={label}
        aria-disabled="true"
      >
        {content}
      </div>
    )
  }

  return (
    <Link
      href={href}
      className="flex w-full items-start gap-4 rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm transition-all hover:border-blue-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label={label}
    >
      {content}
    </Link>
  )
}

function PaymentStatusTag({ paid, label }: { paid: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
        paid
          ? 'bg-green-100 text-green-700'
          : 'bg-gray-100 text-gray-600'
      }`}
    >
      {paid ? (
        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )}
      {label}: {paid ? '완료' : '대기'}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Skeleton loader
// ---------------------------------------------------------------------------

function DetailSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 w-48 rounded bg-gray-200" />
      <div className="h-6 w-32 rounded bg-gray-100" />
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <div className="h-48 rounded-xl bg-gray-100" />
          <div className="h-48 rounded-xl bg-gray-100" />
        </div>
        <div className="h-96 rounded-xl bg-gray-100" />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// 403 Component
// ---------------------------------------------------------------------------

function ForbiddenView() {
  return (
    <div
      className="flex flex-col items-center justify-center px-4 py-24"
      role="alert"
    >
      <svg
        className="mb-4 h-16 w-16 text-red-300"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
        />
      </svg>
      <h2 className="mb-2 text-xl font-bold text-gray-900">접근 권한 없음</h2>
      <p className="mb-6 text-sm text-gray-500">
        이 프로젝트에 대한 접근 권한이 없습니다.
      </p>
      <Link
        href="/projects/list"
        className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        프로젝트 목록으로 돌아가기
      </Link>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function ProjectDetailPage() {
  const params = useParams()!
  const router = useRouter()
  const projectId = params.id as string

  // State
  const [project, setProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isForbidden, setIsForbidden] = useState(false)

  // Supabase client (memoized)
  const supabase = useMemo(() => createSupabase(), [])

  // Fetch project
  const fetchProject = useCallback(async () => {
    if (!projectId) {
      router.push('/projects/list')
      return
    }

    setIsLoading(true)
    setError(null)
    setIsForbidden(false)

    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) {
        setError('로그인이 필요합니다.')
        setIsLoading(false)
        return
      }

      // Get user role
      const { data: profile } = await supabase
        .from('users')
        .select('role')
        .eq('user_id', user.id)
        .single()

      const role = (profile?.role as UserRole) ?? 'customer'

      // Fetch project with accountant join
      const { data, error: fetchError } = await supabase
        .from('projects')
        .select(
          `project_id,
           request_id,
           user_id,
           accountant_id,
           company_name_kr,
           company_name_en,
           business_registration_number,
           representative_name,
           industry,
           valuation_purpose,
           requested_methods,
           target_date,
           requirements,
           budget_min,
           budget_max,
           agreed_price,
           deposit_amount,
           deposit_paid_at,
           balance_paid_at,
           status,
           current_step,
           accountant:users!projects_accountant_id_fkey (
             user_id,
             email,
             name
           ),
           created_at,
           updated_at`,
        )
        .eq('project_id', projectId)
        .single()

      if (fetchError) {
        if (fetchError.code === 'PGRST116') {
          // Not found -> redirect to list
          router.push('/projects/list')
          return
        }
        console.error('[ProjectDetailPage] Fetch error:', fetchError.message)
        setError('프로젝트 정보를 불러오는데 실패했습니다.')
        return
      }

      if (!data) {
        router.push('/projects/list')
        return
      }

      // Access control
      const isOwner = data.user_id === user.id
      const isAssigned = data.accountant_id === user.id
      const isAdmin = role === 'admin'

      if (!isOwner && !isAssigned && !isAdmin) {
        setIsForbidden(true)
        setIsLoading(false)
        return
      }

      setProject(data as unknown as Project)
    } catch (err) {
      console.error('[ProjectDetailPage] Unexpected error:', err)
      setError('예기치 않은 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }, [supabase, projectId, router])

  useEffect(() => {
    fetchProject()
  }, [fetchProject])

  // -------------------------------------------------------------------------
  // Render: Loading
  // -------------------------------------------------------------------------

  if (isLoading) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8" aria-busy="true">
        <DetailSkeleton />
        <span className="sr-only">프로젝트 정보를 불러오는 중입니다...</span>
      </main>
    )
  }

  // -------------------------------------------------------------------------
  // Render: Forbidden
  // -------------------------------------------------------------------------

  if (isForbidden) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <ForbiddenView />
      </main>
    )
  }

  // -------------------------------------------------------------------------
  // Render: Error
  // -------------------------------------------------------------------------

  if (error) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-6 text-center"
          role="alert"
        >
          <p className="text-sm text-red-700">{error}</p>
          <button
            type="button"
            onClick={fetchProject}
            className="mt-4 inline-flex items-center gap-2 rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-50"
          >
            다시 시도
          </button>
        </div>
      </main>
    )
  }

  // -------------------------------------------------------------------------
  // Render: No project (should not happen after redirect logic, but guard)
  // -------------------------------------------------------------------------

  if (!project) {
    return null
  }

  // -------------------------------------------------------------------------
  // Render: Project Detail
  // -------------------------------------------------------------------------

  const statusConfig = STATUS_CONFIG[project.status] ?? STATUS_CONFIG.in_progress

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Back navigation */}
      <Link
        href="/projects/list"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-700"
        aria-label="프로젝트 목록으로 돌아가기"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        프로젝트 목록
      </Link>

      {/* Project Header */}
      <div className="mb-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {project.company_name_kr}
            </h1>
            {project.company_name_en && (
              <p className="mt-0.5 text-sm text-gray-500">
                {project.company_name_en}
              </p>
            )}
          </div>
          <StatusBadge status={project.status} />
        </div>
        <p className="mt-2 font-mono text-xs text-gray-400">
          {project.project_id}
        </p>
      </div>

      {/* Main layout: 2 columns on large screens */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left column: Info cards */}
        <div className="space-y-6 lg:col-span-2">
          {/* Company Information */}
          <InfoCard title="기업 정보">
            <InfoRow label="회사명 (한글)" value={project.company_name_kr} />
            <InfoRow label="회사명 (영문)" value={project.company_name_en} />
            <InfoRow label="업종" value={project.industry} />
            <InfoRow label="대표자" value={project.representative_name} />
            <InfoRow
              label="사업자등록번호"
              value={project.business_registration_number}
            />
          </InfoCard>

          {/* Valuation Information */}
          <InfoCard title="평가 정보">
            <InfoRow label="평가 목적">
              <span className="font-medium">
                {PURPOSE_LABELS[project.valuation_purpose] ??
                  project.valuation_purpose}
              </span>
            </InfoRow>
            <InfoRow label="평가 방법">
              <div className="flex flex-wrap gap-1.5">
                {project.requested_methods?.map((method) => (
                  <span
                    key={method}
                    className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
                  >
                    {METHOD_LABELS[method] ?? method}
                  </span>
                ))}
                {(!project.requested_methods ||
                  project.requested_methods.length === 0) && (
                  <span className="text-gray-400">-</span>
                )}
              </div>
            </InfoRow>
            <InfoRow label="목표일" value={formatDate(project.target_date)} />
            <InfoRow label="요구사항" value={project.requirements} />
          </InfoCard>

          {/* Payment Information */}
          <InfoCard title="결제 정보">
            <InfoRow label="예산 범위">
              {project.budget_min !== null || project.budget_max !== null ? (
                <span>
                  {formatCurrency(project.budget_min)} ~{' '}
                  {formatCurrency(project.budget_max)}
                </span>
              ) : (
                '-'
              )}
            </InfoRow>
            <InfoRow
              label="합의 금액"
              value={formatCurrency(project.agreed_price)}
            />
            <InfoRow
              label="계약금"
              value={formatCurrency(project.deposit_amount)}
            />
            <InfoRow label="입금 상태">
              <div className="flex flex-wrap gap-2">
                <PaymentStatusTag
                  paid={!!project.deposit_paid_at}
                  label="계약금"
                />
                <PaymentStatusTag
                  paid={!!project.balance_paid_at}
                  label="잔금"
                />
              </div>
            </InfoRow>
            {project.deposit_paid_at && (
              <InfoRow
                label="계약금 입금일"
                value={formatDateTime(project.deposit_paid_at)}
              />
            )}
            {project.balance_paid_at && (
              <InfoRow
                label="잔금 입금일"
                value={formatDateTime(project.balance_paid_at)}
              />
            )}
          </InfoCard>

          {/* Accountant Information */}
          <InfoCard title="담당 회계사">
            {project.accountant ? (
              <>
                <InfoRow
                  label="이름"
                  value={project.accountant.name ?? '-'}
                />
                <InfoRow label="이메일" value={project.accountant.email} />
              </>
            ) : (
              <p className="text-sm text-gray-400">
                담당 회계사가 아직 배정되지 않았습니다.
              </p>
            )}
          </InfoCard>

          {/* Timeline */}
          <InfoCard title="일정">
            <InfoRow
              label="프로젝트 생성"
              value={formatDateTime(project.created_at)}
            />
            <InfoRow
              label="최종 수정"
              value={formatDateTime(project.updated_at)}
            />
          </InfoCard>
        </div>

        {/* Right column: Progress + Quick Actions */}
        <div className="space-y-6">
          {/* Progress Tracker */}
          <ProgressTracker currentStep={Math.min(Math.max(project.current_step ?? 1, 1), 14)} />

          {/* Quick Actions */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              빠른 작업
            </h2>
            <div className="space-y-3">
              <QuickActionButton
                label="프로세스 진행"
                description={`${STEP_LABELS[(project.current_step ?? 1) - 1] ?? `단계 ${project.current_step ?? 1}`} 진행하기`}
                href={`/valuation/process/step-${Math.min(Math.max(project.current_step ?? 1, 1), 12)}?project_id=${project.project_id}`}
                icon={
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                }
                disabled={
                  project.status === 'completed' ||
                  project.status === 'archived'
                }
              />
              {/* 서류 관리: /projects/{id}/documents 페이지 미구현 — 구현 전까지 비표시 */}
              {/* 보고서 확인: /projects/{id}/reports 페이지 미구현 — 구현 전까지 비표시 */}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
