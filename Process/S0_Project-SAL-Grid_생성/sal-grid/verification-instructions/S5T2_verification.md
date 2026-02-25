# S5T2 Verification Instruction

## Task 정보
- **Task ID**: S5T2
- **Task Name**: 테스트 커버리지 향상 및 에러 핸들링 강화
- **Verification Agent**: qa-specialist

---

## 검증 체크리스트

### 1. 파일 생성 확인

- [ ] `Process/S5_개발_마무리/Testing/tests/integration/edge-cases.test.ts` 존재
- [ ] `Process/S5_개발_마무리/Testing/lib/errors/api-errors.ts` 존재
- [ ] `Process/S5_개발_마무리/Testing/docs/error-handling-guide.md` 존재
- [ ] 총 3개 파일 생성 확인

---

### 2. 엣지 케이스 테스트 검증

#### 2.1 파일 구조
- [ ] `edge-cases.test.ts` 파일 존재
- [ ] 3개 describe 블록 (Error Handling, Boundary Conditions, Concurrency)
- [ ] 15개 이상 테스트 케이스 (it 블록)

#### 2.2 테스트 카테고리
- [ ] **에러 핸들링**: PGRST116, 네트워크 타임아웃, 잘못된 JSON
- [ ] **경계 조건**: 잘못된 project_id 형식, DCF 매출 0원, WACC > 100%
- [ ] **동시성**: 동시 프로젝트 생성

#### 2.3 코드 품질
- [ ] import 문 정확 (`@jest/globals`, `@supabase/supabase-js`)
- [ ] async/await 올바르게 사용
- [ ] expect 단언문 명확

**검증 방법:**
```bash
# 테스트 실행
npm run test tests/integration/edge-cases.test.ts

# 예상 결과
# PASS tests/integration/edge-cases.test.ts
#   Edge Cases - Error Handling
#     ✓ should handle PGRST116 error
#     ✓ should handle network timeout
#     ✓ should handle invalid JSON payload
#   Edge Cases - Boundary Conditions
#     ✓ should reject project_id with invalid format
#     ✓ should handle DCF with zero revenue
#     ✓ should handle WACC > 100%
#   Edge Cases - Concurrency
#     ✓ should handle concurrent project creation
```

---

### 3. API 에러 클래스 검증

#### 3.1 기본 클래스 (APIError)
- [ ] `APIError` 클래스 정의
- [ ] 4개 속성 (code, statusCode, details, message)
- [ ] `toJSON()` 메서드 포함

#### 3.2 사전 정의 에러 (5개)
- [ ] `ValidationError` (400)
- [ ] `NotFoundError` (404)
- [ ] `UnauthorizedError` (401)
- [ ] `DatabaseError` (500)
- [ ] `ExternalAPIError` (502)

#### 3.3 유틸리티 함수
- [ ] `handleAPIError()` 함수 정의
- [ ] Supabase 에러 코드 매핑 (PGRST116 → NotFoundError)
- [ ] 일반 Error 객체 처리

**검증 방법:**
```typescript
// api-errors.ts 코드 확인

export class APIError extends Error {
  public code: string
  public statusCode: number
  public details?: Record<string, any>

  constructor(...) { ... }
  toJSON() { ... }
}

export class ValidationError extends APIError { ... }
export class NotFoundError extends APIError { ... }
export class UnauthorizedError extends APIError { ... }
export class DatabaseError extends APIError { ... }
export class ExternalAPIError extends APIError { ... }

export function handleAPIError(error: unknown): APIError { ... }
```

---

### 4. 에러 핸들링 가이드 검증

#### 4.1 문서 구조
- [ ] Markdown 문법 올바름
- [ ] 4개 섹션 (에러 코드 목록, 에러 응답 형식, 클라이언트 예시, 서버 예시)

#### 4.2 에러 코드 목록 표
- [ ] 5개 에러 코드 설명
- [ ] HTTP 상태 코드 명시
- [ ] 해결 방법 포함

#### 4.3 코드 예시
- [ ] 클라이언트 에러 처리 예시 (fetch + switch)
- [ ] 서버 에러 처리 예시 (try-catch + handleAPIError)
- [ ] 코드 실행 가능 (문법 오류 없음)

**검증 방법:**
```markdown
# docs/error-handling-guide.md 확인

## 에러 코드 목록
| 에러 코드 | 설명 | HTTP 상태 | 해결 방법 |
|-----------|------|----------|----------|
| VALIDATION_ERROR | ... | 400 | ... |
| NOT_FOUND | ... | 404 | ... |
...

## 에러 응답 형식
```json
{
  "error": "Project not found",
  "code": "NOT_FOUND",
  ...
}
```

## 클라이언트 에러 처리 예시
```typescript
try {
  const response = await fetch(...)
  if (!response.ok) {
    const error = await response.json()
    switch (error.code) { ... }
  }
} catch (error) { ... }
```
```

---

### 5. 테스트 커버리지 검증 ⭐

#### 5.1 커버리지 목표
- [ ] **Branch Coverage ≥ 85.0%** (필수)
- [ ] Statement Coverage ≥ 87.0% (유지)
- [ ] Function Coverage ≥ 89.0% (유지)
- [ ] Line Coverage ≥ 86.0% (유지)

#### 5.2 커버리지 측정
```bash
# 커버리지 리포트 생성
npm run test:coverage

# 예상 결과
# ----------------------------|---------|----------|---------|---------|
# File                        | % Stmts | % Branch | % Funcs | % Lines |
# ----------------------------|---------|----------|---------|---------|
# All files                   |   87.5  |   85.3   |   89.7  |   87.1  |
# ----------------------------|---------|----------|---------|---------|
```

**검증 기준:**
- Branch Coverage가 85.0% 이상이면 PASS ✅
- 85.0% 미만이면 FAIL ❌

---

### 6. 통합 테스트 (API 에러 클래스 적용)

#### 6.1 API 핸들러 수정 확인 (선택 사항)
- [ ] 최소 1개 API에 `handleAPIError()` 적용
- [ ] try-catch 블록 포함
- [ ] 에러 응답 JSON 형식 통일

**검증 방법:**
```typescript
// 예시: api/projects/[id]/route.ts 확인

import { NotFoundError, handleAPIError } from '@/lib/errors/api-errors'

export async function GET(req: Request) {
  try {
    const project = await getProject(id)
    if (!project) throw new NotFoundError('Project')
    return Response.json(project)
  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```

---

### 7. 빌드 & 타입 체크

- [ ] TypeScript 컴파일 성공
- [ ] Next.js 빌드 성공
- [ ] ESLint 경고 0개
- [ ] 테스트 실행 성공 (엣지 케이스 테스트 포함)

**검증 방법:**
```bash
# TypeScript 타입 체크
npm run type-check

# Next.js 빌드
npm run build

# ESLint
npm run lint

# 테스트 실행
npm run test
```

**예상 결과:**
```
✓ Type checking complete (0 errors)
✓ Creating an optimized production build
✓ ESLint (0 warnings, 0 errors)
✓ Tests: 15 passed, 15 total
```

---

## 검증 결과 기록 형식

### Test Result
```json
{
  "unit_test": "PASS/FAIL - APIError 클래스 5개, handleAPIError 함수",
  "integration_test": "PASS/FAIL - 엣지 케이스 15개 테스트",
  "edge_cases": "PASS/FAIL - 에러 핸들링, 경계 조건, 동시성",
  "manual_test": "PENDING/PASS/FAIL - PO 테스트 실행"
}
```

### Build Verification
```json
{
  "compile": "PASS/FAIL - TypeScript 컴파일",
  "lint": "PASS/FAIL - ESLint 0 warnings",
  "deploy": "N/A - Test/Library 파일",
  "runtime": "PASS/FAIL - 테스트 실행 성공"
}
```

### Integration Verification
```json
{
  "dependency_propagation": "PASS/FAIL - S5T1 커버리지 향상",
  "cross_task_connection": "PASS/FAIL - API 핸들러와 연동",
  "data_flow": "PASS/FAIL - 에러 객체 직렬화 (toJSON)"
}
```

### Blockers
```json
{
  "dependency": "None/WARNING - 설명",
  "environment": "None/WARNING - 설명",
  "external_api": "None/WARNING - 설명",
  "status": "No Blockers / N Blockers"
}
```

### Comprehensive Verification
```json
{
  "task_instruction": "PASS/FAIL - 3개 파일 생성",
  "test": "PASS/FAIL - 엣지 케이스 15개, Branch Coverage 85%+",
  "build": "PASS/FAIL - TypeScript, Next.js, ESLint",
  "integration": "PASS/FAIL - API 에러 클래스 적용",
  "blockers": "None/N개",
  "final": "Verified / Needs Fix"
}
```

---

## PO 테스트 가이드

### 테스트 전 준비
1. `npm install` 실행 (dependencies 최신 상태)
2. `.env.local` 파일 설정 (Supabase URL/Key)

### 테스트 시나리오

#### 시나리오 1: 엣지 케이스 테스트 실행
```bash
npm run test tests/integration/edge-cases.test.ts
```

**예상 결과**: 15개 테스트 모두 PASS ✅

#### 시나리오 2: 커버리지 확인
```bash
npm run test:coverage
```

**예상 결과**: Branch Coverage ≥ 85.0% ✅

#### 시나리오 3: API 에러 응답 확인 (Postman/cURL)
```bash
# 1. 존재하지 않는 프로젝트 조회
curl http://localhost:3000/api/projects/VL-99999999-9999

# 예상 응답:
{
  "error": "Project not found",
  "code": "NOT_FOUND",
  "statusCode": 404
}

# 2. 잘못된 입력값
curl -X POST http://localhost:3000/api/projects \
  -H "Content-Type: application/json" \
  -d '{}'

# 예상 응답:
{
  "error": "project_name is required",
  "code": "VALIDATION_ERROR",
  "statusCode": 400,
  "details": { "field": "project_name" }
}
```

---

## 승인 기준

- ✅ 3개 파일 생성 완료
- ✅ 엣지 케이스 테스트 15개 이상
- ✅ **Branch Coverage ≥ 85.0%** (핵심 목표)
- ✅ API 에러 클래스 5개 정의
- ✅ handleAPIError() 유틸리티 함수
- ✅ 에러 핸들링 가이드 문서 완성
- ✅ TypeScript 타입 체크 통과
- ✅ Next.js 빌드 성공
- ✅ 테스트 실행 성공

**최종 판정**: Verified / Needs Fix

---

**작성자**: Main Agent
**작성일**: 2026-02-23
**버전**: 1.0
