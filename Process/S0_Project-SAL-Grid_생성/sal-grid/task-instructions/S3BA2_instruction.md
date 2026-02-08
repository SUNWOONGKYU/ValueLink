# S3BA2: Financial Math Library (신규 구현)

## Task 정보

- **Task ID**: S3BA2
- **Task Name**: 재무 수학 라이브러리 구현
- **Stage**: S3 (AI Integration - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1 (Valuation Engine Orchestrator)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**기업가치평가에 필요한 순수 수학 함수 라이브러리 구현**

- WACC, NPV, IRR, Terminal Value 계산
- Enterprise Value, Equity Value, Share Price 계산
- Multiples (P/E, P/S, EV/EBITDA) 계산
- 유틸리티 함수 (평균, 중앙값, CAGR)
- **4가지 측면에서 구현** (정확성, 성능, 코드 품질, 테스트 가능성)

---

## 🎯 구현 필수 영역 (4가지)

### 1️⃣ 계산 정확성 (Accuracy)
- ✅ 재무 수식 정확히 구현
- ✅ IRR Newton-Raphson 알고리즘 수렴 보장
- ✅ 부동소수점 오차 최소화
- ✅ 0, 음수, NaN 예외 처리

### 2️⃣ 성능 최적화 (Performance)
- ✅ 순수 함수 (Pure Function) - 메모이제이션 가능
- ✅ IRR 반복 계산 최적화 (최대 100회)
- ✅ 불필요한 배열 복사 방지
- ✅ 타입스크립트 컴파일 최적화

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ JSDoc 주석 (수식, 파라미터 설명)
- ✅ 유닛 테스트 작성 용이
- ✅ 명확한 함수명 (calculateWACC, calculateNPV)

### 4️⃣ 테스트 가능성 (Testability)
- ✅ 순수 함수로 테스트 용이
- ✅ 엣지 케이스 테스트 가능
- ✅ 예상 결과 값 검증 가능
- ✅ Mock 없이 테스트 가능

---

## 작업 방식

### Step 1: 재무 수식 검증

**주요 수식:**

```
1. WACC (가중평균자본비용)
   WACC = (E/V) × Re + (D/V) × Rd × (1 - Tc)
   - E: 자기자본
   - D: 타인자본
   - V: E + D
   - Re: 자기자본비용
   - Rd: 타인자본비용
   - Tc: 법인세율

2. NPV (순현재가치)
   NPV = Σ (CFt / (1 + r)^t)
   - CFt: t기의 현금흐름
   - r: 할인율
   - t: 기간

3. IRR (내부수익률) - Newton-Raphson
   f(r) = Σ (CFt / (1 + r)^t) = 0
   r_(n+1) = r_n - f(r_n) / f'(r_n)

4. Terminal Value (영구가치)
   TV = FCF × (1 + g) / (WACC - g)
   - FCF: 마지막 현금흐름
   - g: 영구성장률
   - WACC: 할인율

5. Enterprise Value (기업가치)
   EV = NPV + TV

6. Equity Value (주주가치)
   Equity = EV - Net Debt

7. Share Price (주당가치)
   Price = Equity / Shares Outstanding
```

### Step 2: TypeScript 타입 정의

**함수 시그니처:**

```typescript
// WACC
export function calculateWACC(
  equity: number,
  debt: number,
  costOfEquity: number,
  costOfDebt: number,
  taxRate: number
): number

// NPV
export function calculateNPV(
  cashFlows: number[],
  discountRate: number
): number

// IRR
export function calculateIRR(
  cashFlows: number[],
  initialGuess?: number
): number

// Terminal Value
export function calculateTerminalValue(
  lastCashFlow: number,
  growthRate: number,
  wacc: number
): number

// Enterprise Value
export function calculateEnterpriseValue(
  npv: number,
  terminalValue: number
): number

// Equity Value
export function calculateEquityValue(
  enterpriseValue: number,
  netDebt: number
): number

// Share Price
export function calculateSharePrice(
  equityValue: number,
  sharesOutstanding: number
): number

// Multiples
export function calculatePE(
  marketCap: number,
  netIncome: number
): number

export function calculatePS(
  marketCap: number,
  revenue: number
): number

export function calculateEVtoEBITDA(
  enterpriseValue: number,
  ebitda: number
): number

// Utilities
export function average(numbers: number[]): number
export function median(numbers: number[]): number
export function cagr(
  startValue: number,
  endValue: number,
  years: number
): number
```

### Step 3: 구현 사항 적용

**예시 1: WACC 계산**

```typescript
// ❌ 단순 구현: 검증 없음
function calculateWACC(E, D, Re, Rd, Tc) {
  const V = E + D
  return (E / V) * Re + (D / V) * Rd * (1 - Tc)
}

// ✅ 개선: 입력 검증 + JSDoc + 부동소수점 처리
/**
 * 가중평균자본비용(WACC) 계산
 *
 * @param equity - 자기자본 (원)
 * @param debt - 타인자본 (원)
 * @param costOfEquity - 자기자본비용 (0~1, 예: 0.12 = 12%)
 * @param costOfDebt - 타인자본비용 (0~1, 예: 0.05 = 5%)
 * @param taxRate - 법인세율 (0~1, 예: 0.22 = 22%)
 * @returns WACC (0~1, 예: 0.09 = 9%)
 *
 * @example
 * const wacc = calculateWACC(100_000_000, 50_000_000, 0.12, 0.05, 0.22)
 * // Returns: 0.093 (9.3%)
 */
export function calculateWACC(
  equity: number,
  debt: number,
  costOfEquity: number,
  costOfDebt: number,
  taxRate: number
): number {
  // 입력 검증
  if (equity < 0 || debt < 0) {
    throw new Error('자기자본과 타인자본은 음수일 수 없습니다.')
  }

  if (equity === 0 && debt === 0) {
    throw new Error('자기자본과 타인자본이 모두 0일 수 없습니다.')
  }

  if (costOfEquity < 0 || costOfEquity > 1) {
    throw new Error('자기자본비용은 0과 1 사이여야 합니다.')
  }

  if (costOfDebt < 0 || costOfDebt > 1) {
    throw new Error('타인자본비용은 0과 1 사이여야 합니다.')
  }

  if (taxRate < 0 || taxRate > 1) {
    throw new Error('법인세율은 0과 1 사이여야 합니다.')
  }

  const totalValue = equity + debt

  // WACC 계산
  const equityWeight = equity / totalValue
  const debtWeight = debt / totalValue
  const wacc = equityWeight * costOfEquity + debtWeight * costOfDebt * (1 - taxRate)

  // 소수점 6자리 반올림 (0.123456 = 12.3456%)
  return Math.round(wacc * 1_000_000) / 1_000_000
}
```

**예시 2: IRR 계산 (Newton-Raphson)**

```typescript
// ❌ 단순 구현: 수렴 보장 없음
function calculateIRR(cashFlows) {
  let rate = 0.1
  for (let i = 0; i < 10; i++) {
    const npv = cashFlows.reduce((sum, cf, t) => sum + cf / Math.pow(1 + rate, t), 0)
    if (Math.abs(npv) < 0.01) break
    rate += 0.01
  }
  return rate
}

// ✅ 개선: Newton-Raphson 알고리즘 + 수렴 보장
/**
 * 내부수익률(IRR) 계산 - Newton-Raphson 방법
 *
 * @param cashFlows - 현금흐름 배열 (첫 번째는 초기투자, 음수)
 * @param initialGuess - 초기 추정값 (기본값: 0.1 = 10%)
 * @param maxIterations - 최대 반복 횟수 (기본값: 100)
 * @param tolerance - 허용 오차 (기본값: 0.0001)
 * @returns IRR (0~1, 예: 0.15 = 15%)
 *
 * @example
 * const irr = calculateIRR([-1000, 300, 400, 500])
 * // Returns: 0.124 (12.4%)
 */
export function calculateIRR(
  cashFlows: number[],
  initialGuess: number = 0.1,
  maxIterations: number = 100,
  tolerance: number = 0.0001
): number {
  // 입력 검증
  if (!cashFlows || cashFlows.length < 2) {
    throw new Error('현금흐름은 최소 2개 이상이어야 합니다.')
  }

  if (cashFlows[0] >= 0) {
    throw new Error('초기 현금흐름은 음수(투자)여야 합니다.')
  }

  let rate = initialGuess

  for (let iteration = 0; iteration < maxIterations; iteration++) {
    // f(r) = NPV
    let npv = 0
    // f'(r) = dNPV/dr
    let derivative = 0

    for (let t = 0; t < cashFlows.length; t++) {
      const discountFactor = Math.pow(1 + rate, t)
      npv += cashFlows[t] / discountFactor
      derivative -= (t * cashFlows[t]) / Math.pow(1 + rate, t + 1)
    }

    // 수렴 확인
    if (Math.abs(npv) < tolerance) {
      return Math.round(rate * 1_000_000) / 1_000_000
    }

    // Newton-Raphson 업데이트
    if (derivative === 0) {
      throw new Error('IRR 계산 실패: 미분값이 0입니다.')
    }

    rate = rate - npv / derivative

    // 비정상 값 체크
    if (isNaN(rate) || !isFinite(rate) || rate < -1 || rate > 10) {
      throw new Error('IRR 계산 실패: 수렴하지 않습니다.')
    }
  }

  throw new Error(`IRR 계산 실패: ${maxIterations}회 반복 후에도 수렴하지 않습니다.`)
}
```

**예시 3: Terminal Value 계산**

```typescript
// ❌ 단순 구현: g >= WACC 처리 없음
function calculateTerminalValue(fcf, g, wacc) {
  return (fcf * (1 + g)) / (wacc - g)
}

// ✅ 개선: 검증 + 예외 처리
/**
 * 영구가치(Terminal Value) 계산
 *
 * @param lastCashFlow - 마지막 기간 현금흐름 (원)
 * @param growthRate - 영구성장률 (0~1, 예: 0.02 = 2%)
 * @param wacc - 가중평균자본비용 (0~1, 예: 0.09 = 9%)
 * @returns Terminal Value (원)
 *
 * @example
 * const tv = calculateTerminalValue(10_000_000, 0.02, 0.09)
 * // Returns: 145_714_286
 */
export function calculateTerminalValue(
  lastCashFlow: number,
  growthRate: number,
  wacc: number
): number {
  // 입력 검증
  if (lastCashFlow <= 0) {
    throw new Error('현금흐름은 양수여야 합니다.')
  }

  if (growthRate < 0 || growthRate > 1) {
    throw new Error('성장률은 0과 1 사이여야 합니다.')
  }

  if (wacc < 0 || wacc > 1) {
    throw new Error('WACC는 0과 1 사이여야 합니다.')
  }

  if (growthRate >= wacc) {
    throw new Error('성장률은 WACC보다 작아야 합니다.')
  }

  // Terminal Value 계산
  const terminalValue = (lastCashFlow * (1 + growthRate)) / (wacc - growthRate)

  // 반올림 (원 단위)
  return Math.round(terminalValue)
}
```

### Step 4: Best Practice 적용

**순수 함수 (Pure Function):**
- 같은 입력 → 같은 출력
- 부작용(Side Effect) 없음
- 테스트 용이

**JSDoc 주석:**
```typescript
/**
 * 함수 설명
 *
 * @param 파라미터명 - 설명 (단위, 범위)
 * @returns 반환값 설명 (단위, 범위)
 *
 * @example
 * const result = functionName(100, 0.1)
 * // Returns: 10
 */
```

**에러 처리:**
```typescript
// ✅ 명확한 에러 메시지
if (value < 0) {
  throw new Error('값은 양수여야 합니다.')
}

// ✅ 범위 체크
if (rate < 0 || rate > 1) {
  throw new Error('비율은 0과 1 사이여야 합니다.')
}
```

---

## 전제조건 확인

**S3BA1 완료 확인:**
- ValuationEngine abstract class 구현됨
- 타입 정의 완료 (ValuationInput, ValuationResult)

---

## 생성 파일 (1개)

### api/Backend_APIs/valuation/financial-math.ts
**목표:** 재무 수학 함수 라이브러리

**포함 함수:**
1. **WACC 계산**: `calculateWACC()`
2. **NPV 계산**: `calculateNPV()`
3. **IRR 계산**: `calculateIRR()` - Newton-Raphson
4. **Terminal Value**: `calculateTerminalValue()`
5. **Enterprise Value**: `calculateEnterpriseValue()`
6. **Equity Value**: `calculateEquityValue()`
7. **Share Price**: `calculateSharePrice()`
8. **Multiples**: `calculatePE()`, `calculatePS()`, `calculateEVtoEBITDA()`
9. **Utilities**: `average()`, `median()`, `cagr()`

**개선 사항:**
- ✅ 입력 검증 (음수, 0, 범위)
- ✅ JSDoc 주석 (수식, 예시)
- ✅ 부동소수점 반올림
- ✅ 명확한 에러 메시지

---

## 완료 기준

### 필수 (Must Have)
- [ ] WACC, NPV, IRR 함수 구현
- [ ] Terminal Value, EV, Equity, Share Price 구현
- [ ] Multiples 계산 (P/E, P/S, EV/EBITDA)
- [ ] Utility 함수 (평균, 중앙값, CAGR)
- [ ] 모든 함수에 JSDoc 주석
- [ ] 입력 검증 로직

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] IRR 수렴 테스트 (양수/음수 현금흐름)
- [ ] Terminal Value g >= WACC 예외 처리
- [ ] 부동소수점 반올림 확인

### 구현 항목 (Implementation)
- [ ] 정확성: 재무 수식 정확, 예외 처리
- [ ] 성능: 순수 함수, IRR 최적화
- [ ] 코드 품질: JSDoc, 명확한 함수명
- [ ] 테스트 가능성: 순수 함수, 엣지 케이스

---

## 참조

### 재무 수식
- **WACC**: (E/V)×Re + (D/V)×Rd×(1-Tc)
- **NPV**: Σ(CFt / (1+r)^t)
- **IRR**: Newton-Raphson 방법으로 NPV = 0 되는 r 찾기
- **Terminal Value**: FCF×(1+g) / (WACC-g)

### Newton-Raphson 알고리즘
```
f(r) = Σ(CFt / (1+r)^t) = 0
f'(r) = -Σ(t×CFt / (1+r)^(t+1))
r_(n+1) = r_n - f(r_n) / f'(r_n)
```

### 관련 Task
- **S3BA1**: Valuation Engine Orchestrator (타입 정의)
- **S3BA3**: DCF Engine (NPV, Terminal Value 사용)
- **S3BA4**: Other Engines (Multiples 사용)

---

## 주의사항

### 🔢 계산 정확성

1. **부동소수점 반올림**
   - WACC, IRR: 소수점 6자리 (0.123456 = 12.3456%)
   - 금액: 원 단위 (Math.round())

2. **IRR 수렴 보장**
   - 최대 100회 반복
   - 허용 오차 0.0001
   - 수렴 실패 시 명확한 에러

3. **예외 처리**
   - 0으로 나누기 방지
   - growthRate >= WACC 체크
   - 음수 입력 검증

### ⚡ 성능

1. **순수 함수**
   - 부작용 없음
   - 메모이제이션 가능

2. **IRR 최적화**
   - Newton-Raphson 방법 (빠른 수렴)
   - 초기 추정값 0.1 (일반적)

### 📝 코드 품질

1. **JSDoc 주석**
   - 수식 설명
   - 파라미터 범위 (0~1 = %)
   - 예시 코드

2. **명확한 함수명**
   - `calculateWACC` (동사 + 명사)
   - `average`, `median` (간결)

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 1개
**라인 수**: ~500줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경
