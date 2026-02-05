# S5T1 Verification

## 검증 대상

- **Task ID**: S5T1
- **Task Name**: 테스팅 & QA
- **Stage**: S5 (개발 마무리)
- **Area**: T (Testing)

## 검증자

**Verification Agent**: qa-specialist

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)
- [ ] **테스트 파일 문법 검증** (Jest 설정 확인)

---

### 2. 파일 생성 확인

- [ ] **`tests/integration/valuation-workflow.test.ts` 존재** - 통합 테스트
- [ ] **`tests/e2e/user-journey.test.ts` 존재** - E2E 테스트
- [ ] **`docs/test-report.md` 존재** - 테스트 리포트
- [ ] **`jest.config.js` 존재** (또는 `jest.config.ts`)
- [ ] **`playwright.config.ts` 존재**

---

### 3. 핵심 기능 테스트

#### 3.1 통합 테스트 (`valuation-workflow.test.ts`)

**테스트 구조:**
- [ ] **describe 블록**: `'Valuation Workflow Integration Tests'`
- [ ] **beforeAll**: Supabase 클라이언트 초기화, 테스트 데이터 생성
- [ ] **afterAll**: 테스트 데이터 정리

**Step 1-3: 프로젝트 생성 및 견적**
- [ ] **프로젝트 생성 테스트**
  - `projects` 테이블에 INSERT
  - customer_id, company_name, valuation_method, status 검증

- [ ] **견적 생성 테스트**
  - `quotes` 테이블에 INSERT
  - project_id, amount, status 검증

- [ ] **협상 테스트**
  - `negotiations` 테이블에 INSERT
  - quote_id, status 검증

**Step 4-6: 문서 업로드 및 검토**
- [ ] **문서 업로드 테스트**
  - Supabase Storage 업로드
  - `documents` 테이블에 INSERT
  - file_path, document_type 검증

- [ ] **AI 승인 테스트**
  - `approval_points` 테이블에 INSERT
  - approval_type, status 검증

**Step 7-9: 데이터 입력 및 가정**
- [ ] **재무 데이터 입력 테스트**
  - JSON 형식 검증
  - 필수 필드 존재 확인

- [ ] **가정 입력 테스트**
  - WACC 컴포넌트 검증
  - Projection 데이터 검증

**Step 10: DCF 평가 엔진 실행**
- [ ] **평가 실행 테스트**
  - `orchestrator.executeValuation()` 호출
  - method: 'dcf' 검증
  - equity_value > 0 검증
  - value_per_share 정수 검증

- [ ] **결과 저장 테스트**
  - `valuation_results` 테이블에 INSERT
  - project_id, method, equity_value 검증

**Step 11: 민감도 분석**
- [ ] **민감도 분석 테스트**
  - WACC x Growth Rate 2D 배열 생성
  - 5x5 행렬 검증

**Step 12-13: 초안 생성 및 검토**
- [ ] **초안 생성 테스트**
  - `drafts` 테이블에 INSERT
  - content, version 검증

- [ ] **수정 요청 테스트**
  - `revisions` 테이블에 INSERT
  - draft_id, customer_comments 검증

**Step 14: 최종 보고서 생성**
- [ ] **보고서 생성 테스트**
  - `reports` 테이블에 INSERT
  - file_path, status 검증

- [ ] **프로젝트 완료 테스트**
  - `projects.status = 'completed'` 업데이트
  - completed_at 필드 검증

**전체 워크플로우 테스트:**
- [ ] **14단계 모두 순차 실행**
- [ ] **각 단계 성공 확인**
- [ ] **데이터 일관성 검증**

#### 3.2 E2E 테스트 (`user-journey.test.ts`)

**테스트 구조:**
- [ ] **beforeAll**: 브라우저 실행
- [ ] **afterAll**: 브라우저 종료

**Journey 1: 고객 여정 (Customer Journey)**
- [ ] **로그인**
  - `/login` 페이지 접속
  - 이메일/비밀번호 입력
  - 로그인 성공 확인

- [ ] **프로젝트 생성**
  - `/projects/create` 페이지 접속
  - 회사명, 평가 방법 입력
  - 제출 성공 확인

- [ ] **견적 확인**
  - 견적서 페이지 표시 확인
  - 금액 표시 확인

- [ ] **문서 업로드**
  - 파일 선택 (재무제표, 사업계획서)
  - 업로드 성공 확인

- [ ] **초안 검토**
  - 초안 페이지 표시 확인
  - 수정 요청 버튼 클릭

**Journey 2: 회계사 여정 (Accountant Journey)**
- [ ] **로그인**
  - 회계사 계정으로 로그인

- [ ] **프로젝트 검토**
  - 배정된 프로젝트 목록 확인
  - 프로젝트 상세 페이지 접속

- [ ] **평가 실행**
  - 재무 데이터 입력
  - DCF 평가 실행
  - 결과 확인 (equity_value, value_per_share)

- [ ] **초안 작성**
  - 초안 편집기 접속
  - 텍스트 입력
  - 저장 성공 확인

**Journey 3: 관리자 여정 (Admin Journey)**
- [ ] **로그인**
  - 관리자 계정으로 로그인

- [ ] **대시보드 접속**
  - 전체 프로젝트 현황 확인
  - 통계 표시 확인 (총 프로젝트 수, 완료율)

- [ ] **사용자 관리**
  - 사용자 목록 확인
  - 역할 변경 테스트

**브라우저 호환성:**
- [ ] **Chromium 테스트 성공**
- [ ] **Firefox 테스트 성공** (선택)
- [ ] **WebKit 테스트 성공** (선택)

#### 3.3 테스트 리포트 (`test-report.md`)

**섹션 구성:**
- [ ] **개요**
  - 테스트 날짜
  - 테스트 환경
  - 테스트 범위

- [ ] **테스트 결과 요약**
  - 총 테스트 수: 21개 (18 통합 + 3 E2E)
  - 통과: 21개
  - 실패: 0개
  - 통과율: 100%

- [ ] **커버리지 상세**
  - Statements: 87%
  - Branches: 82%
  - Functions: 86%
  - Lines: 85%
  - 테이블: 파일별 커버리지

- [ ] **통합 테스트 결과**
  - 18개 테스트 케이스 나열
  - 각 테스트 실행 시간
  - 성공/실패 상태

- [ ] **E2E 테스트 결과**
  - 3개 Journey 나열
  - 스크린샷 (선택)
  - 실행 시간

- [ ] **성능 메트릭**
  - Page Load Time: < 3초
  - API Response Time: < 1초
  - DCF Calculation: < 5초
  - Crawler Execution: < 60초

- [ ] **알려진 이슈**
  - 발견된 버그 목록 (0개면 "없음")
  - 제한 사항

- [ ] **개선 사항**
  - 추가 테스트 필요 영역
  - 커버리지 향상 방안

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **S1D1 (Database Schema)**
  - Supabase 클라이언트 연결 가능
  - 12개 테이블 존재 확인

- [ ] **S2BA1-S2BA4 (Backend APIs)**
  - API 엔드포인트 호출 가능

- [ ] **S3BA1-S3BA4 (Valuation Engines)**
  - orchestrator.executeValuation() 호출 가능
  - DCF 엔진 작동 확인

#### 4.2 Jest 실행

```bash
# 전체 테스트 실행
npm test

# 커버리지 포함
npm run test:coverage

# Watch 모드 (개발 시)
npm test -- --watch
```

**예상 출력:**
```
PASS  tests/integration/valuation-workflow.test.ts
  Valuation Workflow Integration Tests
    Step 1-3: 프로젝트 생성 및 견적
      ✓ 프로젝트 생성 성공 (245ms)
      ✓ 견적 생성 성공 (123ms)
      ✓ 협상 생성 성공 (98ms)
    Step 4-6: 문서 업로드 및 검토
      ✓ 문서 업로드 성공 (310ms)
      ✓ AI 승인 생성 성공 (87ms)
    ...
    Step 14: 최종 보고서 생성
      ✓ 보고서 생성 성공 (156ms)
      ✓ 프로젝트 완료 성공 (92ms)

Test Suites: 1 passed, 1 total
Tests:       18 passed, 18 total
Time:        12.456s
```

- [ ] **전체 테스트 통과** (18/18)
- [ ] **실행 시간 30초 이내**
- [ ] **에러 없음**

#### 4.3 Playwright 실행

```bash
# E2E 테스트 실행
npm run test:e2e

# Headed 모드 (브라우저 표시)
npm run test:e2e -- --headed

# 특정 브라우저
npm run test:e2e -- --project=chromium
```

**예상 출력:**
```
Running 3 tests using 3 workers

  ✓  1 tests/e2e/user-journey.test.ts:5:5 › 전체 평가 프로세스 (23.5s)
  ✓  2 tests/e2e/user-journey.test.ts:45:5 › 회계사 평가 작업 (18.2s)
  ✓  3 tests/e2e/user-journey.test.ts:75:5 › 관리자 모니터링 (12.8s)

  3 passed (54.5s)
```

- [ ] **3개 테스트 모두 통과**
- [ ] **실행 시간 60초 이내**
- [ ] **스크린샷 생성 확인** (test-results/)

#### 4.4 커버리지 검증

```bash
# 커버리지 리포트 생성
npm run test:coverage

# 브라우저에서 확인
open coverage/lcov-report/index.html
```

**커버리지 목표:**
- [ ] **Statements: 85% 이상**
- [ ] **Branches: 80% 이상**
- [ ] **Functions: 85% 이상**
- [ ] **Lines: 85% 이상**

**미커버 영역 확인:**
- [ ] 에러 핸들링 코드 (try-catch)
- [ ] Edge cases
- [ ] 사용하지 않는 코드 (제거 권장)

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - 모든 S1-S4 Task 완료 확인

- [ ] **환경 차단**
  - Supabase 테스트 프로젝트 설정 확인
  - 테스트용 계정 생성 확인

- [ ] **외부 API 차단**
  - AI API는 Mock 사용 (실제 호출 불필요)

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **3개 파일 생성 완료** ✅
3. **통합 테스트 18개 통과** ✅
4. **E2E 테스트 3개 통과** ✅
5. **커버리지 85% 이상** ✅
6. **테스트 리포트 작성** ✅
7. **실행 시간 60초 이내** ✅

### 권장 (Nice to Pass)

1. **커버리지 90% 이상** ✨
2. **시각적 회귀 테스트** ✨ (Percy, Chromatic)
3. **부하 테스트** ✨ (k6, Artillery)

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **테스트 데이터 격리**
   - 각 테스트는 독립적으로 실행
   - beforeEach/afterEach로 데이터 초기화
   - 테스트용 Supabase 프로젝트 사용 (프로덕션 X)

2. **비동기 처리**
   - async/await 사용
   - `waitFor()` 사용 (React Testing Library)
   - Playwright의 `waitForSelector()` 사용

3. **Mock vs 실제 API**
   - **통합 테스트**: 실제 Supabase 연결
   - **E2E 테스트**: 실제 브라우저, 실제 서버
   - **AI API**: Mock 사용 (비용 절감)

4. **타임아웃**
   - Jest 기본 5초 → 10초로 증가 (DB 연결)
   - Playwright 기본 30초 (충분함)

5. **CI/CD 통합**
   - GitHub Actions에서 자동 실행
   - 테스트 실패 시 배포 중단

6. **커버리지 제외**
   - `*.test.ts` 파일
   - `node_modules/`
   - `.next/`
   - 설정 파일 (jest.config.js, playwright.config.ts)

7. **환경 변수**
   - `.env.test` 파일 사용
   - 테스트용 Supabase URL/Key

---

## PO 테스트 가이드

### 1. Jest 통합 테스트 실행

```bash
# 프로젝트 루트에서
npm test

# 예상 출력:
# PASS  tests/integration/valuation-workflow.test.ts
#   Valuation Workflow Integration Tests
#     ✓ 프로젝트 생성 성공 (245ms)
#     ✓ 견적 생성 성공 (123ms)
#     ...
#     ✓ 프로젝트 완료 성공 (92ms)
#
# Test Suites: 1 passed, 1 total
# Tests:       18 passed, 18 total
```

**확인 사항:**
- [ ] 18개 테스트 모두 통과 (✓ 표시)
- [ ] 실행 시간 30초 이내
- [ ] 에러 메시지 없음

### 2. Jest 커버리지 확인

```bash
# 커버리지 포함 실행
npm run test:coverage

# 예상 출력:
# -------------------------|---------|----------|---------|---------|
# File                     | % Stmts | % Branch | % Funcs | % Lines |
# -------------------------|---------|----------|---------|---------|
# All files                |   87.23 |    82.45 |   86.12 |   85.67 |
#  lib/valuation/          |   92.15 |    88.32 |   91.05 |   90.23 |
#   orchestrator.ts        |   95.67 |    92.13 |   94.44 |   94.12 |
#   financial-math.ts      |   91.23 |    87.56 |   90.12 |   89.45 |
#  lib/crawler/            |   84.56 |    78.23 |   82.45 |   83.12 |
#   base-crawler.ts        |   88.90 |    82.10 |   86.50 |   87.20 |
# -------------------------|---------|----------|---------|---------|
```

**브라우저에서 확인:**
```bash
# HTML 리포트 열기
open coverage/lcov-report/index.html
```

**확인 사항:**
- [ ] 전체 커버리지 85% 이상
- [ ] 모든 영역 80% 이상
- [ ] 미커버 영역 확인 (빨간색)

### 3. Playwright E2E 테스트 실행

```bash
# E2E 테스트 실행
npm run test:e2e

# 예상 출력:
# Running 3 tests using 3 workers
#
#   ✓  1 [chromium] › tests/e2e/user-journey.test.ts:5:5 › 전체 평가 프로세스 (23.5s)
#   ✓  2 [chromium] › tests/e2e/user-journey.test.ts:45:5 › 회계사 평가 작업 (18.2s)
#   ✓  3 [chromium] › tests/e2e/user-journey.test.ts:75:5 › 관리자 모니터링 (12.8s)
#
#   3 passed (54.5s)
```

**확인 사항:**
- [ ] 3개 테스트 모두 통과 (✓ 표시)
- [ ] 실행 시간 60초 이내
- [ ] 스크린샷 생성 확인 (`test-results/` 폴더)

**Headed 모드 (브라우저 표시):**
```bash
npm run test:e2e -- --headed

# 브라우저 창이 열리며 테스트 실행 과정 확인 가능
```

### 4. 테스트 리포트 확인

**파일 열기:**
```bash
open docs/test-report.md
```

**확인 사항:**
- [ ] 개요 섹션 (날짜, 환경, 범위)
- [ ] 테스트 결과 요약 (21개 테스트, 100% 통과)
- [ ] 커버리지 상세 (85% 이상)
- [ ] 통합 테스트 결과 (18개)
- [ ] E2E 테스트 결과 (3개)
- [ ] 성능 메트릭 (Page Load < 3초 등)
- [ ] 알려진 이슈 (있으면 나열, 없으면 "없음")
- [ ] 개선 사항

### 5. CI/CD 통합 확인

**GitHub Actions에서:**
1. GitHub 레포지토리 → Actions 탭
2. CI 워크플로우 확인
   - [ ] test Job 성공 ✅
   - [ ] 커버리지 리포트 업로드 확인

**Vercel 배포 전:**
- [ ] 테스트 통과 후에만 배포 진행

---

## 참조

- Task Instruction: `task-instructions/S5T1_instruction.md`
- Jest 공식 문서: https://jestjs.io/
- Playwright 공식 문서: https://playwright.dev/
- Supabase Testing: https://supabase.com/docs/guides/testing

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
