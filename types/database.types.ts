/**
 * @task S1BI1
 * @description Supabase 데이터베이스 타입 정의
 *
 * 자동 생성 방법:
 * npx supabase gen types typescript --project-id <project-id> > types/database.types.ts
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

/**
 * Supabase 데이터베이스 스키마
 * TODO: Supabase CLI로 실제 스키마 생성 후 교체
 */
export interface Database {
  public: {
    Tables: {
      // 예시 테이블 (S1D1에서 실제 테이블 정의)
      users: {
        Row: {
          id: string
          email: string
          created_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
