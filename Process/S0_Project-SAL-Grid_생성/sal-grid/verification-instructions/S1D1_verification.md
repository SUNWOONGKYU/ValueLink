# S1D1 Verification

## 검증 대상

- **Task ID**: S1D1
- **Task Name**: 데이터베이스 스키마 및 RLS 정책 정의
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: D (Database)

## 검증자

**Verification Agent**: database-specialist

---

## 검증 체크리스트

### 1. 파일 생성 확인

#### 1.1 SQL 파일 존재

- [ ] **`database/schema.sql` 파일 존재**
  - 명령어: `ls database/schema.sql`
  - 파일 크기: ~300줄 예상

- [ ] **`database/rls-policies.sql` 파일 존재**
  - 명령어: `ls database/rls-policies.sql`
  - 파일 크기: ~200줄 예상

- [ ] **`database/triggers.sql` 파일 존재**
  - 명령어: `ls database/triggers.sql`
  - 파일 크기: ~50줄 예상

---

### 2. 데이터베이스 스키마 검증

#### 2.1 12개 테이블 정의 확인

**테이블 목록**:
1. ✅ `users` - 사용자 프로필
2. ✅ `projects` - 프로젝트 마스터
3. ✅ `quotes` - 견적
4. ✅ `negotiations` - 협상
5. ✅ `documents` - 파일 업로드
6. ✅ `approval_points` - 22개 승인 포인트
7. ✅ `valuation_results` - 평가 결과
8. ✅ `drafts` - 초안
9. ✅ `revisions` - 수정 요청
10. ✅ `reports` - 최종 보고서
11. ✅ `investment_tracker` - Deal 뉴스
12. ✅ `feedbacks` - 평가

- [ ] **`database/schema.sql`에서 각 테이블 `CREATE TABLE` 구문 확인**
  - 명령어: `grep "CREATE TABLE" database/schema.sql | wc -l`
  - 출력: `12` (12개 테이블)

#### 2.2 테이블 필수 필드 확인

- [ ] **`users` 테이블 필드**
  - `user_id UUID PRIMARY KEY REFERENCES auth.users`
  - `email TEXT UNIQUE NOT NULL`
  - `role TEXT NOT NULL CHECK (role IN (...))`
  - `created_at`, `updated_at`

- [ ] **`projects` 테이블 필드**
  - `project_id UUID PRIMARY KEY`
  - `user_id UUID REFERENCES users`
  - `accountant_id UUID REFERENCES users`
  - `valuation_method TEXT CHECK (valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax'))`
  - `status TEXT CHECK (status IN (...))`
  - `current_step INT CHECK (current_step BETWEEN 1 AND 14)`

- [ ] **`approval_points` 테이블 필드**
  - `approval_id UUID PRIMARY KEY`
  - `project_id UUID REFERENCES projects`
  - `step_number INT CHECK (step_number BETWEEN 1 AND 22)`
  - `status TEXT CHECK (status IN ('pending', 'approved', 'rejected', 'skipped'))`
  - `UNIQUE(project_id, step_number)` 제약 조건

- [ ] **`valuation_results` 테이블 필드**
  - `result_id UUID PRIMARY KEY`
  - `project_id UUID REFERENCES projects`
  - `valuation_method TEXT CHECK (...)`
  - `enterprise_value DECIMAL(20, 2)`
  - `equity_value DECIMAL(20, 2)`
  - `calculation_data JSONB`

#### 2.3 외래 키 제약 조건 확인

- [ ] **외래 키 ON DELETE 동작 확인**
  - `users.user_id` → `auth.users(id)` : `ON DELETE CASCADE`
  - `projects.user_id` → `users(user_id)` : `ON DELETE CASCADE`
  - `projects.accountant_id` → `users(user_id)` : `ON DELETE SET NULL`
  - `quotes.project_id` → `projects(project_id)` : `ON DELETE CASCADE`

#### 2.4 인덱스 생성 확인

- [ ] **인덱스 생성 구문 확인**
  - 명령어: `grep "CREATE INDEX" database/schema.sql | wc -l`
  - 최소 15개 이상의 인덱스 생성 확인
  - 주요 인덱스:
    - `idx_users_email`
    - `idx_projects_user`
    - `idx_projects_status`
    - `idx_approval_points_project`

---

### 3. RLS 정책 검증

#### 3.1 RLS 활성화 확인

- [ ] **12개 테이블 모두 RLS 활성화**
  - 명령어: `grep "ENABLE ROW LEVEL SECURITY" database/rls-policies.sql | wc -l`
  - 출력: `12` (12개 테이블)

#### 3.2 Users 테이블 정책 확인

- [ ] **"Users can view own profile" 정책 존재**
  - 명령어: `grep "Users can view own profile" database/rls-policies.sql`
  - 정책 내용: `USING (auth.uid() = user_id)`

- [ ] **"Users can update own profile" 정책 존재**
  - 명령어: `grep "Users can update own profile" database/rls-policies.sql`
  - 정책 내용: `USING (auth.uid() = user_id)`

#### 3.3 Projects 테이블 정책 확인

- [ ] **"Users can view own projects" 정책 존재**
  - 정책 내용: `auth.uid() = user_id OR auth.uid() = accountant_id OR role = 'admin'`

- [ ] **"Users can create projects" 정책 존재**
  - 정책 내용: `WITH CHECK (auth.uid() = user_id)`

- [ ] **"Users can update own projects" 정책 존재**
  - 정책 내용: 본인/담당 회계사/관리자만 수정 가능

#### 3.4 Approval Points 테이블 정책 확인

- [ ] **"Accountants and admins can update approval points" 정책 존재**
  - 회계사 또는 관리자만 승인 포인트 업데이트 가능

#### 3.5 Investment Tracker 테이블 정책 확인

- [ ] **"Authenticated users can view investment tracker" 정책 존재**
  - 정책 내용: `TO authenticated USING (true)`
  - 인증된 사용자는 모두 조회 가능

---

### 4. 트리거 검증

#### 4.1 updated_at 트리거 함수 확인

- [ ] **`update_updated_at_column()` 함수 정의**
  - 명령어: `grep "CREATE OR REPLACE FUNCTION update_updated_at_column" database/triggers.sql`
  - 함수 내용: `NEW.updated_at = NOW()`

#### 4.2 각 테이블에 트리거 생성 확인

**트리거 목록** (8개):
1. ✅ `update_users_updated_at`
2. ✅ `update_projects_updated_at`
3. ✅ `update_quotes_updated_at`
4. ✅ `update_negotiations_updated_at`
5. ✅ `update_approval_points_updated_at`
6. ✅ `update_valuation_results_updated_at`
7. ✅ `update_drafts_updated_at`
8. ✅ `update_revisions_updated_at`

- [ ] **8개 트리거 생성 구문 확인**
  - 명령어: `grep "CREATE TRIGGER" database/triggers.sql | wc -l`
  - 출력: `8`

---

### 5. SQL 문법 검증

#### 5.1 PostgreSQL 문법 확인

- [ ] **SQL 파일 문법 에러 없음**
  - 방법 1: Supabase SQL Editor에서 실행 테스트
  - 방법 2: 로컬 PostgreSQL에서 실행 테스트
  - 방법 3: SQL Linter 도구 사용

#### 5.2 데이터 타입 적절성 확인

- [ ] **UUID 타입 사용 확인**
  - Primary Key는 `UUID`
  - 외래 키도 `UUID`

- [ ] **DECIMAL 타입 정밀도 확인**
  - 금액 필드: `DECIMAL(12, 2)` (9,999억원까지)
  - 기업가치: `DECIMAL(20, 2)` (더 큰 금액)

- [ ] **JSONB 타입 사용 확인**
  - `valuation_results.calculation_data JSONB`

- [ ] **CHECK 제약 조건 확인**
  - `role IN ('customer', 'accountant', 'admin', 'investor', 'partner', 'supporter')`
  - `valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax')`
  - `current_step BETWEEN 1 AND 14`

---

### 6. 통합 테스트 (Supabase 연결 시)

#### 6.1 테이블 생성 확인

- [ ] **Supabase SQL Editor에서 `schema.sql` 실행**
  - 에러 없이 실행 완료
  - 명령어: `SELECT * FROM information_schema.tables WHERE table_schema = 'public'`
  - 12개 테이블 조회 확인

#### 6.2 RLS 정책 적용 확인

- [ ] **Supabase SQL Editor에서 `rls-policies.sql` 실행**
  - 에러 없이 실행 완료
  - 명령어: `SELECT * FROM pg_policies WHERE schemaname = 'public'`
  - RLS 정책 조회 확인

#### 6.3 트리거 적용 확인

- [ ] **Supabase SQL Editor에서 `triggers.sql` 실행**
  - 에러 없이 실행 완료
  - 명령어: `SELECT * FROM pg_trigger WHERE tgname LIKE 'update_%'`
  - 8개 트리거 조회 확인

#### 6.4 실제 작동 테스트

- [ ] **테스트 데이터 삽입**
  ```sql
  INSERT INTO public.users (user_id, email, full_name, role)
  VALUES (gen_random_uuid(), 'test@example.com', 'Test User', 'customer')
  ```

- [ ] **RLS 정책 작동 확인**
  - 본인 데이터만 조회되는지 확인
  - 다른 사용자 데이터 접근 차단 확인

- [ ] **트리거 작동 확인**
  - UPDATE 실행 후 `updated_at` 자동 갱신 확인
  ```sql
  UPDATE public.users SET full_name = 'Updated Name' WHERE user_id = ...
  SELECT updated_at FROM public.users WHERE user_id = ...
  ```

---

### 7. Blocker 확인

#### 7.1 의존성 차단

- [ ] **S1D1은 선행 Task 없음**
  - 독립적으로 완료 가능

#### 7.2 환경 차단

- [ ] **Supabase 프로젝트 생성 필요 (알림)**
  - Supabase 대시보드에서 프로젝트 생성
  - SQL Editor 접속 가능 확인

- [ ] **PostgreSQL 15 버전 확인**
  - Supabase는 PostgreSQL 15 사용
  - 로컬 테스트 시 동일 버전 권장

#### 7.3 외부 API 차단

- [ ] **외부 API 호출 없음**
  - SQL 파일만 실행하므로 외부 의존성 없음

---

### 8. 데이터 모델 일관성 확인

#### 8.1 외래 키 순환 참조 없음

- [ ] **외래 키 의존성 그래프 검증**
  - 순환 참조 없음 확인
  - `auth.users` → `users` → `projects` → `quotes` → ... (단방향)

#### 8.2 필수 필드 누락 없음

- [ ] **모든 테이블에 `created_at` 필드 존재**
  - 명령어: `grep "created_at TIMESTAMP" database/schema.sql | wc -l`
  - 12개 테이블 모두 포함

- [ ] **필요한 테이블에 `updated_at` 필드 존재**
  - 명령어: `grep "updated_at TIMESTAMP" database/schema.sql | wc -l`
  - 8개 테이블 포함 (트리거 대상)

---

## 합격 기준

### 필수 (Must Pass)

1. **12개 테이블 모두 정의 완료** ✅
   - `CREATE TABLE` 구문 12개 확인

2. **모든 테이블에 RLS 정책 적용** ✅
   - `ENABLE ROW LEVEL SECURITY` 12개 확인
   - 각 테이블별 SELECT/INSERT/UPDATE 정책 확인

3. **8개 트리거 생성 완료** ✅
   - `update_updated_at_column()` 함수 정의
   - 8개 트리거 생성 확인

4. **SQL 문법 에러 없음** ✅
   - PostgreSQL 실행 시 에러 없음

5. **외래 키 제약 조건 올바름** ✅
   - ON DELETE CASCADE/SET NULL 적절히 사용

6. **인덱스 생성 완료** ✅
   - 최소 15개 이상 인덱스 생성

### 권장 (Nice to Pass)

1. **실제 Supabase에서 테스트 완료** ✨
   - SQL 파일 실행 성공
   - 테이블 생성 확인

2. **RLS 정책 실제 작동 테스트** ✨
   - 본인 데이터만 조회 확인
   - 권한 없는 데이터 접근 차단 확인

3. **트리거 실제 작동 테스트** ✨
   - UPDATE 후 `updated_at` 자동 갱신 확인

---

## 검증 결과

### Pass/Fail

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

### 발견 사항

#### 🟢 통과 항목

- (통과한 항목 나열)

#### 🔴 실패 항목

- (실패한 항목 나열 및 수정 필요 사항)

#### 🟡 경고 사항

- (경고 또는 개선 권장 사항)

---

## 주의사항

1. **외래 키 순서**
   - `users` 테이블을 먼저 생성 (다른 테이블에서 참조)
   - `auth.users`는 Supabase Auth가 자동 생성

2. **RLS 정책 테스트**
   - 반드시 실제 Supabase에서 테스트
   - 각 역할(customer, accountant, admin)별로 접근 권한 테스트

3. **JSONB 필드**
   - `calculation_data` 필드는 평가 계산 상세 데이터 저장
   - 인덱싱 필요 시 GIN 인덱스 추가 고려

4. **Decimal 정밀도**
   - 금액 필드는 DECIMAL(12, 2) 사용 (9,999억원까지)
   - 기업가치는 DECIMAL(20, 2) 사용 (더 큰 금액 지원)

5. **트리거 성능**
   - `updated_at` 트리거는 가벼움 (성능 이슈 없음)
   - 대량 UPDATE 시에도 안전

---

## 참조

- Task Instruction: `task-instructions/S1D1_instruction.md`
- Supabase RLS 가이드: https://supabase.com/docs/guides/auth/row-level-security
- PostgreSQL Triggers: https://www.postgresql.org/docs/current/triggers.html

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
