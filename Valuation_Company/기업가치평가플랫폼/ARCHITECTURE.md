# 기업가치평가 플랫폼 아키텍처

**프로젝트**: 기업가치평가 플랫폼 (Valuation Platform)
**버전**: 2.0
**작성일**: 2025-10-18
**업데이트**: Vercel + Supabase 아키텍처 확정

---

## 🏗️ 전체 아키텍처

### 핵심 스택

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 (User)                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Cloudflare CDN (선택)                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               Vercel (Frontend + API Routes)                 │
│  • Next.js 14+ (App Router)                                  │
│  • React 18+                                                 │
│  • Tailwind CSS + shadcn/ui                                  │
│  • TypeScript                                                │
│  • API Routes: /api/valuation/*                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Supabase (BaaS)                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │  PostgreSQL Database                                │     │
│  │  • companies 테이블                                 │     │
│  │  • valuations 테이블                                │     │
│  │  • documents 테이블                                 │     │
│  │  • approval_points 테이블                           │     │
│  │  • report_logs 테이블                               │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Supabase Auth                                      │     │
│  │  • Email/Password 인증                              │     │
│  │  • OAuth (Google, Kakao)                            │     │
│  │  • JWT 토큰 관리                                    │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Supabase Storage                                   │     │
│  │  • 재무제표 PDF 업로드                              │     │
│  │  • 평가 보고서 PDF 저장                             │     │
│  │  • 최대 100MB 파일 지원                             │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Supabase Edge Functions (Deno)                    │     │
│  │  • 5가지 평가 엔진 (DCF, 상대가치, NAV, DDM, 청산)  │     │
│  │  • 문서 파싱 엔진 (PDF → JSON)                      │     │
│  │  • 보고서 생성 엔진 (80페이지 PDF)                  │     │
│  │  • 이메일 발송 (Resend/SendGrid)                    │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Row Level Security (RLS)                          │     │
│  │  • 사용자별 데이터 격리                             │     │
│  │  • 멀티 테넌시 (company_id 기반)                    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  외부 API 통합                               │
│  • Claude API (60%) - 주 평가 엔진                           │
│  • Gemini API (20%) - 검증 및 리뷰                           │
│  • ChatGPT API (20%) - 보조 분석                             │
│  • DART API (한국 상장사 재무제표)                           │
│  • VirusTotal API (파일 스캔)                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 기술 스택 상세

### Frontend (Vercel 배포)

#### Framework & Libraries
```json
{
  "framework": "Next.js 14+",
  "language": "TypeScript 5+",
  "styling": "Tailwind CSS 3+",
  "ui-components": "shadcn/ui",
  "state-management": "Zustand 또는 React Query",
  "forms": "React Hook Form + Zod",
  "charts": "Recharts 또는 Chart.js",
  "file-upload": "react-dropzone"
}
```

#### 주요 페이지
- `/` - 랜딩 페이지 (히어로, 가격표)
- `/dashboard` - 사용자 대시보드
- `/valuation/new` - 신규 평가 시작
- `/valuation/[id]` - 평가 결과 조회
- `/approval/[id]` - 인간 승인 대시보드 (22개 판단 포인트)
- `/reports` - 보고서 목록

---

### Backend (Supabase)

#### 1. Supabase Edge Functions (Deno Runtime)

**평가 엔진 Functions**:
```
supabase/functions/
├── dcf-valuation/              # DCF 엔진
├── relative-valuation/         # 상대가치 엔진
├── asset-valuation/            # NAV 엔진
├── ddm-valuation/              # 배당할인 엔진
├── liquidation-valuation/      # 청산가치 엔진
├── parse-documents/            # PDF/Excel 파싱
├── generate-report/            # 80페이지 보고서 생성
└── send-email/                 # 이메일 발송
```

**Edge Functions 특징**:
- TypeScript/JavaScript 또는 Python 지원 (Deno Runtime)
- 자동 스케일링
- 글로벌 CDN 배포
- JWT 인증 내장

**Python 평가 엔진 통합**:
기존 `backend/app/services/dcf_engine.py`를 Edge Functions로 마이그레이션:
```typescript
// supabase/functions/dcf-valuation/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { fcff_projections, wacc, terminal_growth, ... } = await req.json()

  // Python 엔진 로직을 TypeScript로 재구현 또는
  // Deno에서 Python subprocess 실행
  const result = calculateDCF({ fcff_projections, wacc, ... })

  return new Response(JSON.stringify(result), {
    headers: { "Content-Type": "application/json" }
  })
})
```

#### 2. PostgreSQL Database (Supabase)

**테이블 스키마**:

```sql
-- 회사 정보
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  industry TEXT,
  stock_code TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id)
);

-- 평가 프로젝트
CREATE TABLE valuations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id),
  valuation_date DATE NOT NULL,
  method TEXT NOT NULL, -- 'DCF', 'Relative', 'NAV', 'DDM', 'Liquidation'
  status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'completed'
  result JSONB, -- 평가 결과
  created_at TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id)
);

-- 문서 업로드
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  valuation_id UUID REFERENCES valuations(id),
  file_name TEXT NOT NULL,
  file_url TEXT NOT NULL, -- Supabase Storage URL
  file_size BIGINT,
  parsing_status TEXT DEFAULT 'pending',
  parsed_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인간 승인 포인트 (22개)
CREATE TABLE approval_points (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  valuation_id UUID REFERENCES valuations(id),
  point_name TEXT NOT NULL, -- 'wacc_rate', 'terminal_growth', etc.
  category TEXT NOT NULL, -- '재무', '법률', '시장', '기술'
  ai_value JSONB, -- AI가 계산한 값
  human_decision TEXT, -- 'approved', 'rejected', 'custom'
  custom_value JSONB, -- 사용자가 수정한 값
  created_at TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id)
);

-- 보고서 생성 로그
CREATE TABLE report_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  valuation_id UUID REFERENCES valuations(id),
  report_url TEXT, -- Supabase Storage URL
  generation_time INTERVAL,
  status TEXT DEFAULT 'generating',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. Row Level Security (RLS)

**사용자별 데이터 격리**:
```sql
-- companies 테이블 RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own companies"
  ON companies FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own companies"
  ON companies FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- valuations 테이블 RLS
ALTER TABLE valuations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own valuations"
  ON valuations FOR SELECT
  USING (auth.uid() = user_id);

-- approval_points 테이블 RLS
ALTER TABLE approval_points ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only approve own valuations"
  ON approval_points FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM valuations
      WHERE valuations.id = approval_points.valuation_id
      AND valuations.user_id = auth.uid()
    )
  );
```

#### 4. Supabase Storage

**버킷 구조**:
```
supabase-storage/
├── documents/               # 업로드 재무제표 (Private)
│   ├── {user_id}/
│   │   └── {valuation_id}/
│   │       ├── financial_statements.pdf
│   │       └── audit_report.pdf
└── reports/                 # 생성된 평가 보고서 (Private)
    ├── {user_id}/
    │   └── {valuation_id}/
    │       └── valuation_report_80pages.pdf
```

**Storage 정책**:
```sql
-- documents 버킷: 본인 파일만 업로드/조회
CREATE POLICY "Users can upload own documents"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view own documents"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);
```

#### 5. Supabase Auth

**지원 인증 방식**:
- 이메일/비밀번호
- Google OAuth
- Kakao OAuth
- JWT 자동 관리
- Refresh Token 순환

**사용자 역할**:
```typescript
// auth.users 메타데이터
{
  "role": "user" | "professional_valuator" | "admin",
  "company_id": "uuid" // 멀티 테넌시
}
```

---

### Deployment & Infrastructure

#### Vercel (Frontend + API Routes)

**설정**:
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase-service-key",
    "CLAUDE_API_KEY": "@claude-api-key"
  }
}
```

**CI/CD (GitHub Actions)**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

#### Supabase (Backend + Database)

**프로젝트 설정**:
- Region: Asia Northeast (Seoul 또는 Tokyo)
- Plan: Pro (프로덕션) 또는 Free (개발)
- Database: PostgreSQL 15+
- Storage: 100GB (업로드 파일 + 보고서)

**Edge Functions 배포**:
```bash
# Edge Function 배포
supabase functions deploy dcf-valuation
supabase functions deploy relative-valuation
supabase functions deploy parse-documents
supabase functions deploy generate-report
```

---

## 🔄 데이터 흐름

### 1. 신규 평가 생성 Flow

```
[사용자] → [Vercel: /valuation/new 페이지]
    ↓
[재무제표 업로드] → [Supabase Storage: documents/]
    ↓
[Supabase Edge Function: parse-documents]
    ↓ (PDF → JSON)
[PostgreSQL: documents 테이블에 parsed_data 저장]
    ↓
[Vercel: 입력 폼에 parsed_data 자동 채우기]
    ↓ (사용자 확인/수정)
[Supabase Edge Function: dcf-valuation (또는 다른 엔진)]
    ↓
[PostgreSQL: valuations 테이블에 결과 저장]
    ↓
[22개 판단 포인트 생성] → [approval_points 테이블]
    ↓
[Vercel: /approval/[id] 대시보드로 이동]
```

### 2. 인간 승인 Flow

```
[사용자] → [Vercel: /approval/[id] 대시보드]
    ↓
[22개 판단 포인트 UI 표시]
    ↓ (각 포인트마다)
[승인 / 거부 / 커스텀 선택]
    ↓
[PostgreSQL: approval_points 업데이트]
    ↓ (모든 포인트 완료 시)
[Supabase Edge Function: generate-report]
    ↓ (80페이지 PDF 생성)
[Supabase Storage: reports/ 저장]
    ↓
[PostgreSQL: report_logs 테이블 업데이트]
    ↓
[Supabase Edge Function: send-email]
    ↓
[사용자에게 완료 이메일 발송]
```

---

## 🔐 보안 아키텍처

### 1. 인증/인가
- Supabase Auth (JWT 기반)
- Row Level Security (RLS)
- API 키 암호화 (Vercel Environment Variables)

### 2. 데이터 보호
- 재무 데이터 at-rest 암호화 (PostgreSQL 기본)
- HTTPS 강제 (Vercel + Supabase 기본)
- 파일 업로드 검증 (VirusTotal API)

### 3. API 보안
- Rate Limiting (Supabase Edge Functions)
- CORS 정책 (Vercel API Routes)
- CSP (Content Security Policy)

---

## 📊 모니터링 & 로깅

### Sentry (에러 추적)
- Frontend 에러 모니터링
- Edge Functions 에러 추적
- 사용자 세션 리플레이

### Supabase Dashboard
- Database 쿼리 성능
- Edge Functions 로그
- Storage 사용량

### Vercel Analytics
- 페이지 성능 (Web Vitals)
- 트래픽 분석
- API Route 응답 시간

---

## 🚀 스케일링 전략

### Vercel (자동)
- Serverless Functions 자동 스케일링
- Global CDN 배포
- Edge Caching

### Supabase (설정 필요)
- Database Connection Pooling (PgBouncer)
- Read Replicas (프로덕션 플랜)
- Edge Functions 자동 스케일링

---

## 💰 예상 비용 (월간)

### 개발 단계
- Vercel: $0 (Hobby Plan)
- Supabase: $0 (Free Plan)
- **총**: $0/월

### 프로덕션 (사용자 100명 기준)
- Vercel: $20 (Pro Plan)
- Supabase: $25 (Pro Plan)
- Sentry: $26 (Team Plan)
- Cloudflare: $0 (Free Plan)
- **총**: ~$71/월

### 프로덕션 (사용자 1,000명 기준)
- Vercel: $20
- Supabase: $599 (Team Plan, 확장 필요)
- Sentry: $80
- Resend (이메일): $20
- **총**: ~$719/월

---

## 📝 환경 변수

### Vercel (.env.local)
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI APIs
CLAUDE_API_KEY=your-claude-api-key
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Monitoring
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Email
RESEND_API_KEY=your-resend-api-key
```

### Supabase Edge Functions
```env
CLAUDE_API_KEY=your-claude-api-key
VIRUSTOTAL_API_KEY=your-virustotal-api-key
```

---

## 🔗 참고 자료

- **Vercel 문서**: https://vercel.com/docs
- **Supabase 문서**: https://supabase.com/docs
- **Supabase Edge Functions**: https://supabase.com/docs/guides/functions
- **Next.js 14 문서**: https://nextjs.org/docs

---

**버전**: 2.0 (Vercel + Supabase 확정)
**작성일**: 2025-10-18
**프로젝트**: 기업가치평가 플랫폼
