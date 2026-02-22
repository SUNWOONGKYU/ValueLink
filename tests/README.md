# ValueLink 테스트 가이드

## 테스트 구조

```
tests/
├── integration/                   # 통합 테스트 (Jest)
│   └── valuation-workflow.test.ts # 14단계 워크플로우 테스트
├── e2e/                           # E2E 테스트 (Playwright)
│   └── user-journey.test.ts       # 사용자 여정 테스트
└── README.md                      # 이 파일
```

---

## 필수 환경 변수

테스트 실행 전 `.env.local` 파일에 다음 변수를 설정하세요:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Base URL (E2E tests)
BASE_URL=http://localhost:3000
```

---

## 테스트 실행 방법

### 1. 통합 테스트 (Integration Tests)

**모든 통합 테스트 실행:**
```bash
npm run test
```

**Watch 모드 (파일 변경 시 자동 재실행):**
```bash
npm run test:watch
```

**커버리지 리포트 생성:**
```bash
npm run test:coverage
```

**특정 테스트 파일만 실행:**
```bash
npm test -- valuation-workflow.test.ts
```

---

### 2. E2E 테스트 (End-to-End Tests)

**E2E 테스트 실행 (헤드리스 모드):**
```bash
npm run test:e2e
```

**UI 모드 (디버깅용):**
```bash
npm run test:e2e:ui
```

**특정 브라우저만 테스트:**
```bash
npx playwright test --project=chromium
```

---

## 테스트 데이터 관리

### 자동 정리 (Cleanup)

모든 테스트는 `beforeAll()`에서 테스트 데이터를 생성하고,
`afterAll()`에서 자동으로 삭제합니다.

**정리되는 데이터:**
- 테스트 사용자 계정 (auth.users, public.users)
- 테스트 프로젝트 (valuation_projects)
- 테스트 문서 (dcf_documents)
- 테스트 초안 (dcf_drafts)
- 테스트 보고서 (dcf_reports)

**주의사항:**
- 실제 데이터베이스에 영향을 주지 않도록 테스트 전용 Supabase 프로젝트 사용 권장
- CI/CD 환경에서는 별도의 테스트 DB 사용 필수

---

## 테스트 커버리지 목표

| 메트릭 | 목표 |
|--------|------|
| Statement | 80% |
| Branch | 80% |
| Function | 80% |
| Line | 80% |

**커버리지 리포트 확인:**
```bash
npm run test:coverage
open coverage/lcov-report/index.html
```

---

## 테스트 작성 가이드

### 통합 테스트 (Jest)

**템플릿:**
```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(/* ... */)

describe('Feature Name', () => {
  let testData: any

  beforeAll(async () => {
    // 테스트 데이터 생성
  })

  afterAll(async () => {
    // 테스트 데이터 정리
  })

  test('should do something', async () => {
    const result = await someFunction()
    expect(result).toBeDefined()
  })
})
```

### E2E 테스트 (Playwright)

**템플릿:**
```typescript
import { test, expect } from '@playwright/test'

test.describe('User Journey', () => {
  test('should complete flow', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL(/\/dashboard/)
  })
})
```

---

## 문제 해결

### Jest 테스트 실패 시

**1. 환경 변수 확인:**
```bash
echo $NEXT_PUBLIC_SUPABASE_URL
```

**2. 캐시 삭제:**
```bash
npm run test -- --clearCache
```

**3. 상세 로그 확인:**
```bash
npm run test -- --verbose
```

### Playwright 테스트 실패 시

**1. 브라우저 설치:**
```bash
npx playwright install chromium
```

**2. 디버그 모드 실행:**
```bash
PWDEBUG=1 npm run test:e2e
```

**3. 스크린샷/비디오 확인:**
- `playwright-report/` 폴더에서 확인 가능

---

## CI/CD 통합

### GitHub Actions 예시

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:coverage
      - run: npx playwright install chromium
      - run: npm run test:e2e
```

---

## 추가 리소스

- [Jest 공식 문서](https://jestjs.io/docs/getting-started)
- [Playwright 공식 문서](https://playwright.dev/docs/intro)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Supabase Testing Guide](https://supabase.com/docs/guides/testing)

---

**작성일**: 2026-02-22
**작성자**: Test Engineer (Claude Code)
