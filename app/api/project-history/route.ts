/**
 * @task S2BA2
 * @description Completed Project History Management API
 *
 * Endpoints:
 *   GET  /api/project-history  - Query completed project history (year filter)
 *   POST /api/project-history  - Move a completed project to history (archive)
 *
 * Schema alignment: schema-v4-final.sql (project_history, projects tables)
 */

import { NextRequest, NextResponse } from 'next/server'
import type { User } from '@supabase/supabase-js'
import { createClient } from '@/lib/supabase/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type UserRole = 'customer' | 'accountant' | 'admin'

interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

/** Body shape for POST (archive a project). */
interface ArchiveProjectBody {
  project_id: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** The final step that signifies a project is truly completed. */
const COMPLETION_STEP = 14

// ---------------------------------------------------------------------------
// Auth helper
// ---------------------------------------------------------------------------

async function getAuthenticatedUser(
  supabase: Awaited<ReturnType<typeof createClient>>,
): Promise<{ user: User; role: UserRole } | { user: null; role: null }> {
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
// GET /api/project-history
// ---------------------------------------------------------------------------

/**
 * Queries the completed project history.
 *
 * Access control:
 *   - **Customer**: sees only their own archived projects.
 *   - **Accountant**: sees projects they were assigned to.
 *   - **Admin**: sees all archived projects.
 *
 * Query params:
 *   - `year`  - Filter by year of completed_at (e.g. 2025).
 *   - `page`  - Page number (default 1).
 *   - `limit` - Items per page (default 20, max 100).
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response with paginated project history.
 */
export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse>> {
  try {
    const supabase = await createClient()
    const authResult = await getAuthenticatedUser(supabase)

    if (!authResult.user) {
      return NextResponse.json(
        { success: false, error: 'Authentication required.' },
        { status: 401 },
      )
    }

    const { user, role } = authResult

    const searchParams = request.nextUrl.searchParams
    const { page, limit } = parsePagination(searchParams)
    const yearParam = searchParams.get('year')

    // Validate year if provided
    let year: number | null = null
    if (yearParam) {
      year = parseInt(yearParam, 10)
      if (isNaN(year) || year < 2000 || year > 2100) {
        return NextResponse.json(
          { success: false, error: 'year must be a valid integer between 2000 and 2100.' },
          { status: 400 },
        )
      }
    }

    // Build query against project_history table (aligned with schema-v4-final.sql)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- Supabase query builder chaining narrows the type when conditionally branching; cast to any to preserve re-assignability across switch branches
    let query: any = supabase
      .from('project_history')
      .select(
        `history_id,
         project_id,
         request_id,
         user_id,
         company_name_kr,
         company_name_en,
         industry,
         valuation_purpose,
         completed_methods,
         total_paid,
         final_values,
         completed_at,
         accountant_id,
         accountant:users!project_history_accountant_id_fkey (
           user_id,
           email
         ),
         created_at`,
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
        // Admin sees all
        break
      default:
        query = query.eq('user_id', user.id)
    }

    // Year filter (based on completed_at year)
    if (year !== null) {
      const yearStart = `${year}-01-01T00:00:00.000Z`
      const yearEnd = `${year + 1}-01-01T00:00:00.000Z`
      query = query.gte('completed_at', yearStart).lt('completed_at', yearEnd)
    }

    // Pagination & ordering
    const from = (page - 1) * limit
    const to = from + limit - 1
    query = query.order('completed_at', { ascending: false }).range(from, to)

    const { data, error, count } = await query

    if (error) {
      console.error('[GET /api/project-history]', error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch project history.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        history: data ?? [],
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/project-history] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// POST /api/project-history
// ---------------------------------------------------------------------------

/**
 * Moves a completed project to the project history.
 *
 * Only admins or the assigned accountant can archive a project.
 *
 * Preconditions:
 *   - Project must be at step 14 (completion step) with status 'completed'.
 *   - Project must not already be archived.
 *
 * Process (transactional pattern):
 *   1. Copy relevant project data to the `project_history` table.
 *   2. Update the original project's status to 'archived'.
 *   3. If step 2 fails, rollback step 1 (delete the history entry).
 *
 * Required: `project_id`.
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response confirming the archive operation.
 */
export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse>> {
  try {
    const supabase = await createClient()
    const authResult = await getAuthenticatedUser(supabase)

    if (!authResult.user) {
      return NextResponse.json(
        { success: false, error: 'Authentication required.' },
        { status: 401 },
      )
    }

    const { user, role } = authResult

    // Parse body
    let body: unknown
    try {
      body = await request.json()
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON body.' },
        { status: 400 },
      )
    }

    if (!body || typeof body !== 'object') {
      return NextResponse.json(
        { success: false, error: 'Request body is required.' },
        { status: 400 },
      )
    }

    const { project_id } = body as ArchiveProjectBody

    if (!project_id || typeof project_id !== 'string') {
      return NextResponse.json(
        { success: false, error: 'project_id is required.' },
        { status: 400 },
      )
    }

    // 1. Fetch the project (aligned with projects table columns)
    const { data: project, error: fetchError } = await supabase
      .from('projects')
      .select(
        `project_id,
         request_id,
         user_id,
         company_name_kr,
         company_name_en,
         business_registration_number,
         representative_name,
         industry,
         company_website,
         address,
         phone,
         fax,
         valuation_purpose,
         requested_methods,
         agreed_price,
         deposit_amount,
         balance_paid_at,
         status,
         current_step,
         accountant_id,
         created_at,
         updated_at`,
      )
      .eq('project_id', project_id)
      .single()

    if (fetchError || !project) {
      return NextResponse.json(
        { success: false, error: 'Project not found.' },
        { status: 404 },
      )
    }

    // 2. Authorization: admin or assigned accountant
    const isAdmin = role === 'admin'
    const isAssignedAccountant = project.accountant_id === user.id

    if (!isAdmin && !isAssignedAccountant) {
      return NextResponse.json(
        { success: false, error: 'Only admins or the assigned accountant can archive a project.' },
        { status: 403 },
      )
    }

    // 3. Verify project is completed at step 14
    if (project.current_step !== COMPLETION_STEP) {
      return NextResponse.json(
        {
          success: false,
          error: `Project must be at step ${COMPLETION_STEP} to be archived. Current step: ${project.current_step}.`,
        },
        { status: 400 },
      )
    }

    if (project.status === 'archived') {
      return NextResponse.json(
        { success: false, error: 'Project is already archived.' },
        { status: 400 },
      )
    }

    if (project.status !== 'completed') {
      return NextResponse.json(
        {
          success: false,
          error: `Project status must be 'completed' to archive. Current status: '${project.status}'.`,
        },
        { status: 400 },
      )
    }

    // -----------------------------------------------------------------------
    // Transaction pattern: insert history -> update project -> rollback on failure
    // -----------------------------------------------------------------------

    const now = new Date().toISOString()

    // Calculate total_paid from project payment fields
    const totalPaid = (project.agreed_price ?? 0)

    // Step A: Insert into project_history (aligned with project_history table)
    const { data: historyEntry, error: historyError } = await supabase
      .from('project_history')
      .insert({
        project_id: project.project_id,
        request_id: project.request_id,
        user_id: project.user_id,
        accountant_id: project.accountant_id ?? null,
        company_name_kr: project.company_name_kr,
        company_name_en: project.company_name_en ?? null,
        business_registration_number: project.business_registration_number ?? null,
        representative_name: project.representative_name ?? null,
        industry: project.industry ?? null,
        company_website: project.company_website ?? null,
        address: project.address ?? null,
        phone: project.phone ?? null,
        fax: project.fax ?? null,
        valuation_purpose: project.valuation_purpose,
        completed_methods: project.requested_methods,
        total_paid: totalPaid,
        final_values: null,
        completed_at: project.updated_at,
        created_at: now,
      })
      .select('history_id, project_id, completed_at')
      .single()

    if (historyError || !historyEntry) {
      console.error('[POST /api/project-history] insert history error:', historyError?.message)
      return NextResponse.json(
        { success: false, error: 'Failed to create project history entry.' },
        { status: 500 },
      )
    }

    // Step B: Update original project status to 'archived'
    const { error: archiveError } = await supabase
      .from('projects')
      .update({
        status: 'archived',
        updated_at: now,
      })
      .eq('project_id', project_id)

    if (archiveError) {
      // Rollback: delete the history entry we just created
      console.error(
        '[POST /api/project-history] archive update error, rolling back history entry:',
        archiveError.message,
      )
      await supabase.from('project_history').delete().eq('history_id', historyEntry.history_id)

      return NextResponse.json(
        { success: false, error: 'Failed to archive project. Transaction rolled back.' },
        { status: 500 },
      )
    }

    return NextResponse.json(
      {
        success: true,
        data: {
          history_entry: historyEntry,
          project: {
            project_id,
            status: 'archived',
          },
          message: 'Project successfully archived to history.',
        },
      },
      { status: 201 },
    )
  } catch (err) {
    console.error('[POST /api/project-history] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
