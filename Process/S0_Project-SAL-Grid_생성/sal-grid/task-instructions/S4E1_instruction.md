# S4E1: News Crawler Infrastructure

## Task 정보

- **Task ID**: S4E1
- **Task Name**: 뉴스 크롤러 인프라
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)
- **Dependencies**: S1BI1
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

투자 뉴스 크롤링을 위한 베이스 크롤러 클래스 및 크롤러 관리자 구현

---

## 상세 지시사항

### 1. 베이스 크롤러

**파일**: `lib/crawler/base-crawler.ts`

```typescript
export interface CrawlResult {
  title: string
  url: string
  published_date: string
  content: string
  source: string
  raw_html?: string
}

export interface CrawlerConfig {
  site_name: string
  base_url: string
  rate_limit_ms: number          // 요청 간격 (밀리초)
  max_retries: number
  timeout_ms: number
}

export abstract class BaseCrawler {
  protected config: CrawlerConfig

  constructor(config: CrawlerConfig) {
    this.config = config
  }

  /**
   * 크롤링 실행 (추상 메서드)
   */
  abstract crawl(): Promise<CrawlResult[]>

  /**
   * HTML 가져오기
   */
  protected async fetchHTML(url: string): Promise<string> {
    let lastError: Error | null = null

    for (let attempt = 0; attempt < this.config.max_retries; attempt++) {
      try {
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

        // Rate limiting
        await this.sleep(this.config.rate_limit_ms)

        return await response.text()
      } catch (error) {
        lastError = error as Error
        console.error(`Fetch attempt ${attempt + 1} failed:`, error)

        if (attempt < this.config.max_retries - 1) {
          // Exponential backoff
          await this.sleep(1000 * Math.pow(2, attempt))
        }
      }
    }

    throw new Error(
      `Failed to fetch ${url} after ${this.config.max_retries} attempts: ${lastError?.message}`
    )
  }

  /**
   * Sleep 유틸리티
   */
  protected sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  /**
   * 크롤링 전 검증
   */
  protected validate(): { valid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!this.config.base_url) {
      errors.push('base_url is required')
    }

    if (this.config.rate_limit_ms < 100) {
      errors.push('rate_limit_ms must be at least 100ms')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  /**
   * 크롤러 상태
   */
  getStatus(): {
    site_name: string
    base_url: string
    rate_limit_ms: number
  } {
    return {
      site_name: this.config.site_name,
      base_url: this.config.base_url,
      rate_limit_ms: this.config.rate_limit_ms,
    }
  }
}
```

---

### 2. 크롤러 관리자

**파일**: `lib/crawler/crawler-manager.ts`

```typescript
import type { BaseCrawler, CrawlResult } from './base-crawler'
import { createClient } from '@/lib/supabase/server'

export interface CrawlerJob {
  id: string
  crawler_name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  results_count?: number
  error_message?: string
}

export class CrawlerManager {
  private crawlers: Map<string, BaseCrawler> = new Map()
  private jobs: Map<string, CrawlerJob> = new Map()

  /**
   * 크롤러 등록
   */
  registerCrawler(name: string, crawler: BaseCrawler) {
    this.crawlers.set(name, crawler)
    console.log(`Crawler registered: ${name}`)
  }

  /**
   * 등록된 크롤러 목록
   */
  getCrawlers(): string[] {
    return Array.from(this.crawlers.keys())
  }

  /**
   * 단일 크롤러 실행
   */
  async executeCrawler(name: string): Promise<CrawlResult[]> {
    const crawler = this.crawlers.get(name)

    if (!crawler) {
      throw new Error(`Crawler not found: ${name}`)
    }

    const jobId = this.createJob(name)

    try {
      this.updateJobStatus(jobId, 'running')

      const results = await crawler.crawl()

      // 결과 저장
      await this.saveResults(results)

      this.updateJobStatus(jobId, 'completed', results.length)

      return results
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      this.updateJobStatus(jobId, 'failed', 0, errorMessage)
      throw error
    }
  }

  /**
   * 모든 크롤러 실행
   */
  async executeAll(): Promise<Map<string, CrawlResult[]>> {
    const results = new Map<string, CrawlResult[]>()

    for (const [name, crawler] of this.crawlers) {
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

    return results
  }

  /**
   * 결과 저장 (Supabase)
   */
  private async saveResults(results: CrawlResult[]): Promise<void> {
    if (results.length === 0) return

    const supabase = createClient()

    const { error } = await supabase.from('investment_tracker').insert(
      results.map((result) => ({
        title: result.title,
        article_url: result.url,
        published_date: result.published_date,
        content: result.content,
        source: result.source,
        raw_html: result.raw_html,
        created_at: new Date().toISOString(),
      }))
    )

    if (error) {
      console.error('Failed to save crawl results:', error)
      throw new Error(`Database insert failed: ${error.message}`)
    }

    console.log(`Saved ${results.length} crawl results to database`)
  }

  /**
   * Job 생성
   */
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

  /**
   * Job 상태 업데이트
   */
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

  /**
   * Job 이력 조회
   */
  getJobHistory(): CrawlerJob[] {
    return Array.from(this.jobs.values()).sort((a, b) => {
      const aTime = new Date(a.started_at || 0).getTime()
      const bTime = new Date(b.started_at || 0).getTime()
      return bTime - aTime
    })
  }

  /**
   * 특정 크롤러 상태
   */
  getCrawlerStatus(name: string): any {
    const crawler = this.crawlers.get(name)
    if (!crawler) return null

    return crawler.getStatus()
  }
}

// 싱글톤 인스턴스
export const crawlerManager = new CrawlerManager()
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/crawler/base-crawler.ts` | 베이스 크롤러 | ~130줄 |
| `lib/crawler/crawler-manager.ts` | 크롤러 관리자 | ~200줄 |

**총 파일 수**: 2개
**총 라인 수**: ~330줄

---

## 기술 스택

- **TypeScript 5.x**: 타입 안전성
- **Fetch API**: HTTP 요청
- **Abstract Class**: 베이스 크롤러 패턴
- **Singleton Pattern**: 크롤러 매니저

---

## 완료 기준

### 필수 (Must Have)

- [ ] 베이스 크롤러 추상 클래스 구현
- [ ] HTML 가져오기 기능 (`fetchHTML`)
- [ ] Rate limiting 구현
- [ ] Retry 로직 (exponential backoff)
- [ ] 크롤러 관리자 구현
- [ ] 크롤러 등록/실행 기능
- [ ] Supabase 결과 저장

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] Rate limiting 동작 확인
- [ ] Retry 로직 동작 확인
- [ ] Job 상태 관리 확인

### 권장 (Nice to Have)

- [ ] 프록시 지원
- [ ] 캐싱 기능
- [ ] 크롤링 스케줄링

---

## 참조

### 기존 프로토타입
- `backend/app/services/news_crawler/base_crawler.py`
- `backend/app/services/news_crawler/crawler_manager.py`

---

## 주의사항

1. **Rate Limiting**
   - 최소 100ms 간격
   - 사이트별로 다른 간격 설정 가능

2. **Retry 로직**
   - 최대 3회 재시도
   - Exponential backoff (1초, 2초, 4초)

3. **Timeout**
   - 기본 10초
   - AbortController 사용

4. **User-Agent**
   - 실제 브라우저처럼 설정
   - 차단 방지

5. **에러 처리**
   - 명확한 에러 메시지
   - Job 상태에 에러 기록

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
