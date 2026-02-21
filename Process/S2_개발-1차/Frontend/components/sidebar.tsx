/**
 * @task S2F7
 * @description Common Sidebar Component - Role-based navigation sidebar
 *
 * Features:
 * - User info section (name, role badge)
 * - Navigation links based on role (customer, accountant, admin, investor)
 * - Active link highlighting via usePathname
 * - Logout button
 * - Collapsible on mobile
 * - Korean language UI, ARIA attributes
 * - Responsive design with Tailwind CSS
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { createBrowserClient } from '@supabase/ssr'
import Link from 'next/link'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

type UserRole = 'customer' | 'accountant' | 'admin' | 'investor'

interface NavItem {
  href: string
  label: string
  icon: string
}

const ROLE_NAV: Record<UserRole, NavItem[]> = {
  customer: [
    {
      href: '/mypage/customer',
      label: '마이페이지',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 0 0 1 1h3m10-11l2 2m-2-2v10a1 1 0 0 1-1 1h-3m-4 0h4',
    },
    {
      href: '/projects/list',
      label: '내 프로젝트',
      icon: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2',
    },
    {
      href: '/projects/create',
      label: '평가 신청',
      icon: 'M12 4v16m8-8H4',
    },
    {
      href: '/service-guide',
      label: '서비스 안내',
      icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z',
    },
  ],
  accountant: [
    {
      href: '/mypage/accountant',
      label: '마이페이지',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 0 0 1 1h3m10-11l2 2m-2-2v10a1 1 0 0 1-1 1h-3m-4 0h4',
    },
    {
      href: '/projects/assigned',
      label: '담당 프로젝트',
      icon: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2m-6 9l2 2 4-4',
    },
    {
      href: '/accountant/dashboard',
      label: '업무 현황',
      icon: 'M9 19v-6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2zm0 0V9a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v10m-6 0a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2m0 0V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2z',
    },
  ],
  admin: [
    {
      href: '/admin',
      label: '대시보드',
      icon: 'M4 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5zm0 8a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-6zm12 0a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1v-6z',
    },
    {
      href: '/admin/users',
      label: '사용자 관리',
      icon: 'M12 4.354a4 4 0 1 1 0 5.292M15 21H3v-1a6 6 0 0 1 12 0v1zm0 0h6v-1a6 6 0 0 0-9-5.197m9 5.197v1',
    },
    {
      href: '/admin/projects',
      label: '프로젝트 관리',
      icon: 'M19 11H5m14 0a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2m14 0V9a2 2 0 0 0-2-2M5 11V9a2 2 0 0 1 2-2m0 0V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2M7 7h10',
    },
  ],
  investor: [
    {
      href: '/mypage/investor',
      label: '마이페이지',
      icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 0 0 1 1h3m10-11l2 2m-2-2v10a1 1 0 0 1-1 1h-3m-4 0h4',
    },
    {
      href: '/investor/review',
      label: '투자 검토',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z',
    },
  ],
}

const ROLE_CONFIG: Record<
  UserRole,
  { label: string; badgeColor: string; accentColor: string }
> = {
  customer: {
    label: '고객',
    badgeColor: 'bg-blue-100 text-blue-700',
    accentColor: 'bg-blue-700',
  },
  accountant: {
    label: '공인회계사',
    badgeColor: 'bg-emerald-100 text-emerald-700',
    accentColor: 'bg-emerald-700',
  },
  admin: {
    label: '관리자',
    badgeColor: 'bg-red-100 text-red-700',
    accentColor: 'bg-red-700',
  },
  investor: {
    label: '투자자',
    badgeColor: 'bg-amber-100 text-amber-700',
    accentColor: 'bg-amber-700',
  },
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function Sidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  const [userName, setUserName] = useState<string>('')
  const [userRole, setUserRole] = useState<UserRole | null>(null)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // ---- Fetch user info ----
  const fetchUserInfo = useCallback(async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) {
        setIsLoading(false)
        return
      }

      const { data: userData } = await supabase
        .from('users')
        .select('name, role')
        .eq('user_id', user.id)
        .single()

      if (userData) {
        setUserName(userData.name ?? user.email?.split('@')[0] ?? '')
        setUserRole(userData.role as UserRole)
      }
    } catch {
      // Not logged in
    } finally {
      setIsLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    fetchUserInfo()
  }, [fetchUserInfo])

  // ---- Close mobile sidebar on route change ----
  useEffect(() => {
    setIsMobileOpen(false)
  }, [pathname])

  // ---- Logout ----
  async function handleLogout() {
    await supabase.auth.signOut()
    router.push('/')
  }

  // ---- Is active ----
  function isActive(href: string): boolean {
    return pathname === href
  }

  // ---- Don't render if not logged in or loading ----
  if (isLoading || !userRole) {
    return null
  }

  const config = ROLE_CONFIG[userRole]
  const navItems = ROLE_NAV[userRole] ?? []

  // ---- Sidebar content ----
  const sidebarContent = (
    <>
      {/* User Info */}
      <div className="p-5 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 ${config.accentColor} text-white rounded-full flex items-center justify-center font-bold text-sm`}
          >
            {userName.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">{userName}</p>
            <span
              className={`inline-block mt-0.5 px-2 py-0.5 text-xs font-medium rounded-full ${config.badgeColor}`}
            >
              {config.label}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 overflow-y-auto" aria-label="사이드바 내비게이션">
        <ul className="space-y-1" role="list">
          {navItems.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.href)
                    ? `${config.accentColor} text-white`
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
                aria-current={isActive(item.href) ? 'page' : undefined}
              >
                <svg
                  className="w-5 h-5 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                </svg>
                {!isCollapsed && <span>{item.label}</span>}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors"
          aria-label="로그아웃"
        >
          <svg
            className="w-5 h-5 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3h4a3 3 0 0 1 3 3v1"
            />
          </svg>
          {!isCollapsed && <span>로그아웃</span>}
        </button>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed bottom-6 left-6 z-40 w-12 h-12 bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-800 transition-colors"
        aria-label="사이드바 열기"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/50"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`lg:hidden fixed top-0 left-0 z-50 w-72 h-full bg-white shadow-xl flex flex-col transform transition-transform duration-300 ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        role="complementary"
        aria-label="사이드바"
      >
        {/* Close button */}
        <div className="flex justify-end p-3">
          <button
            onClick={() => setIsMobileOpen(false)}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="사이드바 닫기"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        {sidebarContent}
      </aside>

      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:flex flex-col h-screen bg-white border-r border-gray-200 sticky top-0 transition-all duration-300 ${
          isCollapsed ? 'w-16' : 'w-64'
        }`}
        role="complementary"
        aria-label="사이드바"
      >
        {/* Collapse Toggle */}
        <div className="flex justify-end p-2">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label={isCollapsed ? '사이드바 펼치기' : '사이드바 접기'}
          >
            <svg
              className={`w-4 h-4 transition-transform ${isCollapsed ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
        </div>
        {sidebarContent}
      </aside>
    </>
  )
}
