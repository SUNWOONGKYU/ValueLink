# S1D1: Database Schema & RLS Policies

## Task 정보

- **Task ID**: S1D1
- **Task Name**: 데이터베이스 스키마 및 RLS 정책 정의
- **Stage**: S1 (Development Setup - 개발 준비)
- **Area**: D (Database)
- **Dependencies**: 없음
- **Task Agent**: database-specialist
- **Verification Agent**: database-specialist

---

## Task 목표

Supabase PostgreSQL에서 ValueLink 플랫폼의 12개 테이블 정의, Row Level Security (RLS) 정책 설정, 트리거 생성

---

## 상세 지시사항

### 1. 데이터베이스 스키마 정의

**파일**: `database/schema.sql`

#### 1.1 Users 테이블 (프로필 및 역할)

```sql
-- 사용자 프로필 테이블
CREATE TABLE public.users (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone TEXT,
  company_name TEXT,
  role TEXT NOT NULL CHECK (role IN ('customer', 'accountant', 'admin', 'investor', 'partner', 'supporter')),
  profile_image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_role ON public.users(role);
```

#### 1.2 Projects 테이블 (프로젝트 마스터)

```sql
-- 프로젝트 마스터 테이블
CREATE TABLE public.projects (
  project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  accountant_id UUID REFERENCES public.users(user_id) ON DELETE SET NULL,
  project_name TEXT NOT NULL,
  valuation_method TEXT NOT NULL CHECK (valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'quoted', 'negotiating', 'in_progress', 'draft_ready', 'revision_requested', 'completed', 'cancelled')),
  current_step INT DEFAULT 1 CHECK (current_step BETWEEN 1 AND 14),
  deadline DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_user ON public.projects(user_id);
CREATE INDEX idx_projects_accountant ON public.projects(accountant_id);
CREATE INDEX idx_projects_status ON public.projects(status);
```

#### 1.3 Quotes 테이블 (견적)

```sql
-- 견적 테이블
CREATE TABLE public.quotes (
  quote_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  amount DECIMAL(12, 2) NOT NULL,
  deposit_amount DECIMAL(12, 2) NOT NULL,
  balance_amount DECIMAL(12, 2) NOT NULL,
  delivery_days INT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_quotes_project ON public.quotes(project_id);
```

#### 1.4 Negotiations 테이블 (협상)

```sql
-- 협상 테이블
CREATE TABLE public.negotiations (
  negotiation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  quote_id UUID NOT NULL REFERENCES public.quotes(quote_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  negotiation_type TEXT NOT NULL CHECK (negotiation_type IN ('price', 'deadline', 'both')),
  proposed_amount DECIMAL(12, 2),
  proposed_deadline DATE,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_negotiations_project ON public.negotiations(project_id);
CREATE INDEX idx_negotiations_quote ON public.negotiations(quote_id);
```

#### 1.5 Documents 테이블 (파일 업로드)

```sql
-- 파일 업로드 테이블
CREATE TABLE public.documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL, -- Supabase Storage 경로
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_type TEXT NOT NULL CHECK (document_type IN ('financial_statement', 'business_plan', 'contract', 'other')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_project ON public.documents(project_id);
```

#### 1.6 Approval Points 테이블 (22개 승인 포인트)

```sql
-- 승인 포인트 테이블 (22개)
CREATE TABLE public.approval_points (
  approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  step_number INT NOT NULL CHECK (step_number BETWEEN 1 AND 22),
  step_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'skipped')),
  approved_by UUID REFERENCES public.users(user_id) ON DELETE SET NULL,
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, step_number)
);

CREATE INDEX idx_approval_points_project ON public.approval_points(project_id);
CREATE INDEX idx_approval_points_status ON public.approval_points(status);
```

#### 1.7 Valuation Results 테이블 (5개 방법 결과)

```sql
-- 평가 결과 테이블
CREATE TABLE public.valuation_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  valuation_method TEXT NOT NULL CHECK (valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax')),
  enterprise_value DECIMAL(20, 2),
  equity_value DECIMAL(20, 2),
  value_per_share DECIMAL(20, 2),
  calculation_data JSONB, -- 계산 상세 데이터
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_valuation_results_project ON public.valuation_results(project_id);
```

#### 1.8 Drafts 테이블 (초안)

```sql
-- 초안 테이블
CREATE TABLE public.drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  content TEXT NOT NULL, -- Markdown 형식
  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_drafts_project ON public.drafts(project_id);
CREATE INDEX idx_drafts_version ON public.drafts(project_id, version);
```

#### 1.9 Revisions 테이블 (수정 요청)

```sql
-- 수정 요청 테이블
CREATE TABLE public.revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL, -- 수정할 섹션
  comment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_revisions_draft ON public.revisions(draft_id);
CREATE INDEX idx_revisions_status ON public.revisions(status);
```

#### 1.10 Reports 테이블 (최종 보고서)

```sql
-- 최종 보고서 테이블
CREATE TABLE public.reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL, -- Supabase Storage 경로 (PDF)
  file_size BIGINT NOT NULL,
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reports_project ON public.reports(project_id);
```

#### 1.11 Investment Tracker 테이블 (Deal 뉴스)

```sql
-- 투자 뉴스 테이블
CREATE TABLE public.investment_tracker (
  deal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT NOT NULL,
  industry TEXT,
  investment_stage TEXT,
  investor TEXT,
  amount DECIMAL(15, 2),
  location TEXT,
  employee_count INT,
  news_url TEXT,
  news_title TEXT NOT NULL,
  news_content TEXT,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_investment_tracker_company ON public.investment_tracker(company_name);
CREATE INDEX idx_investment_tracker_published ON public.investment_tracker(published_at DESC);
```

#### 1.12 Feedbacks 테이블 (평가)

```sql
-- 피드백 테이블
CREATE TABLE public.feedbacks (
  feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_feedbacks_project ON public.feedbacks(project_id);
CREATE INDEX idx_feedbacks_rating ON public.feedbacks(rating);
```

### 2. Row Level Security (RLS) 정책

**파일**: `database/rls-policies.sql`

```sql
-- RLS 활성화
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.negotiations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.approval_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.valuation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investment_tracker ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedbacks ENABLE ROW LEVEL SECURITY;

-- Users 정책: 본인 프로필만 조회/수정
CREATE POLICY "Users can view own profile"
ON public.users FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
ON public.users FOR UPDATE
USING (auth.uid() = user_id);

-- Projects 정책: 본인 프로젝트 + 담당 회계사 + 관리자 접근
CREATE POLICY "Users can view own projects"
ON public.projects FOR SELECT
USING (
  auth.uid() = user_id OR
  auth.uid() = accountant_id OR
  EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin')
);

CREATE POLICY "Users can create projects"
ON public.projects FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects"
ON public.projects FOR UPDATE
USING (
  auth.uid() = user_id OR
  auth.uid() = accountant_id OR
  EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin')
);

-- Quotes 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view quotes for accessible projects"
ON public.quotes FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = quotes.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Negotiations 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view negotiations for accessible projects"
ON public.negotiations FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = negotiations.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create negotiations"
ON public.negotiations FOR INSERT
WITH CHECK (auth.uid() = requested_by);

-- Documents 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view documents for accessible projects"
ON public.documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = documents.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can upload documents"
ON public.documents FOR INSERT
WITH CHECK (auth.uid() = uploaded_by);

-- Approval Points 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view approval points for accessible projects"
ON public.approval_points FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = approval_points.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Accountants and admins can update approval points"
ON public.approval_points FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.projects p, public.users u
    WHERE p.project_id = approval_points.project_id
    AND u.user_id = auth.uid()
    AND (p.accountant_id = auth.uid() OR u.role = 'admin')
  )
);

-- Valuation Results 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view valuation results for accessible projects"
ON public.valuation_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = valuation_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Drafts 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view drafts for accessible projects"
ON public.drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Revisions 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view revisions for accessible projects"
ON public.revisions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.drafts d, public.projects p
    WHERE d.draft_id = revisions.draft_id
    AND p.project_id = d.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create revisions"
ON public.revisions FOR INSERT
WITH CHECK (auth.uid() = requested_by);

-- Reports 정책: 프로젝트 접근 가능한 사용자만
CREATE POLICY "Users can view reports for accessible projects"
ON public.reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Investment Tracker 정책: 모든 인증된 사용자 읽기 가능
CREATE POLICY "Authenticated users can view investment tracker"
ON public.investment_tracker FOR SELECT
TO authenticated
USING (true);

-- Feedbacks 정책: 본인 피드백만 조회/생성
CREATE POLICY "Users can view own feedbacks"
ON public.feedbacks FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create feedbacks"
ON public.feedbacks FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

### 3. 트리거 (updated_at 자동 갱신)

**파일**: `database/triggers.sql`

```sql
-- updated_at 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 각 테이블에 트리거 생성
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON public.projects
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotes_updated_at
BEFORE UPDATE ON public.quotes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_negotiations_updated_at
BEFORE UPDATE ON public.negotiations
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_points_updated_at
BEFORE UPDATE ON public.approval_points
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_valuation_results_updated_at
BEFORE UPDATE ON public.valuation_results
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_drafts_updated_at
BEFORE UPDATE ON public.drafts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_revisions_updated_at
BEFORE UPDATE ON public.revisions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `database/schema.sql` | 12개 테이블 정의 | ~300줄 |
| `database/rls-policies.sql` | RLS 정책 설정 | ~200줄 |
| `database/triggers.sql` | updated_at 트리거 | ~50줄 |

**총 파일 수**: 3개
**총 라인 수**: ~550줄

---

## 기술 스택

- **Database**: PostgreSQL 15 (Supabase)
- **Features**: Row Level Security, Triggers, JSONB

---

## 완료 기준

### 필수 (Must Have)
- [ ] 12개 테이블 모두 생성 완료
- [ ] 모든 테이블에 RLS 정책 적용
- [ ] updated_at 트리거 모든 테이블에 적용
- [ ] 인덱스 생성 완료
- [ ] SQL 문법 에러 없음

### 검증 (Verification)
- [ ] 테이블 생성 확인: `SELECT * FROM information_schema.tables WHERE table_schema = 'public'`
- [ ] RLS 활성화 확인: 각 테이블의 RLS 정책 테스트
- [ ] 트리거 작동 확인: UPDATE 실행 후 updated_at 자동 갱신

### 권장 (Nice to Have)
- [ ] 외래 키 제약 조건 검증
- [ ] CHECK 제약 조건 검증
- [ ] JSONB 필드 구조 문서화

---

## 참조

### 기존 프로토타입
- `Process/P3_프로토타입_제작/Database/complete-schema.sql` (기존 스키마 참조)

### Supabase 공식 문서
- RLS: https://supabase.com/docs/guides/auth/row-level-security
- Triggers: https://supabase.com/docs/guides/database/functions

### 관련 Task
- **S1BI1**: Database & Configuration Infrastructure (Supabase 클라이언트 설정)
- **S2BA1**: Valuation Process API (테이블 사용)
- **S2F4**: Role-Based My Page (역할 기반 접근 제어)

---

## 주의사항

1. **외래 키 순서**
   - users 테이블을 먼저 생성 (다른 테이블에서 참조)
   - CASCADE 옵션 주의 (데이터 삭제 시 연쇄 삭제)

2. **RLS 정책 테스트**
   - 각 역할(customer, accountant, admin)별로 접근 권한 테스트 필수
   - `auth.uid()` 함수가 정상 작동하는지 확인

3. **JSONB 필드**
   - `calculation_data` 필드에는 평가 계산 상세 데이터 저장
   - 인덱싱이 필요하면 GIN 인덱스 추가 고려

4. **Decimal 정밀도**
   - 금액 필드는 DECIMAL(12, 2) 사용 (9,999억원까지, 소수점 2자리)
   - 기업가치는 DECIMAL(20, 2) 사용 (더 큰 금액 지원)

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 3개
**라인 수**: ~550줄

---

**작성일**: 2026-02-05
**작성자**: Claude Code (Sonnet 4.5)
