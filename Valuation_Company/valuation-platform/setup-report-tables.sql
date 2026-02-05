-- =============================================
-- 평가보고서 초안 관련 테이블 생성
-- =============================================

-- 1. report_draft_sections: 보고서 섹션별 내용 저장
CREATE TABLE IF NOT EXISTS report_draft_sections (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    method VARCHAR(50) NOT NULL,
    section_key VARCHAR(50) NOT NULL,
    section_title VARCHAR(200),
    content TEXT DEFAULT '',
    is_completed BOOLEAN DEFAULT false,
    updated_by VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, method, section_key)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_draft_sections_project ON report_draft_sections(project_id, method);

-- RLS 정책
ALTER TABLE report_draft_sections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "report_draft_sections_select" ON report_draft_sections
    FOR SELECT USING (true);

CREATE POLICY "report_draft_sections_insert" ON report_draft_sections
    FOR INSERT WITH CHECK (true);

CREATE POLICY "report_draft_sections_update" ON report_draft_sections
    FOR UPDATE USING (true);

-- 2. projects 테이블 컬럼 추가 (이미 존재하면 무시)
ALTER TABLE projects ADD COLUMN IF NOT EXISTS draft_status VARCHAR(50) DEFAULT 'not_started';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS draft_submitted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS final_report_url VARCHAR(1000);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS agreed_price INTEGER;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS deposit_amount INTEGER DEFAULT 0;

-- agreed_price: 관리자가 승인한 총 서비스 금액 (원)
--   고객이 가격을 제안 → 관리자가 승인하면 이 컬럼에 저장
--   NULL이면 아직 가격 미확정
-- deposit_amount: 선금 납부액 (원)
--   잔금 = agreed_price - deposit_amount

-- 3. Supabase Storage 버킷 생성 (Supabase 대시보드에서 수동 생성 필요)
-- 버킷명: valuation-reports
-- 공개 여부: private (인증된 사용자만 접근)

-- draft_status 값:
--   not_started     : 초안 작성 시작 전
--   in_progress     : 초안 작성 중
--   submitted       : 초안 제출 완료 (고객 검토 대기)
--   confirmed       : 고객 확인 완료
--   revision_requested : 수정 요청됨
--   finalized       : 최종 보고서 완료

-- =============================================
-- 7. draft_method_status: 평가 방법별 draft 상태 관리
-- =============================================
-- projects.draft_status는 단일 값이므로 다중 평가법 동시 진행 시 충돌 가능
-- 이 테이블로 방법별 독립적 상태 관리
CREATE TABLE IF NOT EXISTS draft_method_status (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    method VARCHAR(50) NOT NULL,
    draft_status VARCHAR(50) DEFAULT 'not_started',
    draft_submitted_at TIMESTAMP WITH TIME ZONE,
    final_report_url VARCHAR(1000),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, method)
);

CREATE INDEX IF NOT EXISTS idx_draft_method_status_project ON draft_method_status(project_id, method);

ALTER TABLE draft_method_status ENABLE ROW LEVEL SECURITY;

CREATE POLICY "draft_method_status_select" ON draft_method_status
    FOR SELECT USING (true);

CREATE POLICY "draft_method_status_insert" ON draft_method_status
    FOR INSERT WITH CHECK (true);

CREATE POLICY "draft_method_status_update" ON draft_method_status
    FOR UPDATE USING (true);

-- draft_method_status.draft_status 값: not_started, in_progress, submitted, confirmed, revision_requested, finalized

-- =============================================
-- 4. balance_payments: 잔금 무통장 입금 관리
-- =============================================
CREATE TABLE IF NOT EXISTS balance_payments (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    method VARCHAR(50) NOT NULL,
    depositor_name VARCHAR(100) NOT NULL,
    amount INTEGER NOT NULL,
    bank_name VARCHAR(50),
    account_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    requested_by VARCHAR(200),
    requested_name VARCHAR(100),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    confirmed_by VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, method)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_balance_payments_project ON balance_payments(project_id, method);
CREATE INDEX IF NOT EXISTS idx_balance_payments_status ON balance_payments(status);

-- RLS 정책
ALTER TABLE balance_payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "balance_payments_select" ON balance_payments
    FOR SELECT USING (true);

CREATE POLICY "balance_payments_insert" ON balance_payments
    FOR INSERT WITH CHECK (true);

CREATE POLICY "balance_payments_update" ON balance_payments
    FOR UPDATE USING (true);

-- balance_payments.status 값:
--   pending   : 입금 대기 (고객이 입금 요청함)
--   confirmed : 입금 확인 완료 (관리자가 확인)

-- =============================================
-- 5. revision_requests: 고객 수정 요청
-- =============================================
CREATE TABLE IF NOT EXISTS revision_requests (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    method VARCHAR(50) NOT NULL,
    section VARCHAR(100) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    request_detail TEXT NOT NULL,
    attachment_urls TEXT[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT '접수됨',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_revision_requests_project ON revision_requests(project_id, method);

-- RLS 정책
ALTER TABLE revision_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "revision_requests_select" ON revision_requests
    FOR SELECT USING (true);

CREATE POLICY "revision_requests_insert" ON revision_requests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "revision_requests_update" ON revision_requests
    FOR UPDATE USING (true);

-- revision_requests.status 값: 접수됨, 처리중, 완료

-- =============================================
-- 6. report_delivery_requests: 보고서 수령 요청 (이메일/하드카피)
-- =============================================
CREATE TABLE IF NOT EXISTS report_delivery_requests (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    method VARCHAR(50) NOT NULL,
    delivery_type VARCHAR(20) NOT NULL,
    email VARCHAR(200),
    recipient_name VARCHAR(100),
    recipient_phone VARCHAR(30),
    zip_code VARCHAR(10),
    address VARCHAR(500),
    address_detail VARCHAR(200),
    copy_count INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_delivery_requests_project ON report_delivery_requests(project_id, method);

-- RLS 정책
ALTER TABLE report_delivery_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "delivery_requests_select" ON report_delivery_requests
    FOR SELECT USING (true);

CREATE POLICY "delivery_requests_insert" ON report_delivery_requests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "delivery_requests_update" ON report_delivery_requests
    FOR UPDATE USING (true);

-- delivery_type 값: email, hardcopy
-- status 값: pending (접수), processing (처리중), completed (완료)
