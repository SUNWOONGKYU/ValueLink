/**
 * @task S2BA1
 * @description 22 Approval Points (Judgment Points) Manager
 *
 * Manages the 22 accountant judgment points (JP001-JP022) that form the
 * human-in-the-loop review layer of the valuation workflow.
 *
 * Categories:
 *   FINANCIAL  (JP001-JP008)  - DCF / asset-related financial assumptions
 *   MARKET     (JP009-JP012)  - Relative valuation & market multiples
 *   ASSET      (JP013-JP018)  - Asset-based valuation items
 *   LEGAL      (JP019-JP022)  - Regulatory / statutory valuation items
 */

import { createClient } from '@/lib/supabase/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Approval point categories */
export type ApprovalCategory = 'FINANCIAL' | 'MARKET' | 'ASSET' | 'LEGAL'

/** Importance levels */
export type ImportanceLevel = 'high' | 'medium' | 'low'

/** Statuses an approval point can be in */
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'custom'

/** Valuation methods an approval point relates to */
export type ValuationMethod =
  | 'dcf'
  | 'relative'
  | 'asset'
  | 'capital_market_law'
  | 'inheritance_tax_law'

/** Static specification of a single approval point */
export interface ApprovalPointSpec {
  point_id: string
  point_name: string
  display_name: string
  category: ApprovalCategory
  importance: ImportanceLevel
  valuation_method: ValuationMethod
  description: string
}

/** Shape of an individual decision in a batch request */
export interface ApprovalDecision {
  point_id: string
  decision: 'approved' | 'rejected' | 'custom'
  custom_value?: unknown
  rationale?: string
}

/**
 * Row shape returned by the approval_points table (schema-v5).
 *
 * Schema-v5 simplified the table: legacy fields (point_id, point_name,
 * display_name, importance, valuation_method, description, ai_value,
 * suggested_range, custom_value, status, approved_by, approved_at,
 * approval_rationale, impact_analysis, updated_at) were removed.
 * The v5 columns are:
 *   approval_id (number, PK), project_id, point_code, category,
 *   question, ai_decision, ai_rationale, human_decision, human_note, created_at
 */
export interface ApprovalPointRow {
  approval_id: number
  project_id: string | null
  point_code: string | null   // previously point_id (e.g. "JP001")
  category: string | null
  question: string | null     // previously description
  ai_decision: string | null
  ai_rationale: string | null
  human_decision: string | null
  human_note: string | null   // previously approval_rationale
  created_at: string | null
  [key: string]: unknown
}

/** Generic result wrapper */
export interface ApprovalResult<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

// ---------------------------------------------------------------------------
// Constants – 22 Judgment Points
// ---------------------------------------------------------------------------

/**
 * Full specification of the 22 judgment points (JP001-JP022).
 *
 * Migrated from the Python `APPROVAL_POINTS_SPEC` list with added
 * English descriptions and refined categorisation.
 */
export const APPROVAL_POINTS_SPEC: readonly ApprovalPointSpec[] = Object.freeze(
  [
    // --- FINANCIAL (JP001-JP008) ---
    {
      point_id: 'JP001',
      point_name: 'revenue_growth_rate',
      display_name: '매출 성장률',
      category: 'FINANCIAL',
      importance: 'high',
      valuation_method: 'dcf',
      description:
        'Projected revenue growth rate used in the DCF free-cash-flow forecast.',
    },
    {
      point_id: 'JP002',
      point_name: 'ebit_margin',
      display_name: '영업이익률',
      category: 'FINANCIAL',
      importance: 'medium',
      valuation_method: 'dcf',
      description:
        'Operating profit margin assumption for the projection period.',
    },
    {
      point_id: 'JP003',
      point_name: 'wacc_rate',
      display_name: 'WACC (가중평균자본비용)',
      category: 'FINANCIAL',
      importance: 'high',
      valuation_method: 'dcf',
      description:
        'Weighted Average Cost of Capital used to discount future cash flows.',
    },
    {
      point_id: 'JP004',
      point_name: 'terminal_growth_rate',
      display_name: '영구성장률',
      category: 'FINANCIAL',
      importance: 'medium',
      valuation_method: 'dcf',
      description:
        'Long-term sustainable growth rate for the terminal value calculation.',
    },
    {
      point_id: 'JP005',
      point_name: 'forecast_period',
      display_name: '예측 기간',
      category: 'FINANCIAL',
      importance: 'low',
      valuation_method: 'dcf',
      description:
        'Number of years in the explicit forecast period before terminal value.',
    },
    {
      point_id: 'JP006',
      point_name: 'capex_rate',
      display_name: '자본적지출률',
      category: 'FINANCIAL',
      importance: 'medium',
      valuation_method: 'dcf',
      description:
        'Capital expenditure as a percentage of revenue during the forecast period.',
    },
    {
      point_id: 'JP007',
      point_name: 'working_capital_change',
      display_name: '운전자본 변화',
      category: 'FINANCIAL',
      importance: 'medium',
      valuation_method: 'dcf',
      description:
        'Projected change in net working capital that affects free cash flow.',
    },
    {
      point_id: 'JP008',
      point_name: 'beta_coefficient',
      display_name: '베타 계수',
      category: 'FINANCIAL',
      importance: 'medium',
      valuation_method: 'dcf',
      description:
        'Equity beta used in CAPM to derive the cost of equity component of WACC.',
    },

    // --- MARKET (JP009-JP012) ---
    {
      point_id: 'JP009',
      point_name: 'comparable_companies',
      display_name: '비교기업 목록',
      category: 'MARKET',
      importance: 'medium',
      valuation_method: 'relative',
      description:
        'Set of peer companies selected for relative valuation multiples.',
    },
    {
      point_id: 'JP010',
      point_name: 'selected_multiple',
      display_name: '선택 멀티플',
      category: 'MARKET',
      importance: 'medium',
      valuation_method: 'relative',
      description:
        'Primary valuation multiple chosen (PER, PBR, EV/EBITDA, etc.).',
    },
    {
      point_id: 'JP011',
      point_name: 'industry_multiple',
      display_name: '업종 멀티플',
      category: 'MARKET',
      importance: 'medium',
      valuation_method: 'relative',
      description:
        'Industry-average multiple applied as a cross-check or primary input.',
    },
    {
      point_id: 'JP012',
      point_name: 'unlisted_discount',
      display_name: '비상장 할인율',
      category: 'MARKET',
      importance: 'high',
      valuation_method: 'relative',
      description:
        'Discount rate applied to reflect illiquidity of unlisted shares.',
    },

    // --- ASSET (JP013-JP018) ---
    {
      point_id: 'JP013',
      point_name: 'land_building_appraisal',
      display_name: '토지/건물 감정평가액',
      category: 'ASSET',
      importance: 'high',
      valuation_method: 'asset',
      description:
        'Fair market value of land and buildings from certified appraisals.',
    },
    {
      point_id: 'JP014',
      point_name: 'patent_valuation',
      display_name: '특허권 평가액',
      category: 'ASSET',
      importance: 'medium',
      valuation_method: 'asset',
      description:
        'Assessed value of patents and intellectual property held by the company.',
    },
    {
      point_id: 'JP015',
      point_name: 'contingent_liabilities',
      display_name: '우발채무',
      category: 'ASSET',
      importance: 'high',
      valuation_method: 'asset',
      description:
        'Contingent liabilities (lawsuits, guarantees) that may affect net asset value.',
    },
    {
      point_id: 'JP016',
      point_name: 'allowance_for_bad_debts',
      display_name: '대손충당금',
      category: 'ASSET',
      importance: 'medium',
      valuation_method: 'asset',
      description:
        'Adequacy of the bad-debt reserve relative to receivable quality.',
    },
    {
      point_id: 'JP017',
      point_name: 'inventory_nrv',
      display_name: '재고자산 순실현가치',
      category: 'ASSET',
      importance: 'medium',
      valuation_method: 'asset',
      description:
        'Net Realisable Value of inventory versus its book value.',
    },
    {
      point_id: 'JP018',
      point_name: 'unlisted_equity_valuation',
      display_name: '비상장주식 평가액',
      category: 'ASSET',
      importance: 'high',
      valuation_method: 'asset',
      description:
        'Fair value estimate for unlisted equity investments on the balance sheet.',
    },

    // --- LEGAL (JP019-JP022) ---
    {
      point_id: 'JP019',
      point_name: 'income_value_method',
      display_name: '수익가치 산정 방법',
      category: 'LEGAL',
      importance: 'medium',
      valuation_method: 'capital_market_law',
      description:
        'Method used to compute the income/earnings value under the Capital Market Act.',
    },
    {
      point_id: 'JP020',
      point_name: 'asset_income_weight',
      display_name: '자산가치/수익가치 가중치',
      category: 'LEGAL',
      importance: 'medium',
      valuation_method: 'capital_market_law',
      description:
        'Weighting ratio between asset value and income value per statutory formula.',
    },
    {
      point_id: 'JP021',
      point_name: 'three_year_avg_income',
      display_name: '최근 3년 평균 순손익',
      category: 'LEGAL',
      importance: 'medium',
      valuation_method: 'inheritance_tax_law',
      description:
        'Three-year weighted average net income used for the Inheritance Tax Act valuation.',
    },
    {
      point_id: 'JP022',
      point_name: 'ownership_ratio',
      display_name: '지분율 및 주주 유형',
      category: 'LEGAL',
      importance: 'high',
      valuation_method: 'inheritance_tax_law',
      description:
        'Ownership percentage and shareholder classification affecting premium/discount.',
    },
  ],
)

/** Quick lookup map: point_id -> spec */
const SPEC_MAP = new Map<string, ApprovalPointSpec>(
  APPROVAL_POINTS_SPEC.map((s) => [s.point_id, s]),
)

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

const POINT_ID_REGEX = /^JP\d{3}$/

function isValidPointId(pointId: string): boolean {
  return typeof pointId === 'string' && POINT_ID_REGEX.test(pointId)
}

function isValidProjectId(projectId: string): boolean {
  if (!projectId || typeof projectId !== 'string') return false
  const pattern = /^[A-Za-z0-9_-]{5,50}$/
  const uuid =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  return pattern.test(projectId) || uuid.test(projectId)
}

function isValidDecision(
  d: string,
): d is 'approved' | 'rejected' | 'custom' {
  return d === 'approved' || d === 'rejected' || d === 'custom'
}

// ---------------------------------------------------------------------------
// ApprovalPointManager
// ---------------------------------------------------------------------------

/**
 * Handles creation, approval, rejection, and querying of the 22 accountant
 * judgment points for a valuation project.
 *
 * Usage:
 * ```ts
 * const mgr = new ApprovalPointManager()
 * await mgr.createApprovalPoints('PROJECT-123')
 * await mgr.approveStep('PROJECT-123', 'JP001', 'approved')
 * ```
 */
export class ApprovalPointManager {
  // -----------------------------------------------------------------------
  // Creation
  // -----------------------------------------------------------------------

  /**
   * Initialises all 22 approval points for a project.
   *
   * Inserts one row per judgment point into the `approval_points` table.
   * Skips insertion if the project already has approval points (idempotent).
   *
   * @param projectId - Target project identifier.
   * @returns The number of points created.
   */
  async createApprovalPoints(
    projectId: string,
  ): Promise<ApprovalResult<{ created_count: number }>> {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }

      const supabase = await createClient()

      // Check for existing points (idempotency)
      const { data: existing, error: checkErr } = await supabase
        .from('approval_points')
        .select('point_id')
        .eq('project_id', projectId)
        .limit(1)

      if (checkErr) {
        return { success: false, error: checkErr.message }
      }

      if (existing && existing.length > 0) {
        return {
          success: false,
          error:
            'Approval points already exist for this project. Delete them first to re-create.',
        }
      }

      const now = new Date().toISOString()
      // Schema-v5: approval_points has point_code, category, question,
      // ai_decision, ai_rationale, human_decision, human_note, created_at.
      // Legacy fields (point_name, display_name, importance, valuation_method,
      // description, status, approved_by, updated_at, etc.) were dropped.
      const rows = APPROVAL_POINTS_SPEC.map((spec) => ({
        project_id: projectId,
        point_code: spec.point_id,   // JP001-JP022 stored in point_code
        category: spec.category as string,
        question: spec.description,   // description maps to question
        ai_decision: null,
        ai_rationale: null,
        human_decision: null,
        human_note: null,
        created_at: now,
      }))

      const { error: insertErr } = await supabase
        .from('approval_points')
        .insert(rows)

      if (insertErr) {
        return { success: false, error: insertErr.message }
      }

      return { success: true, data: { created_count: rows.length } }
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Unknown error in createApprovalPoints'
      console.error('[ApprovalPointManager.createApprovalPoints]', msg)
      return { success: false, error: msg }
    }
  }

  // -----------------------------------------------------------------------
  // Individual approve / reject
  // -----------------------------------------------------------------------

  /**
   * Records an accountant's decision on a single approval point.
   *
   * @param projectId  - Target project identifier.
   * @param pointId    - Judgment point ID (JP001-JP022).
   * @param decision   - 'approved', 'rejected', or 'custom'.
   * @param customValue - Custom value when decision is 'custom'.
   * @param rationale  - Rationale / notes explaining the decision.
   * @param approvedBy - Email or identifier of the approving accountant.
   * @returns The updated approval point row.
   */
  async approveStep(
    projectId: string,
    pointId: string,
    decision: 'approved' | 'rejected' | 'custom',
    customValue?: unknown,
    rationale?: string,
    approvedBy?: string,
  ): Promise<ApprovalResult<ApprovalPointRow>> {
    try {
      // --- Input validation ---
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }
      if (!isValidPointId(pointId)) {
        return {
          success: false,
          error: 'Invalid point_id format. Expected JP001-JP022.',
        }
      }
      if (!isValidDecision(decision)) {
        return {
          success: false,
          error:
            "Invalid decision. Must be 'approved', 'rejected', or 'custom'.",
        }
      }
      if (decision === 'custom' && customValue === undefined) {
        return {
          success: false,
          error: "custom_value is required when decision is 'custom'.",
        }
      }
      if (decision === 'rejected' && !rationale) {
        return {
          success: false,
          error: "rationale is required when decision is 'rejected'.",
        }
      }

      const supabase = await createClient()

      // --- Fetch existing point ---
      const { data: point, error: fetchErr } = await supabase
        .from('approval_points')
        .select('*')
        .eq('project_id', projectId)
        .eq('point_code', pointId)   // schema-v5: point_id is stored in point_code
        .single()

      if (fetchErr || !point) {
        return {
          success: false,
          error:
            fetchErr?.message ??
            `Approval point ${pointId} not found for project ${projectId}.`,
        }
      }

      const existing = point as unknown as ApprovalPointRow

      // --- Duplicate decision prevention ---
      if (
        existing.human_decision !== null &&
        existing.human_decision !== 'pending'
      ) {
        return {
          success: false,
          error: `Point ${pointId} has already been decided (${existing.human_decision}). Reset it first to change the decision.`,
        }
      }

      // --- Persist (schema-v5 fields only) ---
      // Legacy fields (custom_value, status, approved_by, approved_at,
      // approval_rationale, impact_analysis, updated_at) were removed in v5.
      // human_note stores the rationale; custom decision value is embedded in human_note.
      const noteValue = decision === 'custom' && customValue !== undefined
        ? `${rationale ?? ''} [custom_value: ${JSON.stringify(customValue)}]`
        : (rationale ?? null)
      const { data: updated, error: updateErr } = await supabase
        .from('approval_points')
        .update({
          human_decision: decision,
          human_note: noteValue,
        })
        .eq('project_id', projectId)
        .eq('point_code', pointId)   // schema-v5: use point_code
        .select()
        .single()

      if (updateErr || !updated) {
        return { success: false, error: updateErr?.message ?? 'Update failed.' }
      }

      return { success: true, data: updated as unknown as ApprovalPointRow }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : 'Unknown error in approveStep'
      console.error('[ApprovalPointManager.approveStep]', msg)
      return { success: false, error: msg }
    }
  }

  /**
   * Convenience method to reject an approval point with a mandatory rationale.
   *
   * @param projectId - Target project identifier.
   * @param pointId   - Judgment point ID (JP001-JP022).
   * @param rationale - Explanation for the rejection.
   * @param rejectedBy - Email or identifier of the rejecting accountant.
   */
  async rejectStep(
    projectId: string,
    pointId: string,
    rationale: string,
    rejectedBy?: string,
  ): Promise<ApprovalResult<ApprovalPointRow>> {
    if (!rationale || rationale.trim().length === 0) {
      return {
        success: false,
        error: 'Rationale is required when rejecting an approval point.',
      }
    }
    return this.approveStep(
      projectId,
      pointId,
      'rejected',
      undefined,
      rationale,
      rejectedBy,
    )
  }

  // -----------------------------------------------------------------------
  // Batch operations
  // -----------------------------------------------------------------------

  /**
   * Processes multiple approval decisions in a single call.
   *
   * Each decision is applied independently; failures on one point do not
   * block others. After all decisions are processed, the method checks
   * whether all 22 points have been decided and, if so, returns a flag
   * indicating that the project may advance.
   *
   * @param projectId - Target project identifier.
   * @param decisions - Array of individual decisions.
   * @param approvedBy - Email or identifier shared across all decisions.
   */
  async batchApprove(
    projectId: string,
    decisions: ApprovalDecision[],
    approvedBy?: string,
  ): Promise<
    ApprovalResult<{
      success_count: number
      failed_count: number
      errors: Array<{ point_id: string; error: string }>
      all_decided: boolean
      pending_count: number
    }>
  > {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }
      if (!Array.isArray(decisions) || decisions.length === 0) {
        return { success: false, error: 'decisions array must not be empty.' }
      }

      let successCount = 0
      let failedCount = 0
      const errors: Array<{ point_id: string; error: string }> = []

      for (const d of decisions) {
        if (!isValidDecision(d.decision)) {
          failedCount++
          errors.push({
            point_id: d.point_id,
            error: `Invalid decision: ${d.decision}`,
          })
          continue
        }

        const result = await this.approveStep(
          projectId,
          d.point_id,
          d.decision,
          d.custom_value,
          d.rationale,
          approvedBy,
        )

        if (result.success) {
          successCount++
        } else {
          failedCount++
          errors.push({
            point_id: d.point_id,
            error: result.error ?? 'Unknown error',
          })
        }
      }

      // Check remaining pending points
      const pending = await this.getPendingApprovals(projectId)
      const pendingCount = pending.success ? (pending.data?.length ?? 0) : 0

      return {
        success: true,
        data: {
          success_count: successCount,
          failed_count: failedCount,
          errors,
          all_decided: pendingCount === 0,
          pending_count: pendingCount,
        },
      }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : 'Unknown error in batchApprove'
      console.error('[ApprovalPointManager.batchApprove]', msg)
      return { success: false, error: msg }
    }
  }

  // -----------------------------------------------------------------------
  // Queries
  // -----------------------------------------------------------------------

  /**
   * Retrieves the full approval history for a project, ordered by point_id.
   *
   * @param projectId - Target project identifier.
   * @returns Array of approval point rows with summary statistics.
   */
  async getApprovalHistory(
    projectId: string,
  ): Promise<
    ApprovalResult<{
      points: ApprovalPointRow[]
      total: number
      approved_count: number
      rejected_count: number
      custom_count: number
      pending_count: number
    }>
  > {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }

      const supabase = await createClient()

      const { data, error } = await supabase
        .from('approval_points')
        .select('*')
        .eq('project_id', projectId)
        .order('point_code', { ascending: true })   // schema-v5: point_code replaces point_id

      if (error) {
        return { success: false, error: error.message }
      }

      const points = (data ?? []) as unknown as ApprovalPointRow[]
      const total = points.length
      const approvedCount = points.filter(
        (p) => p.human_decision === 'approved',
      ).length
      const rejectedCount = points.filter(
        (p) => p.human_decision === 'rejected',
      ).length
      const customCount = points.filter(
        (p) => p.human_decision === 'custom',
      ).length
      const pendingCount = points.filter(
        (p) => p.human_decision === null || p.human_decision === 'pending',
      ).length

      return {
        success: true,
        data: {
          points,
          total,
          approved_count: approvedCount,
          rejected_count: rejectedCount,
          custom_count: customCount,
          pending_count: pendingCount,
        },
      }
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Unknown error in getApprovalHistory'
      console.error('[ApprovalPointManager.getApprovalHistory]', msg)
      return { success: false, error: msg }
    }
  }

  /**
   * Returns only the pending (undecided) approval points for a project.
   *
   * @param projectId - Target project identifier.
   */
  async getPendingApprovals(
    projectId: string,
  ): Promise<ApprovalResult<ApprovalPointRow[]>> {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }

      const supabase = await createClient()

      // schema-v5: no 'status' column; pending points are those with null human_decision
      const { data, error } = await supabase
        .from('approval_points')
        .select('*')
        .eq('project_id', projectId)
        .is('human_decision', null)
        .order('point_code', { ascending: true })   // schema-v5: point_code replaces point_id

      if (error) {
        return { success: false, error: error.message }
      }

      return {
        success: true,
        data: (data ?? []) as unknown as ApprovalPointRow[],
      }
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Unknown error in getPendingApprovals'
      console.error('[ApprovalPointManager.getPendingApprovals]', msg)
      return { success: false, error: msg }
    }
  }

  /**
   * Checks whether all approval points for a given workflow step have been
   * decided (approved or custom). Looks up which points map to the step's
   * valuation method and verifies none are still pending.
   *
   * For simplicity, the current implementation checks if all 22 points across
   * the entire project are decided, since the approval gate at step 7 requires
   * all judgment points to be resolved before the workflow can advance.
   *
   * @param projectId  - Target project identifier.
   * @param _stepNumber - Step number (reserved for future per-step logic).
   */
  async isStepApproved(
    projectId: string,
    _stepNumber: number,
  ): Promise<ApprovalResult<{ approved: boolean; pending_count: number }>> {
    try {
      if (!isValidProjectId(projectId)) {
        return { success: false, error: 'Invalid project_id format.' }
      }

      const pending = await this.getPendingApprovals(projectId)
      if (!pending.success) {
        return { success: false, error: pending.error }
      }

      const count = pending.data?.length ?? 0
      return {
        success: true,
        data: { approved: count === 0, pending_count: count },
      }
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Unknown error in isStepApproved'
      console.error('[ApprovalPointManager.isStepApproved]', msg)
      return { success: false, error: msg }
    }
  }

  // -----------------------------------------------------------------------
  // Static helpers
  // -----------------------------------------------------------------------

  /**
   * Returns the static specification for a single approval point.
   *
   * @param pointId - Judgment point ID (JP001-JP022).
   */
  static getPointSpec(pointId: string): ApprovalPointSpec | undefined {
    return SPEC_MAP.get(pointId)
  }

  /**
   * Returns all 22 approval point specifications.
   */
  static getAllSpecs(): readonly ApprovalPointSpec[] {
    return APPROVAL_POINTS_SPEC
  }

  /**
   * Returns approval point specs filtered by category.
   *
   * @param category - One of FINANCIAL, MARKET, ASSET, LEGAL.
   */
  static getSpecsByCategory(category: ApprovalCategory): ApprovalPointSpec[] {
    return APPROVAL_POINTS_SPEC.filter((s) => s.category === category)
  }

  // -----------------------------------------------------------------------
  // Private helpers
  // -----------------------------------------------------------------------

  /**
   * Computes a basic impact analysis for a decision.
   *
   * The Python original hardcoded all impact values to zero. This
   * implementation provides a structural placeholder with the correct shape
   * and a flag indicating the analysis is estimated. A full implementation
   * would invoke the relevant valuation engine to re-calculate.
   */
  private computeImpactAnalysis(
    pointId: string,
    decision: string,
    aiValue: unknown,
    customValue: unknown,
  ): Record<string, unknown> {
    const spec = SPEC_MAP.get(pointId)
    const affectedMethods = spec ? [spec.valuation_method] : []

    // When the decision is 'approved' the AI value is kept, so the nominal
    // change is zero.  For 'custom' a real re-calculation would be needed.
    const hasChange = decision === 'custom' && customValue !== undefined
    const changeNote = hasChange
      ? 'Re-calculation required with custom value.'
      : 'No change from AI-proposed value.'

    return {
      point_id: pointId,
      decision,
      ai_value: aiValue,
      custom_value: customValue ?? null,
      affected_methods: affectedMethods,
      value_change_estimated: hasChange,
      note: changeNote,
    }
  }
}
