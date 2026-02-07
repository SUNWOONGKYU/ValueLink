# Coding Standards

## 개요

ValueLink 플랫폼 개발을 위한 TypeScript, React, Next.js 코딩 표준입니다.

---

## TypeScript 코딩 표준

### 1. 명명 규칙

#### 변수/함수: camelCase

```typescript
// ✅ Good
const userName = 'John'
const projectId = 'VL-2026-0001'
function getUserData() { }
function calculateValuation() { }

// ❌ Bad
const user_name = 'John'      // snake_case
const UserName = 'John'       // PascalCase
function GetUserData() { }    // PascalCase
```

#### 타입/인터페이스: PascalCase

```typescript
// ✅ Good
type User = {
  id: string
  email: string
}

interface ProjectData {
  projectId: string
  status: ProjectStatus
}

// ❌ Bad
type user = { }               // camelCase
interface project_data { }    // snake_case
```

#### 상수: UPPER_SNAKE_CASE

```typescript
// ✅ Good
const MAX_RETRY_COUNT = 3
const API_BASE_URL = 'https://api.valuation.ai.kr'
const VALUATION_METHODS = ['dcf', 'relative', 'asset', 'intrinsic', 'tax'] as const

// ❌ Bad
const maxRetryCount = 3       // camelCase
const MaxRetryCount = 3       // PascalCase
```

#### Enum: PascalCase (값도 PascalCase)

```typescript
// ✅ Good
enum ProjectStatus {
  Pending = 'pending',
  InProgress = 'in_progress',
  Completed = 'completed'
}

enum ValuationMethod {
  DCF = 'dcf',
  Relative = 'relative',
  Asset = 'asset'
}

// ❌ Bad
enum project_status { }       // snake_case
enum PROJECTSTATUS { }        // UPPERCASE
```

#### Boolean 변수: is/has/can 접두사

```typescript
// ✅ Good
const isLoading = true
const hasPermission = false
const canEdit = true
const shouldRefetch = false

// ❌ Bad
const loading = true          // 접두사 없음
const permission = false      // 명확하지 않음
```

---

### 2. 파일 구조

```
src/
├── app/                      # Next.js App Router 페이지
│   ├── (auth)/              # 인증 관련 그룹
│   ├── (dashboard)/         # 대시보드 그룹
│   ├── api/                 # API 라우트
│   └── layout.tsx           # 루트 레이아웃
├── components/              # 재사용 가능한 컴포넌트
│   ├── ui/                  # 기본 UI 컴포넌트 (Button, Card, etc.)
│   ├── forms/               # 폼 관련 컴포넌트
│   └── features/            # 기능별 컴포넌트
├── lib/                     # 유틸리티, 클라이언트
│   ├── supabase/           # Supabase 클라이언트
│   ├── ai/                 # AI 관련 유틸
│   └── utils/              # 공통 유틸리티
├── types/                   # TypeScript 타입 정의
│   ├── database.types.ts   # DB 타입 (Supabase 생성)
│   └── api.types.ts        # API 타입
├── hooks/                   # Custom React Hooks
│   ├── useAuth.ts
│   └── useProjects.ts
└── constants/               # 상수 정의
    ├── config.ts
    └── messages.ts
```

---

### 3. Import 순서

```typescript
// 1. React / Next.js (프레임워크)
import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

// 2. 외부 라이브러리 (알파벳 순)
import { createClient } from '@supabase/supabase-js'
import { motion } from 'framer-motion'
import { z } from 'zod'

// 3. 내부 모듈 (@ alias 사용)
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { config } from '@/lib/config'
import { formatCurrency } from '@/lib/utils'

// 4. 타입 (type 키워드 사용)
import type { User, Project } from '@/types/database.types'
import type { APIResponse } from '@/types/api.types'

// 5. 스타일 / 에셋
import styles from './component.module.css'
import Logo from '@/assets/logo.svg'
```

---

### 4. 함수 작성 규칙

#### 함수는 한 가지 일만 수행 (Single Responsibility)

```typescript
// ✅ Good - 각 함수가 한 가지 책임
function calculateTotalPrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

function applyDiscount(price: number, discountRate: number): number {
  return price * (1 - discountRate)
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW'
  }).format(price)
}

// ❌ Bad - 여러 책임을 한 함수에
function calculateAndFormatFinalPrice(
  items: Item[],
  discountRate: number,
  taxRate: number
): string {
  const total = items.reduce((sum, item) => sum + item.price, 0)
  const discounted = total * (1 - discountRate)
  const withTax = discounted * (1 + taxRate)
  return `${withTax.toLocaleString()}원`
}
```

#### 함수는 짧게 (20줄 이하 권장)

```typescript
// ✅ Good - 짧고 명확
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

function validatePassword(password: string): ValidationResult {
  if (password.length < 8) {
    return { valid: false, message: '8자 이상 입력해주세요' }
  }
  if (!/[A-Za-z]/.test(password)) {
    return { valid: false, message: '영문자를 포함해주세요' }
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: '숫자를 포함해주세요' }
  }
  return { valid: true }
}
```

#### 조기 반환 (Early Return)

```typescript
// ✅ Good - 조기 반환으로 중첩 최소화
async function getProject(projectId: string): Promise<Project | null> {
  if (!projectId) return null

  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .eq('project_id', projectId)
    .single()

  if (error) {
    console.error('Failed to fetch project:', error)
    return null
  }

  return data
}

// ❌ Bad - 깊은 중첩
async function getProject(projectId: string): Promise<Project | null> {
  if (projectId) {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('project_id', projectId)
      .single()

    if (!error) {
      return data
    } else {
      console.error('Failed to fetch project:', error)
      return null
    }
  } else {
    return null
  }
}
```

---

### 5. 타입 안전성

#### `any` 사용 금지

```typescript
// ✅ Good - 구체적인 타입 사용
function parseJSON<T>(json: string): T {
  return JSON.parse(json) as T
}

function processData(data: unknown): void {
  if (typeof data === 'string') {
    console.log(data.toUpperCase())
  }
}

// ❌ Bad - any 사용
function parseJSON(json: string): any {
  return JSON.parse(json)
}

function processData(data: any): void {
  console.log(data.someProperty)
}
```

#### Optional Chaining & Nullish Coalescing

```typescript
// ✅ Good
const userName = user?.profile?.name ?? 'Unknown'
const projectCount = stats?.projects?.length ?? 0

// ❌ Bad
const userName = user && user.profile && user.profile.name
  ? user.profile.name
  : 'Unknown'
```

#### 타입 가드 사용

```typescript
// ✅ Good - 타입 가드
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'email' in obj
  )
}

function processItem(item: User | Project) {
  if (isUser(item)) {
    console.log(item.email) // User 타입으로 추론
  } else {
    console.log(item.projectId) // Project 타입으로 추론
  }
}
```

---

### 6. 에러 처리

#### Try-Catch 사용

```typescript
// ✅ Good
async function fetchUser(userId: string): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${userId}`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error fetching user:', error.message)
    }
    return null
  }
}
```

#### 커스텀 에러 클래스

```typescript
// ✅ Good - 구체적인 에러 클래스
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public code: string
  ) {
    super(message)
    this.name = 'ValidationError'
  }
}

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public endpoint: string
  ) {
    super(message)
    this.name = 'APIError'
  }
}

// 사용
function validateForm(data: FormData) {
  if (!data.email) {
    throw new ValidationError('이메일을 입력해주세요', 'email', 'REQUIRED')
  }
}
```

---

## React 컴포넌트 표준

### 1. 함수형 컴포넌트 사용

```typescript
// ✅ Good - 함수형 컴포넌트
export function UserProfile({ user }: { user: User }) {
  return (
    <div className="profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}

// ❌ Bad - 클래스 컴포넌트 (사용 금지)
export class UserProfile extends React.Component<{ user: User }> {
  render() {
    return <div>{this.props.user.name}</div>
  }
}
```

### 2. Props 타입 정의

```typescript
// ✅ Good - 명확한 Props 타입
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  isLoading?: boolean
}

export function Button({
  label,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  isLoading = false
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`btn btn-${variant} btn-${size}`}
    >
      {isLoading ? 'Loading...' : label}
    </button>
  )
}
```

### 3. 컴포넌트 분리 기준

```typescript
// 컴포넌트가 너무 커지면 분리
// 기준: 100줄 이상, 여러 책임, 재사용 가능

// ✅ Good - 적절히 분리된 컴포넌트
// components/project/ProjectCard.tsx
export function ProjectCard({ project }: { project: Project }) {
  return (
    <Card>
      <ProjectHeader project={project} />
      <ProjectStatus status={project.status} />
      <ProjectActions projectId={project.id} />
    </Card>
  )
}

// components/project/ProjectHeader.tsx
export function ProjectHeader({ project }: { project: Project }) {
  return (
    <div>
      <h3>{project.name}</h3>
      <p>{project.description}</p>
    </div>
  )
}
```

### 4. Hooks 사용 규칙

```typescript
// ✅ Good - 커스텀 훅으로 로직 분리
function useProject(projectId: string) {
  const [project, setProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    async function fetchProject() {
      try {
        setIsLoading(true)
        const data = await getProject(projectId)
        setProject(data)
      } catch (e) {
        setError(e instanceof Error ? e : new Error('Unknown error'))
      } finally {
        setIsLoading(false)
      }
    }

    fetchProject()
  }, [projectId])

  return { project, isLoading, error }
}

// 컴포넌트에서 사용
function ProjectPage({ projectId }: { projectId: string }) {
  const { project, isLoading, error } = useProject(projectId)

  if (isLoading) return <Loading />
  if (error) return <Error message={error.message} />
  if (!project) return <NotFound />

  return <ProjectDetail project={project} />
}
```

---

## 주석 작성 규칙

### JSDoc 주석

```typescript
/**
 * 프로젝트의 기업가치를 계산합니다.
 *
 * @param projectId - 프로젝트 ID
 * @param method - 평가 방법 (dcf, relative, asset, intrinsic, tax)
 * @returns 계산된 기업가치 결과
 * @throws {ValidationError} 입력 데이터가 유효하지 않은 경우
 * @throws {APIError} API 호출 실패 시
 *
 * @example
 * const result = await calculateValuation('VL-2026-0001', 'dcf')
 * console.log(result.equityValue)
 */
async function calculateValuation(
  projectId: string,
  method: ValuationMethod
): Promise<ValuationResult> {
  // 구현
}
```

### TODO 주석

```typescript
// TODO(TaskID): 설명
// TODO(S3BA3): DCF 엔진 통합 후 실제 계산 로직으로 교체
const mockValue = 1000000

// FIXME(TaskID): 수정 필요한 부분
// FIXME(S2BA2): 동시성 이슈 해결 필요
await updateProject(projectId, data)

// NOTE: 중요한 설명
// NOTE: 이 함수는 서버 사이드에서만 호출해야 함
```

---

## ESLint 설정

**`.eslintrc.json`**:
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
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/no-empty-function": "warn",
    "prefer-const": "error",
    "no-console": ["warn", {
      "allow": ["warn", "error"]
    }],
    "react/prop-types": "off",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

---

## Prettier 설정

**`.prettierrc`**:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

---

## 테스트 작성 규칙

### 1. 테스트 파일 위치

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx     # 같은 폴더에 배치
├── lib/
│   ├── utils.ts
│   └── utils.test.ts
```

### 2. 테스트 작성 예시

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('renders with label', () => {
    render(<Button label="Click me" onClick={() => {}} />)

    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button label="Click me" onClick={handleClick} />)

    fireEvent.click(screen.getByText('Click me'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state', () => {
    render(<Button label="Submit" onClick={() => {}} isLoading />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('is disabled when loading', () => {
    render(<Button label="Submit" onClick={() => {}} isLoading />)

    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### 3. 테스트 명명 규칙

```typescript
describe('컴포넌트/함수 이름', () => {
  it('행동을 설명하는 문장', () => {
    // ...
  })

  describe('특정 조건에서', () => {
    it('기대하는 행동', () => {
      // ...
    })
  })
})

// 예시
describe('calculateDCF', () => {
  it('returns positive value for valid inputs', () => { })

  describe('with negative cash flows', () => {
    it('returns adjusted value', () => { })
  })

  describe('with zero WACC', () => {
    it('throws ValidationError', () => { })
  })
})
```

---

## API 라우트 작성 규칙

### Next.js App Router API

```typescript
// app/api/projects/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('user_id', user.id)

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      )
    }

    return NextResponse.json({ projects: data })
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## 금지 사항 체크리스트

- [ ] `any` 타입 사용 금지
- [ ] 클래스 컴포넌트 사용 금지
- [ ] `var` 사용 금지 (`const`, `let` 사용)
- [ ] `==` 사용 금지 (`===` 사용)
- [ ] `console.log` 프로덕션 코드에서 금지
- [ ] 하드코딩된 API 키 금지
- [ ] 주석 처리된 코드 커밋 금지
- [ ] 500줄 이상 파일 금지 (분리 필요)

---

## 버전 정보

- **문서 버전**: v1.0
- **Last Updated**: 2026-02-07

---

**작성일**: 2026-02-07
**작성자**: Claude Code
