# OAuth Setup Guide Template

## Overview

OAuth 인증 설정 가이드입니다. (Google, GitHub, Kakao 등)

---

## 1. OAuth 인증 흐름

```
사용자 → OAuth Provider → 인증 서버 → 앱
              ↓
      (Google, GitHub 등)
```

---

## 2. Google OAuth 설정

### 2.1 Google Cloud Console 설정

**Step 1: 프로젝트 생성**
```
Google Cloud Console → 새 프로젝트 생성
https://console.cloud.google.com/
```

**Step 2: OAuth 동의 화면 구성**
```
APIs & Services → OAuth consent screen

- User Type: External
- App name: [프로젝트 이름]
- Scopes: email, profile, openid
```

**Step 3: OAuth 2.0 클라이언트 생성**
```
APIs & Services → Credentials → Create Credentials → OAuth client ID

- Application type: Web application (중요!)
- Name: [클라이언트 이름]
- Authorized redirect URIs: [Callback URL]
```

### 2.2 발급된 정보

```
Client ID: [GOOGLE_CLIENT_ID]
Client Secret: [GOOGLE_CLIENT_SECRET]
```

---

## 3. GitHub OAuth 설정

### 3.1 GitHub Developer Settings

**Step 1: OAuth App 생성**
```
GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
```

**Step 2: 앱 설정**
```
- Application name: [프로젝트 이름]
- Homepage URL: [앱 URL]
- Authorization callback URL: [Callback URL]
```

### 3.2 발급된 정보

```
Client ID: [GITHUB_CLIENT_ID]
Client Secret: [GITHUB_CLIENT_SECRET]
```

---

## 4. Callback URL 설정

### 4.1 개발 환경

```
http://localhost:3000/auth/callback
http://localhost:8888/auth/callback
```

### 4.2 프로덕션 환경

```
https://your-domain.com/auth/callback
```

### 4.3 Supabase 사용 시

```
https://[project-id].supabase.co/auth/v1/callback
```

---

## 5. 클라이언트 구현 예시

### 5.1 Supabase + Google OAuth

```javascript
const { createClient } = supabase;
const supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function handleGoogleLogin() {
    const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: window.location.origin + '/dashboard',
            queryParams: {
                access_type: 'offline',
                prompt: 'consent'
            }
        }
    });

    if (error) {
        console.error('Login error:', error.message);
    }
}
```

### 5.2 세션 확인

```javascript
async function checkSession() {
    const { data: { session } } = await supabaseClient.auth.getSession();
    if (session) {
        console.log('User:', session.user.email);
    }
}
```

### 5.3 로그아웃

```javascript
async function handleLogout() {
    const { error } = await supabaseClient.auth.signOut();
    if (!error) {
        window.location.href = '/login';
    }
}
```

---

## 6. 트러블슈팅

### 문제 1: Provider not enabled
```
Unsupported provider: provider is not enabled
```
**해결**: 인증 서버(Supabase 등)에서 해당 Provider 활성화

### 문제 2: Redirect URI 불일치
```
Error 400: redirect_uri_mismatch
```
**해결**: OAuth 설정의 Redirect URI와 앱의 Callback URL 일치시키기

### 문제 3: Application type 오류
**해결**: OAuth Client 생성 시 "Web application" 선택 (Desktop 아님)

---

## 7. 체크리스트

### OAuth Provider 설정
- [ ] OAuth 동의 화면 구성
- [ ] OAuth Client 생성 (Web application)
- [ ] Redirect URI 등록
- [ ] Client ID / Secret 저장

### 인증 서버 설정 (Supabase 등)
- [ ] Provider 활성화
- [ ] Client ID / Secret 입력
- [ ] Callback URL 확인

### 앱 설정
- [ ] 환경변수에 Client ID 설정
- [ ] 로그인 UI 구현
- [ ] Callback 처리 구현

---

**Template Version**: 1.0
