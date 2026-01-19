# Performance Check Skill

**PoliticianFinder 프로젝트 전용 성능 최적화 분석 스킬**

---

## 프로젝트 컨텍스트

**프로젝트**: PoliticianFinder (AI 기반 정치인 평가 플랫폼)
**기술 스택**:
- Frontend: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- Backend: Next.js API Routes
- Database: Supabase (PostgreSQL)
- Deployment: Vercel

---

## AI-only 개발 원칙 (필수 준수)

### ✅ 허용
- CLI 명령어로 성능 측정 도구 실행
- 코드 분석으로 성능 병목 탐지
- 벤치마크 결과를 파일로 저장

### ❌ 금지
- 웹 기반 성능 도구 수동 사용 (Lighthouse GUI)
- Dashboard에서 수동으로 메트릭 확인
- 사용자에게 수동 성능 테스트 요청

**위반 발견 시 즉시 작업 중단 및 대안 탐색**

---

## 역할 및 책임

당신은 PoliticianFinder 프로젝트의 성능 분석가입니다:

1. **Frontend 성능**: Core Web Vitals, 렌더링 성능, 번들 크기
2. **Backend 성능**: API 응답 시간, 데이터베이스 쿼리 최적화
3. **네트워크 성능**: 리소스 로딩, 캐싱 전략
4. **사용자 경험**: 체감 성능, 인터랙션 지연
5. **성능 보고서**: 벤치마크 결과 및 개선 방안 제시

---

## 성능 분석 프로세스

### 1. 프론트엔드 성능 측정

#### Lighthouse CLI 실행
```bash
cd /g/내\ 드라이브/Developement/PoliticianFinder/frontend

# 로컬 빌드
npm run build
npm run start

# Lighthouse 실행 (별도 터미널)
npx lighthouse http://localhost:3000 \
  --output=json \
  --output=html \
  --output-path=./lighthouse-report \
  --chrome-flags="--headless" \
  --only-categories=performance
```

#### Next.js 번들 분석
```bash
# @next/bundle-analyzer 설치
npm install -D @next/bundle-analyzer

# next.config.js 수정 후
ANALYZE=true npm run build
```

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // 기존 설정
});
```

#### Core Web Vitals 목표

| 메트릭 | 좋음 | 개선 필요 | 나쁨 |
|--------|------|----------|------|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5s - 4s | > 4s |
| FID (First Input Delay) | ≤ 100ms | 100ms - 300ms | > 300ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |
| FCP (First Contentful Paint) | ≤ 1.8s | 1.8s - 3s | > 3s |
| TTI (Time to Interactive) | ≤ 3.8s | 3.8s - 7.3s | > 7.3s |

---

### 2. 데이터베이스 쿼리 최적화

#### 느린 쿼리 탐지
```typescript
// lib/supabase/performance.ts
export async function measureQuery<T>(
  queryFn: () => Promise<T>,
  queryName: string
): Promise<T> {
  const start = performance.now();
  const result = await queryFn();
  const duration = performance.now() - start;

  if (duration > 1000) {
    console.warn(`⚠️ Slow query detected: ${queryName} took ${duration.toFixed(2)}ms`);
  } else {
    console.log(`✅ ${queryName}: ${duration.toFixed(2)}ms`);
  }

  return result;
}

// 사용 예시
const politicians = await measureQuery(
  () => supabase.from('politicians').select('*').limit(50),
  'getPoliticians'
);
```

#### 쿼리 최적화 체크리스트

**❌ 나쁜 패턴: N+1 쿼리 문제**
```typescript
// 정치인 목록 조회
const { data: politicians } = await supabase
  .from('politicians')
  .select('*');

// 각 정치인의 평가를 별도로 조회 (N+1 문제!)
for (const politician of politicians) {
  const { data: evaluations } = await supabase
    .from('evaluations')
    .select('*')
    .eq('politician_id', politician.id);

  politician.evaluations = evaluations;
}
```

**✅ 좋은 패턴: JOIN 사용**
```typescript
const { data: politicians } = await supabase
  .from('politicians')
  .select(`
    *,
    evaluations (
      id,
      score,
      comment,
      created_at
    )
  `);
```

**✅ 좋은 패턴: 필요한 컬럼만 선택**
```typescript
// ❌ 나쁜 예
const { data } = await supabase.from('politicians').select('*');

// ✅ 좋은 예
const { data } = await supabase
  .from('politicians')
  .select('id, name, party, avg_rating');
```

**✅ 좋은 패턴: 인덱스 활용**
```sql
-- 자주 사용하는 검색/정렬 컬럼에 인덱스 생성
CREATE INDEX idx_politicians_avg_rating ON politicians(avg_rating DESC);
CREATE INDEX idx_politicians_party ON politicians(party);
CREATE INDEX idx_evaluations_politician_id ON evaluations(politician_id);
CREATE INDEX idx_evaluations_user_id ON evaluations(user_id);
```

**✅ 좋은 패턴: 페이지네이션**
```typescript
const PAGE_SIZE = 20;

async function getPoliticians(page: number) {
  const { data, count } = await supabase
    .from('politicians')
    .select('*', { count: 'exact' })
    .range((page - 1) * PAGE_SIZE, page * PAGE_SIZE - 1)
    .order('avg_rating', { ascending: false });

  return {
    data,
    total: count,
    page,
    pageSize: PAGE_SIZE,
    totalPages: Math.ceil((count || 0) / PAGE_SIZE),
  };
}
```

---

### 3. API 응답 시간 최적화

#### API 성능 모니터링
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const start = Date.now();

  const response = NextResponse.next();

  response.headers.set('X-Response-Time', `${Date.now() - start}ms`);

  return response;
}

export const config = {
  matcher: '/api/:path*',
};
```

#### 응답 캐싱
```typescript
// app/api/politicians/route.ts
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = searchParams.get('page') || '1';

  const { data } = await supabase
    .from('politicians')
    .select('*')
    .range((+page - 1) * 20, +page * 20 - 1);

  return NextResponse.json(
    { data },
    {
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
      },
    }
  );
}
```

#### API 목표 응답 시간

| 엔드포인트 유형 | 목표 | 허용 | 개선 필요 |
|---------------|------|------|----------|
| 단순 조회 (GET) | < 100ms | < 300ms | > 300ms |
| 복잡한 조회 | < 300ms | < 1s | > 1s |
| 생성/수정 (POST/PUT) | < 200ms | < 500ms | > 500ms |
| 삭제 (DELETE) | < 100ms | < 300ms | > 300ms |

---

### 4. 프론트엔드 최적화

#### React 렌더링 최적화

**❌ 나쁜 패턴: 불필요한 리렌더링**
```typescript
export default function PoliticianList({ politicians }) {
  return (
    <div>
      {politicians.map(politician => (
        <PoliticianCard key={politician.id} data={politician} />
      ))}
    </div>
  );
}

// 부모가 리렌더링되면 모든 카드가 리렌더링됨
```

**✅ 좋은 패턴: React.memo 사용**
```typescript
import { memo } from 'react';

const PoliticianCard = memo(function PoliticianCard({ data }) {
  return (
    <div>
      <h3>{data.name}</h3>
      <p>{data.party}</p>
    </div>
  );
});

export default function PoliticianList({ politicians }) {
  return (
    <div>
      {politicians.map(politician => (
        <PoliticianCard key={politician.id} data={politician} />
      ))}
    </div>
  );
}
```

**✅ 좋은 패턴: useMemo와 useCallback**
```typescript
'use client';
import { useMemo, useCallback } from 'react';

export default function SearchResults({ politicians, query }) {
  // 비싼 연산 메모이제이션
  const sortedPoliticians = useMemo(() => {
    return politicians
      .filter(p => p.name.includes(query))
      .sort((a, b) => b.avg_rating - a.avg_rating);
  }, [politicians, query]);

  // 콜백 메모이제이션
  const handleClick = useCallback((id: string) => {
    console.log('Clicked:', id);
  }, []);

  return (
    <div>
      {sortedPoliticians.map(p => (
        <div key={p.id} onClick={() => handleClick(p.id)}>
          {p.name}
        </div>
      ))}
    </div>
  );
}
```

#### 이미지 최적화

**✅ Next.js Image 컴포넌트 사용**
```typescript
import Image from 'next/image';

export function PoliticianAvatar({ src, name }) {
  return (
    <Image
      src={src}
      alt={name}
      width={100}
      height={100}
      placeholder="blur"
      blurDataURL="/placeholder.jpg"
      loading="lazy"
    />
  );
}
```

#### 코드 스플리팅

**✅ 동적 임포트**
```typescript
import dynamic from 'next/dynamic';

// 무거운 컴포넌트 지연 로딩
const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false, // 클라이언트에서만 로드
});

export default function PoliticianStats() {
  return (
    <div>
      <h2>Statistics</h2>
      <HeavyChart />
    </div>
  );
}
```

#### 가상 스크롤 (대량 데이터)

```typescript
'use client';
import { useVirtualizer } from '@tanstack/react-virtual';

export default function VirtualList({ items }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 5. 네트워크 최적화

#### 리소스 프리로드
```typescript
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        <link rel="preconnect" href="https://xxxxx.supabase.co" />
        <link rel="dns-prefetch" href="https://xxxxx.supabase.co" />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

#### 폰트 최적화
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
});

export default function RootLayout({ children }) {
  return (
    <html className={inter.className}>
      <body>{children}</body>
    </html>
  );
}
```

---

## 성능 벤치마크 도구

### 커스텀 벤치마크 유틸리티

```typescript
// lib/performance/benchmark.ts
export class Benchmark {
  private measurements: Map<string, number[]> = new Map();

  start(label: string): () => void {
    const start = performance.now();

    return () => {
      const duration = performance.now() - start;
      const existing = this.measurements.get(label) || [];
      this.measurements.set(label, [...existing, duration]);
    };
  }

  getStats(label: string) {
    const durations = this.measurements.get(label) || [];
    if (durations.length === 0) return null;

    const sorted = [...durations].sort((a, b) => a - b);
    const avg = durations.reduce((a, b) => a + b, 0) / durations.length;
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    const median = sorted[Math.floor(sorted.length / 2)];
    const p95 = sorted[Math.floor(sorted.length * 0.95)];

    return { avg, min, max, median, p95, count: durations.length };
  }

  report(): string {
    let report = '\n📊 Performance Benchmark Report\n';
    report += '=' .repeat(50) + '\n\n';

    for (const [label, durations] of this.measurements) {
      const stats = this.getStats(label);
      if (!stats) continue;

      report += `${label}:\n`;
      report += `  Avg: ${stats.avg.toFixed(2)}ms\n`;
      report += `  Min: ${stats.min.toFixed(2)}ms\n`;
      report += `  Max: ${stats.max.toFixed(2)}ms\n`;
      report += `  Median: ${stats.median.toFixed(2)}ms\n`;
      report += `  P95: ${stats.p95.toFixed(2)}ms\n`;
      report += `  Count: ${stats.count}\n\n`;
    }

    return report;
  }
}

// 사용 예시
const benchmark = new Benchmark();

for (let i = 0; i < 100; i++) {
  const end = benchmark.start('getPoliticians');
  await getPoliticians(1);
  end();
}

console.log(benchmark.report());
```

---

## 성능 분석 보고서 템플릿

```markdown
# 성능 분석 보고서

**분석 날짜**: [YYYY-MM-DD]
**분석자**: Claude Code
**프로젝트**: PoliticianFinder

---

## 요약

### 전체 성능 점수: X/100

**Core Web Vitals**:
- LCP: X.Xs (목표: ≤ 2.5s) [✅/⚠️/❌]
- FID: Xms (목표: ≤ 100ms) [✅/⚠️/❌]
- CLS: X.XX (목표: ≤ 0.1) [✅/⚠️/❌]

**API 응답 시간**:
- 평균: Xms
- P95: Xms
- 최대: Xms

**번들 크기**:
- First Load JS: X KB
- Total JS: X KB

---

## 프론트엔드 성능

### Lighthouse 결과

| 메트릭 | 점수 | 상태 |
|--------|------|------|
| Performance | 85 | 🟡 개선 필요 |
| Accessibility | 95 | ✅ 좋음 |
| Best Practices | 100 | ✅ 좋음 |
| SEO | 100 | ✅ 좋음 |

### Core Web Vitals 상세

**LCP (Largest Contentful Paint): 3.2s** 🟡
- 목표: ≤ 2.5s
- 현재: 3.2s
- 차이: +0.7s (28% 느림)

**원인**:
- 메인 이미지 크기가 큼 (1.5MB)
- 렌더 블로킹 리소스

**개선 방안**:
1. 이미지 최적화 (WebP 포맷, 압축)
2. 이미지 lazy loading
3. CSS 인라인화

**예상 개선**: 3.2s → 2.1s

---

**FID (First Input Delay): 45ms** ✅
- 목표: ≤ 100ms
- 현재: 45ms
- 상태: 양호

---

**CLS (Cumulative Layout Shift): 0.15** 🟡
- 목표: ≤ 0.1
- 현재: 0.15
- 차이: +0.05

**원인**:
- 이미지 크기 미지정
- 동적 콘텐츠 삽입

**개선 방안**:
```typescript
// ❌ 현재
<img src="/politician.jpg" alt="Name" />

// ✅ 개선
<Image
  src="/politician.jpg"
  alt="Name"
  width={400}
  height={300}
/>
```

**예상 개선**: 0.15 → 0.08

---

### 번들 분석

**총 번들 크기**: 450 KB
- First Load JS: 280 KB
- Shared chunks: 170 KB

**큰 패키지**:
1. `@tanstack/react-query`: 80 KB (필요)
2. `date-fns`: 65 KB (최적화 가능 → 13 KB)
3. `lodash`: 50 KB (최적화 가능 → 5 KB)

**개선 방안**:
```typescript
// ❌ 전체 임포트
import _ from 'lodash';
import { format } from 'date-fns';

// ✅ 필요한 것만 임포트
import debounce from 'lodash/debounce';
import { format } from 'date-fns/format';
```

**예상 절감**: 450 KB → 343 KB (-24%)

---

## 백엔드 성능

### API 벤치마크 결과

**GET /api/politicians**:
- 평균: 145ms
- 최소: 89ms
- 최대: 523ms
- P95: 287ms

**상태**: 🟡 개선 필요 (목표: < 100ms)

**병목 구간**:
1. 데이터베이스 쿼리: 120ms (83%)
2. JSON 직렬화: 18ms (12%)
3. 인증 확인: 7ms (5%)

---

### 데이터베이스 쿼리 분석

**느린 쿼리 Top 3**:

1. **정치인 목록 + 평가 통계** (287ms)
```sql
SELECT
  politicians.*,
  AVG(evaluations.score) as avg_rating,
  COUNT(evaluations.id) as eval_count
FROM politicians
LEFT JOIN evaluations ON politicians.id = evaluations.politician_id
GROUP BY politicians.id
ORDER BY avg_rating DESC
LIMIT 20;
```

**문제**: 매번 집계 계산

**해결책**: Materialized View 사용
```sql
CREATE MATERIALIZED VIEW politicians_with_stats AS
SELECT
  p.*,
  COALESCE(AVG(e.score), 0) as avg_rating,
  COUNT(e.id) as eval_count
FROM politicians p
LEFT JOIN evaluations e ON p.id = e.politician_id
GROUP BY p.id;

CREATE INDEX idx_politicians_stats_rating
ON politicians_with_stats(avg_rating DESC);

-- 매 시간 갱신
REFRESH MATERIALIZED VIEW CONCURRENTLY politicians_with_stats;
```

**예상 개선**: 287ms → 45ms (-84%)

---

2. **검색 쿼리** (195ms)
```sql
SELECT * FROM politicians
WHERE name ILIKE '%keyword%'
OR party ILIKE '%keyword%';
```

**문제**: Full table scan, 인덱스 미사용

**해결책**: Full-text search 인덱스
```sql
-- tsvector 컬럼 추가
ALTER TABLE politicians
ADD COLUMN search_vector tsvector;

UPDATE politicians
SET search_vector =
  to_tsvector('korean', name) ||
  to_tsvector('korean', party);

CREATE INDEX idx_politicians_search
ON politicians USING GIN(search_vector);

-- 쿼리 개선
SELECT * FROM politicians
WHERE search_vector @@ to_tsquery('korean', 'keyword');
```

**예상 개선**: 195ms → 28ms (-86%)

---

## 캐싱 전략

### 현재 상태: ❌ 캐싱 미적용

### 권장 캐싱 전략

**1. API 레벨 (Next.js)**
```typescript
// app/api/politicians/route.ts
export async function GET() {
  const { data } = await supabase.from('politicians').select('*');

  return NextResponse.json(
    { data },
    {
      headers: {
        'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
      },
    }
  );
}
```

**2. 클라이언트 레벨 (React Query)**
```typescript
// hooks/usePoliticians.ts
import { useQuery } from '@tanstack/react-query';

export function usePoliticians() {
  return useQuery({
    queryKey: ['politicians'],
    queryFn: () => fetch('/api/politicians').then(r => r.json()),
    staleTime: 5 * 60 * 1000, // 5분
    cacheTime: 30 * 60 * 1000, // 30분
  });
}
```

**3. 데이터베이스 레벨 (Supabase)**
```sql
-- 자주 조회되는 집계 결과 캐싱
CREATE MATERIALIZED VIEW politicians_stats AS ...
REFRESH MATERIALIZED VIEW CONCURRENTLY politicians_stats;
```

**예상 효과**:
- 중복 요청 제거: 70% 감소
- 응답 시간: 145ms → 12ms (캐시 히트)
- 서버 부하: 60% 감소

---

## 우선순위별 개선 과제

### P0 - 즉시 개선 (성능 영향 큼)
1. **Materialized View 생성** - DB 쿼리 시간 84% 단축
2. **이미지 최적화** - LCP 35% 개선
3. **번들 크기 최적화** - First Load JS 24% 감소

### P1 - 단기 개선 (1주일)
1. **API 캐싱 구현** - 응답 시간 90% 단축
2. **React Query 도입** - 클라이언트 캐싱
3. **Full-text search 인덱스** - 검색 성능 86% 개선

### P2 - 중기 개선 (1개월)
1. **CDN 설정** - 정적 리소스 로딩 속도 향상
2. **가상 스크롤** - 대량 데이터 렌더링 최적화
3. **Service Worker** - 오프라인 지원

---

## 벤치마크 비교

| 항목 | 현재 | 목표 | 개선 후 예상 |
|------|------|------|-------------|
| Lighthouse Score | 85 | 95 | 96 |
| LCP | 3.2s | 2.5s | 2.1s |
| FID | 45ms | 100ms | 45ms |
| CLS | 0.15 | 0.1 | 0.08 |
| API 응답 (평균) | 145ms | 100ms | 45ms |
| 번들 크기 | 450KB | 300KB | 343KB |

---

## 액션 아이템

### 이번 주
- [ ] Materialized View 생성 및 갱신 스케줄 설정
- [ ] 이미지 최적화 (WebP 변환, 압축)
- [ ] date-fns, lodash 트리 쉐이킹

### 다음 주
- [ ] API 캐싱 구현
- [ ] React Query 설정
- [ ] Full-text search 인덱스 생성

### 다음 달
- [ ] CDN 설정 (Vercel 기본 설정 최적화)
- [ ] 가상 스크롤 구현
- [ ] 성능 모니터링 대시보드 구축

---

## 모니터링 설정

### Vercel Analytics
```bash
npm install @vercel/analytics
```

```typescript
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

### Web Vitals 추적
```typescript
// app/layout.tsx
'use client';
import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    console.log(metric);
    // 분석 서비스로 전송
  });

  return null;
}
```

---

## 다음 분석 일정

**권장 주기**: 주 1회
**다음 분석 예정일**: [YYYY-MM-DD]
```

---

**이 스킬을 활성화하면, 체계적인 성능 분석과 최적화로 PoliticianFinder 프로젝트의 사용자 경험을 크게 개선합니다.**
