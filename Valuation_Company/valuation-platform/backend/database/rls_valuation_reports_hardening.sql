-- ============================================================
-- valuation_reports 보안분리 (쓰기 admin 전용) — RLS 후속 (2026-06-22)
-- 선행: rls_remediation_delta_v2.sql 202-208행 "범위 외 — 후속 판단 필요"
--       (2026_06_15__PHASE_결함_일괄수정.md 51행 [~] valuation_reports 보안분리 DDL)
--
-- 배경:
--  * valuation_reports = 공개 평가보고서 샘플 데이터 (DART/KIND 수집)
--  * 공개 SELECT는 의도된 동작 — link.html이 비로그인 기업목록으로 사용 → 유지
--  * 문제: 쓰기(INSERT/UPDATE/DELETE) 명시정책 없음 → 방어가 암묵적 default-deny에만 의존
--          정책 구성이 바뀌거나 광범위 정책이 추가되면 anon 쓰기가 열릴 위험(심층방어 부재)
--  * 대책: 쓰기를 admin 전용으로 명시 분리. 공개 읽기 유지.
--          (샘플 시드/적재는 service_role 키로 수행 — service_role은 RLS 우회하므로 영향 없음)
--
-- 의존: public.get_my_role() (rls_remediation_delta_v2/v3에서 이미 프로덕션에 생성됨)
--       만약 미존재 환경이면 아래 [0] 블록이 안전하게 생성(idempotent).
--
-- ⚠️ 적용 게이트: 본 DDL은 프로덕션 DB 구조 변경 → 절대규칙6에 따라 PO 사전승인 필요.
--    데이터 무손실(정책만 추가/조정, 컬럼·행 변경 없음). 롤백 하단 동봉.
-- ============================================================

-- ============================================================
-- [0] 역할 조회 함수 — 미존재 환경 대비 idempotent 생성 (이미 있으면 REPLACE)
--     SECURITY DEFINER로 users RLS 우회(무한재귀 방지)
-- ============================================================
CREATE OR REPLACE FUNCTION public.get_my_role()
RETURNS text
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT role FROM users WHERE user_id = auth.uid();
$$;


-- ============================================================
-- [1] RLS 활성 보장 (enable_public_access.sql에서 이미 활성. 멱등 재확인)
-- ============================================================
ALTER TABLE valuation_reports ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- [2] 공개 읽기 정책 — 의도된 공개. 단일 정책으로 정규화(중복 제거).
--     (enable_public_access.sql의 "Enable read access for all users" 및
--      과거 중복 생성됐을 수 있는 read 정책 정리 후 표준명으로 재생성)
-- ============================================================
DROP POLICY IF EXISTS "Enable read access for all users" ON valuation_reports;
DROP POLICY IF EXISTS "Allow public read access" ON valuation_reports;
DROP POLICY IF EXISTS "valuation_reports_select_public" ON valuation_reports;

CREATE POLICY "valuation_reports_select_public" ON valuation_reports
    FOR SELECT USING (true);


-- ============================================================
-- [3] 쓰기 정책 — admin 전용 명시 분리 (심층방어)
--     anon/authenticated에는 쓰기 정책이 없으므로 default-deny가 명시적으로 보강됨.
--     service_role(시드/적재 스크립트)은 RLS 자체를 우회하므로 영향 없음.
-- ============================================================
DROP POLICY IF EXISTS "valuation_reports_insert_admin" ON valuation_reports;
DROP POLICY IF EXISTS "valuation_reports_update_admin" ON valuation_reports;
DROP POLICY IF EXISTS "valuation_reports_delete_admin" ON valuation_reports;

CREATE POLICY "valuation_reports_insert_admin" ON valuation_reports
    FOR INSERT WITH CHECK (public.get_my_role() = 'admin');

CREATE POLICY "valuation_reports_update_admin" ON valuation_reports
    FOR UPDATE USING (public.get_my_role() = 'admin')
    WITH CHECK (public.get_my_role() = 'admin');

CREATE POLICY "valuation_reports_delete_admin" ON valuation_reports
    FOR DELETE USING (public.get_my_role() = 'admin');

-- 정책 설명 코멘트 (enable_public_access.sql의 코멘트 관행 유지)
COMMENT ON POLICY "valuation_reports_select_public" ON valuation_reports IS '공개 샘플 데이터 — 모든 사용자(비로그인 포함) 조회 허용 (link.html 기업목록)';
COMMENT ON POLICY "valuation_reports_insert_admin" ON valuation_reports IS '쓰기 admin 전용 — 시드/적재는 service_role(RLS 우회)로 수행';


-- ============================================================
-- [검증 쿼리] 적용 후 정책 구성 확인 (PO/검증자용)
--   기대: SELECT(public) 1개 + INSERT/UPDATE/DELETE(admin) 3개 = 4개
-- ============================================================
-- SELECT polname, cmd, qual, with_check
-- FROM pg_policies WHERE tablename = 'valuation_reports' ORDER BY cmd;


-- ============================================================
-- [롤백] 문제 발생 시 — 공개 읽기만 남기고 쓰기 정책 제거 (데이터 무손실)
-- ============================================================
-- DROP POLICY IF EXISTS "valuation_reports_insert_admin" ON valuation_reports;
-- DROP POLICY IF EXISTS "valuation_reports_update_admin" ON valuation_reports;
-- DROP POLICY IF EXISTS "valuation_reports_delete_admin" ON valuation_reports;
-- DROP POLICY IF EXISTS "valuation_reports_select_public" ON valuation_reports;
-- CREATE POLICY "Enable read access for all users" ON valuation_reports FOR SELECT USING (true);
