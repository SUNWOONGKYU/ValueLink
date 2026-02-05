# ValueLink 개발 워크플로우

**작성일**: 2026-02-05
**버전**: 1.0
**프로젝트**: ValueLink - AI 기반 기업가치평가 플랫폼

---

## 개요

본 문서는 ValueLink 프로젝트의 **개발 워크플로우**를 정의합니다.

### 핵심 원칙

```
✅ SAL Grid 방법론 준수
✅ 단계별 검증 (Stage Gate)
✅ Git 브랜치 전략
✅ 코드 리뷰 프로세스
✅ 자동화된 배포
```

---

## 1. SAL Grid 개발 프로세스

### 1.1 전체 흐름

```
┌───────────────────────────────────────────────────────────┐
│  1. Task Instruction 읽기                                 │
│     → sal-grid/task-instructions/{TaskID}_instruction.md  │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  2. Git 브랜치 생성                                       │
│     → git checkout -b task/{TaskID}                       │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  3. JSON 상태 업데이트 (In Progress)                      │
│     → grid_records/{TaskID}.json                          │
│     → task_status: 'Pending' → 'In Progress'             │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  4. Task 작업 수행 (Task Agent)                          │
│     → 코드 작성/수정                                      │
│     → 로컬 테스트                                         │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  5. JSON 상태 업데이트 (Executed)                         │
│     → task_status: 'In Progress' → 'Executed'            │
│     → generated_files 기록                                │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  6. 검증 (Verification Agent)                             │
│     → verification-instructions/{TaskID}_verification.md  │
│     → 빌드, 테스트, 통합 검증                             │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  7. JSON 상태 업데이트 (Verified → Completed)            │
│     → verification_status: 'Not Verified' → 'Verified'    │
│     → task_status: 'Executed' → 'Completed'              │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  8. Git 커밋 & 푸시                                       │
│     → git commit -m "feat: {TaskID} {Task Name}"          │
│     → git push origin task/{TaskID}                       │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  9. Pull Request 생성                                     │
│     → GitHub에서 PR 생성                                  │
│     → 코드 리뷰 요청                                      │
└───────────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│  10. Merge to main                                        │
│      → PR 승인 후 main 브랜치 병합                        │
└───────────────────────────────────────────────────────────┘
```

### 1.2 상태 전이 규칙

```
task_status 전이:
Pending → In Progress → Executed → Completed
                              ↑
                        Verified 후만!

verification_status 전이:
Not Verified → In Review → Verified (또는 Needs Fix)
```

**핵심**: `Completed`는 `verification_status = 'Verified'`일 때만 설정 가능!

---

## 2. Git 브랜치 전략

### 2.1 브랜치 구조

```
main (Production)
    ↓
develop (Integration)
    ↓
├─ stage/s1 (Stage 1)
│   ├─ task/S1BI1
│   ├─ task/S1D1
│   └─ task/S1S1
│
├─ stage/s2 (Stage 2)
│   ├─ task/S2F1
│   ├─ task/S2BA1
│   └─ task/S2S1
│
└─ hotfix/issue-123 (긴급 수정)
```

### 2.2 브랜치 명명 규칙

| 브랜치 타입 | 형식 | 예시 |
|------------|------|------|
| **Task** | `task/{TaskID}` | `task/S2F1` |
| **Stage** | `stage/s{N}` | `stage/s2` |
| **Hotfix** | `hotfix/issue-{N}` | `hotfix/issue-123` |
| **Feature** | `feature/{name}` | `feature/ai-avatar` |

### 2.3 브랜치 생명주기

```bash
# Task 브랜치 생성
git checkout develop
git pull origin develop
git checkout -b task/S2F1

# 작업 & 커밋
git add .
git commit -m "feat(S2F1): Google 로그인 UI 구현"

# 푸시
git push origin task/S2F1

# PR 생성 (GitHub)
gh pr create --base develop --head task/S2F1 \
  --title "S2F1: Google 로그인 UI 구현" \
  --body "..."

# 병합 후 삭제
git branch -d task/S2F1
git push origin --delete task/S2F1
```

---

## 3. 커밋 메시지 규칙

### 3.1 Conventional Commits

```
<type>(<TaskID>): <subject>

[optional body]

[optional footer]
```

### 3.2 Type 목록

| Type | 설명 | 예시 |
|------|------|------|
| **feat** | 새 기능 | `feat(S2F1): Google 로그인 UI 구현` |
| **fix** | 버그 수정 | `fix(S2BA1): 구독 취소 API 오류 수정` |
| **docs** | 문서 변경 | `docs(S0): TASK_PLAN.md 업데이트` |
| **style** | 코드 스타일 | `style(S2F1): ESLint 경고 제거` |
| **refactor** | 리팩토링 | `refactor(S3E1): AI 요청 로직 개선` |
| **test** | 테스트 | `test(S2BA1): API 통합 테스트 추가` |
| **chore** | 기타 | `chore: package.json 업데이트` |

### 3.3 예시

```bash
# 좋은 예
git commit -m "feat(S2F1): Google 로그인 UI 구현

- Google OAuth 2.0 연동
- 로그인 성공 시 대시보드 이동
- 에러 핸들링 추가

Closes #45
"

# 나쁜 예
git commit -m "수정"
git commit -m "버그 고침"
git commit -m "작업 완료"
```

---

## 4. Pull Request 프로세스

### 4.1 PR 생성

```bash
gh pr create --base develop --head task/S2F1 \
  --title "S2F1: Google 로그인 UI 구현" \
  --body "$(cat <<'EOF'
## Task 정보
- Task ID: S2F1
- Task Name: Google 로그인 UI 구현
- Stage: S2 (개발 1차)
- Area: F (Frontend)

## 변경 사항
- Google OAuth 2.0 연동
- 로그인 성공 시 대시보드 이동
- 에러 핸들링 추가

## 생성/수정 파일
- `pages/auth/google-login.html`
- `lib/supabase/auth.ts`

## 테스트
- [ ] 로그인 성공 시나리오
- [ ] 로그인 실패 시나리오
- [ ] 에러 핸들링

## 스크린샷
(첨부)

## 관련 Task
- Closes S2F1

🤖 Generated with Claude Code
EOF
)"
```

### 4.2 PR 체크리스트

**자동 검증 (CI/CD)**:
- [ ] 빌드 성공
- [ ] ESLint 통과
- [ ] TypeScript 타입 체크
- [ ] 단위 테스트 통과
- [ ] E2E 테스트 통과 (선택)

**수동 검증**:
- [ ] 코드 리뷰 승인
- [ ] 기능 테스트 통과
- [ ] JSON 상태 업데이트 확인
- [ ] 문서 업데이트 (필요 시)

### 4.3 PR 리뷰 가이드

**리뷰어 체크리스트**:
- [ ] 코드가 Task Instruction을 따르는가?
- [ ] 변수명/함수명이 명확한가?
- [ ] 에러 핸들링이 충분한가?
- [ ] 테스트가 충분한가?
- [ ] 성능 이슈가 없는가?
- [ ] 보안 취약점이 없는가?

**리뷰 코멘트 예시**:
```
✅ Approve:
"LGTM! 코드가 명확하고 테스트도 충분합니다."

💬 Comment:
"에러 메시지를 더 구체적으로 작성하면 좋겠습니다.
예: '로그인 실패' → '이메일 또는 비밀번호가 올바르지 않습니다'"

🚫 Request Changes:
"Supabase RLS 정책이 누락되었습니다. 추가 후 재요청 바랍니다."
```

---

## 5. 코드 리뷰 프로세스

### 5.1 Self-Review (자체 검토)

**PR 생성 전 체크**:
```bash
# 1. 코드 스타일 검사
npm run lint

# 2. 타입 체크
npm run type-check

# 3. 테스트 실행
npm test

# 4. 로컬 빌드
npm run build

# 5. 변경된 파일 확인
git diff develop...HEAD
```

### 5.2 AI Review (Claude Code)

```bash
# Bash 도구로 /review-pr 실행
gh pr view 123 --json body --jq .body | claude-code review
```

**AI Review 포인트**:
- 코드 스타일
- 잠재적 버그
- 성능 이슈
- 보안 취약점
- 테스트 커버리지

### 5.3 Human Review (PO)

**리뷰 우선순위**:
1. **P0 (필수)**: S (Security), BA (Backend APIs), BI (Backend Infra)
2. **P1 (권장)**: F (Frontend), D (Database)
3. **P2 (선택)**: M (Documentation), T (Testing)

---

## 6. Stage Gate 프로세스

### 6.1 Stage 완료 조건

```
□ Stage 내 모든 Task가 'Completed' 상태
□ 모든 Task의 comprehensive_verification이 'Passed'
□ Blocker 0개
□ 전체 빌드 성공
□ 전체 테스트 통과
□ 의존성 체인 완결
```

### 6.2 Stage Gate 검증

**수행자**: Main Agent

**검증 절차**:
```bash
# 1. JSON 상태 확인
cat method/json/data/grid_records/S2*.json | jq '.task_status'

# 2. 빌드 확인
npm run build

# 3. 테스트 확인
npm test

# 4. 검증 리포트 생성
# sal-grid/stage-gates/S2GATE_verification_report.md
```

### 6.3 Stage Gate 리포트

**저장 위치**: `S0_Project-SAL-Grid_생성/sal-grid/stage-gates/S{N}GATE_verification_report.md`

**템플릿**:
```markdown
# S2 Stage Gate Verification Report

## 1. Task 완료 현황
| Task ID | Task Name | Status | Verification |
|---------|-----------|--------|--------------|
| S2F1 | Google 로그인 UI | ✅ 완료 | ✅ Passed |
| ... | ... | ... | ... |

## 2. 빌드/테스트 결과
- 전체 빌드: ✅ 성공
- 단위 테스트: 24/24 통과
- 통합 테스트: 5/5 통과

## 3. Blockers
- 없음 ✅

## 4. PO 승인
- [ ] 승인
- [ ] 거부 (사유: _________)
```

---

## 7. 배포 워크플로우

### 7.1 개발 환경 (Development)

```
develop 브랜치 → Vercel Preview Deployment

자동 배포:
- PR 생성 시 자동 Preview 배포
- URL: https://valuelink-{pr-number}.vercel.app
- 용도: 기능 테스트
```

### 7.2 스테이징 환경 (Staging)

```
stage/* 브랜치 → Vercel Staging Deployment

배포 조건:
- Stage Gate 통과
- PO 승인

URL: https://staging.valuation.ai.kr
용도: QA, UAT
```

### 7.3 프로덕션 환경 (Production)

```
main 브랜치 → Vercel Production Deployment

배포 조건:
- S5 완료
- E2E 테스트 통과
- 보안 감사 통과
- PO 최종 승인

URL: https://valuation.ai.kr
용도: 실제 서비스
```

### 7.4 배포 체크리스트

**배포 전**:
- [ ] 환경 변수 설정 확인
- [ ] Database Migration 완료
- [ ] Backup 완료

**배포 중**:
- [ ] 빌드 성공
- [ ] Health Check 통과
- [ ] 배포 완료 알림

**배포 후**:
- [ ] Smoke Test (주요 기능 확인)
- [ ] 모니터링 확인 (Sentry, Vercel Analytics)
- [ ] Rollback 준비 (문제 시)

---

## 8. CI/CD 파이프라인

### 8.1 GitHub Actions Workflow

**파일 위치**: `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Test
        run: npm test

      - name: Build
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  deploy-preview:
    needs: build
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel Preview
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel Production
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### 8.2 Pre-commit Hook

**파일 위치**: `.git/hooks/pre-commit`

```bash
#!/bin/sh

echo "🔍 Running pre-commit checks..."

# 1. Lint
echo "📝 Linting..."
npm run lint --fix
if [ $? -ne 0 ]; then
    echo "❌ Lint failed! Fix errors and try again."
    exit 1
fi

# 2. Type Check
echo "🔧 Type checking..."
npm run type-check
if [ $? -ne 0 ]; then
    echo "❌ Type check failed! Fix errors and try again."
    exit 1
fi

# 3. Tests
echo "🧪 Running tests..."
npm test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Fix errors and try again."
    exit 1
fi

# 4. Stage → Root 동기화 (해당되는 경우)
node scripts/sync-to-root.js

echo "✅ Pre-commit checks passed!"
```

---

## 9. 테스트 전략

### 9.1 테스트 피라미드

```
             ┌──────────┐
             │   E2E    │  10%
             └──────────┘
          ┌──────────────┐
          │ Integration  │  30%
          └──────────────┘
      ┌──────────────────────┐
      │     Unit Tests       │  60%
      └──────────────────────┘
```

### 9.2 단위 테스트 (Unit Tests)

**도구**: Jest, React Testing Library

**범위**:
- 유틸리티 함수
- React 컴포넌트
- API 클라이언트
- 비즈니스 로직

**예시**:
```typescript
// components/Button.test.tsx
import { render, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Button>Click me</Button>);
    expect(getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = jest.fn();
    const { getByText } = render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(getByText('Click me'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### 9.3 통합 테스트 (Integration Tests)

**도구**: Jest, Supertest (API)

**범위**:
- API 엔드포인트
- Supabase 연동
- 컴포넌트 간 상호작용

**예시**:
```typescript
// api/projects.test.ts
import request from 'supertest';
import app from '../app';

describe('POST /api/projects', () => {
  it('creates a new project', async () => {
    const res = await request(app)
      .post('/api/projects')
      .send({
        company_name: '테스트 회사',
        industry: 'IT',
        revenue: 1000000000,
      })
      .expect(201);

    expect(res.body).toHaveProperty('id');
    expect(res.body.company_name).toBe('테스트 회사');
  });
});
```

### 9.4 E2E 테스트 (End-to-End Tests)

**도구**: Playwright, Cypress

**범위**:
- 핵심 사용자 시나리오
- 14단계 워크플로우
- 결제 플로우

**예시**:
```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('user can login with Google', async ({ page }) => {
  await page.goto('https://valuation.ai.kr/auth/login');
  await page.click('text=Google로 로그인');

  // Google 로그인 페이지
  await page.fill('input[type="email"]', 'test@example.com');
  await page.click('text=다음');
  await page.fill('input[type="password"]', 'password123');
  await page.click('text=로그인');

  // 대시보드로 이동
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.locator('h1')).toContainText('대시보드');
});
```

---

## 10. 모니터링 & 로깅

### 10.1 에러 추적 (Sentry)

```typescript
// lib/sentry.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
});

// 사용 예시
try {
  // 코드
} catch (error) {
  Sentry.captureException(error);
  throw error;
}
```

### 10.2 성능 모니터링 (Vercel Analytics)

```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### 10.3 로깅 (Winston)

```typescript
// lib/logger.ts
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
}

export default logger;
```

---

## 11. 문서화 워크플로우

### 11.1 코드 문서화

**TypeScript**: JSDoc 주석

```typescript
/**
 * 프로젝트를 생성합니다.
 *
 * @param data - 프로젝트 생성 데이터
 * @returns 생성된 프로젝트
 * @throws {Error} 필수 필드 누락 시
 */
export async function createProject(data: CreateProjectInput): Promise<Project> {
  // ...
}
```

### 11.2 API 문서화

**도구**: Swagger (FastAPI 자동 생성)

**접근**: `http://localhost:8000/docs`

### 11.3 README 업데이트

**위치**: 각 폴더의 `README.md`

**내용**:
- 폴더 목적
- 파일 목록 및 설명
- 사용 방법
- 예시

---

## 요약

```
✅ SAL Grid 6단계 프로세스 정의
✅ Git 브랜치 전략 (task/stage/hotfix)
✅ Conventional Commits 규칙
✅ PR 프로세스 및 체크리스트
✅ Stage Gate 검증 절차
✅ 3-tier 배포 전략 (Dev/Staging/Prod)
✅ CI/CD 파이프라인 (GitHub Actions)
✅ 테스트 피라미드 (Unit 60%, Integration 30%, E2E 10%)
✅ 모니터링 (Sentry, Vercel Analytics, Winston)
```

**다음 단계**: P2 마지막 문서 (Requirements) 작성 → P3 프로토타입 정리

**작성자**: Claude Code
**버전**: 1.0
**작성일**: 2026-02-05
