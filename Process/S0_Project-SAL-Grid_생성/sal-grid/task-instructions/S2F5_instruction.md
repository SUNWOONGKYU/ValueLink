# S2F5: Process Step Template & 12 Workflow Pages (마이그레이션)

## Task 정보

- **Task ID**: S2F5
- **Task Name**: 프로세스 단계 템플릿 및 12개 워크플로우 페이지 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화), S2BA1 (14단계 워크플로우 API)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

**Valuation_Company의 HTML 워크플로우 페이지를 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 콘텐츠를 참고하여 TSX로 변환
- 14단계 평가 워크플로우 중 12개 주요 단계 페이지 구현
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ 단계 순서 검증 (이전 단계 완료 확인)
- ✅ 본인 프로젝트만 접근 (RLS)
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ 안전한 외부 링크 (rel="noopener noreferrer")

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 사용 (정적 템플릿)
- ✅ Client Components 최소화 (동적 상태만)
- ✅ Static Generation (가능한 페이지)
- ✅ 이미지 최적화 (Next.js Image)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 재사용 가능한 템플릿 컴포넌트
- ✅ 에러 핸들링 강화
- ✅ 접근성 개선 (ARIA, semantic HTML)

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 반응형 디자인
- ✅ 진행 상황 사이드바 (14단계 시각화)
- ✅ 다음 단계 안내 명확화
- ✅ 계좌번호 복사 기능 (무통장 입금)

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/valuation/
├── evaluation-progress.html
├── deposit-payment.html
└── (기타 워크플로우 HTML 파일)
```

**분석 항목:**
1. 각 단계별 콘텐츠 구조
2. 진행 상황 표시 방식
3. 다음 단계 액션 버튼
4. 무통장 입금 계좌 정보
5. UI/UX 패턴

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="process-step">` | `<div className="process-step">` |
| `<a href="/valuation/step6">` | `<Link href="/valuation/step6">` |
| `<button onclick="copyAccount()">` | `<button onClick={handleCopy}>` |
| Static HTML | Server Component (템플릿) + Client Component (상태) |

**주의사항:**
- HTML의 `class` → TSX `className`
- HTML의 inline 이벤트 → TSX props
- 진행 상황은 동적 데이터 (Client Component)

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: 단계 순서 검증 없음 (건너뛰기 가능)
<Link href="/valuation/step10?project_id=...">다음 단계</Link>

// ✅ 개선: 단계 순서 검증
const { data: project } = await supabase
  .from('projects')
  .select('current_step')
  .eq('project_id', projectId)
  .single()

if (project.current_step < 9) {
  // 이전 단계 미완료
  return (
    <div className="bg-yellow-50 p-4 rounded-lg">
      <p className="text-yellow-800">
        이전 단계를 먼저 완료해주세요.
      </p>
    </div>
  )
}

// 다음 단계 버튼 활성화
<button
  disabled={project.current_step !== 9}
  onClick={handleNextStep}
  className="..."
>
  다음 단계로
</button>
```

```tsx
// ❌ 목업: 정적 진행 상황 (하드코딩)
<div className="step completed">Step 1: 프로젝트 생성</div>
<div className="step completed">Step 2: 견적 요청</div>
<div className="step current">Step 3: 협상</div>

// ✅ 개선: 동적 진행 상황 (current_step 기반)
const steps: Step[] = [
  { number: 1, title: '프로젝트 생성', status: 'completed' },
  { number: 2, title: '견적 요청', status: 'completed' },
  { number: 3, title: '협상', status: 'completed' },
  // ...
]

const updatedSteps = steps.map((step) => ({
  ...step,
  status:
    step.number < currentStep
      ? 'completed'
      : step.number === currentStep
      ? 'current'
      : 'upcoming',
}))
```

```tsx
// ❌ 목업: 계좌번호 복사 기능 없음
<p>계좌번호: 1005-404-483025</p>

// ✅ 개선: 클립보드 복사 기능
const [copied, setCopied] = useState(false)

const handleCopyAccountNumber = () => {
  navigator.clipboard.writeText('1005-404-483025')
  setCopied(true)
  setTimeout(() => setCopied(false), 2000)
}

<div className="flex items-center gap-2">
  <span className="text-lg font-semibold text-blue-900">
    1005-404-483025
  </span>
  <button
    onClick={handleCopyAccountNumber}
    className="px-3 py-1 text-sm text-blue-700 bg-blue-100 rounded hover:bg-blue-200 flex items-center gap-1"
  >
    {copied ? (
      <>
        <CheckCircle className="w-4 h-4" />
        <span>복사됨</span>
      </>
    ) : (
      <>
        <Copy className="w-4 h-4" />
        <span>복사</span>
      </>
    )}
  </button>
</div>
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Server Components (정적 템플릿)
- Client Components (동적 상태)
- SearchParams (project_id 전달)

**TypeScript 타입 안전성:**
```typescript
// ✅ 단계 타입 정의
export interface Step {
  number: number
  title: string
  status: 'completed' | 'current' | 'upcoming'
}

export interface ProcessStepTemplateProps {
  projectId: string
  projectName: string
  currentStep: number
  totalSteps: number
  stepTitle: string
  children: ReactNode
}

// ✅ 프로젝트 정보
export interface Project {
  project_id: string
  project_name: string
  current_step: number
  status: string
  valuation_method: string
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨

**S2BA1 완료 확인 (선택적):**
- 워크플로우 API는 동시 개발 가능
- API 없이도 UI 먼저 구현 가능

---

## 생성 파일 (13개)

### 1. components/process-step-template.tsx
**목표:** 공통 프로세스 템플릿

**참고 파일:** `frontend/app/valuation/*.html`의 공통 구조

**개선 사항:**
- ✅ 재사용 가능한 템플릿
- ✅ 진행 상황 사이드바 (14단계 시각화)
- ✅ 반응형 레이아웃

### 2-13. app/valuation/{step}/page.tsx (12개)
**목표:** 12개 워크플로우 페이지

**참고 파일:**
- `evaluation-progress.html` → `app/valuation/evaluation-progress/page.tsx`
- `deposit-payment.html` → `app/valuation/deposit-payment/page.tsx`
- (기타 단계별 HTML 존재 시 참조)

**개선 사항:**
- ✅ 각 단계별 상태 표시
- ✅ 다음 단계 액션 버튼
- ✅ 단계 순서 검증
- ✅ 로딩/에러 상태

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 구조 분석 완료
- [ ] 프로세스 템플릿 컴포넌트 구현
- [ ] 12개 워크플로우 페이지 구현
- [ ] 진행 상황 사이드바 동작
- [ ] 무통장 입금 페이지 (계좌정보 표시)
- [ ] 반응형 디자인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 페이지 정상 렌더링
- [ ] 계좌번호 복사 기능 동작
- [ ] 단계 순서 검증 확인

### 개선 항목 (Improvement)
- [ ] 보안: 단계 순서 검증, RLS
- [ ] 성능: Server Components, Static Generation
- [ ] 코드 품질: TypeScript strict, 재사용 템플릿
- [ ] UI/UX: 진행 상황 시각화, 계좌 복사

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/valuation/evaluation-progress.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/deposit-payment.html`
- (기타 워크플로우 HTML 파일)

**분석 포인트:**
1. 각 단계별 콘텐츠는 명확한가?
2. 진행 상황 표시는 어떻게 되어 있는가?
3. 단계 순서 검증이 있는가? (개선 필요)
4. 계좌번호 복사 기능이 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 초기화
- **S2BA1**: 14단계 워크플로우 API

---

## 주의사항

### ⚠️ 목업의 한계

1. **단계 순서 검증 없음**
   - 건너뛰기 가능
   - 이전 단계 완료 확인 필요

2. **UX 개선 필요**
   - 계좌번호 복사 기능 없음
   - 다음 단계 안내 미흡

3. **성능 최적화 부족**
   - Client-side only
   - Server Components 미활용

### 🔒 보안

1. **무통장 입금 정보**
   - 계좌번호: 1005-404-483025 (우리은행)
   - 예금주: 호수회계법인
   - Stripe 결제 영원히 제외

2. **프로세스 흐름**
   - 단계 순서 엄격히 준수
   - 이전 단계 완료 전 다음 단계 진입 불가

### ⚡ 성능

1. **Server Components**
   - 정적 템플릿은 Server Component
   - 동적 상태만 Client Component

2. **Static Generation**
   - 가능한 페이지는 Static
   - project_id는 SearchParams

### 📝 코드 품질

1. **재사용성**
   - ProcessStepTemplate 컴포넌트
   - 단계별 상태 관리 통일

2. **타입 안전성**
   - Step 인터페이스
   - Project 타입 정의

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 13개
**라인 수**: ~2,000줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
