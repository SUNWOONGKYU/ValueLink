# S1BI1: Database & Configuration Infrastructure

## Task 정보

- **Task ID**: S1BI1
- **Task Name**: 데이터베이스 및 설정 인프라 구축
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: BI (Backend Infrastructure)
- **Dependencies**: 없음
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

Next.js 프로젝트 초기화 및 Supabase 클라이언트 설정, 환경 변수 관리 인프라 구축, Vercel 배포 준비

---

## 상세 지시사항

### 0. Next.js 프로젝트 초기화 (최우선)

#### 0.1 프로젝트 생성

```bash
npx create-next-app@latest valuelink --typescript --tailwind --app --src-dir=false --import-alias="@/*"
cd valuelink
```

**선택 옵션**:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ `src/` directory: No (루트에 app/ 폴더)
- ✅ App Router
- ✅ Import alias: `@/*`
- ❌ Turbopack: No (안정성 우선)

#### 0.2 루트 디렉토리 구조 확인

생성 후 다음 구조여야 함:

```
valuelink/
├── app/                     # App Router 페이지
│   ├── layout.tsx          # 루트 레이아웃
│   ├── page.tsx            # 홈 페이지
│   └── globals.css         # 글로벌 스타일
├── public/                 # 정적 파일
│   └── favicon.ico
├── lib/                    # (생성 필요) 유틸리티, 클라이언트
├── components/             # (생성 필요) 재사용 컴포넌트
├── types/                  # (생성 필요) 타입 정의
├── .eslintrc.json         # ESLint 설정
├── .gitignore             # Git 제외 파일
├── next.config.js         # Next.js 설정
├── package.json           # 패키지 정보
├── tailwind.config.ts     # Tailwind 설정
├── tsconfig.json          # TypeScript 설정
├── postcss.config.js      # PostCSS 설정
└── README.md              # 프로젝트 설명
```

#### 0.3 필수 폴더 생성

```bash
mkdir -p lib/supabase
mkdir -p lib/ai
mkdir -p lib/email
mkdir -p lib/utils
mkdir -p components/ui
mkdir -p components/features
mkdir -p types
mkdir -p hooks
```

#### 0.4 next.config.js 수정

**파일**: `next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      'lh3.googleusercontent.com', // Google OAuth 프로필 이미지
      // Supabase Storage 도메인 (프로젝트 생성 후 추가)
    ],
  },
  experimental: {
    serverActions: {
      bodySizeLimit: '10mb', // 파일 업로드 제한
    },
  },
}

module.exports = nextConfig
```

#### 0.5 tsconfig.json 확인

**파일**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

#### 0.6 .gitignore 확인

**파일**: `.gitignore`

```
# dependencies
/node_modules

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local
.env

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts
```

#### 0.7 package.json scripts 확인

**파일**: `package.json`

```json
{
  "name": "valuelink",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.4.20",
    "eslint": "^8",
    "eslint-config-next": "14.2.0",
    "postcss": "^8",
    "tailwindcss": "^3.4.1",
    "typescript": "^5"
  }
}
```

#### 0.8 Vercel 배포를 위한 필수 파일 확인

**✅ Vercel이 자동 감지하는 파일**:
- `package.json` (필수 - build script 포함)
- `next.config.js` (필수 - Next.js 설정)
- `app/` 폴더 (필수 - App Router)
- `public/` 폴더 (정적 파일)

**🔧 Vercel 설정 파일 (선택)**:

**파일**: `vercel.json` (선택 사항)

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["icn1"]
}
```

**⚠️ 중요**: `vercel.json`이 없어도 Vercel이 자동으로 Next.js를 감지하고 배포합니다.

---

### 1. Supabase 클라이언트 설정

#### 1.1 브라우저용 클라이언트 생성

**파일**: `lib/supabase/client.ts`

```typescript
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**용도**: Client Component에서 사용

#### 1.2 서버용 클라이언트 생성

**파일**: `lib/supabase/server.ts`

```typescript
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value, ...options })
          } catch (error) {
            // Server Component에서는 쿠키 설정 불가 (무시)
          }
        },
        remove(name: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value: '', ...options })
          } catch (error) {
            // Server Component에서는 쿠키 삭제 불가 (무시)
          }
        },
      },
    }
  )
}
```

**용도**: Server Component, Server Actions, Route Handlers에서 사용

#### 1.3 Middleware용 클라이언트 생성

**파일**: `lib/supabase/middleware.ts`

```typescript
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({
            name,
            value,
            ...options,
          })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({
            name,
            value,
            ...options,
          })
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({
            name,
            value: '',
            ...options,
          })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({
            name,
            value: '',
            ...options,
          })
        },
      },
    }
  )

  await supabase.auth.getUser()

  return response
}
```

**용도**: Middleware에서 인증 세션 갱신

### 2. 환경 설정 파일

#### 2.1 환경 변수 템플릿

**파일**: `.env.local.example`

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# AI Services
ANTHROPIC_API_KEY=your-claude-api-key
GOOGLE_AI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Email Service
RESEND_API_KEY=your-resend-api-key

# Application
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

#### 2.2 중앙 설정 관리

**파일**: `lib/config.ts`

```typescript
export const config = {
  supabase: {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL!,
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  },
  ai: {
    anthropic: {
      apiKey: process.env.ANTHROPIC_API_KEY,
      model: 'claude-sonnet-3.5',
    },
    google: {
      apiKey: process.env.GOOGLE_AI_API_KEY,
      model: 'gemini-pro-1.5',
    },
    openai: {
      apiKey: process.env.OPENAI_API_KEY,
      model: 'gpt-4',
    },
  },
  email: {
    apiKey: process.env.RESEND_API_KEY,
    from: 'ValueLink <noreply@valuation.ai.kr>',
  },
  app: {
    url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
    name: 'ValueLink',
  },
} as const

// 환경 변수 검증
export function validateConfig() {
  const required = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
  ]

  const missing = required.filter((key) => !process.env[key])

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}`
    )
  }
}
```

### 3. Middleware 설정

**파일**: `middleware.ts` (프로젝트 루트)

```typescript
import { updateSession } from '@/lib/supabase/middleware'

export async function middleware(request: NextRequest) {
  return await updateSession(request)
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

### 4. TypeScript 타입 정의

**파일**: `types/database.types.ts` (S1D1에서 자동 생성될 파일 위치 지정)

```typescript
// Supabase CLI로 생성될 타입 정의
// npx supabase gen types typescript --project-id [project-id] > types/database.types.ts

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

// S1D1에서 생성될 스키마 타입
```

### 5. 패키지 설치

**필수 패키지**:

```bash
npm install @supabase/supabase-js @supabase/ssr
npm install -D @supabase/cli
```

---

## 생성/수정 파일

### 0. Next.js 프로젝트 초기화 (자동 생성)

| 파일 | 변경 내용 | 생성 방법 |
|------|----------|----------|
| `package.json` | 패키지 정보 | create-next-app |
| `next.config.js` | Next.js 설정 (수정 필요) | create-next-app |
| `tsconfig.json` | TypeScript 설정 | create-next-app |
| `.gitignore` | Git 제외 파일 | create-next-app |
| `.eslintrc.json` | ESLint 설정 | create-next-app |
| `tailwind.config.ts` | Tailwind 설정 | create-next-app |
| `postcss.config.js` | PostCSS 설정 | create-next-app |
| `app/layout.tsx` | 루트 레이아웃 | create-next-app |
| `app/page.tsx` | 홈 페이지 | create-next-app |
| `app/globals.css` | 글로벌 스타일 | create-next-app |
| `public/favicon.ico` | 파비콘 | create-next-app |

### 1. Supabase 클라이언트 (수동 생성)

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/supabase/client.ts` | 브라우저용 Supabase 클라이언트 | ~10줄 |
| `lib/supabase/server.ts` | 서버용 Supabase 클라이언트 | ~40줄 |
| `lib/supabase/middleware.ts` | Middleware용 세션 갱신 | ~60줄 |

### 2. 환경 설정 (수동 생성)

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/config.ts` | 환경 설정 중앙 관리 | ~50줄 |
| `.env.local.example` | 환경 변수 템플릿 | ~15줄 |
| `middleware.ts` | Next.js Middleware | ~20줄 |
| `types/database.types.ts` | 타입 정의 (빈 파일, S1D1에서 채움) | ~0줄 |

### 3. Vercel 배포 설정 (선택)

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `vercel.json` | Vercel 설정 (선택 사항) | ~7줄 |

**총 파일 수**:
- 자동 생성: 11개
- 수동 생성: 7개
- 선택 사항: 1개
- **합계**: 19개

**총 라인 수**: ~195줄 (수동 생성) + 자동 생성 파일

---

## 기술 스택

- **Language**: TypeScript 5.x
- **Framework**: Next.js 14 (App Router)
- **Database Client**: @supabase/supabase-js ^2.39.0
- **SSR Support**: @supabase/ssr ^0.1.0

---

## 완료 기준

### 0. Next.js 프로젝트 초기화 (최우선)
- [ ] `npx create-next-app@latest` 실행 완료
- [ ] 루트 디렉토리에 `package.json` 존재
- [ ] 루트 디렉토리에 `next.config.js` 존재
- [ ] 루트 디렉토리에 `tsconfig.json` 존재
- [ ] `app/layout.tsx`, `app/page.tsx` 존재
- [ ] `npm run dev` 실행 가능 (localhost:3000)
- [ ] `npm run build` 성공
- [ ] 필수 폴더 생성 완료 (lib/, components/, types/, hooks/)

### 1. Supabase 클라이언트 설정
- [ ] `lib/supabase/client.ts` 파일 생성 완료
- [ ] `lib/supabase/server.ts` 파일 생성 완료
- [ ] `lib/supabase/middleware.ts` 파일 생성 완료
- [ ] `lib/config.ts` 파일 생성 완료
- [ ] `.env.local.example` 파일 생성 완료
- [ ] `middleware.ts` 파일 생성 완료
- [ ] TypeScript 컴파일 에러 없음
- [ ] ESLint 경고 0개

### 2. Vercel 배포 준비
- [ ] `vercel.json` 생성 (선택 사항)
- [ ] `.gitignore`에 `.env*.local` 포함 확인
- [ ] `package.json`에 `build` script 존재
- [ ] Git 저장소 초기화 완료

### 검증 (Verification)
- [ ] 브라우저 클라이언트 import 가능
- [ ] 서버 클라이언트 import 가능
- [ ] 환경 변수 검증 함수 작동
- [ ] Middleware 정상 실행
- [ ] **Vercel 로컬 테스트**: `npx vercel dev` 실행 가능

### 권장 (Nice to Have)
- [ ] JSDoc 주석 추가
- [ ] 에러 처리 로직 추가
- [ ] 타입 안전성 검증

---

## 참조

### Supabase 공식 문서
- Next.js App Router: https://supabase.com/docs/guides/auth/server-side/nextjs
- SSR 패키지: https://supabase.com/docs/guides/auth/server-side/creating-a-client

### 기존 프로토타입
- `Valuation_Company/valuation-platform/frontend/assets/js/supabase.js` (Vanilla JS 버전, 참고용)

### 관련 Task
- **S1D1**: Database Schema & RLS Policies (데이터베이스 타입 생성)
- **S2F7**: Authentication & Landing Pages (인증 페이지에서 사용)
- **S2BA1**: Valuation Process API (API에서 사용)

---

## 주의사항

1. **Next.js 프로젝트 초기화 최우선**
   - **반드시 프로젝트 초기화부터 시작**
   - `create-next-app` 완료 후 Supabase 설정 진행
   - 루트 디렉토리에 필수 파일들이 있어야 Vercel 배포 가능

2. **Vercel 배포 필수 조건**
   - ✅ `package.json` (build script 포함)
   - ✅ `next.config.js` (Next.js 설정)
   - ✅ `app/` 폴더 (App Router)
   - ✅ TypeScript 컴파일 성공
   - `vercel.json`은 선택 사항 (없어도 자동 감지)

3. **환경 변수 보안**
   - `.env.local`은 절대 Git에 커밋하지 않음 (`.gitignore`에 포함)
   - `.env.local.example`만 커밋
   - Vercel 대시보드에서 환경 변수 설정 필요

4. **Cookie 설정 에러 처리**
   - Server Component에서는 쿠키 설정 불가
   - `try-catch`로 에러 무시 처리 필수

5. **Middleware 성능**
   - 모든 요청에서 실행되므로 가벼워야 함
   - `getUser()` 호출만으로 세션 갱신

6. **타입 안전성**
   - `process.env.*!` 사용 시 undefined 확인 필수
   - `validateConfig()` 함수로 시작 시 검증

7. **Import Alias**
   - `@/*` alias 사용 (tsconfig.json에 설정됨)
   - 예: `import { Button } from '@/components/ui/button'`

---

## 예상 소요 시간

**작업 복잡도**: Medium (Next.js 초기화 + Supabase 설정)
**파일 수**: 19개 (자동 11개 + 수동 7개 + 선택 1개)
**라인 수**: ~195줄 (수동 생성)

**단계별 소요 시간**:
- Next.js 프로젝트 초기화: 10분
- Supabase 클라이언트 설정: 20분
- 환경 설정 파일 작성: 15분
- 테스트 및 검증: 15분
- **총 예상 시간**: 60분

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
