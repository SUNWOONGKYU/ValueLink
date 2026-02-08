# S4F1: Deal News Tracker & Investment Monitor (마이그레이션)

## Task 정보

- **Task ID**: S4F1
- **Task Name**: Deal 뉴스 트래커 및 투자 모니터 마이그레이션
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S4E2 (News Parser)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

**Valuation_Company의 HTML Deal 뉴스 페이지를 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 콘텐츠를 참고하여 TSX로 변환
- Deal 뉴스 트래커 및 투자 네트워크 페이지 구현
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ 외부 링크 안전 처리 (rel="noopener noreferrer")
- ✅ SQL Injection 방지 (Supabase 파라미터화 쿼리)
- ✅ RLS 정책 (공개 데이터)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 사용 (통계 데이터)
- ✅ Client Components 최소화 (필터만)
- ✅ 페이지네이션 (100개 제한)
- ✅ 인덱싱 최적화 (published_date)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 에러 핸들링 강화
- ✅ 접근성 개선 (ARIA 속성)
- ✅ 반응형 디자인

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 실시간 검색 (클라이언트 사이드)
- ✅ 복수 필터 (투자 단계 + 업종)
- ✅ 통계 카드 (이번 주 투자 등)
- ✅ 빈 상태 UI 명확화

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/
├── deal.html (2497줄)
└── link.html (959줄)
```

**분석 항목:**
1. Deal 목록 표시 방식
2. 필터링 UI 구조
3. 통계 카드 구성
4. 투자자-기업 네트워크 표시
5. UI/UX 패턴

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="deal-card">` | `<div className="deal-card">` |
| `<input onchange="filter()">` | `<input onChange={handleFilter} />` |
| `<select onchange="sort()">` | `<select onChange={handleSort} value={filterStatus}>` |
| Static HTML | Server Component (통계) + Client Component (필터) |

**주의사항:**
- HTML의 `class` → TSX `className`
- 필터 상태는 useState로 관리
- Supabase 조회는 useEffect에서

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: 전체 페이지 Client Component (느림)
'use client'
export default function DealPage() {
  const [deals, setDeals] = useState([])
  // ...
}

// ✅ 개선: Server Component (통계) + Client Component (필터)
// Server Component (통계 데이터 미리 로드)
export default async function DealPage() {
  const supabase = createServerClient()
  const { data: initialDeals } = await supabase
    .from('investment_tracker')
    .select('*')
    .order('published_date', { ascending: false })
    .limit(100)

  return <DealList initialDeals={initialDeals || []} />
}

// Client Component (필터링만)
'use client'
function DealList({ initialDeals }: { initialDeals: DealNews[] }) {
  const [deals] = useState(initialDeals)
  const [searchTerm, setSearchTerm] = useState('')
  // 클라이언트 사이드 필터링
}
```

```tsx
// ❌ 목업: 검색 기능 미흡
<input type="text" placeholder="검색..." />

// ✅ 개선: 실시간 검색 (기업명 + 투자자)
const [searchTerm, setSearchTerm] = useState('')

const filteredDeals = deals.filter((deal) =>
  deal.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
  deal.investors.some((inv) => inv.toLowerCase().includes(searchTerm.toLowerCase()))
)

<div className="relative">
  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
  <input
    type="text"
    placeholder="기업명 또는 투자자 검색..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
  />
</div>
```

```tsx
// ❌ 목업: 통계 계산 로직 없음
<p>총 Deal 수: {deals.length}건</p>

// ✅ 개선: 이번 주 투자 통계 추가
const weekAgo = new Date()
weekAgo.setDate(weekAgo.getDate() - 7)

const thisWeekDeals = filteredDeals.filter((d) => {
  const publishedDate = new Date(d.published_date)
  return publishedDate >= weekAgo
})

<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
  <div className="bg-white rounded-lg shadow-sm p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">총 Deal 수</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">
          {filteredDeals.length}건
        </p>
      </div>
      <TrendingUp className="h-10 w-10 text-red-600" />
    </div>
  </div>

  <div className="bg-white rounded-lg shadow-sm p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">이번 주 투자</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">
          {thisWeekDeals.length}건
        </p>
      </div>
      <Calendar className="h-10 w-10 text-blue-600" />
    </div>
  </div>

  <div className="bg-white rounded-lg shadow-sm p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">참여 기업</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">
          {new Set(filteredDeals.map((d) => d.company_name)).size}개
        </p>
      </div>
      <Building2 className="h-10 w-10 text-green-600" />
    </div>
  </div>
</div>
```

```tsx
// ❌ 목업: 네트워크 집계 로직 복잡
let investorMap = {}
data.forEach(item => {
  item.investors.forEach(investor => {
    if (!investorMap[investor]) investorMap[investor] = []
    investorMap[investor].push(item.company_name)
  })
})

// ✅ 개선: Map 자료구조 사용 (중복 제거)
const investorMap = new Map<string, Set<string>>()

data?.forEach((item) => {
  item.investors.forEach((investor: string) => {
    if (!investorMap.has(investor)) {
      investorMap.set(investor, new Set())
    }
    investorMap.get(investor)!.add(item.company_name)
  })
})

const connectionData: Connection[] = Array.from(investorMap.entries()).map(
  ([investor, companies], index) => ({
    id: `conn-${index}`,
    investor_name: investor,
    company_name: Array.from(companies).join(', '),
    investment_count: companies.size,
  })
)

// 투자 횟수 내림차순 정렬
connectionData.sort((a, b) => b.investment_count - a.investment_count)
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Server Components (초기 데이터 로드)
- Client Components (필터링만)
- Supabase RLS (공개 데이터)

**TypeScript 타입 정의:**
```typescript
// ✅ Deal 뉴스 타입
export interface DealNews {
  id: string
  company_name: string
  investment_stage: string
  investment_amount: string
  investors: string[]
  industry: string
  location?: string
  published_date: string
  article_url: string
  source: string
}

// ✅ 투자자-기업 연결 타입
export interface Connection {
  id: string
  investor_name: string
  company_name: string
  investment_count: number
}

// ✅ 필터 상태 타입
export type FilterStatus = 'all' | '시드' | '프리A' | '시리즈A' | '시리즈B' | '시리즈C' | '브릿지'
export type IndustryFilter = 'all' | 'AI' | '헬스케어' | '핀테크' | '이커머스' | '푸드테크' | '기타'
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase 클라이언트 설정 완료

**S4E2 완료 확인:**
- investment_tracker 테이블에 데이터 존재

---

## 생성 파일 (2개)

### 1. app/deal/page.tsx
**목표:** Deal 뉴스 트래커 페이지

**참고 파일:** `frontend/app/deal.html`

**개선 사항:**
- ✅ 검색 및 필터 (투자 단계 + 업종)
- ✅ 통계 카드 (총 Deal, 이번 주, 참여 기업)
- ✅ Deal 목록 그리드 레이아웃
- ✅ 빈 상태 UI

### 2. app/link/page.tsx
**목표:** 투자 네트워크 페이지

**참고 파일:** `frontend/app/link.html`

**개선 사항:**
- ✅ 투자자-기업 연결 집계 (Map 사용)
- ✅ 투자 횟수 내림차순 정렬
- ✅ 포트폴리오 표시
- ✅ 반응형 디자인

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 구조 분석 완료
- [ ] Deal 뉴스 페이지 구현
- [ ] 검색 및 필터 기능
- [ ] 통계 카드 (3개)
- [ ] Deal 목록 표시
- [ ] 네트워크 페이지 구현
- [ ] 투자자별 포트폴리오

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] Deal 목록 조회 확인
- [ ] 필터링 동작 확인
- [ ] 네트워크 집계 확인
- [ ] 반응형 디자인 확인

### 개선 항목 (Improvement)
- [ ] 보안: XSS 방지, 안전한 링크
- [ ] 성능: Server Components, 페이지네이션
- [ ] 코드 품질: TypeScript strict, 에러 처리
- [ ] UI/UX: 실시간 검색, 통계 카드, 빈 상태 UI

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/deal.html` (2497줄)
- `Valuation_Company/valuation-platform/frontend/app/link.html` (959줄)

**분석 포인트:**
1. Deal 목록 표시는 명확한가?
2. 검색/필터 기능이 있는가? (개선 필요)
3. 통계 카드가 있는가? (개선 필요)
4. 네트워크 집계 로직은? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 초기화
- **S4E2**: News Parser (데이터 수집)

---

## 주의사항

### ⚠️ 목업의 한계

1. **검색 기능 미흡**
   - 기업명 검색만 지원
   - 투자자 검색 추가 필요

2. **통계 계산 없음**
   - 이번 주 투자 통계 없음
   - 참여 기업 수 계산 필요

3. **UX 개선 필요**
   - 빈 상태 UI 부족
   - 로딩 상태 표시 미흡

### 🔒 보안

1. **외부 링크**
   - rel="noopener noreferrer" 필수
   - target="_blank" 사용 시 보안

2. **RLS 정책**
   - investment_tracker 테이블은 공개 읽기
   - 삽입/수정/삭제는 인증 필요

### ⚡ 성능

1. **Server Components**
   - 초기 데이터 로드는 Server Component
   - 필터링만 Client Component

2. **페이지네이션**
   - 최대 100개 제한
   - Infinite scroll 고려

### 📝 코드 품질

1. **실시간 검색**
   - 클라이언트 사이드 필터링
   - 디바운싱 권장 (300ms)

2. **타입 안전성**
   - DealNews 인터페이스
   - 필터 상태 타입

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 2개
**라인 수**: ~420줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
