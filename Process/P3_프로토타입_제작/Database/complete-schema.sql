-- ValueLink Complete Database Schema
-- Supabase PostgreSQL 15.x
-- 작성일: 2026-02-05
-- 버전: 1.0

-- ============================================
-- 1. Users 테이블 (프로필)
-- ============================================
-- Note: auth.users는 Supabase가 자동 관리
-- 이 테이블은 추가 프로필 정보 저장

CREATE TABLE IF NOT EXISTS public.users (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'accountant', 'admin', 'investor')),
    phone VARCHAR(20),
    company_name VARCHAR(200),
    position VARCHAR(100),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책: 사용자는 본인 정보만 조회/수정 가능
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = user_id);

-- Index
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_role ON public.users(role);

-- ============================================
-- 2. Projects 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS public.projects (
    project_id VARCHAR(50) PRIMARY KEY,
    user_id UUID REFERENCES public.users(user_id) ON DELETE CASCADE,
    accountant_id UUID REFERENCES public.users(user_id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    -- 상태: draft, submitted, quote_sent, negotiation, contract_signed,
    --       payment_completed, in_progress, completed, delivered, cancelled
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    revenue BIGINT,
    employees INTEGER,
    founded_date DATE,
    valuation_purpose VARCHAR(50),
    -- 목적: investment, ma, succession, ipo, other
    requested_methods TEXT[],
    -- ['dcf', 'relative', 'asset', 'intrinsic', 'tax']
    target_date DATE,
    actual_completion_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Customers can view own projects"
    ON public.projects FOR SELECT
    USING (
        auth.uid() = user_id OR
        auth.uid() = accountant_id OR
        EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "Customers can create projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Customers can update own projects"
    ON public.projects FOR UPDATE
    USING (
        (auth.uid() = user_id AND status IN ('draft', 'submitted')) OR
        auth.uid() = accountant_id OR
        EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin')
    );

-- Index
CREATE INDEX idx_projects_user_id ON public.projects(user_id);
CREATE INDEX idx_projects_accountant_id ON public.projects(accountant_id);
CREATE INDEX idx_projects_status ON public.projects(status);
CREATE INDEX idx_projects_created_at ON public.projects(created_at DESC);

-- ============================================
-- 3. Quotes 테이블 (견적)
-- ============================================
CREATE TABLE IF NOT EXISTS public.quotes (
    quote_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    base_fee BIGINT NOT NULL,
    discount_rate FLOAT DEFAULT 0,
    final_fee BIGINT NOT NULL,
    payment_terms TEXT,
    delivery_days INTEGER,
    valid_until DATE,
    status VARCHAR(20) DEFAULT 'sent',
    -- 상태: sent, accepted, rejected, expired
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.quotes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view quotes for their projects"
    ON public.quotes FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = quotes.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

-- Index
CREATE INDEX idx_quotes_project_id ON public.quotes(project_id);

-- ============================================
-- 4. Negotiations 테이블 (협상)
-- ============================================
CREATE TABLE IF NOT EXISTS public.negotiations (
    negotiation_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(user_id),
    request_type VARCHAR(50),
    -- 유형: price_discount, deadline_extension, method_change, other
    details TEXT NOT NULL,
    admin_response TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    -- 상태: pending, accepted, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    responded_at TIMESTAMP WITH TIME ZONE
);

-- RLS 정책
ALTER TABLE public.negotiations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view negotiations for their projects"
    ON public.negotiations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = negotiations.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

-- Index
CREATE INDEX idx_negotiations_project_id ON public.negotiations(project_id);
CREATE INDEX idx_negotiations_status ON public.negotiations(status);

-- ============================================
-- 5. Documents 테이블 (서류)
-- ============================================
CREATE TABLE IF NOT EXISTS public.documents (
    document_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    -- Supabase Storage 경로
    file_size BIGINT,
    -- bytes
    file_type VARCHAR(50),
    -- pdf, xlsx, docx, jpg, png
    description TEXT,
    upload_status VARCHAR(20) DEFAULT 'uploaded',
    -- 상태: uploaded, processing, processed, error
    extracted_data JSONB,
    -- AI가 추출한 데이터
    uploaded_by UUID REFERENCES public.users(user_id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view documents for their projects"
    ON public.documents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = documents.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

CREATE POLICY "Users can upload documents to their projects"
    ON public.documents FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = project_id
            AND p.user_id = auth.uid()
        )
    );

-- Index
CREATE INDEX idx_documents_project_id ON public.documents(project_id);
CREATE INDEX idx_documents_uploaded_at ON public.documents(uploaded_at DESC);

-- ============================================
-- 6. Approval Points 테이블 (승인 포인트)
-- ============================================
CREATE TABLE IF NOT EXISTS public.approval_points (
    approval_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    point_number INTEGER NOT NULL,
    -- 1 ~ 22
    category VARCHAR(50) NOT NULL,
    -- revenue_growth, operating_margin, wacc, peer_multiple, etc.
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scenarios JSONB NOT NULL,
    -- [{label: 'optimistic', value: 0.25, description: '...', is_recommended: false}, ...]
    selected_scenario VARCHAR(20),
    -- optimistic, neutral, conservative
    status VARCHAR(20) DEFAULT 'pending',
    -- 상태: pending, approved, rejected
    accountant_note TEXT,
    accountant_id UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- RLS 정책
ALTER TABLE public.approval_points ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view approval points for their projects"
    ON public.approval_points FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = approval_points.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

CREATE POLICY "Accountants can update approval points"
    ON public.approval_points FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = approval_points.project_id
            AND p.accountant_id = auth.uid()
        ) OR
        EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin')
    );

-- Index
CREATE INDEX idx_approval_points_project_id ON public.approval_points(project_id);
CREATE INDEX idx_approval_points_status ON public.approval_points(status);

-- ============================================
-- 7. Valuation Results 테이블 (평가 결과)
-- ============================================
CREATE TABLE IF NOT EXISTS public.valuation_results (
    result_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    method VARCHAR(50) NOT NULL,
    -- dcf, relative, asset, intrinsic, tax
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    calculation_details JSONB,
    -- 상세 계산 내역 (JSON)
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.valuation_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view valuation results for their projects"
    ON public.valuation_results FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = valuation_results.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

-- Index
CREATE INDEX idx_valuation_results_project_id ON public.valuation_results(project_id);
CREATE INDEX idx_valuation_results_method ON public.valuation_results(method);

-- ============================================
-- 8. Drafts 테이블 (초안)
-- ============================================
CREATE TABLE IF NOT EXISTS public.drafts (
    draft_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    -- Markdown 형식
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    -- 상태: draft, submitted, approved, rejected
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view drafts for their projects"
    ON public.drafts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = drafts.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

-- Index
CREATE INDEX idx_drafts_project_id ON public.drafts(project_id);
CREATE INDEX idx_drafts_version ON public.drafts(version);

-- ============================================
-- 9. Revisions 테이블 (수정 요청)
-- ============================================
CREATE TABLE IF NOT EXISTS public.revisions (
    revision_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    draft_id INTEGER REFERENCES public.drafts(draft_id) ON DELETE CASCADE,
    revision_type VARCHAR(50) NOT NULL,
    -- content_change, data_correction, calculation_error, other
    section VARCHAR(100),
    -- 수정 요청 섹션
    details TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    -- 상태: pending, in_progress, completed, rejected
    requested_by UUID REFERENCES public.users(user_id),
    assigned_to UUID REFERENCES public.users(user_id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- RLS 정책
ALTER TABLE public.revisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view revisions for their projects"
    ON public.revisions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = revisions.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

-- Index
CREATE INDEX idx_revisions_project_id ON public.revisions(project_id);
CREATE INDEX idx_revisions_draft_id ON public.revisions(draft_id);
CREATE INDEX idx_revisions_status ON public.revisions(status);

-- ============================================
-- 10. Reports 테이블 (최종 보고서)
-- ============================================
CREATE TABLE IF NOT EXISTS public.reports (
    report_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    report_url VARCHAR(1000) NOT NULL,
    -- Supabase Storage 경로
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    issued_by UUID REFERENCES public.users(user_id),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view reports for their projects"
    ON public.reports FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = reports.project_id
            AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

-- Index
CREATE INDEX idx_reports_project_id ON public.reports(project_id);

-- ============================================
-- 11. Investment Tracker 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS public.investment_tracker (
    investment_id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES public.users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    investment_stage VARCHAR(50),
    -- seed, series_a, series_b, series_c, pre_ipo
    investment_amount BIGINT NOT NULL,
    equity_percentage FLOAT,
    investment_date DATE NOT NULL,
    current_value BIGINT,
    -- 현재 평가액 (예상)
    exit_date DATE,
    exit_amount BIGINT,
    status VARCHAR(20) DEFAULT 'active',
    -- 상태: active, exited, failed
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.investment_tracker ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own investments"
    ON public.investment_tracker FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own investments"
    ON public.investment_tracker FOR ALL
    USING (auth.uid() = user_id);

-- Index
CREATE INDEX idx_investment_tracker_user_id ON public.investment_tracker(user_id);
CREATE INDEX idx_investment_tracker_status ON public.investment_tracker(status);

-- ============================================
-- 12. Feedbacks 테이블 (피드백)
-- ============================================
CREATE TABLE IF NOT EXISTS public.feedbacks (
    feedback_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES public.projects(project_id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(user_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책
ALTER TABLE public.feedbacks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view feedbacks for their projects"
    ON public.feedbacks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = feedbacks.project_id
            AND (p.user_id = auth.uid()
                OR EXISTS (SELECT 1 FROM public.users WHERE user_id = auth.uid() AND role = 'admin'))
        )
    );

CREATE POLICY "Users can create feedbacks for their projects"
    ON public.feedbacks FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.project_id = project_id
            AND p.user_id = auth.uid()
        )
    );

-- Index
CREATE INDEX idx_feedbacks_project_id ON public.feedbacks(project_id);
CREATE INDEX idx_feedbacks_rating ON public.feedbacks(rating);

-- ============================================
-- Triggers: updated_at 자동 갱신
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_investment_tracker_updated_at BEFORE UPDATE ON public.investment_tracker
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Views: 편리한 조회
-- ============================================

-- 프로젝트 전체 정보 View
CREATE OR REPLACE VIEW project_full_info AS
SELECT
    p.project_id,
    p.status,
    p.company_name_kr,
    p.valuation_purpose,
    p.requested_methods,
    u.name AS customer_name,
    u.email AS customer_email,
    acc.name AS accountant_name,
    q.final_fee,
    q.status AS quote_status,
    COUNT(DISTINCT d.document_id) AS document_count,
    COUNT(DISTINCT ap.approval_id) AS approval_point_count,
    p.created_at,
    p.updated_at
FROM public.projects p
LEFT JOIN public.users u ON p.user_id = u.user_id
LEFT JOIN public.users acc ON p.accountant_id = acc.user_id
LEFT JOIN public.quotes q ON p.project_id = q.project_id
LEFT JOIN public.documents d ON p.project_id = d.project_id
LEFT JOIN public.approval_points ap ON p.project_id = ap.project_id
GROUP BY p.project_id, u.name, u.email, acc.name, q.final_fee, q.status;

-- 통계 View (관리자용)
CREATE OR REPLACE VIEW admin_statistics AS
SELECT
    (SELECT COUNT(*) FROM public.projects) AS total_projects,
    (SELECT COUNT(*) FROM public.projects WHERE status = 'in_progress') AS in_progress_projects,
    (SELECT COUNT(*) FROM public.projects WHERE status = 'completed') AS completed_projects,
    (SELECT COUNT(*) FROM public.users WHERE role = 'customer') AS total_customers,
    (SELECT COUNT(*) FROM public.users WHERE role = 'accountant') AS total_accountants,
    (SELECT SUM(final_fee) FROM public.quotes WHERE status = 'accepted') AS total_revenue,
    (SELECT AVG(rating) FROM public.feedbacks) AS average_rating;

-- ============================================
-- Sample Data (테스트용)
-- ============================================

-- Admin 사용자 생성 (주의: auth.users에 먼저 생성 필요)
-- INSERT INTO public.users (user_id, email, name, role)
-- VALUES ('00000000-0000-0000-0000-000000000000', 'admin@valuation.ai.kr', '관리자', 'admin');

-- ============================================
-- Backup & Migration
-- ============================================

-- 백업 명령어 (pg_dump)
-- pg_dump -h db.xxx.supabase.co -U postgres -d postgres -t public.* -F c -f valuelink_backup.dump

-- 복원 명령어 (pg_restore)
-- pg_restore -h db.xxx.supabase.co -U postgres -d postgres -c valuelink_backup.dump

-- ============================================
-- 완료
-- ============================================
-- 총 12개 테이블 생성 완료
-- RLS 정책 적용 완료
-- Index 생성 완료
-- Trigger 생성 완료
-- View 생성 완료
