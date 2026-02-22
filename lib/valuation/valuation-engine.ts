/**
 * @task S3BA1
 * @description Valuation Engine 추상 기본 클래스
 *
 * 모든 평가 엔진(DCF, Relative, Asset, Intrinsic, Tax)이 상속하는
 * 추상 클래스입니다. 공통 입력 검증 로직과 인터페이스 규약을 정의합니다.
 */

import type {
  ValuationInput,
  ValuationResult,
  ValidationResult,
} from './types';

/**
 * 평가 엔진 추상 기본 클래스
 *
 * 각 평가법 엔진은 이 클래스를 상속하여 `getName()`과 `calculate()`를
 * 구현해야 합니다. 공통 유효성 검증 로직은 `validate()` 메서드에서
 * 제공되며, 하위 클래스에서 오버라이드하여 평가법별 추가 검증을
 * 수행할 수 있습니다.
 *
 * @example
 * ```typescript
 * class DCFEngine extends ValuationEngine {
 *   getName(): string { return 'dcf'; }
 *
 *   async calculate(data: ValuationInput): Promise<ValuationResult> {
 *     const validation = this.validate(data);
 *     if (!validation.valid) {
 *       throw new ValuationError(validation.error!, this.getName(), 'VALIDATION_FAILED');
 *     }
 *     // DCF 계산 로직...
 *   }
 * }
 * ```
 */
export abstract class ValuationEngine {
  /**
   * 평가 엔진 이름을 반환합니다.
   *
   * @returns 평가법 식별자 ('dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax')
   */
  abstract getName(): string;

  /**
   * 평가 계산을 수행합니다.
   *
   * @param data - 평가에 필요한 입력 데이터
   * @returns 평가 결과 (기업가치, 주주가치, 주당가치 등)
   * @throws {ValuationError} 계산 중 오류 발생 시
   */
  abstract calculate(data: ValuationInput): Promise<ValuationResult>;

  /**
   * 입력 데이터의 기본 유효성을 검증합니다.
   *
   * 모든 평가법에 공통으로 적용되는 기본 검증을 수행합니다:
   * - 평가 방법 필드 존재 여부
   * - 프로젝트 ID 존재 여부
   * - 프로젝트 ID 형식 검증 (VL-YYYYMMDD-XXXX 또는 영숫자)
   *
   * 하위 클래스에서 오버라이드하여 평가법별 추가 검증을 수행할 수 있습니다.
   * 이 경우 `super.validate(data)`를 먼저 호출하여 기본 검증을 수행한 후
   * 추가 검증 로직을 이어서 실행하세요.
   *
   * @param data - 검증할 입력 데이터
   * @returns 검증 결과 ({ valid: true } 또는 { valid: false, error: string })
   *
   * @example
   * ```typescript
   * // 하위 클래스에서 추가 검증
   * validate(data: ValuationInput): ValidationResult {
   *   const baseResult = super.validate(data);
   *   if (!baseResult.valid) return baseResult;
   *
   *   // 평가법별 추가 검증
   *   if (!data.cashFlows || data.cashFlows.length === 0) {
   *     return { valid: false, error: '현금흐름 데이터가 필요합니다.' };
   *   }
   *   return { valid: true };
   * }
   * ```
   */
  validate(data: ValuationInput): ValidationResult {
    // 평가 방법 필드 확인
    if (!data.method || typeof data.method !== 'string') {
      return {
        valid: false,
        error: '평가 방법(method)이 지정되지 않았습니다.',
      };
    }

    // 프로젝트 ID 필드 확인
    if (!data.projectId || typeof data.projectId !== 'string') {
      return {
        valid: false,
        error: '프로젝트 ID(projectId)가 지정되지 않았습니다.',
      };
    }

    // 프로젝트 ID 형식 검증
    // VL-YYYYMMDD-XXXX 형식 또는 영숫자+하이픈 조합 허용
    const projectIdPattern = /^[A-Za-z0-9_-]{5,50}$/;
    const vlPattern = /^VL-\d{8}-[A-Za-z0-9]{4}$/;

    if (
      !projectIdPattern.test(data.projectId) &&
      !vlPattern.test(data.projectId)
    ) {
      return {
        valid: false,
        error:
          '프로젝트 ID 형식이 올바르지 않습니다. (VL-YYYYMMDD-XXXX 또는 영숫자 5~50자)',
      };
    }

    return { valid: true };
  }
}
