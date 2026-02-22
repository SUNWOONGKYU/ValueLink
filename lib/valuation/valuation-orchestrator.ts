/**
 * @task S3BA1
 * @description Valuation Engine 오케스트레이터 (싱글턴)
 *
 * 평가 엔진 등록/관리 및 평가 실행을 조율하는 중앙 관리자입니다.
 * 싱글턴 패턴으로 애플리케이션 전체에서 하나의 인스턴스만 사용됩니다.
 *
 * 사용 흐름:
 * 1. getInstance()로 오케스트레이터 획득
 * 2. registerEngine()으로 평가 엔진 등록 (앱 초기화 시 1회)
 * 3. valuate()로 평가 실행
 */

import { ValuationEngine } from './valuation-engine';
import type { ValuationInput, ValuationResult } from './types';
import { ValuationError } from './types';

/**
 * 평가 엔진 오케스트레이터
 *
 * 등록된 평가 엔진을 관리하고, 요청된 평가 방법에 따라
 * 적절한 엔진을 선택하여 평가를 실행합니다.
 *
 * @example
 * ```typescript
 * import { ValuationOrchestrator } from './valuation-orchestrator';
 * import { DCFEngine } from './engines';
 *
 * // 엔진 등록
 * const orchestrator = ValuationOrchestrator.getInstance();
 * orchestrator.registerEngine('dcf', new DCFEngine());
 *
 * // 평가 실행
 * const result = await orchestrator.valuate('dcf', {
 *   method: 'dcf',
 *   projectId: 'VL-20260222-A001',
 *   cashFlows: [1000000, 1200000, 1400000],
 *   wacc: 0.10,
 *   terminalGrowthRate: 0.02,
 *   netDebt: 500000,
 *   sharesOutstanding: 10000,
 * });
 * ```
 */
export class ValuationOrchestrator {
  /** 싱글턴 인스턴스 */
  private static instance: ValuationOrchestrator | null = null;

  /** 등록된 평가 엔진 맵 (키: 평가법 이름, 값: 엔진 인스턴스) */
  private engines: Map<string, ValuationEngine>;

  /**
   * private 생성자 - 외부에서 직접 인스턴스 생성 방지
   */
  private constructor() {
    this.engines = new Map<string, ValuationEngine>();
  }

  /**
   * 싱글턴 인스턴스를 반환합니다.
   *
   * 최초 호출 시 인스턴스를 생성하고, 이후에는 동일한 인스턴스를 반환합니다.
   *
   * @returns ValuationOrchestrator 싱글턴 인스턴스
   */
  static getInstance(): ValuationOrchestrator {
    if (!ValuationOrchestrator.instance) {
      ValuationOrchestrator.instance = new ValuationOrchestrator();
    }
    return ValuationOrchestrator.instance;
  }

  /**
   * 평가 엔진을 등록합니다.
   *
   * 동일한 이름으로 재등록하면 기존 엔진을 덮어씁니다.
   *
   * @param name - 평가법 이름 (예: 'dcf', 'relative', 'asset', 'intrinsic', 'tax')
   * @param engine - 평가 엔진 인스턴스
   *
   * @throws {ValuationError} 이름이 비어있거나 엔진이 null/undefined인 경우
   *
   * @example
   * ```typescript
   * orchestrator.registerEngine('dcf', new DCFEngine());
   * ```
   */
  registerEngine(name: string, engine: ValuationEngine): void {
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
      throw new ValuationError(
        '엔진 이름이 비어있습니다.',
        'orchestrator',
        'INVALID_ENGINE_NAME'
      );
    }

    if (!engine) {
      throw new ValuationError(
        '엔진 인스턴스가 제공되지 않았습니다.',
        'orchestrator',
        'INVALID_ENGINE_INSTANCE'
      );
    }

    this.engines.set(name.toLowerCase(), engine);
  }

  /**
   * 지정된 평가 방법으로 평가를 실행합니다.
   *
   * 실행 과정:
   * 1. 등록된 엔진에서 해당 평가법 엔진을 검색
   * 2. 입력 데이터 유효성 검증 (엔진의 validate 메서드)
   * 3. 평가 계산 실행 (엔진의 calculate 메서드)
   * 4. 실행 시간(duration) 측정 및 결과에 포함
   *
   * @param method - 평가 방법 ('dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax')
   * @param data - 평가 입력 데이터
   * @returns 평가 결과 (기업가치, 주주가치, 주당가치, 소요시간 등)
   *
   * @throws {ValuationError} 미등록 평가법, 유효성 검증 실패, 계산 오류 시
   *
   * @example
   * ```typescript
   * const result = await orchestrator.valuate('dcf', inputData);
   * console.log(`기업가치: ${result.enterpriseValue.toLocaleString()}원`);
   * console.log(`소요시간: ${result.duration}ms`);
   * ```
   */
  async valuate(
    method: string,
    data: ValuationInput
  ): Promise<ValuationResult> {
    const normalizedMethod = method.toLowerCase();

    // 1. 엔진 검색
    const engine = this.engines.get(normalizedMethod);
    if (!engine) {
      const supported = this.getSupportedMethods();
      throw new ValuationError(
        `지원하지 않는 평가 방법입니다: '${method}'. 사용 가능한 방법: ${supported.join(', ') || '(등록된 엔진 없음)'}`,
        normalizedMethod,
        'UNSUPPORTED_METHOD'
      );
    }

    // 2. 입력 유효성 검증
    const validation = engine.validate(data);
    if (!validation.valid) {
      throw new ValuationError(
        validation.error ?? '입력 데이터 유효성 검증에 실패했습니다.',
        normalizedMethod,
        'VALIDATION_FAILED'
      );
    }

    // 3. 평가 실행 (시간 측정)
    const startTime = performance.now();

    const result = await engine.calculate(data);

    const endTime = performance.now();
    const duration = Math.round(endTime - startTime);

    // 4. duration 및 timestamp 보정
    return {
      ...result,
      method: normalizedMethod,
      duration,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * 등록된 모든 평가 방법 목록을 반환합니다.
   *
   * @returns 평가 방법 이름 배열 (알파벳순 정렬)
   *
   * @example
   * ```typescript
   * const methods = orchestrator.getSupportedMethods();
   * // ['asset', 'dcf', 'intrinsic', 'relative', 'tax']
   * ```
   */
  getSupportedMethods(): string[] {
    return Array.from(this.engines.keys()).sort();
  }
}
