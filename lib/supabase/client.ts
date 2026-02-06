/**
 * @task S1BI1
 * @description Supabase 클라이언트 (브라우저용)
 */

import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '@/types/database.types'

/**
 * 브라우저용 Supabase 클라이언트 생성
 * - 클라이언트 컴포넌트, 이벤트 핸들러, useEffect에서 사용
 * - 자동으로 쿠키에서 세션 읽기
 */
export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
