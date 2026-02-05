# S3BA2 Verification

## 검증 대상

- **Task ID**: S3BA2
- **Task Name**: 금융 수학 라이브러리
- **Stage**: S3 (Valuation Engines - 개발 2차)
- **Area**: BA (Backend APIs)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

- [ ] **`lib/valuation/financial-math.ts` 존재** - 금융 수학 라이브러리

---

### 3. 핵심 기능 테스트

#### 3.1 WACC (가중평균자본비용)

- [ ] **calculateWACC() 함수 export**
  - 입력: `WACCInput` interface
  - 출력: number (퍼센트)
  - 공식: `(E/V) * Re + (D/V) * Rd * (1 - T)`
  - 예외: `total_value = 0` 시 에러

#### 3.2 NPV (순현재가치)

- [ ] **calculateNPV() 함수 export**
  - 입력: `cash_flows[]`, `discount_rate`, `initial_investment`
  - 출력: number
  - 공식: `Σ(CF_t / (1 + r)^t) - Initial Investment`

#### 3.3 IRR (내부수익률)

- [ ] **calculateIRR() 함수 export**
  - 입력: `cash_flows[]`, `initial_guess`, `max_iterations`, `tolerance`
  - 출력: number | null (수렴 실패 시 null)
  - 알고리즘: Newton-Raphson 방법
  - 최대 100회 반복

#### 3.4 할인율 (Discount Rate)

- [ ] **discountCashFlow() 함수 export**
  - 입력: `cash_flow`, `discount_rate`, `period`
  - 출력: number
  - 공식: `CF / (1 + r)^t`

- [ ] **discountCashFlows() 함수 export**
  - 입력: `cash_flows[]`, `discount_rate`
  - 출력: number[] (각 연도별 할인된 현금흐름)

#### 3.5 영구성장가치 (Terminal Value)

- [ ] **calculateTerminalValue() 함수 export**
  - 입력: `final_cash_flow`, `discount_rate`, `growth_rate`
  - 출력: number
  - 공식: `CF * (1 + g) / (r - g)` (Gordon Growth Model)
  - 예외: `discount_rate <= growth_rate` 시 에러

- [ ] **calculatePVOfTerminalValue() 함수 export**
  - 영구성장가치의 현재가치 계산

#### 3.6 기업가치 계산

- [ ] **calculateEnterpriseValue() 함수 export**
  - 입력: `cash_flows[]`, `discount_rate`, `growth_rate`
  - 출력: number
  - DCF 방법: `PV(예측기간) + PV(영구성장가치)`

- [ ] **calculateEquityValue() 함수 export**
  - 입력: `enterprise_value`, `net_debt`
  - 출력: number
  - 공식: `Enterprise Value - Net Debt`

- [ ] **calculateSharePrice() 함수 export**
  - 입력: `equity_value`, `shares_outstanding`
  - 출력: number
  - 공식: `Equity Value / Shares Outstanding`
  - 예외: `shares_outstanding = 0` 시 에러

#### 3.7 배수 계산 (Multiples)

- [ ] **calculatePERatio() 함수 export**
  - P/E 배수 (주가수익비율)
  - 예외: `EPS = 0` 시 에러

- [ ] **calculatePSRatio() 함수 export**
  - P/S 배수 (주가매출비율)
  - 예외: `Sales per share = 0` 시 에러

- [ ] **calculateEVEBITDARatio() 함수 export**
  - EV/EBITDA 배수
  - 예외: `EBITDA = 0` 시 에러

#### 3.8 유틸리티 함수

- [ ] **calculateAverage() 함수 export**
  - 평균 계산
  - 예외: 빈 배열 시 에러

- [ ] **calculateMedian() 함수 export**
  - 중앙값 계산
  - 예외: 빈 배열 시 에러

- [ ] **calculateCAGR() 함수 export**
  - 복리 성장률 계산
  - 공식: `(Ending / Beginning)^(1/years) - 1`
  - 예외: `beginning_value = 0` 또는 `years = 0` 시 에러

---

### 4. 통합 테스트

#### 4.1 순수 함수 검증

- [ ] **부작용 없음**
  - 같은 입력 → 같은 출력
  - 외부 상태 변경 없음

#### 4.2 예외 처리

- [ ] **0으로 나누기 방지**
  - 모든 나눗셈 연산 전 검증
  - 명확한 에러 메시지

#### 4.3 퍼센트 단위 일관성

- [ ] **입력: 퍼센트** (예: 10%)
- [ ] **계산: 소수** (예: 0.1)
- [ ] **출력: 퍼센트** (예: 10%)

---

### 5. Blocker 확인

- [ ] **의존성 없음** (독립적인 라이브러리)

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **파일 생성 완료** ✅ (1개 파일)
3. **WACC 계산 함수** ✅
4. **NPV 계산 함수** ✅
5. **IRR 계산 함수** ✅ (Newton-Raphson)
6. **할인율 계산 함수** ✅
7. **영구성장가치 계산 함수** ✅
8. **기업가치 계산 함수** ✅
9. **배수 계산 함수** ✅
10. **유틸리티 함수** ✅

### 권장 (Nice to Pass)

1. **단위 테스트 작성** ✨ (`financial-math.test.ts`)
2. **JSDoc 주석 추가** ✨
3. **추가 배수** ✨ (P/B, EV/Sales 등)

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **0으로 나누기 방지**
   - `total_value`, `shares_outstanding`, `EPS` 등
   - 명확한 에러 메시지

2. **퍼센트 단위**
   - 입력: 퍼센트 (10%)
   - 계산: 소수 (0.1)
   - 출력: 퍼센트 (10%)

3. **IRR 수렴 실패**
   - 최대 100회 반복
   - 수렴 실패 시 null 반환
   - tolerance: 0.0001

4. **순수 함수**
   - 부작용 없음
   - 같은 입력 → 같은 출력

5. **WACC > 성장률**
   - `calculateTerminalValue()`에서 검증
   - 위반 시 에러

---

## PO 테스트 가이드

### 1. WACC 계산 테스트

```typescript
import { calculateWACC } from '@/lib/valuation/financial-math'

const result = calculateWACC({
  equity_value: 1000,
  debt_value: 500,
  cost_of_equity: 10,
  cost_of_debt: 5,
  tax_rate: 20
})
console.log(result) // 예상: ~8.33%
```

### 2. NPV 계산 테스트

```typescript
import { calculateNPV } from '@/lib/valuation/financial-math'

const result = calculateNPV(
  [100, 110, 120, 130, 140], // 5년 현금흐름
  10, // 할인율 10%
  0 // 초기 투자 없음
)
console.log(result) // 예상: 양수 (NPV > 0)
```

### 3. IRR 계산 테스트

```typescript
import { calculateIRR } from '@/lib/valuation/financial-math'

const result = calculateIRR(
  [-1000, 300, 400, 500, 600] // 초기 투자 + 4년 수익
)
console.log(result) // 예상: ~20% (IRR)
```

---

## 참조

- Task Instruction: `task-instructions/S3BA2_instruction.md`
- 기존 프로토타입: `backend/app/services/valuation_engine/common/financial_math.py`
- WACC: https://en.wikipedia.org/wiki/Weighted_average_cost_of_capital
- NPV: https://en.wikipedia.org/wiki/Net_present_value
- IRR: https://en.wikipedia.org/wiki/Internal_rate_of_return

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
