/**
 * @task S1D1
 * @description updated_at 자동 갱신 트리거
 */

-- ============================================
-- updated_at 자동 갱신 함수
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Users 테이블 트리거
-- ============================================
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Projects 테이블 트리거
-- ============================================
CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON public.projects
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Quotes 테이블 트리거
-- ============================================
CREATE TRIGGER update_quotes_updated_at
BEFORE UPDATE ON public.quotes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Negotiations 테이블 트리거
-- ============================================
CREATE TRIGGER update_negotiations_updated_at
BEFORE UPDATE ON public.negotiations
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Approval Points 테이블 트리거
-- ============================================
CREATE TRIGGER update_approval_points_updated_at
BEFORE UPDATE ON public.approval_points
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Valuation Results 테이블 트리거
-- ============================================
CREATE TRIGGER update_valuation_results_updated_at
BEFORE UPDATE ON public.valuation_results
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Drafts 테이블 트리거
-- ============================================
CREATE TRIGGER update_drafts_updated_at
BEFORE UPDATE ON public.drafts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Revisions 테이블 트리거
-- ============================================
CREATE TRIGGER update_revisions_updated_at
BEFORE UPDATE ON public.revisions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
