# S5T2: Test Coverage & Error Handling Enhancement

## Task 정보
- **Task ID**: S5T2
- **Task Name**: 테스트 커버리지 향상 및 에러 핸들링 강화
- **Stage**: S5 (Finalization - 개발 마무리)
- **Area**: T (Testing)
- **Dependencies**: S5T1

## Task 목표

S5T1에서 달성한 테스트 커버리지를 더욱 향상시키고, API 에러 핸들링을 강화하여 시스템 안정성을 높입니다.

**현재 커버리지 (S5T1):**
- Statement: 87.3%
- Branch: **82.1%** ← 목표 미달 (85% 목표)
- Function: 89.5%
- Line: 86.8%

**개선 목표:**
- Branch Coverage: 82.1% → **85%+** (+2.9%)
- 완성도 +1점 (18 → 19)
- 유용성 +1점 (18 → 19)

---

## 생성/수정 파일

| 파일 | 변경 내용 | 저장 위치 |
|------|----------|----------|
| `edge-cases.test.ts` | 엣지 케이스 테스트 추가 | `Process/S5_개발_마무리/Testing/tests/integration/edge-cases.test.ts` |
| `api-errors.ts` | API 에러 클래스 정의 | `Process/S5_개발_마무리/Testing/lib/errors/api-errors.ts` |
| `error-handling-guide.md` | 에러 핸들링 가이드 문서 | `Process/S5_개발_마무리/Testing/docs/error-handling-guide.md` |

**Pre-commit Hook 자동 복사:**
- `edge-cases.test.ts` → `tests/integration/edge-cases.test.ts`
- `api-errors.ts` → `lib/errors/api-errors.ts`
- `error-handling-guide.md` → `docs/error-handling-guide.md`

---

## 개선 항목 상세

### 1. Branch Coverage 향상 (82.1% → 85%+) ⭐

**Branch란?**
- if/else, switch, 삼항 연산자, 논리 연산자(&&, ||)의 모든 분기

**미커버 분기 예시:**
```typescript
// 현재 테스트되지 않은 분기 (Branch Coverage 하락 원인)

// 1. 에러 핸들링 분기
if (error.code === 'PGRST116') {
  // 테스트 안 함
} else {
  // 테스트 함
}

// 2. 조건부 렌더링 분기
{user ? <Dashboard /> : <Login />}
// user === null 케이스 테스트 안 함

// 3. 삼항 연산자 분기
const message = status === 'success' ? 'Success' : 'Failed'
// status === 'success' 케이스만 테스트함
```

**개선 방안: 엣지 케이스 테스트 추가**

```typescript
// tests/integration/edge-cases.test.ts

import { describe, it, expect } from '@jest/globals'
import { createClient } from '@supabase/supabase-js'

describe('Edge Cases - Error Handling', () => {

  it('should handle PGRST116 error (user not found)', async () => {
    // Supabase 에러 코드 PGRST116 테스트
    const response = await fetch('/api/users/nonexistent-id')
    expect(response.status).toBe(404)
    expect(await response.json()).toEqual({
      error: 'User not found',
      code: 'PGRST116'
    })
  })

  it('should handle network timeout', async () => {
    // 네트워크 타임아웃 테스트
    const controller = new AbortController()
    setTimeout(() => controller.abort(), 100) // 100ms 타임아웃

    await expect(
      fetch('/api/projects', { signal: controller.signal })
    ).rejects.toThrow('The operation was aborted')
  })

  it('should handle invalid JSON payload', async () => {
    // 잘못된 JSON 테스트
    const response = await fetch('/api/projects', {
      method: 'POST',
      body: 'invalid-json'
    })
    expect(response.status).toBe(400)
    expect(await response.json()).toEqual({
      error: 'Invalid JSON payload'
    })
  })

})

describe('Edge Cases - Boundary Conditions', () => {

  it('should reject project_id with invalid format', async () => {
    // VL-YYYYMMDD-XXXX 형식 외 거부
    const invalidIds = ['ABC-123', '12345', 'VL-999999-9999']

    for (const id of invalidIds) {
      const response = await fetch(`/api/projects/${id}`)
      expect(response.status).toBe(400)
      expect(await response.json()).toEqual({
        error: 'Invalid project_id format'
      })
    }
  })

  it('should handle DCF with zero revenue', async () => {
    // 매출 0원일 때 DCF 계산 (엣지 케이스)
    const result = await calculateDCF({
      revenue: 0, // ← 경계 조건
      growth_rate: 0.1,
      wacc: 0.12
    })
    expect(result.enterprise_value).toBe(0)
    expect(result.equity_value).toBe(0)
  })

  it('should handle WACC > 100%', async () => {
    // 비정상적으로 높은 WACC (에러 처리)
    await expect(
      calculateDCF({ revenue: 1000, wacc: 1.5 }) // 150%
    ).rejects.toThrow('WACC must be between 0% and 100%')
  })

})

describe('Edge Cases - Concurrency', () => {

  it('should handle concurrent project creation', async () => {
    // 동시에 3개 프로젝트 생성 (동시성 테스트)
    const promises = [
      createProject({ name: 'Project A' }),
      createProject({ name: 'Project B' }),
      createProject({ name: 'Project C' })
    ]

    const results = await Promise.all(promises)

    // 모든 프로젝트가 고유 ID를 가져야 함
    const ids = results.map(r => r.project_id)
    expect(new Set(ids).size).toBe(3) // 중복 없음
  })

})
```

**예상 효과:**
- 15개 엣지 케이스 테스트 추가
- Branch Coverage: 82.1% → 85.5% (+3.4%)

---

### 2. API 에러 핸들링 강화 ⭐

**현재 문제:**
- 에러 메시지 불명확: "An error occurred"
- 에러 코드 없음
- 사용자가 문제 해결 방법 모름

**개선 방안: API 에러 클래스 정의**

```typescript
// lib/errors/api-errors.ts

/**
 * @task S5T2
 * @description API 에러 클래스 - 구체적 에러 메시지 제공
 */

export class APIError extends Error {
  public code: string
  public statusCode: number
  public details?: Record<string, any>

  constructor(message: string, code: string, statusCode: number, details?: Record<string, any>) {
    super(message)
    this.name = 'APIError'
    this.code = code
    this.statusCode = statusCode
    this.details = details
  }

  toJSON() {
    return {
      error: this.message,
      code: this.code,
      statusCode: this.statusCode,
      details: this.details
    }
  }
}

// 사전 정의된 에러들
export class ValidationError extends APIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'VALIDATION_ERROR', 400, details)
    this.name = 'ValidationError'
  }
}

export class NotFoundError extends APIError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404)
    this.name = 'NotFoundError'
  }
}

export class UnauthorizedError extends APIError {
  constructor(message: string = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401)
    this.name = 'UnauthorizedError'
  }
}

export class DatabaseError extends APIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'DATABASE_ERROR', 500, details)
    this.name = 'DatabaseError'
  }
}

export class ExternalAPIError extends APIError {
  constructor(service: string, message: string) {
    super(`${service} API error: ${message}`, 'EXTERNAL_API_ERROR', 502)
    this.name = 'ExternalAPIError'
  }
}

// 에러 핸들러 유틸리티
export function handleAPIError(error: unknown): APIError {
  if (error instanceof APIError) {
    return error
  }

  if (error instanceof Error) {
    // Supabase 에러 코드 매핑
    if ('code' in error && error.code === 'PGRST116') {
      return new NotFoundError('Resource')
    }

    return new APIError(error.message, 'INTERNAL_ERROR', 500)
  }

  return new APIError('Unknown error occurred', 'UNKNOWN_ERROR', 500)
}
```

**사용 예시:**
```typescript
// API 핸들러에서 사용

import { NotFoundError, ValidationError, handleAPIError } from '@/lib/errors/api-errors'

export async function GET(req: Request) {
  try {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('project_id', projectId)
      .single()

    if (error) throw error
    if (!data) throw new NotFoundError('Project')

    return Response.json(data)

  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```

**개선 효과:**
- 에러 메시지 구체화: "An error occurred" → "Project not found"
- 에러 코드 제공: `NOT_FOUND`, `VALIDATION_ERROR`
- HTTP 상태 코드 명확: 404, 400, 401, 500, 502
- 사용자에게 해결 방법 제시 가능

---

### 3. 에러 핸들링 가이드 문서 ⭐

**파일:** `docs/error-handling-guide.md`

**내용:**
```markdown
# API 에러 핸들링 가이드

## 에러 코드 목록

| 에러 코드 | 설명 | HTTP 상태 | 해결 방법 |
|-----------|------|----------|----------|
| VALIDATION_ERROR | 입력값 검증 실패 | 400 | 입력값 확인 후 재시도 |
| NOT_FOUND | 리소스 없음 | 404 | URL/ID 확인 |
| UNAUTHORIZED | 인증 실패 | 401 | 로그인 후 재시도 |
| DATABASE_ERROR | DB 오류 | 500 | 관리자 문의 |
| EXTERNAL_API_ERROR | 외부 API 오류 | 502 | 잠시 후 재시도 |

## 에러 응답 형식

```json
{
  "error": "Project not found",
  "code": "NOT_FOUND",
  "statusCode": 404,
  "details": {
    "project_id": "VL-20260223-0001"
  }
}
```

## 클라이언트 에러 처리 예시

```typescript
try {
  const response = await fetch('/api/projects/VL-20260223-0001')

  if (!response.ok) {
    const error = await response.json()

    switch (error.code) {
      case 'NOT_FOUND':
        alert('프로젝트를 찾을 수 없습니다.')
        break
      case 'UNAUTHORIZED':
        router.push('/login')
        break
      default:
        alert(`오류: ${error.error}`)
    }
  }

  const data = await response.json()
  // 성공 처리

} catch (error) {
  console.error('Network error:', error)
  alert('네트워크 오류가 발생했습니다.')
}
```

## 서버 에러 처리 예시

```typescript
import { NotFoundError, ValidationError, handleAPIError } from '@/lib/errors/api-errors'

export async function POST(req: Request) {
  try {
    const body = await req.json()

    // 입력값 검증
    if (!body.project_name) {
      throw new ValidationError('project_name is required', {
        field: 'project_name'
      })
    }

    // DB 조회
    const project = await getProject(body.project_id)
    if (!project) {
      throw new NotFoundError('Project')
    }

    // 성공
    return Response.json({ success: true })

  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```
```

---

## 검증 기준

### 1. 테스트 커버리지
- [ ] Branch Coverage ≥ 85.0%
- [ ] Statement Coverage ≥ 87.0% (유지)
- [ ] Function Coverage ≥ 89.0% (유지)
- [ ] Line Coverage ≥ 86.0% (유지)

### 2. 엣지 케이스 테스트
- [ ] 15개 이상 엣지 케이스 테스트 추가
- [ ] 에러 핸들링 분기 커버
- [ ] 경계 조건 테스트 (0, null, undefined, 최댓값)
- [ ] 동시성 테스트

### 3. API 에러 클래스
- [ ] APIError 기본 클래스 정의
- [ ] 5개 사전 정의 에러 (Validation, NotFound, Unauthorized, Database, ExternalAPI)
- [ ] toJSON() 메서드 포함
- [ ] handleAPIError() 유틸리티 함수

### 4. 에러 핸들링 가이드
- [ ] 에러 코드 목록 표
- [ ] 에러 응답 형식 예시
- [ ] 클라이언트 에러 처리 예시
- [ ] 서버 에러 처리 예시

---

## 예상 결과

**개선 전 (S5T1):**
- Branch Coverage: 82.1%
- 에러 메시지: 불명확
- 에러 코드: 없음

**개선 후 (S5T2):**
- Branch Coverage: 85.5% (+3.4%)
- 에러 메시지: 구체적 ("Project not found")
- 에러 코드: 명확 (NOT_FOUND, VALIDATION_ERROR 등)

**품질 향상:**
- 완성도: 18/20 → 19/20 (+1점)
- 유용성: 18/20 → 19/20 (+1점)

---

**작성자**: Main Agent
**작성일**: 2026-02-23
**버전**: 1.0
