/**
 * ValueLink Complete Database Schema v4.0 (Final)
 * 전체 41개 테이블
 *
 * 작성일: 2026-02-07
 *
 * 구조:
 * - 기존 테이블: 11개
 * - 평가법별 분리 테이블: 30개 (6종류 x 5평가법)
 *
 * 변경사항 (v3 → v4):
 * - quotes, negotiations 삭제 (불필요)
 * - report_draft_sections, draft_method_status 삭제 (drafts에 통합)
 * - evaluation_requests, project_history 추가 (3단계 분리)
 * - drafts 테이블에 section_X_completed, submitted_at 추가
 */

-- ============================================
-- PART A: 기존 테이블 (11개)
-- ============================================

-- ============================================
-- A1. users - 사용자 프로필
-- ============================================
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

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);

-- ============================================
-- A2. accountants - 회계사
-- ============================================
CREATE TABLE IF NOT EXISTS public.accountants (
    accountant_id VARCHAR(20) PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES public.users(user_id) ON DELETE CASCADE,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    license_issue_date DATE,
    license_issuer VARCHAR(100) DEFAULT '한국공인회계사회',
    education TEXT[],
    career TEXT[],
    specialization VARCHAR(100)[],
    bio TEXT,
    profile_summary TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5.00),
    total_projects INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    max_concurrent_projects INTEGER DEFAULT 3,

    -- 입금 계좌 정보
    bank_name VARCHAR(50),
    bank_account VARCHAR(50),
    account_holder VARCHAR(100),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accountants_user_id ON public.accountants(user_id);
CREATE INDEX IF NOT EXISTS idx_accountants_license ON public.accountants(license_number);

-- ============================================
-- A3. customers - 고객사
-- ============================================
CREATE TABLE IF NOT EXISTS public.customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    user_id UUID REFERENCES public.users(user_id) ON DELETE CASCADE,
    email VARCHAR(100) UNIQUE NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    company_name_en VARCHAR(200),
    ceo_name VARCHAR(50) NOT NULL,
    industry VARCHAR(100),
    founded_date DATE,
    business_number VARCHAR(20) NOT NULL,
    employees INTEGER,
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON public.customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON public.customers(user_id);

-- ============================================
-- A4. evaluation_requests - 평가 요청 (관리자 승인 대기)
-- ============================================
CREATE TABLE IF NOT EXISTS public.evaluation_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,

    -- 기업 정보
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    revenue BIGINT,
    employees INTEGER,
    founded_date DATE,
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 평가 요청 정보
    valuation_purpose VARCHAR(50),
    requested_methods TEXT[],
    target_date DATE,
    requirements TEXT,
    budget_min INTEGER,
    budget_max INTEGER,

    -- 승인 상태
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_id UUID REFERENCES public.users(user_id),
    admin_comment TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eval_requests_user ON public.evaluation_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_eval_requests_status ON public.evaluation_requests(status);

-- ============================================
-- A5. projects - 진행 중 프로젝트 (승인된 것만)
-- ============================================
CREATE TABLE IF NOT EXISTS public.projects (
    project_id VARCHAR(50) PRIMARY KEY,
    request_id UUID REFERENCES public.evaluation_requests(request_id),
    user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    accountant_id UUID REFERENCES public.users(user_id) ON DELETE SET NULL,

    -- 기업 정보 (evaluation_requests에서 복사)
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    revenue BIGINT,
    employees INTEGER,
    founded_date DATE,
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 평가 정보
    valuation_purpose VARCHAR(50),
    requested_methods TEXT[],
    target_date DATE,
    requirements TEXT,
    budget_min INTEGER,
    budget_max INTEGER,

    -- 결제 정보
    agreed_price INTEGER,
    deposit_amount INTEGER DEFAULT 0,
    deposit_paid_at TIMESTAMP WITH TIME ZONE,
    balance_paid_at TIMESTAMP WITH TIME ZONE,

    -- 진행 상태
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    current_step INTEGER DEFAULT 1,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_accountant ON public.projects(accountant_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON public.projects(status);

-- ============================================
-- A6. project_history - 완료된 프로젝트
-- ============================================
CREATE TABLE IF NOT EXISTS public.project_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL,
    request_id UUID,
    user_id UUID NOT NULL REFERENCES public.users(user_id),
    accountant_id UUID REFERENCES public.users(user_id),

    -- 기업 정보
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 평가 정보
    valuation_purpose VARCHAR(50),
    completed_methods TEXT[],

    -- 결제 정보
    total_paid INTEGER,

    -- 완료 정보
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 최종 결과 요약
    final_values JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_history_user ON public.project_history(user_id);
CREATE INDEX IF NOT EXISTS idx_project_history_completed ON public.project_history(completed_at DESC);

-- ============================================
-- A7. valuation_reports - 샘플 보고서 (DART/KIND)
-- ============================================
CREATE TABLE IF NOT EXISTS public.valuation_reports (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    industry VARCHAR(100),
    ceo_name VARCHAR(100),
    founded_year VARCHAR(20),
    location VARCHAR(100),
    employee_count VARCHAR(50),
    valuation_method VARCHAR(50) NOT NULL,
    valuation_amount_krw BIGINT,
    valuation_amount_display VARCHAR(100),
    valuation_date DATE,
    evaluator VARCHAR(200),
    executive_summary TEXT,
    evaluation_overview TEXT,
    company_analysis TEXT,
    financial_summary TEXT,
    methodology TEXT,
    valuation_results TEXT,
    sensitivity_analysis TEXT,
    conclusion TEXT,
    appendix TEXT,
    report_url VARCHAR(500),
    pdf_url VARCHAR(500),
    tags TEXT[],
    key_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_valuation_reports_company ON public.valuation_reports(company_name);
CREATE INDEX IF NOT EXISTS idx_valuation_reports_method ON public.valuation_reports(valuation_method);

-- ============================================
-- A8. deals - 투자 딜 뉴스
-- ============================================
CREATE TABLE IF NOT EXISTS public.deals (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    investment_stage VARCHAR(50),
    investment_amount VARCHAR(100),
    investors TEXT,
    location VARCHAR(100),
    employees VARCHAR(50),
    article_url VARCHAR(500),
    article_title TEXT,
    article_source VARCHAR(100),
    published_date DATE,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deals_company ON public.deals(company_name);
CREATE INDEX IF NOT EXISTS idx_deals_score ON public.deals(score DESC);

-- ============================================
-- A9. investment_news_articles - 투자 뉴스 기사
-- ============================================
CREATE TABLE IF NOT EXISTS public.investment_news_articles (
    id SERIAL PRIMARY KEY,
    site_number INTEGER NOT NULL,
    site_name VARCHAR(100),
    article_url VARCHAR(500) UNIQUE NOT NULL,
    article_title TEXT NOT NULL,
    published_date DATE,
    content TEXT,
    company_name VARCHAR(200),
    score INTEGER DEFAULT 0,
    has_amount BOOLEAN DEFAULT false,
    has_investors BOOLEAN DEFAULT false,
    has_stage BOOLEAN DEFAULT false,
    has_industry BOOLEAN DEFAULT false,
    has_location BOOLEAN DEFAULT false,
    has_employees BOOLEAN DEFAULT false,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_site ON public.investment_news_articles(site_number);
CREATE INDEX IF NOT EXISTS idx_news_score ON public.investment_news_articles(score DESC);

-- ============================================
-- A10. balance_payments - 잔금 결제
-- ============================================
CREATE TABLE IF NOT EXISTS public.balance_payments (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    method VARCHAR(50) NOT NULL,
    depositor_name VARCHAR(100) NOT NULL,
    amount INTEGER NOT NULL,
    bank_name VARCHAR(50),
    account_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed')),
    requested_by UUID REFERENCES public.users(user_id),
    requested_name VARCHAR(100),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    confirmed_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, method)
);

CREATE INDEX IF NOT EXISTS idx_balance_payments_project ON public.balance_payments(project_id);

-- ============================================
-- A11. report_delivery_requests - 보고서 수령 요청
-- ============================================
CREATE TABLE IF NOT EXISTS public.report_delivery_requests (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    method VARCHAR(50) NOT NULL,
    delivery_type VARCHAR(20) NOT NULL CHECK (delivery_type IN ('email', 'hardcopy')),
    email VARCHAR(200),
    recipient_name VARCHAR(100),
    recipient_phone VARCHAR(30),
    zip_code VARCHAR(10),
    address VARCHAR(500),
    address_detail VARCHAR(200),
    copy_count INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed')),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_delivery_requests_project ON public.report_delivery_requests(project_id);


-- ============================================
-- PART B: 평가법별 분리 테이블 (30개)
-- ============================================

-- ============================================
-- B1. Documents 테이블 (5개)
-- ============================================

-- DCF Documents
CREATE TABLE IF NOT EXISTS public.dcf_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    upload_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_data JSONB,
    uploaded_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dcf_documents_project ON public.dcf_documents(project_id);

-- Relative Documents
CREATE TABLE IF NOT EXISTS public.relative_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    upload_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_data JSONB,
    uploaded_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relative_documents_project ON public.relative_documents(project_id);

-- Intrinsic Documents
CREATE TABLE IF NOT EXISTS public.intrinsic_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    upload_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_data JSONB,
    uploaded_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intrinsic_documents_project ON public.intrinsic_documents(project_id);

-- Asset Documents
CREATE TABLE IF NOT EXISTS public.asset_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    upload_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_data JSONB,
    uploaded_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_documents_project ON public.asset_documents(project_id);

-- Tax Documents
CREATE TABLE IF NOT EXISTS public.tax_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    category VARCHAR(100),
    description TEXT,
    upload_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_data JSONB,
    uploaded_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tax_documents_project ON public.tax_documents(project_id);

-- ============================================
-- B2. Approval Points 테이블 (5개) - 22개 AI 승인 포인트
-- ============================================

-- DCF Approval Points (JP001-JP008: 8개)
CREATE TABLE IF NOT EXISTS public.dcf_approval_points (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    point_id TEXT NOT NULL CHECK (point_id IN ('JP001', 'JP002', 'JP003', 'JP004', 'JP005', 'JP006', 'JP007', 'JP008')),
    point_name TEXT NOT NULL,
    importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
    ai_scenarios JSONB,
    ai_recommended JSONB,
    approved_value JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
    approved_by UUID REFERENCES public.users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, point_id)
);

CREATE INDEX IF NOT EXISTS idx_dcf_approval_project ON public.dcf_approval_points(project_id);

-- Relative Approval Points (JP009-JP012: 4개)
CREATE TABLE IF NOT EXISTS public.relative_approval_points (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    point_id TEXT NOT NULL CHECK (point_id IN ('JP009', 'JP010', 'JP011', 'JP012')),
    point_name TEXT NOT NULL,
    importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
    ai_scenarios JSONB,
    ai_recommended JSONB,
    approved_value JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
    approved_by UUID REFERENCES public.users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, point_id)
);

CREATE INDEX IF NOT EXISTS idx_relative_approval_project ON public.relative_approval_points(project_id);

-- Intrinsic Approval Points (JP019-JP020: 2개)
CREATE TABLE IF NOT EXISTS public.intrinsic_approval_points (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    point_id TEXT NOT NULL CHECK (point_id IN ('JP019', 'JP020')),
    point_name TEXT NOT NULL,
    importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
    ai_scenarios JSONB,
    ai_recommended JSONB,
    approved_value JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
    approved_by UUID REFERENCES public.users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, point_id)
);

CREATE INDEX IF NOT EXISTS idx_intrinsic_approval_project ON public.intrinsic_approval_points(project_id);

-- Asset Approval Points (JP013-JP018: 6개)
CREATE TABLE IF NOT EXISTS public.asset_approval_points (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    point_id TEXT NOT NULL CHECK (point_id IN ('JP013', 'JP014', 'JP015', 'JP016', 'JP017', 'JP018')),
    point_name TEXT NOT NULL,
    importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
    ai_scenarios JSONB,
    ai_recommended JSONB,
    approved_value JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
    approved_by UUID REFERENCES public.users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, point_id)
);

CREATE INDEX IF NOT EXISTS idx_asset_approval_project ON public.asset_approval_points(project_id);

-- Tax Approval Points (JP021-JP022: 2개)
CREATE TABLE IF NOT EXISTS public.tax_approval_points (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    point_id TEXT NOT NULL CHECK (point_id IN ('JP021', 'JP022')),
    point_name TEXT NOT NULL,
    importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
    ai_scenarios JSONB,
    ai_recommended JSONB,
    approved_value JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
    approved_by UUID REFERENCES public.users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, point_id)
);

CREATE INDEX IF NOT EXISTS idx_tax_approval_project ON public.tax_approval_points(project_id);

-- ============================================
-- B3. Results 테이블 (5개)
-- ============================================

-- DCF Results
CREATE TABLE IF NOT EXISTS public.dcf_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    wacc DECIMAL(5,2),
    terminal_growth_rate DECIMAL(5,2),
    projection_years INTEGER DEFAULT 5,
    free_cash_flows JSONB,
    terminal_value BIGINT,
    sensitivity_matrix JSONB,
    calculation_details JSONB,
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dcf_results_project ON public.dcf_results(project_id);

-- Relative Results
CREATE TABLE IF NOT EXISTS public.relative_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    peer_companies JSONB,
    selected_multiples JSONB,
    per_value BIGINT,
    pbr_value BIGINT,
    evebitda_value BIGINT,
    psr_value BIGINT,
    calculation_details JSONB,
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relative_results_project ON public.relative_results(project_id);

-- Intrinsic Results
CREATE TABLE IF NOT EXISTS public.intrinsic_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    net_asset_value BIGINT,
    earnings_value BIGINT,
    weight_asset DECIMAL(5,2),
    weight_earnings DECIMAL(5,2),
    calculation_details JSONB,
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intrinsic_results_project ON public.intrinsic_results(project_id);

-- Asset Results
CREATE TABLE IF NOT EXISTS public.asset_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    total_assets BIGINT,
    total_liabilities BIGINT,
    net_asset_value BIGINT,
    asset_adjustments JSONB,
    liability_adjustments JSONB,
    fair_value_adjustments JSONB,
    calculation_details JSONB,
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_results_project ON public.asset_results(project_id);

-- Tax Results (상증세법)
CREATE TABLE IF NOT EXISTS public.tax_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    net_asset_value BIGINT,
    net_profit_value BIGINT,
    weight_asset DECIMAL(5,2) DEFAULT 0.4,
    weight_profit DECIMAL(5,2) DEFAULT 0.6,
    supplementary_value BIGINT,
    calculation_details JSONB,
    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tax_results_project ON public.tax_results(project_id);

-- ============================================
-- B4. Drafts 테이블 (5개) - 섹션 완료 여부 포함
-- ============================================

-- DCF Drafts
CREATE TABLE IF NOT EXISTS public.dcf_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'submitted', 'confirmed', 'revision_requested', 'finalized')),

    -- 9개 섹션 내용
    section_1_summary TEXT,
    section_2_overview TEXT,
    section_3_company TEXT,
    section_4_financial TEXT,
    section_5_methodology TEXT,
    section_6_results TEXT,
    section_7_sensitivity TEXT,
    section_8_conclusion TEXT,
    section_9_appendix TEXT,

    -- 9개 섹션 완료 여부 (report_draft_sections에서 이관)
    section_1_completed BOOLEAN DEFAULT false,
    section_2_completed BOOLEAN DEFAULT false,
    section_3_completed BOOLEAN DEFAULT false,
    section_4_completed BOOLEAN DEFAULT false,
    section_5_completed BOOLEAN DEFAULT false,
    section_6_completed BOOLEAN DEFAULT false,
    section_7_completed BOOLEAN DEFAULT false,
    section_8_completed BOOLEAN DEFAULT false,
    section_9_completed BOOLEAN DEFAULT false,

    -- 제출 시각 (draft_method_status에서 이관)
    submitted_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dcf_drafts_project ON public.dcf_drafts(project_id);

-- Relative Drafts
CREATE TABLE IF NOT EXISTS public.relative_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'submitted', 'confirmed', 'revision_requested', 'finalized')),

    section_1_summary TEXT,
    section_2_overview TEXT,
    section_3_company TEXT,
    section_4_financial TEXT,
    section_5_methodology TEXT,
    section_6_results TEXT,
    section_7_sensitivity TEXT,
    section_8_conclusion TEXT,
    section_9_appendix TEXT,

    section_1_completed BOOLEAN DEFAULT false,
    section_2_completed BOOLEAN DEFAULT false,
    section_3_completed BOOLEAN DEFAULT false,
    section_4_completed BOOLEAN DEFAULT false,
    section_5_completed BOOLEAN DEFAULT false,
    section_6_completed BOOLEAN DEFAULT false,
    section_7_completed BOOLEAN DEFAULT false,
    section_8_completed BOOLEAN DEFAULT false,
    section_9_completed BOOLEAN DEFAULT false,

    submitted_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relative_drafts_project ON public.relative_drafts(project_id);

-- Intrinsic Drafts
CREATE TABLE IF NOT EXISTS public.intrinsic_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'submitted', 'confirmed', 'revision_requested', 'finalized')),

    section_1_summary TEXT,
    section_2_overview TEXT,
    section_3_company TEXT,
    section_4_financial TEXT,
    section_5_methodology TEXT,
    section_6_results TEXT,
    section_7_sensitivity TEXT,
    section_8_conclusion TEXT,
    section_9_appendix TEXT,

    section_1_completed BOOLEAN DEFAULT false,
    section_2_completed BOOLEAN DEFAULT false,
    section_3_completed BOOLEAN DEFAULT false,
    section_4_completed BOOLEAN DEFAULT false,
    section_5_completed BOOLEAN DEFAULT false,
    section_6_completed BOOLEAN DEFAULT false,
    section_7_completed BOOLEAN DEFAULT false,
    section_8_completed BOOLEAN DEFAULT false,
    section_9_completed BOOLEAN DEFAULT false,

    submitted_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intrinsic_drafts_project ON public.intrinsic_drafts(project_id);

-- Asset Drafts
CREATE TABLE IF NOT EXISTS public.asset_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'submitted', 'confirmed', 'revision_requested', 'finalized')),

    section_1_summary TEXT,
    section_2_overview TEXT,
    section_3_company TEXT,
    section_4_financial TEXT,
    section_5_methodology TEXT,
    section_6_results TEXT,
    section_7_sensitivity TEXT,
    section_8_conclusion TEXT,
    section_9_appendix TEXT,

    section_1_completed BOOLEAN DEFAULT false,
    section_2_completed BOOLEAN DEFAULT false,
    section_3_completed BOOLEAN DEFAULT false,
    section_4_completed BOOLEAN DEFAULT false,
    section_5_completed BOOLEAN DEFAULT false,
    section_6_completed BOOLEAN DEFAULT false,
    section_7_completed BOOLEAN DEFAULT false,
    section_8_completed BOOLEAN DEFAULT false,
    section_9_completed BOOLEAN DEFAULT false,

    submitted_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_drafts_project ON public.asset_drafts(project_id);

-- Tax Drafts
CREATE TABLE IF NOT EXISTS public.tax_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'submitted', 'confirmed', 'revision_requested', 'finalized')),

    section_1_summary TEXT,
    section_2_overview TEXT,
    section_3_company TEXT,
    section_4_financial TEXT,
    section_5_methodology TEXT,
    section_6_results TEXT,
    section_7_sensitivity TEXT,
    section_8_conclusion TEXT,
    section_9_appendix TEXT,

    section_1_completed BOOLEAN DEFAULT false,
    section_2_completed BOOLEAN DEFAULT false,
    section_3_completed BOOLEAN DEFAULT false,
    section_4_completed BOOLEAN DEFAULT false,
    section_5_completed BOOLEAN DEFAULT false,
    section_6_completed BOOLEAN DEFAULT false,
    section_7_completed BOOLEAN DEFAULT false,
    section_8_completed BOOLEAN DEFAULT false,
    section_9_completed BOOLEAN DEFAULT false,

    submitted_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES public.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tax_drafts_project ON public.tax_drafts(project_id);

-- ============================================
-- B5. Revisions 테이블 (5개)
-- ============================================

-- DCF Revisions
CREATE TABLE IF NOT EXISTS public.dcf_revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.dcf_drafts(draft_id) ON DELETE CASCADE,
    revision_type VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    details TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    requested_by UUID REFERENCES public.users(user_id),
    assigned_to UUID REFERENCES public.users(user_id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dcf_revisions_draft ON public.dcf_revisions(draft_id);

-- Relative Revisions
CREATE TABLE IF NOT EXISTS public.relative_revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.relative_drafts(draft_id) ON DELETE CASCADE,
    revision_type VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    details TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    requested_by UUID REFERENCES public.users(user_id),
    assigned_to UUID REFERENCES public.users(user_id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relative_revisions_draft ON public.relative_revisions(draft_id);

-- Intrinsic Revisions
CREATE TABLE IF NOT EXISTS public.intrinsic_revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.intrinsic_drafts(draft_id) ON DELETE CASCADE,
    revision_type VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    details TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    requested_by UUID REFERENCES public.users(user_id),
    assigned_to UUID REFERENCES public.users(user_id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intrinsic_revisions_draft ON public.intrinsic_revisions(draft_id);

-- Asset Revisions
CREATE TABLE IF NOT EXISTS public.asset_revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.asset_drafts(draft_id) ON DELETE CASCADE,
    revision_type VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    details TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    requested_by UUID REFERENCES public.users(user_id),
    assigned_to UUID REFERENCES public.users(user_id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_revisions_draft ON public.asset_revisions(draft_id);

-- Tax Revisions
CREATE TABLE IF NOT EXISTS public.tax_revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES public.tax_drafts(draft_id) ON DELETE CASCADE,
    revision_type VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    details TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    requested_by UUID REFERENCES public.users(user_id),
    assigned_to UUID REFERENCES public.users(user_id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tax_revisions_draft ON public.tax_revisions(draft_id);

-- ============================================
-- B6. Reports 테이블 (5개)
-- ============================================

-- DCF Reports
CREATE TABLE IF NOT EXISTS public.dcf_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    draft_id UUID REFERENCES public.dcf_drafts(draft_id),
    report_url VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    issued_by UUID REFERENCES public.users(user_id),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dcf_reports_project ON public.dcf_reports(project_id);

-- Relative Reports
CREATE TABLE IF NOT EXISTS public.relative_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    draft_id UUID REFERENCES public.relative_drafts(draft_id),
    report_url VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    issued_by UUID REFERENCES public.users(user_id),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relative_reports_project ON public.relative_reports(project_id);

-- Intrinsic Reports
CREATE TABLE IF NOT EXISTS public.intrinsic_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    draft_id UUID REFERENCES public.intrinsic_drafts(draft_id),
    report_url VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    issued_by UUID REFERENCES public.users(user_id),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intrinsic_reports_project ON public.intrinsic_reports(project_id);

-- Asset Reports
CREATE TABLE IF NOT EXISTS public.asset_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    draft_id UUID REFERENCES public.asset_drafts(draft_id),
    report_url VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    issued_by UUID REFERENCES public.users(user_id),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_reports_project ON public.asset_reports(project_id);

-- Tax Reports
CREATE TABLE IF NOT EXISTS public.tax_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    draft_id UUID REFERENCES public.tax_drafts(draft_id),
    report_url VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    issued_by UUID REFERENCES public.users(user_id),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tax_reports_project ON public.tax_reports(project_id);


-- ============================================
-- PART C: 트리거 함수
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- 완료
-- ============================================
-- 총 41개 테이블:
--
-- 기존 테이블 (11개):
--   1. users
--   2. accountants
--   3. customers
--   4. evaluation_requests (신규)
--   5. projects
--   6. project_history (신규)
--   7. valuation_reports
--   8. deals
--   9. investment_news_articles
--  10. balance_payments
--  11. report_delivery_requests
--
-- 평가법별 분리 테이블 (30개 = 6종류 x 5평가법):
--   - Documents: 5개
--   - Approval Points: 5개 (22개 AI 승인 포인트)
--   - Results: 5개
--   - Drafts: 5개 (섹션 완료 여부 + 제출 시각 포함)
--   - Revisions: 5개
--   - Reports: 5개
--
-- 삭제된 테이블:
--   - quotes (불필요)
--   - negotiations (불필요)
--   - report_draft_sections (drafts에 통합)
--   - draft_method_status (drafts에 통합)
