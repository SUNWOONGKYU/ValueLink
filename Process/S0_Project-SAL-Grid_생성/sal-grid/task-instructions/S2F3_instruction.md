# S2F3: Educational Guide Template & 5 Method Pages (마이그레이션)

## Task 정보

- **Task ID**: S2F3
- **Task Name**: 평가 방법 가이드 템플릿 및 5개 가이드 페이지 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

**Valuation_Company의 HTML 가이드 페이지를 Next.js TSX로 마이그레이션하고 개선**

- 기존 HTML 콘텐츠를 참고하여 TSX로 변환
- 5개 평가 방법(DCF, Relative, Asset, Intrinsic, Tax) 교육 콘텐츠 페이지
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ XSS 방지 (React 자동 이스케이프)
- ✅ 안전한 외부 링크 (rel="noopener noreferrer")

### 2️⃣ 성능 최적화 (Performance)
- ✅ Server Components 사용 (정적 콘텐츠)
- ✅ 이미지 최적화 (Next.js Image)
- ✅ Code Splitting (각 가이드 페이지 분리)
- ✅ 메타데이터 최적화 (SEO)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 재사용 가능한 템플릿 컴포넌트
- ✅ 콘텐츠 구조화 (Markdown or MDX)
- ✅ 접근성 개선 (ARIA, semantic HTML)

### 4️⃣ UI/UX 개선 (User Experience)
- ✅ 반응형 디자인
- ✅ 목차 (TOC) 네비게이션
- ✅ 코드 하이라이팅
- ✅ 다이어그램/차트 추가
- ✅ 프린트 친화적 스타일

---

## 작업 방식

### Step 1: 기존 HTML 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/frontend/app/valuation/guides/
├── guide-dcf.html
├── guide-relative.html
├── guide-asset.html
├── guide-intrinsic.html
└── guide-tax.html
```

**분석 항목:**
1. 각 가이드의 콘텐츠 구조
2. 섹션 구성 (개요, 원리, 입력 요소, 장단점 등)
3. 계산 예시
4. UI/UX 패턴
5. 네비게이션 구조

### Step 2: HTML → TSX 변환

**변환 가이드:**

| HTML | TSX (React) |
|------|-------------|
| `<div class="guide-content">` | `<div className="guide-content">` |
| `<h1>DCF 평가란?</h1>` | `<h1>DCF 평가란?</h1>` (동일, Tailwind Typography 적용) |
| `<a href="/submission">` | `<Link href="/submission">` |
| Static HTML | Server Component (기본값) |

**주의사항:**
- HTML의 `class` → TSX `className`
- HTML의 `<a>` → Next.js `<Link>`
- 정적 콘텐츠는 Server Component로 유지

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```tsx
// ❌ 목업: 정적 HTML (SEO 부족)
<html>
  <head>
    <title>DCF 가이드</title>
  </head>
</html>

// ✅ 개선: Next.js Metadata API (SEO 최적화)
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'DCF (현금흐름할인법) 가이드 | ValueLink',
  description: '기업이 미래에 창출할 현금흐름을 현재가치로 할인하여 기업가치를 평가하는 DCF 방법을 상세히 설명합니다.',
  keywords: ['DCF', '현금흐름할인법', '기업가치평가', 'WACC', '터미널 가치'],
  openGraph: {
    title: 'DCF (현금흐름할인법) 가이드',
    description: 'DCF 평가 방법 완벽 가이드',
    type: 'article',
  },
}
```

```tsx
// ❌ 목업: Typography 스타일 부족
<div>
  <p>텍스트...</p>
</div>

// ✅ 개선: Tailwind Typography 적용
<article className="prose prose-gray max-w-none">
  <h2>DCF 평가란?</h2>
  <p>
    DCF(Discounted Cash Flow, 현금흐름할인법)는 기업이 미래에 창출할
    현금흐름을 현재가치로 할인하여 기업가치를 평가하는 방법입니다.
  </p>
</article>
```

```tsx
// ❌ 목업: 네비게이션 없음
// (단일 페이지)

// ✅ 개선: 사이드바 네비게이션 추가
const methods = [
  { id: 'dcf', name: 'DCF', label: '현금흐름할인법' },
  { id: 'relative', name: 'Relative', label: '상대가치평가' },
  { id: 'asset', name: 'Asset', label: '자산가치평가' },
  { id: 'intrinsic', name: 'Intrinsic', label: '내재가치평가' },
  { id: 'tax', name: 'Tax', label: '세법상평가' },
]

<aside className="w-64">
  <nav>
    {methods.map((m) => (
      <Link
        key={m.id}
        href={`/valuation/guides/${m.id}`}
        className={method === m.id ? 'active' : ''}
      >
        {m.name} - {m.label}
      </Link>
    ))}
  </nav>
</aside>
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Server Components (정적 콘텐츠)
- Metadata API (SEO)
- Static Generation (빠른 로딩)

**TypeScript 타입 안전성:**
```typescript
// ✅ Guide 타입 정의
export type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'

export interface GuideSection {
  title: string
  content: string
}

export interface GuideContent {
  method: ValuationMethod
  title: string
  description: string
  sections: GuideSection[]
  examples: string[]
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Tailwind CSS 설정 완료
- `@tailwindcss/typography` 플러그인 설치

---

## 생성 파일 (6개)

### 1. components/guide-template.tsx
**목표:** 공통 가이드 템플릿 컴포넌트

**참고 파일:** `frontend/app/valuation/guides/*.html`의 공통 구조

**개선 사항:**
- ✅ 재사용 가능한 템플릿
- ✅ 사이드바 네비게이션
- ✅ "평가 신청하기" 버튼
- ✅ 반응형 레이아웃

### 2-6. app/valuation/guides/{method}/page.tsx (5개)
**목표:** 5개 평가 방법별 가이드 페이지

**참고 파일:**
- `guide-dcf.html` → `app/valuation/guides/dcf/page.tsx`
- `guide-relative.html` → `app/valuation/guides/relative/page.tsx`
- 등등...

**개선 사항:**
- ✅ Metadata API (SEO)
- ✅ Tailwind Typography
- ✅ 계산 예시 강화
- ✅ 목차 (TOC) 추가 (권장)

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 HTML 파일 읽고 콘텐츠 분석 완료
- [ ] 공통 가이드 템플릿 구현
- [ ] 5개 평가 방법 가이드 페이지 작성
- [ ] 사이드바 네비게이션 동작
- [ ] "평가 신청하기" 버튼 연결
- [ ] 반응형 디자인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] 각 가이드 페이지 정상 렌더링
- [ ] 사이드바 네비게이션 동작 확인
- [ ] 콘텐츠 가독성 확인

### 개선 항목 (Improvement)
- [ ] 보안: XSS 방지, 안전한 링크
- [ ] 성능: Server Components, 이미지 최적화, SEO
- [ ] 코드 품질: TypeScript strict, 콘텐츠 구조화
- [ ] UI/UX: Typography, 목차, 반응형

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/frontend/app/valuation/guides/guide-dcf.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/guides/guide-relative.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/guides/guide-asset.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/guides/guide-intrinsic.html`
- `Valuation_Company/valuation-platform/frontend/app/valuation/guides/guide-tax.html`

**분석 포인트:**
1. 각 가이드의 섹션 구성은?
2. 계산 예시는 명확한가?
3. 네비게이션 구조는? (개선 필요)
4. SEO는 고려되어 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: Next.js 초기화
- **S2F2**: 평가 신청 폼 (링크 연결)

---

## 주의사항

### ⚠️ 목업의 한계

1. **SEO 부족**
   - 메타데이터 없음
   - Metadata API 필요

2. **Typography 부족**
   - 스타일 일관성 부족
   - Tailwind Typography 필요

3. **네비게이션 부족**
   - 가이드 간 이동 불편
   - 사이드바 추가 필요

### 📝 콘텐츠 품질

1. **명확한 언어**
   - 전문 용어 설명
   - 계산 예시 정확히
   - 문장 간결

2. **SEO 최적화**
   - 메타 태그
   - 제목 계층 구조
   - 키워드 포함

3. **가독성**
   - Typography 스타일
   - 적절한 여백
   - 코드 하이라이팅

---

## 예상 소요 시간

**작업 복잡도**: Low-Medium
**파일 수**: 6개
**라인 수**: ~620줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
