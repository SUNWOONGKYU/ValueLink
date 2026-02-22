/**
 * @task S3BA1
 * @description Valuation Engine 공통 타입 정의
 *
 * 모든 평가 엔진(DCF, Relative, Asset, Intrinsic, Tax)이 공유하는
 * 입력/출력 인터페이스, 에러 클래스, 민감도 분석 타입을 정의합니다.
 */

// ---------------------------------------------------------------------------
// Input Types
// ---------------------------------------------------------------------------

/**
 * 비교 대상 기업 정보
 *
 * 상대가치 평가법(Relative Valuation)에서 유사기업 멀티플 산정에 사용됩니다.
 */
export interface ComparableCompany {
  /** 비교기업명 */
  name: string;
  /** 시가총액 (원) */
  marketCap: number;
  /** 매출액 (원) */
  revenue: number;
  /** EBITDA (원) */
  ebitda: number;
  /** 기업가치 (원) - EV = 시가총액 + 순차입금 */
  enterpriseValue: number;
}

/**
 * 자산 조정 항목
 *
 * 자산가치 평가법(Asset-based Valuation)에서 장부가액을 공정가치로
 * 조정할 때 사용되는 가감 항목입니다.
 */
export interface AssetAdjustments {
  /** 재고자산 평가 조정액 (원) - 양수: 증가, 음수: 감소 */
  inventory: number;
  /** 무형자산 평가 조정액 (원) - 양수: 증가, 음수: 감소 */
  intangibles: number;
}

/**
 * 평가 엔진 공통 입력 데이터
 *
 * 5개 평가법(DCF, 상대가치, 자산가치, 본질가치, 세법) 모두에서
 * 사용 가능한 통합 입력 인터페이스입니다. 각 평가법은 필요한
 * 필드만 선택적으로 사용합니다.
 */
export interface ValuationInput {
  /** 평가 방법 ('dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax') */
  method: string;

  /** 프로젝트 ID (VL-YYYYMMDD-XXXX 형식) */
  projectId: string;

  // --- DCF (현금흐름할인법) 관련 ---

  /** 예상 미래 현금흐름 배열 (원) - 연도별 FCF */
  cashFlows?: number[];

  /** 가중평균자본비용 (소수, 예: 0.1 = 10%) */
  wacc?: number;

  /** 영구성장률 (소수, 예: 0.02 = 2%) */
  terminalGrowthRate?: number;

  /** 순차입금 (원) - 유이자부채 - 현금성자산 */
  netDebt?: number;

  /** 발행주식수 (주) */
  sharesOutstanding?: number;

  // --- Relative (상대가치법) 관련 ---

  /** 대상기업 매출액 (원) */
  revenue?: number;

  /** 대상기업 EBITDA (원) */
  ebitda?: number;

  /** 비교 대상 기업 목록 */
  comparableCompanies?: ComparableCompany[];

  // --- Asset (자산가치법) 관련 ---

  /** 총자산 (원) */
  assets?: number;

  /** 총부채 (원) */
  liabilities?: number;

  /** 자산 조정 항목 */
  assetAdjustments?: AssetAdjustments;

  // --- Intrinsic (본질가치법) 관련 ---

  /** 자기자본이익률 (소수, 예: 0.15 = 15%) */
  roe?: number;

  /** 1주당 장부가액 (원) */
  bookValue?: number;

  /** 당기순이익 (원) */
  netIncome?: number;

  /** 자기자본 (원) */
  equity?: number;

  // --- Tax (세법 기준 평가) 관련 ---

  /** 1주당 순이익 (원) */
  earnings?: number;

  /** 할인율 (소수, 예: 0.1 = 10%) - 세법 기준 할인율 */
  discountRate?: number;

  /** 순자산가치 가중치 (소수, 0~1) - 세법상 자산가치 비중 */
  navWeight?: number;
}

// ---------------------------------------------------------------------------
// Output Types
// ---------------------------------------------------------------------------

/**
 * 평가 엔진 실행 결과
 *
 * 모든 평가 엔진이 반환하는 공통 결과 구조입니다.
 * `details` 필드에 평가법별 상세 산출 내역이 포함됩니다.
 */
export interface ValuationResult {
  /** 사용된 평가 방법 */
  method: string;

  /** 기업가치 (원) - Enterprise Value */
  enterpriseValue: number;

  /** 주주가치 (원) - Equity Value = EV - 순차입금 */
  equityValue: number;

  /** 1주당 가치 (원) - Share Price = Equity Value / 발행주식수 */
  sharePrice: number;

  /** 평가법별 상세 산출 내역 (자유 형식) */
  details: Record<string, unknown>;

  /** 계산 소요 시간 (밀리초) */
  duration: number;

  /** 결과 생성 시각 (ISO 8601) */
  timestamp: string;
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

/**
 * 입력 데이터 유효성 검증 결과
 */
export interface ValidationResult {
  /** 유효성 검증 통과 여부 */
  valid: boolean;

  /** 검증 실패 시 에러 메시지 (한국어) */
  error?: string;
}

// ---------------------------------------------------------------------------
// Error
// ---------------------------------------------------------------------------

/**
 * 평가 엔진 전용 에러 클래스
 *
 * 평가 계산 중 발생하는 에러에 평가법 이름과 에러 코드를
 * 부가 정보로 포함합니다.
 *
 * @example
 * ```typescript
 * throw new ValuationError(
 *   '할인율이 영구성장률보다 커야 합니다.',
 *   'dcf',
 *   'INVALID_WACC'
 * );
 * ```
 */
export class ValuationError extends Error {
  /** 에러가 발생한 평가 방법 */
  public readonly method: string;

  /** 에러 분류 코드 */
  public readonly code: string;

  constructor(message: string, method: string, code: string) {
    super(message);
    this.name = 'ValuationError';
    this.method = method;
    this.code = code;

    // ES5 환경 호환을 위한 프로토타입 체인 복원
    Object.setPrototypeOf(this, ValuationError.prototype);
  }
}

// ---------------------------------------------------------------------------
// Sensitivity Analysis
// ---------------------------------------------------------------------------

/**
 * 민감도 분석 개별 시나리오
 *
 * WACC와 영구성장률 조합별 산출 결과를 나타냅니다.
 */
export interface SensitivityScenario {
  /** 시나리오에 적용된 WACC (소수) */
  wacc: number;

  /** 시나리오에 적용된 영구성장률 (소수) */
  growthRate: number;

  /** 산출된 기업가치 (원) */
  enterpriseValue: number;

  /** 산출된 주주가치 (원) */
  equityValue: number;

  /** 산출된 1주당 가치 (원) */
  sharePrice: number;
}

/**
 * 민감도 분석 종합 결과
 *
 * DCF 평가에서 핵심 변수(WACC, 영구성장률) 변동에 따른
 * 기업가치 변화를 매트릭스 형태로 제공합니다.
 */
export interface SensitivityAnalysisResult {
  /** 분석에 사용된 WACC 범위 배열 (소수) */
  waccRange: number[];

  /** 분석에 사용된 영구성장률 범위 배열 (소수) */
  growthRange: number[];

  /**
   * 기업가치 매트릭스 (2차원 배열)
   *
   * matrix[i][j] = waccRange[i]와 growthRange[j] 조합의 기업가치
   */
  matrix: number[][];

  /** 모든 시나리오 목록 (상세 정보 포함) */
  scenarios: SensitivityScenario[];
}
