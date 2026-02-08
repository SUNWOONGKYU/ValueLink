# S3BA3: DCF Engine & Sensitivity Analysis (신규 구현)

## Task 정보

- **Task ID**: S3BA3
- **Task Name**: DCF 평가 엔진 및 민감도 분석 구현
- **Stage**: S3 (AI Integration - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1 (Orchestrator), S3BA2 (Financial Math)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**DCF (현금흐름할인법) 평가 엔진 구현 및 민감도 분석 제공**

- ValuationEngine abstract class 상속
- Free Cash Flow (FCF) 계산
- NPV 및 Terminal Value 계산
- 민감도 분석 (WACC × Growth Rate 매트릭스)
- **4가지 측면에서 구현** (정확성, 성능, 코드 품질, 확장성)

---

## 🎯 구현 필수 영역 (4가지)

### 1️⃣ 계산 정확성 (Accuracy)
- ✅ FCF 수식 정확히 구현 (NOPAT + 감가상각 - Capex - ΔWC)
- ✅ NPV와 Terminal Value 올바른 계산
- ✅ 민감도 분석 매트릭스 (WACC ±2%, Growth ±1%)
- ✅ 입력 데이터 검증 (필수 필드, 범위)

### 2️⃣ 성능 최적화 (Performance)
- ✅ 민감도 분석 병렬 계산 (Promise.all)
- ✅ 중복 계산 제거 (기본 NPV 재사용)
- ✅ 불필요한 배열 복사 방지
- ✅ 타임아웃 설정 (무한 루프 방지)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ ValuationEngine 인터페이스 준수
- ✅ JSDoc 주석 (FCF 계산 수식)
- ✅ 에러 핸들링 강화

### 4️⃣ 확장성 (Extensibility)
- ✅ 다른 평가 방법과 일관된 인터페이스
- ✅ 민감도 분석 범위 설정 가능
- ✅ 중간 계산 결과 반환 (디버깅 용이)
- ✅ 다양한 FCF 계산 방식 지원 가능

---

## 작업 방식

### Step 1: DCF 이론 검증

**DCF 핵심 수식:**

```
1. Free Cash Flow (FCF)
   FCF = NOPAT + 감가상각 - Capex - ΔWC
   - NOPAT: Net Operating Profit After Tax (세후영업이익)
   - 감가상각: Depreciation & Amortization
   - Capex: Capital Expenditure (자본적 지출)
   - ΔWC: Change in Working Capital (운전자본 변동)

2. NPV (현재가치)
   NPV = Σ(FCFt / (1 + WACC)^t)

3. Terminal Value (영구가치)
   TV = FCF_마지막 × (1 + g) / (WACC - g)

4. Enterprise Value (기업가치)
   EV = NPV + PV(TV)
   - PV(TV) = TV / (1 + WACC)^n

5. Equity Value (주주가치)
   Equity = EV - Net Debt

6. Share Price (주당가치)
   Price = Equity / Shares Outstanding
```

**민감도 분석:**
```
WACC 범위: 기본값 ± 2% (4단계: -2%, -1%, 기본, +1%, +2%)
Growth 범위: 기본값 ± 1% (4단계: -1%, -0.5%, 기본, +0.5%, +1%)

매트릭스: 4 × 4 = 16개 시나리오
```

### Step 2: ValuationEngine 상속

**인터페이스 구현:**

```typescript
// S3BA1에서 정의한 Abstract class
abstract class ValuationEngine {
  abstract getName(): string
  abstract calculate(data: ValuationInput): Promise<ValuationResult>
  validate(data: ValuationInput): ValidationResult {
    // 기본 검증 로직
  }
}

// DCF Engine 구현
class DCFEngine extends ValuationEngine {
  getName(): string {
    return 'DCF'
  }

  validate(data: ValuationInput): ValidationResult {
    // DCF 특화 검증
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    // DCF 계산 로직
  }
}
```

### Step 3: 구현 사항 적용

**예시 1: FCF 계산**

```typescript
// ❌ 단순 구현: 검증 없음
function calculateFCF(nopat, depreciation, capex, workingCapital) {
  return nopat + depreciation - capex - workingCapital
}

// ✅ 개선: 검증 + 타입 안전성
/**
 * Free Cash Flow (FCF) 계산
 *
 * FCF = NOPAT + 감가상각 - Capex - ΔWC
 *
 * @param nopat - 세후영업이익 (원)
 * @param depreciation - 감가상각비 (원)
 * @param capex - 자본적 지출 (원)
 * @param deltaWorkingCapital - 운전자본 변동 (원)
 * @returns FCF (원)
 */
function calculateFCF(
  nopat: number,
  depreciation: number,
  capex: number,
  deltaWorkingCapital: number
): number {
  // 입력 검증
  if (isNaN(nopat) || isNaN(depreciation) || isNaN(capex) || isNaN(deltaWorkingCapital)) {
    throw new Error('모든 입력값은 숫자여야 합니다.')
  }

  // FCF 계산
  const fcf = nopat + depreciation - capex - deltaWorkingCapital

  // 반올림 (원 단위)
  return Math.round(fcf)
}
```

**예시 2: DCF Engine 구현**

```typescript
// ❌ 단순 구현: 검증 없음, 중간 결과 없음
class DCFEngine extends ValuationEngine {
  async calculate(data: any) {
    const npv = calculateNPV(data.cashFlows, data.wacc)
    const tv = calculateTerminalValue(data.lastCF, data.g, data.wacc)
    return { value: npv + tv }
  }
}

// ✅ 개선: 검증 + 중간 결과 + 명확한 타입
class DCFEngine extends ValuationEngine {
  getName(): string {
    return 'DCF'
  }

  validate(data: ValuationInput): ValidationResult {
    // 부모 검증 먼저
    const baseValidation = super.validate(data)
    if (!baseValidation.valid) return baseValidation

    // DCF 필수 필드 검증
    if (!data.cashFlows || data.cashFlows.length === 0) {
      return {
        valid: false,
        error: '현금흐름 데이터가 필요합니다.'
      }
    }

    if (!data.wacc || data.wacc <= 0 || data.wacc >= 1) {
      return {
        valid: false,
        error: 'WACC는 0과 1 사이여야 합니다.'
      }
    }

    if (!data.terminalGrowthRate && data.terminalGrowthRate !== 0) {
      return {
        valid: false,
        error: '영구성장률이 필요합니다.'
      }
    }

    if (data.terminalGrowthRate >= data.wacc) {
      return {
        valid: false,
        error: '영구성장률은 WACC보다 작아야 합니다.'
      }
    }

    return { valid: true }
  }

  async calculate(data: ValuationInput): Promise<ValuationResult> {
    // 검증
    const validation = this.validate(data)
    if (!validation.valid) {
      throw new Error(validation.error)
    }

    try {
      // 1. NPV 계산
      const npv = calculateNPV(data.cashFlows!, data.wacc!)

      // 2. Terminal Value 계산
      const lastCashFlow = data.cashFlows![data.cashFlows!.length - 1]
      const terminalValue = calculateTerminalValue(
        lastCashFlow,
        data.terminalGrowthRate!,
        data.wacc!
      )

      // 3. Terminal Value의 현재가치
      const pvTerminalValue = terminalValue / Math.pow(1 + data.wacc!, data.cashFlows!.length)

      // 4. Enterprise Value
      const enterpriseValue = npv + pvTerminalValue

      // 5. Equity Value
      const netDebt = data.netDebt || 0
      const equityValue = enterpriseValue - netDebt

      // 6. Share Price
      const sharesOutstanding = data.sharesOutstanding || 1
      const sharePrice = equityValue / sharesOutstanding

      return {
        method: 'DCF',
        enterpriseValue: Math.round(enterpriseValue),
        equityValue: Math.round(equityValue),
        sharePrice: Math.round(sharePrice * 100) / 100,
        details: {
          npv: Math.round(npv),
          terminalValue: Math.round(terminalValue),
          pvTerminalValue: Math.round(pvTerminalValue),
          netDebt,
          sharesOutstanding
        },
        timestamp: new Date().toISOString()
      }
    } catch (error: any) {
      throw new Error(`DCF 계산 실패: ${error.message}`)
    }
  }
}
```

**예시 3: 민감도 분석**

```typescript
// ❌ 단순 구현: 순차 계산 (느림)
async function sensitivityAnalysis(data) {
  const results = []
  for (const wacc of waccRange) {
    for (const growth of growthRange) {
      const result = await calculateDCF({ ...data, wacc, growth })
      results.push(result)
    }
  }
  return results
}

// ✅ 개선: 병렬 계산 (빠름)
/**
 * DCF 민감도 분석
 *
 * WACC와 Growth Rate를 변화시켜 기업가치 변동 분석
 *
 * @param baseData - 기본 평가 데이터
 * @param waccRange - WACC 범위 (기본값 ± 2%)
 * @param growthRange - Growth Rate 범위 (기본값 ± 1%)
 * @returns 민감도 분석 매트릭스
 */
async function performSensitivityAnalysis(
  baseData: ValuationInput,
  waccRange: number[] = [-0.02, -0.01, 0, 0.01, 0.02],
  growthRange: number[] = [-0.01, -0.005, 0, 0.005, 0.01]
): Promise<SensitivityAnalysisResult> {
  const baseWacc = baseData.wacc!
  const baseGrowth = baseData.terminalGrowthRate!

  const dcfEngine = new DCFEngine()
  const scenarios: Promise<SensitivityScenario>[] = []

  // 병렬 계산을 위한 Promise 배열
  for (const waccDelta of waccRange) {
    for (const growthDelta of growthRange) {
      const newWacc = baseWacc + waccDelta
      const newGrowth = baseGrowth + growthDelta

      // WACC > Growth 검증
      if (newWacc <= newGrowth) continue

      const scenario = dcfEngine.calculate({
        ...baseData,
        wacc: newWacc,
        terminalGrowthRate: newGrowth
      }).then((result) => ({
        wacc: newWacc,
        growthRate: newGrowth,
        enterpriseValue: result.enterpriseValue,
        equityValue: result.equityValue,
        sharePrice: result.sharePrice
      }))

      scenarios.push(scenario)
    }
  }

  // 병렬 실행
  const results = await Promise.all(scenarios)

  // 매트릭스 형태로 변환
  const matrix: number[][] = []
  let idx = 0

  for (let i = 0; i < waccRange.length; i++) {
    matrix[i] = []
    for (let j = 0; j < growthRange.length; j++) {
      if (idx < results.length) {
        matrix[i][j] = results[idx].enterpriseValue
        idx++
      } else {
        matrix[i][j] = NaN // WACC <= Growth인 경우
      }
    }
  }

  return {
    waccRange: waccRange.map((d) => baseWacc + d),
    growthRange: growthRange.map((d) => baseGrowth + d),
    matrix,
    scenarios: results
  }
}
```

### Step 4: Best Practice 적용

**TypeScript 타입 정의:**
```typescript
export interface DCFInput extends ValuationInput {
  cashFlows: number[] // 5년 FCF
  wacc: number // WACC (0~1)
  terminalGrowthRate: number // 영구성장률 (0~1)
  netDebt?: number // 순차입금
  sharesOutstanding?: number // 발행주식수
}

export interface SensitivityScenario {
  wacc: number
  growthRate: number
  enterpriseValue: number
  equityValue: number
  sharePrice: number
}

export interface SensitivityAnalysisResult {
  waccRange: number[]
  growthRange: number[]
  matrix: number[][] // [WACC][Growth] = EV
  scenarios: SensitivityScenario[]
}
```

**병렬 처리 패턴:**
```typescript
// ✅ Promise.all로 병렬 실행
const scenarios = [scenario1, scenario2, ...]
const results = await Promise.all(scenarios)
```

---

## 전제조건 확인

**S3BA1 완료 확인:**
- ValuationEngine abstract class 구현됨

**S3BA2 완료 확인:**
- calculateNPV(), calculateTerminalValue() 함수 구현됨

---

## 생성 파일 (1개)

### api/Backend_APIs/valuation/engines/dcf-engine.ts
**목표:** DCF 평가 엔진 및 민감도 분석

**포함 메서드:**
1. **getName()**: 엔진 이름 반환 ('DCF')
2. **validate()**: 입력 검증 (cashFlows, wacc, terminalGrowthRate)
3. **calculate()**: DCF 계산 (NPV + Terminal Value)
4. **performSensitivityAnalysis()**: 민감도 분석 (WACC × Growth)

**개선 사항:**
- ✅ FCF 계산 함수
- ✅ 입력 검증 (필수 필드, 범위)
- ✅ 중간 계산 결과 반환
- ✅ 민감도 분석 병렬 처리
- ✅ JSDoc 주석

---

## 완료 기준

### 필수 (Must Have)
- [ ] DCFEngine 클래스 구현
- [ ] ValuationEngine 상속 확인
- [ ] calculate() 메서드 구현
- [ ] 민감도 분석 구현
- [ ] 입력 검증 로직

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] DCF 계산 결과 확인
- [ ] 민감도 분석 매트릭스 확인
- [ ] WACC > Growth 검증 테스트

### 구현 항목 (Implementation)
- [ ] 정확성: FCF 수식, NPV, Terminal Value
- [ ] 성능: 민감도 분석 병렬 처리
- [ ] 코드 품질: JSDoc, 타입 안전성
- [ ] 확장성: 중간 결과 반환, 범위 설정

---

## 참조

### DCF 수식
```
FCF = NOPAT + 감가상각 - Capex - ΔWC
NPV = Σ(FCFt / (1+WACC)^t)
Terminal Value = FCF_마지막 × (1+g) / (WACC-g)
Enterprise Value = NPV + PV(Terminal Value)
Equity Value = EV - Net Debt
Share Price = Equity Value / Shares Outstanding
```

### 민감도 분석 매트릭스
```
        Growth -1%  -0.5%   0%    +0.5%  +1%
WACC
-2%       1000    1050   1100   1150   1200
-1%        950    1000   1050   1100   1150
 0%        900     950   1000   1050   1100
+1%        850     900    950   1000   1050
+2%        800     850    900    950   1000
```

### 관련 Task
- **S3BA1**: Valuation Engine (Abstract class)
- **S3BA2**: Financial Math (NPV, Terminal Value)
- **S3BA4**: Other Engines (Relative, Asset, Intrinsic, Tax)

---

## 주의사항

### 🔢 계산 정확성

1. **FCF 계산**
   - NOPAT + 감가상각 - Capex - ΔWC
   - 모든 항목 원 단위 반올림

2. **Terminal Value**
   - Growth Rate < WACC 필수
   - WACC - Growth = 0 방지

3. **민감도 분석**
   - WACC > Growth인 경우만 계산
   - 나머지는 NaN 처리

### ⚡ 성능

1. **병렬 처리**
   - Promise.all로 모든 시나리오 병렬 실행
   - 4×4 = 16개 시나리오 동시 계산

2. **중복 계산 제거**
   - 기본 NPV 재사용
   - 불필요한 배열 복사 방지

### 📝 코드 품질

1. **ValuationEngine 인터페이스**
   - getName(), validate(), calculate() 구현
   - 일관된 반환 타입

2. **중간 결과 반환**
   - NPV, Terminal Value, PV(TV) 반환
   - 디버깅 및 검증 용이

---

## 예상 소요 시간

**작업 복잡도**: Medium-High
**파일 수**: 1개
**라인 수**: ~350줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경
