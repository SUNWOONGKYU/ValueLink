-- ============================================================
-- RLS 보완 정책 v3 — 백호 작전 Phase 5 후속 (security 에이전트 검증 반영, 2026-06-12)
-- 선행: rls_remediation_delta_v2.sql (실행 완료, 19/19 검증 PASS)
--
-- security 에이전트 Needs Fix 반영 사항:
--  [H-1] 가입 INSERT가 role <> 'admin'만 차단 → accountant 자기가입으로
--        customers 전체 열람 권한 획득 가능 → 가입 역할 화이트리스트로 강화
--        (PO 승인: 회계사 자기가입 차단, 회계사 계정은 관리자가 부여)
--  [H-2] accountants UPDATE/INSERT가 authenticated 전체 허용 → 타인 프로필
--        변조 가능 → admin 전용으로 강화
--        (실DB accountants에 user_id 컬럼 없음 → '본인 행' 정책 적용 불가,
--         프론트엔드 쓰기 경로는 스키마 불일치로 이미 동작 불가 → 영향 없음)
--  [M-2] customers INSERT/UPDATE/DELETE가 authenticated 전체 허용 → 타사
--        고객정보 변조/삭제 가능 → admin 전용으로 강화
--        (register.html customers INSERT는 실DB에 없는 user_id 컬럼 참조로
--         이미 동작 불가 → 영향 없음)
--  [M-1] newsletter_subscribers anon INSERT 무제한 → 의도된 공개 구독 기능,
--        위험 수용 (완화는 앱 레벨 rate limiting 과제로 기록)
-- ============================================================

-- ============================================================
-- [H-1] users — 가입 역할 화이트리스트 (accountant/admin 자기가입 차단)
-- ============================================================
DROP POLICY IF EXISTS "users_insert_signup" ON users;
CREATE POLICY "users_insert_signup" ON users
    FOR INSERT WITH CHECK (
        role IN ('customer', 'investor', 'partner', 'supporter')
    );
-- users_insert_admin(admin은 모든 역할 생성 가능)은 v2 그대로 유지


-- ============================================================
-- [H-2] accountants — 쓰기 admin 전용
-- ============================================================
DROP POLICY IF EXISTS "accountants_insert_auth" ON accountants;
DROP POLICY IF EXISTS "accountants_insert_admin" ON accountants;
CREATE POLICY "accountants_insert_admin" ON accountants
    FOR INSERT WITH CHECK (public.get_my_role() = 'admin');

DROP POLICY IF EXISTS "accountants_update_auth" ON accountants;
DROP POLICY IF EXISTS "accountants_update_admin" ON accountants;
CREATE POLICY "accountants_update_admin" ON accountants
    FOR UPDATE USING (public.get_my_role() = 'admin')
    WITH CHECK (public.get_my_role() = 'admin');
-- accountants_select_public(프로필 공개 조회), accountants_delete_admin은 v2 유지


-- ============================================================
-- [M-2] customers — 쓰기 admin 전용
-- (SELECT 정책 3종: own/admin/accountant는 v2 유지 — 회계사 평가 업무 조회 가능)
-- ============================================================
DROP POLICY IF EXISTS "Allow authenticated insert" ON customers;
DROP POLICY IF EXISTS "customers_insert_admin" ON customers;
CREATE POLICY "customers_insert_admin" ON customers
    FOR INSERT WITH CHECK (public.get_my_role() = 'admin');

DROP POLICY IF EXISTS "Allow authenticated update" ON customers;
DROP POLICY IF EXISTS "customers_update_admin" ON customers;
CREATE POLICY "customers_update_admin" ON customers
    FOR UPDATE USING (public.get_my_role() = 'admin')
    WITH CHECK (public.get_my_role() = 'admin');

DROP POLICY IF EXISTS "Allow authenticated delete" ON customers;
DROP POLICY IF EXISTS "customers_delete_admin" ON customers;
CREATE POLICY "customers_delete_admin" ON customers
    FOR DELETE USING (public.get_my_role() = 'admin');


-- ============================================================
-- [롤백] 문제 발생 시 아래 실행으로 v2 직후 상태로 복구 (데이터 무손실)
-- (아래 원본 정의는 2026-06-12 실DB pg_policies 조회 결과 기준)
-- ============================================================
-- DROP POLICY IF EXISTS "users_insert_signup" ON users;
-- CREATE POLICY "users_insert_signup" ON users
--     FOR INSERT WITH CHECK (role <> 'admin');
--
-- DROP POLICY IF EXISTS "accountants_insert_admin" ON accountants;
-- CREATE POLICY "accountants_insert_auth" ON accountants
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');
-- DROP POLICY IF EXISTS "accountants_update_admin" ON accountants;
-- CREATE POLICY "accountants_update_auth" ON accountants
--     FOR UPDATE USING (auth.role() = 'authenticated');
--
-- DROP POLICY IF EXISTS "customers_insert_admin" ON customers;
-- CREATE POLICY "Allow authenticated insert" ON customers
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');
-- DROP POLICY IF EXISTS "customers_update_admin" ON customers;
-- CREATE POLICY "Allow authenticated update" ON customers
--     FOR UPDATE USING (auth.role() = 'authenticated');
-- DROP POLICY IF EXISTS "customers_delete_admin" ON customers;
-- CREATE POLICY "Allow authenticated delete" ON customers
--     FOR DELETE USING (auth.role() = 'authenticated');
