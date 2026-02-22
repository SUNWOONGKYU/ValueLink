/**
 * @task S3BA4
 * @description Relative (상대가치평가) 엔진
 *
 * 유사기업의 시장 배수(Multiples)를 활용하여 대상 기업의
 * 가치를 산출하는 상대가치 평가법(Comparable Company Analysis)을
 * 구현합니다.
 *
 * 사용하는 배수:
 *   - P/S (Price-to-Sales) = 시가총액 / 매출액
 *   - EV/EBITDA = 기업가치 / EBITDA
 *
 * 이상치 영향을 줄이기 위해 평균 대신 **중앙값(median)**을 사용합니다.
 */

import {
  ValuationInput,
  ValuationResult,
  ValidationResult,
  ComparableCompany,
} from '../types';
import { ValuationEngine } from '../valuation-engine';
import { calculatePS, calculateEVtoEBITDA, average, median } from '../financial-math';

/**
 * 상대가치 평가 엔진
 *
 * 유사기업의 P/S 및 EV/EBITDA 배수 중앙값을 적용하여
 * 대상 기업의 시가총액 및 주당가치를 산출합니다.
 *
 * @example
 * ```typescript
 * const engine = new RelativeEngine();
 * const result = await engine.calculate({
 *   method: 'relative',
 *   projectId: 'VL-20260222-0001',
 *   revenue: 10_000_000_000,
 *   ebitda: 2_000_000_000,
 *   sharesOutstanding: 10_000_000,
 *   comparableCompanies: [
 *     { name: 'A사', marketCap: 50e9, revenue: 15e9, ebitda: 3e9, enterpriseValue: 55e9 },
 *     { name: 'B사', marketCap: 30e9, revenue: 8e9,  ebitda: 1.6e9, enterpriseValue: 33e9 },
 *     { name: 'C사', marketCap: 40e9, revenue: 12e9, ebitda: 2.5e9, enterpriseValue: 44e9 },
 *   ],
 * });
 * ```
 */
class RelativeEngine extends ValuationEngine {
  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * 엔진 이름을 반환합니다.
   *
   * @returns 'Relative'
   */
  getName(): string {
    return 'Relative';
  }

  /**
   * 상대가치 평가를 위한 입력 데이터 유효성을 검증합니다.
   *
   * 검증 항목:
   * 1. 부모 클래스 기본 검증
   * 2. 매출액(revenue) > 0
   * 3. 비교 기업(comparableCompanies) 최소 3개
   *
   * @param data - 평가 입력 데이터
   * @returns 유효성 검증 결과
   */
  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data);
    if (!baseValidation.valid) return baseValidation;

    if (!data.revenue || data.revenue <= 0) {
      return {
        valid: false,
        error: '매출액(revenue)은 0보다 커야 합니다.',
      };
    }

    if (!data.comparableCompanies || data.comparableCompanies.length < 3) {
      return {
        valid: false,
        error: '유사기업(comparableCompanies)은 최소 3개 이상이어야 합니다. 신뢰도 높은 배수 산출을 위해 충분한 비교 기업이 필요합니다.',
      };
    }

    return { valid: true };
  }

  /**
   * 상대가치 평가를 수행합니다.
   *
   * 계산 흐름:
   *   1. 유사기업별 P/S 배수 산출 → 중앙값 적용 → 시가총액(P/S) 산출
   *   2. (EBITDA 있으면) EV/EBITDA 배수 산출 → 중앙값 적용 → 기업가치 산출
   *   3. 두 방법 모두 가능하면 평균, P/S만 가능하면 P/S 결과 사용
   *   4. 주당가치 계산
   *
   * @param data - 평가 입력 데이터
   * @returns 평가 결과
   * @throws Error 입력 검증 실패 또는 계산 오류 시
   */
  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const startTime = Date.now();

    const validation = this.validate(data);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    try {
      const comparables = data.comparableCompanies!;
      const sharesOutstanding = data.sharesOutstanding || 1;

      // ----- 1. P/S Multiple 기반 평가 -----
      const psMultiples = comparables
        .map((c: ComparableCompany) => calculatePS(c.marketCap, c.revenue))
        .filter((v: number) => v > 0 && isFinite(v));

      if (psMultiples.length === 0) {
        throw new Error('유효한 P/S 배수를 산출할 수 없습니다. 비교기업의 매출 데이터를 확인하세요.');
      }

      const medianPS = median(psMultiples);
      const avgPS = average(psMultiples);

      // 대상 기업의 P/S 기반 시가총액
      const marketCapByPS = data.revenue! * medianPS;
      const sharePriceByPS = marketCapByPS / sharesOutstanding;

      // ----- 2. EV/EBITDA Multiple 기반 평가 (선택) -----
      let marketCapByEVEBITDA = 0;
      let sharePriceByEVEBITDA = 0;
      let medianEVEBITDA = 0;
      let avgEVEBITDA = 0;

      if (data.ebitda && data.ebitda > 0) {
        const evEbitdaMultiples = comparables
          .map((c: ComparableCompany) => calculateEVtoEBITDA(c.enterpriseValue, c.ebitda))
          .filter((v: number) => v > 0 && isFinite(v));

        if (evEbitdaMultiples.length > 0) {
          medianEVEBITDA = median(evEbitdaMultiples);
          avgEVEBITDA = average(evEbitdaMultiples);

          const enterpriseValueByEBITDA = data.ebitda * medianEVEBITDA;
          const equityValueByEBITDA = enterpriseValueByEBITDA - (data.netDebt || 0);
          marketCapByEVEBITDA = equityValueByEBITDA;
          sharePriceByEVEBITDA = equityValueByEBITDA / sharesOutstanding;
        }
      }

      // ----- 3. 두 방법의 평균 (EV/EBITDA가 유효하면) -----
      let finalEquityValue = marketCapByPS;
      let finalSharePrice = sharePriceByPS;

      if (marketCapByEVEBITDA > 0) {
        finalEquityValue = (marketCapByPS + marketCapByEVEBITDA) / 2;
        finalSharePrice = (sharePriceByPS + sharePriceByEVEBITDA) / 2;
      }

      const duration = Date.now() - startTime;

      return {
        method: 'Relative',
        enterpriseValue: Math.round(finalEquityValue),
        equityValue: Math.round(finalEquityValue),
        sharePrice: Math.round(finalSharePrice),
        details: {
          medianPS: Math.round(medianPS * 100) / 100,
          avgPS: Math.round(avgPS * 100) / 100,
          marketCapByPS: Math.round(marketCapByPS),
          sharePriceByPS: Math.round(sharePriceByPS),
          medianEVEBITDA: Math.round(medianEVEBITDA * 100) / 100,
          avgEVEBITDA: Math.round(avgEVEBITDA * 100) / 100,
          marketCapByEVEBITDA: Math.round(marketCapByEVEBITDA),
          sharePriceByEVEBITDA: Math.round(sharePriceByEVEBITDA),
          comparablesCount: comparables.length,
          psMultiplesCount: psMultiples.length,
        },
        duration,
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`상대가치 평가 계산 실패: ${message}`);
    }
  }
}

export default RelativeEngine;
