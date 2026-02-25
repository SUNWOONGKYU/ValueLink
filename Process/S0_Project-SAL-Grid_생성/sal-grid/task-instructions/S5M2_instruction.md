# S5M2: Code Quality & Readability Enhancement

## Task 정보
- **Task ID**: S5M2
- **Task Name**: 코드 품질 및 가독성 향상
- **Stage**: S5 (Finalization - 개발 마무리)
- **Area**: M (Documentation)
- **Dependencies**: S5M1

## Task 목표

코드 주석, 변수명, 사용자 가이드, 샘플 데이터를 개선하여 코드 품질과 가독성을 향상시킵니다.

**개선 목표:**
- 기술적 정확성 +1점 (18 → 19)
- 가독성 +1점 (18 → 19)
- 구조 및 구성 +1점 (18 → 19)
- 유용성 +1점 (19 → 19, 유지)

**총 +3점** (88점 → 91점 기여)

---

## 생성/수정 파일

| 파일 | 변경 내용 | 저장 위치 |
|------|----------|----------|
| `code-style-guide.md` | 코드 스타일 가이드 문서 | `Process/S5_개발_마무리/Documentation/docs/code-style-guide.md` |
| `user-guide-enhanced.md` | 향상된 사용자 가이드 (단계별 도움말) | `Process/S5_개발_마무리/Documentation/docs/user-guide-enhanced.md` |
| `sample-datasets.md` | 샘플 데이터 세트 (실전 예시) | `Process/S5_개발_마무리/Documentation/docs/sample-datasets.md` |

**Pre-commit Hook 자동 복사:**
- `code-style-guide.md` → `docs/code-style-guide.md`
- `user-guide-enhanced.md` → `docs/user-guide-enhanced.md`
- `sample-datasets.md` → `docs/sample-datasets.md`

---

## 개선 항목 상세

### 1. 코드 스타일 가이드 (기술 +1점, 가독성 +1점) ⭐

**목표:**
- 코드 주석 규칙 정의
- 변수명 규칙 정의
- 파일 구조 규칙 정의

**파일:** `docs/code-style-guide.md`

**내용 구조:**
```markdown
# ValueLink 코드 스타일 가이드

## 1. 파일 헤더 주석

모든 파일은 Task ID와 설명을 포함해야 합니다.

```typescript
/**
 * @task S2BA1
 * @description 프로젝트 생성 API - 14단계 워크플로우 Step 1
 *
 * @endpoint POST /api/projects
 * @auth Required
 * @role customer, admin
 */

'use client'

import { ... } from ...
```

## 2. 변수명 규칙

### 2.1 camelCase (변수, 함수)
```typescript
// ✅ Good
const projectId = 'VL-20260223-0001'
const evaluationRequest = await fetchRequest()
function calculateDCF(params: DCFParams) { ... }

// ❌ Bad
const project_id = 'VL-20260223-0001' // snake_case 금지
const EvaluationRequest = ... // PascalCase 금지 (클래스 아님)
function CalculateDCF(...) { ... } // PascalCase 금지
```

### 2.2 PascalCase (컴포넌트, 클래스, 타입)
```typescript
// ✅ Good
interface DCFParams { ... }
class ValuationEngine { ... }
function ProjectCard() { ... } // React 컴포넌트

// ❌ Bad
interface dcfParams { ... }
class valuationEngine { ... }
function projectCard() { ... }
```

### 2.3 UPPER_SNAKE_CASE (상수)
```typescript
// ✅ Good
const MAX_RETRIES = 3
const API_TIMEOUT_MS = 5000
const DEFAULT_WACC = 0.12

// ❌ Bad
const maxRetries = 3
const MaxRetries = 3
```

### 2.4 의미 있는 변수명
```typescript
// ✅ Good
const discountedCashFlows = years.map(y => y.fcf / Math.pow(1 + wacc, y.year))
const enterpriseValue = terminalValue + dcfSum
const equityValue = enterpriseValue + cash - debt

// ❌ Bad
const dcf = years.map(y => y.fcf / Math.pow(1 + w, y.y)) // w, y.y 불명확
const ev = tv + ds // 약어 금지
const val = ev + c - d // 의미 불명
```

## 3. 함수 주석

### 3.1 복잡한 로직에만 주석 추가
```typescript
// ✅ Good - 복잡한 계산 로직에 주석
/**
 * DCF 평가 엔진 실행
 *
 * @param revenue - 현재 연간 매출 (원)
 * @param growthRate - 연평균 성장률 (0.1 = 10%)
 * @param wacc - 가중평균자본비용 (0.12 = 12%)
 * @returns 기업가치 (enterprise_value, equity_value)
 */
async function calculateDCF(revenue: number, growthRate: number, wacc: number) {
  // 5년 FCF 예측
  const fcfProjections = projectFCF(revenue, growthRate, margin)

  // Terminal Value 계산 (Gordon Growth Model)
  const terminalValue = fcfProjections[4] * (1 + PERPETUAL_GROWTH) / (wacc - PERPETUAL_GROWTH)

  // DCF 합계 (현재가치 할인)
  const dcfSum = fcfProjections.reduce((sum, fcf, year) =>
    sum + fcf / Math.pow(1 + wacc, year + 1), 0
  )

  const enterpriseValue = dcfSum + terminalValue / Math.pow(1 + wacc, 5)
  const equityValue = enterpriseValue + cash - debt

  return { enterpriseValue, equityValue }
}

// ❌ Bad - 자명한 코드에 불필요한 주석
// 프로젝트 ID를 가져옴
const projectId = req.params.id // 주석 불필요

// 사용자 이름을 출력함
console.log(user.name) // 주석 불필요
```

### 3.2 JSDoc 형식 (API, 공개 함수)
```typescript
/**
 * 프로젝트 생성 API
 *
 * @param req - Request 객체 (body: { project_name, company_name_kr, ... })
 * @returns Response 객체 (project_id, created_at)
 *
 * @throws {ValidationError} - 필수 필드 누락 시
 * @throws {DatabaseError} - DB 저장 실패 시
 *
 * @example
 * POST /api/projects
 * {
 *   "project_name": "ABC 기업 평가",
 *   "company_name_kr": "ABC 주식회사",
 *   "valuation_method": "dcf"
 * }
 */
export async function POST(req: Request) { ... }
```

## 4. 파일 구조 규칙

### 4.1 import 순서
```typescript
// 1. React/Next.js
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// 2. 외부 라이브러리
import { createClient } from '@supabase/supabase-js'

// 3. 내부 라이브러리 (@/ alias)
import { calculateDCF } from '@/lib/valuation/dcf-engine'
import { Toast } from '@/app/components/ui/toast'

// 4. 타입
import type { DCFParams, ValuationResult } from '@/types/valuation'

// 5. 스타일 (마지막)
import './styles.css'
```

### 4.2 파일 내 순서
```typescript
// 1. 파일 헤더 주석
/**
 * @task S2BA1
 * @description ...
 */

// 2. Directive ('use client', 'use server')
'use client'

// 3. import 문
import ...

// 4. 상수 정의
const MAX_RETRIES = 3

// 5. 타입 정의
interface Props { ... }

// 6. Helper 함수
function calculateWACC(...) { ... }

// 7. Main 함수/컴포넌트
export default function Page() { ... }
```

## 5. TypeScript 타입 규칙

### 5.1 any 금지
```typescript
// ❌ Bad
function processData(data: any) { ... }

// ✅ Good
function processData(data: ValuationData) { ... }
function processData(data: unknown) { ... } // 타입 불명 시
```

### 5.2 명시적 타입 선언
```typescript
// ✅ Good
const revenue: number = 1000000000
const projects: Project[] = await fetchProjects()

// ❌ Bad (타입 추론에만 의존)
const revenue = 1000000000 // number로 추론되지만 명시적 선언 권장
const projects = await fetchProjects() // 반환 타입 불명확
```

## 6. 에러 처리 규칙

### 6.1 try-catch 필수 (async 함수)
```typescript
// ✅ Good
async function fetchProject(id: string) {
  try {
    const { data, error } = await supabase.from('projects').select('*').eq('project_id', id).single()
    if (error) throw error
    return data
  } catch (error) {
    const apiError = handleAPIError(error)
    throw apiError
  }
}

// ❌ Bad
async function fetchProject(id: string) {
  const { data } = await supabase.from('projects').select('*').eq('project_id', id).single()
  return data // 에러 처리 없음
}
```

---

## 2. 향상된 사용자 가이드 (구조 +1점, 유용성 +1점) ⭐

**목표:**
- 14단계 워크플로우 각 단계별 도움말 제공
- 스크린샷/다이어그램 추가
- 자주 묻는 질문 (FAQ) 추가

**파일:** `docs/user-guide-enhanced.md`

**내용 구조:**
```markdown
# ValueLink 사용자 가이드 (Enhanced)

## 1. 14단계 워크플로우 상세 가이드

### Step 1: 평가 의뢰 생성
**목적**: 고객이 평가를 요청합니다.

**필수 정보**:
- 프로젝트명 (예: "ABC 기업 DCF 평가")
- 회사명 (한글) (예: "ABC 주식회사")
- 평가 방법 (DCF, Relative, Asset, Intrinsic, Tax 중 선택)
- 산업 분류 (예: "제조업 - 반도체")

**화면 예시**:
```
┌─────────────────────────────────────┐
│  프로젝트 생성                        │
├─────────────────────────────────────┤
│  프로젝트명: [ABC 기업 DCF 평가     ]│
│  회사명: [ABC 주식회사              ]│
│  평가 방법: [DCF ▼]                 │
│  산업 분류: [제조업 - 반도체 ▼]     │
│                                     │
│  [ 견적 요청 ]                       │
└─────────────────────────────────────┘
```

**다음 단계**: Step 2 (견적 제시)

---

### Step 2: 견적 제시
**목적**: 회계사가 평가 비용을 제시합니다.

**견적 산출 기준**:
- 기본 요율: 500만원
- 평가 방법별 가중치: DCF (1.5x), Relative (1.0x), Asset (1.2x)
- 산업별 가중치: 제조업 (1.2x), IT (1.3x)
- 회사 규모별 가중치: 매출 100억 미만 (1.0x), 100-500억 (1.5x)

**예시 계산**:
```
기본 요율: 500만원
평가 방법: DCF (1.5x)
산업: 제조업 (1.2x)
매출: 150억 (1.5x)

총 견적: 500만원 × 1.5 × 1.2 × 1.5 = 1,350만원
```

**화면 예시**:
```
┌─────────────────────────────────────┐
│  견적서                              │
├─────────────────────────────────────┤
│  프로젝트: ABC 기업 DCF 평가          │
│  평가 방법: DCF                      │
│                                     │
│  기본 요율:      500만원             │
│  평가 방법 (1.5x): +250만원         │
│  산업 (1.2x):    +100만원           │
│  규모 (1.5x):    +500만원           │
│  ─────────────────────────          │
│  총 견적:      1,350만원             │
│                                     │
│  [ 견적 수락 ]  [ 견적 거부 ]         │
└─────────────────────────────────────┘
```

---

### Step 3-14: (동일 형식으로 각 단계 상세 설명)
...

---

## 2. 자주 묻는 질문 (FAQ)

### Q1: 평가 방법을 어떻게 선택해야 하나요?
**A**: 회사 상황에 따라 다릅니다.

| 평가 방법 | 적합한 경우 | 예시 |
|----------|------------|------|
| DCF | 안정적 현금흐름, 성장 기업 | IT 스타트업, 제조업 |
| Relative | 비슷한 회사 많음 | 음식점, 프랜차이즈 |
| Asset | 자산 가치 중심 | 부동산, 금융 |
| Intrinsic | ROE 중시 | 은행, 보험 |
| Tax | 세무 목적 | 상속, 증여 |

### Q2: 평가 기간은 얼마나 걸리나요?
**A**: 평균 2-3주 소요됩니다.

- Step 1-3 (의뢰~협상): 3일
- Step 4-7 (문서 수집): 7일
- Step 8-10 (평가 진행): 7일
- Step 11-14 (보고서): 3일

### Q3: 필요한 재무 자료는 무엇인가요?
**A**: 평가 방법별로 다릅니다.

**DCF 평가:**
- 최근 3개년 재무제표 (손익계산서, 재무상태표, 현금흐름표)
- 사업 계획서 (향후 5년)
- 산업 보고서

**Relative 평가:**
- 최근 1개년 재무제표
- 비교 가능한 회사 목록

...

---

## 3. 문제 해결 가이드

### 문제 1: "견적이 너무 높아요"
**해결 방법**:
1. 평가 방법 재검토 (DCF → Relative로 변경 시 30% 절감)
2. 평가 범위 축소 (일부 자회사 제외)
3. 분할 납부 협의

### 문제 2: "문서를 어디에 업로드하나요?"
**해결 방법**:
1. Step 4 (문서 수집) 진입
2. "문서 업로드" 버튼 클릭
3. 파일 선택 (PDF, Excel, Word)
4. 문서 종류 선택 (재무제표, 사업계획서 등)

...
```

---

## 3. 샘플 데이터 세트 (유용성 +1점) ⭐

**목표:**
- 3개 산업별 샘플 데이터 제공
- DCF 계산 과정 단계별 설명
- 실전 사용 가능한 템플릿

**파일:** `docs/sample-datasets.md`

**내용 구조:**
```markdown
# 샘플 데이터 세트

## 1. IT 스타트업 (DCF 평가)

### 회사 정보
- **회사명**: 테크이노 주식회사
- **산업**: IT - 인공지능
- **설립일**: 2021년 3월
- **매출**: 50억원 (2025년)
- **성장률**: 연 30%
- **직원수**: 50명

### 재무 데이터
```json
{
  "revenue_current": 5000000000,
  "cogs_ratio": 0.4,
  "opex_ratio": 0.3,
  "tax_rate": 0.22,
  "capex_ratio": 0.1,
  "nwc_change_ratio": 0.05,
  "growth_rate": 0.3,
  "wacc": 0.15,
  "perpetual_growth": 0.03,
  "cash": 1000000000,
  "debt": 500000000
}
```

### DCF 계산 과정

#### Step 1: 5년 매출 예측
```
Year 1: 50억 × (1 + 0.3) = 65억
Year 2: 65억 × (1 + 0.3) = 84.5억
Year 3: 84.5억 × (1 + 0.3) = 109.85억
Year 4: 109.85억 × (1 + 0.3) = 142.8억
Year 5: 142.8억 × (1 + 0.3) = 185.64억
```

#### Step 2: FCF 계산
```
Year 1 FCF:
  매출: 65억
  COGS (40%): -26억
  OpEx (30%): -19.5억
  EBIT: 19.5억
  세금 (22%): -4.29억
  NOPAT: 15.21억
  CapEx (10%): -6.5억
  NWC 변화 (5%): -3.25억
  FCF: 5.46억

(Year 2-5 동일 방식)
```

#### Step 3: DCF 현재가치 할인
```
PV(Year 1) = 5.46억 / (1 + 0.15)^1 = 4.75억
PV(Year 2) = 7.1억 / (1 + 0.15)^2 = 5.37억
PV(Year 3) = 9.23억 / (1 + 0.15)^3 = 6.07억
...
DCF 합계 = 25.3억
```

#### Step 4: Terminal Value
```
Year 5 FCF: 15.5억
Perpetual Growth: 3%
Terminal Value = 15.5억 × (1 + 0.03) / (0.15 - 0.03) = 133억
PV(Terminal Value) = 133억 / (1 + 0.15)^5 = 66.1억
```

#### Step 5: 기업가치 & 주주가치
```
Enterprise Value = DCF 합계 + PV(Terminal Value)
                 = 25.3억 + 66.1억
                 = 91.4억

Equity Value = Enterprise Value + 현금 - 부채
             = 91.4억 + 10억 - 5억
             = 96.4억
```

**결론**: 테크이노의 기업가치는 **91.4억원**, 주주가치는 **96.4억원**

---

## 2. 제조업 (Relative 평가)
...

## 3. 부동산 (Asset 평가)
...
```

---

## 검증 기준

### 1. 코드 스타일 가이드
- [ ] 6개 섹션 (파일 헤더, 변수명, 함수 주석, 파일 구조, 타입 규칙, 에러 처리)
- [ ] 각 섹션마다 ✅ Good / ❌ Bad 예시
- [ ] 코드 예시 실행 가능 (문법 오류 없음)

### 2. 향상된 사용자 가이드
- [ ] 14단계 워크플로우 각 단계 설명
- [ ] 화면 예시 (ASCII 다이어그램 또는 스크린샷)
- [ ] FAQ 10개 이상
- [ ] 문제 해결 가이드 5개 이상

### 3. 샘플 데이터 세트
- [ ] 3개 산업별 샘플 (IT, 제조, 부동산)
- [ ] DCF 계산 과정 단계별 설명
- [ ] JSON 형식 템플릿
- [ ] 실제 사용 가능한 수치

---

## 예상 결과

**개선 전:**
- 코드 주석: 부족
- 변수명: 일부 불명확
- 사용자 가이드: 기본적
- 샘플 데이터: 없음

**개선 후:**
- 코드 스타일 가이드 완비
- 변수명 규칙 명확
- 14단계 상세 가이드 + FAQ
- 3개 산업 샘플 데이터

**품질 향상:**
- 기술적 정확성: 18/20 → 19/20 (+1점)
- 가독성: 18/20 → 19/20 (+1점)
- 구조 및 구성: 18/20 → 19/20 (+1점)
- 유용성: 18/20 → 19/20 (+1점)

**총 +4점** (88점 → 92점 기여)

---

**작성자**: Main Agent
**작성일**: 2026-02-23
**버전**: 1.0
