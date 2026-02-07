# Authentication Flow

## 개요

ValueLink는 Supabase Auth를 사용하여 인증을 처리합니다.

- **인증 방식**: JWT Bearer Token
- **세션 관리**: Supabase SSR (Server-Side Rendering)
- **OAuth Providers**: Google, Kakao, GitHub

---

## 1. 회원가입 (이메일)

### POST /api/auth/signup

이메일로 회원가입합니다.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "홍길동",
  "company_name": "스타트업 A",
  "role": "customer"
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | 이메일 주소 |
| password | string | Yes | 비밀번호 (최소 8자) |
| name | string | Yes | 이름 |
| company_name | string | No | 회사명 |
| role | string | Yes | 역할 (customer, investor) |

**Password Requirements**:
- 최소 8자 이상
- 영문, 숫자 포함
- 특수문자 권장

**Response** (201 Created):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "email_confirmed_at": null,
    "created_at": "2026-02-07T10:00:00Z"
  },
  "session": null,
  "message": "확인 이메일이 발송되었습니다."
}
```

**Note**: 이메일 확인 후 세션이 생성됩니다.

---

## 2. 로그인 (이메일)

### POST /api/auth/login

이메일로 로그인합니다.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "email_confirmed_at": "2026-02-07T10:30:00Z"
  },
  "session": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "v1.refresh-token-string",
    "expires_in": 3600,
    "expires_at": 1738756800,
    "token_type": "bearer"
  }
}
```

**Error Responses**:
- 400: Invalid email or password
- 422: Email not confirmed

---

## 3. OAuth 로그인

### 3.1 Google 로그인

#### GET /api/auth/google

Google OAuth 로그인을 시작합니다.

**Flow**:
```
1. 클라이언트 → GET /api/auth/google
2. 서버 → Google OAuth URL 리디렉션
3. 사용자 → Google 로그인
4. Google → /api/auth/callback?code=... 리디렉션
5. 서버 → 세션 생성 → 대시보드 리디렉션
```

**Response** (302 Redirect):
```
Location: https://accounts.google.com/o/oauth2/v2/auth?
  client_id=...&
  redirect_uri=https://valuation.ai.kr/api/auth/callback&
  scope=email%20profile&
  response_type=code&
  state=...
```

---

### 3.2 Kakao 로그인

#### GET /api/auth/kakao

Kakao OAuth 로그인을 시작합니다.

**Response** (302 Redirect):
```
Location: https://kauth.kakao.com/oauth/authorize?
  client_id=...&
  redirect_uri=https://valuation.ai.kr/api/auth/callback&
  response_type=code&
  state=...
```

---

### 3.3 GitHub 로그인

#### GET /api/auth/github

GitHub OAuth 로그인을 시작합니다.

**Response** (302 Redirect):
```
Location: https://github.com/login/oauth/authorize?
  client_id=...&
  redirect_uri=https://valuation.ai.kr/api/auth/callback&
  scope=user:email&
  state=...
```

---

### 3.4 OAuth Callback

#### GET /api/auth/callback

OAuth 콜백을 처리합니다.

**Query Parameters**:
| Parameter | Description |
|-----------|-------------|
| code | Authorization code |
| state | CSRF 방지 토큰 |
| error | 에러 코드 (실패 시) |

**Success**: 대시보드로 리디렉션 (`/dashboard`)
**Failure**: 로그인 페이지로 리디렉션 (`/login?error=...`)

---

## 4. 세션 관리

### 4.1 세션 갱신

#### POST /api/auth/refresh

Access token을 갱신합니다.

**Request**:
```json
{
  "refresh_token": "v1.refresh-token-string"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "v1.new-refresh-token-string",
  "expires_in": 3600,
  "expires_at": 1738760400
}
```

---

### 4.2 현재 사용자 조회

#### GET /api/auth/user

현재 로그인한 사용자 정보를 조회합니다.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "홍길동",
    "role": "customer",
    "company_name": "스타트업 A",
    "avatar_url": "https://example.com/avatar.jpg",
    "created_at": "2026-02-07T10:00:00Z"
  }
}
```

---

### 4.3 로그아웃

#### POST /api/auth/logout

세션을 종료합니다.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "message": "로그아웃되었습니다."
}
```

---

## 5. 비밀번호 관리

### 5.1 비밀번호 재설정 요청

#### POST /api/auth/reset-password

비밀번호 재설정 이메일을 발송합니다.

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "message": "비밀번호 재설정 이메일이 발송되었습니다."
}
```

**Note**: 보안상 이메일 존재 여부와 관계없이 동일한 응답을 반환합니다.

---

### 5.2 비밀번호 업데이트

#### PUT /api/auth/update-password

비밀번호를 변경합니다. (로그인 필요)

**Headers**:
```
Authorization: Bearer {access_token}
```

**Request**:
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

**Response**:
```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

---

## 6. JWT 토큰 사용

### 6.1 토큰 구조

```
Header.Payload.Signature

Header: {
  "alg": "HS256",
  "typ": "JWT"
}

Payload: {
  "aud": "authenticated",
  "exp": 1738756800,
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "customer",
  "session_id": "session-uuid"
}
```

---

### 6.2 API 요청 시 사용

모든 인증이 필요한 API 요청에 `Authorization` 헤더를 포함합니다:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**예시 (cURL)**:
```bash
curl -X GET "https://valuation.ai.kr/api/projects" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

---

### 6.3 토큰 만료 처리

Access token 만료 시 (1시간):
1. 401 Unauthorized 응답 수신
2. Refresh token으로 새 access token 요청
3. 새 token으로 원래 요청 재시도

```javascript
// 예시: 토큰 갱신 로직
async function refreshAndRetry(originalRequest) {
  const { data } = await fetch('/api/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: getRefreshToken() })
  });

  setAccessToken(data.access_token);
  return fetch(originalRequest.url, {
    ...originalRequest,
    headers: {
      ...originalRequest.headers,
      'Authorization': `Bearer ${data.access_token}`
    }
  });
}
```

---

## 7. 역할 기반 접근 제어 (RBAC)

### 7.1 역할 정의

| 역할 | 코드 | 설명 |
|------|------|------|
| 고객 | customer | 기업 고객 (평가 요청자) |
| 회계사 | accountant | 공인회계사 (평가 수행자) |
| 관리자 | admin | 시스템 관리자 |
| 투자자 | investor | 투자자 (뉴스 조회) |

---

### 7.2 역할별 권한

| 기능 | customer | accountant | admin | investor |
|------|:--------:|:----------:|:-----:|:--------:|
| 평가 요청 생성 | ✅ | ❌ | ✅ | ❌ |
| 프로젝트 조회 (본인) | ✅ | ✅ | ✅ | ❌ |
| 프로젝트 조회 (전체) | ❌ | ❌ | ✅ | ❌ |
| 승인 포인트 승인 | ❌ | ✅ | ✅ | ❌ |
| 평가 수행 | ❌ | ✅ | ✅ | ❌ |
| 초안 작성/수정 | ❌ | ✅ | ✅ | ❌ |
| 요청 승인/거절 | ❌ | ❌ | ✅ | ❌ |
| 회계사 배정 | ❌ | ❌ | ✅ | ❌ |
| Deal 뉴스 조회 | ✅ | ✅ | ✅ | ✅ |
| 사용자 관리 | ❌ | ❌ | ✅ | ❌ |

---

### 7.3 미들웨어 역할 검증

```typescript
// middleware.ts
import { createClient } from '@/lib/supabase/middleware';

export async function middleware(request: NextRequest) {
  const { supabase, response } = createClient(request);
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 역할 검증
  const { data: userData } = await supabase
    .from('users')
    .select('role')
    .eq('user_id', user.id)
    .single();

  // Admin 전용 경로 검증
  if (request.nextUrl.pathname.startsWith('/admin')) {
    if (userData?.role !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  return response;
}
```

---

## 8. RLS (Row Level Security)

Supabase RLS 정책으로 데이터베이스 수준에서 접근을 제어합니다.

### 8.1 Projects 테이블 RLS

```sql
-- 고객: 본인 프로젝트만 조회
CREATE POLICY "Customers view own projects"
ON projects FOR SELECT
USING (
  auth.uid() = user_id
  OR
  (SELECT role FROM users WHERE user_id = auth.uid()) = 'admin'
  OR
  auth.uid() = accountant_id
);

-- 회계사: 담당 프로젝트만 수정
CREATE POLICY "Accountants update assigned projects"
ON projects FOR UPDATE
USING (
  auth.uid() = accountant_id
  OR
  (SELECT role FROM users WHERE user_id = auth.uid()) = 'admin'
);
```

---

### 8.2 Documents 테이블 RLS

```sql
-- 프로젝트 관계자만 문서 접근
CREATE POLICY "Project members access documents"
ON documents FOR SELECT
USING (
  project_id IN (
    SELECT project_id FROM projects
    WHERE user_id = auth.uid()
    OR accountant_id = auth.uid()
  )
  OR
  (SELECT role FROM users WHERE user_id = auth.uid()) = 'admin'
);
```

---

## 9. 보안 권장사항

### 9.1 클라이언트 측

- Access token은 메모리에만 저장 (localStorage 사용 금지)
- Refresh token은 httpOnly 쿠키로 저장
- HTTPS 필수 사용
- XSS 방지를 위한 입력값 sanitize

### 9.2 서버 측

- 모든 API에서 토큰 검증
- Rate limiting 적용
- CORS 설정 (허용된 도메인만)
- SQL Injection 방지 (Prepared Statements)

### 9.3 비밀번호 정책

- 최소 8자 이상
- 영문 + 숫자 필수
- 특수문자 권장
- 이전 비밀번호 재사용 금지

---

## 10. 에러 코드

| Code | Message | 설명 |
|------|---------|------|
| AUTH001 | Invalid credentials | 잘못된 이메일/비밀번호 |
| AUTH002 | Email not confirmed | 이메일 미확인 |
| AUTH003 | Token expired | 토큰 만료 |
| AUTH004 | Invalid token | 유효하지 않은 토큰 |
| AUTH005 | Insufficient permissions | 권한 부족 |
| AUTH006 | Account disabled | 비활성화된 계정 |
| AUTH007 | Rate limit exceeded | 요청 한도 초과 |

---

## 버전 정보

- **API Version**: v1
- **Supabase SSR**: @supabase/ssr ^0.5.2
- **Last Updated**: 2026-02-07

---

**작성일**: 2026-02-07
**작성자**: Claude Code
