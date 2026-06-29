-- ============================================================
-- valuation_reports — 사용자(고객)당 등록 건수 상한 (스팸 견고 차단)
-- 작성: 2026-06-29 (PO 승인: 스팸 경고차단 DB측 적용)
-- 목적: 한 고객이 회사명 변형 등으로 무제한 INSERT 하는 스팸을 DB에서 차단
--       (프론트 20건 가드는 우회 가능 → DB 트리거로 최종 강제)
-- 안전: 멱등(CREATE OR REPLACE / DROP TRIGGER IF EXISTS) + 비파괴 + 롤백 동봉
--       user_id IS NULL(관리자·샘플)은 제한 없음 → 기존 샘플/관리자 입력 무영향
-- ============================================================

CREATE OR REPLACE FUNCTION public.enforce_valuation_reports_user_limit()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  cnt INTEGER;
  max_per_user CONSTANT INTEGER := 20;  -- 프론트(report-auto.html) 상한과 일치
BEGIN
  -- 소유자 없는 행(관리자 시딩·샘플)은 제한 대상 아님
  IF NEW.user_id IS NULL THEN
    RETURN NEW;
  END IF;
  SELECT COUNT(*) INTO cnt
    FROM public.valuation_reports
   WHERE user_id = NEW.user_id;
  IF cnt >= max_per_user THEN
    RAISE EXCEPTION '등록 가능한 회사 수(%)를 초과했습니다.', max_per_user
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_valuation_reports_user_limit ON public.valuation_reports;
CREATE TRIGGER trg_valuation_reports_user_limit
  BEFORE INSERT ON public.valuation_reports
  FOR EACH ROW
  EXECUTE FUNCTION public.enforce_valuation_reports_user_limit();

-- ============================================================
-- 검증 쿼리
--   SELECT tgname FROM pg_trigger WHERE tgrelid='public.valuation_reports'::regclass AND NOT tgisinternal;
--   → trg_valuation_reports_user_limit 확인
-- ============================================================

-- ============================================================
-- 롤백 (필요 시)
-- DROP TRIGGER IF EXISTS trg_valuation_reports_user_limit ON public.valuation_reports;
-- DROP FUNCTION IF EXISTS public.enforce_valuation_reports_user_limit();
-- ============================================================
