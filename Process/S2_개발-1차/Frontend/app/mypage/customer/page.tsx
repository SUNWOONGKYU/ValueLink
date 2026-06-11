/**
 * @task S2F4
 * @description Customer My Page - Project dashboard and management
 *
 * - 'use client' for dynamic Supabase data fetching
 * - Shows project stats (total, in_progress, completed, pending)
 * - Lists own projects via `.eq('user_id', user.id)`
 * - "New Project" CTA button
 * - Pagination, empty state, responsive design
 * - Korean language UI, ARIA labels
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { createBrowserClient } from '@supabase/ssr'
import MyPageTemplate, {
  StatCard,
  EmptyState,
  DashboardSection,
  StatusBadge,
} from '@/components/mypage-template'
import Link from 'next/link'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Project {
  project_id: string
  company_name_kr: string
  company_name_en: string | null
  status: string
  current_step: number | null   // DB는 DEFAULT 1이지만 nullable — 사용처에서 ?? 1 방어
  valuation_purpose: string | null
  requested_methods: string[] | null
  created_at: string
  updated_at: string
}

interface Stats {
  total: number
  in_progress: number
  completed: number
  pending: number
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ITEMS_PER_PAGE = 10

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function CustomerMyPage() {
  const router = useRouter()

  // Auth state
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const [userId, setUserId] = useState<string>('')

  // Data state
  const [projects, setProjects] = useState<Project[]>([])
  const [stats, setStats] = useState<Stats>({ total: 0, in_progress: 0, completed: 0, pending: 0 })
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)

  // UI state
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  // ---- Auth check & user data fetch ----
  useEffect(() => {
    async function init() {
      try {
        const { data: { user }, error: authError } = await supabase.auth.getUser()

        if (authError || !user) {
          router.replace('/login')
          return
        }

        // Fetch user profile
        const { data: profile, error: profileError } = await supabase
          .from('users')
          .select('name, email, role')
          .eq('user_id', user.id)
          .single()

        if (profileError || !profile) {
          router.replace('/login')
          return
        }

        // Verify role
        if (profile.role !== 'customer') {
          router.replace(`/mypage/${profile.role}`)
          return
        }

        setUserName(profile.name ?? user.email?.split('@')[0] ?? '사용자')
        setUserEmail(profile.email ?? user.email ?? '')
        setUserId(user.id)
      } catch {
        setError('인증 정보를 확인할 수 없습니다.')
        setLoading(false)
      }
    }

    init()
  }, [router, supabase])

  // ---- Fetch projects ----
  const fetchProjects = useCallback(async () => {
    if (!userId) return

    setLoading(true)
    setError(null)

    try {
      // Stats query
      const { data: allProjects, error: statsError } = await supabase
        .from('projects')
        .select('status', { count: 'exact' })
        .eq('user_id', userId)

      if (statsError) throw statsError

      const newStats: Stats = { total: 0, in_progress: 0, completed: 0, pending: 0 }
      if (allProjects) {
        newStats.total = allProjects.length
        newStats.in_progress = allProjects.filter(p => p.status === 'in_progress').length
        newStats.completed = allProjects.filter(p => p.status === 'completed').length
        newStats.pending = allProjects.filter(
          p => p.status === 'human_approval' || p.status === 'draft_generated'
        ).length
      }
      setStats(newStats)

      // Paginated list query
      const from = (currentPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1

      const { data, error: listError, count } = await supabase
        .from('projects')
        .select(
          'project_id, company_name_kr, company_name_en, status, current_step, valuation_purpose, requested_methods, created_at, updated_at',
          { count: 'exact' }
        )
        .eq('user_id', userId)
        .order('updated_at', { ascending: false })
        .range(from, to)

      if (listError) throw listError

      setProjects(data ?? [])
      setTotalCount(count ?? 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }, [userId, currentPage, supabase])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // ---- Helpers ----
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE)

  function formatDate(dateString: string): string {
    const d = new Date(dateString)
    return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  function formatMethods(methods: string[] | null): string {
    if (!methods || methods.length === 0) return '-'
    const methodLabels: Record<string, string> = {
      dcf: 'DCF',
      relative: '상대가치',
      asset: '자산가치',
      intrinsic: '내재가치',
      tax: '세법상 평가',
    }
    return methods.map(m => methodLabels[m] ?? m).join(', ')
  }

  // ---- Loading state ----
  if (loading && !userName) {
    return (
      <div
        className="flex min-h-screen items-center justify-center bg-gray-50"
        role="status"
        aria-label="로딩 중"
      >
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-gray-500">마이페이지 로딩 중...</p>
        </div>
      </div>
    )
  }

  // ---- Render ----
  return (
    <MyPageTemplate role="customer" userName={userName} userEmail={userEmail}>
      {/* Error banner */}
      {error && (
        <div
          className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* ---- Stats overview ---- */}
      <DashboardSection title="프로젝트 현황" description="전체 프로젝트 진행 상태 요약">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="전체 프로젝트" value={stats.total} accentColor="blue" />
          <StatCard label="진행 중" value={stats.in_progress} accentColor="emerald" />
          <StatCard label="완료" value={stats.completed} accentColor="violet" />
          <StatCard label="대기/검토" value={stats.pending} accentColor="amber" />
        </div>
      </DashboardSection>

      {/* ---- Project list ---- */}
      <DashboardSection
        title="프로젝트 목록"
        description="등록된 프로젝트를 관리합니다"
        id="projects"
      >
        {/* CTA buttons */}
        <div className="mb-4 flex justify-end gap-2">
          <Link
            href="/projects/list"
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            전체 프로젝트 보기
          </Link>
          <Link
            href="/projects/create"
            className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            새 프로젝트 시작
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
          </div>
        ) : projects.length === 0 ? (
          <EmptyState
            title="아직 등록된 프로젝트가 없습니다"
            description="새 프로젝트를 시작하여 기업가치 평가를 받아보세요."
            actionLabel="새 프로젝트 시작"
            actionHref="/projects/create"
          />
        ) : (
          <>
            {/* Table (desktop) */}
            <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm sm:block">
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm" aria-label="프로젝트 목록">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">
                        프로젝트 ID
                      </th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">
                        회사명
                      </th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">
                        상태
                      </th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-600">
                        진행 단계
                      </th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">
                        평가 방법
                      </th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">
                        최종 수정일
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.map((project) => (
                      <tr
                        key={project.project_id}
                        className="border-b border-gray-100 transition-colors hover:bg-gray-50"
                      >
                        <td className="px-4 py-3">
                          <Link
                            href={`/projects/${project.project_id}`}
                            className="font-medium text-blue-600 hover:underline"
                          >
                            {project.project_id}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-gray-900">
                          {project.company_name_kr}
                          {project.company_name_en && (
                            <span className="ml-1 text-xs text-gray-400">
                              ({project.company_name_en})
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={project.status} />
                        </td>
                        <td className="px-4 py-3 text-center text-gray-700">
                          {project.current_step ?? 1}/14
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {formatMethods(project.requested_methods)}
                        </td>
                        <td className="px-4 py-3 text-gray-500">
                          {formatDate(project.updated_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Card list (mobile) */}
            <div className="space-y-3 sm:hidden">
              {projects.map((project) => (
                <Link
                  key={project.project_id}
                  href={`/projects/${project.project_id}`}
                  className="block rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-semibold text-blue-600">
                      {project.project_id}
                    </span>
                    <StatusBadge status={project.status} />
                  </div>
                  <p className="font-medium text-gray-900">
                    {project.company_name_kr}
                  </p>
                  <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                    <span>단계 {project.current_step ?? 1}/14</span>
                    <span>{formatDate(project.updated_at)}</span>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <nav
                className="mt-6 flex items-center justify-center gap-1"
                aria-label="페이지 네비게이션"
              >
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="이전 페이지"
                >
                  이전
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                      page === currentPage
                        ? 'bg-gray-900 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                    aria-current={page === currentPage ? 'page' : undefined}
                    aria-label={`${page} 페이지`}
                  >
                    {page}
                  </button>
                ))}
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="다음 페이지"
                >
                  다음
                </button>
              </nav>
            )}
          </>
        )}
      </DashboardSection>
    </MyPageTemplate>
  )
}
