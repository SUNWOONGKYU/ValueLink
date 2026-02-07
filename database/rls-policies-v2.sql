/**
 * ValueLink RLS Policies v2.0
 * Row Level Security 정책 (33개 테이블)
 *
 * 작성일: 2026-02-07
 */

-- ============================================
-- RLS 활성화 - 기본 테이블
-- ============================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 활성화 - Documents 테이블 (5개)
-- ============================================
ALTER TABLE public.dcf_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relative_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intrinsic_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_documents ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 활성화 - Approval Points 테이블 (5개)
-- ============================================
ALTER TABLE public.dcf_approval_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relative_approval_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intrinsic_approval_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_approval_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_approval_points ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 활성화 - Results 테이블 (5개)
-- ============================================
ALTER TABLE public.dcf_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relative_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intrinsic_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_results ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 활성화 - Drafts 테이블 (5개)
-- ============================================
ALTER TABLE public.dcf_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relative_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intrinsic_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_drafts ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 활성화 - Revisions 테이블 (5개)
-- ============================================
ALTER TABLE public.dcf_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relative_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intrinsic_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_revisions ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 활성화 - Reports 테이블 (5개)
-- ============================================
ALTER TABLE public.dcf_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relative_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intrinsic_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_reports ENABLE ROW LEVEL SECURITY;


-- ============================================
-- Users 정책
-- ============================================
CREATE POLICY "Users can view own profile"
ON public.users FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
ON public.users FOR UPDATE
USING (auth.uid() = user_id);


-- ============================================
-- Projects 정책
-- ============================================
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


-- ============================================
-- Payments 정책
-- ============================================
CREATE POLICY "Users can view payments for own projects"
ON public.payments FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = payments.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create payments"
ON public.payments FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = payments.project_id
    AND p.user_id = auth.uid()
  )
);


-- ============================================
-- Documents 정책 (5개 테이블 공통 패턴)
-- ============================================

-- DCF Documents
CREATE POLICY "Users can view dcf documents for accessible projects"
ON public.dcf_documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = dcf_documents.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can upload dcf documents"
ON public.dcf_documents FOR INSERT
WITH CHECK (auth.uid() = uploaded_by);

-- Relative Documents
CREATE POLICY "Users can view relative documents for accessible projects"
ON public.relative_documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = relative_documents.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can upload relative documents"
ON public.relative_documents FOR INSERT
WITH CHECK (auth.uid() = uploaded_by);

-- Intrinsic Documents
CREATE POLICY "Users can view intrinsic documents for accessible projects"
ON public.intrinsic_documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = intrinsic_documents.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can upload intrinsic documents"
ON public.intrinsic_documents FOR INSERT
WITH CHECK (auth.uid() = uploaded_by);

-- Asset Documents
CREATE POLICY "Users can view asset documents for accessible projects"
ON public.asset_documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = asset_documents.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can upload asset documents"
ON public.asset_documents FOR INSERT
WITH CHECK (auth.uid() = uploaded_by);

-- Tax Documents
CREATE POLICY "Users can view tax documents for accessible projects"
ON public.tax_documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = tax_documents.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can upload tax documents"
ON public.tax_documents FOR INSERT
WITH CHECK (auth.uid() = uploaded_by);


-- ============================================
-- Approval Points 정책 (5개 테이블 공통 패턴)
-- ============================================

-- DCF Approval Points
CREATE POLICY "Users can view dcf approval points for accessible projects"
ON public.dcf_approval_points FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = dcf_approval_points.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Accountants can update dcf approval points"
ON public.dcf_approval_points FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.projects p, public.users u
    WHERE p.project_id = dcf_approval_points.project_id
    AND u.user_id = auth.uid()
    AND (p.accountant_id = auth.uid() OR u.role = 'admin')
  )
);

-- Relative Approval Points
CREATE POLICY "Users can view relative approval points for accessible projects"
ON public.relative_approval_points FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = relative_approval_points.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Accountants can update relative approval points"
ON public.relative_approval_points FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.projects p, public.users u
    WHERE p.project_id = relative_approval_points.project_id
    AND u.user_id = auth.uid()
    AND (p.accountant_id = auth.uid() OR u.role = 'admin')
  )
);

-- Intrinsic Approval Points
CREATE POLICY "Users can view intrinsic approval points for accessible projects"
ON public.intrinsic_approval_points FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = intrinsic_approval_points.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Accountants can update intrinsic approval points"
ON public.intrinsic_approval_points FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.projects p, public.users u
    WHERE p.project_id = intrinsic_approval_points.project_id
    AND u.user_id = auth.uid()
    AND (p.accountant_id = auth.uid() OR u.role = 'admin')
  )
);

-- Asset Approval Points
CREATE POLICY "Users can view asset approval points for accessible projects"
ON public.asset_approval_points FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = asset_approval_points.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Accountants can update asset approval points"
ON public.asset_approval_points FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.projects p, public.users u
    WHERE p.project_id = asset_approval_points.project_id
    AND u.user_id = auth.uid()
    AND (p.accountant_id = auth.uid() OR u.role = 'admin')
  )
);

-- Tax Approval Points
CREATE POLICY "Users can view tax approval points for accessible projects"
ON public.tax_approval_points FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = tax_approval_points.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Accountants can update tax approval points"
ON public.tax_approval_points FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM public.projects p, public.users u
    WHERE p.project_id = tax_approval_points.project_id
    AND u.user_id = auth.uid()
    AND (p.accountant_id = auth.uid() OR u.role = 'admin')
  )
);


-- ============================================
-- Results 정책 (5개 테이블 공통 패턴)
-- ============================================

-- DCF Results
CREATE POLICY "Users can view dcf results for accessible projects"
ON public.dcf_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = dcf_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Relative Results
CREATE POLICY "Users can view relative results for accessible projects"
ON public.relative_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = relative_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Intrinsic Results
CREATE POLICY "Users can view intrinsic results for accessible projects"
ON public.intrinsic_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = intrinsic_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Asset Results
CREATE POLICY "Users can view asset results for accessible projects"
ON public.asset_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = asset_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Tax Results
CREATE POLICY "Users can view tax results for accessible projects"
ON public.tax_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = tax_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);


-- ============================================
-- Drafts 정책 (5개 테이블 공통 패턴)
-- ============================================

-- DCF Drafts
CREATE POLICY "Users can view dcf drafts for accessible projects"
ON public.dcf_drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = dcf_drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Relative Drafts
CREATE POLICY "Users can view relative drafts for accessible projects"
ON public.relative_drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = relative_drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Intrinsic Drafts
CREATE POLICY "Users can view intrinsic drafts for accessible projects"
ON public.intrinsic_drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = intrinsic_drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Asset Drafts
CREATE POLICY "Users can view asset drafts for accessible projects"
ON public.asset_drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = asset_drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Tax Drafts
CREATE POLICY "Users can view tax drafts for accessible projects"
ON public.tax_drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = tax_drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);


-- ============================================
-- Revisions 정책 (5개 테이블 공통 패턴)
-- ============================================

-- DCF Revisions
CREATE POLICY "Users can view dcf revisions for accessible projects"
ON public.dcf_revisions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.dcf_drafts d, public.projects p
    WHERE d.draft_id = dcf_revisions.draft_id
    AND p.project_id = d.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create dcf revisions"
ON public.dcf_revisions FOR INSERT
WITH CHECK (auth.uid() = requested_by);

-- Relative Revisions
CREATE POLICY "Users can view relative revisions for accessible projects"
ON public.relative_revisions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.relative_drafts d, public.projects p
    WHERE d.draft_id = relative_revisions.draft_id
    AND p.project_id = d.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create relative revisions"
ON public.relative_revisions FOR INSERT
WITH CHECK (auth.uid() = requested_by);

-- Intrinsic Revisions
CREATE POLICY "Users can view intrinsic revisions for accessible projects"
ON public.intrinsic_revisions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.intrinsic_drafts d, public.projects p
    WHERE d.draft_id = intrinsic_revisions.draft_id
    AND p.project_id = d.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create intrinsic revisions"
ON public.intrinsic_revisions FOR INSERT
WITH CHECK (auth.uid() = requested_by);

-- Asset Revisions
CREATE POLICY "Users can view asset revisions for accessible projects"
ON public.asset_revisions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.asset_drafts d, public.projects p
    WHERE d.draft_id = asset_revisions.draft_id
    AND p.project_id = d.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create asset revisions"
ON public.asset_revisions FOR INSERT
WITH CHECK (auth.uid() = requested_by);

-- Tax Revisions
CREATE POLICY "Users can view tax revisions for accessible projects"
ON public.tax_revisions FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.tax_drafts d, public.projects p
    WHERE d.draft_id = tax_revisions.draft_id
    AND p.project_id = d.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

CREATE POLICY "Users can create tax revisions"
ON public.tax_revisions FOR INSERT
WITH CHECK (auth.uid() = requested_by);


-- ============================================
-- Reports 정책 (5개 테이블 공통 패턴)
-- ============================================

-- DCF Reports
CREATE POLICY "Users can view dcf reports for accessible projects"
ON public.dcf_reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = dcf_reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Relative Reports
CREATE POLICY "Users can view relative reports for accessible projects"
ON public.relative_reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = relative_reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Intrinsic Reports
CREATE POLICY "Users can view intrinsic reports for accessible projects"
ON public.intrinsic_reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = intrinsic_reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Asset Reports
CREATE POLICY "Users can view asset reports for accessible projects"
ON public.asset_reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = asset_reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- Tax Reports
CREATE POLICY "Users can view tax reports for accessible projects"
ON public.tax_reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = tax_reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);
