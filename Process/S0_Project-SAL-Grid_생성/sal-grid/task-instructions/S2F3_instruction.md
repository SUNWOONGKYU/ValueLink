# S2F3: Educational Guide Template & 5 Method Pages

## Task 정보

- **Task ID**: S2F3
- **Task Name**: 평가 방법 가이드 템플릿 및 5개 가이드 페이지
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: F (Frontend)
- **Dependencies**: S1BI1 (Next.js 초기화)
- **Task Agent**: frontend-developer
- **Verification Agent**: qa-specialist

---

## Task 목표

5개 평가 방법(DCF, Relative, Asset, Intrinsic, Tax)에 대한 교육 콘텐츠 페이지를 구현하여 사용자가 각 평가 방법을 이해할 수 있도록 함

---

## 상세 지시사항

### 0. 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Tailwind CSS 설정 완료

---

### 1. 공통 가이드 템플릿 컴포넌트

**파일**: `components/guide-template.tsx`

```typescript
'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { ArrowLeft, BookOpen, FileText, Calculator } from 'lucide-react'

interface GuideTemplateProps {
  method: 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
  title: string
  icon: ReactNode
  children: ReactNode
}

export default function GuideTemplate({
  method,
  title,
  icon,
  children,
}: GuideTemplateProps) {
  const methods = [
    { id: 'dcf', name: 'DCF', label: '현금흐름할인법' },
    { id: 'relative', name: 'Relative', label: '상대가치평가' },
    { id: 'asset', name: 'Asset', label: '자산가치평가' },
    { id: 'intrinsic', name: 'Intrinsic', label: '내재가치평가' },
    { id: 'tax', name: 'Tax', label: '세법상평가' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/service-guide"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>가이드 홈</span>
              </Link>
              <div className="border-l pl-4 flex items-center gap-3">
                {icon}
                <div>
                  <h1 className="text-xl font-bold text-gray-900">{title}</h1>
                  <p className="text-sm text-gray-500">평가 방법 가이드</p>
                </div>
              </div>
            </div>
            <Link
              href={`/valuation/submissions/${method}`}
              className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
            >
              평가 신청하기
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* 사이드바 */}
          <aside className="w-64 flex-shrink-0">
            <nav className="bg-white rounded-lg shadow p-4">
              <h2 className="text-sm font-semibold text-gray-900 mb-3">
                평가 방법
              </h2>
              <ul className="space-y-1">
                {methods.map((m) => (
                  <li key={m.id}>
                    <Link
                      href={`/valuation/guides/${m.id}`}
                      className={`block px-3 py-2 rounded text-sm ${
                        m.id === method
                          ? 'bg-red-50 text-red-600 font-medium'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {m.name} - {m.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>

          {/* 메인 콘텐츠 */}
          <main className="flex-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-8">{children}</div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
```

---

### 2. DCF 가이드 페이지

**파일**: `app/valuation/guides/dcf/page.tsx`

```typescript
import GuideTemplate from '@/components/guide-template'
import { TrendingUp } from 'lucide-react'

export default function DCFGuidePage() {
  return (
    <GuideTemplate
      method="dcf"
      title="DCF (현금흐름할인법)"
      icon={<TrendingUp className="w-6 h-6 text-red-600" />}
    >
      <article className="prose prose-gray max-w-none">
        <h2>DCF 평가란?</h2>
        <p>
          DCF(Discounted Cash Flow, 현금흐름할인법)는 기업이 미래에 창출할
          현금흐름을 현재가치로 할인하여 기업가치를 평가하는 방법입니다.
        </p>

        <h2>평가 원리</h2>
        <p>기업가치 = 미래 현금흐름의 현재가치 합</p>
        <ul>
          <li>미래 5년간의 잉여현금흐름(FCF) 예측</li>
          <li>할인율(WACC)을 적용하여 현재가치 계산</li>
          <li>터미널 가치(Terminal Value) 추가</li>
          <li>순부채 차감하여 자기자본가치 산출</li>
        </ul>

        <h2>주요 입력 요소</h2>
        <h3>1. 잉여현금흐름 (FCF)</h3>
        <p>
          FCF = 영업이익 × (1 - 법인세율) + 감가상각비 - 설비투자 -
          운전자본증가액
        </p>

        <h3>2. 할인율 (WACC)</h3>
        <p>
          WACC = (자기자본비용 × 자기자본비중) + (타인자본비용 ×
          타인자본비중)
        </p>

        <h3>3. 영구성장률</h3>
        <p>
          터미널 기간 동안 기업이 지속적으로 성장할 것으로 예상되는 성장률
          (일반적으로 2-3%)
        </p>

        <h2>적용 시점</h2>
        <ul>
          <li>안정적인 현금흐름이 예측 가능한 기업</li>
          <li>성숙기 단계의 기업</li>
          <li>M&A, IPO 등 기업가치 평가가 필요한 시점</li>
        </ul>

        <h2>장점</h2>
        <ul>
          <li>미래 성장성을 반영</li>
          <li>이론적으로 가장 정확한 방법</li>
          <li>국제적으로 널리 인정되는 평가 방법</li>
        </ul>

        <h2>단점</h2>
        <ul>
          <li>미래 예측의 불확실성</li>
          <li>할인율 산정의 어려움</li>
          <li>스타트업처럼 현금흐름이 불안정한 기업에는 부적합</li>
        </ul>

        <h2>계산 예시</h2>
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">가정</h3>
          <ul className="space-y-1 text-sm">
            <li>5년 FCF: 100억, 120억, 144억, 173억, 207억</li>
            <li>WACC: 12%</li>
            <li>영구성장률: 3%</li>
            <li>순부채: 50억</li>
          </ul>

          <h3 className="text-lg font-semibold mt-4 mb-3">계산</h3>
          <ol className="space-y-2 text-sm">
            <li>FCF 현재가치 합: 500억</li>
            <li>터미널 가치: 2,300억</li>
            <li>기업가치: 2,800억</li>
            <li>자기자본가치: 2,750억 (= 2,800억 - 50억)</li>
          </ol>
        </div>
      </article>
    </GuideTemplate>
  )
}
```

---

### 3. 나머지 4개 가이드 페이지

**파일**:
- `app/valuation/guides/relative/page.tsx`
- `app/valuation/guides/asset/page.tsx`
- `app/valuation/guides/intrinsic/page.tsx`
- `app/valuation/guides/tax/page.tsx`

**구조 패턴** (각 페이지마다 동일):
1. 평가 방법 개요
2. 평가 원리
3. 주요 입력 요소
4. 적용 시점
5. 장점 / 단점
6. 계산 예시

**콘텐츠 참조**: 기존 HTML 가이드 파일의 내용을 Markdown 형식으로 변환

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `components/guide-template.tsx` | 공통 가이드 템플릿 | ~120줄 |
| `app/valuation/guides/dcf/page.tsx` | DCF 가이드 | ~100줄 |
| `app/valuation/guides/relative/page.tsx` | Relative 가이드 | ~100줄 |
| `app/valuation/guides/asset/page.tsx` | Asset 가이드 | ~100줄 |
| `app/valuation/guides/intrinsic/page.tsx` | Intrinsic 가이드 | ~100줄 |
| `app/valuation/guides/tax/page.tsx` | Tax 가이드 | ~100줄 |

**총 파일 수**: 6개
**총 라인 수**: ~620줄

---

## 기술 스택

- **Framework**: Next.js 14 (App Router, 정적 페이지)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS + @tailwindcss/typography
- **Icons**: lucide-react

---

## 완료 기준

### 필수 (Must Have)

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

### 권장 (Nice to Have)

- [ ] 목차(TOC) 자동 생성
- [ ] 코드 하이라이팅
- [ ] 다이어그램 추가

---

## 참조

### 기존 프로토타입

- `Valuation_Company/valuation-platform/frontend/app/valuation/guides/guide-dcf.html`

### 관련 Task

- **S1BI1**: Next.js 프로젝트 초기화
- **S2F2**: 평가 신청 폼 (링크 연결)

---

## 주의사항

1. **콘텐츠 품질**
   - 전문 용어 설명 명확히
   - 계산 예시 정확히 작성
   - 문장 간결하고 이해하기 쉽게

2. **SEO 최적화**
   - 메타 태그 추가 (향후)
   - 제목 계층 구조 유지

3. **스타일링**
   - @tailwindcss/typography 플러그인 사용
   - prose 클래스로 Markdown 스타일 자동 적용

---

## 예상 소요 시간

**작업 복잡도**: Low
**파일 수**: 6개
**라인 수**: ~620줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
