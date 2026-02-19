/**
 * @task S2F4
 * @description Supporter My Page - Support case tracking and resolution dashboard
 *
 * - 'use client' for dynamic Supabase data fetching
 * - Shows stats: support cases, resolved count
 * - Support history list with priority and status
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
} from '@/components/mypage-template'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SupportCase {
  id: string
  title: string
  description: string | null
  category: string | null
  priority: string
  status: string
  requester_name: string | null
  requester_email: string | null
  assigned_at: string
  resolved_at: string | null
  resolution_note: string | null
}

interface SupporterStats {
  total_cases: number
  open_cases: number
  resolved: number
  avg_resolution_hours: number | null
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ITEMS_PER_PAGE = 10
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function CaseStatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    open: { label: '접수', cls: 'bg-blue-100 text-blue-700' },
    in_progress: { label: '처리 중', cls: 'bg-amber-100 text-amber-700' },
    waiting: { label: '대기', cls: 'bg-gray-100 text-gray-600' },
    resolved: { label: '해결', cls: 'bg-emerald-100 text-emerald-700' },
    closed: { label: '종료', cls: 'bg-gray-100 text-gray-500' },
  }
  const info = map[status] ?? { label: status, cls: 'bg-gray-100 text-gray-600' }

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${info.cls}`}>
      {info.label}
    </span>
  )
}

function PriorityBadge({ priority }: { priority: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    low: { label: '낮음', cls: 'text-gray-500' },
    medium: { label: '보통', cls: 'text-blue-600' },
    high: { label: '높음', cls: 'text-amber-600 font-semibold' },
    urgent: { label: '긴급', cls: 'text-red-600 font-bold' },
  }
  const info = map[priority] ?? { label: priority, cls: 'text-gray-500' }

  return <span className={`text-xs ${info.cls}`}>{info.label}</span>
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function SupporterMyPage() {
  const router = useRouter()

  // Auth
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const [userId, setUserId] = useState<string>('')

  // Data
  const [cases, setCases] = useState<SupportCase[]>([])
  const [stats, setStats] = useState<SupporterStats>({
    total_cases: 0,
    open_cases: 0,
    resolved: 0,
    avg_resolution_hours: null,
  })
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

        if (profile.role !== 'supporter') {
          router.replace(`/mypage/${profile.role}`)
          return
        }

        setUserName(profile.name ?? user.email?.split('@')[0] ?? '서포터')
        setUserEmail(profile.email ?? user.email ?? '')
        setUserId(user.id)
      } catch {
        setError('인증 정보를 확인할 수 없습니다.')
        setLoading(false)
      }
    }

    init()
  }, [router, supabase])

  // ---- Fetch cases ----
  const fetchData = useCallback(async () => {
    if (!userId) return

    setLoading(true)
    setError(null)

    try {
      // Stats
      const { data: allCases, error: statsError } = await supabase
        .from('support_cases')
        .select('status, assigned_at, resolved_at')
        .eq('supporter_id', userId)

      if (statsError) throw statsError

      const newStats: SupporterStats = {
        total_cases: 0,
        open_cases: 0,
        resolved: 0,
        avg_resolution_hours: null,
      }

      if (allCases) {
        newStats.total_cases = allCases.length
        newStats.open_cases = allCases.filter(
          c => c.status === 'open' || c.status === 'in_progress' || c.status === 'waiting'
        ).length
        newStats.resolved = allCases.filter(
          c => c.status === 'resolved' || c.status === 'closed'
        ).length

        // Calculate average resolution time
        const resolvedWithTime = allCases.filter(c => c.resolved_at && c.assigned_at)
        if (resolvedWithTime.length > 0) {
          const totalHours = resolvedWithTime.reduce((sum, c) => {
            const diff = new Date(c.resolved_at!).getTime() - new Date(c.assigned_at).getTime()
            return sum + diff / (1000 * 60 * 60)
          }, 0)
          newStats.avg_resolution_hours = Math.round(totalHours / resolvedWithTime.length)
        }
      }
      setStats(newStats)

      // Paginated list
      const from = (currentPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1

      let query = supabase
        .from('support_cases')
        .select(
          'id, title, description, category, priority, status, requester_name, requester_email, assigned_at, resolved_at, resolution_note',
          { count: 'exact' }
        )
        .eq('supporter_id', userId)

      if (statusFilter !== 'all') {
        query = query.eq('status', statusFilter)
      }

      const { data, error: listError, count } = await query
        .order('assigned_at', { ascending: false })
        .range(from, to)

      if (listError) throw listError

      setCases(data ?? [])
      setTotalCount(count ?? 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }, [userId, currentPage, statusFilter, supabase])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // ---- Helpers ----
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE)

  function formatDate(dateString: string | null): string {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // ---- Loading ----
  if (loading && !userName) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50" role="status" aria-label="로딩 중">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-rose-200 border-t-rose-600" />
          <p className="text-sm text-gray-500">마이페이지 로딩 중...</p>
        </div>
      </div>
    )
  }

  // ---- Render ----
  return (
    <MyPageTemplate role="supporter" userName={userName} userEmail={userEmail}>
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      {/* Stats */}
      <DashboardSection title="지원 현황" description="배정된 지원 케이스 요약">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="전체 케이스" value={stats.total_cases} accentColor="rose" />
          <StatCard label="진행 중" value={stats.open_cases} accentColor="amber" />
          <StatCard label="해결 완료" value={stats.resolved} accentColor="emerald" />
          <StatCard
            label="평균 해결 시간"
            value={stats.avg_resolution_hours !== null ? `${stats.avg_resolution_hours}시간` : '-'}
            accentColor="blue"
          />
        </div>
      </DashboardSection>

      {/* Case list */}
      <DashboardSection
        title="지원 내역"
        description="배정된 지원 케이스 목록"
        id="cases"
      >
        {/* Filter tabs */}
        <div className="mb-4 flex flex-wrap gap-2" role="tablist" aria-label="케이스 상태 필터">
          {[
            { value: 'all', label: '전체' },
            { value: 'open', label: '접수' },
            { value: 'in_progress', label: '처리 중' },
            { value: 'resolved', label: '해결' },
            { value: 'closed', label: '종료' },
          ].map(tab => (
            <button
              key={tab.value}
              onClick={() => { setStatusFilter(tab.value); setCurrentPage(1) }}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                statusFilter === tab.value
                  ? 'bg-rose-600 text-white'
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
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-rose-200 border-t-rose-600" />
          </div>
        ) : cases.length === 0 ? (
          <EmptyState
            title="지원 케이스가 없습니다"
            description="현재 배정된 지원 케이스가 없습니다."
          />
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm md:block">
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm" aria-label="지원 케이스 목록">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">제목</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">카테고리</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-600">우선순위</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">상태</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">요청자</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">배정일</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">해결일</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cases.map(c => (
                      <tr key={c.id} className="border-b border-gray-100 transition-colors hover:bg-gray-50">
                        <td className="max-w-[250px] truncate px-4 py-3 font-medium text-gray-900" title={c.title}>
                          {c.title}
                        </td>
                        <td className="px-4 py-3 text-gray-600">{c.category ?? '-'}</td>
                        <td className="px-4 py-3 text-center"><PriorityBadge priority={c.priority} /></td>
                        <td className="px-4 py-3"><CaseStatusBadge status={c.status} /></td>
                        <td className="px-4 py-3 text-gray-600">{c.requester_name ?? c.requester_email ?? '-'}</td>
                        <td className="px-4 py-3 text-gray-500">{formatDate(c.assigned_at)}</td>
                        <td className="px-4 py-3 text-gray-500">{formatDate(c.resolved_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Mobile cards */}
            <div className="space-y-3 md:hidden">
              {cases.map(c => (
                <div
                  key={c.id}
                  className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
                >
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <h3 className="min-w-0 truncate font-semibold text-gray-900">{c.title}</h3>
                    <CaseStatusBadge status={c.status} />
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                    {c.category && <span>{c.category}</span>}
                    <PriorityBadge priority={c.priority} />
                    <span>배정: {formatDate(c.assigned_at)}</span>
                  </div>
                  {c.requester_name && (
                    <p className="mt-1 text-xs text-gray-400">요청자: {c.requester_name}</p>
                  )}
                  {c.resolution_note && (
                    <p className="mt-2 rounded-lg bg-emerald-50 p-2 text-xs text-emerald-700">
                      {c.resolution_note}
                    </p>
                  )}
                </div>
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
