# S4O1: Background Task Scheduler

## Task 정보

- **Task ID**: S4O1
- **Task Name**: 백그라운드 작업 스케줄러
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: O (DevOps)
- **Dependencies**: S4E1, S4E2
- **Task Agent**: devops-troubleshooter
- **Verification Agent**: code-reviewer

---

## Task 목표

주간 뉴스 수집 작업을 자동으로 실행하는 스케줄러 인프라 구현

---

## 상세 지시사항

### 1. Task Scheduler Infrastructure

**파일**: `lib/scheduler/task-scheduler.ts`

```typescript
import { CronJob } from 'cron'

export interface ScheduledTask {
  id: string
  name: string
  schedule: string // Cron 표현식
  handler: () => Promise<void>
  enabled: boolean
  lastRun?: Date
  nextRun?: Date
  status: 'idle' | 'running' | 'error'
}

export class TaskScheduler {
  private tasks: Map<string, { task: ScheduledTask; job: CronJob }> = new Map()
  private running: boolean = false

  /**
   * 작업 등록
   */
  registerTask(task: ScheduledTask): void {
    const cronJob = new CronJob(
      task.schedule,
      async () => {
        await this.runTask(task.id)
      },
      null,
      task.enabled,
      'Asia/Seoul'
    )

    this.tasks.set(task.id, { task, job: cronJob })
    console.log(`Task registered: ${task.name} (${task.schedule})`)
  }

  /**
   * 작업 실행
   */
  private async runTask(taskId: string): Promise<void> {
    const entry = this.tasks.get(taskId)
    if (!entry) return

    const { task, job } = entry

    // 이미 실행 중이면 스킵
    if (task.status === 'running') {
      console.log(`Task ${task.name} is already running, skipping...`)
      return
    }

    try {
      task.status = 'running'
      task.lastRun = new Date()
      console.log(`[${new Date().toISOString()}] Running task: ${task.name}`)

      await task.handler()

      task.status = 'idle'
      task.nextRun = job.nextDate().toDate()
      console.log(`[${new Date().toISOString()}] Task completed: ${task.name}`)
      console.log(`Next run: ${task.nextRun}`)
    } catch (error) {
      task.status = 'error'
      console.error(`[${new Date().toISOString()}] Task failed: ${task.name}`, error)
      throw error
    }
  }

  /**
   * 작업 수동 실행
   */
  async triggerTask(taskId: string): Promise<void> {
    const entry = this.tasks.get(taskId)
    if (!entry) {
      throw new Error(`Task not found: ${taskId}`)
    }

    console.log(`Manually triggering task: ${entry.task.name}`)
    await this.runTask(taskId)
  }

  /**
   * 스케줄러 시작
   */
  start(): void {
    if (this.running) {
      console.log('Scheduler is already running')
      return
    }

    for (const [taskId, { task, job }] of this.tasks) {
      if (task.enabled) {
        job.start()
        task.nextRun = job.nextDate().toDate()
        console.log(`Task started: ${task.name} - Next run: ${task.nextRun}`)
      }
    }

    this.running = true
    console.log('Scheduler started')
  }

  /**
   * 스케줄러 종료
   */
  stop(): void {
    if (!this.running) {
      console.log('Scheduler is not running')
      return
    }

    for (const { job } of this.tasks.values()) {
      job.stop()
    }

    this.running = false
    console.log('Scheduler stopped')
  }

  /**
   * 작업 활성화/비활성화
   */
  setTaskEnabled(taskId: string, enabled: boolean): void {
    const entry = this.tasks.get(taskId)
    if (!entry) return

    entry.task.enabled = enabled

    if (enabled) {
      entry.job.start()
      entry.task.nextRun = entry.job.nextDate().toDate()
    } else {
      entry.job.stop()
      entry.task.nextRun = undefined
    }

    console.log(`Task ${entry.task.name} ${enabled ? 'enabled' : 'disabled'}`)
  }

  /**
   * 상태 조회
   */
  getStatus(): {
    running: boolean
    tasks: Array<{
      id: string
      name: string
      schedule: string
      enabled: boolean
      status: string
      lastRun?: string
      nextRun?: string
    }>
  } {
    const tasks = Array.from(this.tasks.values()).map(({ task }) => ({
      id: task.id,
      name: task.name,
      schedule: task.schedule,
      enabled: task.enabled,
      status: task.status,
      lastRun: task.lastRun?.toISOString(),
      nextRun: task.nextRun?.toISOString()
    }))

    return {
      running: this.running,
      tasks
    }
  }

  /**
   * 특정 작업 조회
   */
  getTask(taskId: string): ScheduledTask | undefined {
    return this.tasks.get(taskId)?.task
  }

  /**
   * 등록된 모든 작업 ID 목록
   */
  getTaskIds(): string[] {
    return Array.from(this.tasks.keys())
  }
}

// 싱글톤 인스턴스
export const taskScheduler = new TaskScheduler()
```

---

### 2. Weekly Collection Task

**파일**: `lib/scheduler/tasks/weekly-collection.ts`

```typescript
import { crawlerManager } from '@/lib/crawler/crawler-manager'
import { taskScheduler, ScheduledTask } from '../task-scheduler'

/**
 * 주간 투자 뉴스 수집 작업
 *
 * 매주 일요일 오전 6시 (KST) 자동 실행
 */
export async function weeklyCollectionHandler(): Promise<void> {
  console.log('Starting weekly investment news collection...')

  try {
    // 모든 등록된 크롤러 실행
    const results = await crawlerManager.executeAll()

    let totalCount = 0
    for (const [name, crawlResults] of results) {
      totalCount += crawlResults.length
      console.log(`${name}: ${crawlResults.length} articles collected`)
    }

    console.log(`Weekly collection completed: ${totalCount} articles total`)
  } catch (error) {
    console.error('Weekly collection failed:', error)
    throw error
  }
}

/**
 * 수동 수집 실행 (테스트/관리자 트리거)
 */
export async function triggerManualCollection(): Promise<{
  success: boolean
  totalArticles: number
  results: Map<string, number>
}> {
  console.log('Manual collection triggered')

  try {
    const results = await crawlerManager.executeAll()

    const summary = new Map<string, number>()
    let totalArticles = 0

    for (const [name, crawlResults] of results) {
      summary.set(name, crawlResults.length)
      totalArticles += crawlResults.length
    }

    return {
      success: true,
      totalArticles,
      results: summary
    }
  } catch (error) {
    console.error('Manual collection failed:', error)
    return {
      success: false,
      totalArticles: 0,
      results: new Map()
    }
  }
}

/**
 * 특정 사이트만 수집
 */
export async function collectFromSites(sites: string[]): Promise<{
  success: boolean
  results: Map<string, number>
}> {
  console.log(`Collecting from sites: ${sites.join(', ')}`)

  const results = new Map<string, number>()

  try {
    for (const site of sites) {
      const crawlResults = await crawlerManager.executeCrawler(site)
      results.set(site, crawlResults.length)
      console.log(`${site}: ${crawlResults.length} articles`)
    }

    return {
      success: true,
      results
    }
  } catch (error) {
    console.error('Site collection failed:', error)
    return {
      success: false,
      results
    }
  }
}

// 주간 수집 작업 등록
export function registerWeeklyCollectionTask(): void {
  const task: ScheduledTask = {
    id: 'weekly_investment_collection',
    name: 'Weekly Investment News Collection',
    schedule: '0 6 * * 0', // 매주 일요일 오전 6시 (Cron: 분 시 일 월 요일)
    handler: weeklyCollectionHandler,
    enabled: true,
    status: 'idle'
  }

  taskScheduler.registerTask(task)
  console.log('Weekly collection task registered')
}
```

---

### 3. API Endpoint (수동 실행 및 상태 조회)

**파일**: `app/api/scheduler/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { taskScheduler } from '@/lib/scheduler/task-scheduler'
import { triggerManualCollection } from '@/lib/scheduler/tasks/weekly-collection'

/**
 * GET /api/scheduler
 * 스케줄러 상태 조회
 */
export async function GET(request: NextRequest) {
  try {
    const status = taskScheduler.getStatus()
    return NextResponse.json(status)
  } catch (error) {
    console.error('Scheduler status error:', error)
    return NextResponse.json(
      { error: 'Failed to get scheduler status' },
      { status: 500 }
    )
  }
}

/**
 * POST /api/scheduler/trigger
 * 수동 수집 실행
 */
export async function POST(request: NextRequest) {
  try {
    const { taskId } = await request.json()

    if (taskId === 'weekly_investment_collection') {
      const result = await triggerManualCollection()
      return NextResponse.json(result)
    }

    // 일반 작업 트리거
    await taskScheduler.triggerTask(taskId)
    return NextResponse.json({ success: true, message: 'Task triggered' })
  } catch (error) {
    console.error('Task trigger error:', error)
    return NextResponse.json(
      { error: 'Failed to trigger task' },
      { status: 500 }
    )
  }
}
```

---

### 4. 스케줄러 초기화 (서버 시작 시)

**파일**: `lib/scheduler/init.ts`

```typescript
import { taskScheduler } from './task-scheduler'
import { registerWeeklyCollectionTask } from './tasks/weekly-collection'

/**
 * 스케줄러 초기화 (서버 시작 시 실행)
 */
export function initializeScheduler(): void {
  console.log('Initializing scheduler...')

  // 주간 수집 작업 등록
  registerWeeklyCollectionTask()

  // 스케줄러 시작
  taskScheduler.start()

  console.log('Scheduler initialized')
}

/**
 * 스케줄러 종료 (서버 종료 시 실행)
 */
export function shutdownScheduler(): void {
  console.log('Shutting down scheduler...')
  taskScheduler.stop()
  console.log('Scheduler shut down')
}
```

**Next.js 서버 시작 시 호출 (필요 시 `middleware.ts` 또는 `instrumentation.ts` 활용)**

---

### 5. Vercel Cron Jobs 통합 (프로덕션)

**파일**: `vercel.json`

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

**파일**: `app/api/cron/weekly-collection/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { weeklyCollectionHandler } from '@/lib/scheduler/tasks/weekly-collection'

/**
 * Vercel Cron Job 엔드포인트
 * 매주 일요일 오전 6시 실행
 */
export async function GET(request: NextRequest) {
  // Vercel Cron 요청 검증
  const authHeader = request.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    await weeklyCollectionHandler()
    return NextResponse.json({ success: true, message: 'Weekly collection completed' })
  } catch (error) {
    console.error('Cron job error:', error)
    return NextResponse.json(
      { error: 'Weekly collection failed' },
      { status: 500 }
    )
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|-----------------|
| `lib/scheduler/task-scheduler.ts` | 스케줄러 인프라 | ~200줄 |
| `lib/scheduler/tasks/weekly-collection.ts` | 주간 수집 작업 | ~120줄 |
| `lib/scheduler/init.ts` | 스케줄러 초기화 | ~30줄 |
| `app/api/scheduler/route.ts` | 스케줄러 API | ~60줄 |
| `app/api/cron/weekly-collection/route.ts` | Vercel Cron 엔드포인트 | ~30줄 |
| `vercel.json` | Vercel Cron 설정 | ~10줄 |

**총 파일 수**: 6개
**총 라인 수**: ~450줄

---

## 기술 스택

- **node-cron**: Cron 표현식 기반 스케줄링 (개발 환경)
- **Vercel Cron Jobs**: 프로덕션 스케줄링
- **Next.js API Routes**: 수동 실행 엔드포인트
- **Crawler Manager**: S4E1에서 구현한 크롤러 관리자

---

## 완료 기준

### 필수 (Must Have)

- [ ] TaskScheduler 클래스 구현
- [ ] 작업 등록, 시작, 종료 기능
- [ ] 수동 실행 기능 (triggerTask)
- [ ] 상태 조회 기능 (getStatus)
- [ ] 주간 수집 작업 핸들러 (weeklyCollectionHandler)
- [ ] 스케줄러 초기화 (initializeScheduler)
- [ ] 스케줄러 API (`/api/scheduler`)
- [ ] Vercel Cron Jobs 통합 (`/api/cron/weekly-collection`)

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] 로컬 환경에서 스케줄러 동작 확인
- [ ] 수동 실행 API 테스트
- [ ] 상태 조회 API 테스트
- [ ] Vercel Cron 엔드포인트 보안 검증 (CRON_SECRET)

### 권장 (Nice to Have)

- [ ] 스케줄 히스토리 저장 (Supabase)
- [ ] 작업 실패 시 알림 (Email/Slack)
- [ ] 재시도 로직 (Exponential Backoff)

---

## 참조

### 기존 프로토타입
- `backend/app/core/scheduler.py` (165줄 - APScheduler)
- `backend/app/tasks/weekly_collection.py` (77줄)

### 의존성
- S4E1: News Crawler Infrastructure (크롤러 관리자)
- S4E2: News Parser (뉴스 파싱)

---

## 주의사항

1. **Cron 표현식**
   - `0 6 * * 0`: 매주 일요일 오전 6시
   - 분 시 일 월 요일 순서
   - 타임존: Asia/Seoul (KST)

2. **로컬 vs 프로덕션**
   - 로컬: node-cron 사용
   - 프로덕션: Vercel Cron Jobs 사용 (serverless)

3. **Vercel Cron 보안**
   - `CRON_SECRET` 환경 변수 필수
   - Authorization 헤더로 검증

4. **중복 실행 방지**
   - 작업 상태 확인 (running이면 스킵)
   - `max_instances: 1` 설정

5. **에러 처리**
   - 개별 크롤러 실패 시 전체 작업은 계속 진행
   - 에러 로그 저장 및 알림

6. **환경 변수**
   - `CRON_SECRET`: Vercel Cron 인증 키

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
