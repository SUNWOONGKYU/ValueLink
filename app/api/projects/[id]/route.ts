/**
 * @task S2BA2-ext
 * @description Project Single-Record API — GET /api/projects/[id]
 *
 * Returns a single project by project_id for the authenticated user.
 * All step pages (step-1 through step-12) fetch from this endpoint.
 *
 * Response shape covers the union of all ProjectData interfaces used
 * across step pages:
 *   project_id, company_name_kr, company_name_en, valuation_purpose,
 *   requested_methods, status, current_step, created_at,          (step-1)
 *   accountant_id,                                                  (step-6)
 *   agreed_price, deposit_amount, deposit_paid_at, balance_paid_at (step-10/11)
 *
 * Schema: schema-v5 (types/database.types.ts — projects table)
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

// ---------------------------------------------------------------------------
// Auth helper (mirrors pattern from /api/projects/route.ts)
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
// GET /api/projects/[id]
// ---------------------------------------------------------------------------

/**
 * Fetches a single project by its project_id.
 *
 * Access control:
 *   - Customer: may only access their own projects.
 *   - Accountant: may access projects assigned to them.
 *   - Admin: may access any project.
 *
 * @param request - Incoming Next.js request object.
 * @param context - Route context containing { params: { id } }.
 * @returns JSON with the project row or an error object.
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } },
): Promise<NextResponse> {
  try {
    const projectId = params.id

    if (!projectId) {
      return NextResponse.json(
        { success: false, error: 'project_id is required.' },
        { status: 400 },
      )
    }

    const supabase = await createClient()
    const authResult = await getAuthenticatedUser(supabase)

    if (!authResult.user) {
      return NextResponse.json(
        { success: false, error: 'Authentication required.' },
        { status: 401 },
      )
    }

    const { user, role } = authResult

    // Fetch the project with all fields needed by step pages
    const { data: project, error: fetchError } = await supabase
      .from('projects')
      .select(
        `project_id,
         company_name_kr,
         company_name_en,
         valuation_purpose,
         requested_methods,
         status,
         current_step,
         accountant_id,
         agreed_price,
         deposit_amount,
         deposit_paid_at,
         balance_paid_at,
         user_id,
         created_at,
         updated_at`,
      )
      .eq('project_id', projectId)
      .single()

    if (fetchError || !project) {
      return NextResponse.json(
        { success: false, error: 'Project not found.' },
        { status: 404 },
      )
    }

    // Access control: customer can only see own projects; accountant sees assigned ones
    if (role !== 'admin') {
      const isOwner = project.user_id === user.id
      const isAssignedAccountant = project.accountant_id === user.id

      if (!isOwner && !isAssignedAccountant) {
        return NextResponse.json(
          { success: false, error: 'You do not have access to this project.' },
          { status: 403 },
        )
      }
    }

    // Return the project row directly (step pages destructure fields they need)
    return NextResponse.json(project)
  } catch (err) {
    console.error('[GET /api/projects/[id]] Unexpected error:', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error.' },
      { status: 500 },
    )
  }
}
