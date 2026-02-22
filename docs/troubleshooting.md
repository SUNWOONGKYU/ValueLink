# ValueLink Troubleshooting Guide

**빌드, 런타임, DB, 인증, 크롤러, 배포, 성능 문제 해결**

**Version**: 1.0
**Last Updated**: 2026-02-22

---

## 목차

1. [일반적인 문제](#1-일반적인-문제)
2. [빌드 에러](#2-빌드-에러)
3. [런타임 에러](#3-런타임-에러)
4. [데이터베이스 에러](#4-데이터베이스-에러)
5. [인증 에러](#5-인증-에러)
6. [크롤러 에러](#6-크롤러-에러)
7. [배포 문제](#7-배포-문제)
8. [성능 문제](#8-성능-문제)

---

## 1. 일반적인 문제

### 1.1 로컬 서버가 시작되지 않음

#### 증상
```bash
$ npm run dev
Error: Cannot find module '@/lib/supabase/client'
```

#### 원인
TypeScript path alias 설정 오류 또는 모듈 미설치

#### 해결
```bash
# 1. node_modules 재설치
rm -rf node_modules package-lock.json
npm install

# 2. tsconfig.json 확인
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}

# 3. 서버 재시작
npm run dev
```

---

### 1.2 환경 변수가 undefined

#### 증상
```typescript
Error: NEXT_PUBLIC_SUPABASE_URL is not defined
```

#### 원인
- `.env.local` 파일 없음
- 환경 변수 prefix 오류 (`NEXT_PUBLIC_` 누락)
- 서버 재시작 안 함

#### 해결

**❌ Bad**:
```env
SUPABASE_URL=https://xxx.supabase.co
```

**✅ Good**:
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

```bash
# .env.local 파일 확인
cat .env.local

# 서버 재시작
npm run dev
```

**중요**: 클라이언트에서 사용하는 환경 변수는 반드시 `NEXT_PUBLIC_` prefix 필요!

---

### 1.3 Supabase 연결 실패

#### 증상
```typescript
Error: Invalid URL: undefined
```

#### 원인
- 환경 변수 미설정
- Supabase URL 형식 오류
- 네트워크 문제

#### 해결

```typescript
// lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

**URL 형식 확인**:
- ✅ `https://your-project.supabase.co`
- ❌ `https://your-project.supabase.co/`  (끝에 슬래시 있으면 안 됨)

---

## 2. 빌드 에러

### 2.1 TypeScript 컴파일 에러

#### 증상
```bash
Type 'string | undefined' is not assignable to type 'string'
```

#### 원인
Optional 타입을 non-null로 사용

#### 해결

**❌ Bad**:
```typescript
const url: string = process.env.NEXT_PUBLIC_SUPABASE_URL;
```

**✅ Good (Option 1: Non-null assertion)**:
```typescript
const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
```

**✅ Good (Option 2: Type guard)**:
```typescript
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
if (!url) {
  throw new Error('NEXT_PUBLIC_SUPABASE_URL is required');
}
// 이제 url은 string 타입
```

---

### 2.2 Module not found

#### 증상
```bash
Module not found: Can't resolve '@/components/Button'
```

#### 원인
- 파일 경로 오류
- Import 경로 대소문자 불일치
- TypeScript path alias 미설정

#### 해결

```typescript
// ❌ Bad
import Button from '@/components/button';  // 대소문자 틀림

// ✅ Good
import Button from '@/components/Button';
```

```json
// tsconfig.json 확인
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

### 2.3 Next.js 빌드 실패

#### 증상
```bash
Error: You're importing a component that needs useState.
It only works in a Client Component but none of its parents are marked with "use client"
```

#### 원인
Server Component에서 Client-only 훅 사용

#### 해결

**❌ Bad (Server Component에서 useState)**:
```typescript
// app/page.tsx
export default function Page() {
  const [count, setCount] = useState(0);  // 에러!
  return <div>{count}</div>;
}
```

**✅ Good (Client Component로 분리)**:
```typescript
// components/Counter.tsx
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return <div>{count}</div>;
}

// app/page.tsx (Server Component)
import { Counter } from '@/components/Counter';

export default function Page() {
  return <Counter />;
}
```

---

## 3. 런타임 에러

### 3.1 Hydration 에러

#### 증상
```
Error: Hydration failed because the initial UI does not match
what was rendered on the server
```

#### 원인
- SSR 렌더링과 클라이언트 렌더링 불일치
- `Date.now()`, `Math.random()` 등 동적 값 사용
- localStorage, window 객체 접근

#### 해결

**❌ Bad (서버/클라이언트 값 다름)**:
```typescript
export default function Page() {
  return <div>{new Date().toISOString()}</div>;  // 서버/클라이언트 시간 다름
}
```

**✅ Good (useEffect로 클라이언트에서만 렌더)**:
```typescript
'use client';

import { useState, useEffect } from 'react';

export default function Page() {
  const [date, setDate] = useState<string | null>(null);

  useEffect(() => {
    setDate(new Date().toISOString());
  }, []);

  if (!date) return null;
  return <div>{date}</div>;
}
```

**✅ Good (suppressHydrationWarning 사용)**:
```typescript
<div suppressHydrationWarning>
  {new Date().toISOString()}
</div>
```

---

### 3.2 Supabase RLS 에러

#### 증상
```typescript
Error: Row level security policy violated
```

#### 원인
RLS 정책이 현재 사용자의 접근을 차단

#### 해결

```sql
-- RLS 정책 확인
SELECT * FROM pg_policies WHERE tablename = 'projects';

-- 정책 수정 (예: 본인 프로젝트만 조회)
DROP POLICY IF EXISTS "Users can view own projects" ON projects;

CREATE POLICY "Users can view own projects"
ON projects FOR SELECT
USING (auth.uid() = user_id OR auth.uid() = accountant_id);
```

**디버깅**:
```typescript
// 현재 사용자 확인
const { data: { user } } = await supabase.auth.getUser();
console.log('Current user:', user?.id);

// RLS 우회 (서버 사이드에서만 사용)
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!  // service_role 키 사용
);
```

---

### 3.3 CORS 에러

#### 증상
```
Access to fetch at 'https://api.example.com' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

#### 원인
- API 서버에서 CORS 헤더 미설정
- Supabase CORS 설정 오류

#### 해결

**Supabase**:
```typescript
// Supabase는 기본적으로 모든 origin 허용
// 제한하려면 Dashboard → Settings → API → CORS
```

**Custom API (Next.js API Routes)**:
```typescript
// app/api/data/route.ts
export async function GET(request: Request) {
  const response = await fetch('https://external-api.com/data');
  const data = await response.json();

  return new Response(JSON.stringify(data), {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
  });
}
```

---

## 4. 데이터베이스 에러

### 4.1 Connection timeout

#### 증상
```
Error: Connection timeout
```

#### 원인
- DB 과부하
- 네트워크 문제
- 너무 많은 동시 연결

#### 해결

```typescript
// 연결 풀 크기 제한
const supabase = createClient(url, key, {
  db: {
    schema: 'public'
  },
  global: {
    headers: {}
  }
});

// 타임아웃 증가
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .abortSignal(AbortSignal.timeout(30000));  // 30초
```

**Supabase Dashboard 확인**:
- Database → Connections
- 동시 연결 수 확인 (Max: 100)

---

### 4.2 Slow query

#### 증상
```
Warning: Query took 5.2 seconds
```

#### 원인
- 인덱스 누락
- N+1 쿼리
- 불필요한 JOIN

#### 해결

**인덱스 추가**:
```sql
-- EXPLAIN ANALYZE로 실행 계획 확인
EXPLAIN ANALYZE
SELECT * FROM projects
WHERE status = 'in_progress'
ORDER BY created_at DESC;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_projects_status_created
ON projects(status, created_at DESC);
```

**N+1 방지**:
```typescript
// ❌ Bad (N+1 쿼리)
const projects = await supabase.from('projects').select('*');
for (const project of projects.data) {
  const user = await supabase
    .from('users')
    .select('*')
    .eq('user_id', project.user_id)
    .single();
}

// ✅ Good (1번 쿼리)
const { data } = await supabase
  .from('projects')
  .select('*, user:users(*)');
```

---

### 4.3 Deadlock

#### 증상
```
Error: deadlock detected
```

#### 원인
- 두 트랜잭션이 서로의 Lock을 대기
- UPDATE 순서 불일치

#### 해결

```sql
-- 트랜잭션에서 항상 같은 순서로 Lock 획득
BEGIN;
  -- 항상 id 순서로 UPDATE
  UPDATE projects SET status = 'completed'
  WHERE id IN (1, 2, 3)
  ORDER BY id;  -- 순서 보장
COMMIT;
```

**Deadlock 확인**:
```sql
SELECT * FROM pg_stat_activity
WHERE wait_event_type = 'Lock';
```

---

## 5. 인증 에러

### 5.1 JWT expired

#### 증상
```
Error: JWT expired
```

#### 원인
- 액세스 토큰 만료 (1시간)
- 리프레시 토큰 만료 (7일)

#### 해결

```typescript
// Supabase는 자동으로 토큰 갱신 (autoRefreshToken: true)
const supabase = createClient(url, key, {
  auth: {
    autoRefreshToken: true,
    persistSession: true
  }
});

// 수동 갱신
const { data, error } = await supabase.auth.refreshSession();
```

---

### 5.2 OAuth 리다이렉트 실패

#### 증상
OAuth 로그인 후 앱으로 돌아오지 않음

#### 원인
- Redirect URL 미설정
- Callback URL 오류

#### 해결

**Supabase Dashboard 설정**:
```
Authentication → URL Configuration → Redirect URLs
```

추가할 URL:
```
http://localhost:3000/auth/callback
https://valuelink.vercel.app/auth/callback
```

**코드**:
```typescript
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: `${window.location.origin}/auth/callback`
  }
});
```

---

### 5.3 세션 유지 안 됨

#### 증상
페이지 새로고침 시 로그아웃됨

#### 원인
- 쿠키 설정 오류
- localStorage 비활성화
- `persistSession: false`

#### 해결

```typescript
// ❌ Bad
const supabase = createClient(url, key, {
  auth: {
    persistSession: false  // 세션 유지 안 됨
  }
});

// ✅ Good
const supabase = createClient(url, key, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
});
```

---

## 6. 크롤러 에러

### 6.1 0건 수집

#### 증상
크롤러 실행 후 0건 수집

#### 원인
- CSS 선택자 변경
- 사이트 IP 차단
- 로봇 탐지

#### 해결

**CSS 선택자 확인**:
```typescript
// 브라우저 F12 → Elements → Copy selector
const title = $('article.post h2.entry-title a').text();

// 선택자 변경 시 업데이트
const title = $('article.article-item h3.title a').text();
```

**User-Agent 변경**:
```typescript
const response = await axios.get(url, {
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'ko-KR,ko;q=0.9'
  }
});
```

---

### 6.2 Timeout

#### 증상
```
Error: timeout of 10000ms exceeded
```

#### 원인
- 서버 응답 느림
- 네트워크 불안정

#### 해결

```typescript
// 타임아웃 증가
const response = await axios.get(url, {
  timeout: 20000  // 10초 → 20초
});

// 재시도 로직
async function fetchWithRetry(url: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await axios.get(url, { timeout: 10000 });
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 2000));  // 2초 대기
    }
  }
}
```

---

### 6.3 Rate limiting

#### 증상
```
Error: Request failed with status code 429
```

#### 원인
- Too Many Requests
- 사이트에서 IP 차단

#### 해결

```typescript
// 요청 간 대기 시간 증가
for (const url of urls) {
  const data = await fetch(url);
  await new Promise(resolve => setTimeout(resolve, 3000));  // 2초 → 3초
}

// Exponential backoff
async function fetchWithBackoff(url: string) {
  let delay = 1000;
  let retries = 5;

  for (let i = 0; i < retries; i++) {
    try {
      return await axios.get(url);
    } catch (error) {
      if (error.response?.status !== 429) throw error;
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2;  // 1초 → 2초 → 4초 → 8초 → 16초
    }
  }
}
```

---

## 7. 배포 문제

### 7.1 Vercel 빌드 실패

#### 증상
```
Error: Command "npm run build" exited with 1
```

#### 원인
- TypeScript 에러
- 환경 변수 미설정
- 의존성 설치 실패

#### 해결

**로컬에서 빌드 테스트**:
```bash
npm run build
```

**Vercel Dashboard에서 환경 변수 확인**:
```
Settings → Environment Variables
```

필요한 변수:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

**빌드 로그 확인**:
```
Vercel Dashboard → Deployments → [최신 배포] → Logs
```

---

### 7.2 Vercel Cron 작동 안 함

#### 증상
Cron Job이 실행되지 않음

#### 원인
- `vercel.json` 설정 오류
- CRON_SECRET 인증 실패
- Vercel Cron 미활성화

#### 해결

**vercel.json 확인**:
```json
{
  "crons": [
    {
      "path": "/api/cron/collect-news",
      "schedule": "0 23 * * *"
    }
  ]
}
```

**CRON_SECRET 검증**:
```typescript
// api/cron/collect-news/route.ts
export async function GET(request: Request) {
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }
  // ...
}
```

**Vercel Dashboard 확인**:
```
Settings → Cron Jobs
```

Cron이 활성화되어 있는지 확인

---

### 7.3 프로덕션 환경 변수 undefined

#### 증상
```
Error: NEXT_PUBLIC_SUPABASE_URL is not defined
```

#### 원인
- Vercel에 환경 변수 미등록
- 환경별 변수 설정 오류 (Production, Preview, Development)

#### 해결

**Vercel Dashboard**:
```
Settings → Environment Variables
```

각 환경별로 체크:
- [x] Production
- [x] Preview
- [x] Development

**재배포**:
```bash
vercel --prod
```

---

## 8. 성능 문제

### 8.1 페이지 로딩 느림

#### 증상
페이지 로딩 시간 > 5초

#### 원인
- 이미지 최적화 안 됨
- JavaScript 번들 크기 큼
- Server Component 미활용
- Streaming 미사용

#### 해결

**이미지 최적화**:
```typescript
// ❌ Bad
<img src="/images/logo.png" width="200" height="50" />

// ✅ Good
import Image from 'next/image';

<Image
  src="/images/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority  // LCP 이미지
/>
```

**번들 크기 줄이기**:
```typescript
// 동적 import
const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  ssr: false,
  loading: () => <p>Loading...</p>
});
```

**Server Component 활용**:
```typescript
// app/projects/page.tsx (Server Component)
async function ProjectsPage() {
  const projects = await getProjects();  // 서버에서 fetch
  return <ProjectList projects={projects} />;
}
```

**Streaming으로 빠른 초기 렌더링**:
```typescript
import { Suspense } from 'react';

export default function Page() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <DataComponent />
    </Suspense>
  );
}
```

---

### 8.2 API 응답 느림

#### 증상
API 응답 시간 > 2초

#### 원인
- DB 쿼리 최적화 안 됨
- 캐싱 미사용
- 순차 요청 (병렬 가능)

#### 해결

**DB 쿼리 최적화**:
```sql
-- 느린 쿼리 확인
EXPLAIN ANALYZE
SELECT * FROM projects WHERE status = 'in_progress';

-- 인덱스 추가
CREATE INDEX idx_projects_status ON projects(status);
```

**캐싱 (React Query)**:
```typescript
const { data } = useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  staleTime: 5 * 60 * 1000  // 5분 캐싱
});
```

**병렬 요청**:
```typescript
// ❌ Bad (순차)
const user = await fetchUser();
const projects = await fetchProjects();

// ✅ Good (병렬)
const [user, projects] = await Promise.all([
  fetchUser(),
  fetchProjects()
]);
```

---

### 8.3 DCF 계산 느림

#### 증상
DCF 계산 시간 > 5초

#### 원인
- IRR 계산 반복 횟수 많음
- 민감도 분석 비효율적

#### 해결

**IRR 반복 횟수 제한**:
```typescript
function calculateIRR(cashFlows: number[], maxIterations = 50) {
  let irr = 0.1;
  let tolerance = 0.0001;

  for (let i = 0; i < maxIterations; i++) {  // 100 → 50
    const npv = calculateNPV(cashFlows, irr);
    const derivative = calculateNPVDerivative(cashFlows, irr);
    const nextIRR = irr - npv / derivative;

    if (Math.abs(nextIRR - irr) < tolerance) {
      return nextIRR;
    }
    irr = nextIRR;
  }
  return irr;
}
```

**민감도 분석 병렬 처리**:
```typescript
// ❌ Bad (순차)
const results = [];
for (const scenario of scenarios) {
  results.push(await calculateScenario(scenario));
}

// ✅ Good (병렬)
const results = await Promise.all(
  scenarios.map(scenario => calculateScenario(scenario))
);
```

---

**Document Version**: 1.0
**Last Updated**: 2026-02-22
**Maintainer**: ValueLink Team
