-- ============================================================
-- valuation_reports — 로그인 고객 본인 평가 등록 지원
-- 작성: 2026-06-29 (PO 승인: 평가액 Link 등록 / 로그인 고객 방식)
-- 목적: 평가 완료 시 로그인 고객이 본인 평가를 Link 페이지(공개)에 등록
-- 의존: public.get_my_role() (백호작전 v2/v3에서 생성됨)
-- 안전: 비파괴(ADD COLUMN IF NOT EXISTS) + 멱등(DROP POLICY IF EXISTS) + 롤백 동봉
-- ============================================================

-- 1) 등록자 추적용 user_id 컬럼 (비파괴 ADD, nullable — 기존 샘플행 영향 없음)
ALTER TABLE public.valuation_reports
  ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- 2) RLS 활성 확인 (이미 활성이면 무영향)
ALTER TABLE public.valuation_reports ENABLE ROW LEVEL SECURITY;

-- 3) 고객 본인 INSERT 정책
--    로그인 + role='customer' + user_id가 본인(auth.uid())일 때만 등록 허용
--    → 익명/타인사칭/가짜 대량등록 차단 (등록자 추적 가능)
DROP POLICY IF EXISTS "valuation_reports_insert_customer" ON public.valuation_reports;
CREATE POLICY "valuation_reports_insert_customer" ON public.valuation_reports
  FOR INSERT TO authenticated
  WITH CHECK (
    user_id = auth.uid()
    AND public.get_my_role() = 'customer'
  );

-- 4) 고객 본인 UPDATE 정책 (재평가 시 본인 행만 수정 — admin 정책은 별도 유지)
DROP POLICY IF EXISTS "valuation_reports_update_own" ON public.valuation_reports;
CREATE POLICY "valuation_reports_update_own" ON public.valuation_reports
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid() AND public.get_my_role() = 'customer')
  WITH CHECK (user_id = auth.uid() AND public.get_my_role() = 'customer');

-- (DELETE는 고객에게 열지 않음 — admin 전용 유지)

-- ============================================================
-- 검증 쿼리
--   SELECT policyname, cmd FROM pg_policies WHERE tablename='valuation_reports';
--   → select_public / insert_admin / update_admin / delete_admin
--     + insert_customer / update_own 확인
-- ============================================================

-- ============================================================
-- 롤백 (필요 시)
-- DROP POLICY IF EXISTS "valuation_reports_insert_customer" ON public.valuation_reports;
-- DROP POLICY IF EXISTS "valuation_reports_update_own" ON public.valuation_reports;
-- ALTER TABLE public.valuation_reports DROP COLUMN IF EXISTS user_id;
-- ============================================================
