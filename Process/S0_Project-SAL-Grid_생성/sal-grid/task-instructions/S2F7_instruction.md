# S2F7: Authentication & Landing Pages

## Task 정보

- **Task ID**: S2F7
- **Task Name**: 인증 페이지 및 랜딩 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2S1 (인증 API - 동시 작업 가능)
- **Task Agent**: frontend-developer
- **Verification Agent**: security-auditor

---

## Task 목표

로그인, 회원가입, 랜딩 페이지 및 공통 컴포넌트(헤더, 사이드바)를 구현하여 사용자 인증 흐름 완성

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase Auth 설정 완료

---

### 1. 로그인 페이지

**파일**: `app/(auth)/login/page.tsx`

```typescript
'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'
import { Mail, Lock, AlertCircle } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const supabase = createClient()

      const { error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (signInError) {
        setError('이메일 또는 비밀번호가 올바르지 않습니다.')
        setIsSubmitting(false)
        return
      }

      router.push('/mypage/company')
    } catch (err) {
      setError('로그인에 실패했습니다. 다시 시도해주세요.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* 로고 & 제목 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ValueLink</h1>
          <p className="text-gray-600">기업가치평가 플랫폼</p>
        </div>

        {/* 로그인 폼 */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">로그인</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 이메일 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                이메일
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 비밀번호 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                비밀번호
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 로그인 버튼 */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-4 py-3 text-white bg-red-600 rounded-lg hover:bg-red-700 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '로그인 중...' : '로그인'}
            </button>
          </form>

          {/* 링크 */}
          <div className="mt-6 text-center text-sm">
            <p className="text-gray-600">
              계정이 없으신가요?{' '}
              <Link
                href="/register"
                className="text-red-600 hover:text-red-700 font-medium"
              >
                회원가입
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### 2. 회원가입 페이지

**파일**: `app/(auth)/register/page.tsx`

```typescript
'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'
import { Mail, Lock, User, Building, AlertCircle } from 'lucide-react'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    passwordConfirm: '',
    fullName: '',
    companyName: '',
    role: 'customer',
  })
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    if (formData.password !== formData.passwordConfirm) {
      setError('비밀번호가 일치하지 않습니다.')
      return
    }

    if (formData.password.length < 6) {
      setError('비밀번호는 6자 이상이어야 합니다.')
      return
    }

    setIsSubmitting(true)

    try {
      const supabase = createClient()

      // 회원가입
      const { data: authData, error: signUpError } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            full_name: formData.fullName,
            company_name: formData.companyName,
            role: formData.role,
          },
        },
      })

      if (signUpError) {
        setError('회원가입에 실패했습니다. 이미 가입된 이메일일 수 있습니다.')
        setIsSubmitting(false)
        return
      }

      // users 테이블에 추가 정보 저장
      if (authData.user) {
        const { error: insertError } = await supabase.from('users').insert({
          user_id: authData.user.id,
          email: formData.email,
          full_name: formData.fullName,
          company_name: formData.companyName,
          role: formData.role,
        })

        if (insertError) {
          console.error('사용자 정보 저장 실패:', insertError)
        }
      }

      router.push('/login?registered=true')
    } catch (err) {
      setError('회원가입에 실패했습니다. 다시 시도해주세요.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* 로고 & 제목 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ValueLink</h1>
          <p className="text-gray-600">기업가치평가 플랫폼</p>
        </div>

        {/* 회원가입 폼 */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            회원가입
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 이메일 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                이메일
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 비밀번호 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                비밀번호
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 비밀번호 확인 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                비밀번호 확인
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.passwordConfirm}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      passwordConfirm: e.target.value,
                    })
                  }
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 이름 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                이름
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.fullName}
                  onChange={(e) =>
                    setFormData({ ...formData, fullName: e.target.value })
                  }
                  placeholder="홍길동"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 기업명 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                기업명
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.companyName}
                  onChange={(e) =>
                    setFormData({ ...formData, companyName: e.target.value })
                  }
                  placeholder="주식회사 ABC"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
            </div>

            {/* 회원가입 버튼 */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-4 py-3 text-white bg-red-600 rounded-lg hover:bg-red-700 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '가입 중...' : '회원가입'}
            </button>
          </form>

          {/* 링크 */}
          <div className="mt-6 text-center text-sm">
            <p className="text-gray-600">
              이미 계정이 있으신가요?{' '}
              <Link
                href="/login"
                className="text-red-600 hover:text-red-700 font-medium"
              >
                로그인
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### 3. 랜딩 페이지 (홈)

**파일**: `app/page.tsx`

```typescript
import Link from 'next/link'
import { TrendingUp, Shield, Zap, Users } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-red-600 to-red-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">
              기업가치평가의 새로운 기준
            </h1>
            <p className="text-xl mb-8 text-red-100">
              AI와 전문 회계사가 함께하는 빠르고 정확한 평가
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/register"
                className="px-8 py-3 bg-white text-red-600 rounded-lg font-semibold hover:bg-gray-100 text-lg"
              >
                무료로 시작하기
              </Link>
              <Link
                href="/service-guide"
                className="px-8 py-3 bg-red-700 text-white border-2 border-white rounded-lg font-semibold hover:bg-red-800 text-lg"
              >
                서비스 알아보기
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            왜 ValueLink인가?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">빠른 평가</h3>
              <p className="text-gray-600">
                평균 10일 이내 평가 완료
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">전문성</h3>
              <p className="text-gray-600">
                회계사 직접 검토 및 승인
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">5가지 평가 방법</h3>
              <p className="text-gray-600">
                DCF, Relative, Asset, Intrinsic, Tax
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">투명한 프로세스</h3>
              <p className="text-gray-600">
                14단계 진행 상황 실시간 확인
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            회원가입 후 첫 번째 평가를 신청해보세요
          </p>
          <Link
            href="/register"
            className="inline-block px-8 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 text-lg"
          >
            무료 회원가입
          </Link>
        </div>
      </section>
    </div>
  )
}
```

---

### 4. 공통 헤더 컴포넌트

**파일**: `components/header.tsx`

```typescript
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navigation = [
    { name: '서비스 안내', href: '/service-guide' },
    { name: '평가 방법', href: '/valuation/guides/dcf' },
    { name: '내 프로젝트', href: '/projects/list' },
  ]

  return (
    <header className="bg-white border-b">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* 로고 */}
          <Link href="/" className="text-2xl font-bold text-red-600">
            ValueLink
          </Link>

          {/* 데스크톱 네비게이션 */}
          <div className="hidden md:flex items-center gap-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`text-sm font-medium ${
                  pathname?.startsWith(item.href)
                    ? 'text-red-600'
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                {item.name}
              </Link>
            ))}
            <Link
              href="/login"
              className="px-4 py-2 text-gray-700 hover:text-gray-900"
            >
              로그인
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
            >
              시작하기
            </Link>
          </div>

          {/* 모바일 메뉴 버튼 */}
          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* 모바일 메뉴 */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            <Link
              href="/login"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-50"
              onClick={() => setMobileMenuOpen(false)}
            >
              로그인
            </Link>
            <Link
              href="/register"
              className="block px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 mx-4"
              onClick={() => setMobileMenuOpen(false)}
            >
              시작하기
            </Link>
          </div>
        )}
      </nav>
    </header>
  )
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `app/(auth)/login/page.tsx` | 로그인 페이지 | ~150줄 |
| `app/(auth)/register/page.tsx` | 회원가입 페이지 | ~250줄 |
| `app/page.tsx` | 랜딩 페이지 (홈) | ~150줄 |
| `app/service-guide/page.tsx` | 서비스 안내 페이지 | ~100줄 |
| `components/header.tsx` | 공통 헤더 | ~100줄 |
| `components/sidebar.tsx` | 공통 사이드바 | ~80줄 |

**총 파일 수**: 6개 (5개 명시 + sidebar)
**총 라인 수**: ~830줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router, Route Groups)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Auth**: Supabase Auth
- **Icons**: lucide-react

---

## 완료 기준

### 필수 (Must Have)

- [ ] 로그인 페이지 구현
- [ ] 회원가입 페이지 구현
- [ ] 랜딩 페이지 구현
- [ ] 공통 헤더 컴포넌트
- [ ] Supabase Auth 연동
- [ ] 반응형 디자인

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 로그인/회원가입 동작 확인
- [ ] 인증 후 리디렉션 동작
- [ ] 모바일 메뉴 동작 확인

### 권장 (Nice to Have)

- [ ] Google OAuth
- [ ] 비밀번호 찾기
- [ ] 이메일 인증

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/login.html`
- `Valuation_Company/valuation-platform/frontend/app/register.html`

### 관련 Task

- **S1BI1**: Next.js 초기화
- **S1D1**: users 테이블
- **S2S1**: 인증 API (동시 작업 가능)

---

## 주의사항

1. **Route Groups**
   - `(auth)` 폴더로 인증 관련 페이지 그룹화
   - 레이아웃 공유 가능

2. **보안**
   - 비밀번호 6자 이상
   - 이메일 유효성 검사
   - CSRF 방지 (Supabase 자동 처리)

3. **사용자 경험**
   - 에러 메시지 명확히
   - 로딩 상태 표시
   - 모바일 최적화

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 6개
**라인 수**: ~830줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
