/**
 * @task S3BA4
 * @description Asset (자산가치평가) 엔진
 *
 * 기업이 보유한 자산의 공정가치에서 부채를 차감하여
 * 순자산가치(NAV, Net Asset Value)를 산출하는 자산접근법
 * (Asset-based Approach)을 구현합니다.
 *
 * 핵심 수식:
 *   Adjusted Assets = Total Assets - 재고 감가(10%) - 무형자산 감가(20%)
 *   NAV = Adjusted Assets - Total Liabilities
 *   Share Price = NAV / Shares Outstanding
 *
 * 부동산, 제조업 등 유형자산 비중이 높은 기업에 적합합니다.
 */

import {
  ValuationInput,
  ValuationResult,
  ValidationResult,
} from '../types';
import { ValuationEngine } from '../valuation-engine';

/**
 * 자산가치 평가 엔진
 *
 * 총자산에서 자산 조정(재고 감가, 무형자산 감가)을 적용한 뒤
 * 부채를 차감하여 순자산가치(NAV)를 산출합니다.
 *
 * @example
 * ```typescript
 * const engine = new AssetEngine();
 * const result = await engine.calculate({
 *   method: 'asset',
 *   projectId: 'VL-20260222-0001',
 *   assets: 29_000_000_000,
 *   liabilities: 11_500_000_000,
 *   assetAdjustments: { inventory: 2_500_000_000, intangibles: 3_000_000_000 },
 *   sharesOutstanding: 10_000_000,
 * });
 * ```
 */
class AssetEngine extends ValuationEngine {
  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * 엔진 이름을 반환합니다.
   *
   * @returns 'Asset'
   */
  getName(): string {
    return 'Asset';
  }

  /**
   * 자산가치 평가를 위한 입력 데이터 유효성을 검증합니다.
   *
   * 검증 항목:
   * 1. 부모 클래스 기본 검증
   * 2. 총자산(assets) > 0
   * 3. 총부채(liabilities) >= 0
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

    return { valid: true };
  }

  /**
   * 자산가치 평가를 수행합니다.
   *
   * 계산 흐름:
   *   1. 자산 조정 적용 (재고 -10%, 무형자산 -20%)
   *   2. NAV = 조정 후 자산 - 총부채
   *   3. 주당가치 = NAV / 발행주식수
   *
   * @param data - 평가 입력 데이터
   * @returns 평가 결과 (NAV, 주당가치, 조정 상세)
   * @throws Error 입력 검증 실패 또는 계산 오류 시
   */
  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const startTime = Date.now();

    const validation = this.validate(data);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    try {
      const totalAssets = data.assets!;
      const totalLiabilities = data.liabilities!;
      const sharesOutstanding = data.sharesOutstanding || 1;

      // ----- 자산 조정 -----
      let adjustedAssets = totalAssets;
      let inventoryAdjustment = 0;
      let intangiblesAdjustment = 0;

      if (data.assetAdjustments) {
        // 재고자산 감가 (-10%)
        if (data.assetAdjustments.inventory && data.assetAdjustments.inventory > 0) {
          inventoryAdjustment = data.assetAdjustments.inventory * 0.1;
          adjustedAssets -= inventoryAdjustment;
        }

        // 무형자산 감가 (-20%)
        if (data.assetAdjustments.intangibles && data.assetAdjustments.intangibles > 0) {
          intangiblesAdjustment = data.assetAdjustments.intangibles * 0.2;
          adjustedAssets -= intangiblesAdjustment;
        }
      }

      // ----- 순자산가치(NAV) 산출 -----
      const netAssetValue = adjustedAssets - totalLiabilities;

      // ----- 주당가치 -----
      const sharePrice = netAssetValue / sharesOutstanding;

      const duration = Date.now() - startTime;

      return {
        method: 'Asset',
        enterpriseValue: Math.round(netAssetValue),
        equityValue: Math.round(netAssetValue),
        sharePrice: Math.round(sharePrice),
        details: {
          totalAssets: Math.round(totalAssets),
          adjustedAssets: Math.round(adjustedAssets),
          totalLiabilities: Math.round(totalLiabilities),
          netAssetValue: Math.round(netAssetValue),
          inventoryAdjustment: Math.round(inventoryAdjustment),
          intangiblesAdjustment: Math.round(intangiblesAdjustment),
          adjustments: data.assetAdjustments || {},
          sharesOutstanding,
        },
        duration,
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`자산가치 평가 계산 실패: ${message}`);
    }
  }
}

export default AssetEngine;
