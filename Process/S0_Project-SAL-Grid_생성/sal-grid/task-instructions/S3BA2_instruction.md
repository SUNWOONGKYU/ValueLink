# S3BA2: Financial Math Library

## Task 정보

- **Task ID**: S3BA2
- **Task Name**: 금융 수학 라이브러리
- **Stage**: S3 (Valuation Engines - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: 없음
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

기업가치평가에 필요한 금융 수학 함수 라이브러리 구현 (WACC, NPV, IRR, 할인율 계산 등)

---

## 상세 지시사항

### 1. 금융 수학 라이브러리

**파일**: `lib/valuation/financial-math.ts`

```typescript
/**
 * 금융 수학 라이브러리
 * 기업가치평가에 필요한 핵심 계산 함수 제공
 */

// ==================== WACC (가중평균자본비용) ====================

export interface WACCInput {
  equity_value: number          // 자기자본 시가총액
  debt_value: number             // 부채 시가총액
  cost_of_equity: number         // 자기자본비용 (%)
  cost_of_debt: number           // 타인자본비용 (%)
  tax_rate: number               // 법인세율 (%)
}

/**
 * WACC 계산
 * WACC = (E/V) * Re + (D/V) * Rd * (1 - T)
 */
export function calculateWACC(input: WACCInput): number {
  const { equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate } = input
  const total_value = equity_value + debt_value

  if (total_value === 0) {
    throw new Error('Total value (E + D) cannot be zero')
  }

  const equity_weight = equity_value / total_value
  const debt_weight = debt_value / total_value

  const wacc =
    equity_weight * (cost_of_equity / 100) +
    debt_weight * (cost_of_debt / 100) * (1 - tax_rate / 100)

  return wacc * 100 // 퍼센트로 반환
}

// ==================== NPV (순현재가치) ====================

/**
 * NPV 계산
 * NPV = Σ(CF_t / (1 + r)^t) - Initial Investment
 */
export function calculateNPV(
  cash_flows: number[],
  discount_rate: number,
  initial_investment: number = 0
): number {
  const npv = cash_flows.reduce((sum, cf, t) => {
    return sum + cf / Math.pow(1 + discount_rate / 100, t + 1)
  }, 0)

  return npv - initial_investment
}

// ==================== IRR (내부수익률) ====================

/**
 * IRR 계산 (Newton-Raphson 방법)
 * IRR은 NPV = 0이 되는 할인율
 */
export function calculateIRR(
  cash_flows: number[],
  initial_guess: number = 0.1,
  max_iterations: number = 100,
  tolerance: number = 0.0001
): number | null {
  let rate = initial_guess

  for (let i = 0; i < max_iterations; i++) {
    const npv = cash_flows.reduce((sum, cf, t) => {
      return sum + cf / Math.pow(1 + rate, t)
    }, 0)

    const dnpv = cash_flows.reduce((sum, cf, t) => {
      return sum - (t * cf) / Math.pow(1 + rate, t + 1)
    }, 0)

    const new_rate = rate - npv / dnpv

    if (Math.abs(new_rate - rate) < tolerance) {
      return new_rate * 100 // 퍼센트로 반환
    }

    rate = new_rate
  }

  return null // 수렴 실패
}

// ==================== 할인율 (Discount Rate) ====================

/**
 * 현금흐름 할인
 * PV = CF / (1 + r)^t
 */
export function discountCashFlow(
  cash_flow: number,
  discount_rate: number,
  period: number
): number {
  return cash_flow / Math.pow(1 + discount_rate / 100, period)
}

/**
 * 현금흐름 배열 할인 (각 연도별)
 */
export function discountCashFlows(
  cash_flows: number[],
  discount_rate: number
): number[] {
  return cash_flows.map((cf, t) => discountCashFlow(cf, discount_rate, t + 1))
}

// ==================== 영구성장가치 (Terminal Value) ====================

/**
 * 영구성장가치 계산 (Gordon Growth Model)
 * TV = CF * (1 + g) / (r - g)
 */
export function calculateTerminalValue(
  final_cash_flow: number,
  discount_rate: number,
  growth_rate: number
): number {
  if (discount_rate <= growth_rate) {
    throw new Error('Discount rate must be greater than growth rate')
  }

  return (final_cash_flow * (1 + growth_rate / 100)) / ((discount_rate - growth_rate) / 100)
}

/**
 * 영구성장가치의 현재가치
 */
export function calculatePVOfTerminalValue(
  final_cash_flow: number,
  discount_rate: number,
  growth_rate: number,
  forecast_period: number
): number {
  const tv = calculateTerminalValue(final_cash_flow, discount_rate, growth_rate)
  return discountCashFlow(tv, discount_rate, forecast_period)
}

// ==================== 기업가치 계산 ====================

/**
 * 기업가치 계산 (DCF 방법)
 * Enterprise Value = PV(예측기간 현금흐름) + PV(영구성장가치)
 */
export function calculateEnterpriseValue(
  cash_flows: number[],
  discount_rate: number,
  growth_rate: number
): number {
  // 예측기간 현금흐름의 현재가치
  const pv_cash_flows = cash_flows.reduce((sum, cf, t) => {
    return sum + discountCashFlow(cf, discount_rate, t + 1)
  }, 0)

  // 영구성장가치의 현재가치
  const final_cf = cash_flows[cash_flows.length - 1]
  const pv_terminal_value = calculatePVOfTerminalValue(
    final_cf,
    discount_rate,
    growth_rate,
    cash_flows.length
  )

  return pv_cash_flows + pv_terminal_value
}

/**
 * 자기자본가치 계산
 * Equity Value = Enterprise Value - Net Debt
 */
export function calculateEquityValue(
  enterprise_value: number,
  net_debt: number
): number {
  return enterprise_value - net_debt
}

/**
 * 주당 가치 계산
 * Share Price = Equity Value / Shares Outstanding
 */
export function calculateSharePrice(
  equity_value: number,
  shares_outstanding: number
): number {
  if (shares_outstanding === 0) {
    throw new Error('Shares outstanding cannot be zero')
  }

  return equity_value / shares_outstanding
}

// ==================== 배수 계산 (Multiples) ====================

/**
 * P/E 배수 (주가수익비율)
 */
export function calculatePERatio(stock_price: number, earnings_per_share: number): number {
  if (earnings_per_share === 0) {
    throw new Error('EPS cannot be zero')
  }
  return stock_price / earnings_per_share
}

/**
 * P/S 배수 (주가매출비율)
 */
export function calculatePSRatio(stock_price: number, sales_per_share: number): number {
  if (sales_per_share === 0) {
    throw new Error('Sales per share cannot be zero')
  }
  return stock_price / sales_per_share
}

/**
 * EV/EBITDA 배수
 */
export function calculateEVEBITDARatio(
  enterprise_value: number,
  ebitda: number
): number {
  if (ebitda === 0) {
    throw new Error('EBITDA cannot be zero')
  }
  return enterprise_value / ebitda
}

// ==================== 유틸리티 함수 ====================

/**
 * 평균 계산
 */
export function calculateAverage(values: number[]): number {
  if (values.length === 0) {
    throw new Error('Array cannot be empty')
  }
  return values.reduce((sum, val) => sum + val, 0) / values.length
}

/**
 * 중앙값 계산
 */
export function calculateMedian(values: number[]): number {
  if (values.length === 0) {
    throw new Error('Array cannot be empty')
  }

  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)

  return sorted.length % 2 === 0
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid]
}

/**
 * 복리 성장률 계산 (CAGR)
 * CAGR = (Ending Value / Beginning Value)^(1/years) - 1
 */
export function calculateCAGR(
  beginning_value: number,
  ending_value: number,
  years: number
): number {
  if (beginning_value === 0) {
    throw new Error('Beginning value cannot be zero')
  }
  if (years === 0) {
    throw new Error('Years cannot be zero')
  }

  const cagr = Math.pow(ending_value / beginning_value, 1 / years) - 1
  return cagr * 100 // 퍼센트로 반환
}

// ==================== Export All ====================

export default {
  calculateWACC,
  calculateNPV,
  calculateIRR,
  discountCashFlow,
  discountCashFlows,
  calculateTerminalValue,
  calculatePVOfTerminalValue,
  calculateEnterpriseValue,
  calculateEquityValue,
  calculateSharePrice,
  calculatePERatio,
  calculatePSRatio,
  calculateEVEBITDARatio,
  calculateAverage,
  calculateMedian,
  calculateCAGR,
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/valuation/financial-math.ts` | 금융 수학 라이브러리 | ~350줄 |

**총 파일 수**: 1개
**총 라인 수**: ~350줄

---

## 기술 스택

- **TypeScript 5.x**: 타입 안전성
- **Pure Functions**: 순수 함수 (부작용 없음)
- **Mathematical Algorithms**: Newton-Raphson (IRR 계산)

---

## 완료 기준

### 필수 (Must Have)

- [ ] WACC 계산 함수
- [ ] NPV 계산 함수
- [ ] IRR 계산 함수 (Newton-Raphson 방법)
- [ ] 할인율 계산 함수
- [ ] 영구성장가치 계산 함수
- [ ] 기업가치/자기자본가치/주당가치 계산 함수
- [ ] 배수 계산 함수 (P/E, P/S, EV/EBITDA)
- [ ] 유틸리티 함수 (평균, 중앙값, CAGR)

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] 각 함수 단위 테스트 통과
- [ ] 예외 처리 (0으로 나누기 등)
- [ ] 수학적 정확성 검증

### 권장 (Nice to Have)

- [ ] 단위 테스트 작성 (`financial-math.test.ts`)
- [ ] JSDoc 주석 추가
- [ ] 추가 배수 (P/B, EV/Sales 등)

---

## 참조

### 기존 프로토타입
- `backend/app/services/valuation_engine/common/financial_math.py` (Python 버전)

### 수학 공식
- WACC: https://en.wikipedia.org/wiki/Weighted_average_cost_of_capital
- NPV: https://en.wikipedia.org/wiki/Net_present_value
- IRR: https://en.wikipedia.org/wiki/Internal_rate_of_return

---

## 주의사항

1. **0으로 나누기 방지**
   - 모든 나눗셈 연산 전 검증
   - 명확한 에러 메시지

2. **퍼센트 단위**
   - 입력: 퍼센트 (예: 10%)
   - 계산: 소수 (예: 0.1)
   - 출력: 퍼센트 (예: 10%)

3. **IRR 수렴 실패**
   - 최대 100회 반복
   - 수렴 실패 시 null 반환

4. **순수 함수**
   - 부작용 없음
   - 같은 입력 → 같은 출력

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
