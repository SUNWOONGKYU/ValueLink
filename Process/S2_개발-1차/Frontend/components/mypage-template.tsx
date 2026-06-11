/**
 * @task S2F4
 * @description Role-Based My Page Template - Shared layout for all 6 role mypage pages
 *
 * - React Server Component (NO 'use client')
 * - Receives role, userName, userEmail, children props
 * - Role-specific color scheme and navigation
 * - Responsive layout with mobile hamburger support
 * - ARIA labels and semantic HTML
 * - Korean language UI
 */

import Link from 'next/link'

// ---------------------------------------------------------------------------
// Type Definitions
// ---------------------------------------------------------------------------

export type UserRole =
  | 'customer'
  | 'accountant'
  | 'investor'
  | 'partner'
  | 'supporter'
  | 'admin'

export interface MyPageTemplateProps {
  role: UserRole
  userName: string
  userEmail: string
  children: React.ReactNode
}

export interface DashboardStat {
  label: string
  value: number | string
  icon: string
  color: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ROLE_CONFIG: Record<
  UserRole,
  {
    label: string
    badgeClass: string
    accentClass: string
    accentBg: string
    headerGradient: string
  }
> = {
  customer: {
    label: '고객',
    badgeClass: 'bg-blue-100 text-blue-700',
    accentClass: 'text-blue-700',
    accentBg: 'bg-blue-600',
    headerGradient: 'from-blue-600 to-blue-800',
  },
  accountant: {
    label: '공인회계사',
    badgeClass: 'bg-emerald-100 text-emerald-700',
    accentClass: 'text-emerald-700',
    accentBg: 'bg-emerald-600',
    headerGradient: 'from-emerald-600 to-emerald-800',
  },
  investor: {
    label: '투자자',
    badgeClass: 'bg-amber-100 text-amber-700',
    accentClass: 'text-amber-700',
    accentBg: 'bg-amber-600',
    headerGradient: 'from-amber-600 to-amber-800',
  },
  partner: {
    label: '제휴자',
    badgeClass: 'bg-violet-100 text-violet-700',
    accentClass: 'text-violet-700',
    accentBg: 'bg-violet-600',
    headerGradient: 'from-violet-600 to-violet-800',
  },
  supporter: {
    label: '서포터',
    badgeClass: 'bg-rose-100 text-rose-700',
    accentClass: 'text-rose-700',
    accentBg: 'bg-rose-600',
    headerGradient: 'from-rose-600 to-rose-800',
  },
  admin: {
    label: '관리자',
    badgeClass: 'bg-red-100 text-red-700',
    accentClass: 'text-red-700',
    accentBg: 'bg-red-600',
    headerGradient: 'from-gray-800 to-gray-950',
  },
}

interface NavItem {
  label: string
  href: string
  icon: string
}

const COMMON_NAV: NavItem[] = [
  { label: '홈', href: '/', icon: 'home' },
]

const ROLE_NAV: Record<UserRole, NavItem[]> = {
  customer: [
    { label: '대시보드', href: '/mypage/customer', icon: 'dashboard' },
    { label: '프로젝트 목록', href: '/projects/list', icon: 'folder' },
    { label: '새 프로젝트', href: '/projects/create', icon: 'add' },
  ],
  accountant: [
    { label: '대시보드', href: '/mypage/accountant', icon: 'dashboard' },
    { label: '배정 프로젝트', href: '/mypage/accountant#projects', icon: 'assignment' },
    { label: '검토 대기', href: '/mypage/accountant#pending', icon: 'pending' },
  ],
  investor: [
    { label: '대시보드', href: '/mypage/investor', icon: 'dashboard' },
    { label: '투자 뉴스', href: '/mypage/investor#news', icon: 'news' },
    { label: '관심 기업', href: '/mypage/investor#watchlist', icon: 'star' },
  ],
  partner: [
    { label: '대시보드', href: '/mypage/partner', icon: 'dashboard' },
    { label: '소개 현황', href: '/mypage/partner#referrals', icon: 'people' },
    { label: '정산 내역', href: '/mypage/partner#settlements', icon: 'payment' },
  ],
  supporter: [
    { label: '대시보드', href: '/mypage/supporter', icon: 'dashboard' },
    { label: '지원 내역', href: '/mypage/supporter#cases', icon: 'support' },
    { label: '해결 현황', href: '/mypage/supporter#resolved', icon: 'check' },
  ],
  admin: [
    { label: '대시보드', href: '/mypage/admin', icon: 'dashboard' },
    { label: '사용자 관리', href: '/mypage/admin#users', icon: 'people' },
    { label: '프로젝트 관리', href: '/mypage/admin#projects', icon: 'folder' },
    { label: '시스템 현황', href: '/mypage/admin#system', icon: 'settings' },
  ],
}

// ---------------------------------------------------------------------------
// Icon Component (inline SVG for zero-dependency icons)
// ---------------------------------------------------------------------------

function NavIcon({ name, className }: { name: string; className?: string }) {
  const cls = className ?? 'h-5 w-5'

  const icons: Record<string, React.ReactNode> = {
    home: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    ),
    dashboard: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
      </svg>
    ),
    folder: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
      </svg>
    ),
    add: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
      </svg>
    ),
    chart: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
      </svg>
    ),
    assignment: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
      </svg>
    ),
    pending: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    news: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25H5.625a2.25 2.25 0 01-2.25-2.25V7.875c0-.621.504-1.125 1.125-1.125H8.25m3.75-3v3" />
      </svg>
    ),
    star: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
      </svg>
    ),
    people: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
      </svg>
    ),
    payment: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" />
      </svg>
    ),
    support: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.712 4.33a9.027 9.027 0 011.652 1.306c.51.51.944 1.064 1.306 1.652M16.712 4.33l-3.448 4.138m3.448-4.138a9.014 9.014 0 00-9.424 0M19.67 7.288l-4.138 3.448m4.138-3.448a9.014 9.014 0 010 9.424m-4.138-5.976a3.736 3.736 0 00-.88-1.388 3.737 3.737 0 00-1.388-.88m2.268 2.268a3.765 3.765 0 010 2.528m-2.268-4.796a3.765 3.765 0 00-2.528 0m4.796 4.796c-.181.506-.475.982-.88 1.388a3.736 3.736 0 01-1.388.88m2.268-2.268l4.138 3.448m0 0a9.027 9.027 0 01-1.306 1.652c-.51.51-1.064.944-1.652 1.306m0 0l-3.448-4.138m3.448 4.138a9.014 9.014 0 01-9.424 0m5.976-4.138a3.765 3.765 0 01-2.528 0m0 0a3.736 3.736 0 01-1.388-.88 3.737 3.737 0 01-.88-1.388m0 0l-4.138 3.448M7.288 19.67a9.014 9.014 0 010-9.424m4.796 5.976l-4.138-3.448m0-2.528l4.138-3.448m-4.138 3.448a9.014 9.014 0 000 2.528" />
      </svg>
    ),
    check: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    settings: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    logout: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
      </svg>
    ),
    menu: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
      </svg>
    ),
    close: (
      <svg className={cls} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    ),
  }

  return <>{icons[name] ?? icons.dashboard}</>
}

// ---------------------------------------------------------------------------
// Template Component (Server Component)
// ---------------------------------------------------------------------------

export default function MyPageTemplate({
  role,
  userName,
  userEmail,
  children,
}: MyPageTemplateProps) {
  const config = ROLE_CONFIG[role]
  const navItems = [...COMMON_NAV, ...ROLE_NAV[role]]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ================================================================= */}
      {/* Header                                                            */}
      {/* ================================================================= */}
      <header
        className={`bg-gradient-to-r ${config.headerGradient} text-white shadow-lg`}
        role="banner"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4 sm:py-6">
            {/* Left: User info */}
            <div className="flex items-center gap-4 min-w-0">
              {/* Avatar */}
              <div
                className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-white/20 text-lg font-bold sm:h-12 sm:w-12"
                aria-hidden="true"
              >
                {userName.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="truncate text-lg font-bold sm:text-xl">
                    {userName}
                  </h1>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${config.badgeClass}`}
                    role="status"
                    aria-label={`역할: ${config.label}`}
                  >
                    {config.label}
                  </span>
                </div>
                <p className="truncate text-sm text-white/70">{userEmail}</p>
              </div>
            </div>

            {/* Right: Mobile menu toggle (handled client-side via CSS checkbox hack) */}
            <div className="flex items-center gap-3">
              {/* Desktop logout button — 파괴적 액션이므로 POST 폼 사용
                  (<Link>는 뷰포트 진입 시 프리페치 GET을 보내 자동 로그아웃을 유발함) */}
              <form action="/api/auth/logout" method="post" className="contents">
                <button
                  type="submit"
                  className="hidden items-center gap-1.5 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white/90 transition-colors hover:bg-white/20 sm:flex"
                  aria-label="로그아웃"
                >
                  <NavIcon name="logout" className="h-4 w-4" />
                  <span>로그아웃</span>
                </button>
              </form>

              {/* Mobile hamburger: uses CSS :target for no-JS toggle */}
              <a
                href="#mobile-nav"
                className="flex items-center justify-center rounded-lg bg-white/10 p-2 transition-colors hover:bg-white/20 sm:hidden"
                aria-label="메뉴 열기"
              >
                <NavIcon name="menu" className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* ================================================================= */}
      {/* Mobile Navigation Overlay (CSS :target based)                     */}
      {/* ================================================================= */}
      <div
        id="mobile-nav"
        className="fixed inset-0 z-50 hidden bg-black/50 backdrop-blur-sm target:flex sm:!hidden"
        aria-label="모바일 네비게이션"
        role="dialog"
        aria-modal="true"
      >
        <nav className="ml-auto h-full w-72 overflow-y-auto bg-white p-6 shadow-xl">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900">메뉴</h2>
            <a
              href="#"
              className="rounded-lg p-1.5 text-gray-500 transition-colors hover:bg-gray-100"
              aria-label="메뉴 닫기"
            >
              <NavIcon name="close" className="h-6 w-6" />
            </a>
          </div>

          {/* User card */}
          <div className="mb-6 rounded-xl bg-gray-50 p-4">
            <p className="font-semibold text-gray-900">{userName}</p>
            <p className="text-sm text-gray-500">{userEmail}</p>
            <span
              className={`mt-2 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${config.badgeClass}`}
            >
              {config.label}
            </span>
          </div>

          {/* Nav links */}
          <ul className="space-y-1" role="list">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
                >
                  <NavIcon name={item.icon} className="h-5 w-5 text-gray-400" />
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          {/* Logout — 파괴적 액션이므로 POST 폼 사용 (프리페치 GET 방지) */}
          <div className="mt-6 border-t border-gray-200 pt-6">
            <form action="/api/auth/logout" method="post">
              <button
                type="submit"
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
              >
                <NavIcon name="logout" className="h-5 w-5" />
                로그아웃
              </button>
            </form>
          </div>
        </nav>
      </div>

      {/* ================================================================= */}
      {/* Body: Sidebar + Main                                              */}
      {/* ================================================================= */}
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:gap-8">
          {/* ---- Desktop sidebar ---- */}
          <aside
            className="hidden w-64 flex-shrink-0 lg:block"
            aria-label="사이드바 네비게이션"
          >
            <div className="sticky top-8">
              <nav aria-label="마이페이지 메뉴">
                <ul className="space-y-1" role="list">
                  {navItems.map((item) => (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-white hover:shadow-sm"
                      >
                        <NavIcon
                          name={item.icon}
                          className="h-5 w-5 text-gray-400"
                        />
                        {item.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </nav>

              {/* Logout — 파괴적 액션이므로 POST 폼 사용 (프리페치 GET 방지) */}
              <div className="mt-6 border-t border-gray-200 pt-6">
                <form action="/api/auth/logout" method="post">
                  <button
                    type="submit"
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                  >
                    <NavIcon name="logout" className="h-5 w-5" />
                    로그아웃
                  </button>
                </form>
              </div>
            </div>
          </aside>

          {/* ---- Mobile tab nav (horizontal scroll) ---- */}
          <nav
            className="lg:hidden"
            aria-label="마이페이지 메뉴 (모바일)"
          >
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {ROLE_NAV[role].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex flex-shrink-0 items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50"
                >
                  <NavIcon name={item.icon} className="h-4 w-4 text-gray-400" />
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>

          {/* ---- Main content ---- */}
          <main className="min-w-0 flex-1" role="main" aria-label="마이페이지 콘텐츠">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Exported Sub-components (reusable across role pages)
// ---------------------------------------------------------------------------

/** Stats card for dashboard overview */
export function StatCard({
  label,
  value,
  description,
  accentColor = 'blue',
}: {
  label: string
  value: number | string
  description?: string
  accentColor?: string
}) {
  const colorMap: Record<string, string> = {
    blue: 'border-l-blue-500 bg-blue-50/50',
    emerald: 'border-l-emerald-500 bg-emerald-50/50',
    amber: 'border-l-amber-500 bg-amber-50/50',
    violet: 'border-l-violet-500 bg-violet-50/50',
    rose: 'border-l-rose-500 bg-rose-50/50',
    red: 'border-l-red-500 bg-red-50/50',
    gray: 'border-l-gray-500 bg-gray-50/50',
  }

  return (
    <div
      className={`rounded-xl border border-gray-200 border-l-4 bg-white p-5 shadow-sm ${colorMap[accentColor] ?? colorMap.blue}`}
    >
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900">
        {typeof value === 'number' ? value.toLocaleString('ko-KR') : value}
      </p>
      {description && (
        <p className="mt-1 text-xs text-gray-400">{description}</p>
      )}
    </div>
  )
}

/** Empty state placeholder */
export function EmptyState({
  title,
  description,
  actionLabel,
  actionHref,
}: {
  title: string
  description: string
  actionLabel?: string
  actionHref?: string
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 bg-white px-6 py-16 text-center">
      <svg
        className="mb-4 h-12 w-12 text-gray-300"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1}
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
        />
      </svg>
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
      {actionLabel && actionHref && (
        <Link
          href={actionHref}
          className="mt-6 inline-flex items-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          {actionLabel}
        </Link>
      )}
    </div>
  )
}

/** Section wrapper with title */
export function DashboardSection({
  title,
  description,
  children,
  id,
}: {
  title: string
  description?: string
  children: React.ReactNode
  id?: string
}) {
  return (
    <section id={id} className="mb-8" aria-label={title}>
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        {description && (
          <p className="mt-1 text-sm text-gray-500">{description}</p>
        )}
      </div>
      {children}
    </section>
  )
}

/** Status badge for project/task status */
export function StatusBadge({ status }: { status: string }) {
  const statusMap: Record<string, { label: string; cls: string }> = {
    in_progress: { label: '진행 중', cls: 'bg-blue-100 text-blue-700' },
    human_approval: { label: '승인 대기', cls: 'bg-amber-100 text-amber-700' },
    draft_generated: { label: '초안 생성', cls: 'bg-violet-100 text-violet-700' },
    completed: { label: '완료', cls: 'bg-emerald-100 text-emerald-700' },
    archived: { label: '보관', cls: 'bg-gray-100 text-gray-600' },
  }

  const info = statusMap[status] ?? { label: status, cls: 'bg-gray-100 text-gray-600' }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${info.cls}`}
    >
      {info.label}
    </span>
  )
}

/** Pagination controls */
export function Pagination({
  currentPage,
  totalPages,
  baseUrl,
}: {
  currentPage: number
  totalPages: number
  baseUrl: string
}) {
  if (totalPages <= 1) return null

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1)

  return (
    <nav
      className="mt-6 flex items-center justify-center gap-1"
      aria-label="페이지 네비게이션"
    >
      {currentPage > 1 && (
        <Link
          href={`${baseUrl}?page=${currentPage - 1}`}
          className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100"
          aria-label="이전 페이지"
        >
          이전
        </Link>
      )}
      {pages.map((page) => (
        <Link
          key={page}
          href={`${baseUrl}?page=${page}`}
          className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
            page === currentPage
              ? 'bg-gray-900 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
          aria-current={page === currentPage ? 'page' : undefined}
          aria-label={`${page} 페이지`}
        >
          {page}
        </Link>
      ))}
      {currentPage < totalPages && (
        <Link
          href={`${baseUrl}?page=${currentPage + 1}`}
          className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100"
          aria-label="다음 페이지"
        >
          다음
        </Link>
      )}
    </nav>
  )
}
