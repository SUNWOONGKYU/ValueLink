# S2F4: Role-Based My Page Template & 6 Role Variants (마이그레이션)

## Task 정보

- **Task ID**: S2F4
- **Task Name**: 역할별 마이페이지 템플릿 및 6개 역할 페이지 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S1D1 (users 테이블)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

**Valuation_Company의 HTML 마이페이지를 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 콘텐츠를 참고하여 TSX로 변환
- 6개 역할별(기업, 회계사, 투자자, 파트너, 서포터, 관리자) 마이페이지 구현
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ RLS 정책 (본인 데이터만 조회)
- ✅ 역할 기반 접근 제어 (Role-Based Access Control)
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ 안전한 로그아웃 (세션 완전 삭제)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 사용 (정적 레이아웃)
- ✅ Client Components 최소화 (동적 데이터만)
- ✅ 페이지네이션 (프로젝트 목록 10개씩)
- ✅ 이미지 최적화 (Next.js Image)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 재사용 가능한 템플릿 컴포넌트
- ✅ 에러 핸들링 강화
- ✅ 접근성 개선 (ARIA, semantic HTML)

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 반응형 디자인 (모바일 최적화)
- ✅ 빈 상태 UI 명확화
- ✅ 로딩 상태 표시
- ✅ 역할별 맞춤 대시보드

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/core/
├── mypage-admin.html
├── mypage-customer.html (존재 시)
└── (기타 역할별 HTML 파일)
```

**분석 항목:**
1. 각 역할별 대시보드 구성
2. 통계 카드 구조
3. 프로젝트 목록 표시 방식
4. 네비게이션 구조
5. UI/UX 패턴

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="dashboard">` | `<div className="dashboard">` |
| `<a href="/mypage/settings">` | `<Link href="/mypage/settings">` |
| `<script>loadProjects()</script>` | `useEffect(() => { loadProjects() }, [])` |
| Static HTML | Server Component (레이아웃) + Client Component (데이터) |

**주의사항:**
- HTML의 `class` → TSX `className`
- HTML의 `<a>` → Next.js `<Link>`
- 역할별 통계는 동적 데이터 (Client Component)

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: Client Component로 전체 페이지 렌더링 (느림)
'use client'
export default function CompanyMyPage() {
  const [user, setUser] = useState(null)
  const [projects, setProjects] = useState([])
  // ...
}

// ✅ 개선: Server Component 템플릿 + Client Component 데이터
// mypage-template.tsx (Server Component)
export default function MyPageTemplate({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header>...</header>
      <main>{children}</main>
    </div>
  )
}

// company/page.tsx (Client Component - 필요한 부분만)
'use client'
export default function CompanyMyPage() {
  const { data: projects } = useProjects() // SWR 또는 React Query
  // ...
}
```

```tsx
// ❌ 목업: 역할별 접근 제어 부족
const [projects, setProjects] = useState([])

// ✅ 개선: RLS + 역할 기반 필터링
const supabase = createClient()
const { data: { user } } = await supabase.auth.getUser()

const { data: userData } = await supabase
  .from('users')
  .select('role')
  .eq('user_id', user.id)
  .single()

let query = supabase.from('projects').select('*')

if (userData.role === 'customer') {
  query = query.eq('user_id', user.id) // 본인 프로젝트만
} else if (userData.role === 'accountant') {
  query = query.eq('accountant_id', user.id) // 담당 프로젝트만
} else if (userData.role === 'admin') {
  // 전체 프로젝트 조회 가능
}

const { data: projects } = await query
```

```tsx
// ❌ 목업: 빈 상태 UI 부족
{projects.length === 0 && <p>프로젝트가 없습니다.</p>}

// ✅ 개선: 명확한 빈 상태 UI
{projects.length === 0 ? (
  <div className="bg-white rounded-lg shadow p-12 text-center">
    <FolderOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      프로젝트가 없습니다.
    </h3>
    <p className="text-gray-500 mb-6">
      첫 번째 프로젝트를 시작해보세요.
    </p>
    <Link
      href="/projects/create"
      className="inline-flex items-center gap-2 px-6 py-3 text-white bg-red-600 rounded-lg hover:bg-red-700"
    >
      <Plus className="w-5 h-5" />
      <span>프로젝트 만들기</span>
    </Link>
  </div>
) : (
  // 프로젝트 목록
)}
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Server Components (정적 템플릿)
- Client Components (동적 데이터)
- Dynamic Routes (역할별 페이지)

**TypeScript 타입 안전성:**
```typescript
// ✅ 역할 타입 정의
export type UserRole = 'customer' | 'accountant' | 'investor' | 'partner' | 'supporter' | 'admin'

export interface MyPageTemplateProps {
  role: UserRole
  userName: string
  userEmail: string
  children: ReactNode
}

// ✅ 역할별 대시보드 데이터
export interface DashboardStats {
  total: number
  in_progress: number
  completed: number
  pending: number
}

export interface CustomerDashboard {
  stats: DashboardStats
  projects: Project[]
}

export interface AccountantDashboard {
  stats: DashboardStats
  assigned_projects: Project[]
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase Auth 설정 완료

**S1D1 완료 확인:**
- users 테이블에 role 컬럼 존재

---

## 생성 파일 (7개)

### 1. components/mypage-template.tsx
**목표:** 공통 마이페이지 템플릿

**참고 파일:** `frontend/app/core/mypage-*.html`의 공통 구조

**개선 사항:**
- ✅ 재사용 가능한 템플릿
- ✅ 역할별 헤더 표시
- ✅ 로그아웃 기능
- ✅ 반응형 레이아웃

### 2-7. app/mypage/{role}/page.tsx (6개)
**목표:** 6개 역할별 마이페이지

**참고 파일:**
- `mypage-admin.html` → `app/mypage/admin/page.tsx`
- (기타 역할별 HTML 존재 시 참조)

**역할:**
- customer: 기업 (프로젝트 목록)
- accountant: 회계사 (담당 프로젝트)
- investor: 투자자 (Deal 뉴스, 관심 기업)
- partner: 파트너 (추천 현황)
- supporter: 서포터 (지원 통계)
- admin: 관리자 (전체 통계, 사용자 관리)

**개선 사항:**
- ✅ 역할별 맞춤 대시보드
- ✅ 통계 카드
- ✅ 페이지네이션
- ✅ 검색/필터 기능

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 구조 분석 완료
- [ ] 공통 템플릿 컴포넌트 구현
- [ ] 6개 역할별 마이페이지 구현
- [ ] 역할 기반 데이터 로드 (RLS)
- [ ] 로그아웃 기능
- [ ] 반응형 디자인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 역할별 페이지 정상 렌더링
- [ ] 데이터 정상 로드
- [ ] 로그아웃 동작 확인
- [ ] RLS 정책 작동 확인

### 개선 항목 (Improvement)
- [ ] 보안: RLS, 역할 기반 접근 제어, 안전한 로그아웃
- [ ] 성능: Server Components, 페이지네이션
- [ ] 코드 품질: TypeScript strict, 재사용 템플릿
- [ ] UI/UX: 반응형, 빈 상태 UI, 로딩 상태

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/core/mypage-admin.html`
- (기타 역할별 HTML 파일 존재 시 참조)

**분석 포인트:**
1. 각 역할별 대시보드 구성은?
2. 통계 카드는 명확한가?
3. 역할별 접근 제어가 있는가? (개선 필요)
4. 빈 상태 UI가 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 초기화
- **S1D1**: users, projects 테이블
- **S2F6**: 프로젝트 관리 페이지

---

## 주의사항

### ⚠️ 목업의 한계

1. **접근 제어 부족**
   - 역할 기반 필터링 없음
   - RLS 정책 필요

2. **성능 최적화 부족**
   - Client-side only
   - Server Components 미활용

3. **UX 개선 필요**
   - 빈 상태 UI 부족
   - 로딩 상태 표시 미흡

### 🔒 보안

1. **RLS 정책**
   - 본인 데이터만 조회 가능
   - 역할 기반 접근 제어

2. **안전한 로그아웃**
   - 세션 완전 삭제
   - 클라이언트 상태 초기화

### ⚡ 성능

1. **Server Components**
   - 정적 템플릿은 Server Component
   - 동적 데이터만 Client Component

2. **페이지네이션**
   - 프로젝트 목록 10개씩
   - Infinite scroll 고려

### 📝 코드 품질

1. **재사용성**
   - MyPageTemplate 컴포넌트
   - 역할별 통계 카드 컴포넌트

2. **타입 안전성**
   - UserRole 타입
   - DashboardStats 인터페이스

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 7개
**라인 수**: ~1,260줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
