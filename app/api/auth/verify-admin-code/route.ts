/**
 * @task S2F7-fix
 * @description Admin code verification API (server-side only)
 *
 * Moves hardcoded ADMIN2026 from client-side to server-side.
 * The admin registration code is stored in env var ADMIN_REGISTRATION_CODE.
 */

import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  try {
    const { code } = await req.json()

    if (!code || typeof code !== 'string') {
      return NextResponse.json(
        { valid: false, error: '인증 코드를 입력해주세요' },
        { status: 400 }
      )
    }

    const validCode = process.env.ADMIN_REGISTRATION_CODE
    if (!validCode) {
      return NextResponse.json(
        { valid: false, error: '서버 설정 오류: 관리자 코드가 설정되지 않았습니다' },
        { status: 500 }
      )
    }

    if (code !== validCode) {
      return NextResponse.json(
        { valid: false, error: '관리자 인증 코드가 올바르지 않습니다' },
        { status: 401 }
      )
    }

    return NextResponse.json({ valid: true })
  } catch {
    return NextResponse.json(
      { valid: false, error: '요청 처리 중 오류가 발생했습니다' },
      { status: 500 }
    )
  }
}
