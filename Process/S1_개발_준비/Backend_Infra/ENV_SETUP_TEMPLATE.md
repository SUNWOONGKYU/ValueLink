# Environment Variables Setup Guide Template

## Overview

프로젝트 환경변수 설정 가이드입니다.

---

## 1. 환경변수 파일 구조

### 1.1 파일 위치

```
프로젝트_루트/
├── .env.example      # 템플릿 (Git에 포함)
├── .env.local        # 로컬 개발용 (Git 제외)
└── .env.production   # 프로덕션용 (Git 제외)
```

### 1.2 .gitignore 설정

```
# 환경변수 파일
.env
.env.local
.env.production
.env*.local
```

---

## 2. 필수 환경변수

### 2.1 Database (예: Supabase)

```env
# Database 연결
DATABASE_URL=https://[project-id].supabase.co
DATABASE_ANON_KEY=[anon-key]
DATABASE_SERVICE_ROLE_KEY=[service-role-key]
```

### 2.2 OAuth (예: Google)

```env
# OAuth
OAUTH_CLIENT_ID=[client-id]
OAUTH_CLIENT_SECRET=[client-secret]
```

### 2.3 이메일 서비스 (예: Resend)

```env
# Email Service
EMAIL_API_KEY=[api-key]
```

### 2.4 결제 서비스 (예: TossPayments)

```env
# Payment
PAYMENT_CLIENT_KEY=[client-key]
PAYMENT_SECRET_KEY=[secret-key]
```

### 2.5 AI API (선택)

```env
# AI APIs
OPENAI_API_KEY=[key]
GOOGLE_AI_API_KEY=[key]
```

### 2.6 앱 설정

```env
# App Configuration
APP_URL=http://localhost:3000
NODE_ENV=development
```

---

## 3. 환경별 설정

### 3.1 환경별 구분

| 환경 | 용도 | 설정 위치 |
|------|------|----------|
| Development | 로컬 개발 | `.env.local` |
| Preview | PR/브랜치 미리보기 | 호스팅 Dashboard |
| Production | 프로덕션 배포 | 호스팅 Dashboard |

---

## 4. 보안 주의사항

### 4.1 금지 사항

- 환경변수 파일을 Git에 커밋
- API 키를 코드에 하드코딩
- 클라이언트 사이드에서 SECRET KEY 사용
- 환경변수 값을 공개 저장소에 노출

### 4.2 권장 사항

- `.env.example`만 Git에 포함 (값 없이 키 이름만)
- 호스팅 Dashboard에서 프로덕션 키 관리
- 정기적으로 API 키 로테이션
- 환경별로 다른 키 사용

---

## 5. 체크리스트

- [ ] `.env.example` 파일 생성
- [ ] `.gitignore`에 환경변수 파일 추가
- [ ] 로컬 `.env.local` 파일 설정
- [ ] 호스팅 서비스에 프로덕션 환경변수 설정

---

**Template Version**: 1.0
