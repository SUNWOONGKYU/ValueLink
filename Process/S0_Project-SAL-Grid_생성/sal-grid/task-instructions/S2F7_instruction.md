# S2F7: Authentication & Landing Pages (마이그레이션)

## Task 정보

- **Task ID**: S2F7
- **Task Name**: 인증 페이지 및 랜딩 페이지 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2S1 (인증 API - 동시 작업 가능)
- **Task Agent**: frontend-developer
- **Verification Agent**: security-auditor

---

## Task 목표

**Valuation_Company의 HTML 인증/랜딩 페이지를 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 콘텐츠를 참고하여 TSX로 변환
- 로그인, 회원가입, 랜딩 페이지 및 공통 컴포넌트(헤더, 사이드바) 구현
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ CSRF 방지 (Supabase 자동 처리)
- ✅ 비밀번호 강도 검증 (최소 6자)
- ✅ 이메일 유효성 검사
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ Rate limiting 고려 (로그인 시도 제한)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 사용 (정적 콘텐츠)
- ✅ Client Components 최소화 (폼만)
- ✅ Static Generation (랜딩 페이지)
- ✅ 이미지 최적화 (Next.js Image)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 에러 핸들링 강화 (명확한 에러 메시지)
- ✅ 접근성 개선 (ARIA 속성)
- ✅ 테스트 가능한 구조

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 반응형 디자인 (모바일 최적화)
- ✅ 로딩 상태 표시 (제출 중)
- ✅ 에러 메시지 명확화
- ✅ 키보드 네비게이션

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/
├── login.html
├── register.html
└── (랜딩 페이지 HTML 존재 시)
```

**분석 항목:**
1. 로그인 폼 구조
2. 회원가입 폼 구조
3. 랜딩 페이지 섹션 구성
4. 헤더/네비게이션 구조
5. UI/UX 패턴

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="auth-form">` | `<div className="auth-form">` |
| `<form onsubmit="handleLogin()">` | `<form onSubmit={handleSubmit}>` |
| `<input type="email" required>` | `<input type="email" required value={email} onChange={...} />` |
| `<a href="/register">` | `<Link href="/register">` |

**주의사항:**
- HTML의 `class` → TSX `className`
- HTML의 inline 이벤트 → TSX props
- 폼 상태 관리: useState

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: 비밀번호 강도 검증 없음
<input type="password" required />

// ✅ 개선: 비밀번호 강도 검증 + 명확한 에러
const [password, setPassword] = useState('')
const [error, setError] = useState<string | null>(null)

const handleSubmit = async (e: FormEvent) => {
  e.preventDefault()
  setError(null)

  if (password.length < 6) {
    setError('비밀번호는 6자 이상이어야 합니다.')
    return
  }

  // Supabase 회원가입/로그인
}

<div>
  <label>비밀번호</label>
  <input
    type="password"
    value={password}
    onChange={(e) => setPassword(e.target.value)}
    className="..."
    required
  />
  {error && (
    <p className="text-sm text-red-600 mt-1" role="alert">
      {error}
    </p>
  )}
</div>
```

```tsx
// ❌ 목업: 회원가입 후 users 테이블 업데이트 없음
const { data } = await supabase.auth.signUp({ email, password })

// ✅ 개선: users 테이블에 추가 정보 저장
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
```

```tsx
// ❌ 목업: Route Groups 미사용
app/
├── login/page.tsx
├── register/page.tsx

// ✅ 개선: Route Groups로 인증 페이지 그룹화
app/
├── (auth)/
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── layout.tsx (공통 레이아웃)
└── page.tsx (랜딩)

// (auth)/layout.tsx
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      {children}
    </div>
  )
}
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Route Groups (`(auth)` 폴더)
- Server Components (정적 콘텐츠)
- Client Components (폼 상태)

**TypeScript 타입 안전성:**
```typescript
// ✅ 폼 데이터 타입
export interface LoginFormData {
  email: string
  password: string
}

export interface RegisterFormData {
  email: string
  password: string
  passwordConfirm: string
  fullName: string
  companyName: string
  role: 'customer'
}

// ✅ 에러 타입
export interface AuthError {
  message: string
  field?: 'email' | 'password' | 'passwordConfirm'
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase Auth 설정 완료

**S1D1 완료 확인:**
- users 테이블 존재

---

## 생성 파일 (6개)

### 1. app/(auth)/login/page.tsx
**목표:** 로그인 페이지

**참고 파일:** `frontend/app/login.html`

**개선 사항:**
- ✅ 이메일/비밀번호 입력
- ✅ Supabase Auth 연동
- ✅ 에러 메시지 표시
- ✅ 로딩 상태 표시

### 2. app/(auth)/register/page.tsx
**목표:** 회원가입 페이지

**참고 파일:** `frontend/app/register.html`

**개선 사항:**
- ✅ 비밀번호 강도 검증
- ✅ 비밀번호 확인 일치 검사
- ✅ users 테이블 업데이트
- ✅ 회원가입 후 리디렉션

### 3. app/page.tsx
**목표:** 랜딩 페이지 (홈)

**참고 파일:** (HTML 존재 시 참조)

**개선 사항:**
- ✅ Hero Section
- ✅ Features Section
- ✅ CTA Section
- ✅ Static Generation

### 4. app/service-guide/page.tsx
**목표:** 서비스 안내 페이지

**개선 사항:**
- ✅ 서비스 설명
- ✅ 가격 안내

### 5. components/header.tsx
**목표:** 공통 헤더

**개선 사항:**
- ✅ 네비게이션 메뉴
- ✅ 모바일 메뉴
- ✅ 반응형 디자인

### 6. components/sidebar.tsx
**목표:** 공통 사이드바

**개선 사항:**
- ✅ 메뉴 링크
- ✅ 로그아웃 버튼

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 구조 분석 완료
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

### 개선 항목 (Improvement)
- [ ] 보안: CSRF 방지, 비밀번호 강도, 이메일 검증
- [ ] 성능: Server Components, Static Generation
- [ ] 코드 품질: TypeScript strict, 에러 처리
- [ ] UI/UX: 반응형, 로딩 상태, 명확한 에러

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/login.html`
- `Valuation_Company/valuation-platform/frontend/app/register.html`

**분석 포인트:**
1. 폼 구조는 명확한가?
2. 비밀번호 검증이 있는가? (개선 필요)
3. users 테이블 업데이트가 있는가? (개선 필요)
4. 모바일 메뉴가 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 초기화
- **S1D1**: users 테이블
- **S2S1**: 인증 API (동시 작업 가능)

---

## 주의사항

### ⚠️ 목업의 한계

1. **비밀번호 검증 부족**
   - 강도 검증 없음
   - 최소 길이 확인 필요

2. **users 테이블 연동 미흡**
   - 회원가입 시 users 테이블 업데이트 필요
   - 추가 정보 (full_name, company_name) 저장

3. **UX 개선 필요**
   - 에러 메시지 불명확
   - 로딩 상태 표시 미흡

### 🔒 보안

1. **Route Groups**
   - `(auth)` 폴더로 인증 관련 페이지 그룹화
   - 레이아웃 공유 가능

2. **보안**
   - 비밀번호 6자 이상
   - 이메일 유효성 검사
   - CSRF 방지 (Supabase 자동 처리)

### ⚡ 성능

1. **Server Components**
   - 정적 콘텐츠는 Server Component
   - 폼만 Client Component

2. **Static Generation**
   - 랜딩 페이지는 Static
   - 빌드 시 미리 생성

### 📝 코드 품질

1. **사용자 경험**
   - 에러 메시지 명확히
   - 로딩 상태 표시
   - 모바일 최적화

2. **접근성**
   - ARIA 속성 추가
   - 키보드 네비게이션

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 6개
**라인 수**: ~830줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
