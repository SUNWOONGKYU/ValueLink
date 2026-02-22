# ValueLink Deployment Guide

> Vercel 배포 및 GitHub Actions CI/CD 가이드

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [환경 변수 설정](#환경-변수-설정)
3. [배포 방법](#배포-방법)
4. [도메인 연결](#도메인-연결)
5. [롤백](#롤백)
6. [문제 해결](#문제-해결)

---

## 사전 준비

### 1. Vercel 계정 생성

1. https://vercel.com 접속
2. GitHub 계정으로 회원가입
3. Organization/Team 생성 (선택)

### 2. Vercel CLI 설치

```bash
npm install -g vercel
```

### 3. Vercel CLI 로그인

```bash
vercel login
```

### 4. 프로젝트 연동

```bash
vercel link
```

실행 후 다음 정보 확인:
- `VERCEL_ORG_ID`: Organization ID
- `VERCEL_PROJECT_ID`: Project ID

`.vercel/project.json` 파일에서 확인 가능:
```json
{
  "orgId": "your_org_id",
  "projectId": "your_project_id"
}
```

---

## 환경 변수 설정

### 필수 환경 변수 (5개)

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase 프로젝트 URL | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Anon Key | `eyJhbGciOiJIUzI1...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | `eyJhbGciOiJIUzI1...` |
| `CRON_SECRET` | Cron Job 인증 키 | `your-secret-key-123` |
| `RESEND_API_KEY` | Resend 이메일 API 키 | `re_xxx` |

### Vercel Dashboard에서 설정

1. Vercel Dashboard → 프로젝트 선택
2. **Settings** → **Environment Variables**
3. 각 변수 추가:
   - Name: 변수명
   - Value: 변수값
   - Environment: Production, Preview, Development 선택
4. **Save** 클릭

### GitHub Secrets 설정 (CI/CD용)

1. GitHub 레포지토리 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. 다음 Secrets 추가:

| Secret 이름 | 값 |
|-------------|-----|
| `VERCEL_TOKEN` | Vercel Dashboard → Settings → Tokens에서 생성 |
| `VERCEL_ORG_ID` | `.vercel/project.json`의 `orgId` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json`의 `projectId` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Anon Key |

---

## 배포 방법

### 방법 1: GitHub Actions (자동 배포) ⭐ 권장

**특징:**
- `main` 브랜치 push 시 자동 배포
- PR 생성 시 Preview 배포 자동 생성
- CI 파이프라인 자동 실행 (lint → type-check → build → test)

**사용법:**
```bash
# 코드 수정 후
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin main
```

GitHub Actions가 자동으로:
1. ✅ ESLint 검사
2. ✅ TypeScript 타입 체크
3. ✅ Next.js 빌드
4. ✅ 테스트 실행 (있으면)
5. ✅ Vercel 배포

**진행 상황 확인:**
- GitHub 레포지토리 → **Actions** 탭

---

### 방법 2: 로컬 스크립트 (`scripts/deploy.sh`)

**특징:**
- 로컬에서 직접 배포
- Pre-flight 체크 (환경 변수, Git 상태, 브랜치)
- Lint → Type Check → Build → Deploy 순서 자동 실행

**사용법:**
```bash
# 환경 변수 설정
export VERCEL_TOKEN="your_token"
export VERCEL_ORG_ID="your_org_id"
export VERCEL_PROJECT_ID="your_project_id"

# 배포 실행
bash scripts/deploy.sh
```

**스크립트가 하는 일:**
1. ✅ 환경 변수 확인
2. ✅ Git 상태 확인 (미커밋 변경사항 경고)
3. ✅ 브랜치 확인 (main/master가 아니면 preview 배포)
4. ✅ ESLint 실행
5. ✅ TypeScript 타입 체크
6. ✅ Next.js 빌드
7. ✅ Vercel 배포
8. ✅ 배포 URL 출력

---

### 방법 3: Vercel CLI (수동 배포)

**특징:**
- 가장 빠른 배포 방법
- 체크 없이 즉시 배포

**사용법:**

#### Production 배포
```bash
vercel --prod
```

#### Preview 배포
```bash
vercel
```

**주의:**
- Pre-flight 체크 없음 (lint, type-check 생략)
- Git 상태 확인 없음
- 빠르지만 위험할 수 있음

---

## 도메인 연결

### 커스텀 도메인 추가

1. Vercel Dashboard → 프로젝트 선택 → **Settings** → **Domains**
2. **Add** 클릭
3. 도메인 입력 (예: `www.valuelink.co.kr`)
4. DNS 설정 안내 확인

### DNS 설정

도메인 등록 업체(가비아, 카페24 등)에서:

**A Record:**
```
Type: A
Name: @
Value: 76.76.21.21
```

**CNAME Record:**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**적용 시간:**
- 보통 5분~1시간
- 최대 24시간

---

## 롤백

### Vercel Dashboard에서 롤백

1. Vercel Dashboard → 프로젝트 선택 → **Deployments**
2. 이전 배포 선택
3. **⋯** (메뉴) → **Promote to Production**

### CLI에서 롤백

```bash
# 최근 배포 목록 확인
vercel ls

# 특정 배포로 롤백 (URL 사용)
vercel promote https://valuelink-xxx.vercel.app
```

### Git에서 롤백

```bash
# 이전 커밋으로 되돌리기
git revert HEAD
git push origin main

# GitHub Actions가 자동으로 재배포
```

---

## 문제 해결

### 1. 배포 실패: "Build Error"

**원인:**
- TypeScript 타입 에러
- ESLint 에러
- 환경 변수 누락

**해결:**
```bash
# 로컬에서 빌드 테스트
npm run build

# 타입 체크
npx tsc --noEmit

# ESLint 실행
npm run lint
```

---

### 2. 배포 성공했지만 페이지 404

**원인:**
- 라우팅 설정 문제
- `vercel.json`의 `redirects` 설정 확인

**해결:**
```json
{
  "redirects": [
    {
      "source": "/",
      "destination": "/pages/landing.html",
      "permanent": false
    }
  ]
}
```

---

### 3. API 요청 CORS 에러

**원인:**
- 보안 헤더 설정 문제

**해결:**
`vercel.json`에서 CORS 헤더 추가:
```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,POST,PUT,DELETE,OPTIONS" }
      ]
    }
  ]
}
```

---

### 4. 환경 변수가 안 읽힘

**원인:**
- Vercel Dashboard에 환경 변수 미설정
- 변수명 오타

**해결:**
1. Vercel Dashboard → Settings → Environment Variables 확인
2. 변수명이 정확한지 확인 (`NEXT_PUBLIC_` 접두사 필수)
3. 재배포 (환경 변수 변경 후 재배포 필수)

---

### 5. Cron Job이 실행 안 됨

**원인:**
- `CRON_SECRET` 미설정
- Cron 경로 오류

**해결:**
1. `vercel.json`의 `crons` 설정 확인:
```json
{
  "crons": [
    {
      "path": "/api/External/deal-news-tracker",
      "schedule": "0 6 * * 0"
    }
  ]
}
```

2. API 함수에서 `CRON_SECRET` 검증:
```javascript
if (req.headers['x-vercel-cron'] !== process.env.CRON_SECRET) {
  return res.status(401).json({ error: 'Unauthorized' });
}
```

---

### 6. GitHub Actions 실패: "VERCEL_TOKEN not found"

**원인:**
- GitHub Secrets 미설정

**해결:**
1. GitHub → Settings → Secrets and variables → Actions
2. `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` 추가

---

## Cron Jobs 설정

### deal-news-tracker (주간 뉴스 수집)

**실행 시간:**
- 매주 일요일 오전 6시 (KST 기준)
- Cron 표현식: `0 6 * * 0`

**경로:**
- `/api/External/deal-news-tracker`

**동작:**
1. Vercel이 매주 일요일 6시에 API 호출
2. `CRON_SECRET` 헤더로 인증
3. 최근 7일간 투자 뉴스 수집
4. Supabase `deals` 테이블에 저장

**로그 확인:**
- Vercel Dashboard → 프로젝트 → **Logs** → Cron 탭

---

## 보안 체크리스트

- [ ] 모든 환경 변수가 GitHub Secrets에 저장되었는가?
- [ ] 코드에 API 키가 하드코딩되지 않았는가?
- [ ] 보안 헤더 5종이 설정되었는가?
- [ ] `CRON_SECRET`으로 Cron Job을 인증하는가?
- [ ] Supabase Row Level Security (RLS)가 활성화되었는가?

---

## 참고 링크

- [Vercel 공식 문서](https://vercel.com/docs)
- [Next.js 배포 가이드](https://nextjs.org/docs/deployment)
- [GitHub Actions 문서](https://docs.github.com/actions)
- [Vercel CLI 문서](https://vercel.com/docs/cli)

---

**작성일**: 2026-02-22
**작성자**: Claude Code (Opus 4.6)
**Task**: S5O1 (배포 설정 및 CI/CD 파이프라인)
