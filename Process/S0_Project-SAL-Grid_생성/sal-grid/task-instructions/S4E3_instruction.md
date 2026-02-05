# S4E3: Site-Specific Crawlers

## Task 정보

- **Task ID**: S4E3
- **Task Name**: 사이트별 크롤러 구현 (6개)
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)
- **Dependencies**: S4E1 (Base Crawler), S4E2 (News Parser)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

6개 투자 뉴스 사이트별 크롤러 구현 (네이버, 아웃스탠딩, 플래텀, 스타트업투데이, 벤처스퀘어, 와우테일)

---

## 상세 지시사항

### 공통 구조

모든 사이트별 크롤러는 `BaseCrawler`를 상속하고 다음 구조를 따릅니다:

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class [Site]Crawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '[사이트명]',
      base_url: '[사이트 URL]',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    // 1. 목록 페이지 가져오기
    // 2. 기사 URL 추출
    // 3. 각 기사 크롤링
    // 4. 파싱
    // 5. CrawlResult 배열 반환
  }
}
```

---

### 1. 네이버 크롤러

**파일**: `lib/crawler/sites/naver-crawler.ts`

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class NaverCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '네이버 뉴스',
      base_url: 'https://search.naver.com',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const results: CrawlResult[] = []

    // 검색 쿼리
    const searchQuery = '스타트업 투자 유치'
    const searchUrl = `${this.config.base_url}/search.naver?where=news&query=${encodeURIComponent(searchQuery)}&sort=date`

    try {
      // 검색 결과 페이지 가져오기
      const html = await this.fetchHTML(searchUrl)
      const $ = cheerio.load(html)

      // 기사 링크 추출
      const articleUrls: string[] = []
      $('.news_tit').each((_, elem) => {
        const url = $(elem).attr('href')
        if (url) {
          articleUrls.push(url)
        }
      })

      // 각 기사 크롤링 (최대 10개)
      for (const url of articleUrls.slice(0, 10)) {
        try {
          const articleHtml = await this.fetchHTML(url)
          const parsed = newsParser.parseArticle(articleHtml, {
            title: 'h2#title_area, h3#articleTitle',
            content: '#dic_area, #articleBodyContents',
            date: '.media_end_head_info_datestamp_time, .t11',
          })

          results.push({
            title: parsed.title,
            url,
            published_date: parsed.published_date,
            content: parsed.content,
            source: this.config.site_name,
            raw_html: articleHtml,
          })
        } catch (error) {
          console.error(`Failed to crawl article: ${url}`, error)
        }
      }
    } catch (error) {
      console.error('Naver crawl failed:', error)
    }

    return results
  }
}
```

---

### 2. 아웃스탠딩 크롤러

**파일**: `lib/crawler/sites/outstanding-crawler.ts`

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class OutstandingCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '아웃스탠딩',
      base_url: 'https://outstanding.kr',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const results: CrawlResult[] = []
    const listUrl = `${this.config.base_url}/investment`

    try {
      const html = await this.fetchHTML(listUrl)
      const $ = cheerio.load(html)

      const articleUrls: string[] = []
      $('.article-item a').each((_, elem) => {
        const href = $(elem).attr('href')
        if (href) {
          articleUrls.push(this.config.base_url + href)
        }
      })

      for (const url of articleUrls.slice(0, 10)) {
        try {
          const articleHtml = await this.fetchHTML(url)
          const parsed = newsParser.parseArticle(articleHtml, {
            title: 'h1.article-title',
            content: '.article-body',
            date: '.article-date',
          })

          results.push({
            title: parsed.title,
            url,
            published_date: parsed.published_date,
            content: parsed.content,
            source: this.config.site_name,
          })
        } catch (error) {
          console.error(`Failed to crawl article: ${url}`, error)
        }
      }
    } catch (error) {
      console.error('Outstanding crawl failed:', error)
    }

    return results
  }
}
```

---

### 3. 플래텀 크롤러

**파일**: `lib/crawler/sites/platum-crawler.ts`

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class PlatumCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '플래텀',
      base_url: 'https://platum.kr',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const results: CrawlResult[] = []
    const listUrl = `${this.config.base_url}/archives/category/investment`

    try {
      const html = await this.fetchHTML(listUrl)
      const $ = cheerio.load(html)

      const articleUrls: string[] = []
      $('.post-item h2 a').each((_, elem) => {
        const href = $(elem).attr('href')
        if (href) {
          articleUrls.push(href)
        }
      })

      for (const url of articleUrls.slice(0, 10)) {
        try {
          const articleHtml = await this.fetchHTML(url)
          const parsed = newsParser.parseArticle(articleHtml, {
            title: 'h1.entry-title',
            content: '.entry-content',
            date: '.entry-date',
          })

          results.push({
            title: parsed.title,
            url,
            published_date: parsed.published_date,
            content: parsed.content,
            source: this.config.site_name,
          })
        } catch (error) {
          console.error(`Failed to crawl article: ${url}`, error)
        }
      }
    } catch (error) {
      console.error('Platum crawl failed:', error)
    }

    return results
  }
}
```

---

### 4. 스타트업투데이 크롤러

**파일**: `lib/crawler/sites/startuptoday-crawler.ts`

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class StartupTodayCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '스타트업투데이',
      base_url: 'https://www.startuptoday.kr',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const results: CrawlResult[] = []
    const listUrl = `${this.config.base_url}/news/articleList.html?sc_section_code=S1N8`

    try {
      const html = await this.fetchHTML(listUrl)
      const $ = cheerio.load(html)

      const articleUrls: string[] = []
      $('.article-list .article-title a').each((_, elem) => {
        const href = $(elem).attr('href')
        if (href) {
          articleUrls.push(this.config.base_url + href)
        }
      })

      for (const url of articleUrls.slice(0, 10)) {
        try {
          const articleHtml = await this.fetchHTML(url)
          const parsed = newsParser.parseArticle(articleHtml, {
            title: '.article-head-title',
            content: '#article-view-content-div',
            date: '.article-info .date',
          })

          results.push({
            title: parsed.title,
            url,
            published_date: parsed.published_date,
            content: parsed.content,
            source: this.config.site_name,
          })
        } catch (error) {
          console.error(`Failed to crawl article: ${url}`, error)
        }
      }
    } catch (error) {
      console.error('StartupToday crawl failed:', error)
    }

    return results
  }
}
```

---

### 5. 벤처스퀘어 크롤러

**파일**: `lib/crawler/sites/venturesquare-crawler.ts`

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class VentureSquareCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '벤처스퀘어',
      base_url: 'https://www.venturesquare.net',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const results: CrawlResult[] = []
    const listUrl = `${this.config.base_url}/category/투자`

    try {
      const html = await this.fetchHTML(listUrl)
      const $ = cheerio.load(html)

      const articleUrls: string[] = []
      $('.post-title a').each((_, elem) => {
        const href = $(elem).attr('href')
        if (href) {
          articleUrls.push(href)
        }
      })

      for (const url of articleUrls.slice(0, 10)) {
        try {
          const articleHtml = await this.fetchHTML(url)
          const parsed = newsParser.parseArticle(articleHtml, {
            title: 'h1.entry-title',
            content: '.entry-content',
            date: '.entry-meta time',
          })

          results.push({
            title: parsed.title,
            url,
            published_date: parsed.published_date,
            content: parsed.content,
            source: this.config.site_name,
          })
        } catch (error) {
          console.error(`Failed to crawl article: ${url}`, error)
        }
      }
    } catch (error) {
      console.error('VentureSquare crawl failed:', error)
    }

    return results
  }
}
```

---

### 6. 와우테일 크롤러

**파일**: `lib/crawler/sites/wowtale-crawler.ts`

```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class WowTaleCrawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '와우테일',
      base_url: 'https://www.wowtale.net',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    const results: CrawlResult[] = []
    const listUrl = `${this.config.base_url}/tag/투자`

    try {
      const html = await this.fetchHTML(listUrl)
      const $ = cheerio.load(html)

      const articleUrls: string[] = []
      $('.article-item h3 a').each((_, elem) => {
        const href = $(elem).attr('href')
        if (href) {
          articleUrls.push(this.config.base_url + href)
        }
      })

      for (const url of articleUrls.slice(0, 10)) {
        try {
          const articleHtml = await this.fetchHTML(url)
          const parsed = newsParser.parseArticle(articleHtml, {
            title: 'h1.article-title',
            content: '.article-content',
            date: '.article-date',
          })

          results.push({
            title: parsed.title,
            url,
            published_date: parsed.published_date,
            content: parsed.content,
            source: this.config.site_name,
          })
        } catch (error) {
          console.error(`Failed to crawl article: ${url}`, error)
        }
      }
    } catch (error) {
      console.error('WowTale crawl failed:', error)
    }

    return results
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/crawler/sites/naver-crawler.ts` | 네이버 크롤러 | ~80줄 |
| `lib/crawler/sites/outstanding-crawler.ts` | 아웃스탠딩 크롤러 | ~70줄 |
| `lib/crawler/sites/platum-crawler.ts` | 플래텀 크롤러 | ~70줄 |
| `lib/crawler/sites/startuptoday-crawler.ts` | 스타트업투데이 크롤러 | ~70줄 |
| `lib/crawler/sites/venturesquare-crawler.ts` | 벤처스퀘어 크롤러 | ~70줄 |
| `lib/crawler/sites/wowtale-crawler.ts` | 와우테일 크롤러 | ~70줄 |

**총 파일 수**: 6개
**총 라인 수**: ~430줄

---

## 기술 스택

- **Cheerio**: HTML 파싱
- **BaseCrawler**: 추상 클래스 상속
- **NewsParser**: 뉴스 파싱

---

## 완료 기준

### 필수 (Must Have)

- [ ] 6개 사이트별 크롤러 구현
- [ ] BaseCrawler 상속
- [ ] 목록 페이지 크롤링
- [ ] 기사 URL 추출
- [ ] 개별 기사 크롤링
- [ ] NewsParser 사용

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] 각 사이트별 크롤링 동작 확인
- [ ] CrawlResult 형식 준수

### 권장 (Nice to Have)

- [ ] 추가 사이트 크롤러
- [ ] 동적 콘텐츠 크롤링 (Puppeteer)

---

## 참조

### 기존 프로토타입
- `backend/app/services/news_crawler/` (6개 파일)

### 의존성
- S4E1: Base Crawler
- S4E2: News Parser

---

## 주의사항

1. **CSS 선택자**
   - 사이트별로 다름
   - 변경될 수 있음

2. **Rate Limiting**
   - 최소 1초 간격

3. **에러 처리**
   - 개별 기사 실패 시 계속 진행

4. **최대 개수**
   - 각 사이트별 최대 10개 기사

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
