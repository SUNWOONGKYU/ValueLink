# S4E3 Verification

## 검증 대상

- **Task ID**: S4E3
- **Task Name**: 사이트별 크롤러 구현 (6개)
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

- [ ] **`lib/crawler/sites/naver-crawler.ts` 존재** - 네이버 뉴스 크롤러
- [ ] **`lib/crawler/sites/outstanding-crawler.ts` 존재** - 아웃스탠딩 크롤러
- [ ] **`lib/crawler/sites/platum-crawler.ts` 존재** - 플래텀 크롤러
- [ ] **`lib/crawler/sites/startuptoday-crawler.ts` 존재** - 스타트업투데이 크롤러
- [ ] **`lib/crawler/sites/venturesquare-crawler.ts` 존재** - 벤처스퀘어 크롤러
- [ ] **`lib/crawler/sites/wowtale-crawler.ts` 존재** - 와우테일 크롤러

---

### 3. 핵심 기능 테스트

#### 3.1 공통 구조 (모든 크롤러)

- [ ] **BaseCrawler 상속**
  - `extends BaseCrawler` 확인

- [ ] **constructor() 구현**
  - super() 호출
  - config 객체 전달 (site_name, base_url, rate_limit_ms, max_retries, timeout_ms)

- [ ] **crawl() 메서드 구현**
  - 목록 페이지 가져오기 (fetchHTML)
  - 기사 URL 추출 (Cheerio)
  - 각 기사 크롤링 (최대 10개)
  - 파싱 (newsParser.parseArticle)
  - CrawlResult 배열 반환

#### 3.2 네이버 크롤러

- [ ] **NaverCrawler 클래스**
  - `site_name: '네이버 뉴스'`
  - `base_url: 'https://search.naver.com'`

- [ ] **검색 쿼리**
  - `'스타트업 투자 유치'` 검색
  - `sort=date` (최신순)

- [ ] **CSS 선택자**
  - 목록: `.news_tit` (기사 링크)
  - 제목: `h2#title_area, h3#articleTitle`
  - 본문: `#dic_area, #articleBodyContents`
  - 날짜: `.media_end_head_info_datestamp_time, .t11`

#### 3.3 아웃스탠딩 크롤러

- [ ] **OutstandingCrawler 클래스**
  - `site_name: '아웃스탠딩'`
  - `base_url: 'https://outstanding.kr'`

- [ ] **목록 페이지**
  - `/investment` 경로

- [ ] **CSS 선택자**
  - 목록: `.article-item a`
  - 제목: `h1.article-title`
  - 본문: `.article-body`
  - 날짜: `.article-date`

#### 3.4 플래텀 크롤러

- [ ] **PlatumCrawler 클래스**
  - `site_name: '플래텀'`
  - `base_url: 'https://platum.kr'`

- [ ] **목록 페이지**
  - `/archives/category/investment` 경로

- [ ] **CSS 선택자**
  - 목록: `.post-item h2 a`
  - 제목: `h1.entry-title`
  - 본문: `.entry-content`
  - 날짜: `.entry-date`

#### 3.5 스타트업투데이 크롤러

- [ ] **StartupTodayCrawler 클래스**
  - `site_name: '스타트업투데이'`
  - `base_url: 'https://www.startuptoday.kr'`

- [ ] **목록 페이지**
  - `/news/articleList.html?sc_section_code=S1N8` 경로

- [ ] **CSS 선택자**
  - 목록: `.article-list .article-title a`
  - 제목: `.article-head-title`
  - 본문: `#article-view-content-div`
  - 날짜: `.article-info .date`

#### 3.6 벤처스퀘어 크롤러

- [ ] **VentureSquareCrawler 클래스**
  - `site_name: '벤처스퀘어'`
  - `base_url: 'https://www.venturesquare.net'`

- [ ] **목록 페이지**
  - `/category/투자` 경로

- [ ] **CSS 선택자**
  - 목록: `.post-title a`
  - 제목: `h1.entry-title`
  - 본문: `.entry-content`
  - 날짜: `.entry-meta time`

#### 3.7 와우테일 크롤러

- [ ] **WowTaleCrawler 클래스**
  - `site_name: '와우테일'`
  - `base_url: 'https://www.wowtale.net'`

- [ ] **목록 페이지**
  - `/tag/투자` 경로

- [ ] **CSS 선택자**
  - 목록: `.article-item h3 a`
  - 제목: `h1.article-title`
  - 본문: `.article-content`
  - 날짜: `.article-date`

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **S4E1 (Base Crawler)**
  - BaseCrawler 상속 확인
  - fetchHTML() 사용 확인

- [ ] **S4E2 (News Parser)**
  - newsParser.parseArticle() 호출 확인
  - ParsedArticle → CrawlResult 변환 확인

#### 4.2 크롤러 등록 및 실행

```typescript
import { crawlerManager } from '@/lib/crawler/crawler-manager'
import { NaverCrawler } from '@/lib/crawler/sites/naver-crawler'
import { OutstandingCrawler } from '@/lib/crawler/sites/outstanding-crawler'
// ... (나머지 크롤러)

// 6개 크롤러 등록
crawlerManager.registerCrawler('naver', new NaverCrawler())
crawlerManager.registerCrawler('outstanding', new OutstandingCrawler())
crawlerManager.registerCrawler('platum', new PlatumCrawler())
crawlerManager.registerCrawler('startuptoday', new StartupTodayCrawler())
crawlerManager.registerCrawler('venturesquare', new VentureSquareCrawler())
crawlerManager.registerCrawler('wowtale', new WowTaleCrawler())

// 전체 실행
const results = await crawlerManager.executeAll()
```

- [ ] **6개 크롤러 모두 등록 성공**
- [ ] **executeAll() 실행 성공**
- [ ] **각 사이트별 결과 반환 확인**

#### 4.3 데이터 품질 검증

- [ ] **최소 결과 개수**
  - 각 사이트별 최소 1개 기사 크롤링

- [ ] **필수 필드 존재**
  - title (빈 문자열 아님)
  - url (유효한 URL)
  - published_date (YYYY-MM-DD 형식)
  - content (빈 문자열 아님)
  - source (사이트명)

- [ ] **중복 URL 제거**
  - 같은 URL이 여러 번 수집되지 않음

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - S4E1 (Base Crawler) 완료 확인
  - S4E2 (News Parser) 완료 확인

- [ ] **환경 차단**
  - 인터넷 연결 확인
  - 사이트 접근 가능 확인 (차단되지 않음)

- [ ] **외부 API 차단**
  - 없음 (HTTP 요청만 사용)

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **6개 파일 생성 완료** ✅
3. **모든 크롤러가 BaseCrawler 상속** ✅
4. **각 사이트별 크롤링 동작 확인** ✅
5. **CrawlResult 형식 준수** ✅
6. **최소 1개 이상 기사 수집 (각 사이트)** ✅

### 권장 (Nice to Pass)

1. **추가 사이트 크롤러** ✨
2. **동적 콘텐츠 크롤링** ✨ (Puppeteer)
3. **CSS 선택자 자동 감지** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **CSS 선택자**
   - 사이트별로 다름
   - 사이트 구조 변경 시 업데이트 필요
   - 여러 선택자 대안 제공 (쉼표로 구분)

2. **Rate Limiting**
   - 최소 1초 간격 (1000ms)
   - 사이트 부하 방지

3. **에러 처리**
   - 개별 기사 실패 시 계속 진행
   - 에러 로깅 (console.error)
   - 빈 배열 반환하지 않도록 주의

4. **최대 개수**
   - 각 사이트별 최대 10개 기사
   - `.slice(0, 10)` 사용

5. **URL 처리**
   - 상대 URL → 절대 URL 변환
   - `base_url + href` 조합

6. **인코딩**
   - 검색 쿼리 URL 인코딩 (`encodeURIComponent`)
   - 한글 URL 처리

---

## PO 테스트 가이드

### 1. 네이버 크롤러 테스트

```typescript
import { NaverCrawler } from '@/lib/crawler/sites/naver-crawler'

const crawler = new NaverCrawler()
const results = await crawler.crawl()

console.log(`총 ${results.length}개 기사 수집`)
results.forEach((result, index) => {
  console.log(`${index + 1}. ${result.title}`)
  console.log(`   URL: ${result.url}`)
  console.log(`   발행일: ${result.published_date}`)
  console.log(`   내용 길이: ${result.content.length}자`)
  console.log()
})
```

### 2. 전체 크롤러 테스트

```typescript
import { crawlerManager } from '@/lib/crawler/crawler-manager'
// ... (6개 크롤러 import 및 등록)

const results = await crawlerManager.executeAll()

for (const [siteName, articles] of results) {
  console.log(`${siteName}: ${articles.length}개 기사`)
}

// 총 수집 기사 수
const totalArticles = Array.from(results.values()).reduce(
  (sum, articles) => sum + articles.length,
  0
)
console.log(`총 ${totalArticles}개 기사 수집`)
```

---

## 참조

- Task Instruction: `task-instructions/S4E3_instruction.md`
- 기존 프로토타입: `backend/app/services/news_crawler/` (6개 파일)

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
