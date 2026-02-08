# S2F2: Valuation Submission Forms Template & 5 Method Pages (마이그레이션)

## Task 정보

- **Task ID**: S2F2
- **Task Name**: 평가 신청 폼 템플릿 및 5개 방법별 페이지 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2F1 (결과 페이지 타입 정의)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

**Valuation_Company의 HTML 평가 신청 폼을 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 로직을 참고하여 TSX로 변환
- 5개 평가 방법(DCF, Relative, Asset, Intrinsic, Tax)별 신청 폼 구현
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ CSRF 방지 (Supabase 자동 처리)
- ✅ 입력 검증 (클라이언트 + 서버)
- ✅ SQL Injection 방지 (Supabase 파라미터화 쿼리)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 우선 사용
- ✅ Client Components 최소화
- ✅ Code Splitting (동적 import)
- ✅ 이미지 최적화 (Next.js Image)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 재사용 가능한 컴포넌트 (FormField, FormTemplate)
- ✅ 에러 핸들링 강화
- ✅ 접근성 개선 (ARIA 속성)

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 반응형 디자인 (모바일 최적화)
- ✅ 실시간 폼 유효성 검사
- ✅ 로딩 상태 표시
- ✅ 에러 메시지 명확화
- ✅ 키보드 네비게이션

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/valuation/submissions/
├── dcf-submission.html
├── relative-submission.html
├── asset-submission.html
├── intrinsic-submission.html
└── tax-submission.html
```

**분석 항목:**
1. 각 평가 방법별 입력 필드
2. 폼 유효성 검사 로직
3. 제출 처리 방식
4. 에러 표시 방식
5. UI/UX 패턴

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="container">` | `<div className="container">` |
| `<input type="text" value="..." onchange="handleChange()">` | `<input value={value} onChange={handleChange} />` |
| `document.getElementById('form')` | `useRef()` Hook |
| `<script>function submit() {...}</script>` | `const handleSubmit = async (e: FormEvent) => {...}` |
| `fetch('/api/projects', {method: 'POST'})` | `await supabase.from('projects').insert(...)` |

**주의사항:**
- HTML의 `class` → TSX `className`
- HTML의 inline 이벤트 → TSX props
- HTML의 global `<script>` → TSX component logic

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: Client Component로 데이터 페칭 (느림)
'use client'
export default function DCFPage() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/api/dcf-data').then(r => r.json()).then(setData)
  }, [])
}

// ✅ 개선: Server Component로 데이터 페칭 (빠름)
import { createServerClient } from '@/lib/supabase/server'

export default async function DCFPage({ searchParams }: { searchParams: { project_id?: string } }) {
  const supabase = createServerClient()
  const { data } = await supabase
    .from('projects')
    .select('*')
    .eq('project_id', searchParams.project_id)
    .single()

  return <DCFForm initialData={data} />
}
```

```tsx
// ❌ 목업: 폼 유효성 검사 없음
<input type="number" />

// ✅ 개선: 실시간 유효성 검사
const [revenue, setRevenue] = useState<number>(0)
const [error, setError] = useState<string>('')

const handleRevenueChange = (value: string) => {
  const num = parseFloat(value)

  if (isNaN(num)) {
    setError('숫자를 입력해주세요')
    return
  }

  if (num < 0) {
    setError('양수를 입력해주세요')
    return
  }

  setError('')
  setRevenue(num)
}

<FormField
  label="매출"
  type="number"
  value={revenue}
  onChange={(e) => handleRevenueChange(e.target.value)}
  error={error}
  required
/>
```

```tsx
// ❌ 목업: 접근성 부족
<input type="text" placeholder="프로젝트명" />

// ✅ 개선: 접근성 개선 (ARIA 속성)
<label htmlFor="project-name" className="sr-only">프로젝트명</label>
<input
  id="project-name"
  type="text"
  placeholder="프로젝트명"
  aria-label="프로젝트명"
  aria-required="true"
  aria-invalid={!!error}
  aria-describedby={error ? 'project-name-error' : undefined}
/>
{error && (
  <p id="project-name-error" role="alert" className="text-red-600">
    {error}
  </p>
)}
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Server Components 우선
- Client Components ('use client') 최소화
- Server Actions 사용 (필요 시)

**TypeScript 타입 안전성:**
```typescript
// ✅ 강력한 타입 정의
export interface DCFFormData {
  project_name: string
  company_name: string
  industry: string
  valuation_method: 'dcf'
  revenue_5years: [number, number, number, number, number]
  operating_margin: number // 0~1 범위
  tax_rate: number // 0~1 범위
  wacc: number // 0~1 범위
  terminal_growth_rate: number // 0~1 범위
  net_debt: number
  shares_outstanding: number
}

// ✅ Validation 함수
function validateDCFForm(data: DCFFormData): string[] {
  const errors: string[] = []

  if (!data.project_name) errors.push('프로젝트명은 필수입니다')
  if (data.revenue_5years.some(r => r < 0)) errors.push('매출은 양수여야 합니다')
  if (data.operating_margin < 0 || data.operating_margin > 1) {
    errors.push('영업이익률은 0~1 사이여야 합니다')
  }

  return errors
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase 클라이언트 설정 완료

**S2F1 완료 확인:**
- `types/valuation.ts` 파일 존재 (타입 재사용)

---

## 생성 파일 (8개)

### 1. types/valuation-forms.ts
**목표:** 폼 입력 타입 정의 (5개 방법)

**개선 사항:**
- ✅ Union 타입 사용
- ✅ 범위 제한 (0~1 등)
- ✅ 필수/선택 필드 구분

### 2. components/submission-form-template.tsx
**목표:** 공통 폼 템플릿 컴포넌트

**참고 파일:** `frontend/app/valuation/submissions/*.html`의 공통 구조

**개선 사항:**
- ✅ 재사용 가능한 템플릿
- ✅ 프로그레스 표시
- ✅ 임시저장 기능

### 3. components/form-field.tsx
**목표:** 재사용 가능한 폼 필드

**개선 사항:**
- ✅ 에러 메시지 표시
- ✅ 도움말 텍스트
- ✅ 접근성 (ARIA)

### 4-8. app/valuation/submissions/{method}/page.tsx (5개)
**목표:** 5개 평가 방법별 신청 폼 페이지

**참고 파일:**
- `dcf-submission.html` → `app/valuation/submissions/dcf/page.tsx`
- `relative-submission.html` → `app/valuation/submissions/relative/page.tsx`
- 등등...

**개선 사항:**
- ✅ 각 방법별 입력 필드
- ✅ 실시간 유효성 검사
- ✅ 제출 전 확인
- ✅ 로딩/에러 상태

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 구조 분석 완료
- [ ] 공통 템플릿 및 FormField 컴포넌트 구현
- [ ] 5개 평가 방법별 신청 폼 구현
- [ ] Supabase에 프로젝트 생성 기능
- [ ] 폼 유효성 검사 (필수 필드)
- [ ] 반응형 디자인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 폼에서 데이터 입력 가능
- [ ] Supabase에 프로젝트 정상 생성
- [ ] 제출 후 프로젝트 상세 페이지 이동

### 개선 항목 (Improvement)
- [ ] 보안: XSS 방지, CSRF 방지, 입력 검증
- [ ] 성능: Server Components, Code Splitting
- [ ] 코드 품질: TypeScript strict, 재사용 컴포넌트
- [ ] UI/UX: 실시간 검증, 접근성, 반응형

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/dcf-submission.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/relative-submission.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/asset-submission.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/intrinsic-submission.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/submissions/tax-submission.html`

**분석 포인트:**
1. 각 평가 방법별 입력 필드는 무엇인가?
2. 폼 유효성 검사는 어떻게 되어 있는가? (개선 필요)
3. UI 패턴은 일관성이 있는가?
4. 접근성은 고려되어 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 프로젝트 초기화
- **S1D1**: projects, documents 테이블
- **S2F1**: 결과 페이지 타입 정의
- **S2BA2**: Projects API

---

## 주의사항

### ⚠️ 목업의 한계

1. **폼 유효성 검사 부족**
   - 실시간 검증 없음
   - 에러 메시지 불명확

2. **접근성 부족**
   - ARIA 속성 없음
   - 키보드 네비게이션 미흡

3. **Client-side만 사용**
   - Server Components 미활용
   - 성능 최적화 부족

### 🔒 보안

1. **XSS 방지**
   - React 자동 이스케이프 활용
   - dangerouslySetInnerHTML 금지

2. **입력 검증**
   - 클라이언트 검증 + 서버 검증
   - 숫자 범위 체크

### ⚡ 성능

1. **Server Components**
   - 정적 데이터는 Server Component
   - 동적 데이터만 Client Component

2. **Code Splitting**
   - 각 방법별 페이지 분리
   - 동적 import 활용

### 📝 코드 품질

1. **재사용성**
   - FormField 컴포넌트 재사용
   - FormTemplate 컴포넌트 재사용

2. **타입 안전성**
   - 각 방법별 타입 정의
   - Union 타입 활용

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 8개
**라인 수**: ~1,440줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
