/**
 * @task S4E4
 * @description Enkino AI 평가보고서 검증 서비스
 *
 * DCF 평가 엔진을 실제 회계법인 평가보고서 데이터로 검증합니다.
 * 태일회계법인이 작성한 엔키노에이아이 FY25 기업가치 평가보고서(2025.06.30)의
 * 실제 수치와 DCF 엔진의 계산 결과를 비교하여 정확도를 검증합니다.
 *
 * 검증 기준: ±5% 이내 오차를 PASS로 간주
 *
 * @example
 * ```typescript
 * const service = new EnkinoVerificationService();
 * const result = await service.runVerification();
 * console.log(service.formatVerificationResult(result));
 * ```
 */

import DCFEngine from '../../../../S3_개발-2차/Backend_APIs/valuation/engines/dcf-engine';

/**
 * 검증 결과 인터페이스
 */
interface VerificationResult {
  /** 검증 통과 여부 */
  passed: boolean;
  /** 최대 오차율 (%) */
  maxError: number;
  /** 개별 항목 비교 결과 */
  comparisons: {
    /** 항목명 */
    field: string;
    /** 평가보고서 실제값 */
    actual: number;
    /** DCF 엔진 계산값 */
    engine: number;
    /** 오차율 (%) */
    errorPct: number;
    /** 항목별 통과 여부 */
    passed: boolean;
  }[];
  /** 계산 소요 시간 (ms) */
  duration: number;
  /** 검증 실행 시각 */
  timestamp: string;
}

/**
 * 엔키노 AI 평가보고서 검증 서비스
 *
 * 실제 회계법인 평가보고서의 수치와 DCF 엔진 계산 결과를 비교하여
 * 평가 엔진의 정확도를 검증합니다.
 */
export class EnkinoVerificationService {
  private dcfEngine: DCFEngine;

  constructor() {
    this.dcfEngine = new DCFEngine();
  }

  /**
   * 엔키노 평가보고서 검증을 실행합니다.
   *
   * 검증 데이터: 태일회계법인 FY25 엔키노에이아이 기업가치 평가보고서 (2025.06.30)
   *
   * 검증 항목:
   * 1. Operating Value (영업가치)
   * 2. PV Cumulative (누적 현금흐름 현재가치)
   * 3. PV Terminal (영구가치 현재가치)
   * 4. Enterprise Value (기업가치)
   * 5. Equity Value (주주가치)
   * 6. Value Per Share (주당가치)
   *
   * @returns 검증 결과 (통과 여부, 오차율, 상세 비교)
   * @throws Error DCF 엔진 계산 실패 시
   */
  async runVerification(): Promise<VerificationResult> {
    const startTime = Date.now();

    // -------------------------------------------------------------------------
    // 1. 평가보고서 실제 데이터 (태일회계법인, 2025.06.30)
    // -------------------------------------------------------------------------

    const actualData = {
      operatingValue: 16_216_378_227, // 영업가치
      pvCumulative: 5_605_401_153, // 누적 현금흐름 현재가치
      pvTerminal: 10_610_977_073, // 영구가치 현재가치
      enterpriseValue: 16_346_048_693, // 기업가치
      equityValue: 15_729_119_359, // 주주가치
      valuePerShare: 2_140, // 주당가치
    };

    // -------------------------------------------------------------------------
    // 2. DCF 엔진 입력 데이터
    // -------------------------------------------------------------------------

    // 평가보고서 기준 입력값
    const inputData = {
      method: 'dcf' as const,
      projectId: 'ENKINO-VERIFICATION-FY25',

      // 연도별 FCFF (Free Cash Flow to Firm)
      // FY26-FY30 5개년 예측값
      cashFlows: [
        1_117_134_000, // FY26 (2026.06.30)
        1_323_608_000, // FY27 (2027.06.30)
        1_556_760_000, // FY28 (2028.06.30)
        1_820_434_000, // FY29 (2029.06.30)
        2_118_732_000, // FY30 (2030.06.30)
      ],

      // WACC (가중평균자본비용) - 12.41%
      wacc: 0.1241,

      // 영구성장률 - 1.0%
      terminalGrowthRate: 0.01,

      // 순부채 (Net Debt)
      // Enterprise Value - Equity Value = 16,346,048,693 - 15,729,119,359 = 616,929,334
      netDebt: 616_929_334,

      // 발행주식수
      sharesOutstanding: 7_350_000,
    };

    // -------------------------------------------------------------------------
    // 3. DCF 엔진 실행
    // -------------------------------------------------------------------------

    const engineResult = await this.dcfEngine.calculate(inputData);

    // -------------------------------------------------------------------------
    // 4. 비교 및 오차 계산
    // -------------------------------------------------------------------------

    const comparisons = [
      {
        field: 'Operating Value',
        actual: actualData.operatingValue,
        engine: engineResult.enterpriseValue, // Operating Value ≈ Enterprise Value
      },
      {
        field: 'PV Cumulative',
        actual: actualData.pvCumulative,
        engine: (engineResult.details.npv as number) || 0,
      },
      {
        field: 'PV Terminal',
        actual: actualData.pvTerminal,
        engine: (engineResult.details.pvTerminalValue as number) || 0,
      },
      {
        field: 'Enterprise Value',
        actual: actualData.enterpriseValue,
        engine: engineResult.enterpriseValue,
      },
      {
        field: 'Equity Value',
        actual: actualData.equityValue,
        engine: engineResult.equityValue,
      },
      {
        field: 'Value Per Share',
        actual: actualData.valuePerShare,
        engine: engineResult.sharePrice,
      },
    ].map((item) => {
      // 오차율 계산: (엔진값 - 실제값) / 실제값 * 100
      const errorPct =
        item.actual !== 0 ? ((item.engine - item.actual) / item.actual) * 100 : 0;

      return {
        field: item.field,
        actual: item.actual,
        engine: item.engine,
        errorPct: Math.abs(errorPct),
        passed: Math.abs(errorPct) <= 5.0, // ±5% 이내 PASS
      };
    });

    // -------------------------------------------------------------------------
    // 5. 검증 결과 생성
    // -------------------------------------------------------------------------

    const maxError = Math.max(...comparisons.map((c) => c.errorPct));
    const passed = maxError <= 5.0;

    const duration = Date.now() - startTime;

    return {
      passed,
      maxError,
      comparisons,
      duration,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * 검증 결과를 읽기 쉬운 텍스트 형식으로 포맷합니다.
   *
   * @param result - 검증 결과 객체
   * @returns 포맷팅된 문자열
   *
   * @example
   * ```typescript
   * const service = new EnkinoVerificationService();
   * const result = await service.runVerification();
   * console.log(service.formatVerificationResult(result));
   * // 출력:
   * // ========================================
   * // Enkino AI 평가보고서 검증 결과
   * // ========================================
   * // ...
   * ```
   */
  formatVerificationResult(result: VerificationResult): string {
    const lines: string[] = [];

    lines.push('========================================');
    lines.push('Enkino AI 평가보고서 검증 결과');
    lines.push('========================================');
    lines.push('');
    lines.push('검증 데이터: 태일회계법인 FY25 엔키노에이아이 기업가치 평가보고서 (2025.06.30)');
    lines.push('검증 기준: ±5% 이내 오차 허용');
    lines.push('');
    lines.push('----------------------------------------');
    lines.push('종합 결과');
    lines.push('----------------------------------------');
    lines.push(`검증 결과: ${result.passed ? '✅ PASS' : '❌ FAIL'}`);
    lines.push(`최대 오차율: ${result.maxError.toFixed(2)}%`);
    lines.push(`계산 소요 시간: ${result.duration}ms`);
    lines.push(`검증 시각: ${result.timestamp}`);
    lines.push('');
    lines.push('----------------------------------------');
    lines.push('상세 비교');
    lines.push('----------------------------------------');
    lines.push('');

    // 항목별 비교 결과
    result.comparisons.forEach((comp) => {
      lines.push(`[${comp.passed ? '✅' : '❌'}] ${comp.field}`);
      lines.push(`  평가보고서:  ${this.formatNumber(comp.actual)}`);
      lines.push(`  DCF 엔진:    ${this.formatNumber(comp.engine)}`);
      lines.push(`  오차율:      ${comp.errorPct.toFixed(2)}%`);
      lines.push('');
    });

    lines.push('========================================');

    return lines.join('\n');
  }

  /**
   * 숫자를 3자리마다 쉼표로 구분하여 포맷합니다.
   *
   * @param value - 포맷할 숫자
   * @returns 포맷팅된 문자열
   *
   * @example
   * formatNumber(16216378227) // "16,216,378,227"
   * formatNumber(2140) // "2,140"
   */
  private formatNumber(value: number): string {
    // 소수점이 있는 경우 (주당가치)
    if (value % 1 !== 0) {
      return value.toLocaleString('ko-KR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    }

    // 정수인 경우
    return value.toLocaleString('ko-KR');
  }
}

// -------------------------------------------------------------------------
// 단독 실행 예시 (테스트용)
// -------------------------------------------------------------------------

/**
 * 스크립트를 직접 실행할 때 검증을 수행합니다.
 *
 * 실행 방법:
 * ```bash
 * npx ts-node lib/integrations/enkino-verification.ts
 * ```
 */
async function main() {
  console.log('엔키노 AI 평가보고서 검증을 시작합니다...\n');

  const service = new EnkinoVerificationService();

  try {
    const result = await service.runVerification();
    console.log(service.formatVerificationResult(result));

    // 검증 실패 시 프로세스 종료 코드 1
    if (!result.passed) {
      process.exit(1);
    }
  } catch (error) {
    console.error('검증 중 오류 발생:', error);
    process.exit(1);
  }
}

// 스크립트 직접 실행 시에만 main() 호출
if (require.main === module) {
  main();
}
