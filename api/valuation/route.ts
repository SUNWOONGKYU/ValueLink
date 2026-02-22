/**
 * @task S2BA1
 * @description Valuation Workflow REST API Endpoint
 *
 * GET  /api/valuation?project_id=XXX  - Query workflow status, approval points, current step
 * POST /api/valuation                 - Execute workflow actions (advance, approve, reject, batch_approve, create_points)
 *
 * Migrated from Python/FastAPI to Next.js Route Handler with:
 *  - TypeScript strict-mode compatible code
 *  - Input validation on all parameters
 *  - Supabase session-based authentication
 *  - Project ownership authorization
 *  - Consistent JSON response envelope
 *  - Proper HTTP status codes
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { WorkflowManager } from '@/lib/workflow/workflow-manager'
import {
  ApprovalPointManager,
  type ApprovalDecision,
} from '@/lib/workflow/approval-points'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Standard API response envelope */
interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

/** POST request body shape */
interface PostBody {
  action: string
  project_id: string
  /** For 'approve' action */
  point_id?: string
  decision?: 'approved' | 'rejected' | 'custom'
  custom_value?: unknown
  rationale?: string
  approved_by?: string
  /** For 'batch_approve' action */
  decisions?: ApprovalDecision[]
  /** For 'can_advance' action */
  target_step?: number
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a typed JSON response with the standard envelope.
 */
function jsonResponse<T>(
  body: ApiResponse<T>,
  status: number,
): NextResponse<ApiResponse<T>> {
  return NextResponse.json(body, { status })
}

/**
 * Validates a project ID string.
 */
function isValidProjectId(id: unknown): id is string {
  if (typeof id !== 'string' || id.length === 0) return false
  const pattern = /^[A-Za-z0-9_-]{5,50}$/
  const uuid =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  return pattern.test(id) || uuid.test(id)
}

const VALID_ACTIONS = new Set([
  'advance',
  'approve',
  'reject',
  'batch_approve',
  'create_points',
  'can_advance',
])

/**
 * Authenticates the request via Supabase session and returns the user.
 * Returns null and a NextResponse if authentication fails.
 */
async function authenticate(): Promise<
  | { user: { id: string; email?: string }; error?: never }
  | { user?: never; error: NextResponse }
> {
  try {
    const supabase = await createClient()
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser()

    if (error || !user) {
      return {
        error: jsonResponse(
          { success: false, error: 'Authentication required.' },
          401,
        ),
      }
    }

    return { user: { id: user.id, email: user.email ?? undefined } }
  } catch {
    return {
      error: jsonResponse(
        { success: false, error: 'Authentication service unavailable.' },
        500,
      ),
    }
  }
}

/**
 * Checks whether the authenticated user owns (or has access to) the project.
 * Returns null if authorized, or a NextResponse if not.
 */
async function authorizeProjectAccess(
  projectId: string,
  userId: string,
): Promise<NextResponse | null> {
  try {
    const supabase = await createClient()
    const { data, error } = await supabase
      .from('valuation_projects')
      .select('owner_id')
      .eq('project_id', projectId)
      .single()

    if (error || !data) {
      return jsonResponse(
        { success: false, error: 'Project not found.' },
        404,
      )
    }

    const row = data as unknown as { owner_id: string }
    if (row.owner_id !== userId) {
      return jsonResponse(
        {
          success: false,
          error: 'You do not have permission to access this project.',
        },
        403,
      )
    }

    return null // authorized
  } catch {
    return jsonResponse(
      { success: false, error: 'Authorization check failed.' },
      500,
    )
  }
}

// ---------------------------------------------------------------------------
// GET /api/valuation
// ---------------------------------------------------------------------------

/**
 * Queries the current workflow status for a project.
 *
 * Query params:
 *   - project_id (required) - The project to look up.
 *   - include    (optional) - Comma-separated list: "steps", "approvals", "pending"
 *
 * Response includes current step information and optionally approval point data.
 */
export async function GET(request: NextRequest) {
  try {
    // 1. Authenticate
    const auth = await authenticate()
    if (auth.error) return auth.error

    // 2. Parse & validate query params
    const { searchParams } = new URL(request.url)
    const projectId = searchParams.get('project_id')

    if (!isValidProjectId(projectId)) {
      return jsonResponse(
        {
          success: false,
          error:
            'project_id query parameter is required and must be a valid identifier.',
        },
        400,
      )
    }

    // 3. Authorize
    const authzErr = await authorizeProjectAccess(projectId, auth.user.id)
    if (authzErr) return authzErr

    // 4. Fetch workflow status
    const workflowMgr = new WorkflowManager()
    const stepResult = await workflowMgr.getCurrentStep(projectId)

    if (!stepResult.success) {
      return jsonResponse(
        { success: false, error: stepResult.error },
        404,
      )
    }

    // 5. Optionally include approval data
    const include = (searchParams.get('include') ?? '')
      .split(',')
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean)

    const responseData: Record<string, unknown> = {
      workflow: stepResult.data,
      all_steps: include.includes('steps')
        ? workflowMgr.getAllSteps()
        : undefined,
    }

    if (include.includes('approvals') || include.includes('pending')) {
      const approvalMgr = new ApprovalPointManager()

      if (include.includes('approvals')) {
        const history = await approvalMgr.getApprovalHistory(projectId)
        if (history.success) {
          responseData.approvals = history.data
        }
      }

      if (include.includes('pending')) {
        const pending = await approvalMgr.getPendingApprovals(projectId)
        if (pending.success) {
          responseData.pending_approvals = pending.data
        }
      }
    }

    return jsonResponse({ success: true, data: responseData }, 200)
  } catch (err) {
    const message =
      err instanceof Error ? err.message : 'Internal server error'
    console.error('[GET /api/valuation]', message)
    return jsonResponse({ success: false, error: message }, 500)
  }
}

// ---------------------------------------------------------------------------
// POST /api/valuation
// ---------------------------------------------------------------------------

/**
 * Executes a workflow action.
 *
 * Request body (JSON):
 * ```json
 * {
 *   "action": "advance" | "approve" | "reject" | "batch_approve" | "create_points" | "can_advance",
 *   "project_id": "...",
 *   // additional fields depending on action
 * }
 * ```
 *
 * Actions:
 *   - **advance**        - Move to the next workflow step
 *   - **approve**        - Approve a single judgment point (requires point_id, decision)
 *   - **reject**         - Reject a single judgment point  (requires point_id, rationale)
 *   - **batch_approve**  - Approve/reject multiple points  (requires decisions[])
 *   - **create_points**  - Initialise 22 approval points for a project
 *   - **can_advance**    - Check if advancement to target_step is possible
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Authenticate
    const auth = await authenticate()
    if (auth.error) return auth.error

    // 2. Parse body
    let body: PostBody
    try {
      body = (await request.json()) as PostBody
    } catch {
      return jsonResponse(
        { success: false, error: 'Invalid JSON in request body.' },
        400,
      )
    }

    // 3. Validate required fields
    const { action, project_id: projectId } = body

    if (!action || typeof action !== 'string') {
      return jsonResponse(
        { success: false, error: 'action field is required.' },
        400,
      )
    }

    if (!VALID_ACTIONS.has(action)) {
      return jsonResponse(
        {
          success: false,
          error: `Unknown action "${action}". Valid actions: ${[...VALID_ACTIONS].join(', ')}`,
        },
        400,
      )
    }

    if (!isValidProjectId(projectId)) {
      return jsonResponse(
        {
          success: false,
          error: 'project_id is required and must be a valid identifier.',
        },
        400,
      )
    }

    // 4. Authorize
    const authzErr = await authorizeProjectAccess(projectId, auth.user.id)
    if (authzErr) return authzErr

    // 5. Dispatch to handler
    switch (action) {
      case 'advance':
        return handleAdvance(projectId)

      case 'approve':
        return handleApprove(projectId, body, auth.user.email)

      case 'reject':
        return handleReject(projectId, body, auth.user.email)

      case 'batch_approve':
        return handleBatchApprove(projectId, body, auth.user.email)

      case 'create_points':
        return handleCreatePoints(projectId)

      case 'can_advance':
        return handleCanAdvance(projectId, body)

      default:
        return jsonResponse(
          { success: false, error: `Unhandled action: ${action}` },
          400,
        )
    }
  } catch (err) {
    const message =
      err instanceof Error ? err.message : 'Internal server error'
    console.error('[POST /api/valuation]', message)
    return jsonResponse({ success: false, error: message }, 500)
  }
}

// ---------------------------------------------------------------------------
// Action handlers
// ---------------------------------------------------------------------------

/**
 * Advances the workflow to the next step.
 */
async function handleAdvance(projectId: string) {
  const mgr = new WorkflowManager()
  const result = await mgr.advanceStep(projectId)

  if (!result.success) {
    // Distinguish between "cannot advance" (400) and "not found" (404)
    const status = result.error?.includes('not found') ? 404 : 400
    return jsonResponse({ success: false, error: result.error }, status)
  }

  return jsonResponse({ success: true, data: result.data }, 200)
}

/**
 * Approves a single judgment point.
 */
async function handleApprove(
  projectId: string,
  body: PostBody,
  userEmail?: string,
) {
  const { point_id, decision, custom_value, rationale } = body

  if (!point_id) {
    return jsonResponse(
      { success: false, error: 'point_id is required for approve action.' },
      400,
    )
  }

  if (!decision || !['approved', 'rejected', 'custom'].includes(decision)) {
    return jsonResponse(
      {
        success: false,
        error:
          "decision is required and must be 'approved', 'rejected', or 'custom'.",
      },
      400,
    )
  }

  const mgr = new ApprovalPointManager()
  const result = await mgr.approveStep(
    projectId,
    point_id,
    decision,
    custom_value,
    rationale,
    body.approved_by ?? userEmail,
  )

  if (!result.success) {
    const status = result.error?.includes('not found') ? 404 : 400
    return jsonResponse({ success: false, error: result.error }, status)
  }

  return jsonResponse({ success: true, data: result.data }, 200)
}

/**
 * Rejects a single judgment point (convenience wrapper requiring rationale).
 */
async function handleReject(
  projectId: string,
  body: PostBody,
  userEmail?: string,
) {
  const { point_id, rationale } = body

  if (!point_id) {
    return jsonResponse(
      { success: false, error: 'point_id is required for reject action.' },
      400,
    )
  }

  if (!rationale || rationale.trim().length === 0) {
    return jsonResponse(
      {
        success: false,
        error: 'rationale is required when rejecting an approval point.',
      },
      400,
    )
  }

  const mgr = new ApprovalPointManager()
  const result = await mgr.rejectStep(
    projectId,
    point_id,
    rationale,
    body.approved_by ?? userEmail,
  )

  if (!result.success) {
    const status = result.error?.includes('not found') ? 404 : 400
    return jsonResponse({ success: false, error: result.error }, status)
  }

  return jsonResponse({ success: true, data: result.data }, 200)
}

/**
 * Batch-approves multiple judgment points.
 */
async function handleBatchApprove(
  projectId: string,
  body: PostBody,
  userEmail?: string,
) {
  const { decisions } = body

  if (!Array.isArray(decisions) || decisions.length === 0) {
    return jsonResponse(
      {
        success: false,
        error: 'decisions array is required and must contain at least one entry.',
      },
      400,
    )
  }

  // Validate each decision has at least point_id and decision
  for (const d of decisions) {
    if (!d.point_id || !d.decision) {
      return jsonResponse(
        {
          success: false,
          error:
            'Each decision must include point_id and decision fields.',
        },
        400,
      )
    }
  }

  const mgr = new ApprovalPointManager()
  const result = await mgr.batchApprove(
    projectId,
    decisions,
    body.approved_by ?? userEmail,
  )

  if (!result.success) {
    return jsonResponse({ success: false, error: result.error }, 400)
  }

  return jsonResponse({ success: true, data: result.data }, 200)
}

/**
 * Initialises the 22 approval points for a project.
 */
async function handleCreatePoints(projectId: string) {
  const mgr = new ApprovalPointManager()
  const result = await mgr.createApprovalPoints(projectId)

  if (!result.success) {
    const status = result.error?.includes('already exist') ? 409 : 400
    return jsonResponse({ success: false, error: result.error }, status)
  }

  return jsonResponse({ success: true, data: result.data }, 201)
}

/**
 * Checks whether a project can advance to a specific target step.
 */
async function handleCanAdvance(projectId: string, body: PostBody) {
  const { target_step } = body

  if (
    target_step === undefined ||
    typeof target_step !== 'number' ||
    !Number.isInteger(target_step) ||
    target_step < 1 ||
    target_step > 14
  ) {
    return jsonResponse(
      {
        success: false,
        error: 'target_step is required and must be an integer between 1 and 14.',
      },
      400,
    )
  }

  const mgr = new WorkflowManager()
  const result = await mgr.canAdvanceToStep(projectId, target_step)

  if (!result.success) {
    const status = result.error?.includes('not found') ? 404 : 400
    return jsonResponse({ success: false, error: result.error }, status)
  }

  return jsonResponse({ success: true, data: result.data }, 200)
}
