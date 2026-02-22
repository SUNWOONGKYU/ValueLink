/**
 * @task S5_FIX_PHASE5
 * @description Workflow Step Validator
 *
 * Phase 5 수정: Workflow Orchestration 구현
 * - Step 순서 검증
 * - 필수 조건 확인 (결제, 보고서 등)
 * - 건너뛰기 방지
 */

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

export interface ValidationResult {
  valid: boolean;
  error?: string;
  warnings?: string[];
}

export interface ProjectData {
  project_id: string;
  current_step: number;
  status: string;
  method?: 'dcf' | 'asset' | 'relative' | 'intrinsic' | 'tax';  // Phase 5 수정: method 추가
  agreed_price?: number;
  deposit_amount?: number;
  deposit_paid_at?: string;
  balance_paid_at?: string;
}

/**
 * Step 14단계 정의
 */
export const WORKFLOW_STEPS = {
  1: 'Project Creation',
  2: 'Quote Generation (SKIPPED)',
  3: 'Negotiation (SKIPPED)',
  4: 'Document Upload',
  5: 'Valuation Execution',
  6: 'Draft Generation',
  7: 'Draft Review',
  8: 'Draft Revision',
  9: 'Report Generation',
  10: 'Report Finalization',
  11: 'Payment Processing',
  12: 'Notification',
  13: 'History Recording',
  14: 'Project Completion',
} as const;

/**
 * Step별 필수 조건 정의
 */
const STEP_REQUIREMENTS: Record<number, (data: ProjectData) => Promise<ValidationResult>> = {
  // Step 1: 프로젝트 생성 (항상 가능)
  1: async () => ({ valid: true }),

  // Step 2-3: 견적/협상 (SKIPPED)
  2: async () => ({ valid: true }),
  3: async () => ({ valid: true }),

  // Step 4: 문서 업로드 (프로젝트 존재만 확인)
  4: async () => ({ valid: true }),

  // Step 5: 평가 실행 (문서 업로드 필요)
  5: async (data) => {
    // 실제로는 documents 테이블 확인해야 함
    if (data.current_step < 4) {
      return {
        valid: false,
        error: 'Step 4 (문서 업로드)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 6: Draft 생성 (평가 완료 필요)
  6: async (data) => {
    if (data.current_step < 5) {
      return {
        valid: false,
        error: 'Step 5 (평가 실행)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 7: Draft 검토
  7: async (data) => {
    if (data.current_step < 6) {
      return {
        valid: false,
        error: 'Step 6 (Draft 생성)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 8: Draft 수정
  8: async (data) => {
    if (data.current_step < 7) {
      return {
        valid: false,
        error: 'Step 7 (Draft 검토)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 9: 보고서 생성
  9: async (data) => {
    if (data.current_step < 8) {
      return {
        valid: false,
        error: 'Step 8 (Draft 수정)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 10: 보고서 확정
  10: async (data) => {
    if (data.current_step < 9) {
      return {
        valid: false,
        error: 'Step 9 (보고서 생성)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 11: 결제 처리 (보고서 확정 필요)
  11: async (data) => {
    if (data.current_step < 10) {
      return {
        valid: false,
        error: 'Step 10 (보고서 확정)를 먼저 완료해야 합니다.',
      };
    }
    return { valid: true };
  },

  // Step 12: 알림
  12: async () => ({ valid: true }),

  // Step 13: 이력 기록
  13: async () => ({ valid: true }),

  // Step 14: 프로젝트 완료 (결제 확인 필수!)
  14: async (data) => {
    const warnings: string[] = [];

    // 1. 계약금 결제 확인
    if (!data.deposit_paid_at) {
      return {
        valid: false,
        error: '계약금이 결제되지 않았습니다. Step 11 (결제 처리)를 먼저 완료하세요.',
      };
    }

    // 2. 잔금 결제 확인
    if (!data.balance_paid_at) {
      return {
        valid: false,
        error: '잔금이 결제되지 않았습니다. Step 11 (결제 처리)를 먼저 완료하세요.',
      };
    }

    // 3. 보고서 확정 확인 (reports 테이블 체크)
    // [Phase 5 수정] 실제 DB 조회
    if (data.method) {
      const reportTable = `${data.method}_reports`;
      const { data: report, error } = await supabase
        .from(reportTable)
        .select('report_id, status')
        .eq('project_id', data.project_id)
        .eq('status', 'finalized')  // 'confirmed'가 아닌 'finalized' 상태 확인
        .single();

      if (error || !report) {
        warnings.push('보고서가 확정(finalized)되지 않았습니다. Step 10 (보고서 확정)을 먼저 완료하세요.');
      }
    } else {
      warnings.push('평가 방법(method)을 확인할 수 없어 보고서 검증을 건너뜁니다.');
    }

    return {
      valid: true,
      warnings: warnings.length > 0 ? warnings : undefined,
    };
  },
};

/**
 * Step 진행 가능 여부를 검증합니다.
 *
 * @param currentStep - 현재 Step
 * @param targetStep - 이동하려는 Step
 * @param projectData - 프로젝트 데이터
 * @returns 검증 결과
 *
 * @example
 * ```typescript
 * const result = await canAdvanceToStep(1, 14, projectData);
 * if (!result.valid) {
 *   console.error(result.error);
 * }
 * ```
 */
export async function canAdvanceToStep(
  currentStep: number,
  targetStep: number,
  projectData: ProjectData
): Promise<ValidationResult> {
  // 1. Step 범위 검증
  if (targetStep < 1 || targetStep > 14) {
    return {
      valid: false,
      error: 'Step은 1~14 범위여야 합니다.',
    };
  }

  // 2. 역진행 허용 (필요 시)
  if (targetStep < currentStep) {
    return {
      valid: true,
      warnings: ['이전 Step으로 이동합니다.'],
    };
  }

  // 3. 건너뛰기 방지 (최대 1 step만 허용)
  if (targetStep > currentStep + 1) {
    return {
      valid: false,
      error: `Step을 건너뛸 수 없습니다. 현재 Step ${currentStep}에서 Step ${targetStep}로 직접 이동할 수 없습니다. 순차적으로 진행하세요.`,
    };
  }

  // 4. Target Step의 필수 조건 확인
  const requirementCheck = STEP_REQUIREMENTS[targetStep];
  if (!requirementCheck) {
    return {
      valid: true,
      warnings: [`Step ${targetStep}의 필수 조건이 정의되지 않았습니다.`],
    };
  }

  const requirementResult = await requirementCheck(projectData);
  if (!requirementResult.valid) {
    return requirementResult;
  }

  return {
    valid: true,
    warnings: requirementResult.warnings,
  };
}

/**
 * 프로젝트 데이터를 Supabase에서 가져옵니다.
 *
 * @param projectId - 프로젝트 ID
 * @returns 프로젝트 데이터
 */
export async function getProjectData(projectId: string): Promise<ProjectData | null> {
  const { data, error } = await supabase
    .from('projects')
    .select('project_id, current_step, status, method, agreed_price, deposit_amount, deposit_paid_at, balance_paid_at')
    .eq('project_id', projectId)
    .single();

  if (error || !data) {
    return null;
  }

  return data as ProjectData;
}

/**
 * Step 진행을 검증하고 업데이트합니다.
 *
 * @param projectId - 프로젝트 ID
 * @param targetStep - 이동하려는 Step
 * @returns 검증 및 업데이트 결과
 *
 * @example
 * ```typescript
 * const result = await validateAndAdvanceStep('VL-20260222-0001', 5);
 * if (!result.valid) {
 *   console.error(result.error);
 * } else {
 *   console.log('Step 진행 성공');
 * }
 * ```
 */
export async function validateAndAdvanceStep(
  projectId: string,
  targetStep: number
): Promise<ValidationResult> {
  // 1. 프로젝트 데이터 조회
  const projectData = await getProjectData(projectId);
  if (!projectData) {
    return {
      valid: false,
      error: '프로젝트를 찾을 수 없습니다.',
    };
  }

  // 2. Step 진행 가능 여부 검증
  const validationResult = await canAdvanceToStep(
    projectData.current_step,
    targetStep,
    projectData
  );

  if (!validationResult.valid) {
    return validationResult;
  }

  // 3. projects 테이블 업데이트
  const { error: updateError } = await supabase
    .from('projects')
    .update({ current_step: targetStep })
    .eq('project_id', projectId);

  if (updateError) {
    return {
      valid: false,
      error: `Step 업데이트 실패: ${updateError.message}`,
    };
  }

  return {
    valid: true,
    warnings: validationResult.warnings,
  };
}
