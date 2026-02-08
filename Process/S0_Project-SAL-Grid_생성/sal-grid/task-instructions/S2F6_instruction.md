# S2F6: Project Management Pages (마이그레이션)

## Task 정보

- **Task ID**: S2F6
- **Task Name**: 프로젝트 관리 페이지 (목록, 상세, 생성) 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2BA2 (프로젝트 API)
- **Task Agent**: frontend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**Valuation_Company의 HTML 프로젝트 관리 페이지를 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 콘텐츠를 참고하여 TSX로 변환
- 프로젝트 목록, 상세, 생성 페이지 구현
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ RLS 정책 (본인 프로젝트만 조회/생성)
- ✅ 입력 검증 (프로젝트명, 평가 방법)
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ SQL Injection 방지 (Supabase 파라미터화 쿼리)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 우선 사용
- ✅ Client Components 최소화
- ✅ 페이지네이션 (프로젝트 목록)
- ✅ 이미지 최적화 (Next.js Image)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 에러 핸들링 강화
- ✅ 접근성 개선 (ARIA 속성)
- ✅ 테스트 가능한 구조

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 반응형 디자인 (모바일 최적화)
- ✅ 빈 상태 UI 명확화
- ✅ 로딩 상태 표시
- ✅ 검색 및 필터 기능 강화

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/core/
├── project-list.html
├── project-detail.html
└── (프로젝트 생성 HTML 존재 시)
```

**분석 항목:**
1. 프로젝트 목록 표시 방식
2. 프로젝트 상세 정보 구성
3. 프로젝트 생성 폼 구조
4. 검색 및 필터 기능
5. UI/UX 패턴

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="project-card">` | `<div className="project-card">` |
| `<a href="/projects/123">` | `<Link href="/projects/123">` |
| `<input onchange="filter()">` | `<input onChange={handleFilter} />` |
| `<select onchange="sort()">` | `<select onChange={handleSort} value={filterStatus}>` |

**주의사항:**
- HTML의 `class` → TSX `className`
- HTML의 `<a>` → Next.js `<Link>`
- 동적 라우팅: `[id]` 폴더 사용

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: 검색 기능 없음 또는 서버 요청
<input type="text" placeholder="검색..." />

// ✅ 개선: 클라이언트 사이드 검색 (실시간)
const [searchTerm, setSearchTerm] = useState('')

const filteredProjects = projects.filter((project) =>
  project.project_name.toLowerCase().includes(searchTerm.toLowerCase())
)

<div className="relative">
  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
  <input
    type="text"
    placeholder="프로젝트 이름 검색..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
  />
</div>
```

```tsx
// ❌ 목업: 필터 기능 미흡
<select>
  <option>전체</option>
  <option>진행 중</option>
</select>

// ✅ 개선: 상태별 필터 + 서버 쿼리
const [filterStatus, setFilterStatus] = useState<string>('all')

useEffect(() => {
  async function loadProjects() {
    let query = supabase
      .from('projects')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (filterStatus !== 'all') {
      query = query.eq('status', filterStatus)
    }

    const { data } = await query
    setProjects(data || [])
  }

  loadProjects()
}, [filterStatus])

<select
  value={filterStatus}
  onChange={(e) => setFilterStatus(e.target.value)}
  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
>
  <option value="all">전체</option>
  <option value="pending">대기 중</option>
  <option value="in_progress">진행 중</option>
  <option value="completed">완료</option>
</select>
```

```tsx
// ❌ 목업: 동적 라우팅 없음 (URL 하드코딩)
<a href="/projects/detail?id=123">프로젝트 보기</a>

// ✅ 개선: Next.js 동적 라우팅
// app/projects/[id]/page.tsx
export default function ProjectDetailPage() {
  const params = useParams()
  const projectId = params.id as string

  useEffect(() => {
    async function loadProject() {
      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .eq('project_id', projectId)
        .single()

      if (error) {
        router.push('/projects/list')
        return
      }

      setProject(data)
    }

    loadProject()
  }, [projectId])
}
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Dynamic Routes (`[id]` 폴더)
- SearchParams (쿼리 파라미터)
- Server Components 우선

**TypeScript 타입 안전성:**
```typescript
// ✅ 프로젝트 타입 정의
export interface Project {
  project_id: string
  project_name: string
  valuation_method: string
  status: string
  current_step: number
  created_at: string
  updated_at: string
}

// ✅ 필터 상태 타입
export type FilterStatus = 'all' | 'pending' | 'in_progress' | 'completed'

// ✅ 정렬 옵션
export type SortOption = 'created_at' | 'updated_at' | 'project_name'
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase 클라이언트 설정 완료

**S2BA2 완료 확인 (선택적):**
- Projects API와 동시 개발 가능

---

## 생성 파일 (3개)

### 1. app/projects/list/page.tsx
**목표:** 프로젝트 목록 페이지

**참고 파일:** `frontend/app/core/project-list.html`

**개선 사항:**
- ✅ 검색 기능 (실시간)
- ✅ 필터 기능 (상태별)
- ✅ 그리드 레이아웃
- ✅ 빈 상태 UI

### 2. app/projects/[id]/page.tsx
**목표:** 프로젝트 상세 페이지

**참고 파일:** `frontend/app/core/project-detail.html`

**개선 사항:**
- ✅ 동적 라우팅
- ✅ 진행 상황 표시
- ✅ 빠른 액션 버튼
- ✅ 담당자 정보

### 3. app/projects/create/page.tsx
**목표:** 프로젝트 생성 페이지

**참고 파일:** (HTML 존재 시 참조)

**개선 사항:**
- ✅ 평가 방법 선택 (라디오 버튼)
- ✅ 실시간 유효성 검사
- ✅ Supabase에 프로젝트 생성
- ✅ 생성 후 리디렉션

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 구조 분석 완료
- [ ] 프로젝트 목록 페이지 구현
- [ ] 프로젝트 상세 페이지 구현
- [ ] 프로젝트 생성 페이지 구현
- [ ] 검색 및 필터 기능
- [ ] Supabase에 프로젝트 생성
- [ ] 반응형 디자인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 프로젝트 CRUD 정상 동작
- [ ] 페이지 간 링크 동작 확인
- [ ] 검색/필터 동작 확인

### 개선 항목 (Improvement)
- [ ] 보안: RLS, 입력 검증
- [ ] 성능: Server Components, 페이지네이션
- [ ] 코드 품질: TypeScript strict, 에러 처리
- [ ] UI/UX: 반응형, 빈 상태 UI, 로딩 상태

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/core/project-list.html`
- `Valuation_Company/valuation-platform/frontend/app/core/project-detail.html`

**분석 포인트:**
1. 프로젝트 목록은 어떻게 표시되는가?
2. 검색/필터 기능이 있는가? (개선 필요)
3. 동적 라우팅이 있는가? (개선 필요)
4. 빈 상태 UI가 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 초기화
- **S1D1**: projects 테이블
- **S2BA2**: Projects API

---

## 주의사항

### ⚠️ 목업의 한계

1. **검색/필터 부족**
   - 실시간 검색 없음
   - 상태별 필터 미흡

2. **동적 라우팅 없음**
   - URL 하드코딩
   - Next.js Dynamic Routes 필요

3. **UX 개선 필요**
   - 빈 상태 UI 부족
   - 로딩 상태 표시 미흡

### 🔒 보안

1. **RLS 보안**
   - 본인 프로젝트만 조회/생성
   - user_id 자동 연결

2. **입력 검증**
   - 프로젝트명 필수
   - 평가 방법 필수

### ⚡ 성능

1. **페이지네이션**
   - 프로젝트 목록 10개씩
   - Infinite scroll 고려

2. **Server Components**
   - 정적 레이아웃은 Server Component
   - 동적 데이터만 Client Component

### 📝 코드 품질

1. **Dynamic Routes**
   - `[id]` 폴더로 동적 라우팅
   - params.id로 project_id 접근

2. **에러 핸들링**
   - 프로젝트 없을 때 404 또는 리디렉션
   - 네트워크 오류 처리

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 3개
**라인 수**: ~760줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
