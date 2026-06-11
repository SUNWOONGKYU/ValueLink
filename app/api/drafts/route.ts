/**
 * @task S2BA3
 * @description Drafts API - Draft management with versioning and section-based content
 *
 * Endpoints:
 *   GET  /api/drafts  - List drafts for a project+method (ordered by version DESC)
 *   POST /api/drafts  - Create a new draft version (auto-increment version)
 *   PUT  /api/drafts  - Update draft status or section content
 *
 * Schema alignment: schema-v4-final.sql
 *   Tables: dcf_drafts, relative_drafts, asset_drafts,
 *           intrinsic_drafts, tax_drafts
 *   Columns: draft_id, project_id, version, status,
 *            section_1_summary..section_9_appendix (9 TEXT),
 *            section_1_completed..section_9_completed (9 BOOLEAN),
 *            submitted_at, created_by, created_at, updated_at
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import type { Database } from '@/types/database.types'

type DraftUpdate = Database['public']['Tables']['dcf_drafts']['Update']

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
type UserRole = 'customer' | 'accountant' | 'admin'
type DraftStatus = 'draft' | 'in_progress' | 'submitted' | 'confirmed' | 'revision_requested' | 'finalized'

interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

/** Section content fields matching schema columns. */
interface SectionFields {
  section_1_summary?: string
  section_2_overview?: string
  section_3_company?: string
  section_4_financial?: string
  section_5_methodology?: string
  section_6_results?: string
  section_7_sensitivity?: string
  section_8_conclusion?: string
  section_9_appendix?: string
  section_1_completed?: boolean
  section_2_completed?: boolean
  section_3_completed?: boolean
  section_4_completed?: boolean
  section_5_completed?: boolean
  section_6_completed?: boolean
  section_7_completed?: boolean
  section_8_completed?: boolean
  section_9_completed?: boolean
}

interface CreateDraftBody extends SectionFields {
  project_id: string
  method: string
}

interface UpdateDraftBody extends SectionFields {
  draft_id: string
  method: string
  status?: DraftStatus
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

const VALID_STATUSES: readonly DraftStatus[] = [
  'draft',
  'in_progress',
  'submitted',
  'confirmed',
  'revision_requested',
  'finalized',
] as const

/** The full SELECT column list matching schema. */
const DRAFT_SELECT_COLUMNS = [
  'draft_id', 'project_id', 'version', 'status',
  'section_1_summary', 'section_2_overview', 'section_3_company',
  'section_4_financial', 'section_5_methodology', 'section_6_results',
  'section_7_sensitivity', 'section_8_conclusion', 'section_9_appendix',
  'section_1_completed', 'section_2_completed', 'section_3_completed',
  'section_4_completed', 'section_5_completed', 'section_6_completed',
  'section_7_completed', 'section_8_completed', 'section_9_completed',
  'submitted_at', 'created_by', 'created_at', 'updated_at',
].join(', ')

/** Section content column names for picking from request body. */
const SECTION_TEXT_KEYS = [
  'section_1_summary', 'section_2_overview', 'section_3_company',
  'section_4_financial', 'section_5_methodology', 'section_6_results',
  'section_7_sensitivity', 'section_8_conclusion', 'section_9_appendix',
] as const

const SECTION_BOOL_KEYS = [
  'section_1_completed', 'section_2_completed', 'section_3_completed',
  'section_4_completed', 'section_5_completed', 'section_6_completed',
  'section_7_completed', 'section_8_completed', 'section_9_completed',
] as const

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function validateMethod(method: string): method is ValuationMethod {
  return (VALID_METHODS as readonly string[]).includes(method)
}

// ---------------------------------------------------------------------------
// Per-method draft row shape (all five *_drafts tables share identical columns)
// Used for narrow casts on .from() calls.
// ---------------------------------------------------------------------------
type DraftsTableName =
  | 'dcf_drafts'
  | 'relative_drafts'
  | 'asset_drafts'
  | 'intrinsic_drafts'
  | 'tax_drafts'

function getDraftsTable(method: ValuationMethod): DraftsTableName {
  return `${method}_drafts` as DraftsTableName
}

/**
 * Extract section fields from the request body.
 * Only includes keys that are actually present in the body.
 */
function pickSectionFields(body: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {}

  for (const key of SECTION_TEXT_KEYS) {
    if (key in body && (typeof body[key] === 'string' || body[key] === null)) {
      result[key] = body[key]
    }
  }

  for (const key of SECTION_BOOL_KEYS) {
    if (key in body && typeof body[key] === 'boolean') {
      result[key] = body[key]
    }
  }

  return result
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
// Project access helper
// ---------------------------------------------------------------------------

async function verifyProjectAccess(
  supabase: Awaited<ReturnType<typeof createClient>>,
  projectId: string,
  userId: string,
  role: UserRole,
): Promise<{ project: Record<string, unknown> | null; error: string | null }> {
  const { data: project, error } = await supabase
    .from('projects')
    .select('project_id, user_id, accountant_id, requested_methods')
    .eq('project_id', projectId)
    .single()

  if (error || !project) {
    return { project: null, error: 'Project not found.' }
  }

  if (role === 'admin') {
    return { project, error: null }
  }

  const isOwner = project.user_id === userId
  const isAssignedAccountant = project.accountant_id === userId

  if (!isOwner && !isAssignedAccountant) {
    return { project: null, error: 'You do not have access to this project.' }
  }

  return { project, error: null }
}

// ---------------------------------------------------------------------------
// GET /api/drafts
// ---------------------------------------------------------------------------

/**
 * Lists drafts for a project and valuation method, ordered by version DESC.
 *
 * Query params:
 *   - project_id (required)
 *   - method     (required) - dcf|relative|asset|intrinsic|tax
 *   - page                  - Page number (default 1)
 *   - limit                 - Items per page (default 20, max 100)
 *
 * Auth: project owner, assigned accountant, or admin.
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
    const projectId = searchParams.get('project_id')
    const method = searchParams.get('method')

    if (!projectId) {
      return NextResponse.json(
        { success: false, error: 'project_id query parameter is required.' },
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

    // Verify project access
    const { error: accessError } = await verifyProjectAccess(
      supabase,
      projectId,
      user.id,
      role as UserRole,
    )
    if (accessError) {
      return NextResponse.json(
        { success: false, error: accessError },
        { status: 403 },
      )
    }

    const { page, limit } = parsePagination(searchParams)
    const from = (page - 1) * limit
    const to = from + limit - 1

    const table = getDraftsTable(method)

    // Cast to representative table: all five *_drafts tables share the same schema.
    const { data, error, count } = await supabase
      .from(table as 'dcf_drafts')
      .select(DRAFT_SELECT_COLUMNS, { count: 'exact' })
      .eq('project_id', projectId)
      .order('version', { ascending: false })
      .range(from, to)

    if (error) {
      console.error(`[GET /api/drafts] ${table}:`, error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch drafts.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        drafts: data ?? [],
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/drafts] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// POST /api/drafts
// ---------------------------------------------------------------------------

/**
 * Creates a new draft version for a project.
 *
 * Body:
 *   - project_id            (string, required)
 *   - method                (string, required) - dcf|relative|asset|intrinsic|tax
 *   - section_1_summary     (string, optional) - Section 1 content
 *   - section_2_overview    (string, optional) - Section 2 content
 *   - ...through section_9_appendix
 *   - section_1_completed   (boolean, optional) - Section 1 completion flag
 *   - ...through section_9_completed
 *
 * Version is auto-incremented: MAX(version) + 1 for the project.
 * status defaults to 'draft'.
 *
 * Auth: assigned accountant or admin.
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
    let body: Record<string, unknown>
    try {
      body = (await request.json()) as Record<string, unknown>
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON body.' },
        { status: 400 },
      )
    }

    // Validate required fields
    if (!body.project_id || typeof body.project_id !== 'string') {
      return NextResponse.json(
        { success: false, error: 'project_id is required.' },
        { status: 400 },
      )
    }

    if (!body.method || typeof body.method !== 'string' || !validateMethod(body.method)) {
      return NextResponse.json(
        {
          success: false,
          error: `method is required and must be one of: ${VALID_METHODS.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    const projectId = body.project_id as string
    const validatedMethod = body.method as ValuationMethod

    // Verify project access
    const { project, error: accessError } = await verifyProjectAccess(
      supabase,
      projectId,
      user.id,
      role as UserRole,
    )
    if (accessError || !project) {
      return NextResponse.json(
        { success: false, error: accessError ?? 'Project not found.' },
        { status: 403 },
      )
    }

    // Only assigned accountant or admin can create drafts
    const isAssignedAccountant = project.accountant_id === user.id
    const isAdmin = role === 'admin'
    if (!isAssignedAccountant && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'Only the assigned accountant or admin can create drafts.' },
        { status: 403 },
      )
    }

    const table = getDraftsTable(validatedMethod)

    // Auto-increment version: get max version for this project
    // Cast to representative table: all five *_drafts tables share the same schema.
    const { data: maxVersionRow } = await supabase
      .from(table as 'dcf_drafts')
      .select('version')
      .eq('project_id', projectId)
      .order('version', { ascending: false })
      .limit(1)
      .single()

    const nextVersion = (maxVersionRow?.version ?? 0) + 1
    const now = new Date().toISOString()

    // Pick section fields from body
    const sectionData = pickSectionFields(body)

    // Cast to representative table: all five *_drafts tables share the same schema.
    type DraftInsert = Database['public']['Tables']['dcf_drafts']['Insert']
    const { data: draft, error: insertError } = await supabase
      .from(table as 'dcf_drafts')
      .insert({
        project_id: projectId,
        version: nextVersion,
        status: 'draft' as DraftStatus,
        ...sectionData,
        created_by: user.id,
        created_at: now,
        updated_at: now,
      } as DraftInsert)
      .select(DRAFT_SELECT_COLUMNS)
      .single()

    if (insertError) {
      console.error(`[POST /api/drafts] ${table} insert error:`, insertError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to create draft.' },
        { status: 500 },
      )
    }

    return NextResponse.json(
      { success: true, data: draft },
      { status: 201 },
    )
  } catch (err) {
    console.error('[POST /api/drafts] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// PUT /api/drafts
// ---------------------------------------------------------------------------

/**
 * Updates a draft's status and/or section content.
 *
 * Body:
 *   - draft_id  (string, required)
 *   - method    (string, required) - dcf|relative|asset|intrinsic|tax
 *   - status    (string, optional) - New status: draft|in_progress|submitted|confirmed|revision_requested|finalized
 *   - section_* (optional)         - Any section content or completion fields to update
 *
 * When status changes to 'submitted', submitted_at is auto-set.
 *
 * Auth: assigned accountant can update content/submit; project owner or admin can confirm/request revision/finalize.
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
    let body: Record<string, unknown>
    try {
      body = (await request.json()) as Record<string, unknown>
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON body.' },
        { status: 400 },
      )
    }

    // Validate required fields
    if (!body.draft_id || typeof body.draft_id !== 'string') {
      return NextResponse.json(
        { success: false, error: 'draft_id is required.' },
        { status: 400 },
      )
    }

    if (!body.method || typeof body.method !== 'string' || !validateMethod(body.method)) {
      return NextResponse.json(
        {
          success: false,
          error: `method is required and must be one of: ${VALID_METHODS.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    // Validate status if provided
    if (
      body.status !== undefined &&
      (typeof body.status !== 'string' ||
        !(VALID_STATUSES as readonly string[]).includes(body.status))
    ) {
      return NextResponse.json(
        {
          success: false,
          error: `status must be one of: ${VALID_STATUSES.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    const draftId = body.draft_id as string
    const validatedMethod = body.method as ValuationMethod
    const newStatus = body.status as DraftStatus | undefined
    const table = getDraftsTable(validatedMethod)

    // Fetch the draft to verify it exists and get its project_id
    // Cast to representative table: all five *_drafts tables share the same schema.
    const { data: draft, error: fetchError } = await supabase
      .from(table as 'dcf_drafts')
      .select('draft_id, project_id, status')
      .eq('draft_id', draftId)
      .single()

    if (fetchError || !draft) {
      return NextResponse.json(
        { success: false, error: 'Draft not found.' },
        { status: 404 },
      )
    }

    // Verify project access and ownership
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

    // Auth check: accountant can edit content/submit, owner/admin can confirm/revise/finalize
    const isOwner = project.user_id === user.id
    const isAssignedAccountant = project.accountant_id === user.id
    const isAdmin = role === 'admin'

    if (!isOwner && !isAssignedAccountant && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'You do not have access to update this draft.' },
        { status: 403 },
      )
    }

    // Build update payload
    const now = new Date().toISOString()
    const updateData: Record<string, unknown> = {
      ...pickSectionFields(body),
      updated_at: now,
    }

    if (newStatus) {
      updateData.status = newStatus
      // Auto-set submitted_at when transitioning to 'submitted'
      if (newStatus === 'submitted') {
        updateData.submitted_at = now
      }
    }

    // Cast to representative table: all five *_drafts tables share the same schema.
    // updateData keys are a known subset of dcf_drafts Update columns (section_* + status + timestamps).
    const { data: updated, error: updateError } = await supabase
      .from(table as 'dcf_drafts')
      .update(updateData as DraftUpdate)
      .eq('draft_id', draftId)
      .select(DRAFT_SELECT_COLUMNS)
      .single()

    if (updateError) {
      console.error(`[PUT /api/drafts] ${table} update error:`, updateError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to update draft.' },
        { status: 500 },
      )
    }

    return NextResponse.json({ success: true, data: updated })
  } catch (err) {
    console.error('[PUT /api/drafts] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
