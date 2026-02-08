# S4E3, S4E4, S4O1: 통합 Instruction (신규 구현)

> **주의**: 이 파일은 나머지 3개 Task를 통합한 간소화 버전입니다.

---

## S4E3: Site-Specific Crawlers (6개 사이트)

### Task 정보
- **Task ID**: S4E3
- **Dependencies**: S4E1 (Base Crawler), S4E2 (News Parser)
- **파일 수**: 6개
- **총 라인 수**: ~430줄

### Task 목표
6개 투자 뉴스 사이트별 크롤러 구현 (네이버, 아웃스탠딩, 플래텀, 스타트업투데이, 벤처스퀘어, 와우테일)

### 공통 구조
```typescript
import { BaseCrawler, CrawlResult } from '../base-crawler'
import { newsParser } from '../news-parser'
import * as cheerio from 'cheerio'

export class [Site]Crawler extends BaseCrawler {
  constructor() {
    super({
      site_name: '[사이트명]',
      base_url: '[URL]',
      rate_limit_ms: 1000,
      max_retries: 3,
      timeout_ms: 10000,
    })
  }

  async crawl(): Promise<CrawlResult[]> {
    // 1. 목록 페이지 가져오기
    // 2. 기사 URL 추출
    // 3. 각 기사 크롤링 (최대 10개)
    // 4. 파싱
    // 5. CrawlResult 배열 반환
  }
}
```

### 생성 파일
1. `lib/crawler/sites/naver-crawler.ts` (~80줄)
2. `lib/crawler/sites/outstanding-crawler.ts` (~70줄)
3. `lib/crawler/sites/platum-crawler.ts` (~70줄)
4. `lib/crawler/sites/startuptoday-crawler.ts` (~70줄)
5. `lib/crawler/sites/venturesquare-crawler.ts` (~70줄)
6. `lib/crawler/sites/wowtale-crawler.ts` (~70줄)

### 핵심 개선 사항
- ✅ BaseCrawler 상속
- ✅ 사이트별 CSS 선택자
- ✅ NewsParser 사용
- ✅ 최대 10개 기사 제한
- ✅ 에러 처리 (개별 기사 실패 시 계속 진행)

---

## S4E4: Enkino AI Verification

### Task 정보
- **Task ID**: S4E4
- **Dependencies**: S3BA3 (DCF Engine)
- **파일 수**: 1개
- **총 라인 수**: ~350줄

### Task 목표
DCF 평가 엔진을 실제 회계법인 평가보고서 데이터로 검증하는 서비스 구현

### 검증 데이터
**실제 데이터**: 태일회계법인 FY25 엔키노에이아이 기업가치 평가보고서 (2025.06.30)

**주요 수치:**
- Operating Value: 16,216,378,227원
- PV Cumulative: 5,605,401,153원
- PV Terminal: 10,610,977,073원
- Enterprise Value: 16,346,048,693원
- Equity Value: 15,729,119,359원
- Value Per Share: 2,140원

### 생성 파일
`lib/integrations/enkino-verification.ts`

**포함 클래스/메서드:**
1. **EnkinoVerificationService 클래스**
2. **runVerification()**: 검증 실행
3. **formatVerificationResult()**: 결과 포맷팅

### 핵심 개선 사항
- ✅ 실제 평가 데이터 정확히 입력
- ✅ DCF 엔진 호출
- ✅ 오차 계산 (±5% 이내 PASS)
- ✅ FCFF 검증
- ✅ PV 검증
- ✅ 포맷팅된 출력

### 검증 기준
```typescript
const passed = maxError <= 5.0  // ±5% 이내
```

**오차 계산:**
```typescript
const errorPct = actualValue !== 0
  ? ((engineValue - actualValue) / actualValue * 100)
  : 0
```

---

## S4O1: Background Task Scheduler

### Task 정보
- **Task ID**: S4O1
- **Dependencies**: S4E1 (Crawler Manager), S4E2 (News Parser)
- **파일 수**: 6개
- **총 라인 수**: ~450줄

### Task 목표
주간 뉴스 수집 작업을 자동으로 실행하는 스케줄러 인프라 구현

### 생성 파일
1. `lib/scheduler/task-scheduler.ts` (~200줄) - 스케줄러 인프라
2. `lib/scheduler/tasks/weekly-collection.ts` (~120줄) - 주간 수집 작업
3. `lib/scheduler/init.ts` (~30줄) - 스케줄러 초기화
4. `app/api/scheduler/route.ts` (~60줄) - 스케줄러 API
5. `app/api/cron/weekly-collection/route.ts` (~30줄) - Vercel Cron 엔드포인트
6. `vercel.json` (~10줄) - Vercel Cron 설정

### 핵심 개선 사항

#### 1. TaskScheduler 클래스
```typescript
export class TaskScheduler {
  private tasks: Map<string, { task: ScheduledTask; job: CronJob }>

  registerTask(task: ScheduledTask): void
  start(): void
  stop(): void
  triggerTask(taskId: string): Promise<void>
  getStatus(): { running: boolean; tasks: [...] }
}
```

#### 2. Weekly Collection Task
```typescript
// Cron 표현식: 매주 일요일 오전 6시 (KST)
schedule: '0 6 * * 0'

async function weeklyCollectionHandler(): Promise<void> {
  const results = await crawlerManager.executeAll()
  // 모든 크롤러 실행
}
```

#### 3. Vercel Cron Jobs 통합
```json
{
  "crons": [
    {
      "path": "/api/cron/weekly-collection",
      "schedule": "0 6 * * 0"
    }
  ]
}
```

### 주의사항

1. **Cron 표현식**
   - `0 6 * * 0`: 매주 일요일 오전 6시
   - 타임존: Asia/Seoul (KST)

2. **로컬 vs 프로덕션**
   - 로컬: node-cron 사용
   - 프로덕션: Vercel Cron Jobs

3. **보안**
   - `CRON_SECRET` 환경 변수 필수
   - Authorization 헤더로 검증

4. **중복 실행 방지**
   - 작업 상태 확인 (running이면 스킵)

---

## 통합 완료 기준

### S4E3
- [ ] 6개 사이트별 크롤러 구현
- [ ] BaseCrawler 상속
- [ ] NewsParser 사용
- [ ] 최대 10개 기사 제한

### S4E4
- [ ] EnkinoVerificationService 구현
- [ ] 실제 평가 데이터 입력
- [ ] DCF 엔진 호출
- [ ] 오차 계산 (±5% PASS)

### S4O1
- [ ] TaskScheduler 클래스 구현
- [ ] 주간 수집 작업 핸들러
- [ ] 스케줄러 API
- [ ] Vercel Cron Jobs 통합

---

## 통합 참조

### S4E3 관련 Task
- **S4E1**: Base Crawler
- **S4E2**: News Parser

### S4E4 관련 Task
- **S3BA3**: DCF Engine
- **S3BA2**: Financial Math

### S4O1 관련 Task
- **S4E1**: Crawler Manager
- **S4E2**: News Parser

---

## 예상 소요 시간

| Task | 복잡도 | 파일 수 | 라인 수 |
|------|--------|---------|---------|
| S4E3 | Medium | 6개 | ~430줄 |
| S4E4 | Medium | 1개 | ~350줄 |
| S4O1 | Medium | 6개 | ~450줄 |
| **합계** | - | **13개** | **~1,230줄** |

---

**작성일**: 2026-02-08 (통합)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경 (3개 Task 통합)
