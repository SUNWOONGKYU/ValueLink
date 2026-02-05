# S5O1 Verification

## 검증 대상

- **Task ID**: S5O1
- **Task Name**: 배포 설정 및 CI/CD
- **Stage**: S5 (개발 마무리)
- **Area**: O (DevOps)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **vercel.json 문법 검증** (JSON 파서로 확인)
- [ ] **GitHub Actions YAML 문법** (`yamllint` 통과)
- [ ] **Bash 스크립트 문법** (`shellcheck` 통과)
- [ ] **Markdown 렌더링** (deployment-guide.md 표시 정상)

---

### 2. 파일 생성 확인

- [ ] **`vercel.json` 존재** (루트 디렉토리)
- [ ] **`.github/workflows/ci.yml` 존재**
- [ ] **`.github/workflows/cd.yml` 존재**
- [ ] **`scripts/deploy.sh` 존재** (실행 권한 `chmod +x`)
- [ ] **`docs/deployment-guide.md` 존재**

---

### 3. 핵심 기능 테스트

#### 3.1 vercel.json 설정

- [ ] **regions 설정**
  - `"icn1"` (Seoul) 포함

- [ ] **Cron Jobs 설정**
  - path: `/api/cron/weekly-collection`
  - schedule: `0 6 * * 0` (일요일 오전 6시 KST)

- [ ] **환경 변수**
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `GOOGLE_AI_API_KEY`
  - `CRON_SECRET`

- [ ] **보안 헤더**
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: strict-origin-when-cross-origin

- [ ] **Rewrites (선택)**
  - `/api/*` → API 라우트

#### 3.2 CI Workflow (.github/workflows/ci.yml)

- [ ] **트리거 조건**
  - `push` (main, develop 브랜치)
  - `pull_request` (main 브랜치)

- [ ] **Job: lint**
  - ESLint 실행 (`npm run lint`)
  - 에러 시 워크플로우 중단

- [ ] **Job: type-check**
  - TypeScript 컴파일 (`npm run type-check`)
  - 에러 시 워크플로우 중단

- [ ] **Job: build**
  - Next.js 빌드 (`npm run build`)
  - 의존성: lint, type-check 성공

- [ ] **Job: test**
  - Jest 테스트 실행 (`npm test`)
  - 커버리지 리포트 생성

#### 3.3 CD Workflow (.github/workflows/cd.yml)

- [ ] **트리거 조건**
  - `push` (main 브랜치만)

- [ ] **Job: deploy**
  - Vercel CLI 사용
  - `vercel deploy --prod` 실행
  - `VERCEL_TOKEN` Secret 사용

- [ ] **환경 변수 동기화**
  - GitHub Secrets → Vercel Environment Variables
  - 프로덕션 전용 변수 설정

#### 3.4 배포 스크립트 (scripts/deploy.sh)

- [ ] **사전 점검**
  - Git 상태 확인 (변경사항 없어야 함)
  - ESLint 실행
  - TypeScript 체크
  - 빌드 테스트

- [ ] **배포 실행**
  - `vercel --prod` 실행
  - 배포 URL 출력

- [ ] **롤백 기능**
  - 이전 배포로 되돌리기
  - `vercel rollback` 사용

- [ ] **실행 권한**
  - `chmod +x scripts/deploy.sh` 확인

#### 3.5 배포 가이드 (docs/deployment-guide.md)

- [ ] **목차 (TOC) 포함**

- [ ] **섹션 구성**
  - 개요
  - Vercel 프로젝트 생성
  - 환경 변수 설정
  - Cron Jobs 설정
  - CI/CD 파이프라인
  - 배포 프로세스
  - 롤백 절차
  - 트러블슈팅

- [ ] **코드 예시 포함**
  - Vercel CLI 명령어
  - GitHub Actions YAML
  - 배포 스크립트 사용법

- [ ] **스크린샷 (선택)**
  - Vercel Dashboard
  - GitHub Actions 실행 화면

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **S1BI1 (Next.js + Supabase 설정)**
  - 환경 변수 참조 가능

- [ ] **S4O1 (스케줄러)**
  - Cron Jobs가 `/api/cron/weekly-collection` 호출

#### 4.2 로컬 배포 테스트

```bash
# Vercel CLI 로그인
vercel login

# 로컬에서 배포 테스트 (Preview)
vercel

# 프로덕션 배포 테스트
vercel --prod

# 배포 상태 확인
vercel ls
```

- [ ] **Preview 배포 성공**
- [ ] **프로덕션 배포 성공**
- [ ] **배포 URL 접속 가능**
- [ ] **환경 변수 적용 확인**

#### 4.3 GitHub Actions 테스트

```bash
# CI 워크플로우 트리거
git checkout -b test-ci
git commit --allow-empty -m "Test CI"
git push origin test-ci

# GitHub → Actions 탭 확인
# ✅ lint, type-check, build, test 모두 성공
```

- [ ] **CI 워크플로우 실행 성공**
- [ ] **모든 Job 통과**
- [ ] **실행 시간 10분 이내**

```bash
# CD 워크플로우 트리거
git checkout main
git merge test-ci
git push origin main

# GitHub → Actions 탭 확인
# ✅ deploy Job 성공
```

- [ ] **CD 워크플로우 실행 성공**
- [ ] **Vercel에 자동 배포**
- [ ] **배포 URL 확인**

#### 4.4 Cron Jobs 테스트

**Vercel Dashboard에서:**
1. Cron Jobs 탭 클릭
2. `weekly-collection` 작업 확인
3. Schedule: `0 6 * * 0` 확인

**수동 실행 테스트:**
```bash
# CRON_SECRET 환경 변수 설정 필요
curl https://your-domain.vercel.app/api/cron/weekly-collection \
  -H "Authorization: Bearer ${CRON_SECRET}"

# 예상 응답: {"success": true}
```

- [ ] **Cron 작업 등록 확인**
- [ ] **수동 실행 성공**
- [ ] **CRON_SECRET 검증 작동**
- [ ] **인증 실패 시 401 에러**

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - 모든 S1-S4 Task 완료 확인

- [ ] **환경 차단**
  - Vercel 계정 생성 확인
  - GitHub 레포지토리 연동 확인
  - `VERCEL_TOKEN` Secret 설정 확인

- [ ] **외부 API 차단**
  - Vercel API 접근 가능
  - GitHub Actions 실행 가능

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **5개 파일 생성 완료** ✅
3. **vercel.json 설정 정확** ✅
4. **CI/CD 파이프라인 작동** ✅
5. **배포 성공 (Preview + Production)** ✅
6. **Cron Jobs 등록 확인** ✅
7. **배포 가이드 작성** ✅

### 권장 (Nice to Pass)

1. **자동 롤백** ✨ (배포 실패 시)
2. **Slack 알림** ✨ (배포 완료/실패 시)
3. **성능 모니터링** ✨ (Vercel Analytics)

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **Vercel 무료 플랜 제한**
   - 빌드 시간: 45분
   - Bandwidth: 100GB/월
   - Cron Jobs: 월 1,000회
   - 초과 시 유료 플랜 필요

2. **환경 변수 보안**
   - GitHub Secrets에 저장
   - 절대 하드코딩 금지
   - `.env.local` 파일 커밋 금지 (`.gitignore` 확인)

3. **Cron Schedule 주의**
   - 시간대: UTC (Vercel 기본값)
   - 한국 시간으로 변환: KST = UTC + 9시간
   - `0 6 * * 0` (KST 일요일 오전 6시) = `0 21 * * 6` (UTC 토요일 오후 9시)
   - **⚠️ 중요**: Vercel Cron은 UTC 기준!

4. **GitHub Actions 병렬 실행**
   - CI 워크플로우의 4개 Job은 병렬 실행 (빠름)
   - CD 워크플로우는 순차 실행 (안전)

5. **배포 실패 시**
   - Vercel Dashboard → Deployments → 실패한 배포 클릭
   - Build Logs 확인
   - Function Logs 확인
   - Runtime Logs 확인

6. **롤백 시나리오**
   - 배포 후 버그 발견 시: `vercel rollback`
   - 이전 배포로 즉시 복원
   - 데이터베이스 마이그레이션 주의 (역방향 마이그레이션 필요)

7. **Seoul Region (icn1)**
   - 한국 사용자 대상 → 낮은 latency
   - `vercel.json`의 `regions` 필드에 명시

---

## PO 테스트 가이드

### 1. Vercel CLI 설치 및 로그인

```bash
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login
# 브라우저에서 인증
```

### 2. 로컬 배포 테스트 (Preview)

```bash
# 프로젝트 루트에서
vercel

# 질문에 답변:
# Set up and deploy "..."? Y
# Which scope? (개인 계정 선택)
# Link to existing project? N
# What's your project's name? valuelink
# In which directory is your code located? ./
# Auto-detected Project Settings (Next.js)
# Override settings? N

# 배포 완료 후 Preview URL 확인:
# Preview: https://valuelink-xxx.vercel.app
```

**브라우저에서 Preview URL 접속:**
- [ ] 메인 페이지 로딩 확인
- [ ] 로그인 기능 작동 확인
- [ ] API 엔드포인트 작동 확인

### 3. 프로덕션 배포 테스트

```bash
# 프로덕션 배포
vercel --prod

# 배포 완료 후 Production URL 확인:
# Production: https://valuelink.vercel.app
```

**브라우저에서 Production URL 접속:**
- [ ] 모든 페이지 정상 작동
- [ ] 환경 변수 적용 확인 (AI API 호출 성공)
- [ ] Cron Jobs 등록 확인 (Vercel Dashboard)

### 4. GitHub Actions 확인

**GitHub 레포지토리에서:**
1. Actions 탭 클릭
2. CI 워크플로우 실행 확인
   - [ ] lint ✅
   - [ ] type-check ✅
   - [ ] build ✅
   - [ ] test ✅
3. CD 워크플로우 실행 확인
   - [ ] deploy ✅

### 5. Vercel Dashboard 확인

**Vercel Dashboard (vercel.com):**
1. 프로젝트 선택
2. Deployments 탭
   - [ ] 최신 배포 성공 확인
3. Settings → Environment Variables
   - [ ] 7개 환경 변수 설정 확인
4. Settings → Cron Jobs
   - [ ] `weekly-collection` 작업 확인

### 6. Cron Jobs 수동 테스트

```bash
# CRON_SECRET 환경 변수 복사 (Vercel Dashboard → Settings → Environment Variables)
export CRON_SECRET=your-secret-here

# Cron 엔드포인트 호출
curl https://valuelink.vercel.app/api/cron/weekly-collection \
  -H "Authorization: Bearer ${CRON_SECRET}"

# 예상 응답:
# {"success": true}
```

- [ ] 인증 성공 시 200 응답
- [ ] 인증 실패 시 401 응답

### 7. 배포 스크립트 테스트

```bash
# 배포 스크립트 실행 (사전 점검 포함)
./scripts/deploy.sh

# 예상 출력:
# ===========================
# ValueLink Deployment Script
# ===========================
# [1/4] Checking Git status...
# ✅ Git status: clean
# [2/4] Running ESLint...
# ✅ ESLint: passed
# [3/4] Type checking...
# ✅ Type check: passed
# [4/4] Building...
# ✅ Build: passed
# Starting production deployment...
# ✅ Deployed to: https://valuelink.vercel.app
```

- [ ] 사전 점검 모두 통과
- [ ] 프로덕션 배포 성공
- [ ] 배포 URL 출력

---

## 참조

- Task Instruction: `task-instructions/S5O1_instruction.md`
- Vercel 공식 문서: https://vercel.com/docs
- GitHub Actions 문서: https://docs.github.com/en/actions
- Vercel Cron Jobs: https://vercel.com/docs/cron-jobs

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
