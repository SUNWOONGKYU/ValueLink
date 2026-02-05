# S1BI1 Verification

## 검증 대상

- **Task ID**: S1BI1
- **Task Name**: 데이터베이스 및 설정 인프라 구축
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: BI (Backend Infrastructure)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 0. Next.js 프로젝트 초기화 검증 (최우선) ⭐

#### 0.1 프로젝트 생성 확인

- [ ] **루트 디렉토리에 `package.json` 파일 존재**
  - 명령어: `ls package.json`
  - 필수 필드 확인: `name`, `version`, `scripts` (dev, build, start, lint)

- [ ] **루트 디렉토리에 `next.config.js` 파일 존재**
  - 명령어: `ls next.config.js`
  - `images.domains` 설정 확인

- [ ] **루트 디렉토리에 `tsconfig.json` 파일 존재**
  - 명령어: `ls tsconfig.json`
  - `paths` 설정 확인: `"@/*": ["./*"]`

- [ ] **`app/` 폴더 존재 및 필수 파일 확인**
  - 명령어: `ls app/layout.tsx app/page.tsx app/globals.css`
  - 3개 파일 모두 존재해야 함

- [ ] **`public/` 폴더 존재**
  - 명령어: `ls -d public/`

#### 0.2 필수 폴더 생성 확인

- [ ] **`lib/` 폴더 및 하위 폴더 존재**
  - 명령어: `ls -d lib/supabase lib/ai lib/email lib/utils`
  - 4개 폴더 모두 존재해야 함

- [ ] **`components/` 폴더 및 하위 폴더 존재**
  - 명령어: `ls -d components/ui components/features`
  - 2개 폴더 모두 존재해야 함

- [ ] **`types/` 폴더 존재**
  - 명령어: `ls -d types/`

- [ ] **`hooks/` 폴더 존재**
  - 명령어: `ls -d hooks/`

#### 0.3 Vercel 배포 준비 확인

- [ ] **`.gitignore` 파일에 환경 변수 제외 확인**
  - 명령어: `grep ".env" .gitignore`
  - `.env*.local`, `.env` 포함되어야 함

---

### 1. 빌드 & 컴파일 (최우선)

#### 1.1 TypeScript 빌드 성공

- [ ] **TypeScript 타입 체킹 성공**
  - 명령어: `npm run type-check` (또는 `tsc --noEmit`)
  - 출력: `0 errors` 또는 에러 없이 완료

#### 1.2 Next.js 빌드 성공

- [ ] **Next.js 프로젝트 빌드 성공**
  - 명령어: `npm run build`
  - 출력: `✓ Compiled successfully` 및 빌드 완료 메시지
  - `.next/` 폴더 생성 확인

#### 1.3 ESLint 경고 0개

- [ ] **ESLint 검사 통과**
  - 명령어: `npm run lint`
  - 출력: `✔ No ESLint warnings or errors` 또는 에러 없이 완료

#### 1.4 개발 서버 실행 가능

- [ ] **개발 서버 실행 가능**
  - 명령어: `npm run dev`
  - 출력: `- Local: http://localhost:3000`
  - 브라우저에서 `http://localhost:3000` 접속 시 페이지 표시

---

### 2. 파일 생성 확인

#### 2.1 Supabase 클라이언트 파일

- [ ] **`lib/supabase/client.ts` 존재 및 내용 확인**
  - 파일 존재: `ls lib/supabase/client.ts`
  - `createBrowserClient` import 확인
  - `createClient()` 함수 export 확인

- [ ] **`lib/supabase/server.ts` 존재 및 내용 확인**
  - 파일 존재: `ls lib/supabase/server.ts`
  - `createServerClient` import 확인
  - 쿠키 처리 로직 (get, set, remove) 확인

- [ ] **`lib/supabase/middleware.ts` 존재 및 내용 확인**
  - 파일 존재: `ls lib/supabase/middleware.ts`
  - `updateSession()` 함수 export 확인
  - `supabase.auth.getUser()` 호출 확인

#### 2.2 환경 설정 파일

- [ ] **`lib/config.ts` 존재 및 내용 확인**
  - 파일 존재: `ls lib/config.ts`
  - `config` 객체 export 확인
  - `validateConfig()` 함수 확인

- [ ] **`.env.local.example` 존재 및 내용 확인**
  - 파일 존재: `ls .env.local.example`
  - 필수 환경 변수 나열 확인:
    - `NEXT_PUBLIC_SUPABASE_URL`
    - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
    - AI API Keys (ANTHROPIC, GOOGLE_AI, OPENAI)
    - `RESEND_API_KEY`

#### 2.3 Middleware 파일

- [ ] **`middleware.ts` 존재 (프로젝트 루트)**
  - 파일 존재: `ls middleware.ts`
  - `updateSession` import 확인
  - `config.matcher` 설정 확인 (정적 파일 제외)

#### 2.4 타입 정의 파일

- [ ] **`types/database.types.ts` 존재 (빈 파일 가능)**
  - 파일 존재: `ls types/database.types.ts`
  - S1D1에서 채워질 예정이므로 빈 파일 허용

---

### 3. 핵심 기능 테스트

#### 3.1 Supabase 클라이언트 import 가능

- [ ] **브라우저 클라이언트 import 테스트**
  - 테스트 코드 작성:
    ```typescript
    import { createClient } from '@/lib/supabase/client'
    const supabase = createClient()
    ```
  - TypeScript 에러 없음 확인

- [ ] **서버 클라이언트 import 테스트**
  - 테스트 코드 작성:
    ```typescript
    import { createClient } from '@/lib/supabase/server'
    const supabase = createClient()
    ```
  - TypeScript 에러 없음 확인

#### 3.2 환경 변수 검증 함수 작동

- [ ] **`validateConfig()` 함수 테스트**
  - `.env.local` 파일 생성 (필수 환경 변수 포함)
  - `validateConfig()` 호출 시 에러 없음 확인
  - 필수 환경 변수 누락 시 에러 발생 확인

#### 3.3 Middleware 정상 실행

- [ ] **Middleware 로직 테스트**
  - 개발 서버 실행 후 페이지 접속
  - 콘솔 에러 없음 확인
  - 쿠키 설정/갱신 정상 작동 확인 (개발자 도구)

---

### 4. 통합 테스트

#### 4.1 선행 Task와 호환

- [ ] **S1BI1은 선행 Task 없음 (Dependencies: 없음)**
  - 독립적으로 완료 가능

#### 4.2 후행 Task 준비 완료

- [ ] **S1D1 (Database Schema) 준비**
  - `types/database.types.ts` 파일 존재 (S1D1에서 타입 생성할 위치)

- [ ] **S2BA1 (Valuation Process API) 준비**
  - Supabase 클라이언트 사용 가능 (import 가능)

- [ ] **S2F7 (Authentication Pages) 준비**
  - Supabase 클라이언트 사용 가능

---

### 5. Blocker 확인

#### 5.1 의존성 차단

- [ ] **Node.js 버전 확인**
  - 명령어: `node -v`
  - 권장 버전: v20.x 이상

- [ ] **npm 패키지 설치 완료**
  - 명령어: `ls node_modules/`
  - `@supabase/supabase-js`, `@supabase/ssr` 폴더 존재 확인

- [ ] **외부 의존성 없음**
  - S1BI1은 다른 Task에 의존하지 않음

#### 5.2 환경 차단

- [ ] **환경 변수 설정 가이드 제공**
  - `.env.local.example` 파일 존재
  - README 또는 문서에 설정 방법 안내

- [ ] **Supabase 프로젝트 생성 필요 (알림)**
  - 실제 환경 변수 값은 Supabase 대시보드에서 가져와야 함
  - 이 단계에서는 파일 구조만 검증, 실제 연결은 S1D1 이후

#### 5.3 외부 API 차단

- [ ] **외부 API 호출 없음**
  - S1BI1은 파일 구조 생성 및 설정만 수행
  - 실제 Supabase 연결은 환경 변수 설정 후 테스트

---

### 6. Vercel 배포 준비 검증

#### 6.1 Vercel 로컬 테스트

- [ ] **Vercel CLI 로컬 테스트 (선택 사항)**
  - 명령어: `npx vercel dev`
  - 실행 가능 여부 확인
  - 에러 없이 로컬 서버 시작 확인

#### 6.2 Production 빌드 확인

- [ ] **Production 빌드 성공**
  - 명령어: `npm run build`
  - 빌드 결과물 생성 확인 (`.next/` 폴더)
  - 빌드 시간 및 경고 확인

---

## 합격 기준

### 필수 (Must Pass)

1. **Next.js 프로젝트 초기화 완료** ✅
   - 루트 디렉토리에 `package.json`, `next.config.js`, `tsconfig.json` 존재
   - `app/` 폴더 및 필수 파일 존재

2. **TypeScript 빌드 성공** ✅
   - `npm run type-check` 에러 없음

3. **Next.js 빌드 성공** ✅
   - `npm run build` 성공

4. **ESLint 경고 0개** ✅
   - `npm run lint` 에러/경고 없음

5. **필수 파일 생성 완료** ✅
   - Supabase 클라이언트 3개 파일 (`client.ts`, `server.ts`, `middleware.ts`)
   - 환경 설정 파일 (`config.ts`, `.env.local.example`)
   - Middleware 파일 (`middleware.ts`)

6. **개발 서버 실행 가능** ✅
   - `npm run dev` 실행 후 `localhost:3000` 접속 가능

### 권장 (Nice to Pass)

1. **Vercel 로컬 테스트 성공** ✨
   - `npx vercel dev` 실행 가능

2. **환경 변수 검증 함수 작동** ✨
   - `validateConfig()` 정상 작동

3. **JSDoc 주석 포함** ✨
   - 주요 함수에 JSDoc 주석 추가

---

## 검증 결과

### Pass/Fail

**Status**: [ ] Pass / [ ] Fail

**검증일**: _______________

**검증자**: _______________

### 발견 사항

#### 🟢 통과 항목

- (통과한 항목 나열)

#### 🔴 실패 항목

- (실패한 항목 나열 및 수정 필요 사항)

#### 🟡 경고 사항

- (경고 또는 개선 권장 사항)

---

## 주의사항

1. **Next.js 프로젝트 초기화가 최우선**
   - 모든 검증 전에 루트 디렉토리 구조 확인 필수
   - `package.json`, `next.config.js`, `app/` 폴더가 없으면 즉시 실패 처리

2. **빌드 성공이 가장 중요**
   - TypeScript 에러 1개라도 있으면 실패
   - Next.js 빌드 실패 시 즉시 실패 처리

3. **환경 변수 실제 값은 불필요**
   - `.env.local.example` 파일만 있으면 충분
   - 실제 Supabase URL/KEY는 배포 시 설정

4. **파일 구조 검증 중심**
   - 실제 Supabase 연결 테스트는 S1D1 이후
   - 이 단계에서는 파일 존재 및 코드 구조만 검증

5. **Vercel 배포 준비**
   - 루트 디렉토리 구조가 Vercel 요구사항 충족하는지 확인
   - `vercel.json`은 선택 사항 (없어도 자동 감지)

---

## 참조

- Task Instruction: `task-instructions/S1BI1_instruction.md`
- Next.js 공식 문서: https://nextjs.org/docs
- Supabase SSR 가이드: https://supabase.com/docs/guides/auth/server-side/nextjs
- Vercel 배포 가이드: https://vercel.com/docs/deployments/overview

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
