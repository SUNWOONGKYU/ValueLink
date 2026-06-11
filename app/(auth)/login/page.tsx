/**
 * @task S2F7
 * @description Login Page - Email/password authentication with role-based redirect
 *
 * - 'use client' for Supabase Auth interaction
 * - Email + password form with validation
 * - Supabase signInWithPassword
 * - Fetches user role from users table (user_id)
 * - Checks is_active status
 * - Role-based redirect: customer/accountant -> /mypage/{role}, admin -> /admin
 * - Loading state, error messages, remember me, responsive
 * - Korean language UI, ARIA attributes
 */

'use client'

import { useState, useEffect, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { createBrowserClient } from '@supabase/ssr'
import Link from 'next/link'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function LoginPage() {
  const router = useRouter()
  const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  // ---- State ----
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [emailError, setEmailError] = useState<string | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  // ---- Check if already logged in ----
  useEffect(() => {
    async function checkAuth() {
      try {
        const { data: { user } } = await supabase.auth.getUser()
        if (user) {
          // Fetch role and redirect
          const { data: userData } = await supabase
            .from('users')
            .select('role')
            .eq('user_id', user.id)
            .single()

          if (userData) {
            redirectByRole(userData.role)
            return
          }
        }
      } catch {
        // Not logged in, continue
      }
      setIsCheckingAuth(false)
    }
    checkAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ---- Load remembered email ----
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedEmail = localStorage.getItem('valuelink_remembered_email')
      if (savedEmail) {
        setEmail(savedEmail)
        setRememberMe(true)
      }
    }
  }, [])

  // ---- Role-based redirect ----
  function redirectByRole(role: string) {
    switch (role) {
      case 'customer':
      case 'accountant':
      case 'investor':
      case 'admin':
        router.push(`/mypage/${role}`)
        break
      default:
        router.push('/')
        break
    }
  }

  // ---- Validation ----
  function validateForm(): boolean {
    let isValid = true
    setEmailError(null)
    setPasswordError(null)

    if (!email.trim()) {
      setEmailError('이메일을 입력해주세요')
      isValid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailError('올바른 이메일 형식이 아닙니다')
      isValid = false
    }

    if (!password) {
      setPasswordError('비밀번호를 입력해주세요')
      isValid = false
    }

    return isValid
  }

  // ---- Submit ----
  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)

    if (!validateForm()) return

    setIsLoading(true)

    try {
      // 1. Supabase Auth sign in
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      })

      if (authError) throw authError

      // 2. Fetch user role and is_active from users table
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('role, is_active, name')
        .eq('user_id', data.user.id)
        .single()

      if (userError) {
        throw new Error('사용자 정보를 가져올 수 없습니다')
      }

      // 3. Check is_active
      if (!userData.is_active) {
        await supabase.auth.signOut()
        throw new Error('비활성화된 계정입니다. 관리자에게 문의하세요.')
      }

      // 4. Remember me
      if (typeof window !== 'undefined') {
        if (rememberMe) {
          localStorage.setItem('valuelink_remembered_email', email.trim())
        } else {
          localStorage.removeItem('valuelink_remembered_email')
        }
      }

      // 5. Role-based redirect
      redirectByRole(userData.role)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '로그인 중 오류가 발생했습니다'

      if (message.includes('Invalid login credentials')) {
        setError('이메일 또는 비밀번호가 올바르지 않습니다')
      } else if (message.includes('Email not confirmed')) {
        setError('이메일 인증이 필요합니다. 이메일을 확인해주세요.')
      } else {
        setError(message)
      }
    } finally {
      setIsLoading(false)
    }
  }

  // ---- Loading (auth check) ----
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-700 to-blue-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent" />
      </div>
    )
  }

  // ---- Render ----
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 to-blue-900 flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
        {/* Card Header */}
        <div className="bg-gradient-to-br from-blue-700 to-blue-900 text-white px-10 py-10 text-center">
          <h1 className="text-3xl font-bold mb-2">ValueLink 로그인</h1>
          <p className="text-blue-200 text-sm">프로젝트 평가 플랫폼</p>
        </div>

        {/* Form */}
        <div className="px-10 py-10">
          <form onSubmit={handleSubmit} noValidate>
            {/* Global Error */}
            {error && (
              <div
                className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm"
                role="alert"
              >
                {error}
              </div>
            )}

            {/* Email */}
            <div className="mb-5">
              <label
                htmlFor="email"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                이메일
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="example@email.com"
                autoComplete="email"
                aria-required="true"
                aria-invalid={!!emailError}
                aria-describedby={emailError ? 'email-error' : undefined}
                className={`w-full px-4 py-3 text-sm border-2 rounded-xl transition-all focus:outline-none focus:ring-0 ${
                  emailError
                    ? 'border-red-400 focus:border-red-500'
                    : 'border-gray-200 focus:border-blue-600 focus:shadow-[0_0_0_3px_rgba(219,234,254,1)]'
                }`}
              />
              {emailError && (
                <p id="email-error" className="mt-1.5 text-xs text-red-500">
                  {emailError}
                </p>
              )}
            </div>

            {/* Password */}
            <div className="mb-5">
              <label
                htmlFor="password"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                비밀번호
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="비밀번호를 입력하세요"
                autoComplete="current-password"
                aria-required="true"
                aria-invalid={!!passwordError}
                aria-describedby={passwordError ? 'password-error' : undefined}
                className={`w-full px-4 py-3 text-sm border-2 rounded-xl transition-all focus:outline-none focus:ring-0 ${
                  passwordError
                    ? 'border-red-400 focus:border-red-500'
                    : 'border-gray-200 focus:border-blue-600 focus:shadow-[0_0_0_3px_rgba(219,234,254,1)]'
                }`}
              />
              {passwordError && (
                <p id="password-error" className="mt-1.5 text-xs text-red-500">
                  {passwordError}
                </p>
              )}
            </div>

            {/* Options */}
            <div className="flex items-center mb-6">
              <label
                htmlFor="rememberMe"
                className="flex items-center gap-2 text-sm text-gray-500 cursor-pointer select-none"
              >
                <input
                  id="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                로그인 상태 유지
              </label>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              aria-busy={isLoading}
              className="w-full py-3.5 text-sm font-semibold text-white bg-blue-700 rounded-xl transition-all hover:bg-blue-800 hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-400">또는</span>
            </div>
          </div>

          {/* Register Link */}
          <p className="text-center text-sm text-gray-500">
            계정이 없으신가요?{' '}
            <Link
              href="/register"
              className="font-semibold text-blue-700 hover:underline"
            >
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
