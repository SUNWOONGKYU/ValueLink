# S4E1 Verification

## 검증 대상

- **Task ID**: S4E1
- **Task Name**: 뉴스 크롤러 인프라
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

- [ ] **`lib/crawler/base-crawler.ts` 존재** - 베이스 크롤러 추상 클래스
- [ ] **`lib/crawler/crawler-manager.ts` 존재** - 크롤러 관리자

---

### 3. 핵심 기능 테스트

#### 3.1 Base Crawler (`base-crawler.ts`)

- [ ] **CrawlResult 인터페이스**
  - title, url, published_date, content, source 필드 정의
  - raw_html (optional) 필드

- [ ] **CrawlerConfig 인터페이스**
  - site_name, base_url, rate_limit_ms, max_retries, timeout_ms 필드 정의

- [ ] **BaseCrawler 추상 클래스**
  - `constructor(config: CrawlerConfig)` 구현
  - `abstract crawl(): Promise<CrawlResult[]>` 선언
  - `protected fetchHTML(url: string): Promise<string>` 구현

- [ ] **fetchHTML() 메서드**
  - Fetch API 사용
  - AbortController로 timeout 구현
  - User-Agent 헤더 설정 (브라우저 에뮬레이션)
  - HTTP 에러 시 예외 발생 (response.ok 확인)
  - Rate limiting: `sleep(rate_limit_ms)` 호출
  - Retry 로직: max_retries만큼 재시도
  - Exponential backoff: 1초, 2초, 4초

- [ ] **sleep() 유틸리티**
  - Promise 기반 setTimeout 구현

- [ ] **validate() 메서드**
  - base_url 필수 확인
  - rate_limit_ms >= 100 확인
  - 에러 배열 반환

- [ ] **getStatus() 메서드**
  - site_name, base_url, rate_limit_ms 반환

#### 3.2 Crawler Manager (`crawler-manager.ts`)

- [ ] **CrawlerJob 인터페이스**
  - id, crawler_name, status, started_at, completed_at, results_count, error_message 필드

- [ ] **CrawlerManager 클래스**
  - `private crawlers: Map<string, BaseCrawler>` 선언
  - `private jobs: Map<string, CrawlerJob>` 선언

- [ ] **registerCrawler() 메서드**
  - 크롤러를 Map에 추가
  - 콘솔 로그 출력

- [ ] **getCrawlers() 메서드**
  - 등록된 크롤러 이름 목록 반환

- [ ] **executeCrawler() 메서드**
  - 크롤러가 없으면 에러 발생
  - Job 생성 (createJob)
  - 상태를 'running'으로 변경 (updateJobStatus)
  - crawler.crawl() 실행
  - 결과 저장 (saveResults)
  - 상태를 'completed'로 변경
  - 에러 시 'failed' 상태로 변경

- [ ] **executeAll() 메서드**
  - 모든 크롤러 순차 실행
  - 각 크롤러 결과를 Map으로 반환
  - 개별 크롤러 실패 시 빈 배열 저장하고 계속 진행

- [ ] **saveResults() 메서드 (private)**
  - Supabase `investment_tracker` 테이블에 insert
  - 결과가 0개면 스킵
  - 에러 시 예외 발생

- [ ] **createJob() 메서드 (private)**
  - 고유 Job ID 생성 (timestamp + random)
  - Job 객체 생성 (status: 'pending')
  - Map에 저장

- [ ] **updateJobStatus() 메서드 (private)**
  - 상태 변경
  - 'running' 시 started_at 설정
  - 'completed'/'failed' 시 completed_at, results_count, error_message 설정

- [ ] **getJobHistory() 메서드**
  - Job 목록 반환
  - started_at 기준 내림차순 정렬

- [ ] **getCrawlerStatus() 메서드**
  - 특정 크롤러 상태 반환
  - crawler.getStatus() 호출

- [ ] **crawlerManager 싱글톤 인스턴스**
  - export const crawlerManager = new CrawlerManager()

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **S1BI1 (Supabase Client)**
  - `createClient()` 정상 작동
  - `investment_tracker` 테이블 insert 가능

#### 4.2 크롤러 등록 및 실행 테스트

```typescript
// 테스트 크롤러 (간단한 구현)
class TestCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: 'Test Site',
      base_url: 'https://example.com',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    return [
      {
        title: 'Test Article',
        url: 'https://example.com/article',
        published_date: '2026-02-06',
        content: 'Test content',
        source: this.config.site_name
      }
    ]
  }
}

// 등록 및 실행
crawlerManager.registerCrawler('test', new TestCrawler())
const results = await crawlerManager.executeCrawler('test')
```

- [ ] **크롤러 등록 성공**
- [ ] **crawl() 메서드 호출 성공**
- [ ] **결과 반환 확인**
- [ ] **Job 상태 'completed' 확인**

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - S1BI1 (Supabase Client) 완료 확인

- [ ] **환경 차단**
  - Supabase URL/KEY 설정 확인
  - `investment_tracker` 테이블 존재 확인

- [ ] **외부 API 차단**
  - 없음 (HTTP 요청만 사용)

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **2개 파일 생성 완료** ✅
3. **BaseCrawler 추상 클래스 구현** ✅
4. **fetchHTML() 동작 확인** ✅ (retry, timeout, rate limiting)
5. **CrawlerManager 구현** ✅
6. **크롤러 등록/실행 동작 확인** ✅
7. **Supabase 결과 저장 확인** ✅

### 권장 (Nice to Pass)

1. **프록시 지원** ✨
2. **캐싱 기능** ✨
3. **스케줄링 연동** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **Rate Limiting**
   - 최소 100ms 간격 필수
   - 사이트별로 다른 간격 설정 가능

2. **Retry 로직**
   - 최대 3회 재시도
   - Exponential backoff (1초, 2초, 4초)
   - 각 시도마다 에러 로깅

3. **Timeout**
   - 기본 10초
   - AbortController 사용 필수

4. **User-Agent**
   - 실제 브라우저처럼 설정
   - 봇 차단 방지

5. **에러 처리**
   - 명확한 에러 메시지
   - Job 상태에 에러 기록
   - 개별 크롤러 실패 시 전체 중단 안 함

6. **Supabase 저장**
   - 결과가 없으면 insert 스킵
   - 중복 키 에러 처리 (필요 시)

---

## PO 테스트 가이드

### 1. 베이스 크롤러 테스트

```typescript
import { BaseCrawler, CrawlResult } from '@/lib/crawler/base-crawler'

class SimpleCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: 'Example Site',
      base_url: 'https://example.com',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const html = await this.fetchHTML('https://example.com')
    return [{
      title: 'Test',
      url: 'https://example.com',
      published_date: '2026-02-06',
      content: html.substring(0, 100),
      source: this.config.site_name
    }]
  }
}

const crawler = new SimpleCrawler()
const results = await crawler.crawl()
console.log(results)
```

### 2. 크롤러 관리자 테스트

```typescript
import { crawlerManager } from '@/lib/crawler/crawler-manager'

// 크롤러 등록
crawlerManager.registerCrawler('example', new SimpleCrawler())

// 단일 실행
const results = await crawlerManager.executeCrawler('example')
console.log(results)

// 전체 실행
const allResults = await crawlerManager.executeAll()
console.log(allResults)

// Job 히스토리 조회
const history = crawlerManager.getJobHistory()
console.log(history)
```

---

## 참조

- Task Instruction: `task-instructions/S4E1_instruction.md`
- 기존 프로토타입:
  - `backend/app/services/news_crawler/base_crawler.py`
  - `backend/app/services/news_crawler/crawler_manager.py`

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
