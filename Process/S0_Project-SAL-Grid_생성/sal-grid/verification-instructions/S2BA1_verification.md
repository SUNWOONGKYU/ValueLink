# S2BA1 Verification

## 검증 대상

- **Task ID**: S2BA1
- **Task Name**: 평가 프로세스 API 및 14단계 워크플로우
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

- [ ] **`lib/workflow/workflow-manager.ts` 존재**
  - `WorkflowManager` 클래스 export
  - `WORKFLOW_STEPS` 배열 (14개 단계) export

- [ ] **`lib/workflow/approval-points.ts` 존재**
  - `ApprovalPointManager` 클래스 export

- [ ] **`app/api/valuation/route.ts` 존재**
  - `GET` 핸들러 export
  - `POST` 핸들러 export

---

### 3. 핵심 기능 테스트

#### 3.1 WorkflowManager 클래스

- [ ] **getCurrentStep() 메서드**
  - Supabase에서 프로젝트의 current_step 조회
  - 기본값 1 반환

- [ ] **advanceStep() 메서드**
  - current_step + 1로 업데이트
  - 14단계 초과 방지
  - `{ success: boolean, nextStep: number }` 반환

- [ ] **canAdvanceToStep() 메서드**
  - 순차 진행만 허용 (건너뛰기 불가)
  - 승인 필요 단계는 승인 확인

- [ ] **isStepApproved() 메서드**
  - `approval_points` 테이블에서 승인 여부 확인

- [ ] **getStepInfo() 메서드**
  - 특정 단계 정보 반환

- [ ] **getAllSteps() 메서드**
  - 14개 전체 단계 정보 반환

#### 3.2 ApprovalPointManager 클래스

- [ ] **createApprovalPoint() 메서드**
  - `approval_points` 테이블에 새 레코드 삽입
  - `approval_type`: 'auto', 'manual', 'ai'

- [ ] **approveStep() 메서드**
  - 기존 승인 포인트 업데이트 또는 새로 생성
  - `approved: true` 설정

- [ ] **getApprovalHistory() 메서드**
  - 프로젝트의 승인 이력 조회
  - 특정 단계 필터링 가능

- [ ] **getPendingApprovals() 메서드**
  - `approved: false`인 승인 포인트 조회

- [ ] **isStepApproved() 메서드**
  - 최신 승인 레코드 확인

#### 3.3 API 엔드포인트 (GET /api/valuation)

- [ ] **현재 워크플로우 상태 조회**
  - Query Parameter: `project_id`
  - 응답 필드:
    - `current_step`: 현재 단계 번호
    - `current_step_info`: 현재 단계 정보
    - `all_steps`: 전체 14개 단계
    - `pending_approvals`: 대기 중인 승인

- [ ] **에러 처리**
  - `project_id` 누락 시 400 에러
  - 서버 에러 시 500 에러

#### 3.4 API 엔드포인트 (POST /api/valuation)

- [ ] **action: 'advance'**
  - 다음 단계로 진행
  - 승인 확인 후 진행
  - 응답: `{ success, next_step }`

- [ ] **action: 'approve'**
  - 특정 단계 승인
  - 필수 필드: `step_number`, `user_id`
  - 응답: `{ success, step_number, approved }`

- [ ] **action: 'create_approval_point'**
  - 새 승인 포인트 생성
  - 필수 필드: `step_number`, `approval_type`
  - 응답: `{ success, approval_point }`

- [ ] **에러 처리**
  - 필수 필드 누락 시 400 에러
  - 잘못된 action 시 400 에러

---

### 4. 통합 테스트

#### 4.1 선행 Task 호환

- [ ] **S1BI1 (Supabase 설정) 의존성 충족**
  - `@/lib/supabase/server` import 가능

- [ ] **S1D1 (Database Schema) 의존성 충족**
  - `projects` 테이블 존재
  - `approval_points` 테이블 존재

#### 4.2 후행 Task 준비

- [ ] **S2F5 (프로세스 단계 페이지) 연결 준비**
  - 프론트엔드에서 API 호출 가능

#### 4.3 데이터 흐름 검증

- [ ] **워크플로우 진행 시나리오**
  1. 프로젝트 생성 (current_step: 1)
  2. 다음 단계 진행 (POST /api/valuation action=advance)
  3. current_step 2로 업데이트 확인
  4. 승인 필요 단계 도달
  5. 승인 생성 (POST action=approve)
  6. 승인 완료 후 다음 단계 진행 가능

---

### 5. Blocker 확인

- [ ] **S1BI1 완료 확인** - Supabase 클라이언트
- [ ] **S1D1 완료 확인** - projects, approval_points 테이블
- [ ] **Supabase 연결** - 테이블 접근 가능

---

### 6. 로직 검증

#### 6.1 14단계 정의 확인

- [ ] **WORKFLOW_STEPS 배열**
  - 14개 단계 모두 정의
  - 각 단계마다 `step_number`, `step_name`, `description` 필드
  - 승인 필요 단계 `approval_required: true` 설정

#### 6.2 순차 진행 로직

- [ ] **건너뛰기 방지**
  - 현재 단계 + 1로만 진행 가능
  - 2 → 4로 직접 진행 불가

#### 6.3 승인 로직

- [ ] **승인 필요 단계 확인**
  - `approval_required: true`인 단계만 승인 확인
  - 승인 없이 다음 단계 진행 불가

#### 6.4 RLS 보안

- [ ] **본인 프로젝트만 조회/수정**
  - user_id 기반 필터링

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (3개 파일)
3. **WorkflowManager 클래스 구현** ✅
4. **ApprovalPointManager 클래스 구현** ✅
5. **API 엔드포인트 구현** ✅
6. **워크플로우 진행 로직 동작** ✅

### 권장 (Nice to Pass)

1. **롤백 기능** ✨
2. **단계 건너뛰기 (관리자 전용)** ✨
3. **알림 발송 연동** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

---

## 주의사항

1. **단계 순서**
   - 반드시 순서대로 진행 (건너뛰기 불가)
   - 이전 단계 완료 확인 필수

2. **승인 로직**
   - 승인이 필요한 단계만 approval_points 생성
   - 승인 완료 후 다음 단계 진행 가능

3. **RLS 보안**
   - 본인 프로젝트만 조회/수정
   - 역할 기반 승인 권한 확인

4. **에러 처리**
   - 명확한 에러 메시지
   - 트랜잭션 고려 (향후)

---

## 참조

- Task Instruction: `task-instructions/S2BA1_instruction.md`
- 기존 프로토타입: `Valuation_Company/valuation-platform/backend/app/services/valuation_orchestrator.py`

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
