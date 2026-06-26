-- ============================================================
-- customers RLS 범위 축소 — 회계사 고객조회를 '담당 프로젝트의 고객'으로 제한 (2026-06-26)
-- 배경: customers_select_accountant 가 회계사에게 전체 고객 조회를 허용(과다).
--       실제로 회계사로 customers를 광범위 조회하는 기능 없음(검증) → 안전하게 축소.
-- 효과: 회계사는 자신이 배정된(projects.accountant_id=auth.uid()) 프로젝트의
--       고객(customers.user_id = projects.user_id)만 조회 가능.
-- 의존: public.get_my_role() (기존 프로덕션 함수)
-- projects RLS는 변경 없음(이미 owner_or_accountant + admin 으로 적정).
-- ⚠️ 프로덕션 DDL — PO 승인 하에 적용. 데이터 무손실(정책 교체). 롤백 하단.
-- ============================================================

DROP POLICY IF EXISTS "customers_select_accountant" ON customers;

CREATE POLICY "customers_select_accountant" ON customers
    FOR SELECT USING (
        public.get_my_role() = 'accountant'
        AND user_id IN (SELECT user_id FROM projects WHERE accountant_id = auth.uid())
    );

-- 검증: SELECT polname, qual FROM pg_policies WHERE tablename='customers' AND policyname='customers_select_accountant';

-- ============================================================
-- [롤백] 전체조회 허용으로 복구
-- DROP POLICY IF EXISTS "customers_select_accountant" ON customers;
-- CREATE POLICY "customers_select_accountant" ON customers FOR SELECT USING (public.get_my_role() = 'accountant');
-- ============================================================
