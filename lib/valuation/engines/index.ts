/**
 * @task S5_FIX_CRITICAL
 * @description 5개 평가 엔진 실제 구현 Export
 *
 * CRITICAL FIX: 스텁/플레이스홀더를 실제 구현으로 교체
 * - 개별 엔진 파일에서 import하여 re-export
 */

// 실제 구현된 엔진들을 import
import DCFEngineImpl from './dcf-engine';
import AssetEngineImpl from './asset-engine';
import RelativeEngineImpl from './relative-engine';
import IntrinsicEngineImpl from './intrinsic-engine';
import TaxEngineImpl from './tax-engine';

// Re-export (이름 유지)
export const DCFEngine = DCFEngineImpl;
export const AssetEngine = AssetEngineImpl;
export const RelativeEngine = RelativeEngineImpl;
export const IntrinsicEngine = IntrinsicEngineImpl;
export const TaxEngine = TaxEngineImpl;

// 기본 export도 제공 (편의성)
export default {
  DCFEngine: DCFEngineImpl,
  AssetEngine: AssetEngineImpl,
  RelativeEngine: RelativeEngineImpl,
  IntrinsicEngine: IntrinsicEngineImpl,
  TaxEngine: TaxEngineImpl,
};
