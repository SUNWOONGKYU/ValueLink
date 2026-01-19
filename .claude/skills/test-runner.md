# Test Runner Skill

**PoliticianFinder 프로젝트 전용 자동화 테스트 실행 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Testing: Jest, React Testing Library, Playwright
- Frontend: Next.js 14, React, TypeScript
- Backend: Next.js API Routes
- Database: Supabase

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- CLI 명령어로 모든 테스트 실행
- 테스트 결과를 파일로 저장
- 자동화된 테스트 리포트 생성

### ❌ 금지
- 웹 브라우저에서 수동 테스트
- GUI 테스트 도구 사용
- 사용자에게 수동 테스트 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 테스트 자동화 엔지니어입니다:

1. **단위 테스트**: 함수, 컴포넌트 단위 테스트 실행
2. **통합 테스트**: API, 데이터베이스 연동 테스트
3. **E2E 테스트**: 사용자 시나리오 테스트
4. **커버리지 분석**: 테스트 커버리지 측정 및 보고
5. **버그 리포트**: 실패한 테스트 분석 및 재현 단계 문서화

---

## 테스트 실행 프로세스

### 1. 테스트 환경 설정

```bash
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend

# 의존성 설치 확인
npm install

# 환경변수 설정 (.env.test)
cp .env.local .env.test
```

### 2. 테스트 실행 명령어

#### 전체 테스트 실행
```bash
# 모든 테스트 실행
npm test

# Watch 모드 (개발 중)
npm test -- --watch

# 커버리지 포함
npm test -- --coverage
```

#### 특정 테스트만 실행
```bash
# 파일 이름으로
npm test -- PoliticianCard

# 경로로
npm test -- src/components/PoliticianCard.test.tsx

# 패턴으로
npm test -- --testPathPattern=components

# 특정 테스트 케이스만
npm test -- --testNamePattern="should render politician name"
```

#### CI/CD 모드
```bash
# CI 환경에서 실행 (watch 모드 비활성화)
npm test -- --ci --coverage --maxWorkers=2
```

---

## 테스트 타입별 실행

### Unit Tests (단위 테스트)

**대상**: 유틸리티 함수, React 컴포넌트

```bash
# 유틸리티 함수 테스트
npm test -- src/lib/utils

# 컴포넌트 테스트
npm test -- src/components
```

**예시: 유틸리티 함수 테스트**
```typescript
// src/lib/utils/format.test.ts
import { formatRating, formatDate } from './format';

describe('formatRating', () => {
  it('should format rating with 1 decimal place', () => {
    expect(formatRating(4.567)).toBe('4.6');
  });

  it('should handle null rating', () => {
    expect(formatRating(null)).toBe('N/A');
  });

  it('should handle edge cases', () => {
    expect(formatRating(0)).toBe('0.0');
    expect(formatRating(5)).toBe('5.0');
  });
});

describe('formatDate', () => {
  it('should format date in Korean', () => {
    const date = new Date('2024-01-15');
    expect(formatDate(date)).toBe('2024년 1월 15일');
  });
});
```

**예시: 컴포넌트 테스트**
```typescript
// src/components/PoliticianCard.test.tsx
import { render, screen } from '@testing-library/react';
import { PoliticianCard } from './PoliticianCard';

describe('PoliticianCard', () => {
  const mockPolitician = {
    id: '1',
    name: '홍길동',
    party: '테스트당',
    avg_rating: 4.5,
  };

  it('should render politician name', () => {
    render(<PoliticianCard data={mockPolitician} />);
    expect(screen.getByText('홍길동')).toBeInTheDocument();
  });

  it('should render rating', () => {
    render(<PoliticianCard data={mockPolitician} />);
    expect(screen.getByText('4.5')).toBeInTheDocument();
  });

  it('should render party', () => {
    render(<PoliticianCard data={mockPolitician} />);
    expect(screen.getByText('테스트당')).toBeInTheDocument();
  });
});
```

---

### Integration Tests (통합 테스트)

**대상**: API Routes, 데이터베이스 연동

```bash
# API 테스트
npm test -- src/app/api
```

**예시: API Route 테스트**
```typescript
// src/app/api/politicians/route.test.ts
import { GET } from './route';
import { NextRequest } from 'next/server';

// Supabase 모킹
jest.mock('@/lib/supabase/server', () => ({
  createClient: jest.fn(() => ({
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        range: jest.fn(() => ({
          data: [
            { id: '1', name: '홍길동', party: '테스트당' },
            { id: '2', name: '김철수', party: '평가당' },
          ],
          error: null,
        })),
      })),
    })),
  })),
}));

describe('GET /api/politicians', () => {
  it('should return list of politicians', async () => {
    const request = new NextRequest('http://localhost:3000/api/politicians');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.data).toHaveLength(2);
    expect(data.data[0].name).toBe('홍길동');
  });

  it('should support pagination', async () => {
    const request = new NextRequest('http://localhost:3000/api/politicians?page=2');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.page).toBe(2);
  });

  it('should handle errors', async () => {
    // 에러 상황 모킹
    jest.mock('@/lib/supabase/server', () => ({
      createClient: jest.fn(() => ({
        from: jest.fn(() => ({
          select: jest.fn(() => ({
            error: new Error('Database error'),
          })),
        })),
      })),
    }));

    const request = new NextRequest('http://localhost:3000/api/politicians');
    const response = await GET(request);

    expect(response.status).toBe(500);
  });
});
```

---

### E2E Tests (End-to-End 테스트)

**대상**: 사용자 플로우, 전체 시나리오

```bash
# Playwright 테스트 실행
npx playwright test

# UI 모드 (디버깅용)
npx playwright test --ui

# 특정 브라우저만
npx playwright test --project=chromium

# 헤드리스 모드 비활성화
npx playwright test --headed
```

**예시: E2E 테스트**
```typescript
// tests/e2e/politician-search.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Politician Search', () => {
  test('should search and display results', async ({ page }) => {
    // 페이지 방문
    await page.goto('http://localhost:3000');

    // 검색창 찾기
    const searchInput = page.getByPlaceholder('정치인 이름 검색');
    await searchInput.fill('홍길동');

    // 검색 버튼 클릭
    await page.getByRole('button', { name: '검색' }).click();

    // 결과 확인
    await expect(page.getByText('홍길동')).toBeVisible();
    await expect(page.getByTestId('politician-card')).toHaveCount(1);
  });

  test('should show no results message', async ({ page }) => {
    await page.goto('http://localhost:3000');

    const searchInput = page.getByPlaceholder('정치인 이름 검색');
    await searchInput.fill('존재하지않는이름');

    await page.getByRole('button', { name: '검색' }).click();

    await expect(page.getByText('검색 결과가 없습니다')).toBeVisible();
  });
});
```

---

## 커버리지 분석

### 커버리지 실행
```bash
# 커버리지 리포트 생성
npm test -- --coverage

# 특정 디렉토리만
npm test -- --coverage --collectCoverageFrom='src/components/**/*.{ts,tsx}'

# HTML 리포트
npm test -- --coverage --coverageReporters=html
```

### 커버리지 목표

| 타입 | 최소 | 목표 | 이상적 |
|------|------|------|--------|
| Statements | 70% | 80% | 90% |
| Branches | 60% | 75% | 85% |
| Functions | 70% | 80% | 90% |
| Lines | 70% | 80% | 90% |

### 커버리지 설정
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/**/__tests__/**',
  ],
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 75,
      functions: 80,
      lines: 80,
    },
    './src/lib/': {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90,
    },
  },
};
```

---

## 테스트 결과 분석

### 테스트 리포트 템플릿

```markdown
# 테스트 실행 보고서

**실행 날짜**: [YYYY-MM-DD HH:mm:ss]
**실행자**: Claude Code
**프로젝트**: PoliticianFinder

---

## 요약

### 전체 결과
- ✅ 통과: X개
- ❌ 실패: Y개
- ⏭️  건너뜀: Z개
- **통과율**: XX%

### 실행 시간
- 총 소요 시간: X.XXs
- 평균 테스트 시간: X.XXms

---

## 테스트 스위트별 결과

### Unit Tests
- 총: 50개
- 통과: 48개 (96%)
- 실패: 2개 (4%)
- 소요 시간: 2.5s

**실패 테스트**:
1. `src/lib/utils/format.test.ts`
   - `formatRating should handle undefined`
   - 원인: undefined 처리 로직 누락
   - 재현: `formatRating(undefined)` 호출 시 에러

2. `src/components/PoliticianCard.test.tsx`
   - `should render placeholder when no image`
   - 원인: 기본 이미지 경로 오류
   - 재현: `image` prop 없이 렌더링

---

### Integration Tests
- 총: 20개
- 통과: 20개 (100%)
- 실패: 0개
- 소요 시간: 1.8s

✅ 모든 API 테스트 통과

---

### E2E Tests
- 총: 15개
- 통과: 14개 (93%)
- 실패: 1개 (7%)
- 소요 시간: 45.3s

**실패 테스트**:
1. `tests/e2e/evaluation.spec.ts`
   - `should submit evaluation`
   - 원인: Submit 버튼 선택자 변경됨
   - 재현 단계:
     1. 정치인 상세 페이지 방문
     2. 평가 작성
     3. 제출 버튼 클릭 시도
     4. TimeoutError: Locator not found

---

## 커버리지 분석

### 전체 커버리지: 82%

| 타입 | 커버리지 | 목표 | 상태 |
|------|----------|------|------|
| Statements | 82% | 80% | ✅ |
| Branches | 73% | 75% | ⚠️ -2% |
| Functions | 85% | 80% | ✅ |
| Lines | 81% | 80% | ✅ |

### 디렉토리별 커버리지

**src/lib/**: 92% ✅
- utils/: 95%
- supabase/: 88%

**src/components/**: 78% ⚠️
- PoliticianCard: 90%
- EvaluationForm: 65% (개선 필요)
- SearchBar: 85%

**src/app/api/**: 85% ✅
- politicians/: 90%
- evaluations/: 80%

### 커버리지 미달 파일

1. `src/components/EvaluationForm.tsx` (65%)
   - 미테스트 라인: 45-52 (에러 핸들링)
   - 미테스트 라인: 78-85 (성공 콜백)

2. `src/lib/utils/validation.ts` (70%)
   - 미테스트 브랜치: 이메일 검증 edge cases

---

## 실패 테스트 상세

### 1. formatRating should handle undefined

**파일**: `src/lib/utils/format.test.ts:25`

**에러 메시지**:
```
TypeError: Cannot read property 'toFixed' of undefined
    at formatRating (format.ts:10)
    at Object.<anonymous> (format.test.ts:27)
```

**현재 코드**:
```typescript
export function formatRating(rating: number | null): string {
  if (rating === null) return 'N/A';
  return rating.toFixed(1); // undefined 처리 안됨!
}
```

**수정 방안**:
```typescript
export function formatRating(rating: number | null | undefined): string {
  if (rating === null || rating === undefined) return 'N/A';
  return rating.toFixed(1);
}
```

**우선순위**: P1 (High)

---

### 2. should render placeholder when no image

**파일**: `src/components/PoliticianCard.test.tsx:45`

**에러 메시지**:
```
Error: Failed to load image: /images/placeholder.jpg
```

**재현 단계**:
```typescript
it('should render placeholder when no image', () => {
  const politician = { id: '1', name: '홍길동', image: null };
  render(<PoliticianCard data={politician} />);
  // 기본 이미지가 렌더링되어야 함
});
```

**원인**: placeholder 이미지 파일이 없음

**수정 방안**:
1. `/public/images/placeholder.jpg` 파일 추가
2. 또는 기본 아바타 컴포넌트 사용

**우선순위**: P2 (Medium)

---

### 3. should submit evaluation (E2E)

**파일**: `tests/e2e/evaluation.spec.ts:35`

**에러 메시지**:
```
TimeoutError: locator.click: Timeout 30000ms exceeded.
Locator: getByRole('button', { name: '제출' })
```

**재현 단계**:
1. `http://localhost:3000/politicians/1` 방문
2. 평가 점수 선택
3. 코멘트 입력
4. 제출 버튼 클릭 시도 → 실패

**원인**: UI 변경으로 버튼 텍스트가 '제출' → '평가 등록'으로 변경됨

**수정 방안**:
```typescript
// ❌ 현재
await page.getByRole('button', { name: '제출' }).click();

// ✅ 수정
await page.getByRole('button', { name: '평가 등록' }).click();

// 또는 data-testid 사용
await page.getByTestId('submit-evaluation-btn').click();
```

**우선순위**: P1 (High)

---

## 액션 아이템

### 즉시 수정 (P1)
- [ ] `formatRating` undefined 처리 추가
- [ ] E2E 테스트 선택자 업데이트

### 단기 수정 (P2)
- [ ] Placeholder 이미지 추가 또는 기본 컴포넌트 사용
- [ ] `EvaluationForm` 테스트 커버리지 75%로 개선
- [ ] Branch 커버리지 75% 달성

### 중기 개선
- [ ] E2E 테스트에 data-testid 속성 추가 (선택자 안정성)
- [ ] 테스트 실행 시간 단축 (병렬 실행 최적화)
- [ ] 스냅샷 테스트 도입

---

## 권장 테스트 전략

### 테스트 피라미드

```
       E2E (15개)
      /          \
     /    통합     \
    /   (20개)     \
   /________________\
        단위 (50개)
```

**비율**: 단위 60% / 통합 25% / E2E 15%

### 테스트 작성 우선순위

1. **Critical Path**: 회원가입, 로그인, 평가 작성
2. **Core Business Logic**: 평가 계산, 정렬, 필터링
3. **Utility Functions**: 포맷팅, 검증, 변환
4. **UI Components**: 재사용 컴포넌트

---

## 다음 테스트 실행 일정

**권장 실행 주기**:
- 커밋 전: Unit + Integration (로컬)
- PR 생성 시: 전체 테스트 (CI)
- 배포 전: 전체 테스트 + E2E (CI)
- 정기: 주 1회 전체 리그레션

**다음 전체 테스트**: [YYYY-MM-DD]
```

---

## 테스트 자동화 스크립트

```bash
#!/bin/bash
# run-tests.sh

echo "🧪 PoliticianFinder 테스트 시작..."

# 1. 단위 테스트
echo "\n📦 단위 테스트 실행 중..."
npm test -- --testPathPattern=src/lib --testPathPattern=src/components --passWithNoTests

# 2. 통합 테스트
echo "\n🔗 통합 테스트 실행 중..."
npm test -- --testPathPattern=src/app/api --passWithNoTests

# 3. 커버리지 생성
echo "\n📊 커버리지 분석 중..."
npm test -- --coverage --coverageReporters=json-summary

# 4. E2E 테스트 (선택적)
if [ "$RUN_E2E" = "true" ]; then
  echo "\n🎭 E2E 테스트 실행 중..."
  npx playwright test
fi

echo "\n✅ 모든 테스트 완료!"
```

---

## CI/CD 통합

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test -- --ci --coverage

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/coverage-final.json
```

---

**이 스킬을 활성화하면, 체계적인 테스트 자동화로 PoliticianFinder 프로젝트의 품질을 보장하고 버그를 조기에 발견합니다.**
