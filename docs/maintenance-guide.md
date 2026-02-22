# ValueLink Maintenance Guide

**일상 점검, DB 관리, 크롤러 관리, 백업/복구, 성능 최적화**

**Version**: 1.0
**Last Updated**: 2026-02-22

---

## 목차

1. [일상적 점검 항목](#1-일상적-점검-항목)
2. [데이터베이스 관리](#2-데이터베이스-관리)
3. [크롤러 관리](#3-크롤러-관리)
4. [로그 모니터링](#4-로그-모니터링)
5. [백업 및 복구](#5-백업-및-복구)
6. [성능 최적화](#6-성능-최적화)
7. [보안 점검](#7-보안-점검)
8. [업데이트 절차](#8-업데이트-절차)

---

## 1. 일상적 점검 항목

### 1.1 매일 확인 (Daily)

#### 시스템 상태

**Vercel 대시보드 확인**:
```
https://vercel.com/[team]/valuelink
```

확인 사항:
- [ ] 배포 상태 (Latest Deployment: Success)
- [ ] 함수 실행 시간 (< 10초)
- [ ] 함수 에러율 (< 1%)
- [ ] Bandwidth 사용량

**Supabase 대시보드 확인**:
```
https://app.supabase.com/project/[project-id]
```

확인 사항:
- [ ] Database 상태 (Healthy)
- [ ] API 요청 수 (Daily Requests)
- [ ] Storage 사용량 (< 80%)
- [ ] Database 사이즈 (< 500MB)

#### 크롤러 실행 기록

```sql
-- 최근 7일간 수집 현황
SELECT
  DATE(created_at) as date,
  COUNT(*) as articles_count
FROM investment_news_articles
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

기대값: 매일 50-150건

#### 사용자 활동

```sql
-- 오늘 가입한 사용자
SELECT COUNT(*) as new_users
FROM users
WHERE DATE(created_at) = CURRENT_DATE;

-- 오늘 생성된 프로젝트
SELECT COUNT(*) as new_projects
FROM projects
WHERE DATE(created_at) = CURRENT_DATE;

-- 오늘 완료된 프로젝트
SELECT COUNT(*) as completed_projects
FROM projects
WHERE DATE(updated_at) = CURRENT_DATE
  AND status = 'completed';
```

### 1.2 주간 확인 (Weekly)

#### 성능 메트릭

**Vercel Analytics**:
- [ ] 평균 페이지 로딩 시간 (< 3초)
- [ ] Core Web Vitals (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] 에러율 (< 1%)

**Supabase Performance**:
```sql
-- 느린 쿼리 확인
SELECT
  query,
  calls,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 1초 이상
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### DB 크기 확인

```sql
-- 테이블별 크기
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Storage 사용량

```sql
-- 사용자별 업로드 파일 크기
SELECT
  u.email,
  COUNT(*) as file_count,
  SUM(d.file_size) / 1024 / 1024 as total_mb
FROM dcf_documents d
JOIN users u ON d.uploaded_by = u.user_id
GROUP BY u.email
ORDER BY total_mb DESC
LIMIT 10;
```

### 1.3 월간 확인 (Monthly)

#### 보안 취약점 스캔

```bash
# npm 의존성 취약점 스캔
npm audit

# 자동 수정 가능한 취약점 패치
npm audit fix

# 심각한 취약점만 확인
npm audit --production --audit-level=high
```

#### RLS 정책 검토

```sql
-- 모든 RLS 정책 확인
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

#### 비즈니스 메트릭

```sql
-- 월간 신규 고객
SELECT COUNT(*) as new_customers
FROM users
WHERE role = 'customer'
  AND created_at >= DATE_TRUNC('month', CURRENT_DATE);

-- 월간 완료 프로젝트
SELECT COUNT(*) as completed_projects
FROM projects
WHERE status = 'completed'
  AND updated_at >= DATE_TRUNC('month', CURRENT_DATE);

-- 평가법별 사용 빈도
SELECT
  unnest(requested_methods) as method,
  COUNT(*) as count
FROM projects
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY method
ORDER BY count DESC;
```

---

## 2. 데이터베이스 관리

### 2.1 인덱스 최적화

#### 느린 쿼리 확인

```sql
-- 실행 시간이 긴 쿼리 (1초 이상)
SELECT
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY total_exec_time DESC
LIMIT 20;
```

#### 인덱스 추가

```sql
-- 예시: projects 테이블의 status + created_at 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_projects_status_created
ON projects(status, created_at DESC);

-- 예시: investment_news_articles의 score 인덱스
CREATE INDEX IF NOT EXISTS idx_news_score
ON investment_news_articles(score DESC)
WHERE processed = false;
```

#### 사용하지 않는 인덱스 확인

```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 2.2 데이터 정리

#### 오래된 데이터 삭제

```sql
-- 1년 이상 된 완료 프로젝트 → project_history로 이동
INSERT INTO project_history (
  project_id, user_id, accountant_id, company_name_kr,
  completed_at, final_values
)
SELECT
  project_id, user_id, accountant_id, company_name_kr,
  updated_at, NULL
FROM projects
WHERE status = 'completed'
  AND updated_at < NOW() - INTERVAL '1 year';

-- 원본 삭제
DELETE FROM projects
WHERE status = 'completed'
  AND updated_at < NOW() - INTERVAL '1 year';
```

#### 중복 데이터 확인

```sql
-- 중복 이메일 확인
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- 중복 뉴스 기사 확인 (같은 URL)
SELECT article_url, COUNT(*) as count
FROM investment_news_articles
GROUP BY article_url
HAVING COUNT(*) > 1;
```

### 2.3 테이블 VACUUM

```sql
-- 모든 테이블 VACUUM (주간 실행 권장)
VACUUM ANALYZE;

-- 특정 테이블만 VACUUM
VACUUM ANALYZE projects;
VACUUM ANALYZE investment_news_articles;

-- VACUUM FULL (월간 실행 권장, 테이블 락 발생)
VACUUM FULL ANALYZE projects;
```

---

## 3. 크롤러 관리

### 3.1 상태 점검

#### 수동 실행

```bash
# 로컬에서 크롤러 테스트
npm run deal-news-tracker

# 결과 확인
# - 수집 건수 출력
# - 에러 메시지 확인
# - 실행 시간 체크
```

#### 수집 결과 확인

```sql
-- 사이트별 수집 현황 (최근 7일)
SELECT
  site_name,
  COUNT(*) as articles_count,
  AVG(score) as avg_score
FROM investment_news_articles
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY site_name
ORDER BY articles_count DESC;
```

### 3.2 실패 원인 파악

#### CSS 선택자 변경 확인

사이트 레이아웃이 변경되면 크롤러가 데이터를 수집하지 못합니다.

**증상**:
- 특정 사이트만 0건 수집
- 에러 없이 빈 배열 반환

**해결**:
1. 해당 사이트 직접 접속
2. 브라우저 개발자 도구 (F12)
3. Elements 탭에서 기사 제목, URL 엘리먼트 확인
4. CSS 선택자 업데이트

```typescript
// 예시: 벤처스퀘어 선택자 변경
// Before
$('article.post h2.entry-title a')

// After (사이트 리뉴얼 시)
$('article.article-item h3.title a')
```

#### Rate Limiting

**증상**:
- 429 Too Many Requests 에러
- 특정 사이트만 타임아웃

**해결**:
```typescript
// 요청 간 대기 시간 증가
await new Promise(resolve => setTimeout(resolve, 3000));  // 2초 → 3초

// 동시 요청 수 제한
const results = [];
for (const url of urls) {
  const data = await fetch(url);
  results.push(data);
  await sleep(2000);  // 순차 실행
}
```

#### 타임아웃

**증상**:
- `Error: timeout of 10000ms exceeded`

**해결**:
```typescript
// axios 타임아웃 증가
axios.get(url, {
  timeout: 20000  // 10초 → 20초
})
```

#### 403 Forbidden / 404 Not Found

**증상**:
- 특정 사이트만 접근 불가

**해결**:
```typescript
// User-Agent 추가/변경
headers: {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'Accept': 'text/html,application/xhtml+xml',
  'Accept-Language': 'ko-KR,ko;q=0.9',
}
```

### 3.3 CSS 선택자 업데이트

**프로세스**:
1. 사이트 접속 및 F12 개발자 도구
2. 기사 엘리먼트 우클릭 → Copy → Copy selector
3. 코드에서 해당 선택자 업데이트
4. 로컬 테스트
5. Git commit & push

**예시 (VentureSquare)**:
```typescript
// Valuation_Company/scripts/investment-news-scraper/bill-news-tracker-enhanced.js

extractData(html: string): Article[] {
  const $ = cheerio.load(html);
  const articles: Article[] = [];

  // 업데이트된 선택자
  $('article.post-item').each((_, element) => {
    const title = $(element).find('h2.post-title a').text().trim();
    const url = $(element).find('h2.post-title a').attr('href');
    // ...
  });

  return articles;
}
```

---

## 4. 로그 모니터링

### 4.1 Vercel 로그

**대시보드 접속**:
```
https://vercel.com/[team]/valuelink/logs
```

**필터**:
- `ERROR` - 에러만 보기
- `api/cron` - Cron Job 로그만 보기
- `2xx` - 성공 요청만 보기

**주요 에러 패턴**:

| 에러 | 원인 | 해결 |
|------|------|------|
| `FUNCTION_INVOCATION_TIMEOUT` | 함수 실행 시간 초과 (10초) | 쿼리 최적화, 병렬 처리 |
| `DEPLOYMENT_ERROR` | 빌드 실패 | TypeScript 에러 수정 |
| `RATE_LIMIT_EXCEEDED` | API 호출 한도 초과 | Caching, 요청 수 감소 |

### 4.2 Supabase 로그

**대시보드 접속**:
```
https://app.supabase.com/project/[project-id]/logs
```

**로그 종류**:
- **API Logs**: REST API 요청
- **Database Logs**: SQL 쿼리 로그
- **Auth Logs**: 인증 이벤트

**느린 쿼리 확인**:
```sql
-- 실행 시간 1초 이상 쿼리
SELECT * FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY total_exec_time DESC;
```

### 4.3 커스텀 로깅

**lib/logger.ts**:
```typescript
export function logError(error: Error, context?: Record<string, any>) {
  console.error('[ERROR]', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString()
  });

  // Sentry 또는 다른 에러 트래킹 서비스로 전송 (선택)
  // Sentry.captureException(error);
}

export function logInfo(message: string, data?: Record<string, any>) {
  console.log('[INFO]', {
    message,
    data,
    timestamp: new Date().toISOString()
  });
}
```

---

## 5. 백업 및 복구

### 5.1 데이터베이스 백업

#### Supabase 자동 백업

Supabase는 매일 자동 백업을 수행합니다 (7일 보관).

**복구 방법**:
1. Supabase Dashboard → Database → Backups
2. 원하는 시점 선택
3. "Restore" 클릭

#### 수동 백업 (pg_dump)

```bash
# 전체 DB 백업
pg_dump -h db.your-project.supabase.co \
        -U postgres \
        -d postgres \
        -F c \
        -f valuelink_backup_$(date +%Y%m%d).dump

# 특정 테이블만 백업
pg_dump -h db.your-project.supabase.co \
        -U postgres \
        -d postgres \
        -t projects -t users \
        -F c \
        -f valuelink_partial_$(date +%Y%m%d).dump
```

#### 백업을 S3에 저장

```bash
# AWS CLI 설치 필요
aws s3 cp valuelink_backup_20260222.dump \
          s3://valuelink-backups/$(date +%Y/%m/%d)/
```

### 5.2 데이터베이스 복구

#### Supabase Dashboard에서 복구

1. Dashboard → Database → Backups
2. 복구할 시점 선택
3. "Restore" 클릭
4. 확인 (기존 데이터는 덮어씌워짐)

#### pg_restore로 복구

```bash
# dump 파일에서 복구
pg_restore -h db.your-project.supabase.co \
           -U postgres \
           -d postgres \
           -c \
           valuelink_backup_20260222.dump
```

### 5.3 Storage 백업

```bash
# Supabase Storage 파일 다운로드 (모든 버킷)
# (Supabase CLI 사용)
supabase storage download --project-ref your-project-id

# 특정 버킷만 다운로드
supabase storage download --bucket documents --project-ref your-project-id
```

---

## 6. 성능 최적화

### 6.1 데이터베이스 쿼리 최적화

#### N+1 문제 방지

**❌ Bad (N+1 쿼리)**:
```typescript
// 프로젝트 목록 조회
const projects = await supabase.from('projects').select('*');

// 각 프로젝트의 사용자 정보 조회 (N번 쿼리)
for (const project of projects.data) {
  const user = await supabase
    .from('users')
    .select('*')
    .eq('user_id', project.user_id)
    .single();
}
```

**✅ Good (1번 쿼리)**:
```typescript
// JOIN으로 한 번에 조회
const { data } = await supabase
  .from('projects')
  .select(`
    *,
    user:users(name, email),
    accountant:users(name, email)
  `);
```

#### 인덱스 활용

```sql
-- 자주 사용하는 WHERE 조건에 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_projects_status_created
ON projects(status, created_at DESC);

-- 복합 인덱스 (status + user_id)
CREATE INDEX IF NOT EXISTS idx_projects_status_user
ON projects(status, user_id);
```

### 6.2 프론트엔드 최적화

#### 이미지 최적화

**Next.js Image 컴포넌트 사용**:
```typescript
import Image from 'next/image';

<Image
  src="/images/logo.png"
  alt="ValueLink Logo"
  width={200}
  height={50}
  priority  // LCP 이미지는 priority 추가
/>
```

#### 코드 스플리팅

```typescript
// 동적 import로 필요 시에만 로드
const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false  // 클라이언트에서만 로드
});
```

#### 서버 컴포넌트 활용

```typescript
// app/projects/page.tsx (Server Component)
async function ProjectsPage() {
  // 서버에서 데이터 fetch (클라이언트 번들에 포함 안 됨)
  const projects = await getProjects();

  return <ProjectList projects={projects} />;
}
```

#### Streaming으로 빠른 초기 렌더링

```typescript
import { Suspense } from 'react';

export default function Page() {
  return (
    <div>
      <h1>프로젝트 목록</h1>
      <Suspense fallback={<LoadingSkeleton />}>
        <ProjectList />  // 비동기 컴포넌트
      </Suspense>
    </div>
  );
}
```

#### 캐싱

```typescript
// Next.js fetch with cache
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 }  // 1시간 캐싱
});

// React Query로 클라이언트 캐싱
const { data } = useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  staleTime: 5 * 60 * 1000  // 5분
});
```

### 6.3 크롤러 최적화

#### 병렬 처리

```typescript
// 순차 실행 (느림)
for (const crawler of crawlers) {
  await crawler.crawl();
}

// 병렬 실행 (빠름)
await Promise.all(
  crawlers.map(crawler => crawler.crawl())
);
```

#### Rate Limiting 조정

```typescript
// 사이트별 대기 시간 차등 적용
const delays = {
  venturesquare: 2000,
  thevc: 3000,  // 엄격한 사이트는 길게
  google: 1000
};

await new Promise(resolve => setTimeout(resolve, delays[siteName]));
```

---

## 7. 보안 점검

### 7.1 의존성 보안 취약점

```bash
# npm 취약점 스캔
npm audit

# 심각한 취약점만 확인
npm audit --production --audit-level=high

# 자동 수정
npm audit fix

# 강제 업데이트 (주의: Breaking changes 가능)
npm audit fix --force
```

### 7.2 GitHub Dependabot

**.github/dependabot.yml**:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### 7.3 RLS 정책 검토

```sql
-- 모든 RLS 정책 확인
SELECT tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public';

-- RLS가 활성화되지 않은 테이블 확인
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename NOT IN (
    SELECT tablename FROM pg_policies
  );
```

### 7.4 환경 변수 로테이션

**주기**: 3개월마다

**변경 항목**:
- `SUPABASE_ANON_KEY` (Supabase에서 재발급)
- `CRON_SECRET` (랜덤 문자열 생성)
- `RESEND_API_KEY` (Resend에서 재발급)
- AI API 키 (필요 시)

**절차**:
1. 새 키 발급
2. Vercel 환경 변수 업데이트
3. 재배포 (`vercel --prod`)
4. 이전 키 무효화

---

## 8. 업데이트 절차

### 8.1 의존성 업데이트

#### Minor/Patch 업데이트

```bash
# 최신 버전 확인
npm outdated

# 업데이트
npm update

# 테스트
npm test

# 커밋
git add package.json package-lock.json
git commit -m "chore: Update dependencies"
```

#### Major 업데이트

```bash
# 한 번에 하나씩 업데이트
npm install next@latest

# 테스트
npm test
npm run build

# 문제 없으면 커밋
git commit -m "chore: Update Next.js to 15.0"
```

### 8.2 Next.js 업데이트

**공식 가이드**: https://nextjs.org/docs/app/building-your-application/upgrading

```bash
# Next.js Codemods 사용
npx @next/codemod@latest upgrade latest

# 수동 업데이트
npm install next@latest react@latest react-dom@latest

# 빌드 테스트
npm run build

# 로컬 테스트
npm run dev
```

### 8.3 Supabase 마이그레이션

**새 테이블 추가**:
```sql
-- migration.sql
CREATE TABLE IF NOT EXISTS new_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Supabase CLI로 적용**:
```bash
supabase db push
```

---

**Document Version**: 1.0
**Last Updated**: 2026-02-22
**Maintainer**: ValueLink Team
