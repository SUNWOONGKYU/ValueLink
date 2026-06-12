-- ============================================================
-- RLS 보완 정책 v2 (실DB 검증 반영 최종본) — 백호 작전 Phase 5 (2026-06-12)
-- 원본: rls_remediation_delta.sql (감사 시점 가정 기반)
--
-- 실DB 점검(Management API) 결과 반영 사항:
--  [반영 1] users / accountants / quotes 등 7개 레거시 테이블은 RLS 자체가
--           비활성 상태 → 정책 생성만으로는 무효, ALTER TABLE ... ENABLE 필수
--  [반영 2] projects는 schema-v5 구조(user_id/accountant_id 직접 보유)이고
--           이미 projects_owner_or_accountant 정책으로 익명조회 차단됨
--           → 원본의 customer_id 기반 정책은 존재하지 않는 컬럼 참조(에러)
--           → admin 관리 정책만 추가
--  [반영 3] HIGH-2 리포트 테이블 5종(report_draft_sections 등)은 실DB에 없음 → 제외
--  [반영 4] 이메일 인증 ON(mailer_autoconfirm=false) → 가입 직후 users INSERT는
--           anon으로 실행됨 → anon INSERT 허용하되 role='admin' 삽입만 차단
--  [반영 5] users 정책이 users를 직접 서브쿼리하면 무한재귀 → SECURITY DEFINER
--           함수(get_my_role)로 우회
--  [반영 6] 일반 사용자가 UPDATE로 자기 role을 셀프 승격하는 경로 차단
--           (role = get_my_role() 조건: 자기 수정 시 role 변경 불가)
-- ============================================================

-- ============================================================
-- [0] 역할 조회 함수 — RLS 우회(SECURITY DEFINER), 무한재귀 방지
-- ============================================================
CREATE OR REPLACE FUNCTION public.get_my_role()
RETURNS text
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT role FROM users WHERE user_id = auth.uid();
$$;


-- ============================================================
-- [CRITICAL-1] users — RLS 비활성 (anon이 전체 조회/수정/삭제 가능한 상태)
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read access" ON users;
DROP POLICY IF EXISTS "users_select_own" ON users;
DROP POLICY IF EXISTS "users_select_admin" ON users;
DROP POLICY IF EXISTS "users_insert_signup" ON users;
DROP POLICY IF EXISTS "users_insert_admin" ON users;
DROP POLICY IF EXISTS "users_update_own" ON users;
DROP POLICY IF EXISTS "users_update_admin" ON users;
DROP POLICY IF EXISTS "users_delete_admin" ON users;

-- 본인 레코드 조회 (로그인/auth-check/역할재확인 의존)
CREATE POLICY "users_select_own" ON users
    FOR SELECT USING (auth.uid() = user_id);

-- admin 전체 조회 (mypage-admin 회원관리 의존)
CREATE POLICY "users_select_admin" ON users
    FOR SELECT USING (public.get_my_role() = 'admin');

-- 가입 INSERT: 이메일 인증 ON이라 가입 직후 anon으로 실행됨 → 허용하되 admin 역할 삽입 차단
CREATE POLICY "users_insert_signup" ON users
    FOR INSERT WITH CHECK (role <> 'admin');

-- admin은 admin 계정도 생성 가능
CREATE POLICY "users_insert_admin" ON users
    FOR INSERT WITH CHECK (public.get_my_role() = 'admin');

-- 본인 수정: role은 변경 불가(셀프 승격 차단), 그 외 필드만 수정 가능
CREATE POLICY "users_update_own" ON users
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id AND role = public.get_my_role());

-- admin은 전체 수정 가능 (mypage-admin 회원 편집 의존)
CREATE POLICY "users_update_admin" ON users
    FOR UPDATE USING (public.get_my_role() = 'admin')
    WITH CHECK (public.get_my_role() = 'admin');

-- 삭제는 admin만
CREATE POLICY "users_delete_admin" ON users
    FOR DELETE USING (public.get_my_role() = 'admin');


-- ============================================================
-- [CRITICAL-2] customers — SELECT USING(true) 과다 공개
-- 보완: 본인(email 일치) + admin + accountant 조회 허용
-- (INSERT/UPDATE/DELETE는 기존 authenticated 정책 유지)
-- ============================================================
DROP POLICY IF EXISTS "Allow public read access" ON customers;
DROP POLICY IF EXISTS "customers_select_own" ON customers;
DROP POLICY IF EXISTS "customers_select_admin" ON customers;
DROP POLICY IF EXISTS "customers_select_accountant" ON customers;

CREATE POLICY "customers_select_own" ON customers
    FOR SELECT USING (
        email = (SELECT email FROM users WHERE user_id = auth.uid())
    );

CREATE POLICY "customers_select_admin" ON customers
    FOR SELECT USING (public.get_my_role() = 'admin');

-- 회계사는 평가 업무상 고객사 정보 조회 필요
CREATE POLICY "customers_select_accountant" ON customers
    FOR SELECT USING (public.get_my_role() = 'accountant');


-- ============================================================
-- [CRITICAL-3] projects — 익명조회는 projects_owner_or_accountant로 이미 차단됨
-- 보완: admin 관리 정책만 추가 (mypage-admin 프로젝트 관리 의존)
-- ============================================================
DROP POLICY IF EXISTS "projects_admin_all" ON projects;

CREATE POLICY "projects_admin_all" ON projects
    FOR ALL USING (public.get_my_role() = 'admin')
    WITH CHECK (public.get_my_role() = 'admin');


-- ============================================================
-- [HIGH-1] accountants — RLS 비활성 (anon이 쓰기/삭제까지 가능한 상태)
-- 보완: 프로필 공개 조회는 유지(accountant-profile.html 비로그인 열람),
--        쓰기는 authenticated, 삭제는 admin만
-- ============================================================
ALTER TABLE accountants ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "accountants_select_public" ON accountants;
DROP POLICY IF EXISTS "accountants_insert_auth" ON accountants;
DROP POLICY IF EXISTS "accountants_update_auth" ON accountants;
DROP POLICY IF EXISTS "accountants_delete_admin" ON accountants;

CREATE POLICY "accountants_select_public" ON accountants
    FOR SELECT USING (true);

CREATE POLICY "accountants_insert_auth" ON accountants
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "accountants_update_auth" ON accountants
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "accountants_delete_admin" ON accountants
    FOR DELETE USING (public.get_my_role() = 'admin');


-- ============================================================
-- [HIGH-3] newsletter_subscribers — 구독자 이메일 전체 공개 조회 차단
-- (INSERT 공개 정책 'Anyone can subscribe'/'Allow public insert'와
--  service_role 정책은 유지)
-- ============================================================
DROP POLICY IF EXISTS "Allow public read" ON newsletter_subscribers;
DROP POLICY IF EXISTS "newsletter_select_admin" ON newsletter_subscribers;
DROP POLICY IF EXISTS "newsletter_delete_admin" ON newsletter_subscribers;

CREATE POLICY "newsletter_select_admin" ON newsletter_subscribers
    FOR SELECT USING (public.get_my_role() = 'admin');

CREATE POLICY "newsletter_delete_admin" ON newsletter_subscribers
    FOR DELETE USING (public.get_my_role() = 'admin');


-- ============================================================
-- [MEDIUM] 레거시 7개 테이블 — RLS 비활성 + 프론트엔드 미사용 확인됨
-- 보완: RLS 활성화 + authenticated 전용
-- ============================================================

ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "quotes_authenticated_only" ON quotes;
CREATE POLICY "quotes_authenticated_only" ON quotes
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

ALTER TABLE negotiations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "negotiations_authenticated_only" ON negotiations;
CREATE POLICY "negotiations_authenticated_only" ON negotiations
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "documents_authenticated_only" ON documents;
CREATE POLICY "documents_authenticated_only" ON documents
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

ALTER TABLE approval_points ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "approval_points_authenticated_only" ON approval_points;
CREATE POLICY "approval_points_authenticated_only" ON approval_points
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "drafts_authenticated_only" ON drafts;
CREATE POLICY "drafts_authenticated_only" ON drafts
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

ALTER TABLE revisions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "revisions_authenticated_only" ON revisions;
CREATE POLICY "revisions_authenticated_only" ON revisions
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "reports_authenticated_only" ON reports;
CREATE POLICY "reports_authenticated_only" ON reports
    FOR ALL USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');


-- ============================================================
-- [범위 외 — 후속 판단 필요 항목] (이번 실행에 미포함)
--  * valuation_reports: 공개 조회 2정책 존재. link.html이 비로그인 기업목록으로
--    사용 중이라 의도된 공개로 보임 → 운영 판단 필요
--  * 회계사 회원가입(register.html saveAccountantData): 실DB accountants에
--    accountant_id/email 컬럼이 없어 RLS와 무관하게 이미 동작 불가 (스키마 불일치)
--  * mypage-admin addUser(): user_id 없이 INSERT → PK 제약으로 이미 동작 불가
-- ============================================================


-- ============================================================
-- [롤백] 문제 발생 시 아래 실행으로 원상 복구 (데이터 무손실)
-- ============================================================
-- ALTER TABLE users DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE accountants DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE quotes DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE negotiations DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE approval_points DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE drafts DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE revisions DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE reports DISABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow public read access" ON customers FOR SELECT USING (true);
-- DROP POLICY IF EXISTS "customers_select_own" ON customers;
-- DROP POLICY IF EXISTS "customers_select_admin" ON customers;
-- DROP POLICY IF EXISTS "customers_select_accountant" ON customers;
-- DROP POLICY IF EXISTS "projects_admin_all" ON projects;
-- CREATE POLICY "Allow public read" ON newsletter_subscribers FOR SELECT USING (true);
-- DROP POLICY IF EXISTS "newsletter_select_admin" ON newsletter_subscribers;
-- DROP POLICY IF EXISTS "newsletter_delete_admin" ON newsletter_subscribers;
