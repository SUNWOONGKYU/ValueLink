/**
 * @task S2F4-logout
 * @description 로그아웃 API Route Handler
 *
 * - POST /api/auth/logout: Supabase 세션 종료 후 /login으로 리다이렉트 (303)
 * - GET /api/auth/logout: 세션을 건드리지 않고 /login으로 리다이렉트만 수행
 *   (Next.js <Link> 프리페치·브라우저 선요청이 GET을 보내도 세션이 파괴되지 않도록
 *    파괴적 동작은 POST에만 둔다 — 프리페치發 자동 로그아웃 회귀 방지)
 * - mypage-template.tsx의 로그아웃 폼(method="post")이 이 경로를 가리킴
 */

import { type NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function POST(request: NextRequest) {
  const supabase = await createClient()
  await supabase.auth.signOut()

  const url = request.nextUrl.clone()
  url.pathname = '/login'
  // 303: POST 후 GET으로 리다이렉트 (재제출 방지)
  return NextResponse.redirect(url, 303)
}

export async function GET(request: NextRequest) {
  // 프리페치 안전: GET은 로그아웃하지 않는다
  const url = request.nextUrl.clone()
  url.pathname = '/login'
  return NextResponse.redirect(url)
}
