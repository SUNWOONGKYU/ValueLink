# S3BA3: DCF Engine & Sensitivity Analysis

## Task 정보

- **Task ID**: S3BA3
- **Task Name**: DCF 평가 엔진 및 민감도 분석
- **Stage**: S3 (Valuation Engines - 개발 2차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S3BA1 (Orchestrator), S3BA2 (Financial Math)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

DCF(현금흐름할인법) 평가 엔진 및 민감도 분석 기능 구현

---

## 상세 지시사항

### 1. DCF 평가 엔진

**파일**: `lib/valuation/engines/dcf-engine.ts`

```typescript
import { ValuationEngine, ValuationInput, ValuationResult } from '../engine-interface'
import {
  calculateWACC,
  calculateEnterpriseValue,
  calculateEquityValue,
  calculateSharePrice,
  discountCashFlows,
} from '../financial-math'

export interface DCFInput extends ValuationInput {
  financial_data: {
    revenue_forecast: number[]      // 5년 매출 예측
    operating_margin: number         // 영업이익률 (%)
    tax_rate: number                 // 법인세율 (%)
    depreciation: number[]           // 감가상각비
    capex: number[]                  // 자본적지출
    working_capital_change: number[] // 운전자본 증감
  }
  assumptions: {
    wacc: number                     // WACC (%)
    terminal_growth_rate: number     // 영구성장률 (%)
    net_debt: number                 // 순부채
    shares_outstanding: number       // 발행주식수
  }
}

export class DCFEngine extends ValuationEngine {
  constructor() {
    super('dcf')
  }

  validate(input: ValuationInput): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    const dcfInput = input as DCFInput

    // 필수 필드 검증
    if (!dcfInput.financial_data.revenue_forecast) {
      errors.push('Revenue forecast is required')
    }

    if (dcfInput.financial_data.revenue_forecast.length !== 5) {
      errors.push('Revenue forecast must be 5 years')
    }

    if (!dcfInput.assumptions.wacc) {
      errors.push('WACC is required')
    }

    if (!dcfInput.assumptions.terminal_growth_rate) {
      errors.push('Terminal growth rate is required')
    }

    if (!dcfInput.assumptions.shares_outstanding) {
      errors.push('Shares outstanding is required')
    }

    // 논리 검증
    if (dcfInput.assumptions.wacc <= dcfInput.assumptions.terminal_growth_rate) {
      errors.push('WACC must be greater than terminal growth rate')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  async calculate(input: ValuationInput): Promise<ValuationResult> {
    const dcfInput = input as DCFInput
    const { financial_data, assumptions } = dcfInput

    // 1. Free Cash Flow 계산
    const fcf = this.calculateFreeCashFlow(financial_data)

    // 2. 기업가치 계산
    const enterprise_value = calculateEnterpriseValue(
      fcf,
      assumptions.wacc,
      assumptions.terminal_growth_rate
    )

    // 3. 자기자본가치 계산
    const equity_value = calculateEquityValue(enterprise_value, assumptions.net_debt)

    // 4. 주당 가치 계산
    const share_price = calculateSharePrice(equity_value, assumptions.shares_outstanding)

    // 5. 상세 계산 내역
    const calculation_details = {
      free_cash_flows: fcf,
      discounted_cash_flows: discountCashFlows(fcf, assumptions.wacc),
      enterprise_value,
      net_debt: assumptions.net_debt,
      equity_value,
      shares_outstanding: assumptions.shares_outstanding,
      share_price,
      wacc: assumptions.wacc,
      terminal_growth_rate: assumptions.terminal_growth_rate,
    }

    const result: ValuationResult = {
      project_id: input.project_id,
      method: 'dcf',
      enterprise_value,
      equity_value,
      share_price,
      calculation_details,
      created_at: new Date().toISOString(),
    }

    // 결과 저장
    await this.saveResult(result)

    return result
  }

  private calculateFreeCashFlow(financial_data: DCFInput['financial_data']): number[] {
    const fcf: number[] = []

    for (let i = 0; i < financial_data.revenue_forecast.length; i++) {
      const revenue = financial_data.revenue_forecast[i]
      const operating_income = revenue * (financial_data.operating_margin / 100)
      const tax = operating_income * (financial_data.tax_rate / 100)
      const nopat = operating_income - tax // Net Operating Profit After Tax

      const depreciation = financial_data.depreciation[i] || 0
      const capex = financial_data.capex[i] || 0
      const wc_change = financial_data.working_capital_change[i] || 0

      // FCF = NOPAT + Depreciation - Capex - ΔWorking Capital
      const free_cash_flow = nopat + depreciation - capex - wc_change

      fcf.push(free_cash_flow)
    }

    return fcf
  }
}
```

---

### 2. 민감도 분석

**파일**: `lib/valuation/engines/sensitivity-analysis.ts`

```typescript
import { calculateEnterpriseValue, calculateEquityValue, calculateSharePrice } from '../financial-math'

export interface SensitivityInput {
  base_fcf: number[]                // 기준 현금흐름
  base_wacc: number                 // 기준 WACC
  base_growth: number               // 기준 영구성장률
  net_debt: number                  // 순부채
  shares_outstanding: number        // 발행주식수
  wacc_range: number[]              // WACC 범위 (예: [8, 9, 10, 11, 12])
  growth_range: number[]            // 성장률 범위 (예: [2, 2.5, 3, 3.5, 4])
}

export interface SensitivityResult {
  share_prices: number[][]          // WACC x Growth 매트릭스
  wacc_range: number[]
  growth_range: number[]
  base_share_price: number
}

/**
 * 민감도 분석 수행
 * WACC와 영구성장률을 변동시켜 주가 변화 분석
 */
export function performSensitivityAnalysis(input: SensitivityInput): SensitivityResult {
  const { base_fcf, wacc_range, growth_range, net_debt, shares_outstanding } = input

  const share_prices: number[][] = []

  // WACC 반복
  for (const wacc of wacc_range) {
    const row: number[] = []

    // 성장률 반복
    for (const growth of growth_range) {
      // WACC <= 성장률이면 무한대 → 건너뛰기
      if (wacc <= growth) {
        row.push(NaN)
        continue
      }

      const enterprise_value = calculateEnterpriseValue(base_fcf, wacc, growth)
      const equity_value = calculateEquityValue(enterprise_value, net_debt)
      const share_price = calculateSharePrice(equity_value, shares_outstanding)

      row.push(share_price)
    }

    share_prices.push(row)
  }

  // 기준 주가 계산 (기준 WACC, 기준 성장률)
  const base_enterprise_value = calculateEnterpriseValue(
    base_fcf,
    input.base_wacc,
    input.base_growth
  )
  const base_equity_value = calculateEquityValue(base_enterprise_value, net_debt)
  const base_share_price = calculateSharePrice(base_equity_value, shares_outstanding)

  return {
    share_prices,
    wacc_range,
    growth_range,
    base_share_price,
  }
}

/**
 * 민감도 분석 결과를 차트 데이터로 변환
 */
export function formatSensitivityData(result: SensitivityResult) {
  const { share_prices, wacc_range, growth_range } = result

  return wacc_range.map((wacc, i) => {
    const row: Record<string, any> = { wacc: `${wacc}%` }

    growth_range.forEach((growth, j) => {
      row[`growth_${growth}`] = share_prices[i][j]
    })

    return row
  })
}
```

---

### 3. DCF 민감도 분석 API

**파일**: `app/api/valuation/dcf-sensitivity/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { performSensitivityAnalysis } from '@/lib/valuation/engines/sensitivity-analysis'

export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const {
      project_id,
      base_fcf,
      base_wacc,
      base_growth,
      net_debt,
      shares_outstanding,
      wacc_range,
      growth_range,
    } = body

    // 프로젝트 소유권 확인
    const { data: project } = await supabase
      .from('projects')
      .select('id')
      .eq('id', project_id)
      .eq('user_id', user.id)
      .single()

    if (!project) {
      return NextResponse.json(
        { error: 'Project not found or access denied' },
        { status: 404 }
      )
    }

    // 민감도 분석 수행
    const result = performSensitivityAnalysis({
      base_fcf,
      base_wacc,
      base_growth,
      net_debt,
      shares_outstanding,
      wacc_range: wacc_range || [6, 8, 10, 12, 14],
      growth_range: growth_range || [1, 2, 3, 4, 5],
    })

    return NextResponse.json({ result }, { status: 200 })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Sensitivity analysis failed' },
      { status: 500 }
    )
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/valuation/engines/dcf-engine.ts` | DCF 평가 엔진 | ~180줄 |
| `lib/valuation/engines/sensitivity-analysis.ts` | 민감도 분석 | ~100줄 |
| `app/api/valuation/dcf-sensitivity/route.ts` | 민감도 API | ~70줄 |

**총 파일 수**: 3개
**총 라인 수**: ~350줄

---

## 기술 스택

- **TypeScript 5.x**: 타입 안전성
- **Financial Math Library**: S3BA2에서 구현한 함수 사용
- **Valuation Engine Interface**: S3BA1에서 정의한 인터페이스 상속

---

## 완료 기준

### 필수 (Must Have)

- [ ] DCF 평가 엔진 구현 (`DCFEngine` 클래스)
- [ ] Free Cash Flow 계산
- [ ] 기업가치/자기자본가치/주당가치 계산
- [ ] 입력 검증 (validate 메서드)
- [ ] 민감도 분석 함수 구현
- [ ] 민감도 분석 API 구현

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] DCF 계산 정확성 검증
- [ ] 민감도 분석 매트릭스 생성 확인
- [ ] API 응답 확인

### 권장 (Nice to Have)

- [ ] 몬테카를로 시뮬레이션
- [ ] 시나리오 분석 (Base, Optimistic, Pessimistic)
- [ ] 차트 데이터 포맷 최적화

---

## 참조

### 기존 프로토타입
- `backend/app/services/valuation_engine/dcf/dcf_engine.py` (504줄 Python 버전)
- `Process/P3_프로토타입_제작/Documentation/valuation-engines.md`

### 의존성
- S3BA1: Orchestrator (ValuationEngine 인터페이스)
- S3BA2: Financial Math (금융 함수)

---

## 주의사항

1. **WACC > 성장률 검증**
   - WACC <= 성장률이면 무한대
   - 검증 로직 필수

2. **Free Cash Flow 계산**
   - FCF = NOPAT + Depreciation - Capex - ΔWC
   - 모든 항목 누락 시 0 처리

3. **민감도 분석 범위**
   - WACC: 6~14% (2% 간격)
   - 성장률: 1~5% (1% 간격)
   - 커스텀 범위 지원

4. **결과 저장**
   - `valuation_results` 테이블
   - `sensitivity_data` JSON 형식

---

**작업 복잡도**: High
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
