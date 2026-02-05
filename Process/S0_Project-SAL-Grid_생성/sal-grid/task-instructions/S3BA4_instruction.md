# S3BA4: Other Valuation Engines

## Task 정보

- **Task ID**: S3BA4
- **Task Name**: 기타 평가 엔진 (Relative, Asset, Intrinsic, Tax)
- **Stage**: S3 (Valuation Engines - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1 (Orchestrator), S3BA2 (Financial Math)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

Relative(상대가치), Asset(자산가치), Intrinsic(내재가치), Tax(세법상평가) 4개 평가 엔진 구현

---

## 상세 지시사항

### 1. Relative 평가 엔진 (상대가치평가)

**파일**: `lib/valuation/engines/relative-engine.ts`

```typescript
import { ValuationEngine, ValuationInput, ValuationResult } from '../engine-interface'
import { calculateAverage, calculateMedian } from '../financial-math'

export interface RelativeInput extends ValuationInput {
  financial_data: {
    revenue: number                  // 매출
    ebitda: number                   // EBITDA
    comparable_companies: {          // 유사기업 목록
      name: string
      ps_multiple: number            // P/S 배수
      ev_ebitda_multiple: number     // EV/EBITDA 배수
    }[]
  }
  assumptions: {
    shares_outstanding: number       // 발행주식수
    net_debt: number                 // 순부채
  }
}

export class RelativeEngine extends ValuationEngine {
  constructor() {
    super('relative')
  }

  validate(input: ValuationInput): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    const relInput = input as RelativeInput

    if (!relInput.financial_data.revenue) {
      errors.push('Revenue is required')
    }

    if (!relInput.financial_data.ebitda) {
      errors.push('EBITDA is required')
    }

    if (!relInput.financial_data.comparable_companies || relInput.financial_data.comparable_companies.length === 0) {
      errors.push('At least one comparable company is required')
    }

    if (!relInput.assumptions.shares_outstanding) {
      errors.push('Shares outstanding is required')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  async calculate(input: ValuationInput): Promise<ValuationResult> {
    const relInput = input as RelativeInput
    const { financial_data, assumptions } = relInput

    // 1. 유사기업 평균 배수 계산
    const ps_multiples = financial_data.comparable_companies.map((c) => c.ps_multiple)
    const ev_ebitda_multiples = financial_data.comparable_companies.map((c) => c.ev_ebitda_multiple)

    const avg_ps = calculateAverage(ps_multiples)
    const avg_ev_ebitda = calculateAverage(ev_ebitda_multiples)

    const median_ps = calculateMedian(ps_multiples)
    const median_ev_ebitda = calculateMedian(ev_ebitda_multiples)

    // 2. 평가 (평균 배수 사용)
    const equity_value_ps = financial_data.revenue * avg_ps
    const enterprise_value_ebitda = financial_data.ebitda * avg_ev_ebitda
    const equity_value_ebitda = enterprise_value_ebitda - assumptions.net_debt

    // 3. 최종 평가 (두 방법의 평균)
    const equity_value = (equity_value_ps + equity_value_ebitda) / 2
    const enterprise_value = equity_value + assumptions.net_debt

    // 4. 주당 가치
    const share_price = equity_value / assumptions.shares_outstanding

    // 5. 상세 계산 내역
    const calculation_details = {
      comparable_companies: financial_data.comparable_companies,
      ps_multiples: {
        average: avg_ps,
        median: median_ps,
        values: ps_multiples,
      },
      ev_ebitda_multiples: {
        average: avg_ev_ebitda,
        median: median_ev_ebitda,
        values: ev_ebitda_multiples,
      },
      equity_value_ps,
      enterprise_value_ebitda,
      equity_value_ebitda,
      equity_value,
      enterprise_value,
      share_price,
    }

    const result: ValuationResult = {
      project_id: input.project_id,
      method: 'relative',
      enterprise_value,
      equity_value,
      share_price,
      calculation_details,
      created_at: new Date().toISOString(),
    }

    await this.saveResult(result)
    return result
  }
}
```

---

### 2. Asset 평가 엔진 (자산가치평가)

**파일**: `lib/valuation/engines/asset-engine.ts`

```typescript
import { ValuationEngine, ValuationInput, ValuationResult } from '../engine-interface'

export interface AssetInput extends ValuationInput {
  financial_data: {
    total_assets: number             // 총자산
    total_liabilities: number        // 총부채
    tangible_assets: number          // 유형자산
    intangible_assets: number        // 무형자산
    current_assets: number           // 유동자산
    non_current_assets: number       // 비유동자산
  }
  assumptions: {
    asset_adjustment_rate: number    // 자산 조정률 (%)
    liability_adjustment_rate: number // 부채 조정률 (%)
    shares_outstanding: number       // 발행주식수
  }
}

export class AssetEngine extends ValuationEngine {
  constructor() {
    super('asset')
  }

  validate(input: ValuationInput): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    const assetInput = input as AssetInput

    if (!assetInput.financial_data.total_assets) {
      errors.push('Total assets is required')
    }

    if (!assetInput.financial_data.total_liabilities) {
      errors.push('Total liabilities is required')
    }

    if (!assetInput.assumptions.shares_outstanding) {
      errors.push('Shares outstanding is required')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  async calculate(input: ValuationInput): Promise<ValuationResult> {
    const assetInput = input as AssetInput
    const { financial_data, assumptions } = assetInput

    // 1. 자산 조정 (공정가치 반영)
    const adjusted_assets =
      financial_data.total_assets * (1 + assumptions.asset_adjustment_rate / 100)

    // 2. 부채 조정
    const adjusted_liabilities =
      financial_data.total_liabilities * (1 + assumptions.liability_adjustment_rate / 100)

    // 3. 순자산가치 (자기자본가치)
    const equity_value = adjusted_assets - adjusted_liabilities

    // 4. 기업가치 (자기자본가치 + 순부채)
    const net_debt = financial_data.total_liabilities - financial_data.current_assets
    const enterprise_value = equity_value + net_debt

    // 5. 주당 가치
    const share_price = equity_value / assumptions.shares_outstanding

    // 6. 상세 계산 내역
    const calculation_details = {
      total_assets: financial_data.total_assets,
      total_liabilities: financial_data.total_liabilities,
      adjusted_assets,
      adjusted_liabilities,
      equity_value,
      enterprise_value,
      share_price,
      asset_adjustment_rate: assumptions.asset_adjustment_rate,
      liability_adjustment_rate: assumptions.liability_adjustment_rate,
      breakdown: {
        tangible_assets: financial_data.tangible_assets,
        intangible_assets: financial_data.intangible_assets,
        current_assets: financial_data.current_assets,
        non_current_assets: financial_data.non_current_assets,
      },
    }

    const result: ValuationResult = {
      project_id: input.project_id,
      method: 'asset',
      enterprise_value,
      equity_value,
      share_price,
      calculation_details,
      created_at: new Date().toISOString(),
    }

    await this.saveResult(result)
    return result
  }
}
```

---

### 3. Intrinsic 평가 엔진 (내재가치평가)

**파일**: `lib/valuation/engines/intrinsic-engine.ts`

```typescript
import { ValuationEngine, ValuationInput, ValuationResult } from '../engine-interface'
import { calculateCAGR } from '../financial-math'

export interface IntrinsicInput extends ValuationInput {
  financial_data: {
    current_revenue: number          // 현재 매출
    revenue_5y_ago: number           // 5년 전 매출
    current_earnings: number         // 현재 순이익
    book_value: number               // 장부가치
  }
  assumptions: {
    expected_growth_rate: number     // 예상 성장률 (%)
    expected_roe: number             // 예상 ROE (%)
    discount_rate: number            // 할인율 (%)
    forecast_period: number          // 예측 기간 (년)
    shares_outstanding: number       // 발행주식수
  }
}

export class IntrinsicEngine extends ValuationEngine {
  constructor() {
    super('intrinsic')
  }

  validate(input: ValuationInput): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    const intrInput = input as IntrinsicInput

    if (!intrInput.financial_data.current_revenue) {
      errors.push('Current revenue is required')
    }

    if (!intrInput.assumptions.expected_growth_rate) {
      errors.push('Expected growth rate is required')
    }

    if (!intrInput.assumptions.shares_outstanding) {
      errors.push('Shares outstanding is required')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  async calculate(input: ValuationInput): Promise<ValuationResult> {
    const intrInput = input as IntrinsicInput
    const { financial_data, assumptions } = intrInput

    // 1. 과거 성장률 계산 (CAGR)
    const historical_cagr = calculateCAGR(
      financial_data.revenue_5y_ago,
      financial_data.current_revenue,
      5
    )

    // 2. 미래 수익 예측
    const future_earnings = this.projectEarnings(
      financial_data.current_earnings,
      assumptions.expected_growth_rate,
      assumptions.forecast_period
    )

    // 3. 현재가치 계산
    const pv_earnings = future_earnings.reduce((sum, earnings, t) => {
      return sum + earnings / Math.pow(1 + assumptions.discount_rate / 100, t + 1)
    }, 0)

    // 4. 자기자본가치
    const equity_value = pv_earnings + financial_data.book_value

    // 5. 기업가치 (간소화)
    const enterprise_value = equity_value * 1.1 // 간소화된 계산

    // 6. 주당 가치
    const share_price = equity_value / assumptions.shares_outstanding

    // 7. 상세 계산 내역
    const calculation_details = {
      historical_cagr,
      expected_growth_rate: assumptions.expected_growth_rate,
      future_earnings,
      pv_earnings,
      book_value: financial_data.book_value,
      equity_value,
      enterprise_value,
      share_price,
    }

    const result: ValuationResult = {
      project_id: input.project_id,
      method: 'intrinsic',
      enterprise_value,
      equity_value,
      share_price,
      calculation_details,
      created_at: new Date().toISOString(),
    }

    await this.saveResult(result)
    return result
  }

  private projectEarnings(
    current_earnings: number,
    growth_rate: number,
    periods: number
  ): number[] {
    const earnings: number[] = []
    let current = current_earnings

    for (let i = 0; i < periods; i++) {
      current = current * (1 + growth_rate / 100)
      earnings.push(current)
    }

    return earnings
  }
}
```

---

### 4. Tax 평가 엔진 (세법상평가)

**파일**: `lib/valuation/engines/tax-engine.ts`

```typescript
import { ValuationEngine, ValuationInput, ValuationResult } from '../engine-interface'

export interface TaxInput extends ValuationInput {
  financial_data: {
    net_asset_value: number          // 순자산가치
    earning_value: number            // 수익가치
    recent_3y_avg_earnings: number   // 최근 3년 평균 순이익
    capitalization_rate: number      // 자본환원율 (%)
  }
  assumptions: {
    weight_nav: number               // 순자산가치 가중치 (%)
    weight_earnings: number          // 수익가치 가중치 (%)
    shares_outstanding: number       // 발행주식수
  }
}

export class TaxEngine extends ValuationEngine {
  constructor() {
    super('tax')
  }

  validate(input: ValuationInput): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    const taxInput = input as TaxInput

    if (!taxInput.financial_data.net_asset_value) {
      errors.push('Net asset value is required')
    }

    if (!taxInput.financial_data.recent_3y_avg_earnings) {
      errors.push('Recent 3-year average earnings is required')
    }

    if (!taxInput.financial_data.capitalization_rate) {
      errors.push('Capitalization rate is required')
    }

    if (!taxInput.assumptions.shares_outstanding) {
      errors.push('Shares outstanding is required')
    }

    // 가중치 합계 검증
    const weight_sum = taxInput.assumptions.weight_nav + taxInput.assumptions.weight_earnings
    if (weight_sum !== 100) {
      errors.push('Weight sum must be 100%')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  async calculate(input: ValuationInput): Promise<ValuationResult> {
    const taxInput = input as TaxInput
    const { financial_data, assumptions } = taxInput

    // 1. 수익가치 계산
    const earning_value = financial_data.recent_3y_avg_earnings / (financial_data.capitalization_rate / 100)

    // 2. 가중평균 기업가치
    const enterprise_value =
      (financial_data.net_asset_value * assumptions.weight_nav) / 100 +
      (earning_value * assumptions.weight_earnings) / 100

    // 3. 자기자본가치 (세법상 평가에서는 동일)
    const equity_value = enterprise_value

    // 4. 주당 가치
    const share_price = equity_value / assumptions.shares_outstanding

    // 5. 상세 계산 내역
    const calculation_details = {
      net_asset_value: financial_data.net_asset_value,
      earning_value,
      weight_nav: assumptions.weight_nav,
      weight_earnings: assumptions.weight_earnings,
      enterprise_value,
      equity_value,
      share_price,
      recent_3y_avg_earnings: financial_data.recent_3y_avg_earnings,
      capitalization_rate: financial_data.capitalization_rate,
    }

    const result: ValuationResult = {
      project_id: input.project_id,
      method: 'tax',
      enterprise_value,
      equity_value,
      share_price,
      calculation_details,
      created_at: new Date().toISOString(),
    }

    await this.saveResult(result)
    return result
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/valuation/engines/relative-engine.ts` | Relative 엔진 | ~130줄 |
| `lib/valuation/engines/asset-engine.ts` | Asset 엔진 | ~120줄 |
| `lib/valuation/engines/intrinsic-engine.ts` | Intrinsic 엔진 | ~130줄 |
| `lib/valuation/engines/tax-engine.ts` | Tax 엔진 | ~120줄 |

**총 파일 수**: 4개
**총 라인 수**: ~500줄

---

## 기술 스택

- **TypeScript 5.x**: 타입 안전성
- **Valuation Engine Interface**: S3BA1에서 정의한 인터페이스 상속
- **Financial Math Library**: S3BA2에서 구현한 함수 사용

---

## 완료 기준

### 필수 (Must Have)

- [ ] Relative 평가 엔진 구현
- [ ] Asset 평가 엔진 구현
- [ ] Intrinsic 평가 엔진 구현
- [ ] Tax 평가 엔진 구현
- [ ] 각 엔진의 validate 메서드 구현
- [ ] 각 엔진의 calculate 메서드 구현

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] 각 엔진 계산 정확성 검증
- [ ] 입력 검증 동작 확인
- [ ] 결과 저장 확인

### 권장 (Nice to Have)

- [ ] 엔진별 단위 테스트
- [ ] 엔진 등록 헬퍼 함수
- [ ] 추가 배수 (P/B, EV/Sales 등)

---

## 참조

### 기존 프로토타입
- `backend/app/services/valuation_engine/relative/relative_engine.py` (487줄)
- `backend/app/services/valuation_engine/asset/asset_engine.py` (497줄)
- `backend/app/services/valuation_engine/intrinsic/intrinsic_engine.py` (258줄)
- `backend/app/services/valuation_engine/tax/tax_engine.py` (379줄)

### 의존성
- S3BA1: Orchestrator (ValuationEngine 인터페이스)
- S3BA2: Financial Math (금융 함수)

---

## 주의사항

1. **Relative 평가**
   - 최소 1개 유사기업 필요
   - P/S와 EV/EBITDA 평균 사용

2. **Asset 평가**
   - 자산/부채 조정률 적용
   - 공정가치 반영

3. **Intrinsic 평가**
   - 과거 CAGR 계산
   - 미래 수익 예측

4. **Tax 평가**
   - 순자산가치 + 수익가치 가중평균
   - 가중치 합계 100% 검증

---

**작업 복잡도**: High
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
