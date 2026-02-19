/**
 * @task S2F4
 * @description Accountant My Page - Assigned project management and review dashboard
 *
 * - 'use client' for dynamic Supabase data fetching
 * - Shows stats: assigned projects, pending reviews, completed
 * - Lists assigned projects via `.eq('accountant_id', user.id)`
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

interface AssignedProject {
  project_id: string
  company_name_kr: string
  company_name_en: string | null
  status: string
  current_step: number
  valuation_purpose: string | null
  requested_methods: string[] | null
  created_at: string
  updated_at: string
}

interface AccountantStats {
  assigned: number
  pending_review: number
  completed: number
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

export default function AccountantMyPage() {
  const router = useRouter()

  // Auth
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const [userId, setUserId] = useState<string>('')

  // Data
  const [projects, setProjects] = useState<AssignedProject[]>([])
  const [stats, setStats] = useState<AccountantStats>({ assigned: 0, pending_review: 0, completed: 0 })
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // UI
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  // ---- Auth check ----
  useEffect(() => {
    async function init() {
      try {
        const { data: { user }, error: authError } = await supabase.auth.getUser()

        if (authError || !user) {
          router.replace('/auth/login')
          return
        }

        const { data: profile, error: profileError } = await supabase
          .from('users')
          .select('name, email, role')
          .eq('user_id', user.id)
          .single()

        if (profileError || !profile) {
          router.replace('/auth/login')
          return
        }

        if (profile.role !== 'accountant') {
          router.replace(`/mypage/${profile.role}`)
          return
        }

        setUserName(profile.name ?? user.email?.split('@')[0] ?? '회계사')
        setUserEmail(profile.email ?? user.email ?? '')
        setUserId(user.id)
      } catch {
        setError('인증 정보를 확인할 수 없습니다.')
        setLoading(false)
      }
    }

    init()
  }, [router, supabase])

  // ---- Fetch assigned projects ----
  const fetchProjects = useCallback(async () => {
    if (!userId) return

    setLoading(true)
    setError(null)

    try {
      // Stats
      const { data: allProjects, error: statsError } = await supabase
        .from('projects')
        .select('status')
        .eq('accountant_id', userId)

      if (statsError) throw statsError

      const newStats: AccountantStats = { assigned: 0, pending_review: 0, completed: 0 }
      if (allProjects) {
        newStats.assigned = allProjects.length
        newStats.pending_review = allProjects.filter(
          p => p.status === 'human_approval' || p.status === 'draft_generated'
        ).length
        newStats.completed = allProjects.filter(p => p.status === 'completed').length
      }
      setStats(newStats)

      // Paginated list
      const from = (currentPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1

      let query = supabase
        .from('projects')
        .select(
          'project_id, company_name_kr, company_name_en, status, current_step, valuation_purpose, requested_methods, created_at, updated_at',
          { count: 'exact' }
        )
        .eq('accountant_id', userId)

      if (statusFilter !== 'all') {
        query = query.eq('status', statusFilter)
      }

      const { data, error: listError, count } = await query
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
  }, [userId, currentPage, statusFilter, supabase])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // ---- Helpers ----
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE)

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  function formatMethods(methods: string[] | null): string {
    if (!methods || methods.length === 0) return '-'
    const labels: Record<string, string> = {
      dcf: 'DCF', relative: '상대가치', asset: '자산가치',
      intrinsic: '내재가치', tax: '세법상 평가',
    }
    return methods.map(m => labels[m] ?? m).join(', ')
  }

  // ---- Loading ----
  if (loading && !userName) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50" role="status" aria-label="로딩 중">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />
          <p className="text-sm text-gray-500">마이페이지 로딩 중...</p>
        </div>
      </div>
    )
  }

  // ---- Render ----
  return (
    <MyPageTemplate role="accountant" userName={userName} userEmail={userEmail}>
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      {/* Stats */}
      <DashboardSection title="업무 현황" description="배정된 프로젝트 검토 상태 요약">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard label="배정 프로젝트" value={stats.assigned} accentColor="emerald" />
          <StatCard label="검토 대기" value={stats.pending_review} accentColor="amber" />
          <StatCard label="검토 완료" value={stats.completed} accentColor="blue" />
        </div>
      </DashboardSection>

      {/* Project list */}
      <DashboardSection
        title="배정 프로젝트 목록"
        description="검토가 필요한 프로젝트를 확인하세요"
        id="projects"
      >
        {/* Filter tabs */}
        <div className="mb-4 flex flex-wrap gap-2" role="tablist" aria-label="프로젝트 상태 필터">
          {[
            { value: 'all', label: '전체' },
            { value: 'human_approval', label: '승인 대기' },
            { value: 'in_progress', label: '진행 중' },
            { value: 'completed', label: '완료' },
          ].map(tab => (
            <button
              key={tab.value}
              onClick={() => { setStatusFilter(tab.value); setCurrentPage(1) }}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                statusFilter === tab.value
                  ? 'bg-emerald-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
              role="tab"
              aria-selected={statusFilter === tab.value}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />
          </div>
        ) : projects.length === 0 ? (
          <EmptyState
            title="배정된 프로젝트가 없습니다"
            description="현재 검토가 필요한 프로젝트가 없습니다."
          />
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm sm:block">
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm" aria-label="배정 프로젝트 목록">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">프로젝트 ID</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">회사명</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">상태</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-600">진행 단계</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">평가 목적</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">평가 방법</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">최종 수정일</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.map(project => (
                      <tr
                        key={project.project_id}
                        className="border-b border-gray-100 transition-colors hover:bg-gray-50"
                      >
                        <td className="px-4 py-3">
                          <Link
                            href={`/projects/${project.project_id}/review`}
                            className="font-medium text-emerald-600 hover:underline"
                          >
                            {project.project_id}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-gray-900">
                          {project.company_name_kr}
                          {project.company_name_en && (
                            <span className="ml-1 text-xs text-gray-400">({project.company_name_en})</span>
                          )}
                        </td>
                        <td className="px-4 py-3"><StatusBadge status={project.status} /></td>
                        <td className="px-4 py-3 text-center text-gray-700">{project.current_step}/14</td>
                        <td className="px-4 py-3 text-gray-600">{project.valuation_purpose ?? '-'}</td>
                        <td className="px-4 py-3 text-gray-600">{formatMethods(project.requested_methods)}</td>
                        <td className="px-4 py-3 text-gray-500">{formatDate(project.updated_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Mobile cards */}
            <div className="space-y-3 sm:hidden">
              {projects.map(project => (
                <Link
                  key={project.project_id}
                  href={`/projects/${project.project_id}/review`}
                  className="block rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-semibold text-emerald-600">{project.project_id}</span>
                    <StatusBadge status={project.status} />
                  </div>
                  <p className="font-medium text-gray-900">{project.company_name_kr}</p>
                  <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                    <span>단계 {project.current_step}/14</span>
                    <span>{formatDate(project.updated_at)}</span>
                  </div>
                  {project.valuation_purpose && (
                    <p className="mt-1 text-xs text-gray-400">목적: {project.valuation_purpose}</p>
                  )}
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <nav className="mt-6 flex items-center justify-center gap-1" aria-label="페이지 네비게이션">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="이전 페이지"
                >
                  이전
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                      page === currentPage ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'
                    }`}
                    aria-current={page === currentPage ? 'page' : undefined}
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
