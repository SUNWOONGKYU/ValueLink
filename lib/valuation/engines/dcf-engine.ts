/**
 * @task S3BA3
 * @description DCF (현금흐름할인법) 평가 엔진 및 민감도 분석
 *
 * DCF(Discounted Cash Flow) 방법론을 사용하여 기업의 미래 현금흐름을
 * 현재가치로 할인하고, 영구가치(Terminal Value)를 합산하여
 * 기업가치(Enterprise Value)를 산출합니다.
 *
 * 핵심 수식:
 *   FCF  = NOPAT + 감가상각 - Capex - Delta(WC)
 *   NPV  = SUM( FCFt / (1 + WACC)^t )
 *   TV   = FCF_last * (1 + g) / (WACC - g)
 *   EV   = NPV + PV(TV)
 *   Equity = EV - Net Debt
 *   Share Price = Equity / Shares Outstanding
 */

import {
  ValuationInput,
  ValuationResult,
  ValidationResult,
  SensitivityScenario,
  SensitivityAnalysisResult,
} from '../types';
import { ValuationEngine } from '../valuation-engine';
import { calculateNPV, calculateTerminalValue } from '../financial-math';

/**
 * DCF(현금흐름할인법) 평가 엔진
 *
 * 미래 현금흐름을 WACC로 할인하여 기업가치를 산출합니다.
 * 민감도 분석(WACC x Growth Rate 매트릭스)을 병렬로 수행할 수 있습니다.
 *
 * @example
 * ```typescript
 * const engine = new DCFEngine();
 * const result = await engine.calculate({
 *   method: 'dcf',
 *   projectId: 'VL-20260222-0001',
 *   cashFlows: [500_000_000, 600_000_000, 720_000_000, 864_000_000, 1_036_800_000],
 *   wacc: 0.12,
 *   terminalGrowthRate: 0.03,
 *   netDebt: 5_000_000_000,
 *   sharesOutstanding: 10_000_000,
 * });
 * ```
 */
class DCFEngine extends ValuationEngine {
  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * 엔진 이름을 반환합니다.
   *
   * @returns 'DCF'
   */
  getName(): string {
    return 'DCF';
  }

  /**
   * DCF 평가를 위한 입력 데이터 유효성을 검증합니다.
   *
   * 검증 항목:
   * 1. 부모 클래스 기본 검증 (method, projectId)
   * 2. cashFlows 배열 존재 및 길이 > 0
   * 3. wacc > 0 이고 wacc < 1
   * 4. terminalGrowthRate 존재
   * 5. terminalGrowthRate < wacc (Gordon Growth Model 전제 조건)
   *
   * @param data - 평가 입력 데이터
   * @returns 유효성 검증 결과
   */
  validate(data: ValuationInput): ValidationResult {
    // 부모 클래스 기본 검증
    const baseValidation = super.validate(data);
    if (!baseValidation.valid) return baseValidation;

    // cashFlows 존재 및 길이 검증
    if (!data.cashFlows || data.cashFlows.length === 0) {
      return {
        valid: false,
        error: '현금흐름(cashFlows) 데이터가 필요합니다. 최소 1개 이상의 연도별 FCF를 입력하세요.',
      };
    }

    // WACC 범위 검증 (0 < wacc < 1)
    if (!data.wacc || data.wacc <= 0 || data.wacc >= 1) {
      return {
        valid: false,
        error: 'WACC(가중평균자본비용)는 0보다 크고 1보다 작아야 합니다.',
      };
    }

    // 영구성장률 존재 검증
    if (data.terminalGrowthRate === undefined || data.terminalGrowthRate === null) {
      return {
        valid: false,
        error: '영구성장률(terminalGrowthRate)이 필요합니다.',
      };
    }

    // 영구성장률 < WACC 검증 (Gordon Growth Model 전제)
    if (data.terminalGrowthRate >= data.wacc) {
      return {
        valid: false,
        error: `영구성장률(${data.terminalGrowthRate})은 WACC(${data.wacc})보다 작아야 합니다. Gordon Growth Model의 전제 조건입니다.`,
      };
    }

    return { valid: true };
  }

  /**
   * DCF 기업가치 평가를 수행합니다.
   *
   * 계산 흐름:
   *   1. NPV = SUM( FCFt / (1 + WACC)^t )
   *   2. TV  = FCF_last * (1 + g) / (WACC - g)
   *   3. PV(TV) = TV / (1 + WACC)^n
   *   4. EV  = NPV + PV(TV)
   *   5. Equity = EV - Net Debt
   *   6. Share Price = Equity / Shares Outstanding
   *
   * @param data - 평가 입력 데이터
   * @returns 평가 결과 (기업가치, 주주가치, 주당가치, 상세 내역)
   * @throws Error 입력 검증 실패 또는 계산 오류 시
   */
  async calculate(data: ValuationInput): Promise<ValuationResult> {
    const startTime = Date.now();

    // 입력 검증
    const validation = this.validate(data);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    try {
      const cashFlows = data.cashFlows!;
      const wacc = data.wacc!;
      const growthRate = data.terminalGrowthRate!;
      const n = cashFlows.length;

      // 1. NPV 계산 - 미래 현금흐름의 현재가치 합계
      const npv = calculateNPV(cashFlows, wacc);

      // 2. Terminal Value 계산 - 마지막 연도 이후 영구 현금흐름의 가치
      const lastCashFlow = cashFlows[n - 1];
      const terminalValue = calculateTerminalValue(lastCashFlow, growthRate, wacc);

      // 3. Terminal Value의 현재가치 - TV를 현재 시점으로 할인
      const pvTerminalValue = terminalValue / Math.pow(1 + wacc, n);

      // 4. Enterprise Value (기업가치) = NPV + PV(TV)
      const enterpriseValue = npv + pvTerminalValue;

      // 5. Equity Value (주주가치) = EV - Net Debt
      const netDebt = data.netDebt || 0;
      const equityValue = enterpriseValue - netDebt;

      // 6. Share Price (주당가치)
      const sharesOutstanding = data.sharesOutstanding || 1;
      const sharePrice = equityValue / sharesOutstanding;

      const duration = Date.now() - startTime;

      return {
        method: 'DCF',
        enterpriseValue: Math.round(enterpriseValue),
        equityValue: Math.round(equityValue),
        sharePrice: Math.round(sharePrice),
        details: {
          npv: Math.round(npv),
          terminalValue: Math.round(terminalValue),
          pvTerminalValue: Math.round(pvTerminalValue),
          enterpriseValue: Math.round(enterpriseValue),
          netDebt,
          equityValue: Math.round(equityValue),
          sharesOutstanding,
          wacc,
          terminalGrowthRate: growthRate,
          cashFlows,
          projectionYears: n,
        },
        duration,
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`DCF 계산 실패: ${message}`);
    }
  }

  // ---------------------------------------------------------------------------
  // Sensitivity Analysis
  // ---------------------------------------------------------------------------

  /**
   * DCF 민감도 분석을 수행합니다.
   *
   * WACC와 영구성장률을 변동시켜 기업가치의 변화를 매트릭스로 제공합니다.
   * 모든 시나리오는 Promise.all을 통해 병렬로 계산됩니다.
   *
   * @param baseData   - 기본 평가 입력 데이터
   * @param waccRange  - WACC 변동 범위 (기본: +-2%, 1% 단위)
   * @param growthRange - 성장률 변동 범위 (기본: +-1%, 0.5% 단위)
   * @returns 민감도 분석 결과 (매트릭스 + 시나리오 목록)
   *
   * @example
   * ```typescript
   * const engine = new DCFEngine();
   * const sensitivity = await engine.performSensitivityAnalysis(baseData);
   * console.log(sensitivity.matrix); // [WACC][Growth] = Enterprise Value
   * ```
   */
  async performSensitivityAnalysis(
    baseData: ValuationInput,
    waccRange: number[] = [-0.02, -0.01, 0, 0.01, 0.02],
    growthRange: number[] = [-0.01, -0.005, 0, 0.005, 0.01],
  ): Promise<SensitivityAnalysisResult> {
    const baseWacc = baseData.wacc!;
    const baseGrowth = baseData.terminalGrowthRate!;

    // 절대값 범위로 변환
    const absoluteWaccRange = waccRange.map((delta) => baseWacc + delta);
    const absoluteGrowthRange = growthRange.map((delta) => baseGrowth + delta);

    // 병렬 계산을 위한 Promise 배열과 좌표 추적
    const promises: Promise<SensitivityScenario | null>[] = [];
    const coordinates: Array<{ i: number; j: number }> = [];

    for (let i = 0; i < absoluteWaccRange.length; i++) {
      for (let j = 0; j < absoluteGrowthRange.length; j++) {
        const newWacc = absoluteWaccRange[i];
        const newGrowth = absoluteGrowthRange[j];

        // Gordon Growth Model 전제: WACC > Growth Rate
        if (newWacc <= newGrowth) {
          promises.push(Promise.resolve(null));
          coordinates.push({ i, j });
          continue;
        }

        const scenarioData: ValuationInput = {
          ...baseData,
          wacc: newWacc,
          terminalGrowthRate: newGrowth,
        };

        const scenarioPromise = this.calculate(scenarioData).then(
          (result): SensitivityScenario => ({
            wacc: newWacc,
            growthRate: newGrowth,
            enterpriseValue: result.enterpriseValue,
            equityValue: result.equityValue,
            sharePrice: result.sharePrice,
          }),
        );

        promises.push(scenarioPromise);
        coordinates.push({ i, j });
      }
    }

    // 모든 시나리오 병렬 실행
    const results = await Promise.all(promises);

    // 매트릭스 초기화 (NaN = WACC <= Growth인 경우)
    const matrix: number[][] = Array.from({ length: absoluteWaccRange.length }, () =>
      new Array(absoluteGrowthRange.length).fill(NaN),
    );

    // 유효한 시나리오만 수집
    const validScenarios: SensitivityScenario[] = [];

    for (let idx = 0; idx < results.length; idx++) {
      const result = results[idx];
      const { i, j } = coordinates[idx];

      if (result !== null) {
        matrix[i][j] = result.enterpriseValue;
        validScenarios.push(result);
      }
    }

    return {
      waccRange: absoluteWaccRange,
      growthRange: absoluteGrowthRange,
      matrix,
      scenarios: validScenarios,
    };
  }
}

export default DCFEngine;
