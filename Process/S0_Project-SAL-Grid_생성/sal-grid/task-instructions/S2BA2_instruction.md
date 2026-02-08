# S2BA2: Projects & Evaluation Requests API (마이그레이션)

## Task 정보

- **Task ID**: S2BA2
- **Task Name**: 프로젝트 및 평가 요청 API 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (Supabase 설정), S1D1 (DB 스키마)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**Valuation_Company의 Python/FastAPI 프로젝트 관리 API를 Next.js TypeScript로 마이그레이션하고 개선**

- 기존 Python 로직을 참고하여 TypeScript로 변환
- 3단계 프로젝트 라이프사이클 API 관리 (evaluation_requests → projects → project_history)
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, API 설계)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ 입력 검증 및 sanitization (request_id, project_id 등)
- ✅ SQL Injection 방지 (Supabase 파라미터화 쿼리 사용)
- ✅ 인증/인가 체크 강화 (본인 프로젝트만 접근, 관리자 권한 확인)
- ✅ Rate limiting 고려 (API 남용 방지)

### 2️⃣ 성능 최적화 (Performance)
- ✅ 불필요한 데이터베이스 쿼리 최소화
- ✅ 필요한 필드만 select (*)
- ✅ 인덱스 활용 (project_id, user_id)
- ✅ 트랜잭션 처리 (승인 시 evaluation_requests + projects 원자성)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ ESLint/Prettier 규칙 준수
- ✅ 에러 핸들링 강화 (try-catch, 명확한 에러 메시지)
- ✅ JSDoc 주석으로 함수 문서화
- ✅ 테스트 가능한 구조

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
├── routers/projects.py (프로젝트 API)
├── routers/evaluation_requests.py (평가 요청 API)
├── models/project.py (프로젝트 모델)
└── services/lifecycle_manager.py (라이프사이클 관리)
```

**분석 항목:**
1. evaluation_requests 생성/승인/거절 로직
2. projects 조회/업데이트 로직
3. project_history 이동 로직
4. 에러 처리 방식
5. 권한 체크 방식

### Step 2: Python → TypeScript 변환

**변환 가이드:**

| Python | TypeScript |
|--------|------------|
| `@router.post("/evaluation-requests")` | `export async function POST(request: NextRequest)` |
| `async def create_request(data: dict):` | `const body = await request.json()` |
| `if not project_id:` | `if (!project_id) { return NextResponse.json(...) }` |
| `return {"data": result}` | `return NextResponse.json({ data: result })` |

**주의사항:**
- Python의 `None` → TypeScript `null`
- Python의 딕셔너리 → TypeScript 객체
- Python의 에러 처리 → TypeScript try-catch

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```typescript
// ❌ 목업: 승인 시 트랜잭션 없음 (중간 실패 시 데이터 불일치)
const { data: project } = await supabase.from('projects').insert(...)
const { error } = await supabase.from('evaluation_requests').update(...)

// ✅ 개선: 트랜잭션 처리 또는 롤백 로직
try {
  const { data: project, error: projectError } = await supabase
    .from('projects')
    .insert({ ...requestData, status: 'in_progress' })
    .select()
    .single()

  if (projectError) {
    throw new Error(`프로젝트 생성 실패: ${projectError.message}`)
  }

  const { error: updateError } = await supabase
    .from('evaluation_requests')
    .update({ status: 'approved', approved_at: new Date().toISOString() })
    .eq('request_id', request_id)

  if (updateError) {
    // 롤백 필요: project 삭제
    await supabase.from('projects').delete().eq('project_id', project.project_id)
    throw new Error(`요청 승인 업데이트 실패: ${updateError.message}`)
  }

  return NextResponse.json({ success: true, project })
} catch (error) {
  console.error('승인 처리 실패:', error)
  return NextResponse.json(
    { error: '승인 처리에 실패했습니다.', details: error.message },
    { status: 500 }
  )
}
```

```typescript
// ❌ 목업: 관리자 권한 체크 누락
const { data } = await supabase.from('evaluation_requests').update(...)

// ✅ 개선: 역할 기반 권한 체크
const { data: { user } } = await supabase.auth.getUser()
if (!user) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
}

const { data: userData } = await supabase
  .from('users')
  .select('role')
  .eq('id', user.id)
  .single()

if (userData?.role !== 'admin') {
  return NextResponse.json(
    { error: 'Admin access required' },
    { status: 403 }
  )
}
```

### Step 4: Best Practice 적용

**Next.js 14 App Router 패턴:**
- Route Handlers (GET, POST, PUT)
- 파라미터 검증
- 일관된 응답 형식

**TypeScript 타입 안전성:**
```typescript
// ✅ 강력한 타입 정의
export type EvaluationRequestStatus = 'pending' | 'approved' | 'rejected'

export interface EvaluationRequest {
  request_id: string
  user_id: string
  company_name: string
  valuation_method: 'dcf' | 'relative' | 'asset' | 'intrinsic' | 'tax'
  status: EvaluationRequestStatus
  created_at: string
  approved_at?: string
  approved_by?: string
  rejection_reason?: string
}

// ✅ 제네릭 사용
async function updateRequest<T extends Partial<EvaluationRequest>>(
  requestId: string,
  updates: T
): Promise<{ data: EvaluationRequest | null; error: Error | null }> {
  // ...
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Supabase 클라이언트 설정 완료
- `lib/supabase/client.ts`, `lib/supabase/server.ts` 존재

**S1D1 완료 확인:**
- `evaluation_requests`, `projects`, `project_history` 테이블 존재
- RLS 정책 설정 완료

---

## 생성 파일 (3개)

### 1. app/api/evaluation-requests/route.ts

**목표:** 평가 요청 CRUD + 승인/거절 API

**참고 파일:** `backend/routers/evaluation_requests.py`

**주요 엔드포인트:**
- `GET`: 평가 요청 목록 조회 (역할별 필터링)
- `POST`: 평가 요청 생성 (고객)
- `PUT`: 승인/거절 (관리자)

**개선 사항:**
- ✅ 입력 검증 (company_name, valuation_method 필수)
- ✅ 역할 기반 접근 제어 (고객: 본인 요청만, 관리자: 전체)
- ✅ 승인 시 트랜잭션 처리
- ✅ 명확한 에러 메시지

### 2. app/api/projects/route.ts

**목표:** 프로젝트 조회/업데이트 API

**참고 파일:** `backend/routers/projects.py`

**주요 엔드포인트:**
- `GET`: 프로젝트 목록 조회 (역할별 필터링)
- `PUT`: 프로젝트 상태/단계 업데이트

**개선 사항:**
- ✅ 역할별 필터링 (customer, accountant, admin)
- ✅ 단계 진행 검증 (순차 진행 확인)
- ✅ Accountants 테이블 조인 (담당 회계사 정보)

### 3. app/api/project-history/route.ts

**목표:** 완료된 프로젝트 히스토리 관리

**참고 파일:** `backend/routers/project_history.py`

**주요 엔드포인트:**
- `GET`: 히스토리 조회 (연도별 필터)
- `POST`: 프로젝트 완료 → 히스토리 이동

**개선 사항:**
- ✅ 완료 여부 확인 (current_step = 14)
- ✅ 데이터 무결성 보장 (projects 상태 변경)
- ✅ 연도별 필터링

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 Python 파일 읽고 로직 분석 완료
- [ ] 3개 API 엔드포인트 구현 (evaluation-requests, projects, project-history)
- [ ] 입력 검증 구현
- [ ] 에러 처리 구현
- [ ] 권한 확인 구현 (RLS)
- [ ] 3단계 라이프사이클 동작 확인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] API 호출 시 정상 응답
- [ ] 역할별 접근 제어 확인
- [ ] 승인 → 프로젝트 생성 플로우 동작 확인

### 개선 항목 (Improvement)
- [ ] 보안: 입력 검증, 권한 확인, 트랜잭션
- [ ] 성능: 불필요한 쿼리 제거, 필드 최적화
- [ ] 코드 품질: JSDoc 주석, 에러 처리
- [ ] API 설계: 일관된 응답 형식

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/backend/routers/projects.py`
- `Valuation_Company/valuation-platform/backend/routers/evaluation_requests.py`
- `Valuation_Company/valuation-platform/backend/models/project.py`

**분석 포인트:**
1. 어떤 API 엔드포인트가 있는가?
2. 3단계 라이프사이클은 어떻게 구현되어 있는가?
3. 승인/거절 로직은 어떻게 되어 있는가?
4. 에러 처리는 어떻게 되어 있는가? (개선 필요)
5. 보안 취약점은 없는가? (개선 필요)

### 관련 Task
- **S1BI1**: Supabase 설정
- **S1D1**: evaluation_requests, projects, project_history 테이블
- **S2F6**: 프로젝트 관리 페이지 (API 호출)

---

## 주의사항

### ⚠️ 목업의 한계

1. **목업은 프로토타입이므로 완벽하지 않음**
   - 트랜잭션 처리 부족
   - 에러 핸들링 미흡
   - 권한 체크 불완전

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
   - 관리자만 승인/거절 가능

2. **입력 검증**
   - request_id, project_id 필수
   - company_name, valuation_method 형식 검증

3. **SQL Injection 방지**
   - Supabase 파라미터화 쿼리만 사용
   - 직접 문자열 결합 금지

### ⚡ 성능

1. **쿼리 최적화**
   - 필요한 필드만 select
   - 인덱스 활용 (project_id, user_id)

2. **트랜잭션 고려**
   - 승인 시 evaluation_requests + projects 원자성
   - 롤백 로직 구현

### 📝 코드 품질

1. **TypeScript strict mode**
   - `tsconfig.json`의 `strict: true`
   - null/undefined 명시적 처리

2. **에러 처리**
   - 모든 async 함수에 try-catch
   - 명확한 에러 메시지
   - 에러 로깅

---

## 예상 소요 시간

**작업 복잡도**: Medium-High
**파일 수**: 3개
**라인 수**: ~400줄 (목업 참조하면서 작성)

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
