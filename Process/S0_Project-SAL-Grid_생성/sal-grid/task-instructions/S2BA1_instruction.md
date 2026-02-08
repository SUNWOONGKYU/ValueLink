# S2BA1: Valuation Process API & 14-Step Workflow (마이그레이션)

## Task 정보

- **Task ID**: S2BA1
- **Task Name**: 평가 프로세스 API 및 14단계 워크플로우 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase 설정), S1D1 (DB 스키마)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**Valuation_Company의 Python/FastAPI 워크플로우 API를 Next.js TypeScript로 마이그레이션하고 개선**

- 기존 Python 로직을 참고하여 TypeScript로 변환
- 14단계 평가 워크플로우 관리 시스템
- 22개 AI 승인 포인트 시스템
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, UI/UX)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ 입력 검증 및 sanitization (project_id, step_number 등)
- ✅ SQL Injection 방지 (Supabase 파라미터화 쿼리 사용)
- ✅ 인증/인가 체크 강화 (본인 프로젝트만 접근)
- ✅ Rate limiting 고려 (API 남용 방지)
- ✅ CSRF 토큰 (추후 적용)

### 2️⃣ 성능 최적화 (Performance)
- ✅ 불필요한 데이터베이스 쿼리 최소화
- ✅ 데이터 캐싱 전략 (자주 조회되는 워크플로우 단계 정보)
- ✅ 병렬 처리 (여러 승인 포인트 조회 시)
- ✅ 응답 크기 최적화 (필요한 필드만 select)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ ESLint/Prettier 규칙 준수
- ✅ 에러 핸들링 강화 (try-catch, 명확한 에러 메시지)
- ✅ JSDoc 주석으로 함수 문서화
- ✅ 테스트 가능한 구조 (클래스 기반 서비스)

### 4️⃣ API 설계 개선 (API Design)
- ✅ RESTful 원칙 준수
- ✅ 일관된 응답 형식 (success, error, data 구조)
- ✅ 상세한 에러 코드 및 메시지
- ✅ API 버전 관리 준비

---

## 작업 방식

### Step 1: 기존 Python 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/backend/
├── routers/approvals.py (승인 API)
├── models/approval_point.py (승인 포인트 모델)
├── schemas/approval.py (승인 스키마)
└── services/valuation_orchestrator.py (워크플로우 오케스트레이션)
```

**분석 항목:**
1. 14단계 워크플로우 정의
2. 승인 필요 단계 식별
3. 승인 타입 (auto, manual, ai)
4. 단계 진행 로직
5. 에러 처리 방식

### Step 2: Python → TypeScript 변환

**변환 가이드:**

| Python | TypeScript |
|--------|------------|
| `@router.get("/approvals")` | `export async function GET(request: NextRequest)` |
| `async def get_approvals(project_id: str):` | `const projectId = searchParams.get('project_id')` |
| `class ApprovalPoint:` | `export class ApprovalPointManager {` |
| `def __init__(self, project_id: str):` | `constructor(private projectId: string) {}` |
| `supabase.from('approval_points').select('*')` | `supabase.from('approval_points').select('*')` (동일) |
| `return {"data": result}` | `return NextResponse.json({ data: result })` |

**주의사항:**
- Python의 `None` → TypeScript `null`
- Python의 `True/False` → TypeScript `true/false`
- Python의 딕셔너리 → TypeScript 객체 또는 Map
- Python의 리스트 컴프리헨션 → TypeScript `map()`, `filter()`

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```typescript
// ❌ 목업: 에러 처리 부족
const { data } = await supabase.from('approval_points').select('*')
return data

// ✅ 개선: 명확한 에러 처리
const { data, error } = await supabase
  .from('approval_points')
  .select('*')
  .eq('project_id', projectId)

if (error) {
  console.error('Failed to fetch approval points:', error)
  return NextResponse.json(
    { error: 'Failed to fetch approval points', details: error.message },
    { status: 500 }
  )
}

if (!data || data.length === 0) {
  return NextResponse.json(
    { error: 'No approval points found' },
    { status: 404 }
  )
}

return NextResponse.json({ success: true, data })
```

```typescript
// ❌ 목업: 입력 검증 없음
const { project_id } = body

// ✅ 개선: 입력 검증
const { project_id } = body

if (!project_id || typeof project_id !== 'string') {
  return NextResponse.json(
    { error: 'project_id is required and must be a string' },
    { status: 400 }
  )
}

// 프로젝트 ID 형식 검증 (예: PRJ-2026-001)
const projectIdRegex = /^PRJ-\d{4}-\d{3}$/
if (!projectIdRegex.test(project_id)) {
  return NextResponse.json(
    { error: 'Invalid project_id format. Expected: PRJ-YYYY-NNN' },
    { status: 400 }
  )
}
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Server Actions 사용 (필요시)
- Route Handlers (GET, POST)
- Server Components vs Client Components 구분

**TypeScript 타입 안전성:**
```typescript
// ✅ 강력한 타입 정의
export type WorkflowStep = {
  step_number: number
  step_name: string
  description: string
  required_role?: 'customer' | 'accountant' | 'admin'
  approval_required: boolean
}

// ✅ 제네릭 사용
async function fetchFromSupabase<T>(
  table: string,
  projectId: string
): Promise<{ data: T | null; error: Error | null }> {
  // ...
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Supabase 클라이언트 설정 완료
- `lib/supabase/client.ts`, `lib/supabase/server.ts` 존재

**S1D1 완료 확인:**
- `projects` 테이블 존재 (current_step 필드 포함)
- `approval_points` 테이블 존재
- RLS 정책 설정 완료

---

## 생성 파일 (3개)

### 1. lib/workflow/workflow-manager.ts

**목표:** 14단계 워크플로우 관리 클래스

**참고 파일:** `backend/services/valuation_orchestrator.py`

**주요 메서드:**
- `getCurrentStep()`: 현재 단계 조회
- `advanceStep()`: 다음 단계로 진행
- `canAdvanceToStep()`: 진행 가능 여부 확인 (승인 체크 포함)
- `isStepApproved()`: 단계 승인 여부 확인
- `getStepInfo()`: 단계 정보 조회
- `getAllSteps()`: 전체 단계 조회

**개선 사항:**
- ✅ 에러 처리 강화 (프로젝트 미존재 시 명확한 에러)
- ✅ 로깅 추가 (단계 진행 이력)
- ✅ 트랜잭션 고려 (승인 + 단계 진행 원자성)

### 2. lib/workflow/approval-points.ts

**목표:** 승인 포인트 관리 클래스

**참고 파일:** `backend/models/approval_point.py`, `backend/routers/approvals.py`

**주요 메서드:**
- `createApprovalPoint()`: 승인 포인트 생성
- `approveStep()`: 단계 승인
- `rejectStep()`: 승인 취소 (신규 추가)
- `getApprovalHistory()`: 승인 히스토리 조회
- `getPendingApprovals()`: 대기 중인 승인 조회
- `isStepApproved()`: 승인 여부 확인

**개선 사항:**
- ✅ 승인 타입별 검증 로직 (auto는 시스템만, manual은 사용자만)
- ✅ 승인자 권한 확인 (역할별 승인 권한)
- ✅ 중복 승인 방지

### 3. app/api/valuation/route.ts

**목표:** 평가 워크플로우 API 엔드포인트

**참고 파일:** `backend/app/api/v1/endpoints/valuation.py`

**엔드포인트:**
- `GET /api/valuation?project_id=XXX`: 워크플로우 상태 조회
- `POST /api/valuation`: 워크플로우 액션 (advance, approve, reject)

**개선 사항:**
- ✅ 프로젝트 존재 여부 사전 확인
- ✅ 사용자 권한 확인 (본인 프로젝트만 접근)
- ✅ 액션별 명확한 응답 구조
- ✅ 에러 코드 체계화 (400 Bad Request, 403 Forbidden, 404 Not Found, 500 Internal Error)

---

## 완료 기준

### 필수 (Must Have)

- [ ] 목업 Python 파일 읽고 로직 분석 완료
- [ ] 워크플로우 관리자 구현 (14단계)
- [ ] 승인 포인트 관리자 구현 (22개 포인트)
- [ ] API 엔드포인트 구현 (GET, POST)
- [ ] 입력 검증 구현
- [ ] 에러 처리 구현
- [ ] 권한 확인 구현 (RLS)

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] API 호출 시 정상 응답
- [ ] 잘못된 입력 시 400 에러 응답
- [ ] 권한 없는 접근 시 403 에러 응답
- [ ] 워크플로우 단계 진행 동작 확인
- [ ] 승인 로직 동작 확인

### 개선 항목 (Improvement)

- [ ] 보안: 입력 검증, 권한 확인
- [ ] 성능: 불필요한 쿼리 제거
- [ ] 코드 품질: JSDoc 주석, 에러 처리
- [ ] API 설계: 일관된 응답 형식

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/backend/routers/approvals.py`
- `Valuation_Company/valuation-platform/backend/models/approval_point.py`
- `Valuation_Company/valuation-platform/backend/schemas/approval.py`
- `Valuation_Company/valuation-platform/backend/services/valuation_orchestrator.py`

**분석 포인트:**
1. 어떤 API 엔드포인트가 있는가?
2. 14단계 워크플로우는 어떻게 정의되어 있는가?
3. 승인 로직은 어떻게 구현되어 있는가?
4. 에러 처리는 어떻게 되어 있는가? (개선 필요)
5. 보안 취약점은 없는가? (개선 필요)

### 관련 Task

- **S1BI1**: Supabase 설정
- **S1D1**: projects, approval_points 테이블
- **S2F5**: 프로세스 단계 페이지 (API 호출)

---

## 주의사항

### ⚠️ 목업의 한계

1. **목업은 프로토타입이므로 완벽하지 않음**
   - 보안 취약점 있을 수 있음 (입력 검증 부족)
   - 에러 처리 미흡할 수 있음
   - 성능 최적화 안 되어 있을 수 있음

2. **단순 복사 금지**
   - 목업을 그대로 복사하면 문제점까지 가져옴
   - 반드시 개선하면서 마이그레이션

3. **Best Practice 적용**
   - Next.js 14 최신 패턴 사용
   - TypeScript strict mode
   - 보안 강화 (입력 검증, 권한 확인)

### 🔒 보안

1. **RLS 정책 확인**
   - 본인 프로젝트만 조회/수정 가능
   - 역할 기반 승인 권한 확인

2. **입력 검증**
   - project_id, step_number, user_id 필수
   - 형식 검증 (정규식)
   - 타입 검증 (string, number)

3. **SQL Injection 방지**
   - Supabase 파라미터화 쿼리만 사용
   - 직접 문자열 결합 금지

### ⚡ 성능

1. **쿼리 최적화**
   - 필요한 필드만 select
   - 인덱스 활용 (project_id, step_number)

2. **캐싱 고려**
   - WORKFLOW_STEPS는 상수 (메모리 캐시)
   - 자주 조회되는 데이터는 Redis 캐시 고려 (향후)

### 📝 코드 품질

1. **TypeScript strict mode**
   - `tsconfig.json`의 `strict: true`
   - null/undefined 명시적 처리

2. **에러 처리**
   - 모든 async 함수에 try-catch
   - 명확한 에러 메시지
   - 에러 로깅

3. **테스트 가능성**
   - 클래스 기반 구조 (의존성 주입 가능)
   - 순수 함수 활용

---

## 예상 소요 시간

**작업 복잡도**: High
**파일 수**: 3개
**라인 수**: ~500줄 (목업 참조하면서 작성)

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
