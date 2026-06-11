/**
 * @task S2F7
 * @description Common Header Component - Navigation bar with auth state
 *
 * Features:
 * - Logo "ValueLink" linking to /
 * - Navigation links
 * - Auth buttons: login/register (logged out) or mypage/logout (logged in)
 * - Auth state check via supabase.auth.getUser()
 * - Mobile hamburger menu
 * - Responsive, sticky top
 * - Korean language UI, ARIA attributes
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

interface NavLink {
  href: string
  label: string
}

const NAV_LINKS: NavLink[] = [
  { href: '/service-guide', label: '서비스 안내' },
  { href: '/valuation/guides/dcf', label: '평가 안내' },
]

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function Header() {
  const router = useRouter()
  const pathname = usePathname()
  const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userRole, setUserRole] = useState<string | null>(null)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // ---- Check auth ----
  const checkAuth = useCallback(async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (user) {
        setIsLoggedIn(true)

        const { data: userData } = await supabase
          .from('users')
          .select('role')
          .eq('user_id', user.id)
          .single()

        if (userData) {
          setUserRole(userData.role)
        }
      } else {
        setIsLoggedIn(false)
        setUserRole(null)
      }
    } catch {
      setIsLoggedIn(false)
      setUserRole(null)
    } finally {
      setIsLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  // ---- Listen for auth state changes ----
  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setIsLoggedIn(true)
        // Re-fetch role
        supabase
          .from('users')
          .select('role')
          .eq('user_id', session.user.id)
          .single()
          .then(({ data }) => {
            if (data) setUserRole(data.role)
          })
      } else {
        setIsLoggedIn(false)
        setUserRole(null)
      }
    })

    return () => {
      subscription.unsubscribe()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ---- Close mobile menu on route change ----
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [pathname])

  // ---- Logout ----
  async function handleLogout() {
    await supabase.auth.signOut()
    setIsLoggedIn(false)
    setUserRole(null)
    router.push('/')
  }

  // ---- My Page path by role ----
  function getMyPagePath(): string {
    if (userRole === 'admin') return '/admin'
    if (userRole) return `/mypage/${userRole}`
    return '/mypage/customer'
  }

  // ---- Is active link ----
  function isActive(href: string): boolean {
    return pathname === href || (pathname?.startsWith(href + '/') ?? false)
  }

  // ---- Render ----
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            href="/"
            className="text-xl font-extrabold text-blue-700 tracking-tight hover:text-blue-800 transition-colors"
            aria-label="ValueLink 홈으로 이동"
          >
            ValueLink
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8" aria-label="주요 내비게이션">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`text-sm font-medium transition-colors ${
                  isActive(link.href)
                    ? 'text-blue-700 font-semibold'
                    : 'text-gray-600 hover:text-blue-700'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center gap-3">
            {isLoading ? (
              <div className="w-20 h-9 bg-gray-100 rounded-lg animate-pulse" />
            ) : isLoggedIn ? (
              <>
                <Link
                  href={getMyPagePath()}
                  className="px-4 py-2 text-sm font-semibold text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  마이페이지
                </Link>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-700 transition-colors"
                >
                  로그인
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 text-sm font-semibold text-white bg-blue-700 rounded-lg hover:bg-blue-800 transition-colors"
                >
                  회원가입
                </Link>
              </>
            )}
          </div>

          {/* Mobile Hamburger */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label={isMobileMenuOpen ? '메뉴 닫기' : '메뉴 열기'}
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-100 py-4" role="navigation" aria-label="모바일 내비게이션">
            <div className="space-y-1">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    isActive(link.href)
                      ? 'text-blue-700 bg-blue-50 font-semibold'
                      : 'text-gray-600 hover:text-blue-700 hover:bg-gray-50'
                  }`}
                >
                  {link.label}
                </Link>
              ))}

              <div className="pt-3 mt-3 border-t border-gray-100">
                {isLoading ? (
                  <div className="px-4 py-3">
                    <div className="w-full h-10 bg-gray-100 rounded-lg animate-pulse" />
                  </div>
                ) : isLoggedIn ? (
                  <>
                    <Link
                      href={getMyPagePath()}
                      className="block px-4 py-3 rounded-lg text-sm font-semibold text-blue-700 hover:bg-blue-50 transition-colors"
                    >
                      마이페이지
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors"
                    >
                      로그아웃
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="block px-4 py-3 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      로그인
                    </Link>
                    <Link
                      href="/register"
                      className="block mx-4 mt-2 px-4 py-3 text-center text-sm font-semibold text-white bg-blue-700 rounded-lg hover:bg-blue-800 transition-colors"
                    >
                      회원가입
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
