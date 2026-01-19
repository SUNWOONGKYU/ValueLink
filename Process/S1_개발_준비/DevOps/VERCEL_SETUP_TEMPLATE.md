# Vercel Deployment Setup Guide Template

## Overview

Vercel 배포 설정 가이드입니다.

---

## 1. Vercel 프로젝트 생성

### Step 1: Vercel 로그인
```
https://vercel.com → Log In (GitHub 계정)
```

### Step 2: 새 프로젝트 추가
```
Dashboard → Add New... → Project
→ Import Git Repository → 프로젝트 선택
```

### Step 3: 프로젝트 설정

| 항목 | 값 |
|------|-----|
| Project Name | `your-project-name` (소문자, 하이픈 가능) |
| Framework Preset | `Other` (정적 사이트) 또는 해당 프레임워크 |
| Root Directory | 배포할 폴더 경로 |
| Build Command | (정적 사이트는 비워두기) |
| Output Directory | (정적 사이트는 비워두기) |

**주의**: Project Name에 대문자, 한글, 특수문자 사용 불가

---

## 2. vercel.json 설정

### 파일 위치
`프로젝트_루트/vercel.json`

### 기본 설정
```json
{
  "version": 2,
  "name": "your-project-name",
  "buildCommand": null,
  "outputDirectory": ".",
  "framework": null,
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Credentials", "value": "true" },
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,POST,PUT,DELETE,OPTIONS" },
        { "key": "Access-Control-Allow-Headers", "value": "Content-Type, Authorization" }
      ]
    }
  ],
  "functions": {
    "api/**/*.js": {
      "maxDuration": 30,
      "memory": 1024
    }
  }
}
```

---

## 3. 환경변수 설정

### Vercel Dashboard 위치
```
Settings → Environment Variables
```

### 환경변수 추가
| Key | Value | 환경 |
|-----|-------|------|
| `DATABASE_URL` | `https://...` | Production, Preview |
| `API_KEY` | `...` | Production, Preview |

---

## 4. 도메인 연결

### Step 1: 도메인 추가
```
Settings → Domains → Add Domain
→ 도메인 입력
```

### Step 2: DNS 설정

#### A 레코드
```
호스트명: @ (또는 비워두기)
IP: 76.76.21.21
```

#### CNAME 레코드 (www)
```
호스트명: www
값: cname.vercel-dns.com
```

---

## 5. 트러블슈팅

### 문제 1: Project Name 에러
```
The name contains invalid characters.
```
**해결**: 소문자, 숫자, 하이픈만 사용

### 문제 2: Build 에러
```
sh: line 1: command not found
```
**해결**: package.json에서 잘못된 build 스크립트 제거

### 문제 3: 함수 패턴 에러
```
The pattern doesn't match any Serverless Functions
```
**해결**: vercel.json에서 존재하지 않는 패턴 제거

---

## 6. 체크리스트

### 배포 전
- [ ] vercel.json 설정 확인
- [ ] 환경변수 설정
- [ ] GitHub에 push

### 배포 후
- [ ] 배포 성공 확인
- [ ] 도메인 연결 (선택)
- [ ] SSL 인증서 확인

---

**Template Version**: 1.0
