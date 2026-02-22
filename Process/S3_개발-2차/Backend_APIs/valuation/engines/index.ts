/**
 * @task S3BA1
 * @description 5개 평가 엔진 스텁 (Placeholder)
 *
 * 각 평가법 엔진의 기본 골격을 정의합니다.
 * 실제 계산 로직은 후속 Task에서 구현됩니다.
 *
 * 지원 평가법:
 * - DCF (현금흐름할인법)
 * - Relative (상대가치법)
 * - Asset (자산가치법)
 * - Intrinsic (본질가치법)
 * - Tax (세법 기준 평가법)
 */

import { ValuationEngine } from '../valuation-engine';
import type {
  ValuationInput,
  ValuationResult,
  ValidationResult,
} from '../types';
import { ValuationError } from '../types';

// ---------------------------------------------------------------------------
// DCF Engine (현금흐름할인법)
// ---------------------------------------------------------------------------

/**
 * DCF 평가 엔진 (현금흐름할인법)
 *
 * 미래 예상 현금흐름을 WACC로 할인하여 기업가치를 산출합니다.
 *
 * 필수 입력: cashFlows, wacc, terminalGrowthRate, netDebt, sharesOutstanding
 */
export class DCFEngine extends ValuationEngine {
  getName(): string {
    return 'dcf';
  }

  /**
   * DCF 고유 입력 검증
   *
   * 기본 검증에 더해 DCF에 필요한 필드를 추가 검증합니다.
   */
  validate(data: ValuationInput): ValidationResult {
    const baseResult = super.validate(data);
    if (!baseResult.valid) return baseResult;

    if (!data.cashFlows || data.cashFlows.length === 0) {
      return {
        valid: false,
        error: '현금흐름(cashFlows) 데이터가 필요합니다.',
      };
    }

    if (data.wacc === undefined || data.wacc === null) {
      return {
        valid: false,
        error: '가중평균자본비용(WACC)이 필요합니다.',
      };
    }

    if (data.wacc <= 0 || data.wacc >= 1) {
      return {
        valid: false,
        error: 'WACC는 0보다 크고 1보다 작아야 합니다.',
      };
    }

    if (
      data.terminalGrowthRate !== undefined &&
      data.terminalGrowthRate !== null
    ) {
      if (data.terminalGrowthRate >= data.wacc) {
        return {
          valid: false,
          error:
            '영구성장률(terminalGrowthRate)은 WACC보다 작아야 합니다.',
        };
      }
    }

    if (data.sharesOutstanding !== undefined && data.sharesOutstanding <= 0) {
      return {
        valid: false,
        error: '발행주식수(sharesOutstanding)는 0보다 커야 합니다.',
      };
    }

    return { valid: true };
  }

  async calculate(_data: ValuationInput): Promise<ValuationResult> {
    throw new ValuationError(
      'DCF 엔진이 아직 구현되지 않았습니다. 후속 Task에서 구현 예정입니다.',
      this.getName(),
      'NOT_IMPLEMENTED'
    );
  }
}

// ---------------------------------------------------------------------------
// Relative Engine (상대가치법)
// ---------------------------------------------------------------------------

/**
 * 상대가치 평가 엔진
 *
 * 유사기업의 시장 멀티플(PER, PSR, EV/EBITDA 등)을 적용하여
 * 대상기업의 가치를 산출합니다.
 *
 * 필수 입력: comparableCompanies, revenue 또는 ebitda
 */
export class RelativeEngine extends ValuationEngine {
  getName(): string {
    return 'relative';
  }

  /**
   * 상대가치법 고유 입력 검증
   */
  validate(data: ValuationInput): ValidationResult {
    const baseResult = super.validate(data);
    if (!baseResult.valid) return baseResult;

    if (
      !data.comparableCompanies ||
      data.comparableCompanies.length === 0
    ) {
      return {
        valid: false,
        error: '비교기업(comparableCompanies) 목록이 필요합니다.',
      };
    }

    if (
      (data.revenue === undefined || data.revenue === null) &&
      (data.ebitda === undefined || data.ebitda === null)
    ) {
      return {
        valid: false,
        error:
          '대상기업의 매출액(revenue) 또는 EBITDA 중 하나 이상이 필요합니다.',
      };
    }

    return { valid: true };
  }

  async calculate(_data: ValuationInput): Promise<ValuationResult> {
    throw new ValuationError(
      '상대가치 엔진이 아직 구현되지 않았습니다. 후속 Task에서 구현 예정입니다.',
      this.getName(),
      'NOT_IMPLEMENTED'
    );
  }
}

// ---------------------------------------------------------------------------
// Asset Engine (자산가치법)
// ---------------------------------------------------------------------------

/**
 * 자산가치 평가 엔진
 *
 * 기업의 순자산가치(총자산 - 총부채 +/- 조정)를 기반으로
 * 기업가치를 산출합니다.
 *
 * 필수 입력: assets, liabilities
 */
export class AssetEngine extends ValuationEngine {
  getName(): string {
    return 'asset';
  }

  /**
   * 자산가치법 고유 입력 검증
   */
  validate(data: ValuationInput): ValidationResult {
    const baseResult = super.validate(data);
    if (!baseResult.valid) return baseResult;

    if (data.assets === undefined || data.assets === null) {
      return {
        valid: false,
        error: '총자산(assets) 데이터가 필요합니다.',
      };
    }

    if (data.assets < 0) {
      return {
        valid: false,
        error: '총자산(assets)은 0 이상이어야 합니다.',
      };
    }

    if (data.liabilities === undefined || data.liabilities === null) {
      return {
        valid: false,
        error: '총부채(liabilities) 데이터가 필요합니다.',
      };
    }

    if (data.liabilities < 0) {
      return {
        valid: false,
        error: '총부채(liabilities)는 0 이상이어야 합니다.',
      };
    }

    return { valid: true };
  }

  async calculate(_data: ValuationInput): Promise<ValuationResult> {
    throw new ValuationError(
      '자산가치 엔진이 아직 구현되지 않았습니다. 후속 Task에서 구현 예정입니다.',
      this.getName(),
      'NOT_IMPLEMENTED'
    );
  }
}

// ---------------------------------------------------------------------------
// Intrinsic Engine (본질가치법)
// ---------------------------------------------------------------------------

/**
 * 본질가치 평가 엔진
 *
 * 자기자본이익률(ROE)과 장부가액을 기반으로 기업의
 * 내재적 가치(본질가치)를 산출합니다.
 *
 * 필수 입력: roe, bookValue, netIncome, equity
 */
export class IntrinsicEngine extends ValuationEngine {
  getName(): string {
    return 'intrinsic';
  }

  /**
   * 본질가치법 고유 입력 검증
   */
  validate(data: ValuationInput): ValidationResult {
    const baseResult = super.validate(data);
    if (!baseResult.valid) return baseResult;

    if (data.roe === undefined || data.roe === null) {
      return {
        valid: false,
        error: '자기자본이익률(ROE) 데이터가 필요합니다.',
      };
    }

    if (data.bookValue === undefined || data.bookValue === null) {
      return {
        valid: false,
        error: '1주당 장부가액(bookValue) 데이터가 필요합니다.',
      };
    }

    if (data.bookValue <= 0) {
      return {
        valid: false,
        error: '1주당 장부가액(bookValue)은 0보다 커야 합니다.',
      };
    }

    if (data.netIncome === undefined || data.netIncome === null) {
      return {
        valid: false,
        error: '당기순이익(netIncome) 데이터가 필요합니다.',
      };
    }

    if (data.equity === undefined || data.equity === null) {
      return {
        valid: false,
        error: '자기자본(equity) 데이터가 필요합니다.',
      };
    }

    if (data.equity <= 0) {
      return {
        valid: false,
        error: '자기자본(equity)은 0보다 커야 합니다.',
      };
    }

    return { valid: true };
  }

  async calculate(_data: ValuationInput): Promise<ValuationResult> {
    throw new ValuationError(
      '본질가치 엔진이 아직 구현되지 않았습니다. 후속 Task에서 구현 예정입니다.',
      this.getName(),
      'NOT_IMPLEMENTED'
    );
  }
}

// ---------------------------------------------------------------------------
// Tax Engine (세법 기준 평가법)
// ---------------------------------------------------------------------------

/**
 * 세법 기준 평가 엔진
 *
 * 상속세 및 증여세법에 따른 비상장주식 평가 방법으로,
 * 순자산가치와 순손익가치를 가중평균하여 1주당 가치를 산출합니다.
 *
 * 필수 입력: earnings, bookValue, discountRate, navWeight
 */
export class TaxEngine extends ValuationEngine {
  getName(): string {
    return 'tax';
  }

  /**
   * 세법 기준 평가법 고유 입력 검증
   */
  validate(data: ValuationInput): ValidationResult {
    const baseResult = super.validate(data);
    if (!baseResult.valid) return baseResult;

    if (data.earnings === undefined || data.earnings === null) {
      return {
        valid: false,
        error: '1주당 순이익(earnings) 데이터가 필요합니다.',
      };
    }

    if (data.bookValue === undefined || data.bookValue === null) {
      return {
        valid: false,
        error: '1주당 장부가액(bookValue) 데이터가 필요합니다.',
      };
    }

    if (data.bookValue <= 0) {
      return {
        valid: false,
        error: '1주당 장부가액(bookValue)은 0보다 커야 합니다.',
      };
    }

    if (data.discountRate === undefined || data.discountRate === null) {
      return {
        valid: false,
        error: '할인율(discountRate) 데이터가 필요합니다.',
      };
    }

    if (data.discountRate <= 0 || data.discountRate >= 1) {
      return {
        valid: false,
        error: '할인율(discountRate)은 0보다 크고 1보다 작아야 합니다.',
      };
    }

    if (data.navWeight === undefined || data.navWeight === null) {
      return {
        valid: false,
        error: '순자산가치 가중치(navWeight) 데이터가 필요합니다.',
      };
    }

    if (data.navWeight < 0 || data.navWeight > 1) {
      return {
        valid: false,
        error:
          '순자산가치 가중치(navWeight)는 0 이상 1 이하여야 합니다.',
      };
    }

    return { valid: true };
  }

  async calculate(_data: ValuationInput): Promise<ValuationResult> {
    throw new ValuationError(
      '세법 기준 평가 엔진이 아직 구현되지 않았습니다. 후속 Task에서 구현 예정입니다.',
      this.getName(),
      'NOT_IMPLEMENTED'
    );
  }
}
