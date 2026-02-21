/**
 * @task S2F4
 * @description Partner My Page - Referral tracking and settlement dashboard
 *
 * - 'use client' for dynamic Supabase data fetching
 * - Shows stats: referral count, active referrals
 * - Referral history list with status tracking
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

interface Referral {
  id: string
  referred_company_name: string
  referred_email: string | null
  status: string
  commission_amount: number | null
  commission_status: string | null
  referred_at: string
  converted_at: string | null
  notes: string | null
}

interface PartnerStats {
  total_referrals: number
  active_referrals: number
  converted: number
  total_commission: number
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

function ReferralStatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    pending: { label: '대기', cls: 'bg-gray-100 text-gray-600' },
    contacted: { label: '연락 완료', cls: 'bg-blue-100 text-blue-700' },
    in_progress: { label: '진행 중', cls: 'bg-amber-100 text-amber-700' },
    converted: { label: '전환 완료', cls: 'bg-emerald-100 text-emerald-700' },
    cancelled: { label: '취소', cls: 'bg-red-100 text-red-700' },
  }
  const info = map[status] ?? { label: status, cls: 'bg-gray-100 text-gray-600' }

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${info.cls}`}>
      {info.label}
    </span>
  )
}

function CommissionStatusBadge({ status }: { status: string | null }) {
  if (!status) return <span className="text-xs text-gray-400">-</span>
  const map: Record<string, { label: string; cls: string }> = {
    pending: { label: '정산 대기', cls: 'bg-amber-100 text-amber-700' },
    paid: { label: '정산 완료', cls: 'bg-emerald-100 text-emerald-700' },
    cancelled: { label: '취소', cls: 'bg-red-100 text-red-700' },
  }
  const info = map[status] ?? { label: status, cls: 'bg-gray-100 text-gray-600' }

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${info.cls}`}>
      {info.label}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function PartnerMyPage() {
  const router = useRouter()

  // Auth
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const [userId, setUserId] = useState<string>('')

  // Data
  const [referrals, setReferrals] = useState<Referral[]>([])
  const [stats, setStats] = useState<PartnerStats>({
    total_referrals: 0,
    active_referrals: 0,
    converted: 0,
    total_commission: 0,
  })
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)

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

        if (profile.role !== 'partner') {
          router.replace(`/mypage/${profile.role}`)
          return
        }

        setUserName(profile.name ?? user.email?.split('@')[0] ?? '파트너')
        setUserEmail(profile.email ?? user.email ?? '')
        setUserId(user.id)
      } catch {
        setError('인증 정보를 확인할 수 없습니다.')
        setLoading(false)
      }
    }

    init()
  }, [router, supabase])

  // ---- Fetch referrals ----
  const fetchData = useCallback(async () => {
    if (!userId) return

    setLoading(true)
    setError(null)

    try {
      // Stats
      const { data: allReferrals, error: statsError } = await supabase
        .from('partner_referrals')
        .select('status, commission_amount, commission_status')
        .eq('partner_id', userId)

      if (statsError) throw statsError

      const newStats: PartnerStats = {
        total_referrals: 0,
        active_referrals: 0,
        converted: 0,
        total_commission: 0,
      }

      if (allReferrals) {
        newStats.total_referrals = allReferrals.length
        newStats.active_referrals = allReferrals.filter(
          r => r.status === 'contacted' || r.status === 'in_progress'
        ).length
        newStats.converted = allReferrals.filter(r => r.status === 'converted').length
        newStats.total_commission = allReferrals
          .filter(r => r.commission_status === 'paid')
          .reduce((sum, r) => sum + (r.commission_amount ?? 0), 0)
      }
      setStats(newStats)

      // Paginated list
      const from = (currentPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1

      const { data, error: listError, count } = await supabase
        .from('partner_referrals')
        .select(
          'id, referred_company_name, referred_email, status, commission_amount, commission_status, referred_at, converted_at, notes',
          { count: 'exact' }
        )
        .eq('partner_id', userId)
        .order('referred_at', { ascending: false })
        .range(from, to)

      if (listError) throw listError

      setReferrals(data ?? [])
      setTotalCount(count ?? 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }, [userId, currentPage, supabase])

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

  function formatCurrency(amount: number): string {
    return amount.toLocaleString('ko-KR') + '원'
  }

  // ---- Loading ----
  if (loading && !userName) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50" role="status" aria-label="로딩 중">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600" />
          <p className="text-sm text-gray-500">마이페이지 로딩 중...</p>
        </div>
      </div>
    )
  }

  // ---- Render ----
  return (
    <MyPageTemplate role="partner" userName={userName} userEmail={userEmail}>
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      {/* Stats */}
      <DashboardSection title="소개 현황" description="제휴 소개 성과 요약">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="총 소개" value={stats.total_referrals} accentColor="violet" />
          <StatCard label="진행 중" value={stats.active_referrals} accentColor="blue" />
          <StatCard label="전환 완료" value={stats.converted} accentColor="emerald" />
          <StatCard
            label="누적 정산"
            value={formatCurrency(stats.total_commission)}
            accentColor="amber"
          />
        </div>
      </DashboardSection>

      {/* Referral list */}
      <DashboardSection
        title="소개 내역"
        description="고객 소개 및 전환 이력"
        id="referrals"
      >
        {loading ? (
          <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600" />
          </div>
        ) : referrals.length === 0 ? (
          <EmptyState
            title="소개 내역이 없습니다"
            description="고객을 소개하여 수수료를 받아보세요."
          />
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm md:block">
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm" aria-label="소개 내역">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">회사명</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">이메일</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">소개 상태</th>
                      <th className="px-4 py-3 text-right font-semibold text-gray-600">수수료</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">정산 상태</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">소개일</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-600">전환일</th>
                    </tr>
                  </thead>
                  <tbody>
                    {referrals.map(ref => (
                      <tr key={ref.id} className="border-b border-gray-100 transition-colors hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">{ref.referred_company_name}</td>
                        <td className="px-4 py-3 text-gray-600">{ref.referred_email ?? '-'}</td>
                        <td className="px-4 py-3"><ReferralStatusBadge status={ref.status} /></td>
                        <td className="px-4 py-3 text-right font-medium text-gray-900">
                          {ref.commission_amount ? formatCurrency(ref.commission_amount) : '-'}
                        </td>
                        <td className="px-4 py-3"><CommissionStatusBadge status={ref.commission_status} /></td>
                        <td className="px-4 py-3 text-gray-500">{formatDate(ref.referred_at)}</td>
                        <td className="px-4 py-3 text-gray-500">{formatDate(ref.converted_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Mobile cards */}
            <div className="space-y-3 md:hidden">
              {referrals.map(ref => (
                <div
                  key={ref.id}
                  className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-semibold text-gray-900">{ref.referred_company_name}</span>
                    <ReferralStatusBadge status={ref.status} />
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                    <span>소개일: {formatDate(ref.referred_at)}</span>
                    {ref.converted_at && <span>전환일: {formatDate(ref.converted_at)}</span>}
                  </div>
                  {ref.commission_amount && (
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">
                        {formatCurrency(ref.commission_amount)}
                      </span>
                      <CommissionStatusBadge status={ref.commission_status} />
                    </div>
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
