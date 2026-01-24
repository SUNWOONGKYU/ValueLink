# ValueLink 색상 디자인 규칙

## 색상 체계 및 적용 규칙

### 1. 파란색 (#1D4ED8) - 시스템/플랫폼 활동

**적용 대상:**
- **Valuation (평가 시스템)**
  - 기업가치 평가 관련 모든 기능
  - DCF, 상대가치, 본질가치, 자산가치, 상증세법 평가
  - 평가 시뮬레이터
  - 학습 콘텐츠

**의미:**
- 플랫폼이 제공하는 시스템 기능
- AI 기반 평가 서비스
- 객관적이고 전문적인 분석

**UI 적용:**
- 메뉴 active 상태
- 카드 border-top
- 카드 hover 효과
- 버튼 색상
- 아이콘 색상

---

### 2. 초록색 (#166534) - 기업 관련 활동 👑

**적용 대상:**
- **Link (기업을 위한 연결)**
  - 투자자 연결
  - 비즈니스 파트너 연결
  - 서포터 연결
  - 매칭 및 제안 기능

- **고객 기업 활동**
  - My Page (마이페이지)
  - 8단계 평가 프로세스
  - 기업 프로필
  - 평가 요청/진행 현황
  - 회원가입 (기업 활동)

**의미:**
- 성장하는 기업 (👑 왕)
- 기업을 위한 연결과 지원
- 고객 기업의 활동

**UI 적용:**
- Link 카드 border-top
- Link 카드 hover 효과
- My Page 관련 UI
- 기업 프로세스 진행 상태
- 회원가입 버튼

---

### 3. 주황색 (#F59E0B) - 투자 정보

**적용 대상:**
- **Deals (투자 정보)**
  - 투자받은 기업 정보
  - 투자유치 뉴스
  - IR 정보
  - 기업 포트폴리오
  - 투자 동향

**의미:**
- 투자 관련 정보와 데이터
- 딜 뉴스 및 트렌드
- 투자 생태계 현황

**UI 적용:**
- Deals 카드 border-top
- Deals 카드 hover 효과
- 투자 정보 관련 버튼

---

## 색상 코드

```css
/* Main Colors */
--deep-blue: #1D4ED8;      /* 시스템/플랫폼 */
--deep-green: #166534;     /* 기업/고객 */
--amber: #F59E0B;          /* 연결 */

/* Hover Effects */
--deep-blue-hover: rgba(29, 78, 216, 0.3);
--deep-green-hover: rgba(22, 101, 52, 0.3);
--amber-hover: rgba(245, 158, 11, 0.3);

/* Light Versions */
--deep-blue-light: #3B82F6;
--deep-green-light: #22C55E;
--amber-light: #FBBF24;

/* Pale Versions (배경용) */
--deep-blue-pale: #DBEAFE;
--deep-green-pale: #DCFCE7;
--amber-pale: #FEF3C7;
```

---

## 적용 예시

### 인트로 화면 (index.html)
```
┌─────────────────────────────────────┐
│ 📊 Valuation (파란색)                │
│ - border-top: blue                  │
│ - hover: blue shadow                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🤝 Link (주황색)                     │
│ - border-top: amber                 │
│ - hover: amber shadow               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📰 Deals (초록색)                    │
│ - border-top: green                 │
│ - hover: green shadow               │
└─────────────────────────────────────┘
```

### 헤더 메뉴
```
Valuation (active: 파란색)
Link (active: 주황색)
Deals (active: 초록색)
```

### My Page
```
전체 테마: 초록색
- 버튼: 초록색
- 아이콘: 초록색
- active 상태: 초록색
```

---

## 문서 버전
- 작성일: 2026-01-24
- 버전: 1.0
- 작성자: Claude Code
