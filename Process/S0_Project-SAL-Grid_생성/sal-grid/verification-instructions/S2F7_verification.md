# S2F7 Verification

## 검증 대상

- **Task ID**: S2F7
- **Task Name**: 인증 페이지 및 랜딩 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)

## 검증자

**Verification Agent**: security-auditor

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

- [ ] **`app/(auth)/login/page.tsx` 존재** - 로그인 페이지
- [ ] **`app/(auth)/register/page.tsx` 존재** - 회원가입 페이지
- [ ] **`app/page.tsx` 존재** - 랜딩 페이지 (홈)
- [ ] **`app/service-guide/page.tsx` 존재** - 서비스 안내 페이지
- [ ] **`components/header.tsx` 존재** - 공통 헤더
- [ ] **`components/sidebar.tsx` 존재** - 공통 사이드바

---

### 3. 핵심 기능 테스트

#### 3.1 로그인 페이지

- [ ] **이메일/비밀번호 입력**
  - 이메일 형식 검증
  - 비밀번호 입력 (마스킹)

- [ ] **로그인 버튼**
  - `supabase.auth.signInWithPassword()` 호출
  - 성공 시 `/mypage/company` 리디렉션

- [ ] **에러 처리**
  - 잘못된 이메일/비밀번호 시 에러 메시지 표시
  - "이메일 또는 비밀번호가 올바르지 않습니다."

- [ ] **로딩 상태**
  - 제출 중 버튼 비활성화
  - "로그인 중..." 텍스트 표시

- [ ] **회원가입 링크**
  - `/register` 페이지로 이동

#### 3.2 회원가입 페이지

- [ ] **폼 필드 입력**
  - 이메일, 비밀번호, 비밀번호 확인, 이름, 기업명

- [ ] **비밀번호 유효성 검사**
  - 6자 이상 검증
  - 비밀번호 확인 일치 검증

- [ ] **회원가입 버튼**
  - `supabase.auth.signUp()` 호출
  - `users` 테이블에 추가 정보 저장
  - 성공 시 `/login?registered=true` 리디렉션

- [ ] **에러 처리**
  - 중복 이메일 시 에러 메시지
  - 비밀번호 불일치 시 에러 메시지

- [ ] **로그인 링크**
  - `/login` 페이지로 이동

#### 3.3 랜딩 페이지 (홈)

- [ ] **Hero Section**
  - 제목, 설명, CTA 버튼
  - "무료로 시작하기" → `/register`
  - "서비스 알아보기" → `/service-guide`

- [ ] **Features Section**
  - 4개 특징 카드 (빠른 평가, 전문성, 5가지 평가 방법, 투명한 프로세스)
  - 아이콘 + 제목 + 설명

- [ ] **CTA Section**
  - "무료 회원가입" 버튼 → `/register`

#### 3.4 공통 헤더 컴포넌트

- [ ] **로고**
  - "ValueLink" 클릭 시 홈 (`/`)으로 이동

- [ ] **네비게이션 메뉴**
  - 서비스 안내, 평가 방법, 내 프로젝트
  - 현재 경로 하이라이트

- [ ] **로그인/시작하기 버튼**
  - 로그인 → `/login`
  - 시작하기 → `/register`

- [ ] **모바일 메뉴**
  - 햄버거 아이콘 클릭 시 메뉴 토글
  - 메뉴 항목 클릭 시 메뉴 닫힘

---

### 4. 통합 테스트

#### 4.1 선행 Task 호환

- [ ] **S1BI1 (Supabase 클라이언트) 의존성 충족**
  - `@/lib/supabase/client` import 가능
  - Supabase Auth 설정 완료

- [ ] **S1D1 (Database Schema) 의존성 충족**
  - `users` 테이블 존재

#### 4.2 인증 흐름 검증

- [ ] **회원가입 → 로그인 → 마이페이지**
  - 회원가입 성공 시 로그인 페이지로 리디렉션
  - 로그인 성공 시 마이페이지로 리디렉션

#### 4.3 Route Groups 동작

- [ ] **`(auth)` 폴더 구조**
  - URL에 `(auth)` 경로 포함되지 않음
  - `/login`, `/register` 경로로 접근

---

### 5. Blocker 확인

- [ ] **S1BI1 완료 확인** - Supabase Auth 설정
- [ ] **lucide-react 패키지 설치** 확인
- [ ] **Supabase 연결** - users 테이블 접근 가능

---

### 6. 보안 검증

#### 6.1 비밀번호 보안

- [ ] **비밀번호 최소 길이**
  - 6자 이상 검증

- [ ] **비밀번호 마스킹**
  - `type="password"` 사용

- [ ] **비밀번호 확인**
  - 두 입력값 일치 검증

#### 6.2 이메일 유효성

- [ ] **이메일 형식 검증**
  - `type="email"` 사용
  - 이메일 형식 자동 검증

#### 6.3 CSRF 방지

- [ ] **Supabase CSRF 보호**
  - Supabase가 자동으로 CSRF 토큰 처리

#### 6.4 XSS 방지

- [ ] **사용자 입력 sanitization**
  - React의 자동 이스케이프 처리 확인

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (6개 파일)
3. **로그인/회원가입 동작 확인** ✅
4. **Supabase Auth 연동** ✅
5. **보안 검증 통과** ✅

### 권장 (Nice to Pass)

1. **Google OAuth** ✨
2. **비밀번호 찾기** ✨
3. **이메일 인증** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

---

## 주의사항

1. **Route Groups**
   - `(auth)` 폴더로 인증 관련 페이지 그룹화
   - URL에는 `(auth)` 경로 포함되지 않음

2. **보안**
   - 비밀번호 6자 이상
   - 이메일 유효성 검사
   - CSRF 방지 (Supabase 자동 처리)

3. **사용자 경험**
   - 에러 메시지 명확히
   - 로딩 상태 표시
   - 모바일 최적화

---

## 참조

- Task Instruction: `task-instructions/S2F7_instruction.md`
- 기존 프로토타입: `Valuation_Company/valuation-platform/frontend/app/login.html`
- Supabase Auth: https://supabase.com/docs/guides/auth

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
