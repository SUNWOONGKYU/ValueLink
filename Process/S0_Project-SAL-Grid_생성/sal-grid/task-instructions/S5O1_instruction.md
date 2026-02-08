# S5O1: Deployment Configuration & CI/CD (신규 구현)

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

**Vercel 배포 설정 및 GitHub Actions CI/CD 파이프라인 구축**

- Vercel 배포 설정 (vercel.json)
- CI 파이프라인 (lint → type-check → build → test)
- CD 파이프라인 (자동 배포)
- 배포 스크립트 및 가이드

---

## 🎯 개선 필수 영역

### 1️⃣ 보안 강화
- ✅ 보안 헤더 설정 (X-Content-Type-Options, X-Frame-Options 등)
- ✅ Permissions-Policy 헤더 추가
- ✅ CRON_SECRET 인증
- ✅ GitHub Secrets로 환경 변수 관리

### 2️⃣ 자동화
- ✅ GitHub Actions CI/CD
- ✅ Vercel Cron Jobs (주간 뉴스 수집)
- ✅ PR 시 자동 Preview 배포
- ✅ main 브랜치 자동 프로덕션 배포

### 3️⃣ 안정성
- ✅ 롤백 가능한 배포 구조
- ✅ 빌드 실패 시 자동 중단
- ✅ 환경 변수 검증

---

## 상세 지시사항

### 1. Vercel 배포 설정

**파일**: `vercel.json`

**핵심 설정:**
- `regions`: `["icn1"]` (서울 리전)
- `crons`: 주간 뉴스 수집 (`0 6 * * 0`)
- `headers`: 보안 헤더 5종
- `env`: Supabase, CRON_SECRET, Resend API Key

**보안 헤더 (필수):**
```json
{
  "headers": [{
    "source": "/(.*)",
    "headers": [
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "X-XSS-Protection", "value": "1; mode=block" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
      { "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=()" }
    ]
  }]
}
```

---

### 2. CI 파이프라인

**파일**: `.github/workflows/ci.yml`

**Job 구성 (4개):**

| Job | 설명 | 실행 조건 |
|-----|------|----------|
| lint | ESLint + Prettier | push, PR |
| type-check | TypeScript 타입 체크 | push, PR |
| build | Next.js 빌드 | push, PR |
| test | Jest + Playwright | lint, type-check 완료 후 |

**핵심:**
- Node.js 20.x, npm cache 활용
- `npm ci` (lock 파일 기반 설치)
- 병렬 실행 (lint + type-check) → 순차 실행 (build, test)

---

### 3. CD 파이프라인

**파일**: `.github/workflows/cd.yml`

**핵심:**
- `main` 브랜치 push 시 자동 실행
- Vercel CLI로 배포
- 성공/실패 알림

**필요한 GitHub Secrets:**
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

### 4. 배포 스크립트

**파일**: `scripts/deploy.sh`

**기능:**
- 환경 변수 확인 (VERCEL_TOKEN, ORG_ID, PROJECT_ID)
- Git 상태 확인 (커밋 안 된 변경사항 경고)
- 브랜치 확인 (main이 아니면 경고)
- lint → type-check → build → deploy 순서
- 배포 URL 출력

---

### 5. 배포 가이드 문서

**파일**: `docs/deployment-guide.md`

**포함 내용:**
- 사전 준비 (Vercel 계정, CLI 설치)
- 환경 변수 설정 (5개 필수 변수)
- 배포 방법 3가지 (GitHub Actions, 로컬 스크립트, Vercel CLI)
- 도메인 연결
- 롤백 방법
- 문제 해결

---

## 생성 파일

| # | 파일 | 설명 | 라인 수 |
|---|------|------|--------|
| 1 | `vercel.json` | Vercel 배포 설정 | ~60줄 |
| 2 | `.github/workflows/ci.yml` | CI 파이프라인 | ~90줄 |
| 3 | `.github/workflows/cd.yml` | CD 파이프라인 | ~60줄 |
| 4 | `scripts/deploy.sh` | 배포 스크립트 | ~100줄 |
| 5 | `docs/deployment-guide.md` | 배포 가이드 | ~250줄 |

**총 파일 수**: 5개
**총 라인 수**: ~560줄

---

## 완료 기준

### 필수 (Must Have)
- [ ] `vercel.json` 설정 완료
- [ ] CI 파이프라인 작동 (lint, type-check, build, test)
- [ ] CD 파이프라인 작동 (자동 배포)
- [ ] `scripts/deploy.sh` 실행 가능
- [ ] `docs/deployment-guide.md` 작성 완료
- [ ] 보안 헤더 5종 설정
- [ ] Cron Jobs 설정

### 검증 (Verification)
- [ ] CI 파이프라인 실행 성공
- [ ] CD 파이프라인 실행 성공
- [ ] Vercel 배포 성공
- [ ] 보안 헤더 적용 확인

---

## 주의사항

1. **환경 변수 보안**: Secrets는 GitHub Secrets에만 저장, 절대 코드에 하드코딩 금지
2. **Vercel 리전**: `icn1` (서울) 고정
3. **npm ci**: `npm install` 대신 사용 (재현 가능한 빌드)
4. **브랜치 전략**: `main` = 프로덕션, PR = Preview 배포

---

**작성일**: 2026-02-08 (REVISED)
**작성자**: Claude Code (Opus 4.6)
**수정 이유**: 신규 구현 방식으로 정리, 보안 강화, 자동화 개선
