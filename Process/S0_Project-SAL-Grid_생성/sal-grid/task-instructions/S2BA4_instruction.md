# S2BA4: AI Client & Email Services (마이그레이션)

## Task 정보

- **Task ID**: S2BA4
- **Task Name**: AI 클라이언트 및 이메일 서비스 마이그레이션
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (환경변수 설정)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**Valuation_Company의 Python AI/Email 서비스를 Next.js TypeScript로 마이그레이션하고 개선**

- 기존 Python 로직을 참고하여 TypeScript로 변환
- Claude/Gemini/GPT-4 AI 통합 클라이언트 및 이메일 발송 서비스(Resend)
- **4가지 측면에서 개선** (보안, 성능, 코드 품질, API 설계)

---

## 🎯 개선 필수 영역 (4가지)

### 1️⃣ 보안 강화 (Security)
- ✅ API 키 환경변수 관리 (하드코딩 금지)
- ✅ Rate limiting (AI API 호출 제한)
- ✅ 이메일 주소 검증
- ✅ AI 프롬프트 injection 방지
- ✅ 민감 정보 로깅 금지

### 2️⃣ 성능 최적화 (Performance)
- ✅ AI 응답 캐싱 (동일 요청)
- ✅ 재시도 로직 (네트워크 오류)
- ✅ 타임아웃 설정
- ✅ 이메일 비동기 발송 (큐 처리)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ 에러 핸들링 강화 (API 실패 시)
- ✅ JSDoc 주석으로 함수 문서화
- ✅ 테스트 가능한 구조 (클래스 기반)

### 4️⃣ API 설계 개선 (API Design)
- ✅ Provider별 인터페이스 통일
- ✅ 일관된 응답 형식
- ✅ 에러 코드 체계화
- ✅ 토큰 사용량 추적

---

## 작업 방식

### Step 1: 기존 Python 코드 분석

**읽어야 할 파일:**
```
Valuation_Company/valuation-platform/backend/
├── services/ai_client.py (AI 클라이언트)
├── services/email_sender.py (이메일 서비스)
├── services/notification_dispatcher.py (알림 디스패처)
└── config/ai_config.py (AI 설정)
```

**분석 항목:**
1. AI 3사 (Claude, Gemini, GPT) 호출 방식
2. 승인 포인트 검증 로직
3. 이메일 템플릿 구조
4. 알림 디스패처 흐름
5. 에러 처리 방식

### Step 2: Python → TypeScript 변환

**변환 가이드:**

| Python | TypeScript |
|--------|------------|
| `class AIClient:` | `export class AIClient {` |
| `def __init__(self, provider: str):` | `constructor(private provider: AIProvider) {}` |
| `response = requests.post(url, json=data)` | `const response = await fetch(url, { method: 'POST', body: JSON.stringify(data) })` |
| `return response.json()` | `return await response.json()` |
| `class EmailSender:` | `export class EmailSender {` |

**주의사항:**
- Python의 `requests` → TypeScript `fetch`
- Python의 클래스 초기화 → TypeScript constructor
- Python의 딕셔너리 → TypeScript 객체

### Step 3: 개선 사항 적용

**목업의 문제점 식별 및 개선:**

```typescript
// ❌ 목업: API 키 하드코딩
const ANTHROPIC_API_KEY = 'sk-ant-api...'

// ✅ 개선: 환경변수 사용 + 검증
if (!process.env.ANTHROPIC_API_KEY) {
  throw new Error('ANTHROPIC_API_KEY is not set in environment variables')
}

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
```

```typescript
// ❌ 목업: 재시도 로직 없음 (네트워크 오류 시 실패)
const response = await fetch(url, options)

// ✅ 개선: 재시도 로직 추가 (exponential backoff)
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options)

      if (!response.ok && response.status >= 500) {
        // 서버 에러는 재시도
        throw new Error(`HTTP ${response.status}`)
      }

      return response
    } catch (error) {
      lastError = error as Error
      const delay = Math.min(1000 * Math.pow(2, attempt), 10000) // 1s, 2s, 4s, 최대 10s
      await new Promise((resolve) => setTimeout(resolve, delay))
    }
  }

  throw new Error(`Failed after ${maxRetries} retries: ${lastError?.message}`)
}
```

```typescript
// ❌ 목업: 타임아웃 없음 (무한 대기 가능)
const response = await fetch(url, options)

// ✅ 개선: 타임아웃 설정 (30초)
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout = 30000
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })
    return response
  } finally {
    clearTimeout(timeoutId)
  }
}
```

```typescript
// ❌ 목업: AI 응답 캐싱 없음 (중복 호출)
const result = await this.chat(provider, messages)

// ✅ 개선: 간단한 메모리 캐싱
const cache = new Map<string, AIResponse>()

async chat(provider: AIProvider, messages: AIMessage[]): Promise<AIResponse> {
  const cacheKey = `${provider}:${JSON.stringify(messages)}`

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey)!
  }

  const result = await this.callProvider(provider, messages)
  cache.set(cacheKey, result)

  return result
}
```

### Step 4: Best Practice 적용

**Next.js 14 패턴:**
- lib/ 폴더에 서비스 클래스
- 환경변수 검증
- 에러 핸들링

**TypeScript 타입 안전성:**
```typescript
// ✅ 강력한 타입 정의
export type AIProvider = 'claude' | 'gemini' | 'gpt'

export interface AIMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface AIResponse {
  content: string
  provider: AIProvider
  tokens_used?: number
  cached?: boolean
}

export interface AIError {
  provider: AIProvider
  error: string
  retryable: boolean
}
```

---

## 전제조건 확인

**S1BI1 완료 확인:**
- `.env.local` 파일 존재
- 환경변수 설정 (ANTHROPIC_API_KEY, GOOGLE_AI_API_KEY, OPENAI_API_KEY, RESEND_API_KEY)

---

## 생성 파일 (3개)

### 1. lib/ai/client.ts

**목표:** AI 통합 클라이언트 (Claude, Gemini, GPT)

**참고 파일:** `backend/services/ai_client.py`

**주요 메서드:**
- `chat()`: AI 3사 통합 인터페이스
- `callClaude()`: Claude API 호출 (60% 사용)
- `callGemini()`: Gemini API 호출 (20% 사용)
- `callGPT()`: GPT API 호출 (20% 사용)
- `validateApproval()`: AI 승인 포인트 검증

**개선 사항:**
- ✅ 환경변수 검증
- ✅ 재시도 로직 (exponential backoff)
- ✅ 타임아웃 설정 (30초)
- ✅ 응답 캐싱
- ✅ 토큰 사용량 추적

### 2. lib/email/sender.ts

**목표:** 이메일 발송 서비스 (Resend)

**참고 파일:** `backend/services/email_sender.py`

**주요 메서드:**
- `send()`: 이메일 발송
- `sendProjectCreatedEmail()`: 프로젝트 생성 알림
- `sendApprovalRequestEmail()`: 승인 요청 알림
- `sendReportCompletedEmail()`: 보고서 완료 알림

**개선 사항:**
- ✅ 이메일 주소 검증
- ✅ HTML 이스케이프 (XSS 방지)
- ✅ 재시도 로직
- ✅ 에러 로깅

### 3. lib/notifications/service.ts

**목표:** 알림 디스패처

**참고 파일:** `backend/services/notification_dispatcher.py`

**주요 메서드:**
- `dispatch()`: 알림 타입별 분기
- `dispatchMultiple()`: 여러 알림 발송

**개선 사항:**
- ✅ 타입 안전성
- ✅ 비동기 처리
- ✅ 실패 시 재시도

---

## 완료 기준

### 필수 (Must Have)
- [ ] 목업 Python 파일 읽고 로직 분석 완료
- [ ] AI 클라이언트 구현 (Claude, Gemini, GPT)
- [ ] 이메일 발송 서비스 구현 (Resend)
- [ ] 알림 디스패처 구현
- [ ] 환경변수 설정 확인

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] AI API 호출 성공 (3사)
- [ ] 이메일 발송 성공
- [ ] 에러 핸들링 동작 확인

### 개선 항목 (Improvement)
- [ ] 보안: API 키 관리, Rate limiting
- [ ] 성능: 캐싱, 재시도, 타임아웃
- [ ] 코드 품질: JSDoc, 에러 처리
- [ ] API 설계: 통일된 인터페이스

---

## 환경 변수

`.env.local`에 추가:

```
# AI API Keys
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
OPENAI_API_KEY=sk-proj-...

# Email API Key
RESEND_API_KEY=re_...
```

---

## 참조

### 기존 프로토타입 (목업)

**⚠️ 주의: 목업은 참고용이며 완벽하지 않음. 개선하면서 마이그레이션할 것**

- `Valuation_Company/valuation-platform/backend/services/ai_client.py`
- `Valuation_Company/valuation-platform/backend/services/email_sender.py`
- `Valuation_Company/valuation-platform/backend/services/notification_dispatcher.py`

**분석 포인트:**
1. AI 3사 호출 방식의 차이점은?
2. 승인 포인트 검증 로직은 어떻게 되어 있는가?
3. 재시도 로직이 있는가? (개선 필요)
4. API 키 관리는 어떻게 되어 있는가? (개선 필요)

### 관련 Task
- **S1BI1**: 환경변수 설정
- **S2BA1**: AI 승인 포인트 연동

---

## 주의사항

### ⚠️ 목업의 한계

1. **재시도 로직 없음**
   - 네트워크 오류 시 즉시 실패
   - Exponential backoff 필요

2. **타임아웃 없음**
   - 무한 대기 가능
   - 30초 타임아웃 설정 필요

3. **API 키 하드코딩**
   - 보안 취약
   - 환경변수 사용 필요

### 🔒 보안

1. **API 키 관리**
   - 환경변수로 관리
   - 하드코딩 금지
   - 로그에 노출 금지

2. **Rate Limiting**
   - AI API 호출 제한
   - 이메일 발송 제한

3. **프롬프트 Injection**
   - 사용자 입력 sanitization
   - 시스템 프롬프트 보호

### ⚡ 성능

1. **캐싱**
   - AI 응답 캐싱 (동일 요청)
   - 메모리 또는 Redis

2. **재시도**
   - Exponential backoff
   - 최대 3회 시도

3. **타임아웃**
   - AI API: 30초
   - 이메일: 10초

---

## 예상 소요 시간

**작업 복잡도**: High
**파일 수**: 3개
**라인 수**: ~400줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 마이그레이션 + 개선 방식으로 변경
