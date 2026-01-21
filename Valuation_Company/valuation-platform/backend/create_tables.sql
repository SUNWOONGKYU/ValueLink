-- Valuation Platform Tables
-- Supabase Dashboard > SQL Editor에서 실행

-- 1. Projects 테이블
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'requested',
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    valuation_purpose VARCHAR(50),
    requested_methods TEXT[],
    target_date DATE,
    actual_completion_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Quotes 테이블
CREATE TABLE IF NOT EXISTS quotes (
    quote_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    base_fee BIGINT,
    discount_rate FLOAT,
    final_fee BIGINT,
    payment_terms TEXT,
    valid_until DATE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Negotiations 테이블
CREATE TABLE IF NOT EXISTS negotiations (
    negotiation_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    request_type VARCHAR(50),
    details TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Documents 테이블
CREATE TABLE IF NOT EXISTS documents (
    document_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    file_name VARCHAR(500),
    file_url VARCHAR(1000),
    file_type VARCHAR(50),
    upload_status VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 5. Approval Points 테이블
CREATE TABLE IF NOT EXISTS approval_points (
    approval_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    point_code VARCHAR(10),
    category VARCHAR(50),
    question TEXT,
    ai_decision VARCHAR(50),
    ai_rationale TEXT,
    human_decision VARCHAR(50),
    human_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Valuation Results 테이블
CREATE TABLE IF NOT EXISTS valuation_results (
    result_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    method VARCHAR(50) NOT NULL,
    enterprise_value BIGINT,
    equity_value BIGINT,
    value_per_share BIGINT,
    calculation_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Drafts 테이블
CREATE TABLE IF NOT EXISTS drafts (
    draft_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    content TEXT,
    version INTEGER DEFAULT 1,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. Revisions 테이블
CREATE TABLE IF NOT EXISTS revisions (
    revision_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    draft_id INTEGER REFERENCES drafts(draft_id),
    revision_type VARCHAR(50),
    details TEXT,
    requested_at TIMESTAMP DEFAULT NOW()
);

-- 9. Reports 테이블
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    report_url VARCHAR(1000),
    issued_at TIMESTAMP DEFAULT NOW()
);
