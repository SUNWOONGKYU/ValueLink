# 02. 저장위치 규칙

> Stage 폴더에 먼저 저장 → Pre-commit Hook으로 루트에 자동 복사

---

## 1. 저장 순서 (핵심)

```
1. Stage 폴더에 저장 (원본, 프로세스 관리용)
      ↓
2. git commit 시 Pre-commit Hook 자동 실행
      ↓
3. 루트 폴더로 자동 복사 (배포용)
```

**핵심:** Stage가 원본, 루트는 자동 복사본

---

## 2. 배포 구조 (루트 디렉토리)

```
루트/
├── api/                    ← 백엔드 인터페이스 (배포)
├── pages/                  ← 화면/페이지 (배포)
├── assets/                 ← 정적 자원 (배포)
├── scripts/                ← 자동화 도구 (개발용)
├── index.html              ← 메인 페이지
└── 404.html                ← 에러 페이지
```

**핵심:** 4개 폴더 + 2개 HTML

---

## 3. Stage → Root 매핑 (자동 복사 대상)

| Area | Stage 폴더 | Root 폴더 (자동 복사) |
|------|-----------|----------------------|
| **F** | `S?_*/Frontend/` | `pages/` |
| **BA** | `S?_*/Backend_APIs/` | `api/Backend_APIs/` |
| **S** | `S?_*/Security/` | `api/Security/` |
| **BI** | `S?_*/Backend_Infra/` | `api/Backend_Infra/` |
| **E** | `S?_*/External/` | `api/External/` |

---

## 4. 저장 예시

### Frontend (F Area)
```
Task: S2F1
File: google-login.html

1. 저장: S2_개발-1차/Frontend/pages/auth/google-login.html  ← 원본
2. 자동복사: pages/auth/google-login.html                    ← 배포
```

### Backend APIs (BA Area)
```
Task: S2BA1
File: subscription-cancel.js

1. 저장: S2_개발-1차/Backend_APIs/subscription-cancel.js    ← 원본
2. 자동복사: api/Backend_APIs/subscription-cancel.js        ← 배포
```

### Security (S Area)
```
Task: S2S1
File: google-callback.js

1. 저장: S2_개발-1차/Security/google-callback.js            ← 원본
2. 자동복사: api/Security/google-callback.js                ← 배포
```

---

## 5. 자동 복사 안 하는 Area (6개)

| # | Area | 설명 | 이유 |
|---|------|------|------|
| 1 | M | Documentation | 문서 - 배포 불필요 |
| 2 | U | Design | 디자인 파일 - 배포 불필요 |
| 3 | D | Database | SQL - DB에서 직접 실행 |
| 4 | T | Testing | 테스트 코드 - 배포 불필요 |
| 5 | O | DevOps | 설정/스크립트 - scripts/ 폴더 |
| 6 | C | Content | 콘텐츠 - DB에 저장 |

---

## 6. Pre-commit Hook 설정

**스크립트 위치:** `scripts/sync-to-root.js`

**Hook 설정:** `.git/hooks/pre-commit`
```bash
#!/bin/sh
echo "🔄 Stage → Root 동기화 중..."

node scripts/sync-to-root.js

if [ $? -ne 0 ]; then
    echo "❌ 동기화 실패! 커밋을 중단합니다."
    exit 1
fi

echo "✅ 동기화 완료! 커밋을 진행합니다."
```

**동작:**
1. `git commit` 실행
2. Pre-commit hook이 `sync-to-root.js` 자동 실행
3. Stage 폴더 → 루트 폴더 복사
4. 복사 성공 시 커밋 진행

---

## 7. 스크립트 저장 원칙

```
1. 단일 대상 스크립트 → 해당 폴더에 저장
   예: generate-ordersheets-js.js → OrderSheet_Templates/

2. 복수 대상 스크립트 → 루트 scripts/에 저장
   예: sync-to-root.js → scripts/
       build-web-assets.js → scripts/
```

---

## 8. 폴더별 상세 구조

### api/ (백엔드 인터페이스)

```
api/
├── Backend_APIs/           ← 핵심 API
├── Security/               ← 인증/인가
├── Backend_Infra/          ← 인프라/라이브러리
└── External/               ← 외부 연동
```

**⚠️ 폴더명 변경 금지!** Vercel이 `api` 이름을 인식함

### pages/ (화면/페이지)

```
pages/
├── auth/                   ← 인증 관련
├── subscription/           ← 구독 관련
└── mypage/                 ← My Page
```

### assets/ (정적 자원)

```
assets/
├── css/                    ← 스타일시트
├── js/                     ← JavaScript
├── images/                 ← 이미지
└── fonts/                  ← 글꼴
```

---

## 체크리스트

- [ ] Stage 폴더에 저장했는가? (원본)
- [ ] 올바른 Stage/Area 폴더인가?
- [ ] git commit 시 자동 복사 확인했는가?
- [ ] 루트 폴더에 복사되었는가? (배포용)

---

## 참고: React/Next.js로 전환할 경우

> 현재 이 프로젝트는 Vanilla를 사용하지만, React로 전환 시 아래 구조 적용

```
루트/
├── app/                    ← 페이지 + API + 레이아웃 통합
├── components/             ← 재사용 UI 조각
├── public/                 ← 정적 자원 (Vanilla의 assets)
└── lib/                    ← 유틸리티, 클라이언트 설정
```

**Vanilla → React 매핑:**
| Vanilla | React |
|---------|-------|
| pages/ | app/ |
| api/ | app/api/ |
| assets/ | public/ |
| index.html | app/page.tsx |
| 404.html | app/not-found.tsx |

**상세 설명:** `부수적_고유기능/콘텐츠/Tips/개발_실무/Vanilla와_React란_무엇인가.md`
