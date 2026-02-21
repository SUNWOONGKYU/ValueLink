/**
 * @task S2BA3
 * @description Revisions API - Revision request management for drafts
 *
 * Endpoints:
 *   GET  /api/revisions  - List revision requests for a draft+method
 *   POST /api/revisions  - Create a new revision request
 *   PUT  /api/revisions  - Update revision status (in_progress / completed)
 *
 * Schema alignment: schema-v4-final.sql
 *   Tables: dcf_revisions, relative_revisions, asset_revisions,
 *           intrinsic_revisions, tax_revisions
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
type UserRole = 'customer' | 'accountant' | 'admin'
type RevisionStatus = 'pending' | 'in_progress' | 'completed' | 'rejected'

interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

interface CreateRevisionBody {
  draft_id: string
  method: string
  revision_type: string
  section: string
  details: string
}

interface UpdateRevisionBody {
  revision_id: string
  method: string
  status: 'in_progress' | 'completed'
  assigned_to?: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const VALID_METHODS: readonly ValuationMethod[] = [
  'dcf',
  'relative',
  'asset',
  'intrinsic',
  'tax',
] as const

const VALID_UPDATE_STATUSES = ['in_progress', 'completed'] as const

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function validateMethod(method: string): method is ValuationMethod {
  return (VALID_METHODS as readonly string[]).includes(method)
}

function getRevisionsTable(method: ValuationMethod): string {
  return `${method}_revisions`
}

function getDraftsTable(method: ValuationMethod): string {
  return `${method}_drafts`
}

// ---------------------------------------------------------------------------
// Auth helper (same pattern as S2BA2)
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
// Pagination helper (same pattern as S2BA2)
// ---------------------------------------------------------------------------

interface PaginationParams {
  page: number
  limit: number
}

function parsePagination(searchParams: URLSearchParams): PaginationParams {
  const page = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10) || 1)
  const limit = Math.min(
    100,
    Math.max(1, parseInt(searchParams.get('limit') ?? '20', 10) || 20),
  )
  return { page, limit }
}

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

function validateCreateBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return 'Request body is required.'

  const b = body as Record<string, unknown>

  if (!b.draft_id || typeof b.draft_id !== 'string') {
    return 'draft_id is required.'
  }

  if (!b.method || typeof b.method !== 'string' || !validateMethod(b.method)) {
    return `method is required and must be one of: ${VALID_METHODS.join(', ')}.`
  }

  if (!b.revision_type || typeof b.revision_type !== 'string' || b.revision_type.trim().length === 0) {
    return 'revision_type is required and must be a non-empty string.'
  }

  if (!b.section || typeof b.section !== 'string' || b.section.trim().length === 0) {
    return 'section is required and must be a non-empty string.'
  }

  if (!b.details || typeof b.details !== 'string' || b.details.trim().length === 0) {
    return 'details is required and must be a non-empty string.'
  }

  return null
}

function validateUpdateBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return 'Request body is required.'

  const b = body as Record<string, unknown>

  if (!b.revision_id || typeof b.revision_id !== 'string') {
    return 'revision_id is required.'
  }

  if (!b.method || typeof b.method !== 'string' || !validateMethod(b.method)) {
    return `method is required and must be one of: ${VALID_METHODS.join(', ')}.`
  }

  if (
    !b.status ||
    typeof b.status !== 'string' ||
    !(VALID_UPDATE_STATUSES as readonly string[]).includes(b.status)
  ) {
    return `status is required and must be one of: ${VALID_UPDATE_STATUSES.join(', ')}.`
  }

  if (b.assigned_to !== undefined && typeof b.assigned_to !== 'string') {
    return 'assigned_to must be a string (UUID) if provided.'
  }

  return null
}

// ---------------------------------------------------------------------------
// GET /api/revisions
// ---------------------------------------------------------------------------

/**
 * Lists revision requests for a draft and valuation method.
 *
 * Query params:
 *   - draft_id (required) - The draft to list revisions for.
 *   - method   (required) - dcf|relative|asset|intrinsic|tax
 *   - page               - Page number (default 1)
 *   - limit              - Items per page (default 20, max 100)
 *
 * Auth: project participants (owner, assigned accountant, or admin).
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
    const draftId = searchParams.get('draft_id')
    const method = searchParams.get('method')

    if (!draftId) {
      return NextResponse.json(
        { success: false, error: 'draft_id query parameter is required.' },
        { status: 400 },
      )
    }

    if (!method || !validateMethod(method)) {
      return NextResponse.json(
        {
          success: false,
          error: `method query parameter is required and must be one of: ${VALID_METHODS.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    // Verify draft exists and get project_id for access check
    const draftsTable = getDraftsTable(method)
    const { data: draft, error: draftError } = await supabase
      .from(draftsTable)
      .select('draft_id, project_id')
      .eq('draft_id', draftId)
      .single()

    if (draftError || !draft) {
      return NextResponse.json(
        { success: false, error: 'Draft not found.' },
        { status: 404 },
      )
    }

    // Verify project access
    if (role !== 'admin') {
      const { data: project, error: projectError } = await supabase
        .from('projects')
        .select('project_id, user_id, accountant_id')
        .eq('project_id', draft.project_id)
        .single()

      if (projectError || !project) {
        return NextResponse.json(
          { success: false, error: 'Associated project not found.' },
          { status: 404 },
        )
      }

      const isOwner = project.user_id === user.id
      const isAssignedAccountant = project.accountant_id === user.id

      if (!isOwner && !isAssignedAccountant) {
        return NextResponse.json(
          { success: false, error: 'You do not have access to this project.' },
          { status: 403 },
        )
      }
    }

    const { page, limit } = parsePagination(searchParams)
    const from = (page - 1) * limit
    const to = from + limit - 1

    const revisionsTable = getRevisionsTable(method)

    const { data, error, count } = await supabase
      .from(revisionsTable)
      .select(
        'revision_id, draft_id, revision_type, section, details, status, requested_by, assigned_to, requested_at, completed_at, created_at, updated_at',
        { count: 'exact' },
      )
      .eq('draft_id', draftId)
      .order('created_at', { ascending: false })
      .range(from, to)

    if (error) {
      console.error(`[GET /api/revisions] ${revisionsTable}:`, error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch revisions.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        revisions: data ?? [],
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/revisions] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// POST /api/revisions
// ---------------------------------------------------------------------------

/**
 * Creates a new revision request for a draft.
 *
 * Body:
 *   - draft_id      (string, required) - UUID of the draft
 *   - method        (string, required) - dcf|relative|asset|intrinsic|tax
 *   - revision_type (string, required) - Type of revision (e.g. "content", "calculation")
 *   - section       (string, required) - Section that needs revision
 *   - details       (string, required) - Description of what needs to be revised
 *
 * Sets requested_by to current user, status to 'pending'.
 *
 * Auth: project owner or admin.
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

    const validationError = validateCreateBody(body)
    if (validationError) {
      return NextResponse.json(
        { success: false, error: validationError },
        { status: 400 },
      )
    }

    const { draft_id, method, revision_type, section, details } = body as CreateRevisionBody
    const validatedMethod = method as ValuationMethod

    // Verify draft exists and get project_id for auth
    const draftsTable = getDraftsTable(validatedMethod)
    const { data: draft, error: draftError } = await supabase
      .from(draftsTable)
      .select('draft_id, project_id')
      .eq('draft_id', draft_id)
      .single()

    if (draftError || !draft) {
      return NextResponse.json(
        { success: false, error: 'Draft not found.' },
        { status: 404 },
      )
    }

    // Verify project access: only owner or admin can create revision requests
    const { data: project, error: projectError } = await supabase
      .from('projects')
      .select('project_id, user_id, accountant_id')
      .eq('project_id', draft.project_id)
      .single()

    if (projectError || !project) {
      return NextResponse.json(
        { success: false, error: 'Associated project not found.' },
        { status: 404 },
      )
    }

    const isOwner = project.user_id === user.id
    const isAdmin = role === 'admin'

    if (!isOwner && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'Only the project owner or admin can create revision requests.' },
        { status: 403 },
      )
    }

    const revisionsTable = getRevisionsTable(validatedMethod)
    const now = new Date().toISOString()

    const { data: revision, error: insertError } = await supabase
      .from(revisionsTable)
      .insert({
        draft_id,
        revision_type: revision_type.trim(),
        section: section.trim(),
        details: details.trim(),
        status: 'pending' as RevisionStatus,
        requested_by: user.id,
        requested_at: now,
        created_at: now,
        updated_at: now,
      })
      .select(
        'revision_id, draft_id, revision_type, section, details, status, requested_by, requested_at, created_at, updated_at',
      )
      .single()

    if (insertError) {
      console.error(`[POST /api/revisions] ${revisionsTable} insert error:`, insertError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to create revision request.' },
        { status: 500 },
      )
    }

    return NextResponse.json(
      { success: true, data: revision },
      { status: 201 },
    )
  } catch (err) {
    console.error('[POST /api/revisions] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// PUT /api/revisions
// ---------------------------------------------------------------------------

/**
 * Updates a revision request status.
 *
 * Body:
 *   - revision_id (string, required) - UUID of the revision
 *   - method      (string, required) - dcf|relative|asset|intrinsic|tax
 *   - status      (string, required) - 'in_progress' | 'completed'
 *   - assigned_to (string, optional) - UUID of the user assigned to this revision
 *
 * When status is 'completed', sets completed_at to current timestamp.
 *
 * Auth: assigned accountant or admin.
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

    const validationError = validateUpdateBody(body)
    if (validationError) {
      return NextResponse.json(
        { success: false, error: validationError },
        { status: 400 },
      )
    }

    const { revision_id, method, status: newStatus, assigned_to } = body as UpdateRevisionBody
    const validatedMethod = method as ValuationMethod
    const revisionsTable = getRevisionsTable(validatedMethod)

    // Fetch the revision to verify existence and get draft_id
    const { data: revision, error: fetchError } = await supabase
      .from(revisionsTable)
      .select('revision_id, draft_id, status')
      .eq('revision_id', revision_id)
      .single()

    if (fetchError || !revision) {
      return NextResponse.json(
        { success: false, error: 'Revision not found.' },
        { status: 404 },
      )
    }

    // Validate status transition
    const currentStatus = revision.status as RevisionStatus
    const validTransitions: Record<string, string[]> = {
      pending: ['in_progress'],
      in_progress: ['completed'],
    }

    if (!validTransitions[currentStatus]?.includes(newStatus)) {
      return NextResponse.json(
        {
          success: false,
          error: `Cannot transition from '${currentStatus}' to '${newStatus}'. Valid transitions: ${validTransitions[currentStatus]?.join(', ') ?? 'none'}.`,
        },
        { status: 400 },
      )
    }

    // Get draft -> project for auth check
    const draftsTable = getDraftsTable(validatedMethod)
    const { data: draft, error: draftError } = await supabase
      .from(draftsTable)
      .select('draft_id, project_id')
      .eq('draft_id', revision.draft_id)
      .single()

    if (draftError || !draft) {
      return NextResponse.json(
        { success: false, error: 'Associated draft not found.' },
        { status: 404 },
      )
    }

    const { data: project, error: projectError } = await supabase
      .from('projects')
      .select('project_id, user_id, accountant_id')
      .eq('project_id', draft.project_id)
      .single()

    if (projectError || !project) {
      return NextResponse.json(
        { success: false, error: 'Associated project not found.' },
        { status: 404 },
      )
    }

    // Auth: assigned accountant or admin
    const isAssignedAccountant = project.accountant_id === user.id
    const isAdmin = role === 'admin'

    if (!isAssignedAccountant && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'Only the assigned accountant or admin can update revision status.' },
        { status: 403 },
      )
    }

    // Build update payload
    const now = new Date().toISOString()
    const updatePayload: Record<string, unknown> = {
      status: newStatus,
      updated_at: now,
    }

    if (assigned_to) {
      updatePayload.assigned_to = assigned_to
    }

    if (newStatus === 'completed') {
      updatePayload.completed_at = now
    }

    const { data: updated, error: updateError } = await supabase
      .from(revisionsTable)
      .update(updatePayload)
      .eq('revision_id', revision_id)
      .select(
        'revision_id, draft_id, revision_type, section, details, status, requested_by, assigned_to, requested_at, completed_at, created_at, updated_at',
      )
      .single()

    if (updateError) {
      console.error(`[PUT /api/revisions] ${revisionsTable} update error:`, updateError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to update revision status.' },
        { status: 500 },
      )
    }

    return NextResponse.json({ success: true, data: updated })
  } catch (err) {
    console.error('[PUT /api/revisions] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
