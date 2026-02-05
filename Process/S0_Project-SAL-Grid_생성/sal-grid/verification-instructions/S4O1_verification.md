# S4O1 Verification

## 검증 대상

- **Task ID**: S4O1
- **Task Name**: 백그라운드 작업 스케줄러
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: O (DevOps)

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

- [ ] **`lib/scheduler/task-scheduler.ts` 존재** - 스케줄러 인프라
- [ ] **`lib/scheduler/tasks/weekly-collection.ts` 존재** - 주간 수집 작업
- [ ] **`lib/scheduler/init.ts` 존재** - 스케줄러 초기화
- [ ] **`app/api/scheduler/route.ts` 존재** - 스케줄러 API
- [ ] **`app/api/cron/weekly-collection/route.ts` 존재** - Vercel Cron 엔드포인트
- [ ] **`vercel.json` 업데이트** - Vercel Cron 설정 추가

---

### 3. 핵심 기능 테스트

#### 3.1 Task Scheduler Infrastructure (`task-scheduler.ts`)

- [ ] **ScheduledTask 인터페이스**
  - id, name, schedule, handler, enabled, lastRun, nextRun, status 필드

- [ ] **TaskScheduler 클래스**
  - `private tasks: Map<...>` 선언
  - `private running: boolean` 선언

- [ ] **registerTask() 메서드**
  - CronJob 인스턴스 생성
  - schedule (Cron 표현식) 설정
  - timezone: 'Asia/Seoul' 설정
  - Map에 저장

- [ ] **runTask() 메서드 (private)**
  - 작업 상태 확인 (이미 실행 중이면 스킵)
  - 상태를 'running'으로 변경
  - lastRun 업데이트
  - handler() 호출
  - 성공 시 'idle' 상태, nextRun 업데이트
  - 실패 시 'error' 상태, 에러 발생

- [ ] **triggerTask() 메서드**
  - 수동 실행
  - runTask() 호출
  - 작업 없으면 에러 발생

- [ ] **start() 메서드**
  - 이미 실행 중이면 리턴
  - 모든 활성화된 작업의 CronJob.start() 호출
  - running = true 설정
  - 콘솔 로그 출력

- [ ] **stop() 메서드**
  - 실행 중이 아니면 리턴
  - 모든 CronJob.stop() 호출
  - running = false 설정

- [ ] **setTaskEnabled() 메서드**
  - 작업 활성화/비활성화
  - CronJob.start() 또는 stop() 호출

- [ ] **getStatus() 메서드**
  - 스케줄러 상태 (running)
  - 작업 목록 (id, name, schedule, enabled, status, lastRun, nextRun)

- [ ] **getTask() 메서드**
  - 특정 작업 조회

- [ ] **getTaskIds() 메서드**
  - 등록된 작업 ID 목록

- [ ] **taskScheduler 싱글톤**
  - `export const taskScheduler = new TaskScheduler()`

#### 3.2 Weekly Collection Task (`weekly-collection.ts`)

- [ ] **weeklyCollectionHandler() 함수**
  - crawlerManager.executeAll() 호출
  - 결과 집계 (totalCount)
  - 콘솔 로그 출력
  - 에러 시 예외 발생

- [ ] **triggerManualCollection() 함수**
  - 수동 수집 실행
  - crawlerManager.executeAll() 호출
  - 결과 반환 (success, totalArticles, results)

- [ ] **collectFromSites() 함수**
  - 특정 사이트만 수집
  - crawlerManager.executeCrawler() 호출
  - 결과 Map 반환

- [ ] **registerWeeklyCollectionTask() 함수**
  - ScheduledTask 객체 생성
  - id: 'weekly_investment_collection'
  - schedule: '0 6 * * 0' (매주 일요일 오전 6시)
  - taskScheduler.registerTask() 호출

#### 3.3 Scheduler Initialization (`init.ts`)

- [ ] **initializeScheduler() 함수**
  - registerWeeklyCollectionTask() 호출
  - taskScheduler.start() 호출
  - 콘솔 로그 출력

- [ ] **shutdownScheduler() 함수**
  - taskScheduler.stop() 호출
  - 콘솔 로그 출력

#### 3.4 Scheduler API (`app/api/scheduler/route.ts`)

- [ ] **GET /api/scheduler**
  - taskScheduler.getStatus() 호출
  - JSON 반환

- [ ] **POST /api/scheduler/trigger**
  - 요청 body에서 taskId 추출
  - taskId === 'weekly_investment_collection'이면 triggerManualCollection() 호출
  - 그 외: taskScheduler.triggerTask() 호출
  - JSON 반환

#### 3.5 Vercel Cron Endpoint (`app/api/cron/weekly-collection/route.ts`)

- [ ] **GET /api/cron/weekly-collection**
  - Authorization 헤더 검증 (`Bearer ${CRON_SECRET}`)
  - 인증 실패 시 401 에러
  - weeklyCollectionHandler() 호출
  - 성공 시 JSON 반환
  - 실패 시 500 에러

#### 3.6 Vercel Cron 설정 (`vercel.json`)

- [ ] **crons 배열 존재**
  - path: '/api/cron/weekly-collection'
  - schedule: '0 6 * * 0'

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **S4E1 (Crawler Infrastructure)**
  - crawlerManager 사용 가능
  - crawlerManager.executeAll() 호출 가능

- [ ] **S4E2 (News Parser)**
  - 파싱된 데이터 수집 확인

#### 4.2 로컬 스케줄러 테스트

```typescript
import { initializeScheduler, shutdownScheduler } from '@/lib/scheduler/init'

// 스케줄러 시작
initializeScheduler()

// 상태 조회
const status = taskScheduler.getStatus()
console.log(status)

// 수동 실행
await taskScheduler.triggerTask('weekly_investment_collection')

// 종료
shutdownScheduler()
```

- [ ] **스케줄러 시작 성공**
- [ ] **작업 등록 확인**
- [ ] **수동 실행 성공**
- [ ] **종료 성공**

#### 4.3 API 테스트

**상태 조회:**
```bash
curl http://localhost:3000/api/scheduler
```

**수동 실행:**
```bash
curl -X POST http://localhost:3000/api/scheduler/trigger \
  -H "Content-Type: application/json" \
  -d '{"taskId": "weekly_investment_collection"}'
```

- [ ] **GET /api/scheduler 동작 확인**
- [ ] **POST /api/scheduler/trigger 동작 확인**
- [ ] **수동 실행 시 크롤러 실행 확인**

#### 4.4 Vercel Cron 테스트

**환경 변수 설정:**
```
CRON_SECRET=your_secret_here
```

**Cron 엔드포인트 호출:**
```bash
curl http://localhost:3000/api/cron/weekly-collection \
  -H "Authorization: Bearer your_secret_here"
```

- [ ] **CRON_SECRET 검증 확인**
- [ ] **인증 실패 시 401 에러**
- [ ] **인증 성공 시 크롤러 실행**

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - S4E1 (Crawler Infrastructure) 완료 확인
  - S4E2 (News Parser) 완료 확인

- [ ] **환경 차단**
  - `CRON_SECRET` 환경 변수 설정 확인
  - Vercel 배포 시 Cron Jobs 활성화 확인

- [ ] **외부 API 차단**
  - 없음

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **6개 파일 생성 완료** ✅
3. **TaskScheduler 클래스 구현** ✅
4. **주간 수집 작업 구현** ✅
5. **스케줄러 시작/종료 동작** ✅
6. **수동 실행 기능** ✅
7. **API 엔드포인트 동작** ✅
8. **Vercel Cron 통합** ✅
9. **CRON_SECRET 보안 검증** ✅

### 권장 (Nice to Pass)

1. **스케줄 히스토리 저장** ✨
2. **작업 실패 시 알림** ✨
3. **재시도 로직** ✨

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **Cron 표현식**
   - `0 6 * * 0`: 매주 일요일 오전 6시
   - 분 시 일 월 요일 순서
   - 타임존: Asia/Seoul (KST)

2. **로컬 vs 프로덕션**
   - 로컬: node-cron 사용
   - 프로덕션: Vercel Cron Jobs 사용

3. **Vercel Cron 보안**
   - `CRON_SECRET` 환경 변수 필수
   - Authorization 헤더로 검증
   - 인증 실패 시 401 에러

4. **중복 실행 방지**
   - 작업 상태 확인 (running이면 스킵)
   - 동시 실행 방지

5. **에러 처리**
   - 개별 크롤러 실패 시 전체 작업 계속 진행
   - 에러 로깅
   - 예외 발생 (재시도 가능하도록)

6. **환경 변수**
   - `CRON_SECRET`: Vercel Cron 인증 키 (프로덕션 필수)

7. **타임존**
   - 'Asia/Seoul' 고정
   - 일광절약시간 고려 안 함

---

## PO 테스트 가이드

### 1. 로컬 스케줄러 테스트

```typescript
import { initializeScheduler } from '@/lib/scheduler/init'
import { taskScheduler } from '@/lib/scheduler/task-scheduler'

// 스케줄러 시작
initializeScheduler()

// 상태 조회
const status = taskScheduler.getStatus()
console.log('스케줄러 상태:', status.running ? '실행 중' : '중단')
console.log('등록된 작업:')
for (const task of status.tasks) {
  console.log(`  - ${task.name}`)
  console.log(`    스케줄: ${task.schedule}`)
  console.log(`    다음 실행: ${task.nextRun}`)
}

// 수동 실행 (테스트)
console.log('\n수동 실행 시작...')
await taskScheduler.triggerTask('weekly_investment_collection')
console.log('수동 실행 완료!')
```

### 2. API 테스트

**상태 조회:**
```bash
# 로컬 환경
curl http://localhost:3000/api/scheduler

# 프로덕션
curl https://your-domain.vercel.app/api/scheduler
```

**수동 실행:**
```bash
# 로컬 환경
curl -X POST http://localhost:3000/api/scheduler/trigger \
  -H "Content-Type: application/json" \
  -d '{"taskId": "weekly_investment_collection"}'

# 프로덕션
curl -X POST https://your-domain.vercel.app/api/scheduler/trigger \
  -H "Content-Type: application/json" \
  -d '{"taskId": "weekly_investment_collection"}'
```

### 3. Vercel Cron 테스트

**환경 변수 설정 (Vercel Dashboard):**
```
CRON_SECRET=your_random_secret_string_here
```

**Cron 엔드포인트 테스트:**
```bash
# 인증 성공
curl https://your-domain.vercel.app/api/cron/weekly-collection \
  -H "Authorization: Bearer your_random_secret_string_here"

# 인증 실패 (401 에러 예상)
curl https://your-domain.vercel.app/api/cron/weekly-collection \
  -H "Authorization: Bearer wrong_secret"
```

### 4. Vercel Cron 로그 확인

```
1. Vercel Dashboard 접속
2. 프로젝트 선택
3. "Cron Jobs" 탭 클릭
4. "weekly-collection" 작업 확인
5. 실행 이력 및 로그 확인
```

---

## 참조

- Task Instruction: `task-instructions/S4O1_instruction.md`
- 기존 프로토타입:
  - `backend/app/core/scheduler.py` (165줄)
  - `backend/app/tasks/weekly_collection.py` (77줄)
- Vercel Cron Jobs: https://vercel.com/docs/cron-jobs

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
