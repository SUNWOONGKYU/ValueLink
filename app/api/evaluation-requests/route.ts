/**
 * @task S2BA2
 * @description Evaluation Request CRUD + Approve/Reject API
 *
 * Endpoints:
 *   GET  /api/evaluation-requests  - List evaluation requests (role-based)
 *   POST /api/evaluation-requests  - Create new evaluation request (customer)
 *   PUT  /api/evaluation-requests  - Approve or reject a request (admin)
 *
 * Schema alignment: schema-v4-final.sql (evaluation_requests, projects tables)
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type EvaluationRequestStatus = 'pending' | 'approved' | 'rejected'
type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
type UserRole = 'customer' | 'accountant' | 'admin'

interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

/** Shape of the body for POST (create request). Aligned with evaluation_requests table. */
interface CreateEvaluationBody {
  company_name_kr: string
  company_name_en?: string
  business_registration_number?: string
  representative_name?: string
  industry?: string
  valuation_purpose: string
  requested_methods: ValuationMethod[]
  target_date?: string
  requirements?: string
  budget_min?: number
  budget_max?: number
}

/** Shape of the body for PUT (approve / reject). */
interface ActionEvaluationBody {
  request_id: string
  action: 'approve' | 'reject'
  admin_comment?: string
  accountant_id?: string
}

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

const VALID_METHODS: readonly ValuationMethod[] = [
  'dcf',
  'relative',
  'asset',
  'intrinsic',
  'tax',
] as const

const VALID_PURPOSES = [
  'ma',
  'ipo',
  'investment',
  'tax',
  'litigation',
  'internal',
  'other',
] as const

/**
 * Validates the create-request payload and returns a descriptive error string
 * when the payload is invalid, or `null` when everything looks good.
 */
function validateCreateBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return 'Request body is required.'

  const b = body as Record<string, unknown>

  if (!b.company_name_kr || typeof b.company_name_kr !== 'string' || b.company_name_kr.trim().length === 0) {
    return 'company_name_kr is required and must be a non-empty string.'
  }
  if (!b.valuation_purpose || typeof b.valuation_purpose !== 'string' || b.valuation_purpose.trim().length === 0) {
    return 'valuation_purpose is required and must be a non-empty string.'
  }
  if (!Array.isArray(b.requested_methods) || b.requested_methods.length === 0) {
    return 'requested_methods must be a non-empty array of valuation methods.'
  }
  for (const method of b.requested_methods) {
    if (!VALID_METHODS.includes(method as ValuationMethod)) {
      return `Each requested_method must be one of: ${VALID_METHODS.join(', ')}.`
    }
  }

  return null
}

/**
 * Validates the approve/reject payload.
 */
function validateActionBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return 'Request body is required.'

  const b = body as Record<string, unknown>

  if (!b.request_id || typeof b.request_id !== 'string') {
    return 'request_id is required.'
  }
  if (b.action !== 'approve' && b.action !== 'reject') {
    return "action must be 'approve' or 'reject'."
  }
  if (b.action === 'reject' && (!b.admin_comment || typeof b.admin_comment !== 'string')) {
    return 'admin_comment is required when action is reject.'
  }

  return null
}

// ---------------------------------------------------------------------------
// Auth helper
// ---------------------------------------------------------------------------

/**
 * Retrieves the authenticated user and their role from Supabase.
 * Returns `null` values when the user is not authenticated.
 */
async function getAuthenticatedUser(supabase: Awaited<ReturnType<typeof createClient>>) {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser()

  if (error || !user) {
    return { user: null, role: null }
  }

  // Fetch role from the users table (PK is user_id, which refs auth.users.id)
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
// Project ID generator
// ---------------------------------------------------------------------------

/**
 * Generates a unique project ID in the format VL-YYYYMMDD-XXXX.
 */
function generateProjectId(): string {
  const now = new Date()
  const datePart = now.toISOString().slice(0, 10).replace(/-/g, '')
  const randomPart = Math.random().toString(36).substring(2, 6).toUpperCase()
  return `VL-${datePart}-${randomPart}`
}

// ---------------------------------------------------------------------------
// GET /api/evaluation-requests
// ---------------------------------------------------------------------------

/**
 * Lists evaluation requests with role-based filtering.
 *
 * - **Customer**: sees only their own requests.
 * - **Admin**: sees all requests, with optional `status` and date-range filters.
 *
 * Query params:
 *   - `status`     - Filter by request status (pending | approved | rejected).
 *   - `page`       - Page number (default 1).
 *   - `limit`      - Items per page (default 20, max 100).
 *   - `from_date`  - ISO date string lower bound for created_at (admin only).
 *   - `to_date`    - ISO date string upper bound for created_at (admin only).
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response with the list of evaluation requests.
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
    const statusFilter = searchParams.get('status') as EvaluationRequestStatus | null
    const fromDate = searchParams.get('from_date')
    const toDate = searchParams.get('to_date')

    // Validate status filter if provided
    if (statusFilter && !['pending', 'approved', 'rejected'].includes(statusFilter)) {
      return NextResponse.json(
        { success: false, error: "Invalid status filter. Must be 'pending', 'approved', or 'rejected'." },
        { status: 400 },
      )
    }

    // Build query - select only needed fields (aligned with schema-v4-final.sql)
    let query = supabase
      .from('evaluation_requests')
      .select(
        'request_id, user_id, company_name_kr, company_name_en, industry, valuation_purpose, requested_methods, target_date, requirements, status, admin_comment, reviewed_at, created_at, updated_at',
        { count: 'exact' },
      )

    // Role-based filtering
    if (role !== 'admin') {
      // Customer & accountant only see their own
      query = query.eq('user_id', user.id)
    }

    // Optional filters
    if (statusFilter) {
      query = query.eq('status', statusFilter)
    }
    if (fromDate && role === 'admin') {
      query = query.gte('created_at', fromDate)
    }
    if (toDate && role === 'admin') {
      query = query.lte('created_at', toDate)
    }

    // Pagination & ordering
    const from = (page - 1) * limit
    const to = from + limit - 1
    query = query.order('created_at', { ascending: false }).range(from, to)

    const { data, error, count } = await query

    if (error) {
      console.error('[GET /api/evaluation-requests]', error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch evaluation requests.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        requests: data ?? [],
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/evaluation-requests] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// POST /api/evaluation-requests
// ---------------------------------------------------------------------------

/**
 * Creates a new evaluation request.
 *
 * Only authenticated customers can create requests.
 *
 * Required fields: `company_name_kr`, `valuation_purpose`, `requested_methods`.
 * Optional: `company_name_en`, `business_registration_number`, `representative_name`,
 *           `industry`, `target_date`, `requirements`, `budget_min`, `budget_max`.
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response with the newly created evaluation request.
 */
export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse>> {
  try {
    const supabase = await createClient()
    const { user, role } = await getAuthenticatedUser(supabase)

    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Authentication required.' },
        { status: 401 },
      )
    }

    if (role !== 'customer') {
      return NextResponse.json(
        { success: false, error: 'Only customers can create evaluation requests.' },
        { status: 403 },
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

    const validationError = validateCreateBody(body)
    if (validationError) {
      return NextResponse.json(
        { success: false, error: validationError },
        { status: 400 },
      )
    }

    const {
      company_name_kr,
      company_name_en,
      business_registration_number,
      representative_name,
      industry,
      valuation_purpose,
      requested_methods,
      target_date,
      requirements,
      budget_min,
      budget_max,
    } = body as CreateEvaluationBody

    // Insert new evaluation request (aligned with evaluation_requests table)
    const { data, error } = await supabase
      .from('evaluation_requests')
      .insert({
        user_id: user.id,
        company_name_kr: company_name_kr.trim(),
        company_name_en: company_name_en?.trim() ?? null,
        business_registration_number: business_registration_number?.trim() ?? null,
        representative_name: representative_name?.trim() ?? null,
        industry: industry?.trim() ?? null,
        valuation_purpose: valuation_purpose.trim(),
        requested_methods,
        target_date: target_date ?? null,
        requirements: requirements?.trim() ?? null,
        budget_min: budget_min ?? null,
        budget_max: budget_max ?? null,
        status: 'pending' as EvaluationRequestStatus,
      })
      .select(
        'request_id, user_id, company_name_kr, valuation_purpose, requested_methods, status, requirements, created_at',
      )
      .single()

    if (error) {
      console.error('[POST /api/evaluation-requests]', error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to create evaluation request.' },
        { status: 500 },
      )
    }

    return NextResponse.json(
      { success: true, data },
      { status: 201 },
    )
  } catch (err) {
    console.error('[POST /api/evaluation-requests] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// PUT /api/evaluation-requests
// ---------------------------------------------------------------------------

/**
 * Approves or rejects an evaluation request (admin only).
 *
 * - **approve**: creates a corresponding project in the `projects` table, then
 *   updates the request status to `approved`. Uses a manual rollback pattern
 *   to ensure both operations succeed or neither does.
 * - **reject**: updates the request status to `rejected` with a mandatory
 *   `admin_comment`.
 *
 * Required fields: `request_id`, `action`.
 * Conditional: `admin_comment` (required for reject), `accountant_id` (optional for approve).
 *
 * @param request - Incoming Next.js request object.
 * @returns JSON response with the outcome of the action.
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

    if (role !== 'admin') {
      return NextResponse.json(
        { success: false, error: 'Only admins can approve or reject requests.' },
        { status: 403 },
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

    const validationError = validateActionBody(body)
    if (validationError) {
      return NextResponse.json(
        { success: false, error: validationError },
        { status: 400 },
      )
    }

    const { request_id, action, admin_comment, accountant_id } =
      body as ActionEvaluationBody

    // 1. Fetch the evaluation request (aligned with evaluation_requests table)
    const { data: evalRequest, error: fetchError } = await supabase
      .from('evaluation_requests')
      .select('request_id, user_id, company_name_kr, company_name_en, business_registration_number, representative_name, industry, revenue, employees, founded_date, company_website, address, phone, fax, valuation_purpose, requested_methods, target_date, requirements, budget_min, budget_max, status')
      .eq('request_id', request_id)
      .single()

    if (fetchError || !evalRequest) {
      return NextResponse.json(
        { success: false, error: 'Evaluation request not found.' },
        { status: 404 },
      )
    }

    if (evalRequest.status !== 'pending') {
      return NextResponse.json(
        {
          success: false,
          error: `Cannot ${action} a request that is already '${evalRequest.status}'.`,
        },
        { status: 400 },
      )
    }

    const now = new Date().toISOString()

    // -----------------------------------------------------------------------
    // Action: REJECT
    // -----------------------------------------------------------------------
    if (action === 'reject') {
      const { data: rejected, error: rejectError } = await supabase
        .from('evaluation_requests')
        .update({
          status: 'rejected' as EvaluationRequestStatus,
          admin_id: user.id,
          admin_comment: admin_comment!,
          reviewed_at: now,
          updated_at: now,
        })
        .eq('request_id', request_id)
        .select('request_id, status, admin_comment, reviewed_at, updated_at')
        .single()

      if (rejectError) {
        console.error('[PUT /api/evaluation-requests] reject error:', rejectError.message)
        return NextResponse.json(
          { success: false, error: 'Failed to reject the evaluation request.' },
          { status: 500 },
        )
      }

      return NextResponse.json({ success: true, data: rejected })
    }

    // -----------------------------------------------------------------------
    // Action: APPROVE  (with transactional rollback pattern)
    // -----------------------------------------------------------------------

    // Step A: Create a project from the evaluation request data
    // project_id is VARCHAR(50) in schema, so we generate a human-readable ID
    const projectId = generateProjectId()

    const { data: newProject, error: projectError } = await supabase
      .from('projects')
      .insert({
        project_id: projectId,
        request_id: evalRequest.request_id,
        user_id: evalRequest.user_id,
        accountant_id: accountant_id ?? null,
        company_name_kr: evalRequest.company_name_kr,
        company_name_en: evalRequest.company_name_en ?? null,
        business_registration_number: evalRequest.business_registration_number ?? null,
        representative_name: evalRequest.representative_name ?? null,
        industry: evalRequest.industry ?? null,
        revenue: evalRequest.revenue ?? null,
        employees: evalRequest.employees ?? null,
        founded_date: evalRequest.founded_date ?? null,
        company_website: evalRequest.company_website ?? null,
        address: evalRequest.address ?? null,
        phone: evalRequest.phone ?? null,
        fax: evalRequest.fax ?? null,
        valuation_purpose: evalRequest.valuation_purpose,
        requested_methods: evalRequest.requested_methods,
        target_date: evalRequest.target_date ?? null,
        requirements: evalRequest.requirements ?? null,
        budget_min: evalRequest.budget_min ?? null,
        budget_max: evalRequest.budget_max ?? null,
        status: 'in_progress',
        current_step: 1,
        created_at: now,
        updated_at: now,
      })
      .select('project_id, request_id, company_name_kr, status, current_step, created_at')
      .single()

    if (projectError || !newProject) {
      console.error('[PUT /api/evaluation-requests] project creation error:', projectError?.message)
      return NextResponse.json(
        { success: false, error: 'Failed to create project from evaluation request.' },
        { status: 500 },
      )
    }

    // Step B: Update evaluation request status to approved
    const { error: approveError } = await supabase
      .from('evaluation_requests')
      .update({
        status: 'approved' as EvaluationRequestStatus,
        admin_id: user.id,
        reviewed_at: now,
        updated_at: now,
      })
      .eq('request_id', request_id)

    if (approveError) {
      // Rollback: delete the project we just created
      console.error(
        '[PUT /api/evaluation-requests] approve update error, rolling back project:',
        approveError.message,
      )
      await supabase.from('projects').delete().eq('project_id', newProject.project_id)

      return NextResponse.json(
        { success: false, error: 'Failed to update request status. Transaction rolled back.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        evaluation_request: { request_id, status: 'approved' },
        project: newProject,
      },
    })
  } catch (err) {
    console.error('[PUT /api/evaluation-requests] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
