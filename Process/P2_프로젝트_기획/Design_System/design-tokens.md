# ValueLink 디자인 시스템

**작성일**: 2026-02-05
**버전**: 1.0
**프로젝트**: ValueLink - AI 기반 기업가치평가 플랫폼

---

## 개요

본 문서는 ValueLink 플랫폼의 **통합 디자인 시스템**을 정의합니다.

### 목적

```
✅ 일관된 사용자 경험 제공
✅ 개발 속도 향상 (재사용 가능한 컴포넌트)
✅ 유지보수 용이성 확보
✅ 브랜드 아이덴티티 강화
```

### 기술 스택

- **CSS Framework**: Tailwind CSS 3.x
- **Font**: Pretendard (한글), Inter (영문)
- **Icons**: Heroicons, Font Awesome
- **Charts**: Chart.js
- **Animation**: CSS Transitions

---

## 1. 컬러 시스템

### 1.1 브랜드 컬러

```css
/* Primary - Red (신뢰감, 전문성) */
--primary-50: #FEF2F2;
--primary-100: #FEE2E2;
--primary-200: #FECACA;
--primary-300: #FCA5A5;
--primary-400: #F87171;
--primary-500: #EF4444;
--primary-600: #DC2626;  /* 메인 */
--primary-700: #B91C1C;
--primary-800: #991B1B;
--primary-900: #7F1D1D;
```

**사용 예시**:
- CTA 버튼: primary-600
- Hover: primary-700
- Active: primary-800

### 1.2 보조 컬러

```css
/* Gray (중립) */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-400: #9CA3AF;
--gray-500: #6B7280;
--gray-600: #4B5563;
--gray-700: #374151;
--gray-800: #1F2937;
--gray-900: #111827;

/* Blue (정보) */
--blue-50: #EFF6FF;
--blue-100: #DBEAFE;
--blue-500: #3B82F6;  /* 정보 표시 */
--blue-600: #2563EB;
--blue-700: #1D4ED8;

/* Green (성공) */
--green-50: #ECFDF5;
--green-100: #D1FAE5;
--green-500: #10B981;  /* 성공 메시지 */
--green-600: #059669;
--green-700: #047857;

/* Yellow (경고) */
--yellow-50: #FFFBEB;
--yellow-100: #FEF3C7;
--yellow-500: #F59E0B;  /* 경고 메시지 */
--yellow-600: #D97706;
--yellow-700: #B45309;

/* Red (에러) */
--red-50: #FEF2F2;
--red-100: #FEE2E2;
--red-500: #EF4444;  /* 에러 메시지 */
--red-600: #DC2626;
--red-700: #B91C1C;
```

### 1.3 상태 컬러

| 상태 | 컬러 | 용도 |
|------|------|------|
| **Success** | green-500 | 작업 완료, 승인 |
| **Warning** | yellow-500 | 주의 필요, 대기 중 |
| **Error** | red-500 | 오류, 거부 |
| **Info** | blue-500 | 정보 안내 |
| **Neutral** | gray-500 | 기본 정보 |

### 1.4 컬러 사용 원칙

**DO ✅**:
- Primary는 CTA 버튼에만 사용
- 상태 컬러는 일관되게 사용
- 텍스트 대비율 최소 4.5:1 유지 (WCAG AA)

**DON'T ❌**:
- Primary를 배경색으로 과도하게 사용 금지
- 여러 상태 컬러를 한 화면에 혼용 금지
- 컬러만으로 정보 전달 금지 (색맹 고려)

---

## 2. 타이포그래피

### 2.1 글꼴 패밀리

```css
/* 한글 */
font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont,
             system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo',
             'Noto Sans KR', 'Malgun Gothic', sans-serif;

/* 영문 & 숫자 */
font-family: 'Inter', 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;

/* 코드 */
font-family: 'Fira Code', 'Courier New', Consolas, Monaco, monospace;
```

**글꼴 로딩**:
```html
<!-- Pretendard -->
<link rel="stylesheet" as="style" crossorigin
      href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" />

<!-- Inter -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### 2.2 글꼴 크기

| Scale | Size | Line Height | 용도 |
|-------|------|-------------|------|
| xs | 12px (0.75rem) | 16px (1rem) | Caption, Label |
| sm | 14px (0.875rem) | 20px (1.25rem) | Body Small, Secondary |
| base | 16px (1rem) | 24px (1.5rem) | Body, Default |
| lg | 18px (1.125rem) | 28px (1.75rem) | Body Large |
| xl | 20px (1.25rem) | 28px (1.75rem) | H5 |
| 2xl | 24px (1.5rem) | 32px (2rem) | H4 |
| 3xl | 30px (1.875rem) | 36px (2.25rem) | H3 |
| 4xl | 36px (2.25rem) | 40px (2.5rem) | H2 |
| 5xl | 48px (3rem) | 1 | H1 |
| 6xl | 60px (3.75rem) | 1 | Display |

### 2.3 글꼴 두께

```css
--font-normal: 400;    /* 본문 */
--font-medium: 500;    /* 강조 */
--font-semibold: 600;  /* 제목 */
--font-bold: 700;      /* 강한 강조 */
```

### 2.4 타이포그래피 스타일

#### Heading

```css
/* H1 - Page Title */
.h1 {
  font-size: 3rem;        /* 48px */
  font-weight: 700;
  line-height: 1;
  color: var(--gray-900);
  letter-spacing: -0.02em;
}

/* H2 - Section Title */
.h2 {
  font-size: 2.25rem;     /* 36px */
  font-weight: 700;
  line-height: 2.5rem;    /* 40px */
  color: var(--gray-900);
  letter-spacing: -0.01em;
}

/* H3 - Subsection Title */
.h3 {
  font-size: 1.875rem;    /* 30px */
  font-weight: 600;
  line-height: 2.25rem;   /* 36px */
  color: var(--gray-900);
}

/* H4 - Card Title */
.h4 {
  font-size: 1.5rem;      /* 24px */
  font-weight: 600;
  line-height: 2rem;      /* 32px */
  color: var(--gray-900);
}
```

#### Body

```css
/* Body - Default */
.body {
  font-size: 1rem;        /* 16px */
  font-weight: 400;
  line-height: 1.5rem;    /* 24px */
  color: var(--gray-700);
}

/* Body Small */
.body-sm {
  font-size: 0.875rem;    /* 14px */
  font-weight: 400;
  line-height: 1.25rem;   /* 20px */
  color: var(--gray-600);
}

/* Body Large */
.body-lg {
  font-size: 1.125rem;    /* 18px */
  font-weight: 400;
  line-height: 1.75rem;   /* 28px */
  color: var(--gray-700);
}
```

#### Label & Caption

```css
/* Label */
.label {
  font-size: 0.875rem;    /* 14px */
  font-weight: 500;
  line-height: 1.25rem;   /* 20px */
  color: var(--gray-700);
}

/* Caption */
.caption {
  font-size: 0.75rem;     /* 12px */
  font-weight: 400;
  line-height: 1rem;      /* 16px */
  color: var(--gray-500);
}
```

---

## 3. 간격 (Spacing)

### 3.1 간격 시스템

```css
/* Tailwind 기본 간격 시스템 사용 */
--spacing-0: 0px;
--spacing-1: 0.25rem;   /* 4px */
--spacing-2: 0.5rem;    /* 8px */
--spacing-3: 0.75rem;   /* 12px */
--spacing-4: 1rem;      /* 16px */
--spacing-5: 1.25rem;   /* 20px */
--spacing-6: 1.5rem;    /* 24px */
--spacing-8: 2rem;      /* 32px */
--spacing-10: 2.5rem;   /* 40px */
--spacing-12: 3rem;     /* 48px */
--spacing-16: 4rem;     /* 64px */
--spacing-20: 5rem;     /* 80px */
--spacing-24: 6rem;     /* 96px */
```

### 3.2 간격 사용 가이드

| 용도 | 간격 | 예시 |
|------|------|------|
| **Component 내부** | 4-12px (1-3) | 버튼 내 텍스트 패딩 |
| **Component 간** | 16-24px (4-6) | 카드 내 요소 간격 |
| **Section 내부** | 32-48px (8-12) | Section 내 그룹 간격 |
| **Section 간** | 64-96px (16-24) | 큰 Section 구분 |

---

## 4. 레이아웃

### 4.1 Grid 시스템

```css
/* 12-column Grid */
.container {
  max-width: 1280px;        /* Desktop */
  margin: 0 auto;
  padding: 0 1rem;          /* 16px */
}

@media (min-width: 640px) {
  .container { padding: 0 2rem; }  /* 32px */
}

@media (min-width: 1024px) {
  .container { padding: 0 4rem; }  /* 64px */
}
```

### 4.2 Breakpoints

| 이름 | 크기 | 용도 |
|------|------|------|
| **sm** | 640px | Mobile Large |
| **md** | 768px | Tablet |
| **lg** | 1024px | Desktop |
| **xl** | 1280px | Desktop Large |
| **2xl** | 1536px | Desktop XL |

### 4.3 레이아웃 패턴

#### Header
```
높이: 64px (Desktop), 56px (Mobile)
배경: White
Border: Bottom 1px Gray-200
그림자: 없음 (스크롤 시 sm 그림자)
```

#### Sidebar
```
너비: 256px (Desktop), Full (Mobile Drawer)
배경: Gray-50
Border: Right 1px Gray-200
```

#### Content Area
```
Max Width: 1280px
Padding: 24px (Mobile), 32px (Tablet), 48px (Desktop)
배경: White 또는 Gray-50
```

#### Footer
```
높이: Auto
배경: Gray-900
텍스트: Gray-300
Padding: 48px (Desktop), 32px (Mobile)
```

---

## 5. 컴포넌트

### 5.1 Buttons

#### Primary Button

```tsx
<button className="
  px-4 py-2
  bg-primary-600 hover:bg-primary-700 active:bg-primary-800
  text-white font-medium text-sm
  rounded-lg
  transition-colors duration-150
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
">
  버튼 텍스트
</button>
```

**크기 변형**:
| Size | Class | Height | Padding |
|------|-------|--------|---------|
| sm | `px-3 py-1.5 text-sm` | 32px | 12px 16px |
| md | `px-4 py-2 text-sm` | 40px | 16px 24px |
| lg | `px-6 py-3 text-base` | 48px | 20px 32px |

#### Secondary Button

```tsx
<button className="
  px-4 py-2
  bg-white hover:bg-gray-50 active:bg-gray-100
  text-gray-700 font-medium text-sm
  border border-gray-300
  rounded-lg
  transition-colors duration-150
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
">
  버튼 텍스트
</button>
```

#### Tertiary Button (Text Only)

```tsx
<button className="
  px-4 py-2
  text-primary-600 hover:text-primary-700 active:text-primary-800
  font-medium text-sm
  rounded-lg
  transition-colors duration-150
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
">
  버튼 텍스트
</button>
```

### 5.2 Cards

```tsx
<div className="
  bg-white
  border border-gray-200
  rounded-lg
  shadow-sm
  p-6
  hover:shadow-md
  transition-shadow duration-200
">
  <h3 className="text-lg font-semibold text-gray-900 mb-2">
    카드 제목
  </h3>
  <p className="text-sm text-gray-600">
    카드 내용
  </p>
</div>
```

**그림자 레벨**:
```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
```

### 5.3 Forms

#### Input

```tsx
<input
  type="text"
  className="
    w-full px-3 py-2
    bg-white
    border border-gray-300
    rounded-lg
    text-sm text-gray-900
    placeholder:text-gray-400
    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
    disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed
  "
  placeholder="입력하세요"
/>
```

#### Label

```tsx
<label className="block text-sm font-medium text-gray-700 mb-1">
  라벨 텍스트
</label>
```

#### Error Message

```tsx
<p className="mt-1 text-sm text-red-600">
  에러 메시지
</p>
```

### 5.4 Tables

```tsx
<table className="min-w-full divide-y divide-gray-200">
  <thead className="bg-gray-50">
    <tr>
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        제목
      </th>
    </tr>
  </thead>
  <tbody className="bg-white divide-y divide-gray-200">
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        데이터
      </td>
    </tr>
  </tbody>
</table>
```

### 5.5 Modals

```tsx
{/* Backdrop */}
<div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-40" />

{/* Modal */}
<div className="fixed inset-0 z-50 flex items-center justify-center p-4">
  <div className="
    bg-white
    rounded-lg
    shadow-xl
    max-w-md w-full
    p-6
  ">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">
      모달 제목
    </h3>
    <p className="text-sm text-gray-600 mb-6">
      모달 내용
    </p>
    <div className="flex justify-end space-x-3">
      <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
        취소
      </button>
      <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">
        확인
      </button>
    </div>
  </div>
</div>
```

### 5.6 Alerts

#### Success

```tsx
<div className="p-4 bg-green-50 border border-green-200 rounded-lg">
  <div className="flex">
    <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
    </svg>
    <div className="ml-3">
      <p className="text-sm font-medium text-green-800">
        성공 메시지
      </p>
    </div>
  </div>
</div>
```

#### Error

```tsx
<div className="p-4 bg-red-50 border border-red-200 rounded-lg">
  <div className="flex">
    <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
    </svg>
    <div className="ml-3">
      <p className="text-sm font-medium text-red-800">
        에러 메시지
      </p>
    </div>
  </div>
</div>
```

### 5.7 Badges

```tsx
{/* Success */}
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
  완료
</span>

{/* Warning */}
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
  대기중
</span>

{/* Error */}
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
  거부
</span>

{/* Neutral */}
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
  진행중
</span>
```

---

## 6. 아이콘

### 6.1 아이콘 시스템

**Heroicons** (Primary):
- 크기: 20px, 24px
- Stroke Width: 2px
- 스타일: Outline (기본), Solid (강조)

**Font Awesome** (보조):
- 크기: 16px, 20px, 24px
- 용도: 소셜 미디어, 특수 아이콘

### 6.2 주요 아이콘

| 용도 | 아이콘 | 크기 |
|------|--------|------|
| Home | `HomeIcon` | 24px |
| User | `UserIcon` | 24px |
| Settings | `CogIcon` | 24px |
| Logout | `ArrowRightOnRectangleIcon` | 20px |
| Add | `PlusIcon` | 20px |
| Edit | `PencilIcon` | 20px |
| Delete | `TrashIcon` | 20px |
| Search | `MagnifyingGlassIcon` | 20px |
| Close | `XMarkIcon` | 24px |
| Check | `CheckIcon` | 20px |

### 6.3 사용 예시

```tsx
import { HomeIcon, UserIcon } from '@heroicons/react/24/outline';

<HomeIcon className="w-6 h-6 text-gray-500" />
<UserIcon className="w-5 h-5 text-primary-600" />
```

---

## 7. 애니메이션

### 7.1 전환 (Transition)

```css
/* 기본 전환 */
.transition-base {
  transition: all 150ms ease-in-out;
}

/* 색상 전환 */
.transition-colors {
  transition: color 150ms ease-in-out,
              background-color 150ms ease-in-out,
              border-color 150ms ease-in-out;
}

/* 그림자 전환 */
.transition-shadow {
  transition: box-shadow 200ms ease-in-out;
}

/* 변형 전환 */
.transition-transform {
  transition: transform 200ms ease-in-out;
}
```

### 7.2 호버 효과

```css
/* 버튼 호버 */
.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

/* 카드 호버 */
.card:hover {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* 링크 호버 */
.link:hover {
  text-decoration: underline;
}
```

### 7.3 로딩 애니메이션

```css
/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

## 8. 반응형 디자인

### 8.1 모바일 우선

```css
/* Mobile First (기본) */
.element {
  font-size: 14px;
  padding: 16px;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .element {
    font-size: 16px;
    padding: 24px;
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .element {
    font-size: 18px;
    padding: 32px;
  }
}
```

### 8.2 반응형 패턴

#### Stack → Columns

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 카드들 */}
</div>
```

#### Hide/Show

```tsx
<div className="hidden md:block">
  {/* Desktop only */}
</div>

<div className="block md:hidden">
  {/* Mobile only */}
</div>
```

---

## 9. 접근성 (Accessibility)

### 9.1 색상 대비

```
WCAG AA 기준 준수:
- 일반 텍스트: 최소 4.5:1
- 큰 텍스트 (18px+): 최소 3:1
- UI 컴포넌트: 최소 3:1
```

### 9.2 키보드 네비게이션

```tsx
{/* Focus 스타일 */}
<button className="focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
  버튼
</button>

{/* Tab 순서 */}
<input tabIndex={1} />
<input tabIndex={2} />
```

### 9.3 스크린 리더

```tsx
{/* aria-label */}
<button aria-label="프로젝트 삭제">
  <TrashIcon className="w-5 h-5" />
</button>

{/* aria-describedby */}
<input
  id="email"
  aria-describedby="email-error"
/>
<p id="email-error" className="text-red-600">
  이메일 형식이 올바르지 않습니다.
</p>
```

---

## 10. 다크 모드 (계획)

### 10.1 컬러 변수

```css
/* Light Mode (기본) */
:root {
  --bg-primary: #FFFFFF;
  --text-primary: #111827;
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1F2937;
    --text-primary: #F9FAFB;
  }
}
```

### 10.2 다크 모드 적용 (Tailwind)

```tsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  콘텐츠
</div>
```

**현재 상태**: 라이트 모드만 지원, 다크 모드는 S4-S5 단계에서 추가 예정

---

## 11. 구현 우선순위

### Phase 1 (S1-S2): 핵심 컴포넌트

1. **Typography** - 폰트, 텍스트 스타일
2. **Colors** - 브랜드 컬러, 상태 컬러
3. **Buttons** - Primary, Secondary, Tertiary
4. **Forms** - Input, Label, Error
5. **Cards** - 기본 카드 레이아웃

### Phase 2 (S3): 플랫폼 컴포넌트

6. **Tables** - 데이터 테이블
7. **Modals** - 다이얼로그
8. **Alerts** - 알림 메시지
9. **Badges** - 상태 뱃지
10. **Progress Bar** - 14 Steps 진행 표시

### Phase 3 (S4): 고급 컴포넌트

11. **Charts** - Chart.js 통합
12. **Tabs** - 탭 네비게이션
13. **Tooltips** - 툴팁
14. **Dropdowns** - 드롭다운 메뉴
15. **Pagination** - 페이지네이션

---

## 12. Tailwind CSS 설정

### 12.1 tailwind.config.js

```javascript
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
      },
      fontFamily: {
        sans: ['Pretendard Variable', 'Pretendard', 'Inter', 'sans-serif'],
        mono: ['Fira Code', 'Courier New', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

---

## 요약

```
✅ 컬러 시스템 정의 (Brand, Status, Semantic)
✅ 타이포그래피 스케일 (12px ~ 60px)
✅ 간격 시스템 (4px ~ 96px)
✅ 12개 핵심 컴포넌트 스타일 정의
✅ 반응형 Breakpoints (sm, md, lg, xl, 2xl)
✅ 접근성 가이드라인 (WCAG AA)
✅ 애니메이션 & 전환 효과
✅ Tailwind CSS 설정 완료
```

**다음 단계**: P2 나머지 문서 작성 → P3 프로토타입 정리

**작성자**: Claude Code
**참조**: 기존 72개 HTML 페이지, Tailwind CSS 문서
**버전**: 1.0
**작성일**: 2026-02-05
