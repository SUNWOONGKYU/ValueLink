/**
 * @task S3BA4
 * @description Tax (세법상 평가) 엔진
 *
 * 상속세 및 증여세법에 따른 비상장주식의 보충적 평가 방법을 구현합니다.
 * 순자산가치와 수익가치의 가중평균으로 1주당 가액을 산출합니다.
 *
 * 핵심 수식:
 *   NAV (순자산가치) = 자산 - 부채
 *   수익가치 = 순이익 / 할인율  (환원가치)
 *   가중평균 = NAV * navWeight + 수익가치 * (1 - navWeight)
 *   Share Price = 가중평균 / 발행주식수
 *
 * 법정 가중치:
 *   - 일반 기업: 순자산 60% + 수익 40% (기본)
 *   - 부동산 과다 기업: 순자산 80% + 수익 20%
 *
 * 참고: 상속세 및 증여세법 제63조 (비상장주식의 평가)
 */

import {
  ValuationInput,
  ValuationResult,
  ValidationResult,
} from '../types';
import { ValuationEngine } from '../valuation-engine';

/**
 * 세법상 평가 엔진
 *
 * 순자산가치와 수익가치의 가중평균으로 비상장주식의 1주당 가액을 산출합니다.
 * 상속/증여 세무 목적의 기업가치 평가에 사용됩니다.
 *
 * @example
 * ```typescript
 * const engine = new TaxEngine();
 * const result = await engine.calculate({
 *   method: 'tax',
 *   projectId: 'VL-20260222-0001',
 *   assets: 15_000_000_000,
 *   liabilities: 5_000_000_000,
 *   earnings: 1_233_333_333,
 *   discountRate: 0.1,
 *   navWeight: 0.6,
 *   sharesOutstanding: 10_000_000,
 * });
 * ```
 */
class TaxEngine extends ValuationEngine {
  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * 엔진 이름을 반환합니다.
   *
   * @returns 'Tax'
   */
  getName(): string {
    return 'Tax';
  }

  /**
   * 세법상 평가를 위한 입력 데이터 유효성을 검증합니다.
   *
   * 검증 항목:
   * 1. 부모 클래스 기본 검증
   * 2. 총자산(assets) > 0
   * 3. 총부채(liabilities) >= 0
   * 4. 수익(earnings) > 0
   * 5. 할인율(discountRate) 0 < x < 1
   *
   * @param data - 평가 입력 데이터
   * @returns 유효성 검증 결과
   */
  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data);
    if (!baseValidation.valid) return baseValidation;

    if (!data.assets || data.assets <= 0) {
      return {
        valid: false,
        error: '총자산(assets)은 0보다 커야 합니다.',
      };
    }

    if (data.liabilities === undefined || data.liabilities === null || data.liabilities < 0) {
      return {
        valid: false,
        error: '총부채(liabilities)는 0 이상이어야 합니다.',
      };
    }

    if (!data.earnings || data.earnings <= 0) {
      return {
        valid: false,
        error: '순이익(earnings)은 0보다 커야 합니다. 적자 기업은 세법상 평가의 수익가치 산출이 불가합니다.',
      };
    }

    if (!data.discountRate || data.discountRate <= 0 || data.discountRate >= 1) {
      return {
        valid: false,
        error: '할인율(discountRate)은 0보다 크고 1보다 작아야 합니다.',
      };
    }

    return { valid: true };
  }

  /**
   * 세법상 평가를 수행합니다.
   *
   * 계산 흐름:
   *   1. 순자산가치(NAV) = 자산 - 부채
   *   2. 수익가치 = 순이익 / 할인율 (환원법)
   *   3. 가중평균 = NAV * navWeight + 수익가치 * (1 - navWeight)
   *   4. 주당가치 = 가중평균 / 발행주식수
   *
   * @param data - 평가 입력 데이터
   * @returns 평가 결과 (NAV, 수익가치, 가중평균, 주당가치)
   * @throws Error 입력 검증 실패 또는 계산 오류 시
   */
  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const startTime = Date.now();

    const validation = this.validate(data);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    try {
      const sharesOutstanding = data.sharesOutstanding || 1;

      // ----- 1. 순자산가치 (NAV) -----
      const netAssetValue = data.assets! - data.liabilities!;

      // ----- 2. 수익가치 (환원법) -----
      //   수익가치 = 순이익 / 할인율
      //   예: 1,233,333,333 / 0.1 = 12,333,333,330
      const earningsValue = data.earnings! / data.discountRate!;

      // ----- 3. 가중평균 -----
      //   기본: 순자산 60% + 수익 40%
      //   부동산 과다: 순자산 80% + 수익 20%
      const navWeight = data.navWeight || 0.6;
      const earningsWeight = 1 - navWeight;

      const weightedValue =
        netAssetValue * navWeight + earningsValue * earningsWeight;

      // ----- 4. 주당가치 -----
      const sharePrice = weightedValue / sharesOutstanding;

      const duration = Date.now() - startTime;

      return {
        method: 'Tax',
        enterpriseValue: Math.round(weightedValue),
        equityValue: Math.round(weightedValue),
        sharePrice: Math.round(sharePrice * 100) / 100,
        details: {
          netAssetValue: Math.round(netAssetValue),
          earningsValue: Math.round(earningsValue),
          navWeight,
          earningsWeight,
          weightedValue: Math.round(weightedValue),
          discountRate: data.discountRate,
          assets: Math.round(data.assets!),
          liabilities: Math.round(data.liabilities!),
          earnings: Math.round(data.earnings!),
          sharesOutstanding,
          taxLawReference: '상속세 및 증여세법 제63조 (비상장주식의 보충적 평가)',
        },
        duration,
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`세법상 평가 계산 실패: ${message}`);
    }
  }
}

export default TaxEngine;
