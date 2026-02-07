/**
 * ValueLink 트리거 v2.0
 * updated_at 자동 갱신 트리거
 *
 * 작성일: 2026-02-07
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
-- 기본 테이블 트리거
-- ============================================
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON public.projects
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at
BEFORE UPDATE ON public.payments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Approval Points 트리거 (5개)
-- ============================================
CREATE TRIGGER update_dcf_approval_points_updated_at
BEFORE UPDATE ON public.dcf_approval_points
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relative_approval_points_updated_at
BEFORE UPDATE ON public.relative_approval_points
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_intrinsic_approval_points_updated_at
BEFORE UPDATE ON public.intrinsic_approval_points
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_asset_approval_points_updated_at
BEFORE UPDATE ON public.asset_approval_points
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_approval_points_updated_at
BEFORE UPDATE ON public.tax_approval_points
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Results 트리거 (5개)
-- ============================================
CREATE TRIGGER update_dcf_results_updated_at
BEFORE UPDATE ON public.dcf_results
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relative_results_updated_at
BEFORE UPDATE ON public.relative_results
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_intrinsic_results_updated_at
BEFORE UPDATE ON public.intrinsic_results
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_asset_results_updated_at
BEFORE UPDATE ON public.asset_results
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_results_updated_at
BEFORE UPDATE ON public.tax_results
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Drafts 트리거 (5개)
-- ============================================
CREATE TRIGGER update_dcf_drafts_updated_at
BEFORE UPDATE ON public.dcf_drafts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relative_drafts_updated_at
BEFORE UPDATE ON public.relative_drafts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_intrinsic_drafts_updated_at
BEFORE UPDATE ON public.intrinsic_drafts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_asset_drafts_updated_at
BEFORE UPDATE ON public.asset_drafts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_drafts_updated_at
BEFORE UPDATE ON public.tax_drafts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Revisions 트리거 (5개)
-- ============================================
CREATE TRIGGER update_dcf_revisions_updated_at
BEFORE UPDATE ON public.dcf_revisions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relative_revisions_updated_at
BEFORE UPDATE ON public.relative_revisions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_intrinsic_revisions_updated_at
BEFORE UPDATE ON public.intrinsic_revisions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_asset_revisions_updated_at
BEFORE UPDATE ON public.asset_revisions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_revisions_updated_at
BEFORE UPDATE ON public.tax_revisions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
