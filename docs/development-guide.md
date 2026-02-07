# Development Workflow Guide

## 개요

ValueLink 플랫폼 개발을 위한 Git 전략, 브랜치 규칙, PR 프로세스, CI/CD 파이프라인 가이드입니다.

---

## Git 전략

### 브랜치 전략 (Git Flow 변형)

```
main (프로덕션)
  ↑
develop (개발 통합)
  ↑
task/* (기능 개발)
hotfix/* (긴급 수정)
```

| 브랜치 | 용도 | 보호 정책 |
|--------|------|----------|
| `main` | 프로덕션 배포 | 직접 push 금지, PR 필수 |
| `develop` | 개발 통합 | PR 필수, CI 통과 필수 |
| `task/*` | 기능 개발 | 자유 push |
| `hotfix/*` | 긴급 수정 | main에서 분기, 양쪽 merge |

---

## 브랜치 명명 규칙

### Task 브랜치 (Feature)

**형식**: `task/{TaskID}-{간단한-설명}`

**예시**:
```
task/S2F1-valuation-results-pages
task/S3BA3-dcf-engine
task/S1BI1-supabase-client
task/S2BA2-projects-api
```

**규칙**:
- TaskID는 SAL Grid의 Task ID와 일치
- 설명은 kebab-case 사용
- 설명은 영문 권장 (한글도 가능)

### Hotfix 브랜치

**형식**: `hotfix/{issue-번호}-{간단한-설명}`

**예시**:
```
hotfix/issue-42-login-error
hotfix/issue-123-payment-bug
hotfix/critical-auth-bypass
```

---

## Commit 메시지 규칙

### Conventional Commits 사용

**형식**: `<type>(<TaskID>): <subject>`

**Types**:
| Type | 설명 | 예시 |
|------|------|------|
| `feat` | 새로운 기능 | `feat(S2F1): 평가 결과 페이지 구현` |
| `fix` | 버그 수정 | `fix(S2BA2): 프로젝트 조회 오류 수정` |
| `docs` | 문서 변경 | `docs(S1M1): API 명세서 작성` |
| `style` | 코드 포맷팅 | `style(S2F3): ESLint 경고 수정` |
| `refactor` | 코드 리팩토링 | `refactor(S3BA3): DCF 계산 로직 개선` |
| `test` | 테스트 추가/수정 | `test(S4T1): 인증 테스트 추가` |
| `chore` | 빌드/설정 변경 | `chore(S1O1): GitHub Actions 설정` |

### Commit 메시지 예시

**좋은 예시**:
```
feat(S2F1): 평가 결과 페이지 템플릿 구현

- 공통 템플릿 컴포넌트 생성
- 5개 평가 방법별 페이지 구현
- Recharts 그래프 통합

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**나쁜 예시**:
```
❌ update files
❌ fixed bug
❌ WIP
❌ asdf
```

### Co-Author 규칙

AI 어시스턴트와 협업 시 반드시 Co-Authored-By 포함:
```
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## Pull Request 프로세스

### 1. Task 브랜치 생성

```bash
# develop에서 최신 코드 가져오기
git checkout develop
git pull origin develop

# Task 브랜치 생성
git checkout -b task/S2F1-valuation-results-pages
```

### 2. 작업 및 커밋

```bash
# 작업 수행
# ...

# 변경 사항 스테이징
git add .

# 커밋 (Conventional Commits 형식)
git commit -m "feat(S2F1): 평가 결과 페이지 템플릿 구현"
```

### 3. Push 및 PR 생성

```bash
# 원격 저장소에 push
git push origin task/S2F1-valuation-results-pages

# GitHub에서 PR 생성 또는 gh CLI 사용
gh pr create --title "feat(S2F1): 평가 결과 페이지" --body-file .github/pull_request_template.md
```

### 4. PR 템플릿

```markdown
## Task 정보
- **Task ID**: S2F1
- **Task Name**: 평가 결과 페이지 템플릿 및 5개 방법별 페이지
- **Stage**: S2 (개발 1차)
- **Area**: F (Frontend)

## 변경 사항
- [x] 공통 템플릿 컴포넌트 생성
- [x] DCF 결과 페이지 구현
- [x] Relative 결과 페이지 구현
- [x] Asset 결과 페이지 구현
- [x] Intrinsic 결과 페이지 구현
- [x] Tax 결과 페이지 구현

## 테스트
- [x] TypeScript 컴파일 성공
- [x] ESLint 경고 0개
- [x] 수동 테스트 완료

## 스크린샷
(UI 변경 시 스크린샷 첨부)

## 관련 Task
- **Depends on**: S1BI1, S1D1
- **Blocks**: S2F2

## 검토 요청사항
- 템플릿 컴포넌트 재사용성 검토 필요
- 접근성(a11y) 확인 요청
```

### 5. Code Review

**리뷰어 체크리스트**:
- [ ] 코드가 Task Instruction을 따르는가?
- [ ] TypeScript 타입이 올바른가?
- [ ] 에러 처리가 적절한가?
- [ ] 테스트가 통과하는가?
- [ ] 보안 이슈가 없는가?
- [ ] 성능 이슈가 없는가?
- [ ] 문서화가 적절한가?

**리뷰 코멘트 예시**:
| 이모지 | 의미 | 사용 상황 |
|--------|------|----------|
| ✅ | LGTM | 승인 |
| 💬 | Question | 질문 |
| 💡 | Suggestion | 제안 |
| ⚠️ | Issue | 버그/문제 |
| 🔒 | Security | 보안 이슈 |
| 🚀 | Performance | 성능 이슈 |

### 6. Merge

```bash
# PR 승인 후
git checkout develop
git pull origin develop
git merge --no-ff task/S2F1-valuation-results-pages
git push origin develop

# Task 브랜치 삭제
git branch -d task/S2F1-valuation-results-pages
git push origin --delete task/S2F1-valuation-results-pages
```

**Merge 정책**:
- `--no-ff` (No Fast-Forward) 사용: Merge 커밋 유지
- Squash Merge는 사용하지 않음 (커밋 히스토리 보존)

---

## CI/CD 파이프라인

### GitHub Actions Workflow

**`.github/workflows/ci.yml`**:
```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  lint-and-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    needs: lint-and-type-check
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
```

### CI 체크 항목

| 단계 | 명령어 | 설명 |
|------|--------|------|
| Lint | `npm run lint` | ESLint 검사 |
| Type Check | `npm run type-check` | TypeScript 타입 검사 |
| Test | `npm run test` | 단위/통합 테스트 |
| Build | `npm run build` | 프로덕션 빌드 |

---

## 환경 분리

| 환경 | 브랜치 | URL | 용도 |
|------|--------|-----|------|
| Production | `main` | valuation.ai.kr | 실서비스 |
| Staging | `develop` | staging.valuation.ai.kr | 통합 테스트 |
| Preview | PR | pr-123.valuation.ai.kr | PR 미리보기 |
| Local | `task/*` | localhost:3000 | 개발 |

### 환경 변수 관리

| 환경 | 파일 | 관리 방법 |
|------|------|----------|
| Local | `.env.local` | Git에서 제외 (`.gitignore`) |
| Staging | Vercel 환경 변수 | Dashboard에서 설정 |
| Production | Vercel 환경 변수 | Dashboard에서 설정 |

**`.env.local.example`**:
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# External
RESEND_API_KEY=your-resend-key
```

---

## Hotfix 프로세스

긴급 수정이 필요한 경우:

```bash
# 1. main에서 hotfix 브랜치 생성
git checkout main
git pull origin main
git checkout -b hotfix/issue-42-login-error

# 2. 수정 및 커밋
# ... 수정 작업 ...
git commit -m "fix(hotfix): 로그인 에러 수정

Issue #42: 이메일 형식 검증 오류 수정"

# 3. main에 merge
git checkout main
git merge --no-ff hotfix/issue-42-login-error
git push origin main

# 4. develop에도 merge (중요!)
git checkout develop
git merge --no-ff hotfix/issue-42-login-error
git push origin develop

# 5. hotfix 브랜치 삭제
git branch -d hotfix/issue-42-login-error
git push origin --delete hotfix/issue-42-login-error
```

---

## 배포 프로세스

### 1. Develop → Staging (자동)

`develop` 브랜치에 push 시 Vercel이 자동으로 Staging 환경에 배포합니다.

```
git push origin develop
→ Vercel 자동 배포
→ https://staging.valuation.ai.kr
```

### 2. Main → Production (반자동)

```bash
# 1. Release 준비
git checkout main
git pull origin main

# 2. develop merge
git merge --no-ff develop

# 3. 버전 태그
git tag -a v1.0.0 -m "Release v1.0.0

- S1 Stage 완료
- S2 Stage 완료
- 인증 시스템 구현
- 평가 요청 API 구현"

# 4. Push
git push origin main --tags

# → Vercel 자동 배포
# → https://valuation.ai.kr
```

### 3. 버전 규칙 (Semantic Versioning)

**형식**: `v{MAJOR}.{MINOR}.{PATCH}`

| 버전 | 변경 시기 |
|------|----------|
| MAJOR | 호환되지 않는 API 변경 |
| MINOR | 새로운 기능 추가 (하위 호환) |
| PATCH | 버그 수정 |

**예시**:
- `v1.0.0`: 첫 릴리스
- `v1.1.0`: 새 기능 추가
- `v1.1.1`: 버그 수정
- `v2.0.0`: Breaking change

---

## Rollback 절차

### 1. 이전 버전으로 롤백

```bash
# 마지막 릴리스 태그 확인
git tag --list

# 이전 버전으로 체크아웃
git checkout v0.9.0

# main에 강제 push (주의!)
git push origin HEAD:main --force

# Vercel이 자동으로 이전 버전 배포
```

### 2. Vercel Instant Rollback

Vercel Dashboard에서 이전 배포를 클릭하고 "Promote to Production" 선택

---

## Pre-commit Hooks

### Husky 설정

**설치**:
```bash
npm install husky lint-staged -D
npx husky init
```

**`.husky/pre-commit`**:
```bash
#!/bin/sh
npx lint-staged
```

**`package.json`**:
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

---

## 유용한 Git 명령어

### 자주 사용하는 명령어

```bash
# 상태 확인
git status
git log --oneline -10

# 브랜치 관리
git branch -a
git checkout -b task/S2F1-new-feature
git branch -d task/S2F1-old-feature

# 원격 동기화
git fetch origin
git pull origin develop
git push origin task/S2F1-feature

# Stash (임시 저장)
git stash
git stash pop
git stash list

# 커밋 수정
git commit --amend
git rebase -i HEAD~3  # 마지막 3개 커밋 수정
```

### GitHub CLI (gh)

```bash
# PR 생성
gh pr create --title "feat(S2F1): 기능 구현" --body "설명"

# PR 목록
gh pr list

# PR 체크아웃
gh pr checkout 123

# Issue 생성
gh issue create --title "버그: 로그인 오류" --body "설명"
```

---

## 체크리스트

### 작업 시작 전
- [ ] `develop` 브랜치 최신화
- [ ] Task Instruction 확인
- [ ] 의존성 Task 완료 확인

### 작업 완료 후
- [ ] TypeScript 컴파일 성공
- [ ] ESLint 경고 0개
- [ ] 로컬 테스트 통과
- [ ] Commit 메시지 규칙 준수
- [ ] PR 생성 및 템플릿 작성

### Merge 전
- [ ] CI 통과
- [ ] Code Review 승인
- [ ] 충돌 해결

---

## 버전 정보

- **문서 버전**: v1.0
- **Last Updated**: 2026-02-07

---

**작성일**: 2026-02-07
**작성자**: Claude Code
