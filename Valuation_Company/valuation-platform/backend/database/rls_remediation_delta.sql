-- ============================================================
-- RLS 보완 정책 — Delta 분대 작성 (2026-06-12)
-- 실행 전 소대장(team-lead) 승인 필수
-- Supabase Dashboard > SQL Editor에서 실행할 것
-- ============================================================

-- ============================================================
-- [CRITICAL-1] users 테이블 — SELECT USING(true) 과다 공개
-- 문제: anon 키로 모든 사용자의 email, role, is_active 조회 가능
-- 현재: FOR SELECT USING (true)  → 전체 공개
-- 보완: 본인 레코드만 조회 허용, anon은 차단
-- ============================================================
DROP POLICY IF EXISTS "Allow public read access" ON users;

CREATE POLICY "users_select_own" ON users
    FOR SELECT USING (auth.uid() = user_id);

-- ※ 회원가입 시 이메일 중복 체크 등 anon SELECT가 필요한 경우
--   아래 정책을 추가하되 email 컬럼만 노출하도록 뷰(View)로 분리 권장
-- CREATE POLICY "users_select_email_check" ON users
--     FOR SELECT USING (true);  -- 이 경우 전체 컬럼 노출 위험 → 뷰 방식 권장


-- ============================================================
-- [CRITICAL-2] customers 테이블 — SELECT USING(true) 과다 공개
-- 문제: anon 키로 모든 고객사 사업자번호, 대표자명, 주소 조회 가능
-- 보완: 본인(email 일치) 레코드만 조회 허용
-- ============================================================
DROP POLICY IF EXISTS "Allow public read access" ON customers;

CREATE POLICY "customers_select_own" ON customers
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE email = customers.email
        )
    );

-- 관리자는 전체 조회 가능
CREATE POLICY "customers_select_admin" ON customers
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'admin'
        )
    );


-- ============================================================
-- [CRITICAL-3] projects 테이블 — SELECT USING(true) 과다 공개
-- 문제: anon 키로 모든 프로젝트(고객사명, project_id, 평가방법 등) 조회 가능
-- 보완: 본인 customer 또는 배정된 accountant, 또는 admin만 조회
-- ============================================================
DROP POLICY IF EXISTS "Allow public read access" ON projects;

CREATE POLICY "projects_select_own_customer" ON projects
    FOR SELECT USING (
        customer_id IN (
            SELECT c.customer_id FROM customers c
            JOIN users u ON u.email = c.email
            WHERE u.user_id = auth.uid()
        )
    );

CREATE POLICY "projects_select_admin" ON projects
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'admin'
        )
    );

-- accountant는 별도 배정 테이블이 없으므로 일단 accountant role 전체 허용
-- (배정 테이블 추가 후 세분화 권장)
CREATE POLICY "projects_select_accountant" ON projects
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'accountant'
        )
    );


-- ============================================================
-- [HIGH-1] accountants 테이블 — SELECT USING(true) 공개
-- 문제: anon 키로 회계사 license_number, 연락처, 경력 조회 가능
-- 수용 가능 여부: 프로필 공개가 비즈니스 요건이라면 현행 유지 가능
-- 보완(선택): 공개 허용 시 민감 컬럼(license_number) 뷰로 분리 권장
-- 현재는 정책 유지, 운영팀 판단에 맡김 — 아래는 강화 버전 예시
-- ============================================================
-- DROP POLICY IF EXISTS "Allow public read access" ON accountants;
-- CREATE POLICY "accountants_select_public_profile" ON accountants
--     FOR SELECT USING (is_available = true);  -- 활성 회계사만 공개


-- ============================================================
-- [HIGH-2] setup-report-tables.sql 테이블들 — INSERT/UPDATE WITH CHECK(true)
-- 문제: anon 키로 인증 없이 INSERT/UPDATE 가능
-- 대상: report_draft_sections, draft_method_status, balance_payments,
--        revision_requests, report_delivery_requests
-- 보완: INSERT/UPDATE를 authenticated role로 제한
-- ============================================================

-- report_draft_sections
DROP POLICY IF EXISTS "report_draft_sections_insert" ON report_draft_sections;
DROP POLICY IF EXISTS "report_draft_sections_update" ON report_draft_sections;

CREATE POLICY "report_draft_sections_insert_auth" ON report_draft_sections
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "report_draft_sections_update_auth" ON report_draft_sections
    FOR UPDATE USING (auth.role() = 'authenticated');

-- draft_method_status
DROP POLICY IF EXISTS "draft_method_status_insert" ON draft_method_status;
DROP POLICY IF EXISTS "draft_method_status_update" ON draft_method_status;

CREATE POLICY "draft_method_status_insert_auth" ON draft_method_status
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "draft_method_status_update_auth" ON draft_method_status
    FOR UPDATE USING (auth.role() = 'authenticated');

-- balance_payments
DROP POLICY IF EXISTS "balance_payments_insert" ON balance_payments;
DROP POLICY IF EXISTS "balance_payments_update" ON balance_payments;

CREATE POLICY "balance_payments_insert_auth" ON balance_payments
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "balance_payments_update_auth" ON balance_payments
    FOR UPDATE USING (auth.role() = 'authenticated');

-- revision_requests
DROP POLICY IF EXISTS "revision_requests_insert" ON revision_requests;
DROP POLICY IF EXISTS "revision_requests_update" ON revision_requests;

CREATE POLICY "revision_requests_insert_auth" ON revision_requests
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "revision_requests_update_auth" ON revision_requests
    FOR UPDATE USING (auth.role() = 'authenticated');

-- report_delivery_requests
DROP POLICY IF EXISTS "delivery_requests_insert" ON report_delivery_requests;
DROP POLICY IF EXISTS "delivery_requests_update" ON report_delivery_requests;

CREATE POLICY "delivery_requests_insert_auth" ON report_delivery_requests
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "delivery_requests_update_auth" ON report_delivery_requests
    FOR UPDATE USING (auth.role() = 'authenticated');


-- ============================================================
-- [HIGH-3] newsletter_subscribers 테이블 — RLS 상태 불명
-- 문제: 스키마 파일 없음, deal.html에서 anon 키로 INSERT 중
-- 보완: RLS 활성화 + INSERT는 anon 허용(구독은 공개), SELECT/DELETE는 admin 전용
-- ============================================================
ALTER TABLE IF EXISTS newsletter_subscribers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "newsletter_insert_public" ON newsletter_subscribers;
DROP POLICY IF EXISTS "newsletter_select_admin" ON newsletter_subscribers;
DROP POLICY IF EXISTS "newsletter_delete_admin" ON newsletter_subscribers;

CREATE POLICY "newsletter_insert_public" ON newsletter_subscribers
    FOR INSERT WITH CHECK (true);  -- 뉴스레터 구독은 비로그인 허용

CREATE POLICY "newsletter_select_admin" ON newsletter_subscribers
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'admin'
        )
    );

CREATE POLICY "newsletter_delete_admin" ON newsletter_subscribers
    FOR DELETE USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'admin'
        )
    );


-- ============================================================
-- [MEDIUM] create_tables.sql 테이블들 — RLS 없음 (미적용 스키마)
-- 대상: quotes, negotiations, documents, approval_points,
--        valuation_results(구버전), drafts, revisions, reports
-- 주의: 이 테이블들이 실제 DB에 적용되어 있는지 확인 필요
--        마이그레이션 파일(supabase/migrations)에 없으므로
--        실제 Supabase에 적용되지 않았을 가능성 있음
-- 보완: 적용 확인 후 아래 실행
-- ============================================================

-- quotes (견적)
ALTER TABLE IF EXISTS quotes ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "quotes_authenticated_only" ON quotes
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- negotiations (협상)
ALTER TABLE IF EXISTS negotiations ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "negotiations_authenticated_only" ON negotiations
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- documents (문서)
ALTER TABLE IF EXISTS documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "documents_authenticated_only" ON documents
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- approval_points
ALTER TABLE IF EXISTS approval_points ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "approval_points_authenticated_only" ON approval_points
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- drafts
ALTER TABLE IF EXISTS drafts ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "drafts_authenticated_only" ON drafts
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- revisions
ALTER TABLE IF EXISTS revisions ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "revisions_authenticated_only" ON revisions
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- reports (구버전 테이블, 신버전은 valuation_reports)
ALTER TABLE IF EXISTS reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "reports_authenticated_only" ON reports
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');
