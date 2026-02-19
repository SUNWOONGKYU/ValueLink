/**
 * @task S2F1
 * @description 기업가치 평가 결과 타입 정의 (5개 방법론)
 *
 * DCF, 상대가치, 자산가치, 본질가치, 상증세법 평가 결과를 표현하는
 * TypeScript 인터페이스 및 유니온 타입
 */

// ---------------------------------------------------------------------------
// 공통 (Base)
// ---------------------------------------------------------------------------

/** 5가지 평가 방법론 */
export type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'

/** 모든 평가 결과가 공유하는 기본 필드 */
export interface BaseValuationResult {
  result_id: string
  project_id: string
  company_name: string
  valuation_method: ValuationMethod
  valuation_date: string
  shares_outstanding: number
  enterprise_value: number
  equity_value: number
  value_per_share: number
  created_at: string
  updated_at: string
}

// ---------------------------------------------------------------------------
// DCF (현금흐름할인법)
// ---------------------------------------------------------------------------

/** FCFF 연도별 데이터 */
export interface FCFFYearData {
  year: number
  revenue: number
  ebit: number
  depreciation: number
  capex: number
  working_capital_change: number
  fcff: number
  discount_factor: number
  present_value: number
}

/** WACC 구성 요소 */
export interface WACCComponents {
  risk_free_rate: number
  market_risk_premium: number
  levered_beta: number
  size_premium: number
  cost_of_equity: number
  cost_of_debt: number
  tax_rate: number
  equity_ratio: number
  debt_ratio: number
  wacc: number
}

export interface DCFResult extends BaseValuationResult {
  valuation_method: 'dcf'
  wacc_components: WACCComponents
  fcff_projections: FCFFYearData[]
  terminal_growth_rate: number
  terminal_value: number
  pv_terminal_value: number
  pv_fcff_sum: number
  operating_value: number
  non_operating_assets: number
  interest_bearing_debt: number
  sensitivity_analysis?: {
    wacc_range: number[]
    growth_range: number[]
    value_matrix: number[][]
  }
}

// ---------------------------------------------------------------------------
// Relative (상대가치평가)
// ---------------------------------------------------------------------------

/** 유사기업 데이터 */
export interface ComparableCompany {
  name: string
  market_cap: number
  per: number
  pbr: number
  psr: number
  ev_ebitda: number
  ev_sales: number
}

/** 멀티플 가중치 */
export interface MultipleWeights {
  per: number
  pbr: number
  psr: number
  ev_ebitda: number
  ev_sales: number
}

/** 멀티플별 주당가치 */
export interface MultipleValues {
  per_value: number
  pbr_value: number
  psr_value: number
  ev_ebitda_value: number
  ev_sales_value: number
}

export interface RelativeResult extends BaseValuationResult {
  valuation_method: 'relative'
  target_financials: {
    net_income: number
    equity: number
    revenue: number
    ebitda: number
    net_debt: number
  }
  comparable_companies: ComparableCompany[]
  average_multiples: {
    per: number
    pbr: number
    psr: number
    ev_ebitda: number
    ev_sales: number
  }
  calc_method: 'average' | 'median'
  weights: MultipleWeights
  per_share_values: MultipleValues
  weighted_market_cap: number
  liquidity_discount: number
  discounted_value_per_share: number | null
}

// ---------------------------------------------------------------------------
// Asset (자산가치평가 - 순자산가치법 NAV)
// ---------------------------------------------------------------------------

/** 자산/부채 항목 (장부가, 시가조정, 시가) */
export interface BalanceSheetItem {
  name: string
  book_value: number
  adjustment: number
  market_value: number
}

export interface AssetResult extends BaseValuationResult {
  valuation_method: 'asset'
  current_assets: BalanceSheetItem[]
  non_current_assets: BalanceSheetItem[]
  current_liabilities: BalanceSheetItem[]
  non_current_liabilities: BalanceSheetItem[]
  totals: {
    total_assets_book: number
    total_assets_adjustment: number
    total_assets_market: number
    total_liabilities_book: number
    total_liabilities_adjustment: number
    total_liabilities_market: number
    nav_book: number
    nav_market: number
  }
  nav_discount_rate: number
  navps_original: number
  navps_adjusted: number
}

// ---------------------------------------------------------------------------
// Intrinsic (본질가치 - 자본시장법)
// ---------------------------------------------------------------------------

export interface IntrinsicResult extends BaseValuationResult {
  valuation_method: 'intrinsic'
  industry: string
  capitalization_rate: number
  income_3years: {
    year1: number
    year2: number
    year3: number
    average: number
  }
  nav_value: number
  income_value: number
  per_share_income_value: number
  per_share_asset_value: number
  asset_weight: number
  income_weight: number
  intrinsic_value_per_share: number
}

// ---------------------------------------------------------------------------
// Tax (상증세법 보충적 평가)
// ---------------------------------------------------------------------------

/** 연도별 순손익 데이터 */
export interface YearlyProfitData {
  year_label: string
  income: number
  non_taxable: number
  tax: number
  net_profit: number
  weight: number
}

export interface TaxResult extends BaseValuationResult {
  valuation_method: 'tax'
  company_type: 'general' | 'realestate'
  yearly_profits: YearlyProfitData[]
  weighted_avg_profit: number
  discount_rate: number
  profit_value_per_share: number
  total_assets: number
  total_liabilities: number
  net_assets: number
  asset_value_per_share: number
  profit_weight: number
  asset_weight: number
  final_value_per_share: number
}

// ---------------------------------------------------------------------------
// Union
// ---------------------------------------------------------------------------

export type ValuationResult =
  | DCFResult
  | RelativeResult
  | AssetResult
  | IntrinsicResult
  | TaxResult
