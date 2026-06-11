/**
 * @task S2F4-logout
 * @description 로그아웃 API Route Handler
 *
 * - GET /api/auth/logout
 * - Supabase 세션 종료 후 /login으로 리다이렉트
 * - mypage-template.tsx의 로그아웃 링크가 이 경로를 가리킴
 */

import { type NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const supabase = await createClient()
  await supabase.auth.signOut()

  const url = request.nextUrl.clone()
  url.pathname = '/login'
  return NextResponse.redirect(url)
}
