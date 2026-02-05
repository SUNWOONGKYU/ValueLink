# S5O1: Deployment Configuration & CI/CD

## Task 정보

- **Task ID**: S5O1
- **Task Name**: 배포 설정 및 CI/CD 파이프라인
- **Stage**: S5 (Finalization - 개발 마무리)
- **Area**: O (DevOps)
- **Dependencies**: 모든 S2-S4 Task 완료
- **Task Agent**: devops-troubleshooter
- **Verification Agent**: code-reviewer

---

## Task 목표

Vercel 배포 설정 및 GitHub Actions CI/CD 파이프라인 구축

---

## 상세 지시사항

### 1. Vercel 배포 설정

**파일**: `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["icn1"],
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase_url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase_anon_key",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase_service_role_key",
    "CRON_SECRET": "@cron_secret",
    "RESEND_API_KEY": "@resend_api_key"
  },
  "crons": [
    {
      "path": "/api/cron/weekly-collection",
      "schedule": "0 6 * * 0"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ]
}
```

---

### 2. CI 파이프라인 (Continuous Integration)

**파일**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Check formatting
        run: npm run format:check

  type-check:
    name: TypeScript Type Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run type-check

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build project
        run: npm run build
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: .next/

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: [lint, type-check]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella
```

---

### 3. CD 파이프라인 (Continuous Deployment)

**파일**: `.github/workflows/cd.yml`

```yaml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy to Vercel
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Vercel CLI
        run: npm install -g vercel@latest

      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Deploy to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Notify deployment success
        if: success()
        run: |
          echo "Deployment successful!"
          echo "URL: https://valuelink.vercel.app"

      - name: Notify deployment failure
        if: failure()
        run: |
          echo "Deployment failed!"
          exit 1
```

---

### 4. 배포 스크립트

**파일**: `scripts/deploy.sh`

```bash
#!/bin/bash

# ValueLink Deployment Script
# 로컬에서 프로덕션 배포 시 사용

set -e

echo "========================================"
echo "ValueLink Deployment Script"
echo "========================================"
echo ""

# 환경 확인
if [ -z "$VERCEL_TOKEN" ]; then
  echo "❌ Error: VERCEL_TOKEN 환경 변수가 설정되지 않았습니다."
  echo "   export VERCEL_TOKEN=your_token_here"
  exit 1
fi

if [ -z "$VERCEL_ORG_ID" ]; then
  echo "❌ Error: VERCEL_ORG_ID 환경 변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$VERCEL_PROJECT_ID" ]; then
  echo "❌ Error: VERCEL_PROJECT_ID 환경 변수가 설정되지 않았습니다."
  exit 1
fi

# Git 상태 확인
echo "📋 Git 상태 확인..."
if [[ -n $(git status -s) ]]; then
  echo "⚠️  Warning: 커밋되지 않은 변경사항이 있습니다."
  read -p "계속하시겠습니까? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# 브랜치 확인
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📌 현재 브랜치: $BRANCH"

if [ "$BRANCH" != "main" ]; then
  echo "⚠️  Warning: main 브랜치가 아닙니다."
  read -p "계속하시겠습니까? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# 의존성 설치
echo ""
echo "📦 의존성 설치..."
npm ci

# Lint 검사
echo ""
echo "🔍 ESLint 검사..."
npm run lint

# TypeScript 타입 체크
echo ""
echo "📝 TypeScript 타입 체크..."
npm run type-check

# 빌드
echo ""
echo "🏗️  프로젝트 빌드..."
npm run build

# Vercel CLI 설치 확인
if ! command -v vercel &> /dev/null; then
  echo ""
  echo "📥 Vercel CLI 설치..."
  npm install -g vercel@latest
fi

# Vercel 배포
echo ""
echo "🚀 Vercel 배포 시작..."

vercel pull --yes --environment=production --token=$VERCEL_TOKEN
vercel build --prod --token=$VERCEL_TOKEN
DEPLOYMENT_URL=$(vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN)

echo ""
echo "========================================"
echo "✅ 배포 완료!"
echo "========================================"
echo "URL: $DEPLOYMENT_URL"
echo ""
```

---

### 5. 배포 가이드

**파일**: `docs/deployment-guide.md`

```markdown
# ValueLink 배포 가이드

## 개요

ValueLink 플랫폼을 Vercel에 배포하는 방법을 설명합니다.

---

## 사전 준비

### 1. Vercel 계정 생성

- https://vercel.com 접속
- GitHub 계정으로 로그인
- Organization 생성 (또는 Personal 사용)

### 2. Vercel CLI 설치

```bash
npm install -g vercel@latest
```

### 3. Vercel 로그인

```bash
vercel login
```

---

## 환경 변수 설정

### Vercel Dashboard에서 설정

1. Vercel Dashboard 접속
2. 프로젝트 선택
3. Settings → Environment Variables
4. 다음 환경 변수 추가:

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase 프로젝트 URL | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Anon Key | `eyJhbG...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | `eyJhbG...` |
| `CRON_SECRET` | Cron Job 인증 키 | 랜덤 문자열 |
| `RESEND_API_KEY` | Resend API Key | `re_...` |

---

## 배포 방법

### 방법 1: GitHub Actions (권장)

**자동 배포 (main 브랜치 푸시 시):**

```bash
git add .
git commit -m "feat: 새 기능 추가"
git push origin main
```

- GitHub Actions가 자동으로 CI/CD 실행
- `.github/workflows/cd.yml` 파이프라인 실행
- 배포 완료 후 Vercel URL 생성

**필요한 GitHub Secrets:**
- `VERCEL_TOKEN`: Vercel Access Token
- `VERCEL_ORG_ID`: Vercel Organization ID
- `VERCEL_PROJECT_ID`: Vercel Project ID

### 방법 2: 로컬 배포 스크립트

```bash
# 환경 변수 설정
export VERCEL_TOKEN=your_token
export VERCEL_ORG_ID=your_org_id
export VERCEL_PROJECT_ID=your_project_id

# 배포 스크립트 실행
bash scripts/deploy.sh
```

### 방법 3: Vercel CLI (수동)

```bash
# 프로덕션 배포
vercel --prod

# 프리뷰 배포
vercel
```

---

## 배포 확인

### 1. Vercel Dashboard 확인

- Deployments 탭에서 배포 상태 확인
- 빌드 로그 확인
- 배포 URL 확인

### 2. 브라우저 접속

```
https://valuelink.vercel.app
```

### 3. 헬스 체크

```bash
curl https://valuelink.vercel.app/api/health
```

---

## 도메인 연결

### 1. Vercel Dashboard에서 도메인 추가

1. Vercel Dashboard → 프로젝트 → Settings → Domains
2. "Add Domain" 클릭
3. 도메인 입력 (예: `valuelink.ai`)
4. DNS 설정 안내에 따라 도메인 DNS 레코드 추가

### 2. DNS 레코드 (예시)

| Type | Name | Value |
|------|------|-------|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com |

---

## 롤백

### 특정 버전으로 롤백

1. Vercel Dashboard → Deployments
2. 이전 배포 버전 선택
3. "Promote to Production" 클릭

### CLI로 롤백

```bash
vercel rollback
```

---

## 문제 해결

### 빌드 실패

**증상:** 빌드 중 에러 발생

**해결:**
1. 로컬에서 `npm run build` 실행하여 빌드 에러 확인
2. 환경 변수 누락 확인
3. 의존성 버전 충돌 확인

### 환경 변수 누락

**증상:** Runtime에서 `undefined` 에러

**해결:**
1. Vercel Dashboard → Settings → Environment Variables 확인
2. `NEXT_PUBLIC_` 접두사 확인 (클라이언트 사이드 변수)
3. 배포 후 "Redeploy" 실행

### Cron Job 실패

**증상:** 주간 수집 작업 실행 안 됨

**해결:**
1. `CRON_SECRET` 환경 변수 설정 확인
2. `/api/cron/weekly-collection` 엔드포인트 직접 호출 테스트
3. Vercel Dashboard → Cron Jobs 탭에서 실행 이력 확인

---

## 모니터링

### Vercel Analytics

- Vercel Dashboard → Analytics
- 트래픽, 성능 지표 확인

### Vercel Logs

```bash
vercel logs
```

### Sentry (권장)

- 에러 모니터링 도구
- https://sentry.io

---

## 참고 자료

- Vercel 공식 문서: https://vercel.com/docs
- Next.js 배포 가이드: https://nextjs.org/docs/deployment
- Supabase 연동: https://supabase.com/docs/guides/getting-started/quickstarts/nextjs
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|-----------------|
| `vercel.json` | Vercel 배포 설정 | ~60줄 |
| `.github/workflows/ci.yml` | CI 파이프라인 | ~90줄 |
| `.github/workflows/cd.yml` | CD 파이프라인 | ~60줄 |
| `scripts/deploy.sh` | 배포 스크립트 | ~100줄 |
| `docs/deployment-guide.md` | 배포 가이드 | ~250줄 |

**총 파일 수**: 5개
**총 라인 수**: ~560줄

---

## 기술 스택

- **Vercel**: Frontend Hosting (Next.js)
- **GitHub Actions**: CI/CD 자동화
- **Vercel CLI**: 배포 도구
- **Bash**: 배포 스크립트

---

## 완료 기준

### 필수 (Must Have)

- [ ] `vercel.json` 설정 파일 생성
- [ ] CI 파이프라인 구성 (lint, type-check, build, test)
- [ ] CD 파이프라인 구성 (자동 배포)
- [ ] 배포 스크립트 (`deploy.sh`) 작성
- [ ] 배포 가이드 문서 작성
- [ ] 환경 변수 문서화
- [ ] 보안 헤더 설정
- [ ] Cron Jobs 설정

### 검증 (Verification)

- [ ] CI 파이프라인 실행 성공
- [ ] CD 파이프라인 실행 성공
- [ ] Vercel 배포 성공
- [ ] 환경 변수 적용 확인
- [ ] 보안 헤더 적용 확인
- [ ] Cron Jobs 동작 확인

### 권장 (Nice to Have)

- [ ] Preview 배포 (PR별)
- [ ] E2E 테스트 자동화
- [ ] Sentry 연동
- [ ] 커스텀 도메인 연결

---

## 참조

### 기존 프로토타입
- 없음 (신규 작성)

### 의존성
- 모든 S2-S4 Task 완료

---

## 주의사항

1. **환경 변수 보안**
   - Secrets는 GitHub Secrets에 저장
   - 절대 코드에 하드코딩하지 않음
   - `.env.local`은 `.gitignore`에 포함

2. **브랜치 전략**
   - `main`: 프로덕션 배포
   - `develop`: 스테이징 배포 (선택)
   - PR: Preview 배포

3. **빌드 최적화**
   - `npm ci` 사용 (package-lock.json 고정)
   - 캐시 활용 (GitHub Actions cache)

4. **보안 헤더**
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - Referrer-Policy

5. **Vercel 리전**
   - `icn1`: 서울 리전
   - 한국 사용자 대상 최적화

6. **배포 전 체크리스트**
   - Lint 통과
   - TypeScript 타입 체크
   - 빌드 성공
   - 환경 변수 설정

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
