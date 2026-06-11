/**
 * @task S2BA3
 * @description Reports API - Final valuation report management
 *
 * Endpoints:
 *   GET  /api/reports  - List reports with signed download URLs
 *   POST /api/reports  - Create (issue) a final report record
 *
 * Schema alignment: schema-v4-final.sql
 *   Tables: dcf_reports, relative_reports, asset_reports,
 *           intrinsic_reports, tax_reports
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import type { Database } from '@/types/database.types'

type ReportsTableName =
  | 'dcf_reports'
  | 'relative_reports'
  | 'asset_reports'
  | 'intrinsic_reports'
  | 'tax_reports'

type DraftsTableName =
  | 'dcf_drafts'
  | 'relative_drafts'
  | 'asset_drafts'
  | 'intrinsic_drafts'
  | 'tax_drafts'

type ReportInsert = Database['public']['Tables']['dcf_reports']['Insert']

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ValuationMethod = 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
type UserRole = 'customer' | 'accountant' | 'admin'

interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

interface CreateReportBody {
  project_id: string
  method: string
  draft_id: string
  report_url: string
  file_size: number
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

/** Supabase Storage bucket for reports. */
const STORAGE_BUCKET = 'valuation-documents'

/** Signed URL expiry in seconds (1 hour). */
const SIGNED_URL_EXPIRY = 3600

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function validateMethod(method: string): method is ValuationMethod {
  return (VALID_METHODS as readonly string[]).includes(method)
}

function getReportsTable(method: ValuationMethod): ReportsTableName {
  return `${method}_reports` as ReportsTableName
}

function getDraftsTable(method: ValuationMethod): DraftsTableName {
  return `${method}_drafts` as DraftsTableName
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
// Validation helpers
// ---------------------------------------------------------------------------

function validateCreateBody(body: unknown): string | null {
  if (!body || typeof body !== 'object') return 'Request body is required.'

  const b = body as Record<string, unknown>

  if (!b.project_id || typeof b.project_id !== 'string') {
    return 'project_id is required.'
  }

  if (!b.method || typeof b.method !== 'string' || !validateMethod(b.method)) {
    return `method is required and must be one of: ${VALID_METHODS.join(', ')}.`
  }

  if (!b.draft_id || typeof b.draft_id !== 'string') {
    return 'draft_id is required.'
  }

  if (!b.report_url || typeof b.report_url !== 'string' || b.report_url.trim().length === 0) {
    return 'report_url is required and must be a non-empty string.'
  }

  if (b.file_size === undefined || typeof b.file_size !== 'number' || b.file_size < 0) {
    return 'file_size is required and must be a non-negative number.'
  }

  return null
}

// ---------------------------------------------------------------------------
// Signed URL helper
// ---------------------------------------------------------------------------

/**
 * Generates a signed download URL for a report file stored in Supabase Storage.
 * If the report_url is an external URL (not a storage path), returns it as-is.
 */
async function getSignedDownloadUrl(
  supabase: Awaited<ReturnType<typeof createClient>>,
  reportUrl: string,
): Promise<string | null> {
  // If it looks like an external URL, return as-is
  if (reportUrl.startsWith('http://') || reportUrl.startsWith('https://')) {
    return reportUrl
  }

  // Treat as a Supabase Storage path and generate a signed URL
  const { data, error } = await supabase.storage
    .from(STORAGE_BUCKET)
    .createSignedUrl(reportUrl, SIGNED_URL_EXPIRY)

  if (error || !data?.signedUrl) {
    console.error('[getSignedDownloadUrl] Error:', error?.message)
    return null
  }

  return data.signedUrl
}

// ---------------------------------------------------------------------------
// GET /api/reports
// ---------------------------------------------------------------------------

/**
 * Lists reports for a project and valuation method.
 * Returns signed download URLs (1-hour expiry) and increments download_count.
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

    const table = getReportsTable(method)

    // Cast to representative table: all five *_reports tables share the same schema.
    const { data, error, count } = await supabase
      .from(table as 'dcf_reports')
      .select(
        'report_id, project_id, draft_id, report_url, file_size, download_count, issued_by, issued_at, created_at',
        { count: 'exact' },
      )
      .eq('project_id', projectId)
      .order('issued_at', { ascending: false })
      .range(from, to)

    if (error) {
      console.error(`[GET /api/reports] ${table}:`, error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch reports.' },
        { status: 500 },
      )
    }

    // Generate signed URLs and increment download_count for each report
    const reportsWithUrls = await Promise.all(
      (data ?? []).map(async (report) => {
        const signedUrl = await getSignedDownloadUrl(supabase, report.report_url)

        // Increment download_count (fire-and-forget, non-blocking)
        // Cast to representative table: all five *_reports tables share the same schema.
        supabase
          .from(table as 'dcf_reports')
          .update({ download_count: (report.download_count ?? 0) + 1 })
          .eq('report_id', report.report_id)
          .then(({ error: incError }) => {
            if (incError) {
              console.error(
                `[GET /api/reports] download_count increment error for ${report.report_id}:`,
                incError.message,
              )
            }
          })

        return {
          ...report,
          download_url: signedUrl,
        }
      }),
    )

    return NextResponse.json({
      success: true,
      data: {
        reports: reportsWithUrls,
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/reports] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// POST /api/reports
// ---------------------------------------------------------------------------

/**
 * Creates (issues) a final report record.
 *
 * Body:
 *   - project_id (string, required)
 *   - method     (string, required) - dcf|relative|asset|intrinsic|tax
 *   - draft_id   (string, required) - UUID of the approved draft
 *   - report_url (string, required) - Storage path or external URL to the report file
 *   - file_size  (number, required) - File size in bytes
 *
 * Sets issued_by to current user and issued_at to current timestamp.
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

    const { project_id, method, draft_id, report_url, file_size } = body as CreateReportBody
    const validatedMethod = method as ValuationMethod

    // Verify project access
    const { project, error: accessError } = await verifyProjectAccess(
      supabase,
      project_id,
      user.id,
      role as UserRole,
    )
    if (accessError || !project) {
      return NextResponse.json(
        { success: false, error: accessError ?? 'Project not found.' },
        { status: 403 },
      )
    }

    // Only assigned accountant or admin can issue reports
    const isAssignedAccountant = project.accountant_id === user.id
    const isAdmin = role === 'admin'

    if (!isAssignedAccountant && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'Only the assigned accountant or admin can issue reports.' },
        { status: 403 },
      )
    }

    // Verify the referenced draft exists and is confirmed/finalized
    // Cast to representative table: all five *_drafts tables share the same schema.
    const draftsTable = getDraftsTable(validatedMethod)
    const { data: draft, error: draftError } = await supabase
      .from(draftsTable as 'dcf_drafts')
      .select('draft_id, project_id, status')
      .eq('draft_id', draft_id)
      .single()

    if (draftError || !draft) {
      return NextResponse.json(
        { success: false, error: 'Referenced draft not found.' },
        { status: 404 },
      )
    }

    if (draft.project_id !== project_id) {
      return NextResponse.json(
        { success: false, error: 'Draft does not belong to the specified project.' },
        { status: 400 },
      )
    }

    if (draft.status !== 'confirmed' && draft.status !== 'finalized') {
      return NextResponse.json(
        {
          success: false,
          error: `Cannot issue a report from a draft with status '${draft.status}'. Draft must be confirmed or finalized.`,
        },
        { status: 400 },
      )
    }

    // Insert report record
    const reportsTable = getReportsTable(validatedMethod)
    const now = new Date().toISOString()

    // Cast to representative table: all five *_reports tables share the same schema.
    const { data: report, error: insertError } = await supabase
      .from(reportsTable as 'dcf_reports')
      .insert({
        project_id,
        draft_id,
        report_url: report_url.trim(),
        file_size,
        download_count: 0,
        issued_by: user.id,
        issued_at: now,
        created_at: now,
      } as ReportInsert)
      .select(
        'report_id, project_id, draft_id, report_url, file_size, download_count, issued_by, issued_at, created_at',
      )
      .single()

    if (insertError) {
      console.error(`[POST /api/reports] ${reportsTable} insert error:`, insertError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to create report.' },
        { status: 500 },
      )
    }

    return NextResponse.json(
      { success: true, data: report },
      { status: 201 },
    )
  } catch (err) {
    console.error('[POST /api/reports] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
