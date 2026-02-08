# S4E1: News Crawler Infrastructure (신규 구현)

## Task 정보

- **Task ID**: S4E1
- **Task Name**: 뉴스 크롤러 인프라 구현
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)
- **Dependencies**: S1BI1 (Next.js 초기화)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**투자 뉴스 크롤링을 위한 베이스 크롤러 클래스 및 크롤러 관리자 구현**

- Abstract class로 베이스 크롤러 정의
- Rate limiting 및 Retry 로직 구현
- 크롤러 관리자 (싱글톤 패턴)
- Supabase 결과 저장
- **4가지 측면에서 구현** (안정성, 성능, 코드 품질, 확장성)

---

## 🎯 구현 필수 영역 (4가지)

### 1️⃣ 안정성 강화 (Reliability)
- ✅ Retry 로직 (Exponential Backoff)
- ✅ 타임아웃 설정 (AbortController)
- ✅ 에러 핸들링 강화
- ✅ Job 상태 관리 (pending/running/completed/failed)

### 2️⃣ 성능 최적화 (Performance)
- ✅ Rate limiting (사이트별 요청 간격)
- ✅ 병렬 크롤링 (여러 사이트 동시)
- ✅ 불필요한 재시도 방지
- ✅ 타임아웃 최적화 (10초)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ Abstract class로 인터페이스 통일
- ✅ 싱글톤 패턴 (크롤러 관리자)
- ✅ JSDoc 주석

### 4️⃣ 확장성 (Extensibility)
- ✅ 새 사이트 크롤러 추가 용이
- ✅ 크롤러별 독립적 설정
- ✅ Job 이력 관리
- ✅ 수동 실행 지원

---

## 작업 방식

### Step 1: 크롤러 패턴 설계

**Abstract Class 패턴:**

```
BaseCrawler (추상 클래스)
    ↓ 상속
NaverCrawler, OutstandingCrawler, ... (구체적 크롤러)
    ↓ 등록
CrawlerManager (싱글톤, 크롤러 관리)
```

**핵심 기능:**
1. HTML 가져오기 (`fetchHTML`)
2. Rate limiting (사이트 보호)
3. Retry 로직 (Exponential backoff)
4. 타임아웃 설정 (AbortController)
5. 크롤러 등록 및 실행

### Step 2: TypeScript 타입 정의

**인터페이스:**

```typescript
// ✅ 크롤링 결과
export interface CrawlResult {
  title: string
  url: string
  published_date: string
  content: string
  source: string
  raw_html?: string
}

// ✅ 크롤러 설정
export interface CrawlerConfig {
  site_name: string
  base_url: string
  rate_limit_ms: number          // 요청 간격 (밀리초)
  max_retries: number
  timeout_ms: number
}

// ✅ Job 상태
export interface CrawlerJob {
  id: string
  crawler_name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  results_count?: number
  error_message?: string
}
```

### Step 3: 구현 사항 적용

**예시 1: Retry 로직 (Exponential Backoff)**

```typescript
// ❌ 단순 구현: Retry 없음
async function fetchHTML(url: string): Promise<string> {
  const response = await fetch(url)
  return response.text()
}

// ✅ 개선: Exponential Backoff Retry
protected async fetchHTML(url: string): Promise<string> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt < this.config.max_retries; attempt++) {
    try {
      // AbortController로 타임아웃 설정
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), this.config.timeout_ms)

      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      })

      clearTimeout(timeout)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // Rate limiting (사이트 보호)
      await this.sleep(this.config.rate_limit_ms)

      return await response.text()
    } catch (error) {
      lastError = error as Error
      console.error(`Fetch attempt ${attempt + 1} failed:`, error)

      if (attempt < this.config.max_retries - 1) {
        // Exponential backoff: 1초, 2초, 4초
        await this.sleep(1000 * Math.pow(2, attempt))
      }
    }
  }

  throw new Error(
    `Failed to fetch ${url} after ${this.config.max_retries} attempts: ${lastError?.message}`
  )
}
```

**예시 2: 크롤러 관리자 (병렬 실행)**

```typescript
// ❌ 단순 구현: 순차 실행 (느림)
async function executeAll() {
  const results = []
  for (const crawler of crawlers) {
    const result = await crawler.crawl()
    results.push(result)
  }
  return results
}

// ✅ 개선: 병렬 실행 (빠름)
async executeAll(): Promise<Map<string, CrawlResult[]>> {
  const results = new Map<string, CrawlResult[]>()

  // Promise.all로 병렬 실행
  const crawlPromises = Array.from(this.crawlers.entries()).map(
    async ([name, crawler]) => {
      try {
        console.log(`Starting crawler: ${name}`)
        const crawlResults = await this.executeCrawler(name)
        results.set(name, crawlResults)
        console.log(`Completed crawler: ${name} (${crawlResults.length} items)`)
      } catch (error) {
        console.error(`Crawler failed: ${name}`, error)
        results.set(name, [])
      }
    }
  )

  await Promise.all(crawlPromises)

  return results
}
```

**예시 3: Job 상태 관리**

```typescript
// ❌ 단순 구현: 상태 관리 없음
async function executeCrawler(name: string) {
  const crawler = this.crawlers.get(name)
  return await crawler.crawl()
}

// ✅ 개선: Job 상태 관리
async executeCrawler(name: string): Promise<CrawlResult[]> {
  const crawler = this.crawlers.get(name)

  if (!crawler) {
    throw new Error(`Crawler not found: ${name}`)
  }

  const jobId = this.createJob(name)

  try {
    this.updateJobStatus(jobId, 'running')

    const results = await crawler.crawl()

    // 결과 저장 (Supabase)
    await this.saveResults(results)

    this.updateJobStatus(jobId, 'completed', results.length)

    return results
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    this.updateJobStatus(jobId, 'failed', 0, errorMessage)
    throw error
  }
}

private createJob(crawlerName: string): string {
  const jobId = `job-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const job: CrawlerJob = {
    id: jobId,
    crawler_name: crawlerName,
    status: 'pending',
  }

  this.jobs.set(jobId, job)
  return jobId
}

private updateJobStatus(
  jobId: string,
  status: CrawlerJob['status'],
  resultsCount?: number,
  errorMessage?: string
) {
  const job = this.jobs.get(jobId)
  if (!job) return

  job.status = status

  if (status === 'running') {
    job.started_at = new Date().toISOString()
  }

  if (status === 'completed' || status === 'failed') {
    job.completed_at = new Date().toISOString()
    job.results_count = resultsCount
    job.error_message = errorMessage
  }

  this.jobs.set(jobId, job)
}
```

### Step 4: Best Practice 적용

**Abstract Class 패턴:**
- 모든 크롤러가 동일한 인터페이스 구현
- `crawl()` 메서드는 추상 메서드
- 공통 로직은 부모 클래스에

**Singleton 패턴:**
```typescript
// ✅ 크롤러 관리자 싱글톤
export class CrawlerManager {
  // ...
}

export const crawlerManager = new CrawlerManager()
```

**에러 처리:**
```typescript
// ✅ 명확한 에러 메시지
throw new Error(`Failed to fetch ${url} after ${max_retries} attempts`)
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- Next.js 프로젝트 초기화됨
- Supabase 클라이언트 설정 완료

---

## 생성 파일 (2개)

### 1. lib/crawler/base-crawler.ts
**목표:** 베이스 크롤러 추상 클래스

**포함 메서드:**
1. **constructor()**: 설정 초기화
2. **crawl()**: 추상 메서드 (각 사이트별 구현)
3. **fetchHTML()**: HTML 가져오기 + Retry
4. **sleep()**: Rate limiting 유틸리티
5. **validate()**: 설정 검증
6. **getStatus()**: 크롤러 상태 조회

**개선 사항:**
- ✅ Retry 로직 (Exponential backoff)
- ✅ 타임아웃 설정 (AbortController)
- ✅ Rate limiting (최소 100ms)
- ✅ User-Agent 설정

### 2. lib/crawler/crawler-manager.ts
**목표:** 크롤러 관리자 (싱글톤)

**포함 메서드:**
1. **registerCrawler()**: 크롤러 등록
2. **getCrawlers()**: 등록된 크롤러 목록
3. **executeCrawler()**: 단일 크롤러 실행
4. **executeAll()**: 모든 크롤러 병렬 실행
5. **saveResults()**: Supabase에 결과 저장
6. **getJobHistory()**: Job 이력 조회

**개선 사항:**
- ✅ 싱글톤 패턴
- ✅ Job 상태 관리
- ✅ 병렬 실행 (Promise.all)
- ✅ Supabase 저장

---

## 완료 기준

### 필수 (Must Have)
- [ ] BaseCrawler 추상 클래스 구현
- [ ] fetchHTML() 메서드 (Retry + Timeout)
- [ ] Rate limiting 구현
- [ ] CrawlerManager 클래스 구현
- [ ] 크롤러 등록/실행 기능
- [ ] Job 상태 관리
- [ ] Supabase 결과 저장

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] Retry 로직 동작 확인
- [ ] Rate limiting 동작 확인
- [ ] Job 상태 관리 확인

### 구현 항목 (Implementation)
- [ ] 안정성: Retry, Timeout, 에러 처리
- [ ] 성능: Rate limiting, 병렬 실행
- [ ] 코드 품질: Abstract class, Singleton
- [ ] 확장성: 크롤러 등록, Job 이력

---

## 참조

### 재무 이론
- (해당 없음 - 크롤러 인프라)

### 디자인 패턴
- **Abstract Class**: 크롤러 인터페이스 통일
- **Singleton**: 크롤러 관리자 1개 인스턴스
- **Exponential Backoff**: Retry 간격 증가

### 관련 Task
- **S4E2**: News Parser (HTML 파싱)
- **S4E3**: Site-Specific Crawlers (6개 사이트)

---

## 주의사항

### 🔒 안정성

1. **Retry 로직**
   - 최대 3회 재시도
   - Exponential backoff (1초, 2초, 4초)

2. **타임아웃**
   - 기본 10초
   - AbortController 사용

### ⚡ 성능

1. **Rate Limiting**
   - 최소 100ms 간격
   - 사이트별로 다른 간격 설정 가능

2. **병렬 실행**
   - Promise.all로 여러 사이트 동시 크롤링
   - 개별 실패는 전체에 영향 없음

### 📝 코드 품질

1. **Abstract Class**
   - 모든 크롤러가 동일한 인터페이스
   - crawl() 메서드 필수 구현

2. **User-Agent**
   - 실제 브라우저처럼 설정
   - 차단 방지

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 2개
**라인 수**: ~330줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경
