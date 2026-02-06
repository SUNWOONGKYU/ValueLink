/**
 * @task S1BI1
 * @description Next.js Middleware - Supabase 세션 관리
 */

import { updateSession } from '@/lib/supabase/middleware'
import { NextRequest } from 'next/server'

/**
 * Middleware 실행
 * - 모든 요청에서 Supabase 세션 갱신
 */
export async function middleware(request: NextRequest) {
  return await updateSession(request)
}

/**
 * Middleware 적용 경로
 * - /auth 제외 (인증 페이지는 보호 불필요)
 */
export const config = {
  matcher: [
    /*
     * 다음 경로를 제외한 모든 요청에 적용:
     * - _next/static (정적 파일)
     * - _next/image (이미지 최적화)
     * - favicon.ico (파비콘)
     * - public 폴더 (정적 자원)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
