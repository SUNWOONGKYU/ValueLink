# S1M2: Development Workflow Guide

## Task 정보

- **Task ID**: S1M2
- **Task Name**: 개발 워크플로우 가이드 작성
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: M (Documentation)
- **Dependencies**: 없음
- **Task Agent**: documentation-specialist
- **Verification Agent**: code-reviewer

---

## Task 목표

Git 전략, 브랜치 규칙, 코딩 표준, 리뷰 프로세스를 문서화하여 일관된 개발 워크플로우 확립

---

## 상세 지시사항

### 1. 개발 워크플로우 가이드

**파일**: `docs/development-guide.md`

#### 구조
```markdown
# Development Workflow Guide

## Git 전략

### 브랜치 전략 (Git Flow 변형)

```
main (프로덕션)
  ↑
develop (개발 통합)
  ↑
feature/* (기능 개발)
hotfix/* (긴급 수정)
```

---

## 브랜치 명명 규칙

### Feature 브랜치

**형식**: `task/{TaskID}-{간단한-설명}`

**예시**:
- `task/S2F1-valuation-results-pages`
- `task/S3BA3-dcf-engine`

### Hotfix 브랜치

**형식**: `hotfix/{issue-번호}-{간단한-설명}`

**예시**:
- `hotfix/issue-42-login-error`

---

## Commit 메시지 규칙

### Conventional Commits 사용

**형식**: `<type>(<TaskID>): <subject>`

**Types**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**예시**:
```
feat(S2F1): 평가 결과 페이지 템플릿 구현

- 공통 템플릿 컴포넌트 생성
- 5개 평가 방법별 페이지 구현
- Recharts 그래프 통합

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**나쁜 예시**:
```
❌ update files
❌ fixed bug
❌ WIP
```

---

## Pull Request 프로세스

### 1. Feature 브랜치 생성

```bash
git checkout develop
git pull origin develop
git checkout -b task/S2F1-valuation-results-pages
```

### 2. 작업 및 커밋

```bash
# 작업 수행
git add .
git commit -m "feat(S2F1): 평가 결과 페이지 템플릿 구현"
```

### 3. Push 및 PR 생성

```bash
git push origin task/S2F1-valuation-results-pages

# GitHub에서 PR 생성
```

### 4. PR 템플릿

```markdown
## Task 정보
- Task ID: S2F1
- Task Name: 평가 결과 페이지 템플릿 및 5개 방법별 페이지

## 변경 사항
- [ ] 공통 템플릿 컴포넌트 생성
- [ ] DCF 결과 페이지 구현
- [ ] Relative 결과 페이지 구현
- [ ] Asset 결과 페이지 구현
- [ ] Intrinsic 결과 페이지 구현
- [ ] Tax 결과 페이지 구현

## 테스트
- [ ] TypeScript 컴파일 성공
- [ ] ESLint 경고 0개
- [ ] 수동 테스트 완료

## 스크린샷
(UI 변경 시 스크린샷 첨부)

## 관련 Task
- Depends on: S1BI1, S1D1
- Blocks: S2F2

## 검토 요청사항
- 템플릿 컴포넌트 재사용성 검토 필요
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
```
✅ LGTM (Looks Good To Me)
💬 Question: 왜 이 방식을 선택했나요?
💡 Suggestion: 이렇게 개선하면 어떨까요?
⚠️ Issue: 이 부분은 버그가 있습니다.
🔒 Security: SQL Injection 취약점이 있습니다.
```

### 6. Merge

```bash
# PR 승인 후
git checkout develop
git merge --no-ff task/S2F1-valuation-results-pages
git push origin develop

# Feature 브랜치 삭제
git branch -d task/S2F1-valuation-results-pages
git push origin --delete task/S2F1-valuation-results-pages
```

---

## CI/CD 파이프라인

### GitHub Actions Workflow

```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run type-check
      - run: npm run lint
      - run: npm run test
      - run: npm run build
```

---

## 환경 분리

| 환경 | 브랜치 | URL | 용도 |
|------|--------|-----|------|
| Production | main | valuation.ai.kr | 실서비스 |
| Staging | develop | staging.valuation.ai.kr | 통합 테스트 |
| Local | feature/* | localhost:3000 | 개발 |

---

## Hotfix 프로세스

```bash
# main에서 hotfix 브랜치 생성
git checkout main
git pull origin main
git checkout -b hotfix/issue-42-login-error

# 수정 및 커밋
git commit -m "fix(hotfix): 로그인 에러 수정

Issue #42: 이메일 형식 검증 오류 수정"

# main과 develop 모두에 merge
git checkout main
git merge --no-ff hotfix/issue-42-login-error
git push origin main

git checkout develop
git merge --no-ff hotfix/issue-42-login-error
git push origin develop

# hotfix 브랜치 삭제
git branch -d hotfix/issue-42-login-error
```

---

## 배포 프로세스

### 1. Develop → Staging 자동 배포

`develop` 브랜치에 push 시 Vercel이 자동으로 Staging 환경에 배포

### 2. Main → Production 배포

```bash
# Release PR 생성
git checkout main
git merge --no-ff develop
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags
```

Vercel이 자동으로 Production 환경에 배포

---

## Rollback 절차

```bash
# 이전 태그로 롤백
git checkout v0.9.0
git push origin HEAD:main --force

# Vercel이 자동으로 이전 버전 배포
```
```

---

### 2. 코딩 표준 가이드

**파일**: `docs/coding-standards.md`

#### 구조
```markdown
# Coding Standards

## TypeScript 코딩 표준

### 1. 명명 규칙

#### 변수/함수: camelCase
```typescript
const userName = 'John'
function getUserData() { }
```

#### 타입/인터페이스: PascalCase
```typescript
type User = { }
interface ProjectData { }
```

#### 상수: UPPER_SNAKE_CASE
```typescript
const MAX_RETRY_COUNT = 3
```

#### Private 멤버: _prefix
```typescript
class Service {
  private _internalCache: Map<string, any>
}
```

---

### 2. 파일 구조

```
src/
├── app/                  # Next.js App Router 페이지
├── components/           # 재사용 가능한 컴포넌트
│   ├── ui/              # 기본 UI 컴포넌트
│   └── features/        # 기능별 컴포넌트
├── lib/                 # 유틸리티, 클라이언트
│   ├── supabase/
│   ├── ai/
│   └── utils/
├── types/               # TypeScript 타입 정의
└── hooks/               # React Hooks
```

---

### 3. Import 순서

```typescript
// 1. React / Next.js
import React from 'react'
import { useRouter } from 'next/navigation'

// 2. 외부 라이브러리
import { createClient } from '@supabase/supabase-js'

// 3. 내부 모듈
import { Button } from '@/components/ui/button'
import { config } from '@/lib/config'

// 4. 타입
import type { User } from '@/types/database.types'

// 5. 스타일
import styles from './component.module.css'
```

---

### 4. 함수 작성 규칙

#### 함수는 한 가지 일만 수행

```typescript
// ✅ Good
function calculateTotalPrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

function applyDiscount(price: number, discount: number): number {
  return price * (1 - discount)
}

// ❌ Bad
function calculateFinalPrice(items: Item[], discount: number): number {
  const total = items.reduce((sum, item) => sum + item.price, 0)
  return total * (1 - discount)
}
```

#### 함수는 짧게 (20줄 이하 권장)

```typescript
// ✅ Good
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

// ❌ Bad (50줄짜리 함수)
```

#### 조기 반환 (Early Return)

```typescript
// ✅ Good
function processUser(user: User | null): string {
  if (!user) return 'No user'
  if (!user.email) return 'No email'

  return user.email
}

// ❌ Bad
function processUser(user: User | null): string {
  if (user) {
    if (user.email) {
      return user.email
    } else {
      return 'No email'
    }
  } else {
    return 'No user'
  }
}
```

---

### 5. 타입 안전성

#### any 사용 금지

```typescript
// ✅ Good
function parseJSON<T>(json: string): T {
  return JSON.parse(json) as T
}

// ❌ Bad
function parseJSON(json: string): any {
  return JSON.parse(json)
}
```

#### Optional Chaining 사용

```typescript
// ✅ Good
const userName = user?.profile?.name ?? 'Unknown'

// ❌ Bad
const userName = user && user.profile && user.profile.name ? user.profile.name : 'Unknown'
```

---

### 6. 에러 처리

#### Try-Catch 사용

```typescript
// ✅ Good
async function fetchUser(userId: string): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${userId}`)
    if (!response.ok) throw new Error('Failed to fetch')
    return await response.json()
  } catch (error) {
    console.error('Error fetching user:', error)
    return null
  }
}
```

#### 에러 타입 지정

```typescript
// ✅ Good
catch (error) {
  if (error instanceof Error) {
    console.error(error.message)
  } else {
    console.error('Unknown error')
  }
}

// ❌ Bad
catch (error) {
  console.error(error.message) // error가 Error 타입이 아닐 수 있음
}
```

---

### 7. React 컴포넌트

#### 함수형 컴포넌트 사용

```typescript
// ✅ Good
export function UserProfile({ user }: { user: User }) {
  return <div>{user.name}</div>
}

// ❌ Bad (클래스 컴포넌트)
export class UserProfile extends React.Component { }
```

#### Props 타입 정의

```typescript
// ✅ Good
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
}

export function Button({ label, onClick, variant = 'primary' }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>
}
```

---

### 8. 주석 작성

#### JSDoc 주석

```typescript
/**
 * 사용자 프로필을 가져옵니다.
 *
 * @param userId - 사용자 ID
 * @returns 사용자 프로필 또는 null
 * @throws {Error} API 호출 실패 시
 */
async function getUserProfile(userId: string): Promise<User | null> {
  // ...
}
```

#### TODO 주석

```typescript
// TODO(S3BA3): DCF 엔진 통합 후 실제 계산 로직으로 교체
const mockValue = 1000000
```

---

## ESLint 설정

### .eslintrc.json

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", {
      "argsIgnorePattern": "^_"
    }],
    "prefer-const": "error",
    "no-console": ["warn", {
      "allow": ["warn", "error"]
    }]
  }
}
```

---

## Prettier 설정

### .prettierrc

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80
}
```

---

## 테스트 작성 규칙

### 1. 테스트 파일 위치

```
src/
├── components/
│   └── button.tsx
│   └── button.test.tsx    # 같은 폴더
```

### 2. 테스트 작성

```typescript
import { render, screen } from '@testing-library/react'
import { Button } from './button'

describe('Button', () => {
  it('renders with label', () => {
    render(<Button label="Click me" onClick={() => {}} />)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = jest.fn()
    render(<Button label="Click me" onClick={onClick} />)

    screen.getByText('Click me').click()

    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
```
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `docs/development-guide.md` | Git 전략, PR 프로세스, CI/CD | ~500줄 |
| `docs/coding-standards.md` | TypeScript/React 코딩 표준 | ~400줄 |

**총 파일 수**: 2개
**총 라인 수**: ~900줄

---

## 기술 스택

- **Format**: Markdown
- **Tools**: 없음 (순수 문서 작성)

---

## 완료 기준

### 필수 (Must Have)
- [ ] development-guide.md 작성 완료
- [ ] coding-standards.md 작성 완료
- [ ] Git 전략 문서화
- [ ] Commit 메시지 규칙 정의
- [ ] PR 프로세스 문서화
- [ ] 코딩 표준 정의

### 검증 (Verification)
- [ ] Markdown 문법 검증
- [ ] 예시 코드 실행 가능
- [ ] 링크 정상 작동

### 권장 (Nice to Have)
- [ ] VS Code 설정 파일 추가
- [ ] Pre-commit Hook 스크립트
- [ ] Husky 설정

---

## 참조

### 관련 표준
- Conventional Commits: https://www.conventionalcommits.org/
- Git Flow: https://nvie.com/posts/a-successful-git-branching-model/
- TypeScript Style Guide: https://google.github.io/styleguide/tsguide.html

### 관련 Task
- **S2BA1**: Valuation Process API (API 구현 시 코딩 표준 적용)
- **S5O1**: Deployment Configuration & CI/CD (CI/CD 파이프라인 구현)

---

## 주의사항

1. **실제 프로세스 반영**
   - 팀의 실제 작업 방식에 맞게 조정
   - 문서와 실제 프로세스 일치 유지

2. **도구 설정 동기화**
   - ESLint, Prettier 설정 파일 실제 생성
   - VS Code 설정 공유

3. **지속적 업데이트**
   - 프로세스 변경 시 문서 업데이트
   - 팀원 피드백 반영

4. **접근성**
   - 신규 개발자도 이해 가능하도록 작성
   - 예시 코드 풍부하게 제공

---

## 예상 소요 시간

**작업 복잡도**: Low
**파일 수**: 2개
**라인 수**: ~900줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
