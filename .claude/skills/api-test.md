# API Test Skill

**PoliticianFinder 프로젝트 전용 API 테스트 전문 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Backend: Next.js API Routes
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth
- Testing: Jest, Supertest

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- CLI 명령어로 API 테스트 실행
- 자동화된 API 테스트 스크립트
- 테스트 결과를 파일로 저장

### ❌ 금지
- Postman GUI로 수동 테스트
- 웹 브라우저에서 API 수동 호출
- 사용자에게 수동 API 테스트 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 API 테스트 전문가입니다:

1. **엔드포인트 테스트**: 모든 API 엔드포인트 기능 검증
2. **Request/Response 검증**: 입출력 데이터 형식 확인
3. **에러 핸들링**: 예외 상황 처리 테스트
4. **성능 테스트**: 응답 시간 및 부하 테스트
5. **보안 테스트**: 인증/인가, 입력 검증 확인

---

## API 테스트 설정

### 의존성 설치
```bash
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend

npm install -D jest @types/jest
npm install -D supertest @types/supertest
npm install -D node-mocks-http
```

### Jest 설정
```javascript
// jest.config.api.js
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/api/**/*.test.ts'],
  setupFilesAfterEnv: ['<rootDir>/tests/api/setup.ts'],
  collectCoverageFrom: ['src/app/api/**/*.ts'],
};
```

---

## API 테스트 실행

```bash
# 모든 API 테스트 실행
npm test -- --config=jest.config.api.js

# 특정 엔드포인트만
npm test -- --config=jest.config.api.js politicians

# Watch 모드
npm test -- --config=jest.config.api.js --watch

# 커버리지 포함
npm test -- --config=jest.config.api.js --coverage
```

---

## 엔드포인트별 테스트

### 1. GET /api/politicians - 정치인 목록 조회

```typescript
// tests/api/politicians/get.test.ts
import { GET } from '@/app/api/politicians/route';
import { NextRequest } from 'next/server';

// Supabase 모킹
jest.mock('@/lib/supabase/server', () => ({
  createClient: jest.fn(() => ({
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        range: jest.fn(() => ({
          order: jest.fn(() => Promise.resolve({
            data: [
              { id: '1', name: '홍길동', party: '테스트당', avg_rating: 4.5 },
              { id: '2', name: '김철수', party: '평가당', avg_rating: 4.2 },
            ],
            error: null,
          })),
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
    expect(data.data[0]).toMatchObject({
      id: '1',
      name: '홍길동',
      party: '테스트당',
    });
  });

  it('should support pagination', async () => {
    const request = new NextRequest('http://localhost:3000/api/politicians?page=2&limit=10');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.page).toBe(2);
    expect(data.limit).toBe(10);
  });

  it('should filter by party', async () => {
    const request = new NextRequest('http://localhost:3000/api/politicians?party=민주당');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    data.data.forEach((p: any) => {
      expect(p.party).toBe('민주당');
    });
  });

  it('should filter by region', async () => {
    const request = new NextRequest('http://localhost:3000/api/politicians?region=서울');
    const response = await GET(request);

    expect(response.status).toBe(200);
  });

  it('should validate page parameter', async () => {
    const request = new NextRequest('http://localhost:3000/api/politicians?page=-1');
    const response = await GET(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({
      error: 'Invalid page parameter',
    });
  });

  it('should handle database errors', async () => {
    // 에러 모킹
    jest.mock('@/lib/supabase/server', () => ({
      createClient: jest.fn(() => ({
        from: jest.fn(() => ({
          select: jest.fn(() => Promise.resolve({
            data: null,
            error: new Error('Database connection failed'),
          })),
        })),
      })),
    }));

    const request = new NextRequest('http://localhost:3000/api/politicians');
    const response = await GET(request);

    expect(response.status).toBe(500);
    expect(await response.json()).toEqual({
      error: 'Internal server error',
    });
  });
});
```

---

### 2. POST /api/evaluations - 평가 생성

```typescript
// tests/api/evaluations/post.test.ts
import { POST } from '@/app/api/evaluations/route';
import { NextRequest } from 'next/server';

describe('POST /api/evaluations', () => {
  const validPayload = {
    politician_id: '123e4567-e89b-12d3-a456-426614174000',
    score: 4.5,
    comment: '훌륭한 정치인입니다. 공약 이행률이 높습니다.',
    categories: {
      promise_fulfillment: 5,
      communication: 4,
      expertise: 5,
    },
  };

  it('should create evaluation', async () => {
    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify(validPayload),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.data).toMatchObject({
      politician_id: validPayload.politician_id,
      score: validPayload.score,
      comment: validPayload.comment,
    });
  });

  it('should require authentication', async () => {
    // 인증되지 않은 요청
    jest.mock('@/lib/supabase/server', () => ({
      createClient: jest.fn(() => ({
        auth: {
          getUser: jest.fn(() => Promise.resolve({ data: { user: null } })),
        },
      })),
    }));

    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify(validPayload),
    });

    const response = await POST(request);

    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({
      error: 'Unauthorized',
    });
  });

  it('should validate score range', async () => {
    const invalidPayload = { ...validPayload, score: 6 };

    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify(invalidPayload),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({
      error: 'Score must be between 0 and 5',
    });
  });

  it('should validate comment length', async () => {
    const invalidPayload = { ...validPayload, comment: '짧음' };

    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify(invalidPayload),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({
      error: expect.stringContaining('Comment must be at least 10 characters'),
    });
  });

  it('should validate politician_id format', async () => {
    const invalidPayload = { ...validPayload, politician_id: 'invalid-uuid' };

    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify(invalidPayload),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({
      error: expect.stringContaining('Invalid politician_id format'),
    });
  });

  it('should prevent duplicate evaluations', async () => {
    // 이미 평가한 정치인
    jest.mock('@/lib/supabase/server', () => ({
      createClient: jest.fn(() => ({
        auth: {
          getUser: jest.fn(() => Promise.resolve({
            data: { user: { id: 'user123' } },
          })),
        },
        from: jest.fn(() => ({
          select: jest.fn(() => ({
            eq: jest.fn(() => ({
              eq: jest.fn(() => Promise.resolve({
                data: [{ id: 'existing-evaluation' }],
                error: null,
              })),
            })),
          })),
        })),
      })),
    }));

    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify(validPayload),
    });

    const response = await POST(request);

    expect(response.status).toBe(409);
    expect(await response.json()).toEqual({
      error: 'You have already evaluated this politician',
    });
  });
});
```

---

### 3. PUT /api/evaluations/[id] - 평가 수정

```typescript
// tests/api/evaluations/put.test.ts
import { PUT } from '@/app/api/evaluations/[id]/route';
import { NextRequest } from 'next/server';

describe('PUT /api/evaluations/[id]', () => {
  const evaluationId = '123e4567-e89b-12d3-a456-426614174000';

  it('should update evaluation', async () => {
    const request = new NextRequest(`http://localhost:3000/api/evaluations/${evaluationId}`, {
      method: 'PUT',
      body: JSON.stringify({
        score: 5,
        comment: '수정된 평가입니다.',
      }),
    });

    const response = await PUT(request, { params: { id: evaluationId } });
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.data.score).toBe(5);
    expect(data.data.comment).toBe('수정된 평가입니다.');
  });

  it('should require ownership', async () => {
    // 다른 사용자의 평가
    jest.mock('@/lib/supabase/server', () => ({
      createClient: jest.fn(() => ({
        auth: {
          getUser: jest.fn(() => Promise.resolve({
            data: { user: { id: 'user123' } },
          })),
        },
        from: jest.fn(() => ({
          select: jest.fn(() => ({
            eq: jest.fn(() => Promise.resolve({
              data: { user_id: 'other-user' },
              error: null,
            })),
          })),
        })),
      })),
    }));

    const request = new NextRequest(`http://localhost:3000/api/evaluations/${evaluationId}`, {
      method: 'PUT',
      body: JSON.stringify({ score: 5 }),
    });

    const response = await PUT(request, { params: { id: evaluationId } });

    expect(response.status).toBe(403);
    expect(await response.json()).toEqual({
      error: 'Forbidden',
    });
  });

  it('should handle not found', async () => {
    const nonExistentId = '00000000-0000-0000-0000-000000000000';

    const request = new NextRequest(`http://localhost:3000/api/evaluations/${nonExistentId}`, {
      method: 'PUT',
      body: JSON.stringify({ score: 5 }),
    });

    const response = await PUT(request, { params: { id: nonExistentId } });

    expect(response.status).toBe(404);
    expect(await response.json()).toEqual({
      error: 'Evaluation not found',
    });
  });
});
```

---

### 4. DELETE /api/evaluations/[id] - 평가 삭제

```typescript
// tests/api/evaluations/delete.test.ts
import { DELETE } from '@/app/api/evaluations/[id]/route';
import { NextRequest } from 'next/server';

describe('DELETE /api/evaluations/[id]', () => {
  const evaluationId = '123e4567-e89b-12d3-a456-426614174000';

  it('should delete evaluation', async () => {
    const request = new NextRequest(`http://localhost:3000/api/evaluations/${evaluationId}`, {
      method: 'DELETE',
    });

    const response = await DELETE(request, { params: { id: evaluationId } });

    expect(response.status).toBe(204);
  });

  it('should require authentication', async () => {
    // 인증 실패 모킹
    const request = new NextRequest(`http://localhost:3000/api/evaluations/${evaluationId}`, {
      method: 'DELETE',
    });

    const response = await DELETE(request, { params: { id: evaluationId } });

    expect(response.status).toBe(401);
  });

  it('should require ownership', async () => {
    // 소유권 확인 실패
    const request = new NextRequest(`http://localhost:3000/api/evaluations/${evaluationId}`, {
      method: 'DELETE',
    });

    const response = await DELETE(request, { params: { id: evaluationId } });

    expect(response.status).toBe(403);
  });
});
```

---

## 성능 테스트

### 응답 시간 측정

```typescript
// tests/api/performance/response-time.test.ts
import { GET } from '@/app/api/politicians/route';
import { NextRequest } from 'next/server';

describe('API Performance', () => {
  it('should respond within 100ms', async () => {
    const start = performance.now();

    const request = new NextRequest('http://localhost:3000/api/politicians');
    await GET(request);

    const duration = performance.now() - start;

    expect(duration).toBeLessThan(100);
  });

  it('should handle concurrent requests', async () => {
    const requests = Array.from({ length: 10 }, () =>
      GET(new NextRequest('http://localhost:3000/api/politicians'))
    );

    const start = performance.now();
    await Promise.all(requests);
    const duration = performance.now() - start;

    expect(duration).toBeLessThan(500);
  });
});
```

---

## 부하 테스트 (Artillery)

### Artillery 설정
```bash
npm install -D artillery
```

### 부하 테스트 시나리오
```yaml
# tests/load/politicians.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10
      name: Warm up
    - duration: 120
      arrivalRate: 50
      name: Ramp up load
    - duration: 60
      arrivalRate: 100
      name: Sustained load
  defaults:
    headers:
      Content-Type: 'application/json'

scenarios:
  - name: Browse politicians
    flow:
      - get:
          url: '/api/politicians'
          expect:
            - statusCode: 200
            - contentType: json
      - think: 2
      - get:
          url: '/api/politicians?page=2'
          expect:
            - statusCode: 200
      - think: 1
      - get:
          url: '/api/politicians?party=민주당'
          expect:
            - statusCode: 200

  - name: Create evaluation
    flow:
      - post:
          url: '/api/evaluations'
          json:
            politician_id: '{{ $randomUUID }}'
            score: 4.5
            comment: 'Test evaluation from load test'
          beforeRequest: 'setAuthToken'
          expect:
            - statusCode: 201
```

### 부하 테스트 실행
```bash
# 부하 테스트 실행
npx artillery run tests/load/politicians.yml

# 리포트 생성
npx artillery run --output report.json tests/load/politicians.yml
npx artillery report report.json
```

---

## 보안 테스트

### SQL Injection 테스트
```typescript
// tests/api/security/sql-injection.test.ts
describe('SQL Injection Prevention', () => {
  it('should prevent SQL injection in search', async () => {
    const maliciousInput = "'; DROP TABLE politicians; --";

    const request = new NextRequest(
      `http://localhost:3000/api/politicians?search=${encodeURIComponent(maliciousInput)}`
    );

    const response = await GET(request);

    // 에러가 발생하지 않고 안전하게 처리되어야 함
    expect(response.status).toBe(200);
  });
});
```

### XSS 테스트
```typescript
// tests/api/security/xss.test.ts
describe('XSS Prevention', () => {
  it('should sanitize comment input', async () => {
    const maliciousComment = '<script>alert("XSS")</script>';

    const request = new NextRequest('http://localhost:3000/api/evaluations', {
      method: 'POST',
      body: JSON.stringify({
        politician_id: '123e4567-e89b-12d3-a456-426614174000',
        score: 4,
        comment: maliciousComment,
      }),
    });

    const response = await POST(request);
    const data = await response.json();

    // 스크립트 태그가 이스케이프되거나 제거되어야 함
    expect(data.data.comment).not.toContain('<script>');
  });
});
```

### Rate Limiting 테스트
```typescript
// tests/api/security/rate-limit.test.ts
describe('Rate Limiting', () => {
  it('should rate limit excessive requests', async () => {
    const requests = Array.from({ length: 100 }, () =>
      GET(new NextRequest('http://localhost:3000/api/politicians'))
    );

    const responses = await Promise.all(requests);

    // 일부 요청은 429 (Too Many Requests) 반환해야 함
    const rateLimited = responses.filter(r => r.status === 429);
    expect(rateLimited.length).toBeGreaterThan(0);
  });
});
```

---

## API 테스트 보고서 템플릿

```markdown
# API 테스트 보고서

**테스트 날짜**: [YYYY-MM-DD HH:mm:ss]
**테스트 환경**: Local Development
**실행자**: Claude Code

---

## 요약

### 전체 결과
- ✅ 통과: 45개
- ❌ 실패: 2개
- **통과율**: 96%

### 카테고리별 결과
- 기능 테스트: 40/42 (95%)
- 성능 테스트: 5/5 (100%)
- 보안 테스트: 0/0 (N/A)

---

## 엔드포인트별 테스트 결과

### GET /api/politicians
- ✅ 정치인 목록 조회
- ✅ 페이지네이션
- ✅ 정당 필터
- ✅ 지역 필터
- ✅ 입력 검증
- ✅ 에러 핸들링

### POST /api/evaluations
- ✅ 평가 생성
- ✅ 인증 확인
- ❌ 점수 범위 검증 (실패)
- ✅ 코멘트 길이 검증
- ✅ UUID 형식 검증
- ❌ 중복 평가 방지 (실패)

### PUT /api/evaluations/[id]
- ✅ 평가 수정
- ✅ 소유권 확인
- ✅ Not Found 처리

### DELETE /api/evaluations/[id]
- ✅ 평가 삭제
- ✅ 인증 확인
- ✅ 소유권 확인

---

## 실패 테스트 상세

### 1. POST /api/evaluations - 점수 범위 검증

**에러**:
```
Expected: 400
Received: 201
```

**원인**: score 값이 6일 때 검증 로직이 작동하지 않음

**수정 방안**:
```typescript
// 현재
if (score < 0 || score > 5) {
  // 검증 로직
}

// 문제: score가 정확히 6일 때 누락
```

---

### 2. POST /api/evaluations - 중복 평가 방지

**에러**: 중복 평가가 허용됨

**원인**: 중복 체크 쿼리가 실행되지 않음

**수정 방안**: 중복 체크 로직 추가 필요

---

## 성능 테스트 결과

### 응답 시간

| 엔드포인트 | 평균 | P50 | P95 | P99 |
|-----------|------|-----|-----|-----|
| GET /api/politicians | 85ms | 78ms | 120ms | 145ms |
| POST /api/evaluations | 110ms | 95ms | 180ms | 220ms |
| PUT /api/evaluations/[id] | 92ms | 85ms | 135ms | 160ms |
| DELETE /api/evaluations/[id] | 65ms | 58ms | 95ms | 115ms |

### 부하 테스트 (Artillery)

**시나리오**: 100 req/s, 2분간

- 총 요청: 12,000
- 성공: 11,950 (99.6%)
- 실패: 50 (0.4%)
- 평균 응답 시간: 95ms
- P95: 180ms
- P99: 250ms

---

## 보안 테스트 결과

- ✅ SQL Injection 방어
- ✅ XSS 방어
- ⚠️  Rate Limiting 미구현

---

## 액션 아이템

### 즉시 수정 (P0)
- [ ] POST /api/evaluations 점수 검증 로직 수정
- [ ] 중복 평가 방지 로직 구현

### 단기 개선 (P1)
- [ ] Rate Limiting 구현
- [ ] API 문서 자동 생성 (OpenAPI/Swagger)

### 중기 개선 (P2)
- [ ] 성능 모니터링 대시보드
- [ ] 자동화된 부하 테스트 CI 통합

---

## 다음 테스트 일정

**권장 주기**: 커밋마다 (CI)
**다음 전체 테스트**: [YYYY-MM-DD]
```

---

## API 테스트 자동화 스크립트

```bash
#!/bin/bash
# run-api-tests.sh

echo "🧪 API 테스트 시작..."

# 1. 기능 테스트
echo "\n📦 기능 테스트 실행 중..."
npm test -- --config=jest.config.api.js --coverage

# 2. 성능 테스트
echo "\n⚡ 성능 테스트 실행 중..."
npm test -- --config=jest.config.api.js --testPathPattern=performance

# 3. 보안 테스트
echo "\n🔒 보안 테스트 실행 중..."
npm test -- --config=jest.config.api.js --testPathPattern=security

# 4. 부하 테스트 (선택적)
if [ "$RUN_LOAD_TEST" = "true" ]; then
  echo "\n💥 부하 테스트 실행 중..."
  npx artillery run tests/load/politicians.yml --output load-report.json
  npx artillery report load-report.json
fi

echo "\n✅ 모든 API 테스트 완료!"
```

---

**이 스킬을 활성화하면, PoliticianFinder 프로젝트의 모든 API 엔드포인트를 체계적으로 테스트하여 안정성과 성능을 보장합니다.**
