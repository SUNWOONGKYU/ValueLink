/**
 * @task S3BA4
 * @description Intrinsic (내재가치평가) 엔진
 *
 * 자기자본이익률(ROE)과 1주당 장부가액(Book Value)을 기반으로
 * 기업의 내재가치(Intrinsic Value)를 산출합니다.
 *
 * 핵심 수식:
 *   ROE = 당기순이익 / 자기자본  (직접 제공되지 않은 경우)
 *   Intrinsic Value = ROE * Book Value
 *   Share Price = Intrinsic Value / Shares Outstanding
 *
 * ROE가 높을수록 기업이 자기자본 대비 더 많은 이익을 창출하며,
 * 내재가치가 장부가보다 높게 산출됩니다.
 */

import {
  ValuationInput,
  ValuationResult,
  ValidationResult,
} from '../types';
import { ValuationEngine } from '../valuation-engine';

/**
 * 내재가치 평가 엔진
 *
 * ROE(자기자본이익률)와 장부가를 곱하여 기업의 내재가치를 산출합니다.
 * ROE가 직접 제공되지 않으면 당기순이익/자기자본으로 자동 계산합니다.
 *
 * @example
 * ```typescript
 * const engine = new IntrinsicEngine();
 * const result = await engine.calculate({
 *   method: 'intrinsic',
 *   projectId: 'VL-20260222-0001',
 *   roe: 0.15,
 *   bookValue: 8_000_000_000,
 *   sharesOutstanding: 10_000_000,
 * });
 * ```
 */
class IntrinsicEngine extends ValuationEngine {
  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * 엔진 이름을 반환합니다.
   *
   * @returns 'Intrinsic'
   */
  getName(): string {
    return 'Intrinsic';
  }

  /**
   * 내재가치 평가를 위한 입력 데이터 유효성을 검증합니다.
   *
   * 검증 항목:
   * 1. 부모 클래스 기본 검증
   * 2. roe 직접 제공 또는 (netIncome AND equity) 모두 제공
   * 3. bookValue 또는 equity 제공
   *
   * @param data - 평가 입력 데이터
   * @returns 유효성 검증 결과
   */
  validate(data: ValuationInput): ValidationResult {
    const baseValidation = super.validate(data);
    if (!baseValidation.valid) return baseValidation;

    // ROE 또는 (netIncome + equity)로 ROE 산출 가능해야 함
    if (!data.roe && !(data.netIncome && data.equity)) {
      return {
        valid: false,
        error: 'ROE(자기자본이익률) 또는 당기순이익(netIncome)과 자기자본(equity)이 필요합니다.',
      };
    }

    // Book Value 또는 equity 필요
    if (!data.bookValue && !data.equity) {
      return {
        valid: false,
        error: '장부가액(bookValue) 또는 자기자본(equity)이 필요합니다.',
      };
    }

    return { valid: true };
  }

  /**
   * 내재가치 평가를 수행합니다.
   *
   * 계산 흐름:
   *   1. ROE 결정: 직접 제공 또는 netIncome / equity
   *   2. Book Value 결정: bookValue 우선, 없으면 equity
   *   3. Intrinsic Value = ROE * Book Value
   *   4. Share Price = Intrinsic Value / Shares Outstanding
   *
   * @param data - 평가 입력 데이터
   * @returns 평가 결과 (내재가치, ROE, 장부가 상세)
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

      // ----- 1. ROE 산출 -----
      let roe = data.roe || 0;

      if (!roe && data.netIncome && data.equity) {
        roe = data.netIncome / data.equity;
      }

      // ----- 2. Book Value 결정 -----
      const bookValue = data.bookValue || data.equity || 0;

      // ----- 3. 내재가치 = ROE * Book Value -----
      const intrinsicValue = roe * bookValue;

      // ----- 4. 주당가치 -----
      const sharePrice = intrinsicValue / sharesOutstanding;

      const duration = Date.now() - startTime;

      return {
        method: 'Intrinsic',
        enterpriseValue: Math.round(intrinsicValue),
        equityValue: Math.round(intrinsicValue),
        sharePrice: Math.round(sharePrice),
        details: {
          roe: Math.round(roe * 10000) / 10000,
          bookValue: Math.round(bookValue),
          intrinsicValue: Math.round(intrinsicValue),
          netIncome: data.netIncome ? Math.round(data.netIncome) : undefined,
          equity: data.equity ? Math.round(data.equity) : undefined,
          sharesOutstanding,
          roeSource: data.roe ? 'provided' : 'calculated (netIncome / equity)',
          bookValueSource: data.bookValue ? 'bookValue' : 'equity',
        },
        duration,
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`내재가치 평가 계산 실패: ${message}`);
    }
  }
}

export default IntrinsicEngine;
