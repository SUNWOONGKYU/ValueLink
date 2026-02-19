/**
 * @task S2F4
 * @description Investor My Page - Investment news and watchlist dashboard
 *
 * - 'use client' for dynamic Supabase data fetching
 * - Shows stats: deal news count, watched companies
 * - Investment news list and watched company list
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
import Link from 'next/link'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DealNews {
  id: string
  company_name: string
  industry: string | null
  investment_stage: string | null
  investor_names: string | null
  investment_amount: string | null
  region: string | null
  published_at: string | null
  source_url: string | null
  created_at: string
}

interface WatchedCompany {
  id: string
  company_name: string
  industry: string | null
  last_deal_date: string | null
  total_funding: string | null
  notes: string | null
}

interface InvestorStats {
  news_count: number
  watched_count: number
  recent_deals_this_month: number
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

export default function InvestorMyPage() {
  const router = useRouter()

  // Auth
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')
  const [userId, setUserId] = useState<string>('')

  // Data
  const [dealNews, setDealNews] = useState<DealNews[]>([])
  const [watchedCompanies, setWatchedCompanies] = useState<WatchedCompany[]>([])
  const [stats, setStats] = useState<InvestorStats>({
    news_count: 0,
    watched_count: 0,
    recent_deals_this_month: 0,
  })
  const [newsPage, setNewsPage] = useState(1)
  const [newsTotalCount, setNewsTotalCount] = useState(0)
  const [activeTab, setActiveTab] = useState<'news' | 'watchlist'>('news')

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

        if (profile.role !== 'investor') {
          router.replace(`/mypage/${profile.role}`)
          return
        }

        setUserName(profile.name ?? user.email?.split('@')[0] ?? '투자자')
        setUserEmail(profile.email ?? user.email ?? '')
        setUserId(user.id)
      } catch {
        setError('인증 정보를 확인할 수 없습니다.')
        setLoading(false)
      }
    }

    init()
  }, [router, supabase])

  // ---- Fetch data ----
  const fetchData = useCallback(async () => {
    if (!userId) return

    setLoading(true)
    setError(null)

    try {
      // Fetch stats - deal_news count
      const { count: newsCount, error: newsCountError } = await supabase
        .from('deal_news')
        .select('id', { count: 'exact', head: true })

      if (newsCountError) throw newsCountError

      // Fetch stats - watched companies count
      const { count: watchCount, error: watchCountError } = await supabase
        .from('investor_watchlist')
        .select('id', { count: 'exact', head: true })
        .eq('user_id', userId)

      if (watchCountError) throw watchCountError

      // Recent deals this month
      const now = new Date()
      const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString()

      const { count: recentCount } = await supabase
        .from('deal_news')
        .select('id', { count: 'exact', head: true })
        .gte('published_at', firstDayOfMonth)

      setStats({
        news_count: newsCount ?? 0,
        watched_count: watchCount ?? 0,
        recent_deals_this_month: recentCount ?? 0,
      })

      // Fetch news list (paginated)
      const from = (newsPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1

      const { data: newsData, error: newsError, count: newsTotal } = await supabase
        .from('deal_news')
        .select(
          'id, company_name, industry, investment_stage, investor_names, investment_amount, region, published_at, source_url, created_at',
          { count: 'exact' }
        )
        .order('published_at', { ascending: false })
        .range(from, to)

      if (newsError) throw newsError

      setDealNews(newsData ?? [])
      setNewsTotalCount(newsTotal ?? 0)

      // Fetch watched companies
      const { data: watchData, error: watchError } = await supabase
        .from('investor_watchlist')
        .select('id, company_name, industry, last_deal_date, total_funding, notes')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

      if (watchError) throw watchError

      setWatchedCompanies(watchData ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }, [userId, newsPage, supabase])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // ---- Helpers ----
  const newsTotalPages = Math.ceil(newsTotalCount / ITEMS_PER_PAGE)

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
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-amber-200 border-t-amber-600" />
          <p className="text-sm text-gray-500">마이페이지 로딩 중...</p>
        </div>
      </div>
    )
  }

  // ---- Render ----
  return (
    <MyPageTemplate role="investor" userName={userName} userEmail={userEmail}>
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      {/* Stats */}
      <DashboardSection title="투자 현황" description="투자 뉴스 및 관심 기업 현황">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard label="투자 뉴스" value={stats.news_count} description="전체 딜 뉴스" accentColor="amber" />
          <StatCard label="관심 기업" value={stats.watched_count} description="워치리스트 등록" accentColor="violet" />
          <StatCard label="이번 달 신규 딜" value={stats.recent_deals_this_month} description="최근 30일" accentColor="emerald" />
        </div>
      </DashboardSection>

      {/* Tab switcher */}
      <div className="mb-6 flex gap-2" role="tablist" aria-label="콘텐츠 탭">
        <button
          onClick={() => setActiveTab('news')}
          className={`rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${
            activeTab === 'news'
              ? 'bg-amber-600 text-white'
              : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
          }`}
          role="tab"
          aria-selected={activeTab === 'news'}
          aria-controls="news-panel"
        >
          투자 뉴스
        </button>
        <button
          onClick={() => setActiveTab('watchlist')}
          className={`rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${
            activeTab === 'watchlist'
              ? 'bg-amber-600 text-white'
              : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
          }`}
          role="tab"
          aria-selected={activeTab === 'watchlist'}
          aria-controls="watchlist-panel"
        >
          관심 기업
        </button>
      </div>

      {/* News panel */}
      {activeTab === 'news' && (
        <DashboardSection title="최근 투자 뉴스" description="스타트업 투자 딜 소식" id="news">
          <div id="news-panel" role="tabpanel" aria-labelledby="투자 뉴스">
            {loading ? (
              <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
                <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-amber-200 border-t-amber-600" />
              </div>
            ) : dealNews.length === 0 ? (
              <EmptyState
                title="투자 뉴스가 없습니다"
                description="아직 등록된 투자 뉴스가 없습니다."
              />
            ) : (
              <>
                {/* Desktop table */}
                <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm md:block">
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm" aria-label="투자 뉴스 목록">
                      <thead>
                        <tr className="border-b border-gray-200 bg-gray-50">
                          <th className="px-4 py-3 text-left font-semibold text-gray-600">기업명</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-600">업종</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-600">투자단계</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-600">투자자</th>
                          <th className="px-4 py-3 text-right font-semibold text-gray-600">투자금액</th>
                          <th className="px-4 py-3 text-left font-semibold text-gray-600">날짜</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dealNews.map(news => (
                          <tr key={news.id} className="border-b border-gray-100 transition-colors hover:bg-gray-50">
                            <td className="px-4 py-3">
                              {news.source_url ? (
                                <a
                                  href={news.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="font-medium text-amber-700 hover:underline"
                                >
                                  {news.company_name}
                                </a>
                              ) : (
                                <span className="font-medium text-gray-900">{news.company_name}</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-gray-600">{news.industry ?? '-'}</td>
                            <td className="px-4 py-3">
                              {news.investment_stage ? (
                                <span className="inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                                  {news.investment_stage}
                                </span>
                              ) : (
                                '-'
                              )}
                            </td>
                            <td className="max-w-[200px] truncate px-4 py-3 text-gray-600" title={news.investor_names ?? ''}>
                              {news.investor_names ?? '-'}
                            </td>
                            <td className="px-4 py-3 text-right font-medium text-gray-900">
                              {news.investment_amount ?? '-'}
                            </td>
                            <td className="px-4 py-3 text-gray-500">{formatDate(news.published_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Mobile cards */}
                <div className="space-y-3 md:hidden">
                  {dealNews.map(news => (
                    <div
                      key={news.id}
                      className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
                    >
                      <div className="mb-2 flex items-center justify-between">
                        {news.source_url ? (
                          <a
                            href={news.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-semibold text-amber-700 hover:underline"
                          >
                            {news.company_name}
                          </a>
                        ) : (
                          <span className="font-semibold text-gray-900">{news.company_name}</span>
                        )}
                        {news.investment_stage && (
                          <span className="inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                            {news.investment_stage}
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                        {news.industry && <span>{news.industry}</span>}
                        {news.investment_amount && (
                          <span className="font-medium text-gray-900">{news.investment_amount}</span>
                        )}
                        <span>{formatDate(news.published_at)}</span>
                      </div>
                      {news.investor_names && (
                        <p className="mt-1 truncate text-xs text-gray-400">{news.investor_names}</p>
                      )}
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {newsTotalPages > 1 && (
                  <nav className="mt-6 flex items-center justify-center gap-1" aria-label="뉴스 페이지 네비게이션">
                    <button
                      onClick={() => setNewsPage(p => Math.max(1, p - 1))}
                      disabled={newsPage === 1}
                      className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                      aria-label="이전 페이지"
                    >
                      이전
                    </button>
                    {Array.from({ length: newsTotalPages }, (_, i) => i + 1).map(page => (
                      <button
                        key={page}
                        onClick={() => setNewsPage(page)}
                        className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                          page === newsPage ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'
                        }`}
                        aria-current={page === newsPage ? 'page' : undefined}
                      >
                        {page}
                      </button>
                    ))}
                    <button
                      onClick={() => setNewsPage(p => Math.min(newsTotalPages, p + 1))}
                      disabled={newsPage === newsTotalPages}
                      className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                      aria-label="다음 페이지"
                    >
                      다음
                    </button>
                  </nav>
                )}
              </>
            )}
          </div>
        </DashboardSection>
      )}

      {/* Watchlist panel */}
      {activeTab === 'watchlist' && (
        <DashboardSection title="관심 기업" description="관심 등록된 기업 목록" id="watchlist">
          <div id="watchlist-panel" role="tabpanel" aria-labelledby="관심 기업">
            {loading ? (
              <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
                <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-amber-200 border-t-amber-600" />
              </div>
            ) : watchedCompanies.length === 0 ? (
              <EmptyState
                title="관심 기업이 없습니다"
                description="투자 뉴스에서 관심 있는 기업을 추가해보세요."
              />
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {watchedCompanies.map(company => (
                  <div
                    key={company.id}
                    className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
                  >
                    <h3 className="text-lg font-semibold text-gray-900">{company.company_name}</h3>
                    <div className="mt-2 space-y-1 text-sm text-gray-500">
                      {company.industry && <p>업종: {company.industry}</p>}
                      {company.total_funding && <p>누적 투자: {company.total_funding}</p>}
                      {company.last_deal_date && <p>최근 딜: {formatDate(company.last_deal_date)}</p>}
                    </div>
                    {company.notes && (
                      <p className="mt-3 rounded-lg bg-gray-50 p-2 text-xs text-gray-500">{company.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </DashboardSection>
      )}
    </MyPageTemplate>
  )
}
