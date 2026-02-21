/**
 * @task S2F2
 * @description 기업가치 평가 신청 폼 데이터 타입 정의 (5개 방법론)
 *
 * evaluation_requests 테이블 스키마(schema-v4-final.sql) 기반
 * 공통 기업정보 + 방법론별 추가 입력 필드
 */

import type { ValuationMethod } from './valuation'

// ---------------------------------------------------------------------------
// 공통 기업정보 (evaluation_requests 테이블 컬럼)
// ---------------------------------------------------------------------------

/** 모든 방법론이 공유하는 기본 폼 데이터 */
export interface BaseFormData {
  /** 기업명 (한글) - 필수 */
  company_name_kr: string
  /** 기업명 (영문) */
  company_name_en?: string
  /** 사업자등록번호 */
  business_registration_number?: string
  /** 대표자명 */
  representative_name?: string
  /** 업종 */
  industry?: string
  /** 매출액 (원) */
  revenue?: number
  /** 직원수 */
  employees?: number
  /** 설립일 */
  founded_date?: string
  /** 회사 웹사이트 */
  company_website?: string
  /** 주소 */
  address?: string
  /** 전화번호 */
  phone?: string
  /** 팩스 */
  fax?: string
  /** 평가 목적 - 필수 */
  valuation_purpose: string
  /** 평가 기준일 */
  target_date?: string
  /** 요구사항 */
  requirements?: string
  /** 예산 하한 */
  budget_min?: number
  /** 예산 상한 */
  budget_max?: number
}

// ---------------------------------------------------------------------------
// DCF (현금흐름할인법) 추가 필드
// ---------------------------------------------------------------------------

/** 연도별 매출 추정 */
export interface RevenueProjection {
  year: number
  revenue: number
}

/** DCF 폼 데이터 */
export interface DCFFormData extends BaseFormData {
  /** 매출 추정 (5년) */
  revenue_projections: RevenueProjection[]
  /** 영업이익률 (%) */
  operating_margin: number
  /** 법인세율 (%) */
  tax_rate: number
  /** 가중평균자본비용 (%) */
  wacc: number
  /** 영구성장률 (%) */
  terminal_growth_rate: number
  /** 순부채 (원) */
  net_debt: number
  /** 발행주식수 */
  shares_outstanding: number
  /** 감가상각비 (원) - 선택 */
  depreciation?: number
  /** 자본적지출 (원) - 선택 */
  capex?: number
  /** 순운전자본 변동 (원) - 선택 */
  working_capital_change?: number
}

// ---------------------------------------------------------------------------
// Relative (상대가치평가) 추가 필드
// ---------------------------------------------------------------------------

/** 유사기업 정보 */
export interface PeerCompanyInput {
  /** 기업명 */
  name: string
  /** 시가총액 (원) */
  market_cap?: number
  /** PER */
  per?: number
  /** EV/EBITDA */
  ev_ebitda?: number
  /** PBR */
  pbr?: number
  /** PSR */
  psr?: number
}

/** 상대가치 폼 데이터 */
export interface RelativeFormData extends BaseFormData {
  /** 유사기업 목록 (최소 3개) */
  peer_companies: PeerCompanyInput[]
  /** 선택 멀티플 */
  selected_multiples: SelectedMultiple[]
  /** 산업 분류 */
  industry_classification: string
  /** 당기순이익 (원) */
  net_income?: number
  /** 자기자본 (원) */
  equity?: number
  /** EBITDA (원) */
  ebitda?: number
  /** 발행주식수 */
  shares_outstanding: number
}

/** 선택된 멀티플 종류 */
export type MultipleType = 'per' | 'ev_ebitda' | 'pbr' | 'psr'

export interface SelectedMultiple {
  type: MultipleType
  weight: number
}

// ---------------------------------------------------------------------------
// Asset (자산가치평가) 추가 필드
// ---------------------------------------------------------------------------

/** 자산/부채 상세 항목 */
export interface AssetDetailItem {
  /** 항목명 */
  name: string
  /** 장부가 (원) */
  book_value: number
  /** 시가 (원) - 선택 */
  market_value?: number
  /** 비고 */
  note?: string
}

/** 자산가치 폼 데이터 */
export interface AssetFormData extends BaseFormData {
  /** 총자산 (원) */
  total_assets: number
  /** 총부채 (원) */
  total_liabilities: number
  /** 유형자산 상세 */
  tangible_assets: AssetDetailItem[]
  /** 무형자산 상세 */
  intangible_assets: AssetDetailItem[]
  /** 부동산 평가금액 (원) - 선택 */
  real_estate_value?: number
  /** 기계장치/설비 (원) - 선택 */
  equipment_value?: number
  /** 재고자산 (원) - 선택 */
  inventory_value?: number
  /** 발행주식수 */
  shares_outstanding: number
}

// ---------------------------------------------------------------------------
// Intrinsic (본질가치 - 자본시장법) 추가 필드
// ---------------------------------------------------------------------------

/** 본질가치 폼 데이터 */
export interface IntrinsicFormData extends BaseFormData {
  /** 기대수익 (원) */
  expected_earnings: number
  /** 요구수익률 (%) */
  required_return_rate: number
  /** 성장률 (%) */
  growth_rate: number
  /** 배당금 (원) - 선택 */
  dividend_amount?: number
  /** 배당성향 (%) - 선택 */
  dividend_payout_ratio?: number
  /** 장부가치 (원) */
  book_value: number
  /** 자산가치 가중치 (%) - 기본 40% */
  asset_weight: number
  /** 수익가치 가중치 (%) - 기본 60% */
  income_weight: number
  /** 발행주식수 */
  shares_outstanding: number
  /** 환원율 (%) - 선택 */
  capitalization_rate?: number
}

// ---------------------------------------------------------------------------
// Tax (상증세법 보충적 평가) 추가 필드
// ---------------------------------------------------------------------------

/** 연도별 순손익 */
export interface YearlyEarningsInput {
  /** 연도 라벨 (예: '2023년') */
  year_label: string
  /** 순손익 (원) */
  net_income: number
  /** 가중치 */
  weight: number
}

/** 상증세법 폼 데이터 */
export interface TaxFormData extends BaseFormData {
  /** 순자산가치 (원) */
  net_asset_value: number
  /** 최근 3년 순손익 */
  earnings_history: YearlyEarningsInput[]
  /** 세법상 평가 목적 */
  tax_purpose: string
  /** 1주당 액면가 (원) */
  par_value_per_share: number
  /** 발행주식수 */
  shares_outstanding: number
  /** 주요 주주 정보 */
  stockholder_info: StockholderInput[]
  /** 회사 유형 */
  company_type: 'general' | 'realestate'
  /** 자산가치 가중치 (일반: 40%, 부동산: 60%) */
  asset_weight: number
  /** 수익가치 가중치 (일반: 60%, 부동산: 40%) */
  income_weight: number
}

/** 주주 정보 */
export interface StockholderInput {
  /** 주주명 */
  name: string
  /** 보유 주식수 */
  shares: number
  /** 지분율 (%) */
  ownership_percentage: number
  /** 관계 (예: 최대주주, 특수관계인 등) */
  relationship?: string
}

// ---------------------------------------------------------------------------
// Union & Utility
// ---------------------------------------------------------------------------

/** 모든 방법론 폼 데이터 유니온 */
export type ValuationFormData =
  | DCFFormData
  | RelativeFormData
  | AssetFormData
  | IntrinsicFormData
  | TaxFormData

/** 방법론 메타데이터 */
export interface MethodMeta {
  slug: ValuationMethod
  label: string
  shortLabel: string
  description: string
  badgeColor: string
}

/** 폼 필드 에러 맵 */
export type FormErrors<T> = Partial<Record<keyof T, string>>

/** 폼 필드 타입 */
export type FormFieldType = 'text' | 'number' | 'email' | 'tel' | 'date' | 'select' | 'textarea' | 'url'

/** 폼 단계 */
export interface FormStep {
  id: string
  label: string
  description?: string
}

/** 폼 제출 결과 */
export interface SubmissionResult {
  success: boolean
  request_id?: string
  error?: string
}

// ---------------------------------------------------------------------------
// 평가 목적 선택지
// ---------------------------------------------------------------------------

export const VALUATION_PURPOSES = [
  { value: 'investment', label: '투자 검토' },
  { value: 'ma', label: 'M&A (인수합병)' },
  { value: 'ipo', label: 'IPO (상장 준비)' },
  { value: 'tax', label: '세무 (상속/증여)' },
  { value: 'litigation', label: '소송/분쟁' },
  { value: 'internal', label: '내부 경영 참고' },
  { value: 'financing', label: '자금 조달' },
  { value: 'other', label: '기타' },
] as const

// ---------------------------------------------------------------------------
// 방법론 메타데이터 상수
// ---------------------------------------------------------------------------

export const METHOD_META_MAP: Record<ValuationMethod, MethodMeta> = {
  dcf: {
    slug: 'dcf',
    label: 'DCF (현금흐름할인법)',
    shortLabel: 'DCF',
    description: '미래 현금흐름을 현재가치로 환산하여 기업가치를 평가합니다.',
    badgeColor: 'bg-blue-100 text-blue-800',
  },
  relative: {
    slug: 'relative',
    label: '상대가치평가',
    shortLabel: '상대가치',
    description: '유사 기업의 시장 멀티플을 비교하여 기업가치를 평가합니다.',
    badgeColor: 'bg-green-100 text-green-800',
  },
  asset: {
    slug: 'asset',
    label: '자산가치평가',
    shortLabel: '자산가치',
    description: '순자산가치(NAV)를 기반으로 기업가치를 평가합니다.',
    badgeColor: 'bg-amber-100 text-amber-800',
  },
  intrinsic: {
    slug: 'intrinsic',
    label: '본질가치평가 (자본시장법)',
    shortLabel: '본질가치',
    description: '자본시장법에 따른 수익가치와 자산가치를 가중평균하여 평가합니다.',
    badgeColor: 'bg-purple-100 text-purple-800',
  },
  tax: {
    slug: 'tax',
    label: '상증세법 보충적 평가',
    shortLabel: '상증세법',
    description: '상속세 및 증여세법에 따른 비상장주식 보충적 평가방법입니다.',
    badgeColor: 'bg-red-100 text-red-800',
  },
}
