/**
 * @task S2F6
 * @description 프로젝트 목록 페이지 - 검색, 필터, 정렬, 페이지네이션
 *
 * - 'use client' (interactive data fetching, search, filter)
 * - Supabase 브라우저 클라이언트 사용
 * - Role-based 프로젝트 표시
 * - 반응형 Tailwind CSS, ARIA 접근성
 */

'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
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
type SortField = 'created_at' | 'updated_at'

interface AccountantInfo {
  user_id: string
  email: string
}

interface Project {
  project_id: string
  request_id: string
  user_id: string
  accountant_id: string | null
  company_name_kr: string
  company_name_en: string | null
  industry: string | null
  valuation_purpose: string
  requested_methods: string[]
  target_date: string | null
  requirements: string | null
  status: ProjectStatus
  current_step: number
  accountant: AccountantInfo | null
  created_at: string
  updated_at: string
}

interface PaginationInfo {
  page: number
  limit: number
  total: number
  total_pages: number
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ITEMS_PER_PAGE = 10

const STATUS_CONFIG: Record<
  ProjectStatus,
  { label: string; bgClass: string; textClass: string }
> = {
  in_progress: {
    label: '진행 중',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-800',
  },
  human_approval: {
    label: '검토 중',
    bgClass: 'bg-yellow-100',
    textClass: 'text-yellow-800',
  },
  draft_generated: {
    label: '초안 생성',
    bgClass: 'bg-purple-100',
    textClass: 'text-purple-800',
  },
  completed: {
    label: '완료',
    bgClass: 'bg-green-100',
    textClass: 'text-green-800',
  },
  archived: {
    label: '아카이브',
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-800',
  },
}

const STATUS_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: '전체' },
  { value: 'in_progress', label: '진행 중' },
  { value: 'human_approval', label: '검토 중' },
  { value: 'draft_generated', label: '초안 생성' },
  { value: 'completed', label: '완료' },
  { value: 'archived', label: '아카이브' },
]

const METHOD_LABELS: Record<string, string> = {
  dcf: 'DCF',
  relative: '상대가치',
  asset: '자산가치',
  intrinsic: '본질가치',
  tax: '세무평가',
}

const PURPOSE_LABELS: Record<string, string> = {
  investment: '투자 유치',
  ma: 'M&A',
  ipo: 'IPO 준비',
  internal: '내부 가치 평가',
  tax: '세무 목적',
  litigation: '소송/분쟁',
  other: '기타',
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createSupabase() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: ProjectStatus }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.in_progress
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.bgClass} ${config.textClass}`}
      role="status"
      aria-label={`프로젝트 상태: ${config.label}`}
    >
      {config.label}
    </span>
  )
}

function StepIndicator({ step }: { step: number }) {
  const percentage = Math.round((step / 14) * 100)
  return (
    <div className="flex items-center gap-2" aria-label={`진행 단계: ${step}/14`}>
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-blue-500 transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-gray-500">
        {step}/14
      </span>
    </div>
  )
}

function MethodTag({ method }: { method: string }) {
  const label = METHOD_LABELS[method] ?? method
  return (
    <span className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
      {label}
    </span>
  )
}

function EmptyState({ onCreateClick }: { onCreateClick: () => void }) {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 bg-white px-6 py-16"
      role="status"
      aria-label="프로젝트 없음"
    >
      <svg
        className="mb-4 h-16 w-16 text-gray-300"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
        />
      </svg>
      <h3 className="mb-1 text-lg font-semibold text-gray-700">
        프로젝트가 없습니다
      </h3>
      <p className="mb-6 text-sm text-gray-500">
        새로운 가치평가 프로젝트를 시작해보세요.
      </p>
      <button
        type="button"
        onClick={onCreateClick}
        className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        aria-label="새 프로젝트 시작하기"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        새 프로젝트 시작
      </button>
    </div>
  )
}

function ProjectCard({
  project,
  userRole,
  onClick,
}: {
  project: Project
  userRole: UserRole
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="group w-full rounded-xl border border-gray-200 bg-white p-5 text-left shadow-sm transition-all hover:border-blue-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label={`프로젝트: ${project.company_name_kr}, 상태: ${STATUS_CONFIG[project.status]?.label ?? project.status}`}
    >
      {/* Header row */}
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-base font-semibold text-gray-900 group-hover:text-blue-600">
            {project.company_name_kr}
          </h3>
          {project.company_name_en && (
            <p className="truncate text-sm text-gray-500">
              {project.company_name_en}
            </p>
          )}
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {userRole === 'accountant' && (
            <span className="inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
              담당
            </span>
          )}
          <StatusBadge status={project.status} />
        </div>
      </div>

      {/* Step indicator */}
      <div className="mb-3">
        <StepIndicator step={project.current_step} />
      </div>

      {/* Info row */}
      <div className="mb-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-600">
        {project.valuation_purpose && (
          <span>
            {PURPOSE_LABELS[project.valuation_purpose] ?? project.valuation_purpose}
          </span>
        )}
        {project.industry && (
          <span className="text-gray-400">|</span>
        )}
        {project.industry && <span>{project.industry}</span>}
      </div>

      {/* Method tags */}
      {project.requested_methods && project.requested_methods.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {project.requested_methods.map((method) => (
            <MethodTag key={method} method={method} />
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-gray-100 pt-3 text-xs text-gray-400">
        <span>생성일: {formatDate(project.created_at)}</span>
        <span className="font-mono">{project.project_id}</span>
      </div>
    </button>
  )
}

function Pagination({
  pagination,
  onPageChange,
}: {
  pagination: PaginationInfo
  onPageChange: (page: number) => void
}) {
  const { page, total_pages } = pagination
  if (total_pages <= 1) return null

  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, page - Math.floor(maxVisible / 2))
  const end = Math.min(total_pages, start + maxVisible - 1)
  start = Math.max(1, end - maxVisible + 1)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return (
    <nav
      className="mt-6 flex items-center justify-center gap-1"
      aria-label="페이지 네비게이션"
    >
      <button
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="rounded-lg px-3 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
        aria-label="이전 페이지"
      >
        &laquo; 이전
      </button>

      {start > 1 && (
        <>
          <button
            type="button"
            onClick={() => onPageChange(1)}
            className="rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-100"
          >
            1
          </button>
          {start > 2 && (
            <span className="px-1 text-gray-400" aria-hidden="true">
              ...
            </span>
          )}
        </>
      )}

      {pages.map((p) => (
        <button
          key={p}
          type="button"
          onClick={() => onPageChange(p)}
          className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
            p === page
              ? 'bg-blue-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
          aria-label={`${p}페이지`}
          aria-current={p === page ? 'page' : undefined}
        >
          {p}
        </button>
      ))}

      {end < total_pages && (
        <>
          {end < total_pages - 1 && (
            <span className="px-1 text-gray-400" aria-hidden="true">
              ...
            </span>
          )}
          <button
            type="button"
            onClick={() => onPageChange(total_pages)}
            className="rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-100"
          >
            {total_pages}
          </button>
        </>
      )}

      <button
        type="button"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= total_pages}
        className="rounded-lg px-3 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
        aria-label="다음 페이지"
      >
        다음 &raquo;
      </button>
    </nav>
  )
}

// ---------------------------------------------------------------------------
// Skeleton loader
// ---------------------------------------------------------------------------

function ProjectCardSkeleton() {
  return (
    <div className="animate-pulse rounded-xl border border-gray-200 bg-white p-5">
      <div className="mb-3 flex items-start justify-between">
        <div className="flex-1">
          <div className="mb-2 h-5 w-40 rounded bg-gray-200" />
          <div className="h-4 w-28 rounded bg-gray-100" />
        </div>
        <div className="h-6 w-16 rounded-full bg-gray-200" />
      </div>
      <div className="mb-3 h-1.5 w-16 rounded-full bg-gray-200" />
      <div className="mb-3 flex gap-2">
        <div className="h-4 w-16 rounded bg-gray-100" />
        <div className="h-4 w-16 rounded bg-gray-100" />
      </div>
      <div className="flex gap-1.5">
        <div className="h-5 w-12 rounded bg-gray-100" />
        <div className="h-5 w-14 rounded bg-gray-100" />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function ProjectListPage() {
  const router = useRouter()

  // State
  const [projects, setProjects] = useState<Project[]>([])
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: ITEMS_PER_PAGE,
    total: 0,
    total_pages: 0,
  })
  const [userRole, setUserRole] = useState<UserRole>('customer')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [sortField, setSortField] = useState<SortField>('created_at')
  const [currentPage, setCurrentPage] = useState(1)

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery)
      setCurrentPage(1)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [statusFilter, sortField])

  // Supabase client (memoized)
  const supabase = useMemo(() => createSupabase(), [])

  // Fetch user role
  useEffect(() => {
    async function fetchUserRole() {
      const {
        data: { user },
      } = await supabase.auth.getUser()
      if (!user) return

      const { data: profile } = await supabase
        .from('users')
        .select('role')
        .eq('user_id', user.id)
        .single()

      if (profile?.role) {
        setUserRole(profile.role as UserRole)
      }
    }
    fetchUserRole()
  }, [supabase])

  // Fetch projects
  const fetchProjects = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) {
        setError('로그인이 필요합니다.')
        setIsLoading(false)
        return
      }

      // Get user role for role-based filtering
      const { data: profile } = await supabase
        .from('users')
        .select('role')
        .eq('user_id', user.id)
        .single()

      const role = (profile?.role as UserRole) ?? 'customer'

      // Build query
      let query = supabase
        .from('projects')
        .select(
          `project_id,
           request_id,
           user_id,
           company_name_kr,
           company_name_en,
           industry,
           valuation_purpose,
           requested_methods,
           target_date,
           requirements,
           status,
           current_step,
           accountant_id,
           accountant:users!projects_accountant_id_fkey (
             user_id,
             email
           ),
           created_at,
           updated_at`,
          { count: 'exact' },
        )

      // Role-based filtering
      switch (role) {
        case 'customer':
          query = query.eq('user_id', user.id)
          break
        case 'accountant':
          query = query.eq('accountant_id', user.id)
          break
        case 'admin':
          // Admin sees all
          break
        default:
          query = query.eq('user_id', user.id)
      }

      // Status filter
      if (statusFilter) {
        query = query.eq('status', statusFilter)
      }

      // Search filter (company_name_kr)
      if (debouncedSearch.trim()) {
        query = query.ilike('company_name_kr', `%${debouncedSearch.trim()}%`)
      }

      // Sort
      query = query.order(sortField, { ascending: false })

      // Pagination
      const from = (currentPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1
      query = query.range(from, to)

      const { data, error: fetchError, count } = await query

      if (fetchError) {
        console.error('[ProjectListPage] Fetch error:', fetchError.message)
        setError('프로젝트 목록을 불러오는데 실패했습니다.')
        return
      }

      setProjects((data as unknown as Project[]) ?? [])
      setPagination({
        page: currentPage,
        limit: ITEMS_PER_PAGE,
        total: count ?? 0,
        total_pages: count ? Math.ceil(count / ITEMS_PER_PAGE) : 0,
      })
    } catch (err) {
      console.error('[ProjectListPage] Unexpected error:', err)
      setError('예기치 않은 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }, [supabase, currentPage, statusFilter, sortField, debouncedSearch])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // Handlers
  const handleProjectClick = (projectId: string) => {
    router.push(`/projects/${projectId}`)
  }

  const handleCreateClick = () => {
    router.push('/projects/create')
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">내 프로젝트</h1>
          <p className="mt-1 text-sm text-gray-500">
            가치평가 프로젝트를 관리하세요.
            {pagination.total > 0 && (
              <span className="ml-1 font-medium text-gray-700">
                총 {pagination.total}건
              </span>
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={handleCreateClick}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          aria-label="새 프로젝트 만들기"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          새 프로젝트
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="mb-6 flex flex-col gap-3 rounded-xl border border-gray-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center">
        {/* Search */}
        <div className="relative flex-1">
          <svg
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="회사명으로 검색..."
            className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            aria-label="회사명 검색"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-3">
          <label htmlFor="status-filter" className="sr-only">
            상태 필터
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-gray-300 py-2 pl-3 pr-8 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            aria-label="프로젝트 상태 필터"
          >
            {STATUS_FILTER_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Sort */}
          <label htmlFor="sort-field" className="sr-only">
            정렬 기준
          </label>
          <select
            id="sort-field"
            value={sortField}
            onChange={(e) => setSortField(e.target.value as SortField)}
            className="rounded-lg border border-gray-300 py-2 pl-3 pr-8 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            aria-label="정렬 기준"
          >
            <option value="created_at">생성일순</option>
            <option value="updated_at">수정일순</option>
          </select>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div
          className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
          role="alert"
        >
          <div className="flex items-center gap-2">
            <svg
              className="h-4 w-4 shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
          aria-label="프로젝트 목록 로딩 중"
          role="status"
        >
          {Array.from({ length: 6 }).map((_, i) => (
            <ProjectCardSkeleton key={i} />
          ))}
          <span className="sr-only">프로젝트 목록을 불러오는 중입니다...</span>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && projects.length === 0 && (
        <EmptyState onCreateClick={handleCreateClick} />
      )}

      {/* Project Grid */}
      {!isLoading && !error && projects.length > 0 && (
        <>
          <div
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
            role="list"
            aria-label="프로젝트 목록"
          >
            {projects.map((project) => (
              <div key={project.project_id} role="listitem">
                <ProjectCard
                  project={project}
                  userRole={userRole}
                  onClick={() => handleProjectClick(project.project_id)}
                />
              </div>
            ))}
          </div>

          {/* Pagination */}
          <Pagination
            pagination={pagination}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </main>
  )
}
