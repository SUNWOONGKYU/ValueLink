/**
 * @task S2BA2
 * @description Project Query and Update API
 *
 * Endpoints:
 *   GET /api/projects  - List projects (role-based filtering)
 *   PUT /api/projects  - Update project status / step (owner or assigned accountant)
 *
 * Schema alignment: schema-v4-final.sql (projects table)
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ProjectStatus =
  | 'in_progress'
  | 'human_approval'
  | 'draft_generated'
  | 'completed'
  | 'archived'
type UserRole = 'customer' | 'accountant' | 'admin'

interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

/** Body shape for PUT (update project). */
interface UpdateProjectBody {
  project_id: string
  /** Target step (must be current_step + 1, sequential only). */
  target_step?: number
  /** New project status. */
  status?: ProjectStatus
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Total number of steps in the valuation workflow. */
const MAX_STEP = 14

/** Valid project statuses. */
const VALID_STATUSES: readonly ProjectStatus[] = [
  'in_progress',
  'human_approval',
  'draft_generated',
  'completed',
  'archived',
] as const

/**
 * Mapping from step number to the expected project status.
 * Used to automatically derive the correct status when a step advances.
 */
const STEP_STATUS_MAP: Record<number, ProjectStatus> = {
  7: 'human_approval',
  8: 'draft_generated',
  14: 'completed',
}

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

function validateUpdateBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return 'Request body is required.'

  const b = body as Record<string, unknown>

  if (!b.project_id || typeof b.project_id !== 'string') {
    return 'project_id is required.'
  }

  if (b.target_step !== undefined) {
    if (typeof b.target_step !== 'number' || !Number.isInteger(b.target_step)) {
      return 'target_step must be an integer.'
    }
    if (b.target_step < 1 || b.target_step > MAX_STEP) {
      return `target_step must be between 1 and ${MAX_STEP}.`
    }
  }

  if (b.status !== undefined) {
    if (!VALID_STATUSES.includes(b.status as ProjectStatus)) {
      return `status must be one of: ${VALID_STATUSES.join(', ')}.`
    }
  }

  if (b.target_step === undefined && b.status === undefined) {
    return 'At least one of target_step or status must be provided.'
  }

  return null
}

// ---------------------------------------------------------------------------
// Auth helper
// ---------------------------------------------------------------------------

async function getAuthenticatedUser(supabase: Awaited<ReturnType<typeof createClient>>) {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser()

  if (error || !user) {
    return { user: null, role: null }
  }

  const { data: profile } = await supabase
    .from('users')
    .select('role')
    .eq('user_id', user.id)
    .single()

  return {
    user,
    role: (profile?.role as UserRole) ?? 'customer',
  }
}

// ---------------------------------------------------------------------------
// Pagination helper
// ---------------------------------------------------------------------------

interface PaginationParams {
  page: number
  limit: number
}

function parsePagination(searchParams: URLSearchParams): PaginationParams {
  const page = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10) || 1)
  const limit = Math.min(100, Math.max(1, parseInt(searchParams.get('limit') ?? '20', 10) || 20))
  return { page, limit }
}

// ---------------------------------------------------------------------------
// GET /api/projects
// ---------------------------------------------------------------------------

/**
 * Lists projects with role-based filtering and optional status filter.
 *
 * - **Customer**: sees only projects they own (`user_id`).
 * - **Accountant**: sees only projects assigned to them (`accountant_id`).
 * - **Admin**: sees all projects.
 *
 * The response includes a join with the `users` table for the assigned
 * accountant name and email when available.
 *
 * Query params:
 *   - `status` - Filter by project status.
 *   - `page`   - Page number (default 1).
 *   - `limit`  - Items per page (default 20, max 100).
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response with the paginated list of projects.
 */
export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse>> {
  try {
    const supabase = await createClient()
    const { user, role } = await getAuthenticatedUser(supabase)

    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Authentication required.' },
        { status: 401 },
      )
    }

    const searchParams = request.nextUrl.searchParams
    const { page, limit } = parsePagination(searchParams)
    const statusFilter = searchParams.get('status') as ProjectStatus | null

    // Validate status filter
    if (statusFilter && !VALID_STATUSES.includes(statusFilter)) {
      return NextResponse.json(
        {
          success: false,
          error: `Invalid status filter. Must be one of: ${VALID_STATUSES.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    // Build query with join for accountant info (aligned with schema-v4-final.sql)
    let query = supabase
      .from('projects')
      .select(
        `project_id,
         request_id,
         user_id,
         company_name_kr,
         company_name_en,
         industry,
         valuation_purpose,
         requested_methods,
         target_date,
         requirements,
         status,
         current_step,
         accountant_id,
         accountant:users!projects_accountant_id_fkey (
           user_id,
           email
         ),
         created_at,
         updated_at`,
        { count: 'exact' },
      )

    // Role-based filtering
    switch (role) {
      case 'customer':
        query = query.eq('user_id', user.id)
        break
      case 'accountant':
        query = query.eq('accountant_id', user.id)
        break
      case 'admin':
        // Admin sees all - no extra filter
        break
      default:
        // Unknown role - restrict to own data
        query = query.eq('user_id', user.id)
    }

    // Optional status filter
    if (statusFilter) {
      query = query.eq('status', statusFilter)
    }

    // Pagination & ordering
    const from = (page - 1) * limit
    const to = from + limit - 1
    query = query.order('created_at', { ascending: false }).range(from, to)

    const { data, error, count } = await query

    if (error) {
      console.error('[GET /api/projects]', error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch projects.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        projects: data ?? [],
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/projects] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// PUT /api/projects
// ---------------------------------------------------------------------------

/**
 * Updates a project's current step and/or status.
 *
 * Authorization:
 *   - Only the project owner, the assigned accountant, or an admin can update.
 *
 * Step progression rules:
 *   - `target_step` must be exactly `current_step + 1` (sequential, no skipping).
 *   - When a step maps to a specific status (e.g., step 7 -> human_approval),
 *     the status is automatically set.
 *   - The project cannot advance past step 14.
 *
 * Required: `project_id` and at least one of `target_step` or `status`.
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response with the updated project.
 */
export async function PUT(request: NextRequest): Promise<NextResponse<ApiResponse>> {
  try {
    const supabase = await createClient()
    const { user, role } = await getAuthenticatedUser(supabase)

    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Authentication required.' },
        { status: 401 },
      )
    }

    // Parse and validate body
    let body: unknown
    try {
      body = await request.json()
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON body.' },
        { status: 400 },
      )
    }

    const validationError = validateUpdateBody(body)
    if (validationError) {
      return NextResponse.json(
        { success: false, error: validationError },
        { status: 400 },
      )
    }

    const { project_id, target_step, status: newStatus } = body as UpdateProjectBody

    // 1. Fetch current project (aligned with projects table columns)
    const { data: project, error: fetchError } = await supabase
      .from('projects')
      .select('project_id, user_id, accountant_id, status, current_step')
      .eq('project_id', project_id)
      .single()

    if (fetchError || !project) {
      return NextResponse.json(
        { success: false, error: 'Project not found.' },
        { status: 404 },
      )
    }

    // 2. Authorization check: owner, assigned accountant, or admin
    const isOwner = project.user_id === user.id
    const isAssignedAccountant = project.accountant_id === user.id
    const isAdmin = role === 'admin'

    if (!isOwner && !isAssignedAccountant && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'You do not have permission to update this project.' },
        { status: 403 },
      )
    }

    // 3. Cannot modify archived or completed projects (unless admin)
    if (
      (project.status === 'archived' || project.status === 'completed') &&
      !isAdmin
    ) {
      return NextResponse.json(
        {
          success: false,
          error: `Cannot update a project that is '${project.status}'.`,
        },
        { status: 400 },
      )
    }

    // 4. Build update payload
    const updatePayload: Record<string, unknown> = {
      updated_at: new Date().toISOString(),
    }

    // Step advancement logic
    if (target_step !== undefined) {
      const currentStep = project.current_step as number

      // Must be exactly current_step + 1 (sequential, no skipping)
      if (target_step !== currentStep + 1) {
        return NextResponse.json(
          {
            success: false,
            error: `Step must advance sequentially. Current step is ${currentStep}, target must be ${currentStep + 1}.`,
          },
          { status: 400 },
        )
      }

      // Cannot go beyond MAX_STEP
      if (target_step > MAX_STEP) {
        return NextResponse.json(
          { success: false, error: `Cannot advance beyond step ${MAX_STEP}.` },
          { status: 400 },
        )
      }

      updatePayload.current_step = target_step

      // Auto-set status based on step if applicable
      if (STEP_STATUS_MAP[target_step]) {
        updatePayload.status = STEP_STATUS_MAP[target_step]
      } else if (!newStatus) {
        // Default to in_progress if no explicit status and no auto-mapping
        updatePayload.status = 'in_progress'
      }
    }

    // Explicit status override (only if not already set by step logic)
    if (newStatus !== undefined && !updatePayload.status) {
      updatePayload.status = newStatus
    }

    // 5. Persist (aligned with projects table columns)
    const { data: updated, error: updateError } = await supabase
      .from('projects')
      .update(updatePayload)
      .eq('project_id', project_id)
      .select(
        'project_id, company_name_kr, status, current_step, accountant_id, updated_at',
      )
      .single()

    if (updateError) {
      console.error('[PUT /api/projects]', updateError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to update project.' },
        { status: 500 },
      )
    }

    return NextResponse.json({ success: true, data: updated })
  } catch (err) {
    console.error('[PUT /api/projects] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
