/**
 * @task S1D1
 * @description Row Level Security (RLS) 정책
 */

-- ============================================
-- RLS 활성화
-- ============================================
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
-- Quotes 정책
-- ============================================
CREATE POLICY "Users can view quotes for accessible projects"
ON public.quotes FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = quotes.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- ============================================
-- Negotiations 정책
-- ============================================
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

-- ============================================
-- Documents 정책
-- ============================================
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

-- ============================================
-- Approval Points 정책
-- ============================================
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

-- ============================================
-- Valuation Results 정책
-- ============================================
CREATE POLICY "Users can view valuation results for accessible projects"
ON public.valuation_results FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = valuation_results.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- ============================================
-- Drafts 정책
-- ============================================
CREATE POLICY "Users can view drafts for accessible projects"
ON public.drafts FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = drafts.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- ============================================
-- Revisions 정책
-- ============================================
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

-- ============================================
-- Reports 정책
-- ============================================
CREATE POLICY "Users can view reports for accessible projects"
ON public.reports FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.project_id = reports.project_id
    AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid() OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
  )
);

-- ============================================
-- Investment Tracker 정책
-- ============================================
CREATE POLICY "Authenticated users can view investment tracker"
ON public.investment_tracker FOR SELECT
TO authenticated
USING (true);

-- ============================================
-- Feedbacks 정책
-- ============================================
CREATE POLICY "Users can view own feedbacks"
ON public.feedbacks FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create feedbacks"
ON public.feedbacks FOR INSERT
WITH CHECK (auth.uid() = user_id);
