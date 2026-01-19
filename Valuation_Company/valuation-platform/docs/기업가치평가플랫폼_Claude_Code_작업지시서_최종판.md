# 기업가치평가 플랫폼 MVP - Claude Code 작업지시서 (최종판)
## valuation.ai.kr

---

## 🎯 프로젝트 개요

### 핵심 목표
**첫 번째 고객 확보!** 이것이 MVP의 유일한 목표입니다.

### 사업 전략
```
1인 개발 → MVP 출시 → 첫 고객 확보 → 수익 발생 → 확장
```

### 차별화 포인트
1. **AI 자동화**: 5-7일 내 평가 완료 (기존: 2-3주)
2. **가격 경쟁력**: 기존 시장 대비 **50% 수준**
3. **이중 산출물 제공**:
   - PDF 평가보고서 (도장 찍힌 정식 문서)
   - 엑셀 계산 파일 (고객이 직접 수치 변경하여 재계산 가능)
4. **투명성**: 모든 계산 과정 공개
5. **무료 시뮬레이터**: 평가 신청 전 간단 테스트 제공

---

## 📊 개발 우선순위

### Phase 1: MVP (우선 개발) - 4주

**A. 정식 평가 서비스 (유료)**
```
1. DCF 평가 시스템
   - 평가 로직 (Python)
   - PDF 보고서 생성
   - 엑셀 계산 파일 생성 (고객이 수정 가능)

2. 상대가치 평가 시스템
   - 평가 로직
   - PDF 보고서 생성
   - 엑셀 계산 파일 생성
```

**B. 무료 체험 기능 (리드 생성)**
```
3. 웹 시뮬레이터 (3종)
   - DCF 간이 계산기 (React)
   - 상대가치 간이 계산기 (React)
   - 상증법 간이 계산기 (React)
   → 목적: 평가 신청 전 간단 테스트
   → [정식 평가 신청하기] 버튼으로 전환 유도
```

**C. 기본 웹사이트**
```
4. 메인 랜딩 페이지
   - 5가지 평가방법 소개
   - YouTube 콘텐츠 임베딩
   - 평가 신청 폼
```

### Phase 2: 확장 (MVP 이후) - +4주
```
1. IPO 평가
2. 상증법 평가
3. 자산가치평가
4. 랭킹 시스템
5. AI 아바타 IR
```

---

## 🔧 기술 스택

### Backend
```yaml
언어: Python 3.11+
프레임워크: FastAPI
데이터베이스: Supabase (PostgreSQL)
ORM: Prisma
AI: Claude API (50%), OpenAI API (30%), Gemini API (20%)
```

### Frontend
```yaml
프레임워크: Next.js 14 (App Router)
스타일링: Tailwind CSS
UI 라이브러리: shadcn/ui
차트: Recharts
```

### Deployment
```yaml
호스팅: Vercel
데이터베이스: Supabase (Managed PostgreSQL)
파일 저장: Supabase Storage
도메인: valuation.ai.kr (이미 확보됨)
```

---

## 📁 프로젝트 구조

```
valuation-platform/
├── frontend/                 # Next.js 프론트엔드
│   ├── app/
│   │   ├── page.tsx         # 메인 페이지
│   │   ├── dcf/            # DCF 평가 신청
│   │   ├── comparable/      # 상대가치 평가
│   │   ├── simulator/       # 시뮬레이터
│   │   └── api/            # API 라우트
│   ├── components/          # 재사용 컴포넌트
│   ├── lib/                # 유틸리티
│   └── public/             # 정적 파일
│
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # FastAPI 앱
│   │   ├── models/         # 데이터 모델
│   │   ├── routers/        # API 라우터
│   │   ├── services/       # 비즈니스 로직
│   │   │   ├── dcf_evaluator.py
│   │   │   ├── comparable_evaluator.py
│   │   │   ├── excel_generator.py
│   │   │   └── pdf_generator.py
│   │   └── utils/          # 유틸리티
│   └── tests/              # 테스트
│
├── database/
│   └── schema.prisma       # Prisma 스키마
│
└── docs/
    └── api-docs.md         # API 문서
```

---

## 💾 데이터베이스 스키마 (Prisma)

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-py"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Company {
  id              String   @id @default(uuid())
  name            String
  businessNumber  String   @unique
  industry        String
  establishedDate DateTime
  ceo             String
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  evaluations     Evaluation[]
}

model Evaluation {
  id              String   @id @default(uuid())
  companyId       String
  evaluationType  String   // "DCF", "COMPARABLE", "IPO", "TAX", "NAV"
  evaluationDate  DateTime
  status          String   // "REQUESTED", "IN_PROGRESS", "COMPLETED"

  // 평가 결과
  enterpriseValue Float?
  equityValue     Float?
  sharePrice      Float?

  // 파일 경로
  excelFilePath   String?
  pdfFilePath     String?

  // 추가 데이터 (JSON)
  inputData       Json
  assumptions     Json?
  results         Json?

  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  company         Company  @relation(fields: [companyId], references: [id])
}

model User {
  id              String   @id @default(uuid())
  email           String   @unique
  name            String
  role            String   // "COMPANY", "INVESTOR", "ADMIN"
  createdAt       DateTime @default(now())
}
```

---

## 🎯 최종 목표

**4주 내에 첫 번째 고객 확보!**

MVP 기능:
1. ✅ DCF 평가 신청 및 자동 처리
2. ✅ 상대가치 평가 신청
3. ✅ 엑셀 파일 생성 및 제공 (고객이 직접 수정 가능)
4. ✅ 3종 웹 시뮬레이터
5. ✅ 메인 페이지 + YouTube 콘텐츠

---

**상세 내용은 Phase1_평가시스템_개발_로드맵.md 참조**
