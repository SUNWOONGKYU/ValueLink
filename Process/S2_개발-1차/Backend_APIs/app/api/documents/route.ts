/**
 * @task S2BA3
 * @description Documents API - File upload, listing, and deletion
 *
 * Endpoints:
 *   GET    /api/documents  - List documents for a project+method
 *   POST   /api/documents  - Upload a file (FormData)
 *   DELETE /api/documents  - Delete a document (storage + metadata)
 *
 * Schema alignment: schema-v4-final.sql
 *   Tables: dcf_documents, relative_documents, asset_documents,
 *           intrinsic_documents, tax_documents
 */

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

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

/** Allowed MIME types for document upload. */
const ALLOWED_MIME_TYPES: ReadonlySet<string> = new Set([
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'image/jpeg',
  'image/png',
])

/** Human-readable labels for allowed file types. */
const ALLOWED_EXTENSIONS = 'PDF, XLSX, DOCX, JPG, PNG'

/** Maximum file size in bytes (50 MB). */
const MAX_FILE_SIZE = 50 * 1024 * 1024

/** Supabase Storage bucket name. */
const STORAGE_BUCKET = 'valuation-documents'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function validateMethod(method: string): method is ValuationMethod {
  return (VALID_METHODS as readonly string[]).includes(method)
}

function getDocumentsTable(method: ValuationMethod): string {
  return `${method}_documents`
}

/**
 * Sanitize a filename by removing path separators, null bytes, and
 * collapsing whitespace. Keeps alphanumeric, hyphens, underscores, dots,
 * and Korean characters.
 */
function sanitizeFilename(raw: string): string {
  return raw
    .replace(/[\\/:\0]/g, '')           // remove path separators & null bytes
    .replace(/[<>"|?*]/g, '')           // remove shell-dangerous chars
    .replace(/\s+/g, '_')              // collapse whitespace to underscore
    .replace(/\.{2,}/g, '.')           // collapse consecutive dots
    .slice(0, 200)                     // cap length
    .trim()
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

/**
 * Verifies the requesting user has access to the given project.
 * Returns the project row on success, or null on failure (with an error message).
 */
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
// GET /api/documents
// ---------------------------------------------------------------------------

/**
 * Lists documents for a project and valuation method.
 *
 * Query params:
 *   - project_id (required) - The project to list documents for.
 *   - method     (required) - Valuation method (dcf|relative|asset|intrinsic|tax).
 *   - page                  - Page number (default 1).
 *   - limit                 - Items per page (default 20, max 100).
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

    const table = getDocumentsTable(method)

    const { data, error, count } = await supabase
      .from(table)
      .select(
        'document_id, project_id, category, file_name, file_path, file_size, file_type, upload_status, uploaded_by, created_at',
        { count: 'exact' },
      )
      .eq('project_id', projectId)
      .order('created_at', { ascending: false })
      .range(from, to)

    if (error) {
      console.error(`[GET /api/documents] ${table}:`, error.message)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch documents.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        documents: data ?? [],
        pagination: {
          page,
          limit,
          total: count ?? 0,
          total_pages: count ? Math.ceil(count / limit) : 0,
        },
      },
    })
  } catch (err) {
    console.error('[GET /api/documents] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// POST /api/documents
// ---------------------------------------------------------------------------

/**
 * Uploads a document file for a project.
 *
 * FormData fields:
 *   - file       (File, required)  - The file to upload.
 *   - project_id (string, required)
 *   - method     (string, required) - dcf|relative|asset|intrinsic|tax
 *   - category   (string, required) - e.g. "financial_statement", "contract"
 *
 * Validation:
 *   - Allowed types: PDF, XLSX, DOCX, JPG, PNG
 *   - Max size: 50 MB
 *   - Filename is sanitized before storage.
 *
 * Storage path: valuation-documents/projects/{project_id}/{method}/{timestamp}-{name}
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

    // Parse FormData
    let formData: FormData
    try {
      formData = await request.formData()
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid form data. Expected multipart/form-data.' },
        { status: 400 },
      )
    }

    const file = formData.get('file') as File | null
    const projectId = formData.get('project_id') as string | null
    const method = formData.get('method') as string | null
    const category = formData.get('category') as string | null

    // ----- Validate required fields -----

    if (!file || !(file instanceof File) || file.size === 0) {
      return NextResponse.json(
        { success: false, error: 'file is required and must be a non-empty file.' },
        { status: 400 },
      )
    }

    if (!projectId || typeof projectId !== 'string') {
      return NextResponse.json(
        { success: false, error: 'project_id is required.' },
        { status: 400 },
      )
    }

    if (!method || !validateMethod(method)) {
      return NextResponse.json(
        {
          success: false,
          error: `method is required and must be one of: ${VALID_METHODS.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    if (!category || typeof category !== 'string' || category.trim().length === 0) {
      return NextResponse.json(
        { success: false, error: 'category is required.' },
        { status: 400 },
      )
    }

    // ----- File validation -----

    if (!ALLOWED_MIME_TYPES.has(file.type)) {
      return NextResponse.json(
        {
          success: false,
          error: `File type '${file.type}' is not allowed. Allowed types: ${ALLOWED_EXTENSIONS}.`,
        },
        { status: 400 },
      )
    }

    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        {
          success: false,
          error: `File size (${(file.size / 1024 / 1024).toFixed(1)} MB) exceeds the 50 MB limit.`,
        },
        { status: 400 },
      )
    }

    // ----- Project access -----

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

    // Only project owner or admin can upload
    const isOwner = project.user_id === user.id
    const isAdmin = role === 'admin'
    if (!isOwner && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'Only the project owner or admin can upload documents.' },
        { status: 403 },
      )
    }

    // ----- Upload to Storage -----

    const sanitizedName = sanitizeFilename(file.name)
    if (!sanitizedName) {
      return NextResponse.json(
        { success: false, error: 'File name is invalid after sanitization.' },
        { status: 400 },
      )
    }

    const timestamp = Date.now()
    const storagePath = `projects/${projectId}/${method}/${timestamp}-${sanitizedName}`

    const fileBuffer = Buffer.from(await file.arrayBuffer())

    const { error: uploadError } = await supabase.storage
      .from(STORAGE_BUCKET)
      .upload(storagePath, fileBuffer, {
        contentType: file.type,
        upsert: false,
      })

    if (uploadError) {
      console.error('[POST /api/documents] Storage upload error:', uploadError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to upload file to storage.' },
        { status: 500 },
      )
    }

    // ----- Insert metadata -----

    const table = getDocumentsTable(method)
    const now = new Date().toISOString()

    const { data: docRecord, error: insertError } = await supabase
      .from(table)
      .insert({
        project_id: projectId,
        category: category.trim(),
        file_name: sanitizedName,
        file_path: storagePath,
        file_size: file.size,
        file_type: file.type,
        uploaded_by: user.id,
        created_at: now,
      })
      .select(
        'document_id, project_id, category, file_name, file_path, file_size, file_type, upload_status, uploaded_by, created_at',
      )
      .single()

    if (insertError) {
      // Rollback: remove the uploaded file from storage
      console.error(`[POST /api/documents] ${table} insert error:`, insertError.message)
      await supabase.storage.from(STORAGE_BUCKET).remove([storagePath])

      return NextResponse.json(
        { success: false, error: 'Failed to save document metadata. Upload rolled back.' },
        { status: 500 },
      )
    }

    return NextResponse.json(
      { success: true, data: docRecord },
      { status: 201 },
    )
  } catch (err) {
    console.error('[POST /api/documents] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}

// ---------------------------------------------------------------------------
// DELETE /api/documents
// ---------------------------------------------------------------------------

/**
 * Deletes a document (both storage file and metadata record).
 *
 * Body:
 *   - document_id (string, required) - UUID of the document to delete.
 *   - method      (string, required) - Valuation method to route to correct table.
 *
 * Auth: original uploader or admin.
 */
export async function DELETE(request: NextRequest): Promise<NextResponse<ApiResponse>> {
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

    const documentId = body.document_id as string | undefined
    const method = body.method as string | undefined

    if (!documentId || typeof documentId !== 'string') {
      return NextResponse.json(
        { success: false, error: 'document_id is required.' },
        { status: 400 },
      )
    }

    if (!method || !validateMethod(method)) {
      return NextResponse.json(
        {
          success: false,
          error: `method is required and must be one of: ${VALID_METHODS.join(', ')}.`,
        },
        { status: 400 },
      )
    }

    const table = getDocumentsTable(method)

    // Fetch existing document
    const { data: doc, error: fetchError } = await supabase
      .from(table)
      .select('document_id, file_path, uploaded_by')
      .eq('document_id', documentId)
      .single()

    if (fetchError || !doc) {
      return NextResponse.json(
        { success: false, error: 'Document not found.' },
        { status: 404 },
      )
    }

    // Auth: only the uploader or admin can delete
    const isUploader = doc.uploaded_by === user.id
    const isAdmin = role === 'admin'

    if (!isUploader && !isAdmin) {
      return NextResponse.json(
        { success: false, error: 'Only the uploader or admin can delete this document.' },
        { status: 403 },
      )
    }

    // Delete from storage
    const { error: storageError } = await supabase.storage
      .from(STORAGE_BUCKET)
      .remove([doc.file_path])

    if (storageError) {
      console.error('[DELETE /api/documents] Storage removal error:', storageError.message)
      // Continue with metadata deletion even if storage fails
      // (the file may have already been removed or the path could be stale)
    }

    // Delete metadata
    const { error: deleteError } = await supabase
      .from(table)
      .delete()
      .eq('document_id', documentId)

    if (deleteError) {
      console.error(`[DELETE /api/documents] ${table} delete error:`, deleteError.message)
      return NextResponse.json(
        { success: false, error: 'Failed to delete document metadata.' },
        { status: 500 },
      )
    }

    return NextResponse.json({
      success: true,
      data: { document_id: documentId, deleted: true },
    })
  } catch (err) {
    console.error('[DELETE /api/documents] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
