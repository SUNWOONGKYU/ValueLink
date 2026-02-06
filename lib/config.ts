/**
 * @task S1BI1
 * @description 환경변수 설정 (타입 안전)
 */

/**
 * 환경변수 유효성 검사
 */
function getEnvVar(key: string): string {
  const value = process.env[key]
  if (!value) {
    throw new Error(`환경변수 ${key}가 설정되지 않았습니다.`)
  }
  return value
}

/**
 * Supabase 설정
 */
export const supabaseConfig = {
  url: getEnvVar('NEXT_PUBLIC_SUPABASE_URL'),
  anonKey: getEnvVar('NEXT_PUBLIC_SUPABASE_ANON_KEY'),
} as const

/**
 * 앱 설정
 */
export const appConfig = {
  url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
} as const
