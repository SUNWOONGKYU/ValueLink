/**
 * @task S1D1
 * @description ValueLink 데이터베이스 스키마 (12개 테이블)
 */

-- ============================================
-- 1. Users 테이블 (프로필 및 역할)
-- ============================================
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

-- ============================================
-- 2. Projects 테이블 (프로젝트 마스터)
-- ============================================
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

-- ============================================
-- 3. Quotes 테이블 (견적)
-- ============================================
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

-- ============================================
-- 4. Negotiations 테이블 (협상)
-- ============================================
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

-- ============================================
-- 5. Documents 테이블 (파일 업로드)
-- ============================================
CREATE TABLE public.documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_type TEXT NOT NULL CHECK (document_type IN ('financial_statement', 'business_plan', 'contract', 'other')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_project ON public.documents(project_id);

-- ============================================
-- 6. Approval Points 테이블 (22개 승인 포인트)
-- ============================================
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

-- ============================================
-- 7. Valuation Results 테이블 (5개 방법 결과)
-- ============================================
CREATE TABLE public.valuation_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  valuation_method TEXT NOT NULL CHECK (valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax')),
  enterprise_value DECIMAL(20, 2),
  equity_value DECIMAL(20, 2),
  value_per_share DECIMAL(20, 2),
  calculation_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_valuation_results_project ON public.valuation_results(project_id);

-- ============================================
-- 8. Drafts 테이블 (초안)
-- ============================================
CREATE TABLE public.drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  content TEXT NOT NULL,
  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_drafts_project ON public.drafts(project_id);
CREATE INDEX idx_drafts_version ON public.drafts(project_id, version);

-- ============================================
-- 9. Revisions 테이블 (수정 요청)
-- ============================================
CREATE TABLE public.revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL,
  comment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_revisions_draft ON public.revisions(draft_id);
CREATE INDEX idx_revisions_status ON public.revisions(status);

-- ============================================
-- 10. Reports 테이블 (최종 보고서)
-- ============================================
CREATE TABLE public.reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reports_project ON public.reports(project_id);

-- ============================================
-- 11. Investment Tracker 테이블 (Deal 뉴스)
-- ============================================
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

-- ============================================
-- 12. Feedbacks 테이블 (평가)
-- ============================================
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
