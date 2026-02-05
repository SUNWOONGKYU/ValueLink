# S2F4 Verification

## 검증 대상

- **Task ID**: S2F4
- **Task Name**: 역할별 마이페이지 템플릿 및 6개 역할 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)

## 검증자

**Verification Agent**: qa-specialist

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

#### 1.1 TypeScript 빌드 성공

- [ ] **TypeScript 타입 체킹 성공**
  - 명령어: `npm run type-check`
  - 출력: `0 errors`

#### 1.2 Next.js 빌드 성공

- [ ] **Next.js 프로젝트 빌드 성공**
  - 명령어: `npm run build`
  - 출력: `✓ Compiled successfully`

#### 1.3 ESLint 경고 0개

- [ ] **ESLint 검사 통과**
  - 명령어: `npm run lint`
  - 출력: ESLint 에러/경고 없음

---

### 2. 파일 생성 확인

#### 2.1 공통 템플릿 컴포넌트

- [ ] **`components/mypage-template.tsx` 파일 존재**
  - 명령어: `ls components/mypage-template.tsx`
  - Props: `role`, `userName`, `userEmail`, `children`
  - Export: `MyPageTemplate` 컴포넌트

#### 2.2 6개 역할별 마이페이지

- [ ] **`app/mypage/company/page.tsx` 존재**
  - 기업(고객) 마이페이지
  - 프로젝트 목록 표시

- [ ] **`app/mypage/accountant/page.tsx` 존재**
  - 회계사 마이페이지
  - 담당 프로젝트 목록

- [ ] **`app/mypage/investor/page.tsx` 존재**
  - 투자자 마이페이지
  - Deal 뉴스, 관심 기업

- [ ] **`app/mypage/partner/page.tsx` 존재**
  - 파트너 마이페이지
  - 추천 현황

- [ ] **`app/mypage/supporter/page.tsx` 존재**
  - 서포터 마이페이지
  - 지원 통계

- [ ] **`app/mypage/admin/page.tsx` 존재**
  - 관리자 마이페이지
  - 전체 통계, 사용자 관리

---

### 3. 핵심 기능 테스트

#### 3.1 템플릿 컴포넌트 재사용

- [ ] **6개 마이페이지 모두 `MyPageTemplate` 사용**
  - 각 페이지에서 import 확인
  - `<MyPageTemplate role="customer" ...>` 형식

#### 3.2 역할 기반 데이터 로드 (RLS)

- [ ] **각 역할별로 본인 데이터만 조회**
  - 기업: 본인이 생성한 프로젝트만
  - 회계사: 담당 프로젝트만
  - 관리자: 모든 데이터 접근

#### 3.3 로그아웃 기능

- [ ] **로그아웃 버튼 클릭 시 정상 동작**
  - `handleLogout` 함수 구현
  - `supabase.auth.signOut()` 호출
  - `/login` 페이지로 리디렉션

#### 3.4 역할별 통계 카드

- [ ] **각 역할별 통계 카드 표시**
  - 기업: 전체/진행중/완료/대기 프로젝트 수
  - 회계사: 담당 프로젝트 통계
  - 투자자: 관심 기업 수, 뉴스 수
  - 관리자: 전체 사용자, 프로젝트 통계

#### 3.5 기업 마이페이지 특수 기능

- [ ] **프로젝트 목록 표시**
  - 프로젝트명, 평가방법, 상태, 진행단계 표시
  - 클릭 시 프로젝트 상세로 이동

- [ ] **"새 프로젝트" 버튼**
  - `/projects/create` 페이지로 이동

- [ ] **빈 상태 표시**
  - 프로젝트가 없을 때 안내 메시지
  - "첫 프로젝트 만들기" 버튼

#### 3.6 회계사 마이페이지 특수 기능

- [ ] **담당 프로젝트 필터링**
  - `approval_points` 테이블 연결
  - 본인이 담당하는 프로젝트만 표시

#### 3.7 관리자 마이페이지 특수 기능

- [ ] **전체 통계 표시**
  - 총 사용자 수
  - 총 프로젝트 수
  - 역할별 사용자 분포

- [ ] **사용자 관리 테이블**
  - 사용자 목록 (이메일, 역할, 가입일)
  - 역할 변경 기능 (선택 사항)

---

### 4. 통합 테스트

#### 4.1 선행 Task 호환

- [ ] **S1BI1 (Supabase 클라이언트) 의존성 충족**
  - `@/lib/supabase/client` import 가능
  - `createClient()` 정상 작동

- [ ] **S1D1 (Database Schema) 의존성 충족**
  - `users` 테이블에 `role` 컬럼 존재
  - `projects` 테이블 존재

#### 4.2 후행 Task 준비

- [ ] **S2F6 (프로젝트 관리 페이지) 연결 준비**
  - 프로젝트 클릭 시 상세 페이지 이동 경로 준비

#### 4.3 데이터 흐름 검증

- [ ] **사용자 인증 → 역할 확인 → 데이터 로드**
  - `supabase.auth.getUser()` 호출
  - `users` 테이블에서 역할 조회
  - 역할 기반 RLS 정책 적용

---

### 5. Blocker 확인

#### 5.1 의존성 차단

- [ ] **S1BI1 완료 확인**
  - Supabase 클라이언트 설정 완료

- [ ] **S1D1 완료 확인**
  - `users`, `projects` 테이블 생성 완료

#### 5.2 환경 차단

- [ ] **lucide-react 패키지 설치 확인**
  - 명령어: `npm list lucide-react`
  - 버전: `^0.300.0` 이상

#### 5.3 외부 API 차단

- [ ] **Supabase 연결 필요**
  - 환경 변수 설정 완료 확인
  - `users`, `projects` 테이블 접근 가능

---

### 6. UI/UX 검증

#### 6.1 페이지 렌더링 확인

- [ ] **개발 서버 실행 후 각 페이지 접속**
  - `/mypage/company` 접속 가능
  - `/mypage/accountant` 접속 가능
  - `/mypage/investor` 접속 가능
  - `/mypage/partner` 접속 가능
  - `/mypage/supporter` 접속 가능
  - `/mypage/admin` 접속 가능

#### 6.2 레이아웃 일관성

- [ ] **모든 마이페이지 레이아웃 동일**
  - 헤더(사용자 정보, 로그아웃 버튼)
  - 통계 카드 (grid layout)
  - 데이터 목록 (table/card)

#### 6.3 반응형 디자인

- [ ] **모바일 화면에서 정상 표시**
  - Tailwind CSS 반응형 클래스 사용 확인 (`md:`, `lg:`)
  - 통계 카드가 모바일에서 1열로 변경

#### 6.4 로딩 상태

- [ ] **데이터 로드 중 스피너 표시**
  - `loading` 상태 관리
  - 애니메이션 스피너 표시

#### 6.5 빈 상태 표시

- [ ] **데이터가 없을 때 안내 메시지**
  - 아이콘 + 텍스트
  - 액션 버튼 (예: "새 프로젝트 만들기")

---

## 합격 기준

### 필수 (Must Pass)

1. **TypeScript 빌드 성공** ✅
   - `npm run type-check` 에러 없음

2. **Next.js 빌드 성공** ✅
   - `npm run build` 성공

3. **ESLint 경고 0개** ✅
   - `npm run lint` 에러/경고 없음

4. **모든 파일 생성 완료** ✅
   - `components/mypage-template.tsx`
   - 6개 역할별 마이페이지 (`app/mypage/{role}/page.tsx`)

5. **템플릿 컴포넌트 재사용** ✅
   - 6개 페이지 모두 `MyPageTemplate` 사용

6. **역할 기반 데이터 로드** ✅
   - RLS 정책 적용
   - 본인 데이터만 조회

7. **로그아웃 기능 구현** ✅
   - `supabase.auth.signOut()` 호출
   - `/login` 페이지로 리디렉션

### 권장 (Nice to Pass)

1. **프로필 수정 기능** ✨
   - 사용자 정보 수정 페이지

2. **알림 센터** ✨
   - 새 알림 표시

3. **활동 로그** ✨
   - 최근 활동 내역

---

## 검증 결과

### Pass/Fail

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

### 발견 사항

#### 🟢 통과 항목

- (통과한 항목 나열)

#### 🔴 실패 항목

- (실패한 항목 나열 및 수정 필요 사항)

#### 🟡 경고 사항

- (경고 또는 개선 권장 사항)

---

## 주의사항

1. **RLS 보안**
   - 역할 기반 접근 제어 필수
   - 본인 데이터만 조회 가능

2. **템플릿 일관성**
   - 모든 마이페이지 레이아웃 동일
   - 역할별 차이는 콘텐츠만

3. **성능 최적화**
   - 프로젝트 목록 페이지네이션 (10개씩)
   - 관리자 페이지 최적화 (사용자 수 많을 경우)

4. **UX**
   - 빈 상태 명확히 표시
   - 로딩 상태 표시
   - 에러 메시지 사용자 친화적으로

5. **역할 확인**
   - 사용자 역할에 맞는 페이지 접근
   - 잘못된 역할로 접근 시 리디렉션

---

## 참조

- Task Instruction: `task-instructions/S2F4_instruction.md`
- 기존 프로토타입: `Valuation_Company/valuation-platform/frontend/app/core/mypage-admin.html`
- Next.js App Router: https://nextjs.org/docs/app
- Supabase RLS: https://supabase.com/docs/guides/auth/row-level-security

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
