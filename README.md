# ValueLink - AI-Powered Valuation Platform

**기업가치 평가 자동화 플랫폼**

[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18.3-blue?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Latest-green?logo=supabase)](https://supabase.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Latest-black?logo=vercel)](https://vercel.com/)

---

## 📋 프로젝트 개요

ValueLink는 AI 기술을 활용하여 기업가치 평가(Valuation)를 자동화하는 플랫폼입니다. 5가지 평가 방법론을 지원하며, 회계사의 전문성과 AI의 효율성을 결합하여 고품질의 평가 보고서를 생성합니다.

### 핵심 기능

1. **5가지 평가 방법론 지원**
   - DCF (Discounted Cash Flow - 현금흐름할인법)
   - Relative Valuation (상대가치평가법 - PER, PBR, EV/EBITDA, PSR)
   - Asset-Based Valuation (자산기준가치평가법)
   - Intrinsic Value (본질가치평가법)
   - Tax-Based Valuation (상증세법 - 순자산·순손익 가중평균)

2. **12단계 평가 워크플로우**
   - Step 1-2: 프로젝트 생성 및 견적
   - Step 3-4: 계약 및 착수금 결제
   - Step 5-7: 자료 제출 및 AI 분석
   - Step 8: 22개 AI 승인 포인트 검토
   - Step 9-10: 초안 작성 및 회계사 검토
   - Step 11-12: 보고서 확정 및 최종 결제

3. **22개 AI 승인 포인트 (Approval Points)**
   - DCF: 8개 (WACC, 성장률, FCF 예측, 영구가치 등)
   - Relative: 4개 (동종업체 선정, Multiple 선택 등)
   - Asset: 6개 (자산 재평가, 부채 조정 등)
   - Intrinsic: 2개 (순자산가치, 수익가치 가중치)
   - Tax: 2개 (순자산가치, 순손익가치 가중치)

4. **자동화된 투자 뉴스 트래커**
   - 국내 5대 언론사 + Google Search 크롤링
   - Gemini API 기반 기사 점수 시스템 (11점 만점)
   - 매일 8am KST 자동 실행 (GitHub Actions)
   - 관리자 이메일 자동 발송

5. **DCF 엔진 정확도 검증**
   - 태일회계법인 실제 평가보고서 대조
   - 오차율 2.63% < 5% (검증 통과)

### 기술 스택

#### Frontend
- **Next.js 14.2** - App Router (React Server Components)
- **React 18.3** - 최신 React 기능 (Streaming, Suspense)
- **TypeScript 5.6** - 타입 안정성
- **Tailwind CSS 3.4** - 유틸리티 퍼스트 CSS

#### Backend
- **Supabase** - PostgreSQL DB + Auth + Storage + RLS
- **Vercel** - 서버리스 배포 + Edge Functions

#### AI & Automation
- **Claude API (Anthropic)** - 문서 분석, 승인 포인트 생성
- **Gemini API (Google)** - 뉴스 기사 점수 시스템
- **OpenAI API** - 보고서 초안 작성 (선택)
- **Cheerio** - HTML 파싱 (뉴스 크롤링)
- **node-cron** - 스케줄링 (로컬 개발)
- **GitHub Actions** - Cron Jobs (프로덕션)

#### Testing
- **Jest** - 단위 테스트
- **Playwright** - E2E 테스트
- **React Testing Library** - 컴포넌트 테스트

---

## 🚀 시작하기

### 사전 요구사항

- **Node.js 18.x 이상** (LTS 권장)
- **npm 9.x 이상** (또는 yarn, pnpm)
- **Supabase 계정** (https://supabase.com)
- **Vercel 계정** (https://vercel.com) (배포 시)

### 설치 (5단계)

#### 1. 레포지토리 클론

```bash
git clone https://github.com/SUNWOONGKYU/ValueLink.git
cd ValueLink
```

#### 2. 의존성 설치

```bash
npm install
```

#### 3. 환경 변수 설정

`.env.local` 파일을 생성하고 다음 내용을 입력합니다:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# AI APIs
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-proj-...

# Cron Secret (프로덕션)
CRON_SECRET=your-random-secret-string

# Email (Resend)
RESEND_API_KEY=re_...
ADMIN_EMAIL=admin@valuelink.com
```

#### 4. 데이터베이스 마이그레이션

Supabase Dashboard → SQL Editor에서 `database/schema-v4-final.sql` 파일 실행:

```bash
# 또는 Supabase CLI 사용
npx supabase db push
```

#### 5. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속

---

## 📂 프로젝트 구조

```
valuelink/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # 루트 레이아웃
│   ├── page.tsx                  # 홈페이지
│   ├── valuation/                # 평가 관련 페이지
│   │   ├── process/              # 12단계 워크플로우
│   │   │   ├── step-1/           # 프로젝트 생성
│   │   │   ├── step-5/           # 자료 제출
│   │   │   ├── step-8/           # AI 승인 포인트
│   │   │   └── ...
│   │   ├── guides/               # 평가법 가이드 (5개)
│   │   └── submissions/          # 자료 제출 폼 (5개)
│   ├── valuation-results/        # 평가 결과 페이지 (5개)
│   ├── projects/                 # 프로젝트 관리
│   ├── mypage/                   # 사용자 페이지 (4개 역할)
│   └── investment-tracker/       # 투자 뉴스 트래커
│
├── components/                   # React 컴포넌트
│   ├── guide-template.tsx        # 평가법 가이드 템플릿
│   ├── form-field.tsx            # 폼 필드 공통 컴포넌트
│   ├── submission-form-template.tsx  # 자료 제출 폼 템플릿
│   ├── process-step-template.tsx # 워크플로우 스텝 템플릿
│   ├── mypage-template.tsx       # My Page 템플릿
│   └── valuation-results-template.tsx # 평가 결과 템플릿
│
├── lib/                          # 유틸리티 & 설정
│   ├── supabase/                 # Supabase 클라이언트
│   │   ├── client.ts             # 브라우저 클라이언트
│   │   ├── server.ts             # 서버 클라이언트
│   │   └── middleware.ts         # 인증 미들웨어
│   ├── workflow/                 # 워크플로우 관리
│   │   ├── workflow-manager.ts   # 12단계 관리
│   │   └── approval-points.ts    # 22개 승인 포인트
│   ├── ai/                       # AI 서비스
│   │   └── client.ts             # Claude/Gemini/OpenAI 클라이언트
│   ├── email/                    # 이메일 서비스
│   │   └── sender.ts             # Resend 이메일 발송
│   └── notifications/            # 알림 서비스
│       └── service.ts            # 사용자 알림
│
├── Process/                      # 개발 프로세스 (SAL Grid)
│   ├── S0_Project-SAL-Grid_생성/ # Task Grid 관리
│   ├── S1_개발_준비/              # Stage 1
│   ├── S2_개발-1차/               # Stage 2 (Auth, Forms)
│   ├── S3_개발-2차/               # Stage 3 (Valuation Engines)
│   │   └── Backend_APIs/valuation/engines/  # 5개 평가 엔진
│   │       ├── dcf-engine.ts     # DCF 엔진
│   │       ├── relative-engine.ts # Relative 엔진
│   │       ├── asset-engine.ts   # Asset 엔진
│   │       ├── intrinsic-engine.ts # Intrinsic 엔진
│   │       └── tax-engine.ts     # Tax 엔진
│   ├── S4_개발-3차/               # Stage 4 (External, Crawler)
│   └── S5_개발_마무리/             # Stage 5 (Documentation)
│
├── Valuation_Company/scripts/investment-news-scraper/  # 뉴스 스크래퍼
│   ├── bill-news-tracker-enhanced.js  # 메인 스크립트
│   └── README.md                 # 사용 가이드
│
├── database/                     # DB 스키마
│   └── schema-v4-final.sql       # 41개 테이블 (11 + 30)
│
├── docs/                         # 문서
│   ├── architecture.md           # 아키텍처 가이드
│   ├── maintenance-guide.md      # 유지보수 가이드
│   └── troubleshooting.md        # 문제 해결 가이드
│
├── .github/workflows/            # GitHub Actions
│   └── news-collection.yml       # 매일 8am 뉴스 수집
│
├── package.json                  # 의존성
├── tsconfig.json                 # TypeScript 설정
├── tailwind.config.ts            # Tailwind CSS 설정
└── README.md                     # 본 문서
```

---

## 🧪 테스트

### 전체 테스트 실행

```bash
npm test
```

### 단위 테스트

```bash
npm run test:unit
```

### 통합 테스트

```bash
npm run test:integration
```

### E2E 테스트 (Playwright)

```bash
npm run test:e2e
```

### 커버리지 확인

```bash
npm run test:coverage
```

### 테스트 현황

- **총 테스트**: 21개
- **커버리지**: 85%
- **평가 엔진**: 5개 (각 3개 테스트)
- **워크플로우**: 3개 테스트
- **인증**: 3개 테스트

---

## 🚢 배포

### Vercel 배포 (3단계)

#### 1. Vercel 프로젝트 생성

```bash
npm install -g vercel
vercel login
vercel
```

#### 2. 환경 변수 설정

Vercel Dashboard → Settings → Environment Variables에서 `.env.local` 내용 추가:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `CRON_SECRET`
- `RESEND_API_KEY`
- `ADMIN_EMAIL`

#### 3. 배포

```bash
vercel --prod
```

### Vercel Cron Jobs 설정

`vercel.json` 파일에 다음 내용 추가:

```json
{
  "crons": [
    {
      "path": "/api/cron/collect-news",
      "schedule": "0 23 * * *"
    }
  ]
}
```

**주의**: Vercel Cron은 UTC 기준이므로 `0 23 * * *` = KST 8am

### GitHub Actions 자동 배포

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

---

## 📚 문서

- **[아키텍처 가이드](docs/architecture.md)** - 시스템 아키텍처, 기술 스택, 디자인 패턴
- **[유지보수 가이드](docs/maintenance-guide.md)** - 일상 점검, DB 관리, 크롤러 관리
- **[문제 해결 가이드](docs/troubleshooting.md)** - 빌드/런타임/DB/인증/크롤러 에러 해결

---

## 🔒 보안

### Row Level Security (RLS)

Supabase에서 모든 테이블에 RLS 정책 적용:

```sql
-- users 테이블: 본인만 조회/수정 가능
CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = user_id);

-- projects 테이블: 본인 또는 담당 회계사만 조회 가능
CREATE POLICY "Users can view own projects"
ON projects FOR SELECT
USING (auth.uid() = user_id OR auth.uid() = accountant_id);

-- documents 테이블: 프로젝트 참여자만 조회 가능
CREATE POLICY "Project participants can view documents"
ON dcf_documents FOR SELECT
USING (
  project_id IN (
    SELECT project_id FROM projects
    WHERE user_id = auth.uid() OR accountant_id = auth.uid()
  )
);
```

### CORS 설정

`lib/supabase/client.ts`에서 허용된 origin만 접근 가능

### Secrets 관리

- `.env.local`에 민감 정보 저장 (Git 제외)
- Vercel에 환경 변수 등록
- `CRON_SECRET`로 Cron Job API 인증

### HTTPS 강제

`vercel.json`에서 HTTP → HTTPS 리다이렉트

---

## 🤝 기여

### Fork 및 브랜치 생성

```bash
git checkout -b feature/new-valuation-method
```

### 커밋 메시지 규칙

```
feat: 새 기능 추가 (예: feat: Add Tax-Based Valuation)
fix: 버그 수정 (예: fix: DCF terminal value calculation)
docs: 문서 수정 (예: docs: Update README installation steps)
refactor: 코드 리팩토링 (예: refactor: Extract approval point logic)
test: 테스트 추가/수정 (예: test: Add DCF engine unit tests)
chore: 빌드/설정 변경 (예: chore: Update Tailwind config)
```

### Pull Request 프로세스

1. Fork 및 브랜치 생성
2. 변경 사항 커밋
3. 테스트 실행 (`npm test`)
4. PR 생성 (template 참조)
5. 코드 리뷰 대기
6. Merge

---

## 💬 지원

- **이슈 트래커**: https://github.com/SUNWOONGKYU/ValueLink/issues
- **이메일**: wksun999@hanmail.net

---

## 📄 라이선스

MIT License

Copyright (c) 2026 ValueLink

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Built with ❤️ by ValueLink Team**

**Last Updated**: 2026-02-22
