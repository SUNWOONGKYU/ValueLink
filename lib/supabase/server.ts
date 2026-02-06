/**
 * @task S1BI1
 * @description Supabase 클라이언트 (서버용)
 */

import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '@/types/database.types'

/**
 * 서버용 Supabase 클라이언트 생성
 * - Server Components, Route Handlers, Server Actions에서 사용
 * - 쿠키를 통한 세션 관리
 */
export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value, ...options })
          } catch (error) {
            // Server Component에서 set 호출 시 에러 무시
            // Middleware나 Route Handler에서만 작동
          }
        },
        remove(name: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value: '', ...options })
          } catch (error) {
            // Server Component에서 remove 호출 시 에러 무시
          }
        },
      },
    }
  )
}
