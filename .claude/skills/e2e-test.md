# E2E Test Skill

**PoliticianFinder 프로젝트 전용 End-to-End 테스트 작성 및 실행 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- E2E Testing: Playwright
- Frontend: Next.js 14, React, TypeScript
- Backend: Next.js API Routes
- Database: Supabase

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- Playwright CLI로 모든 E2E 테스트 실행
- 스크린샷/비디오 자동 캡처
- 테스트 결과를 파일로 저장

### ❌ 금지
- 브라우저에서 수동 테스트
- GUI 기반 테스트 도구 수동 사용
- 사용자에게 수동 시나리오 테스트 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 E2E 테스트 전문가입니다:

1. **사용자 플로우 테스트**: 실제 사용자 시나리오 검증
2. **크로스 브라우저 테스트**: Chrome, Firefox, Safari 호환성
3. **시각적 회귀 테스트**: 스크린샷 비교
4. **테스트 데이터 관리**: 테스트 데이터 생성/정리
5. **테스트 보고서**: 실패 시 재현 단계 및 스크린샷 제공

---

## Playwright 설정

### 초기 설정
```bash
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend

# Playwright 설치
npm install -D @playwright/test
npx playwright install

# 설정 파일 생성 (이미 있다면 스킵)
npx playwright init
```

### playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## E2E 테스트 실행

### 기본 명령어
```bash
# 모든 테스트 실행
npx playwright test

# 특정 파일만
npx playwright test auth.spec.ts

# 특정 브라우저만
npx playwright test --project=chromium

# 헤드리스 모드 비활성화 (브라우저 보이기)
npx playwright test --headed

# UI 모드 (인터랙티브)
npx playwright test --ui

# 디버그 모드
npx playwright test --debug
```

### 테스트 결과 확인
```bash
# HTML 리포트 열기
npx playwright show-report

# 특정 테스트 재실행
npx playwright test --grep "user login"
```

---

## 핵심 사용자 플로우 테스트

### 1. 인증 플로우

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should sign up new user', async ({ page }) => {
    // 1. 회원가입 페이지로 이동
    await page.getByRole('link', { name: '회원가입' }).click();
    await expect(page).toHaveURL('/auth/signup');

    // 2. 폼 작성
    await page.getByLabel('이메일').fill('test@example.com');
    await page.getByLabel('비밀번호').fill('SecurePass123!');
    await page.getByLabel('비밀번호 확인').fill('SecurePass123!');
    await page.getByLabel('닉네임').fill('테스트유저');

    // 3. 제출
    await page.getByRole('button', { name: '가입하기' }).click();

    // 4. 성공 확인
    await expect(page).toHaveURL('/');
    await expect(page.getByText('회원가입이 완료되었습니다')).toBeVisible();
  });

  test('should login existing user', async ({ page }) => {
    // 1. 로그인 페이지
    await page.getByRole('link', { name: '로그인' }).click();
    await expect(page).toHaveURL('/auth/login');

    // 2. 자격 증명 입력
    await page.getByLabel('이메일').fill('existing@example.com');
    await page.getByLabel('비밀번호').fill('password123');

    // 3. 로그인
    await page.getByRole('button', { name: '로그인' }).click();

    // 4. 리다이렉션 확인
    await expect(page).toHaveURL('/');
    await expect(page.getByText('환영합니다')).toBeVisible();
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/auth/login');

    await page.getByLabel('이메일').fill('wrong@example.com');
    await page.getByLabel('비밀번호').fill('wrongpassword');
    await page.getByRole('button', { name: '로그인' }).click();

    await expect(page.getByText('이메일 또는 비밀번호가 올바르지 않습니다')).toBeVisible();
  });

  test('should logout user', async ({ page }) => {
    // 로그인 상태라고 가정 (fixture 사용)
    await page.goto('/');

    // 로그아웃
    await page.getByRole('button', { name: '프로필' }).click();
    await page.getByRole('menuitem', { name: '로그아웃' }).click();

    // 로그아웃 확인
    await expect(page.getByRole('link', { name: '로그인' })).toBeVisible();
  });
});
```

---

### 2. 정치인 검색 및 필터링

```typescript
// tests/e2e/politician-search.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Politician Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should search politician by name', async ({ page }) => {
    // 검색창에 입력
    const searchInput = page.getByPlaceholder('정치인 이름을 검색하세요');
    await searchInput.fill('홍길동');

    // 자동 완성 대기
    await page.waitForResponse(resp => resp.url().includes('/api/politicians/search'));

    // 결과 확인
    await expect(page.getByTestId('politician-card')).toHaveCount(1);
    await expect(page.getByText('홍길동')).toBeVisible();
  });

  test('should filter by party', async ({ page }) => {
    // 정당 필터 선택
    await page.getByRole('combobox', { name: '정당' }).selectOption('민주당');

    // API 요청 대기
    await page.waitForResponse(resp => resp.url().includes('party=민주당'));

    // 결과 확인
    const cards = page.getByTestId('politician-card');
    await expect(cards).toHaveCount(5);

    // 모든 카드가 민주당인지 확인
    const parties = await cards.getByTestId('party-badge').allTextContents();
    expect(parties.every(p => p === '민주당')).toBe(true);
  });

  test('should filter by region', async ({ page }) => {
    await page.getByRole('combobox', { name: '지역' }).selectOption('서울');
    await page.waitForResponse(resp => resp.url().includes('region=서울'));

    await expect(page.getByTestId('politician-card')).toHaveCount(10);
  });

  test('should sort by rating', async ({ page }) => {
    // 정렬 옵션 선택
    await page.getByRole('combobox', { name: '정렬' }).selectOption('평점 높은 순');
    await page.waitForResponse(resp => resp.url().includes('sort=rating'));

    // 첫 번째와 마지막 평점 가져오기
    const cards = page.getByTestId('politician-card');
    const firstRating = await cards.first().getByTestId('rating').textContent();
    const lastRating = await cards.last().getByTestId('rating').textContent();

    // 내림차순 확인
    expect(parseFloat(firstRating!)).toBeGreaterThanOrEqual(parseFloat(lastRating!));
  });

  test('should show no results message', async ({ page }) => {
    await page.getByPlaceholder('정치인 이름을 검색하세요').fill('존재하지않는이름123');
    await page.keyboard.press('Enter');

    await expect(page.getByText('검색 결과가 없습니다')).toBeVisible();
  });
});
```

---

### 3. 평가 작성 플로우

```typescript
// tests/e2e/evaluation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Evaluation Flow', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' }); // 로그인 상태

  test('should submit new evaluation', async ({ page }) => {
    // 1. 정치인 상세 페이지 방문
    await page.goto('/politicians/hong-gildong');

    // 2. 평가 작성 버튼 클릭
    await page.getByRole('button', { name: '평가 작성하기' }).click();

    // 3. 평점 선택 (별 5개 중 4개)
    await page.getByTestId('star-4').click();

    // 4. 코멘트 작성
    await page.getByLabel('평가 내용').fill('훌륭한 정치인입니다. 공약 이행률이 높습니다.');

    // 5. 카테고리별 평가
    await page.getByLabel('공약 이행').selectOption('5');
    await page.getByLabel('소통').selectOption('4');
    await page.getByLabel('전문성').selectOption('5');

    // 6. 제출
    await page.getByRole('button', { name: '평가 등록' }).click();

    // 7. 성공 메시지 확인
    await expect(page.getByText('평가가 등록되었습니다')).toBeVisible();

    // 8. 평가가 목록에 표시되는지 확인
    await expect(page.getByText('훌륭한 정치인입니다')).toBeVisible();
  });

  test('should validate evaluation form', async ({ page }) => {
    await page.goto('/politicians/hong-gildong');
    await page.getByRole('button', { name: '평가 작성하기' }).click();

    // 평점 선택 안하고 제출
    await page.getByRole('button', { name: '평가 등록' }).click();

    // 검증 에러 메시지
    await expect(page.getByText('평점을 선택해주세요')).toBeVisible();

    // 너무 짧은 코멘트
    await page.getByTestId('star-5').click();
    await page.getByLabel('평가 내용').fill('좋음');
    await page.getByRole('button', { name: '평가 등록' }).click();

    await expect(page.getByText('10자 이상 입력해주세요')).toBeVisible();
  });

  test('should edit existing evaluation', async ({ page }) => {
    // 내 평가 페이지로
    await page.goto('/my/evaluations');

    // 첫 번째 평가 수정
    await page.getByTestId('evaluation-card').first().getByRole('button', { name: '수정' }).click();

    // 내용 수정
    await page.getByLabel('평가 내용').clear();
    await page.getByLabel('평가 내용').fill('수정된 평가 내용입니다.');

    await page.getByRole('button', { name: '수정 완료' }).click();

    // 수정 확인
    await expect(page.getByText('평가가 수정되었습니다')).toBeVisible();
    await expect(page.getByText('수정된 평가 내용입니다')).toBeVisible();
  });

  test('should delete evaluation', async ({ page }) => {
    await page.goto('/my/evaluations');

    // 삭제 버튼 클릭
    await page.getByTestId('evaluation-card').first().getByRole('button', { name: '삭제' }).click();

    // 확인 다이얼로그
    page.on('dialog', dialog => dialog.accept());
    await expect(page.getByText('평가가 삭제되었습니다')).toBeVisible();
  });
});
```

---

### 4. 페이지네이션 및 무한 스크롤

```typescript
// tests/e2e/pagination.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Pagination', () => {
  test('should navigate through pages', async ({ page }) => {
    await page.goto('/politicians');

    // 첫 페이지 확인
    await expect(page.getByText('페이지 1 / 10')).toBeVisible();

    // 다음 페이지로
    await page.getByRole('button', { name: '다음' }).click();
    await page.waitForURL('**/politicians?page=2');

    // 페이지 번호 확인
    await expect(page.getByText('페이지 2 / 10')).toBeVisible();

    // 이전 페이지로
    await page.getByRole('button', { name: '이전' }).click();
    await page.waitForURL('**/politicians?page=1');
  });

  test('should load more on infinite scroll', async ({ page }) => {
    await page.goto('/politicians');

    // 초기 카드 수
    let cardCount = await page.getByTestId('politician-card').count();
    expect(cardCount).toBe(20);

    // 스크롤 다운
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // 로딩 인디케이터 확인
    await expect(page.getByText('로딩 중...')).toBeVisible();

    // 추가 카드 로드 대기
    await expect(page.getByTestId('politician-card')).toHaveCount(40);
  });
});
```

---

## 테스트 데이터 관리

### Fixtures 사용

```typescript
// tests/e2e/fixtures/auth.fixture.ts
import { test as base } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // 로그인 수행
    await page.goto('/auth/login');
    await page.getByLabel('이메일').fill('test@example.com');
    await page.getByLabel('비밀번호').fill('password123');
    await page.getByRole('button', { name: '로그인' }).click();
    await page.waitForURL('/');

    await use(page);

    // 로그아웃 (정리)
    await page.getByRole('button', { name: '로그아웃' }).click();
  },
});
```

### 테스트 데이터 시드

```typescript
// tests/e2e/setup/seed.ts
import { createClient } from '@supabase/supabase-js';

export async function seedTestData() {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY! // 관리자 키
  );

  // 테스트 정치인 생성
  const { data: politician } = await supabase
    .from('politicians')
    .insert({
      name: '테스트정치인',
      party: '테스트당',
      region: '서울',
    })
    .select()
    .single();

  return { politician };
}

export async function cleanupTestData() {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  // 테스트 데이터 삭제
  await supabase.from('politicians').delete().eq('party', '테스트당');
  await supabase.from('evaluations').delete().eq('comment', 'E2E Test');
}
```

### Global Setup/Teardown

```typescript
// tests/e2e/global-setup.ts
import { chromium, FullConfig } from '@playwright/test';
import { seedTestData } from './setup/seed';

async function globalSetup(config: FullConfig) {
  console.log('🌱 Seeding test data...');
  await seedTestData();

  console.log('🔐 Authenticating test user...');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000/auth/login');
  await page.getByLabel('이메일').fill('test@example.com');
  await page.getByLabel('비밀번호').fill('password123');
  await page.getByRole('button', { name: '로그인' }).click();
  await page.waitForURL('http://localhost:3000/');

  // 인증 상태 저장
  await page.context().storageState({ path: 'tests/e2e/.auth/user.json' });
  await browser.close();

  console.log('✅ Global setup complete');
}

export default globalSetup;
```

```typescript
// tests/e2e/global-teardown.ts
import { cleanupTestData } from './setup/seed';

async function globalTeardown() {
  console.log('🧹 Cleaning up test data...');
  await cleanupTestData();
  console.log('✅ Global teardown complete');
}

export default globalTeardown;
```

---

## 시각적 회귀 테스트

```typescript
// tests/e2e/visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('politician card should match snapshot', async ({ page }) => {
    await page.goto('/politicians');

    const card = page.getByTestId('politician-card').first();
    await expect(card).toHaveScreenshot('politician-card.png');
  });

  test('homepage should match snapshot', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
    });
  });

  test('should detect layout shifts', async ({ page }) => {
    await page.goto('/politicians/hong-gildong');

    // CLS 측정
    const cls = await page.evaluate(() => {
      return new Promise<number>(resolve => {
        let clsValue = 0;
        const observer = new PerformanceObserver(list => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'layout-shift') {
              clsValue += (entry as any).value;
            }
          }
        });
        observer.observe({ entryTypes: ['layout-shift'] });

        setTimeout(() => {
          observer.disconnect();
          resolve(clsValue);
        }, 3000);
      });
    });

    expect(cls).toBeLessThan(0.1);
  });
});
```

---

## 접근성 테스트

```typescript
// tests/e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('homepage should not have accessibility violations', async ({ page }) => {
    await page.goto('/');

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');

    // Tab으로 네비게이션
    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: '홈' })).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: '정치인' })).toBeFocused();

    // Enter로 링크 클릭
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL('/politicians');
  });
});
```

---

## 모바일 테스트

```typescript
// tests/e2e/mobile.spec.ts
import { test, expect, devices } from '@playwright/test';

test.describe('Mobile Experience', () => {
  test.use({ ...devices['iPhone 12'] });

  test('should show mobile menu', async ({ page }) => {
    await page.goto('/');

    // 햄버거 메뉴 클릭
    await page.getByRole('button', { name: '메뉴' }).click();

    // 모바일 메뉴 확인
    await expect(page.getByRole('navigation')).toBeVisible();
  });

  test('should support touch gestures', async ({ page }) => {
    await page.goto('/politicians');

    // 스와이프로 카드 넘기기
    const card = page.getByTestId('politician-card').first();
    await card.swipe('left');

    // 다음 카드가 보이는지 확인
    await expect(page.getByTestId('politician-card').nth(1)).toBeVisible();
  });
});
```

---

## E2E 테스트 보고서 템플릿

```markdown
# E2E 테스트 보고서

**실행 날짜**: [YYYY-MM-DD HH:mm:ss]
**실행자**: Claude Code
**브라우저**: Chromium, Firefox, WebKit

---

## 요약

### 전체 결과
- ✅ 통과: 42개
- ❌ 실패: 3개
- ⏭️  건너뜀: 0개
- **통과율**: 93%

### 브라우저별 결과
- Chromium: 45/45 (100%)
- Firefox: 43/45 (96%)
- WebKit: 42/45 (93%)

---

## 실패 테스트

### 1. should submit evaluation (WebKit)

**브라우저**: WebKit (Safari)
**파일**: `tests/e2e/evaluation.spec.ts:25`

**에러**:
```
TimeoutError: locator.click: Timeout 30000ms exceeded.
```

**스크린샷**: `test-results/evaluation-webkit-failure.png`

**재현 단계**:
1. Safari에서 `/politicians/hong-gildong` 방문
2. '평가 작성하기' 버튼 클릭
3. 평점 4개 선택
4. 코멘트 입력
5. '평가 등록' 버튼 클릭 시도 → 30초 타임아웃

**원인**: WebKit에서 버튼 클릭 이벤트가 발생하지 않음 (CSS transform 이슈 의심)

**수정 방안**: `pointer-events` CSS 속성 확인

---

## 스크린샷

실패한 테스트의 스크린샷이 `test-results/` 폴더에 저장되었습니다.

---

## 다음 단계

1. WebKit 버튼 클릭 이슈 수정
2. Firefox 모바일 테스트 추가
3. 성능 메트릭 측정 추가
```

---

**이 스킬을 활성화하면, 실제 사용자 관점에서 PoliticianFinder 프로젝트의 모든 기능을 자동으로 검증하여 품질을 보장합니다.**
