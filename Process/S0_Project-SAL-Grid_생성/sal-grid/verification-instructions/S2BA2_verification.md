# S2BA2 Verification

## 검증 대상

- **Task ID**: S2BA2
- **Task Name**: 프로젝트 및 견적 API
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

- [ ] **`app/api/projects/route.ts` 존재** - 프로젝트 CRUD API
- [ ] **`app/api/quotes/route.ts` 존재** - 견적 API
- [ ] **`app/api/negotiations/route.ts` 존재** - 협상 API

---

### 3. 핵심 기능 테스트

#### 3.1 Projects API

- [ ] **GET /api/projects**
  - 본인 프로젝트 목록 조회
  - status 필터링 (선택 사항)
  - 인증 확인 (401 Unauthorized)

- [ ] **POST /api/projects**
  - 프로젝트 생성
  - 필수 필드: `project_name`, `valuation_method`
  - `status: 'pending'`, `current_step: 1` 자동 설정
  - 201 Created 응답

- [ ] **PUT /api/projects**
  - 프로젝트 수정
  - 본인 프로젝트만 수정 가능
  - `updated_at` 자동 업데이트

#### 3.2 Quotes API

- [ ] **POST /api/quotes**
  - 견적 생성
  - 필수 필드: `project_id`, `amount`
  - `deposit_amount` 기본값: amount / 2
  - `balance_amount` 자동 계산
  - `delivery_days` 기본값: 10일
  - 201 Created 응답

#### 3.3 Negotiations API

- [ ] **POST /api/negotiations**
  - 협상 제안 생성
  - 필수 필드: `quote_id`, `negotiation_type`
  - `status: 'pending'` 자동 설정
  - 201 Created 응답

---

### 4. 통합 테스트

- [ ] **S1BI1 (Supabase) 의존성 충족**
- [ ] **S1D1 (Database) 의존성 충족** - projects, quotes, negotiations 테이블
- [ ] **RLS 보안** - 본인 프로젝트만 조회/수정

---

### 5. Blocker 확인

- [ ] **Supabase 클라이언트 설정** 완료
- [ ] **테이블 접근** 가능

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **모든 파일 생성 완료** ✅ (3개 파일)
3. **프로젝트 CRUD API 동작** ✅
4. **견적/협상 API 동작** ✅
5. **RLS 보안 적용** ✅

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **RLS 보안** - 본인 프로젝트만 접근
2. **에러 핸들링** - 명확한 에러 메시지
3. **인증 확인** - user_id 기반 필터링

---

## 참조

- Task Instruction: `task-instructions/S2BA2_instruction.md`

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
