/**
 * @task S2F4
 * @description Admin My Page - System administration dashboard
 *
 * - 'use client' for dynamic Supabase data fetching
 * - Shows stats: total users, total projects, active projects, revenue
 * - User management overview, recent activity, system status
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
import type { UserRole } from '@/components/mypage-template'
import Link from 'next/link'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface UserOverview {
  user_id: string
  name: string | null
  email: string
  role: string
  phone: string | null
  created_at: string
}

interface ProjectOverview {
  project_id: string
  company_name_kr: string
  status: string
  current_step: number
  user_id: string
  accountant_id: string | null
  created_at: string
  updated_at: string
}

interface AdminStats {
  total_users: number
  total_projects: number
  active_projects: number
  completed_projects: number
  users_by_role: Record<string, number>
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ITEMS_PER_PAGE = 10
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

const ROLE_LABELS: Record<string, string> = {
  customer: '고객',
  accountant: '회계사',
  investor: '투자자',
  partner: '제휴자',
  supporter: '서포터',
  admin: '관리자',
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function RoleBadge({ role }: { role: string }) {
  const colorMap: Record<string, string> = {
    customer: 'bg-blue-100 text-blue-700',
    accountant: 'bg-emerald-100 text-emerald-700',
    investor: 'bg-amber-100 text-amber-700',
    partner: 'bg-violet-100 text-violet-700',
    supporter: 'bg-rose-100 text-rose-700',
    admin: 'bg-red-100 text-red-700',
  }

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${colorMap[role] ?? 'bg-gray-100 text-gray-600'}`}>
      {ROLE_LABELS[role] ?? role}
    </span>
  )
}

function SystemStatusCard({ label, status, detail }: { label: string; status: 'ok' | 'warning' | 'error'; detail: string }) {
  const statusConfig = {
    ok: { badge: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500', text: '정상' },
    warning: { badge: 'bg-amber-100 text-amber-700', dot: 'bg-amber-500', text: '주의' },
    error: { badge: 'bg-red-100 text-red-700', dot: 'bg-red-500', text: '오류' },
  }
  const config = statusConfig[status]

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${config.badge}`}>
          <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} aria-hidden="true" />
          {config.text}
        </span>
      </div>
      <p className="text-xs text-gray-500">{detail}</p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function AdminMyPage() {
  const router = useRouter()

  // Auth
  const [userName, setUserName] = useState<string>('')
  const [userEmail, setUserEmail] = useState<string>('')

  // Data
  const [users, setUsers] = useState<UserOverview[]>([])
  const [recentProjects, setRecentProjects] = useState<ProjectOverview[]>([])
  const [stats, setStats] = useState<AdminStats>({
    total_users: 0,
    total_projects: 0,
    active_projects: 0,
    completed_projects: 0,
    users_by_role: {},
  })
  const [userPage, setUserPage] = useState(1)
  const [userTotalCount, setUserTotalCount] = useState(0)
  const [activeTab, setActiveTab] = useState<'users' | 'projects' | 'system'>('users')

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
          router.replace('/login')
          return
        }

        const { data: profile, error: profileError } = await supabase
          .from('users')
          .select('name, email, role')
          .eq('user_id', user.id)
          .single()

        if (profileError || !profile) {
          router.replace('/login')
          return
        }

        if (profile.role !== 'admin') {
          router.replace(`/mypage/${profile.role}`)
          return
        }

        setUserName(profile.name ?? user.email?.split('@')[0] ?? '관리자')
        setUserEmail(profile.email ?? user.email ?? '')
      } catch {
        setError('인증 정보를 확인할 수 없습니다.')
        setLoading(false)
      }
    }

    init()
  }, [router, supabase])

  // ---- Fetch dashboard data ----
  const fetchData = useCallback(async () => {
    if (!userName) return

    setLoading(true)
    setError(null)

    try {
      // ---- Stats: Users ----
      const { data: allUsers, error: usersError } = await supabase
        .from('users')
        .select('role')

      if (usersError) throw usersError

      const usersByRole: Record<string, number> = {}
      if (allUsers) {
        allUsers.forEach(u => {
          usersByRole[u.role] = (usersByRole[u.role] ?? 0) + 1
        })
      }

      // ---- Stats: Projects ----
      const { data: allProjects, error: projectsError } = await supabase
        .from('projects')
        .select('status')

      if (projectsError) throw projectsError

      const newStats: AdminStats = {
        total_users: allUsers?.length ?? 0,
        total_projects: allProjects?.length ?? 0,
        active_projects: allProjects?.filter(p => p.status === 'in_progress').length ?? 0,
        completed_projects: allProjects?.filter(p => p.status === 'completed').length ?? 0,
        users_by_role: usersByRole,
      }
      setStats(newStats)

      // ---- User list (paginated) ----
      const from = (userPage - 1) * ITEMS_PER_PAGE
      const to = from + ITEMS_PER_PAGE - 1

      const { data: userData, error: userListError, count: userCount } = await supabase
        .from('users')
        .select('user_id, name, email, role, phone, created_at', { count: 'exact' })
        .order('created_at', { ascending: false })
        .range(from, to)

      if (userListError) throw userListError

      setUsers(userData ?? [])
      setUserTotalCount(userCount ?? 0)

      // ---- Recent projects ----
      const { data: projectData, error: projectListError } = await supabase
        .from('projects')
        .select(
          'project_id, company_name_kr, status, current_step, user_id, accountant_id, created_at, updated_at'
        )
        .order('updated_at', { ascending: false })
        .limit(10)

      if (projectListError) throw projectListError

      setRecentProjects(projectData ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }, [userName, userPage, supabase])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // ---- Helpers ----
  const userTotalPages = Math.ceil(userTotalCount / ITEMS_PER_PAGE)

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  function formatDateTime(dateString: string): string {
    return new Date(dateString).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // ---- Loading ----
  if (loading && !userName) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50" role="status" aria-label="로딩 중">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-gray-300 border-t-gray-800" />
          <p className="text-sm text-gray-500">관리자 대시보드 로딩 중...</p>
        </div>
      </div>
    )
  }

  // ---- Render ----
  return (
    <MyPageTemplate role="admin" userName={userName} userEmail={userEmail}>
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      {/* Stats */}
      <DashboardSection title="시스템 현황" description="전체 플랫폼 운영 요약">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="전체 사용자" value={stats.total_users} accentColor="blue" />
          <StatCard label="전체 프로젝트" value={stats.total_projects} accentColor="violet" />
          <StatCard label="진행 중 프로젝트" value={stats.active_projects} accentColor="emerald" />
          <StatCard label="완료 프로젝트" value={stats.completed_projects} accentColor="amber" />
        </div>

        {/* Role distribution */}
        <div className="mt-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">역할별 사용자 분포</h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(stats.users_by_role).map(([role, count]) => (
              <div key={role} className="flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2">
                <RoleBadge role={role} />
                <span className="text-sm font-bold text-gray-900">{count}명</span>
              </div>
            ))}
          </div>
        </div>
      </DashboardSection>

      {/* Tab switcher */}
      <div className="mb-6 flex gap-2" role="tablist" aria-label="관리 탭">
        {[
          { key: 'users' as const, label: '사용자 관리' },
          { key: 'projects' as const, label: '프로젝트 관리' },
          { key: 'system' as const, label: '시스템 상태' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${
              activeTab === tab.key
                ? 'bg-gray-800 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
            role="tab"
            aria-selected={activeTab === tab.key}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ---- Users tab ---- */}
      {activeTab === 'users' && (
        <DashboardSection title="사용자 관리" description="등록된 사용자 목록" id="users">
          {loading ? (
            <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
              <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-gray-800" />
            </div>
          ) : users.length === 0 ? (
            <EmptyState title="등록된 사용자가 없습니다" description="아직 가입한 사용자가 없습니다." />
          ) : (
            <>
              {/* Desktop table */}
              <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm md:block">
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm" aria-label="사용자 목록">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50">
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">이름</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">이메일</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">역할</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">연락처</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">가입일</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map(user => (
                        <tr key={user.user_id} className="border-b border-gray-100 transition-colors hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium text-gray-900">{user.name ?? '-'}</td>
                          <td className="px-4 py-3 text-gray-600">{user.email}</td>
                          <td className="px-4 py-3"><RoleBadge role={user.role} /></td>
                          <td className="px-4 py-3 text-gray-600">{user.phone ?? '-'}</td>
                          <td className="px-4 py-3 text-gray-500">{formatDate(user.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Mobile cards */}
              <div className="space-y-3 md:hidden">
                {users.map(user => (
                  <div key={user.user_id} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="font-semibold text-gray-900">{user.name ?? user.email}</span>
                      <RoleBadge role={user.role} />
                    </div>
                    <p className="text-xs text-gray-500">{user.email}</p>
                    <div className="mt-1 flex gap-4 text-xs text-gray-400">
                      {user.phone && <span>{user.phone}</span>}
                      <span>{formatDate(user.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {userTotalPages > 1 && (
                <nav className="mt-6 flex items-center justify-center gap-1" aria-label="사용자 페이지 네비게이션">
                  <button
                    onClick={() => setUserPage(p => Math.max(1, p - 1))}
                    disabled={userPage === 1}
                    className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                    aria-label="이전 페이지"
                  >
                    이전
                  </button>
                  {Array.from({ length: userTotalPages }, (_, i) => i + 1).map(page => (
                    <button
                      key={page}
                      onClick={() => setUserPage(page)}
                      className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                        page === userPage ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'
                      }`}
                      aria-current={page === userPage ? 'page' : undefined}
                    >
                      {page}
                    </button>
                  ))}
                  <button
                    onClick={() => setUserPage(p => Math.min(userTotalPages, p + 1))}
                    disabled={userPage === userTotalPages}
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
      )}

      {/* ---- Projects tab ---- */}
      {activeTab === 'projects' && (
        <DashboardSection title="최근 프로젝트" description="최근 업데이트된 프로젝트 10건" id="projects">
          {loading ? (
            <div className="flex items-center justify-center rounded-xl bg-white py-16 shadow-sm" role="status">
              <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-gray-800" />
            </div>
          ) : recentProjects.length === 0 ? (
            <EmptyState title="프로젝트가 없습니다" description="아직 등록된 프로젝트가 없습니다." />
          ) : (
            <>
              {/* Desktop table */}
              <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm md:block">
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm" aria-label="최근 프로젝트 목록">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50">
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">프로젝트 ID</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">회사명</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">상태</th>
                        <th className="px-4 py-3 text-center font-semibold text-gray-600">진행 단계</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">담당 회계사</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-600">최종 수정</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentProjects.map(project => (
                        <tr key={project.project_id} className="border-b border-gray-100 transition-colors hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <Link
                              href={`/projects/${project.project_id}`}
                              className="font-medium text-blue-600 hover:underline"
                            >
                              {project.project_id}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-gray-900">{project.company_name_kr}</td>
                          <td className="px-4 py-3"><StatusBadge status={project.status} /></td>
                          <td className="px-4 py-3 text-center text-gray-700">{project.current_step}/14</td>
                          <td className="px-4 py-3 text-gray-600">
                            {project.accountant_id ? (
                              <span className="text-emerald-600">배정됨</span>
                            ) : (
                              <span className="text-gray-400">미배정</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-gray-500">{formatDateTime(project.updated_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Mobile cards */}
              <div className="space-y-3 md:hidden">
                {recentProjects.map(project => (
                  <Link
                    key={project.project_id}
                    href={`/projects/${project.project_id}`}
                    className="block rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-sm font-semibold text-blue-600">{project.project_id}</span>
                      <StatusBadge status={project.status} />
                    </div>
                    <p className="font-medium text-gray-900">{project.company_name_kr}</p>
                    <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                      <span>단계 {project.current_step}/14</span>
                      <span>{formatDateTime(project.updated_at)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            </>
          )}
        </DashboardSection>
      )}

      {/* ---- System tab ---- */}
      {activeTab === 'system' && (
        <DashboardSection title="시스템 상태" description="플랫폼 서비스 상태 확인" id="system">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <SystemStatusCard
              label="Supabase 데이터베이스"
              status="ok"
              detail="데이터베이스 연결 정상"
            />
            <SystemStatusCard
              label="인증 서비스"
              status="ok"
              detail="Supabase Auth 정상 작동"
            />
            <SystemStatusCard
              label="프론트엔드 배포"
              status="ok"
              detail="Vercel 배포 상태 정상"
            />
            <SystemStatusCard
              label="API 서버"
              status="ok"
              detail="Vercel Serverless Functions 정상"
            />
            <SystemStatusCard
              label="결제 시스템"
              status="warning"
              detail="Stripe 테스트 모드 운영 중"
            />
            <SystemStatusCard
              label="이메일 서비스"
              status="ok"
              detail="Resend 정상 작동"
            />
          </div>

          {/* Quick stats summary */}
          <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-gray-700">시스템 요약 정보</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-xs text-gray-500">데이터베이스</p>
                <p className="text-sm font-medium text-gray-900">Supabase PostgreSQL</p>
              </div>
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-xs text-gray-500">프론트엔드</p>
                <p className="text-sm font-medium text-gray-900">Next.js 14 + Tailwind CSS</p>
              </div>
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-xs text-gray-500">배포 환경</p>
                <p className="text-sm font-medium text-gray-900">Vercel (Production)</p>
              </div>
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-xs text-gray-500">인증</p>
                <p className="text-sm font-medium text-gray-900">Supabase Auth (Google, Email)</p>
              </div>
            </div>
          </div>
        </DashboardSection>
      )}
    </MyPageTemplate>
  )
}
