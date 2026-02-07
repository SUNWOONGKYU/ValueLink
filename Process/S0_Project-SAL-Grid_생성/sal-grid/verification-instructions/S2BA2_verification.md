# S2BA2 Verification

## 검증 대상

- **Task ID**: S2BA2
- **Task Name**: 프로젝트 및 평가 요청 API
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

- [ ] **`app/api/evaluation-requests/route.ts` 존재** - 평가 요청 CRUD + 승인/거절 API
- [ ] **`app/api/projects/route.ts` 존재** - 프로젝트 조회/업데이트 API
- [ ] **`app/api/project-history/route.ts` 존재** - 완료 프로젝트 조회 + 아카이브 API

---

### 3. 핵심 기능 테스트

#### 3.1 Evaluation Requests API

- [ ] **GET /api/evaluation-requests**
  - 고객: 본인 요청만 조회
  - 관리자: 전체 요청 조회
  - status 필터링 (선택 사항)
  - 인증 확인 (401 Unauthorized)

- [ ] **POST /api/evaluation-requests**
  - 평가 요청 생성 (고객)
  - 필수 필드: `company_name`, `valuation_method`
  - 선택 필드: `company_name_en`, `company_website`, `address`, `phone`, `fax`, `requirements`, `budget_min`, `budget_max`
  - `status: 'pending'` 자동 설정
  - 201 Created 응답

- [ ] **PUT /api/evaluation-requests**
  - 평가 요청 승인/거절 (관리자)
  - 필수 필드: `request_id`, `action` (approve/reject)
  - 승인 시: `accountant_id` 지정, `projects` 테이블에 자동 생성
  - 거절 시: `rejection_reason` 기록
  - 관리자 권한 확인 (403 Forbidden)

#### 3.2 Projects API

- [ ] **GET /api/projects**
  - 고객: 본인 프로젝트만 조회
  - 회계사: 담당 프로젝트만 조회
  - 관리자: 전체 프로젝트 조회
  - status 필터링 (선택 사항)
  - accountants 관계 조인 포함

- [ ] **PUT /api/projects**
  - 프로젝트 상태/단계 업데이트
  - 필수 필드: `project_id`
  - `updated_at` 자동 업데이트

#### 3.3 Project History API

- [ ] **GET /api/project-history**
  - 역할별 필터링 (고객/회계사/관리자)
  - year 필터링 (선택 사항)
  - `completed_at` 기준 내림차순 정렬

- [ ] **POST /api/project-history**
  - 프로젝트 완료 → 히스토리 이동
  - 필수 필드: `project_id`
  - 선택 필드: `final_amount`
  - 원본 프로젝트 데이터 복사
  - 원본 `projects.status` → 'completed' 변경
  - 201 Created 응답

---

### 4. 통합 테스트

- [ ] **S1BI1 (Supabase) 의존성 충족**
- [ ] **S1D1 (Database) 의존성 충족** - evaluation_requests, projects, project_history 테이블
- [ ] **RLS 보안** - 역할별 접근 제어

---

### 5. 3단계 라이프사이클 테스트

```
1. 고객 → 평가 요청 생성 (evaluation_requests.status = 'pending')
2. 관리자 → 요청 승인 (projects 테이블에 생성)
3. 워크플로우 진행 (projects.current_step 업데이트)
4. 프로젝트 완료 → 히스토리 이동 (project_history에 아카이브)
```

- [ ] 단계 1→2 전환 확인
- [ ] 단계 3 진행 확인
- [ ] 단계 4 완료 확인

---

### 6. Blocker 확인

- [ ] **Supabase 클라이언트 설정** 완료
- [ ] **테이블 접근** 가능 (evaluation_requests, projects, project_history)
- [ ] **사용자 역할** 확인 가능 (users.role)

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (3개 파일)
3. **평가 요청 API 동작** ✅ (생성, 승인/거절)
4. **프로젝트 API 동작** ✅ (조회, 업데이트)
5. **히스토리 API 동작** ✅ (조회, 아카이브)
6. **RLS 보안 적용** ✅
7. **역할별 접근 제어** ✅ (customer/accountant/admin)

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **RLS 보안** - 역할별 접근 제어 철저
2. **에러 핸들링** - 명확한 에러 메시지
3. **인증 확인** - user_id, role 기반 필터링
4. **데이터 일관성** - 승인 시 evaluation_requests → projects 데이터 정확히 복사
5. **아카이브 무결성** - project_history에 완료 데이터 정확히 보존

---

## 참조

- Task Instruction: `task-instructions/S2BA2_instruction.md`
- Database Schema: `database/schema-v4-final.sql`

---

**작성일**: 2026-02-07
**수정일**: 2026-02-07 (v4 스키마 반영: quotes/negotiations 삭제, 3단계 라이프사이클 적용)
**작성자**: Claude Code
