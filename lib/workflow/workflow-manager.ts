/**
 * @task S2BA1
 * @description 14-Step Valuation Workflow Manager
 *
 * Manages the full 14-step valuation process lifecycle:
 * Steps 1-3: Home / project setup
 * Step 4: Valuation method selection
 * Step 5: Data collection
 * Step 6: Valuation engine execution
 * Step 7: Accountant review submission
 * Step 8: Draft report generation
 * Step 9: Draft review
 * Step 10: Feedback incorporation
 * Step 11: Final report generation
 * Step 12: Final approval
 * Step 13: Report delivery
 * Step 14: Completion
 */

import { createClient } from '@/lib/supabase/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Allowed project statuses */
export type ProjectStatus =
  | 'not_started'
  | 'in_progress'
  | 'pending_review'
  | 'human_approval'
  | 'draft_generated'
  | 'completed'
  | 'failed'

/** Roles that may be required to advance a step */
export type RequiredRole = 'system' | 'accountant' | 'admin'

/** Single workflow step definition */
export interface WorkflowStep {
  /** Step number (1 - 14) */
  step_number: number
  /** Machine-readable step name */
  step_name: string
  /** Human-readable description (Korean) */
  description: string
  /** Role required to execute / advance this step */
  required_role: RequiredRole
  /** Whether explicit approval is needed before moving on */
  approval_required: boolean
  /** Cumulative progress percentage (0 - 100) */
  progress_percentage: number
}

/** DB row shape returned from the valuation_projects table */
export interface ValuationProjectRow {
  project_id: string
  status: ProjectStatus
  current_step: number
  progress: number
  owner_id: string
  updated_at: string
  [key: string]: unknown
}

/** Result returned by most WorkflowManager methods */
export interface WorkflowResult<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/**
 * Complete definition of the 14-step valuation workflow.
 *
 * Each entry captures the step metadata: name, description, who can advance
 * the step, whether approval is required, and the cumulative progress value
 * that corresponds to reaching this step.
 */
export const WORKFLOW_STEPS: readonly WorkflowStep[] = Object.freeze([
  {
    step_number: 1,
    step_name: 'project_creation',
    description: '프로젝트 생성',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 0,
  },
  {
    step_number: 2,
    step_name: 'company_info_input',
    description: '기업 정보 입력',
    required_role: 'accountant',
    approval_required: false,
    progress_percentage: 0,
  },
  {
    step_number: 3,
    step_name: 'document_upload',
    description: '서류 업로드',
    required_role: 'accountant',
    approval_required: false,
    progress_percentage: 0,
  },
  {
    step_number: 4,
    step_name: 'method_selection',
    description: '평가 방법 선택',
    required_role: 'accountant',
    approval_required: false,
    progress_percentage: 0,
  },
  {
    step_number: 5,
    step_name: 'data_collection',
    description: '데이터 수집',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 10,
  },
  {
    step_number: 6,
    step_name: 'valuation_execution',
    description: '평가 실행',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 30,
  },
  {
    step_number: 7,
    step_name: 'accountant_review_submit',
    description: '회계사 검토 제출',
    required_role: 'system',
    approval_required: true,
    progress_percentage: 50,
  },
  {
    step_number: 8,
    step_name: 'draft_report_generation',
    description: '초안 보고서 생성',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 60,
  },
  {
    step_number: 9,
    step_name: 'draft_review',
    description: '초안 검토',
    required_role: 'accountant',
    approval_required: true,
    progress_percentage: 70,
  },
  {
    step_number: 10,
    step_name: 'feedback_incorporation',
    description: '피드백 반영',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 75,
  },
  {
    step_number: 11,
    step_name: 'final_report_generation',
    description: '최종 보고서 생성',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 80,
  },
  {
    step_number: 12,
    step_name: 'final_approval',
    description: '최종 승인',
    required_role: 'accountant',
    approval_required: true,
    progress_percentage: 90,
  },
  {
    step_number: 13,
    step_name: 'report_delivery',
    description: '보고서 전달',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 95,
  },
  {
    step_number: 14,
    step_name: 'completion',
    description: '완료',
    required_role: 'system',
    approval_required: false,
    progress_percentage: 100,
  },
])

/** Minimum valid step number */
const MIN_STEP = 1
/** Maximum valid step number */
const MAX_STEP = 14

// ---------------------------------------------------------------------------
// Helper – validation
// ---------------------------------------------------------------------------

/**
 * Validates that a project ID follows the expected format.
 *
 * Accepted formats:
 *   - Uppercase alphanumeric + hyphens, 5-50 chars  (e.g. SAMSU-2501191430-CP)
 *   - UUID v4
 *
 * @param projectId - The project identifier to validate.
 * @returns `true` when the format is valid.
 */
function isValidProjectId(projectId: string): boolean {
  if (!projectId || typeof projectId !== 'string') return false
  // Allow typical project-id format or UUID
  const projectIdPattern = /^[A-Za-z0-9_-]{5,50}$/
  const uuidPattern =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  return projectIdPattern.test(projectId) || uuidPattern.test(projectId)
}

/**
 * Validates that a step number is within the valid 1-14 range.
 */
function isValidStep(step: number): boolean {
  return Number.isInteger(step) && step >= MIN_STEP && step <= MAX_STEP
}

// ---------------------------------------------------------------------------
// WorkflowManager
// ---------------------------------------------------------------------------

/**
 * Manages the 14-step valuation workflow for a single project.
 *
 * Usage:
 * ```ts
 * const mgr = new WorkflowManager()
 * const current = await mgr.getCurrentStep('PROJECT-123')
 * const next    = await mgr.advanceStep('PROJECT-123')
 * ```
 */
export class WorkflowManager {
  // -----------------------------------------------------------------------
  // Public API
  // -----------------------------------------------------------------------

  /**
   * Retrieves the current workflow step for a project.
   *
   * @param projectId - Target project identifier.
   * @returns The current step metadata together with the project status.
   */
  async getCurrentStep(
    projectId: string,
  ): Promise<
    WorkflowResult<{
      project_id: string
      status: ProjectStatus
      current_step: number
      progress: number
      step_info: WorkflowStep
    }>
  > {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }

      const supabase = await createClient()

      const { data, error } = await supabase
        .from('valuation_projects')
        .select('project_id, status, current_step, progress, owner_id, updated_at')
        .eq('project_id', projectId)
        .single()

      if (error || !data) {
        return {
          success: false,
          error: error?.message ?? 'Project not found.',
        }
      }

      const row = data as unknown as ValuationProjectRow
      const stepInfo = this.getStepInfo(row.current_step)
      if (!stepInfo) {
        return {
          success: false,
          error: `Invalid current_step ${row.current_step} stored in DB.`,
        }
      }

      return {
        success: true,
        data: {
          project_id: row.project_id,
          status: row.status,
          current_step: row.current_step,
          progress: row.progress,
          step_info: stepInfo,
        },
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unknown error in getCurrentStep'
      console.error('[WorkflowManager.getCurrentStep]', message)
      return { success: false, error: message }
    }
  }

  /**
   * Advances the project to the next sequential step.
   *
   * Validates:
   * - The project exists
   * - The project is not already at the final step
   * - If the current step requires approval, that approval has been recorded
   *
   * @param projectId - Target project identifier.
   * @returns The updated step information after advancement.
   */
  async advanceStep(
    projectId: string,
  ): Promise<
    WorkflowResult<{
      previous_step: number
      current_step: number
      progress: number
      step_info: WorkflowStep
      status: ProjectStatus
    }>
  > {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }

      const supabase = await createClient()

      // 1. Fetch current state
      const { data: project, error: fetchErr } = await supabase
        .from('valuation_projects')
        .select('project_id, status, current_step, progress, owner_id')
        .eq('project_id', projectId)
        .single()

      if (fetchErr || !project) {
        return {
          success: false,
          error: fetchErr?.message ?? 'Project not found.',
        }
      }

      const row = project as unknown as ValuationProjectRow
      const currentStep = row.current_step

      // 2. Already at final step?
      if (currentStep >= MAX_STEP) {
        return {
          success: false,
          error: 'Already at the final step (14). Cannot advance further.',
        }
      }

      // 3. Approval gate check
      const currentStepInfo = this.getStepInfo(currentStep)
      if (currentStepInfo?.approval_required) {
        const approvedResult = await this.isStepApproved(projectId, currentStep)
        if (!approvedResult.success || !approvedResult.data?.approved) {
          return {
            success: false,
            error: `Step ${currentStep} (${currentStepInfo.description}) requires approval before advancing.`,
          }
        }
      }

      // 4. Compute next step values
      const nextStep = currentStep + 1
      const nextStepInfo = this.getStepInfo(nextStep)!
      const nextStatus: ProjectStatus =
        nextStep === MAX_STEP ? 'completed' : 'in_progress'

      // 5. Persist
      const { error: updateErr } = await supabase
        .from('valuation_projects')
        .update({
          current_step: nextStep,
          progress: nextStepInfo.progress_percentage,
          status: nextStatus,
          updated_at: new Date().toISOString(),
        })
        .eq('project_id', projectId)

      if (updateErr) {
        return { success: false, error: updateErr.message }
      }

      return {
        success: true,
        data: {
          previous_step: currentStep,
          current_step: nextStep,
          progress: nextStepInfo.progress_percentage,
          step_info: nextStepInfo,
          status: nextStatus,
        },
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unknown error in advanceStep'
      console.error('[WorkflowManager.advanceStep]', message)
      return { success: false, error: message }
    }
  }

  /**
   * Checks whether a project can advance from its current step to a target
   * step. Validates that every intermediate approval-gated step has been
   * approved.
   *
   * @param projectId  - Target project identifier.
   * @param targetStep - The desired destination step (1-14).
   * @returns Whether advancement is possible and, if not, the reason.
   */
  async canAdvanceToStep(
    projectId: string,
    targetStep: number,
  ): Promise<WorkflowResult<{ can_advance: boolean; reason?: string }>> {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }
      if (!isValidStep(targetStep)) {
        return {
          success: false,
          error: `Target step must be between ${MIN_STEP} and ${MAX_STEP}.`,
        }
      }

      const supabase = await createClient()

      const { data: project, error } = await supabase
        .from('valuation_projects')
        .select('current_step')
        .eq('project_id', projectId)
        .single()

      if (error || !project) {
        return { success: false, error: error?.message ?? 'Project not found.' }
      }

      const current = (project as unknown as { current_step: number })
        .current_step

      if (targetStep <= current) {
        return {
          success: true,
          data: {
            can_advance: false,
            reason: `Target step ${targetStep} is not ahead of current step ${current}.`,
          },
        }
      }

      // Check every approval-gated step between current and target
      for (let s = current; s < targetStep; s++) {
        const info = this.getStepInfo(s)
        if (info?.approval_required) {
          const approved = await this.isStepApproved(projectId, s)
          if (!approved.success || !approved.data?.approved) {
            return {
              success: true,
              data: {
                can_advance: false,
                reason: `Step ${s} (${info.description}) requires approval before advancing past it.`,
              },
            }
          }
        }
      }

      return { success: true, data: { can_advance: true } }
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unknown error in canAdvanceToStep'
      console.error('[WorkflowManager.canAdvanceToStep]', message)
      return { success: false, error: message }
    }
  }

  /**
   * Determines whether a specific step has been approved.
   *
   * Checks the `workflow_approvals` table for a record matching the
   * project and step with status = 'approved'.
   *
   * @param projectId  - Target project identifier.
   * @param stepNumber - The step number to check (1-14).
   */
  async isStepApproved(
    projectId: string,
    stepNumber: number,
  ): Promise<WorkflowResult<{ approved: boolean }>> {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }
      if (!isValidStep(stepNumber)) {
        return {
          success: false,
          error: `Step number must be between ${MIN_STEP} and ${MAX_STEP}.`,
        }
      }

      const supabase = await createClient()

      const { data, error } = await supabase
        .from('workflow_approvals')
        .select('id')
        .eq('project_id', projectId)
        .eq('step_number', stepNumber)
        .eq('status', 'approved')
        .limit(1)

      if (error) {
        return { success: false, error: error.message }
      }

      return {
        success: true,
        data: { approved: Array.isArray(data) && data.length > 0 },
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unknown error in isStepApproved'
      console.error('[WorkflowManager.isStepApproved]', message)
      return { success: false, error: message }
    }
  }

  /**
   * Returns the static metadata for a single step.
   *
   * @param stepNumber - Step number (1-14).
   * @returns The step definition or `null` when the step number is out of range.
   */
  getStepInfo(stepNumber: number): WorkflowStep | null {
    if (!isValidStep(stepNumber)) return null
    return WORKFLOW_STEPS.find((s) => s.step_number === stepNumber) ?? null
  }

  /**
   * Returns all 14 workflow step definitions.
   */
  getAllSteps(): readonly WorkflowStep[] {
    return WORKFLOW_STEPS
  }
}
