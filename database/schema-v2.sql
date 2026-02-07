/**
 * ValueLink 데이터베이스 스키마 v2.0
 * 총 33개 테이블 (기본 3개 + 평가법별 30개)
 *
 * 작성일: 2026-02-07
 * 승인: PO 승인 완료
 */

-- ============================================
-- 1. Users 테이블 (사용자 프로필/역할)
-- ============================================
CREATE TABLE public.users (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone TEXT,
  company_name TEXT,
  role TEXT NOT NULL CHECK (role IN ('customer', 'accountant', 'admin', 'investor', 'partner', 'supporter')),
  profile_image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_role ON public.users(role);

-- ============================================
-- 2. Projects 테이블 (프로젝트 마스터 - 15단계)
-- ============================================
CREATE TABLE public.projects (
  project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  accountant_id UUID REFERENCES public.users(user_id) ON DELETE SET NULL,
  project_name TEXT NOT NULL,
  company_name TEXT,
  valuation_method TEXT NOT NULL CHECK (valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
    'pending',           -- 대기
    'quoted',            -- 견적 발송
    'negotiating',       -- 협상 중
    'approved',          -- 승인됨
    'deposit_paid',      -- 계약금 결제
    'documents_uploaded',-- 자료 업로드
    'in_progress',       -- 평가 진행 중
    'draft_ready',       -- 초안 완료
    'revision_requested',-- 수정 요청
    'final_ready',       -- 최종안 완료
    'balance_paid',      -- 잔금 결제
    'completed',         -- 완료
    'cancelled'          -- 취소
  )),
  current_step INT DEFAULT 1 CHECK (current_step BETWEEN 1 AND 15),
  -- 15단계: 1.안내문 2.신청 3.관리자승인 4.계약금결제 5.자료제출
  --         6.데이터수집 7.평가진행 8.회계사검토 9.초안생성 10.초안확인
  --         11.수정요청 12.최종안작성 13.최종안확인 14.잔금결제 15.보고서수령
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_user ON public.projects(user_id);
CREATE INDEX idx_projects_accountant ON public.projects(accountant_id);
CREATE INDEX idx_projects_status ON public.projects(status);

-- ============================================
-- 3. Payments 테이블 (결제 정보)
-- ============================================
CREATE TABLE public.payments (
  payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

  -- 고객 제시 금액
  customer_proposed_amount DECIMAL(12, 2),

  -- 관리자 승인 금액
  admin_approved_amount DECIMAL(12, 2),
  admin_approved_by UUID REFERENCES public.users(user_id),
  admin_approved_at TIMESTAMP WITH TIME ZONE,

  -- 계약금/잔금
  deposit_amount DECIMAL(12, 2),
  balance_amount DECIMAL(12, 2),

  -- 결제 일시
  deposit_paid_at TIMESTAMP WITH TIME ZONE,
  balance_paid_at TIMESTAMP WITH TIME ZONE,

  -- 상태
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
    'pending',        -- 대기
    'proposed',       -- 고객 제시
    'approved',       -- 관리자 승인
    'deposit_paid',   -- 계약금 결제
    'balance_paid',   -- 잔금 결제
    'completed',      -- 완료
    'rejected'        -- 거부
  )),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payments_project ON public.payments(project_id);
CREATE INDEX idx_payments_status ON public.payments(status);

-- ============================================
-- 4-8. Documents 테이블 (5개 - 평가법별 분리)
-- ============================================

-- 4. DCF Documents
CREATE TABLE public.dcf_documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_category TEXT NOT NULL CHECK (document_category IN (
    'financial',       -- 재무제표 3개년 (필수)
    'business_plan',   -- 사업계획서 5개년 (필수)
    'shareholder',     -- 주주명부 (필수)
    'capex',           -- CAPEX 계획 (선택)
    'working_capital', -- 운전자본 계획 (선택)
    'others'           -- 기타 자료 (선택)
  )),
  is_required BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_dcf_documents_project ON public.dcf_documents(project_id);

-- 5. Relative Documents
CREATE TABLE public.relative_documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_category TEXT NOT NULL CHECK (document_category IN (
    'financial',       -- 재무제표 (필수)
    'shareholder',     -- 주주명부 (필수)
    'others'           -- 기타 자료 (선택)
  )),
  is_required BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_relative_documents_project ON public.relative_documents(project_id);

-- 6. Intrinsic Documents
CREATE TABLE public.intrinsic_documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_category TEXT NOT NULL CHECK (document_category IN (
    'financial',       -- 재무제표 (필수)
    'business_plan',   -- 사업계획서 (필수)
    'shareholder',     -- 주주명부 (필수)
    'others'           -- 기타 자료 (선택)
  )),
  is_required BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_intrinsic_documents_project ON public.intrinsic_documents(project_id);

-- 7. Asset Documents
CREATE TABLE public.asset_documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_category TEXT NOT NULL CHECK (document_category IN (
    'financial',         -- 재무제표 (필수)
    'asset_list',        -- 자산목록 (필수)
    'appraisal',         -- 감정평가서 (선택)
    'property_registry', -- 부동산등기부등본 (선택)
    'shareholder',       -- 주주명부 (필수)
    'others'             -- 기타 자료 (선택)
  )),
  is_required BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_asset_documents_project ON public.asset_documents(project_id);

-- 8. Tax Documents
CREATE TABLE public.tax_documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  document_category TEXT NOT NULL CHECK (document_category IN (
    'financial',          -- 재무제표 3개년 (필수)
    'tax_adjustment',     -- 세무조정계산서 (필수)
    'shareholder',        -- 주주명부 (필수)
    'corporate_registry', -- 법인등기부등본 (필수)
    'others'              -- 기타 자료 (선택)
  )),
  is_required BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tax_documents_project ON public.tax_documents(project_id);

-- ============================================
-- 9-13. Approval Points 테이블 (5개 - 평가법별 분리)
-- ============================================

-- 9. DCF Approval Points (8개 포인트: JP001-JP008)
CREATE TABLE public.dcf_approval_points (
  approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  point_id TEXT NOT NULL CHECK (point_id IN ('JP001', 'JP002', 'JP003', 'JP004', 'JP005', 'JP006', 'JP007', 'JP008')),
  point_name TEXT NOT NULL,
  -- JP001: 매출성장률, JP002: 영업이익률, JP003: WACC, JP004: 영구성장률
  -- JP005: 예측기간, JP006: CAPEX비율, JP007: 운전자본변동, JP008: 베타계수
  importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
  ai_scenarios JSONB,       -- AI 3가지 시나리오
  ai_recommended JSONB,     -- AI 추천값
  approved_value JSONB,     -- 회계사 승인값
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
  approved_by UUID REFERENCES public.users(user_id),
  approved_at TIMESTAMP WITH TIME ZONE,
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, point_id)
);

CREATE INDEX idx_dcf_approval_points_project ON public.dcf_approval_points(project_id);

-- 10. Relative Approval Points (4개 포인트: JP009-JP012)
CREATE TABLE public.relative_approval_points (
  approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  point_id TEXT NOT NULL CHECK (point_id IN ('JP009', 'JP010', 'JP011', 'JP012')),
  point_name TEXT NOT NULL,
  -- JP009: 비교기업선정, JP010: 적용배수, JP011: 업종배수, JP012: 비상장할인율
  importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
  ai_scenarios JSONB,
  ai_recommended JSONB,
  approved_value JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
  approved_by UUID REFERENCES public.users(user_id),
  approved_at TIMESTAMP WITH TIME ZONE,
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, point_id)
);

CREATE INDEX idx_relative_approval_points_project ON public.relative_approval_points(project_id);

-- 11. Intrinsic Approval Points (2개 포인트: JP019-JP020)
CREATE TABLE public.intrinsic_approval_points (
  approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  point_id TEXT NOT NULL CHECK (point_id IN ('JP019', 'JP020')),
  point_name TEXT NOT NULL,
  -- JP019: 수익가치법, JP020: 자산/수익 가중치
  importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
  ai_scenarios JSONB,
  ai_recommended JSONB,
  approved_value JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
  approved_by UUID REFERENCES public.users(user_id),
  approved_at TIMESTAMP WITH TIME ZONE,
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, point_id)
);

CREATE INDEX idx_intrinsic_approval_points_project ON public.intrinsic_approval_points(project_id);

-- 12. Asset Approval Points (6개 포인트: JP013-JP018)
CREATE TABLE public.asset_approval_points (
  approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  point_id TEXT NOT NULL CHECK (point_id IN ('JP013', 'JP014', 'JP015', 'JP016', 'JP017', 'JP018')),
  point_name TEXT NOT NULL,
  -- JP013: 토지/건물감정가, JP014: 특허권가치, JP015: 우발부채
  -- JP016: 대손충당금, JP017: 재고자산NRV, JP018: 비상장주식평가
  importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
  ai_scenarios JSONB,
  ai_recommended JSONB,
  approved_value JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
  approved_by UUID REFERENCES public.users(user_id),
  approved_at TIMESTAMP WITH TIME ZONE,
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, point_id)
);

CREATE INDEX idx_asset_approval_points_project ON public.asset_approval_points(project_id);

-- 13. Tax Approval Points (2개 포인트: JP021-JP022)
CREATE TABLE public.tax_approval_points (
  approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  point_id TEXT NOT NULL CHECK (point_id IN ('JP021', 'JP022')),
  point_name TEXT NOT NULL,
  -- JP021: 3년평균순손익, JP022: 지분율
  importance INT NOT NULL CHECK (importance BETWEEN 1 AND 3),
  ai_scenarios JSONB,
  ai_recommended JSONB,
  approved_value JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'custom', 'rejected')),
  approved_by UUID REFERENCES public.users(user_id),
  approved_at TIMESTAMP WITH TIME ZONE,
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, point_id)
);

CREATE INDEX idx_tax_approval_points_project ON public.tax_approval_points(project_id);

-- ============================================
-- 14-18. Results 테이블 (5개 - 평가법별 분리)
-- ============================================

-- 14. DCF Results
CREATE TABLE public.dcf_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

  -- 핵심 결과
  enterprise_value DECIMAL(20, 2),      -- 기업가치
  equity_value DECIMAL(20, 2),          -- 자기자본가치
  value_per_share DECIMAL(20, 2),       -- 주당가치

  -- DCF 특화 데이터
  wacc DECIMAL(6, 4),                   -- 할인율
  terminal_growth_rate DECIMAL(6, 4),   -- 영구성장률
  forecast_period INT,                  -- 예측기간 (년)
  cash_flows JSONB,                     -- 연도별 현금흐름
  terminal_value DECIMAL(20, 2),        -- 터미널밸류
  non_operating_assets DECIMAL(20, 2),  -- 비영업자산
  interest_bearing_debt DECIMAL(20, 2), -- 이자부부채

  -- 민감도 분석
  sensitivity_analysis JSONB,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id)
);

CREATE INDEX idx_dcf_results_project ON public.dcf_results(project_id);

-- 15. Relative Results
CREATE TABLE public.relative_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

  -- 핵심 결과
  enterprise_value DECIMAL(20, 2),
  equity_value DECIMAL(20, 2),
  value_per_share DECIMAL(20, 2),

  -- 상대가치 특화 데이터
  comparable_companies JSONB,           -- 비교기업 목록
  per_multiple DECIMAL(10, 2),          -- PER 배수
  pbr_multiple DECIMAL(10, 2),          -- PBR 배수
  psr_multiple DECIMAL(10, 2),          -- PSR 배수
  ev_ebitda_multiple DECIMAL(10, 2),    -- EV/EBITDA 배수
  ev_sales_multiple DECIMAL(10, 2),     -- EV/Sales 배수
  applied_weights JSONB,                -- 적용 가중치
  unlisted_discount DECIMAL(6, 4),      -- 비상장 할인율

  -- 배수별 결과
  per_based_value DECIMAL(20, 2),
  pbr_based_value DECIMAL(20, 2),
  psr_based_value DECIMAL(20, 2),
  ev_ebitda_based_value DECIMAL(20, 2),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id)
);

CREATE INDEX idx_relative_results_project ON public.relative_results(project_id);

-- 16. Intrinsic Results (본질가치 - 자본시장법)
CREATE TABLE public.intrinsic_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

  -- 핵심 결과
  enterprise_value DECIMAL(20, 2),
  equity_value DECIMAL(20, 2),
  value_per_share DECIMAL(20, 2),

  -- 본질가치 특화 데이터
  income_value DECIMAL(20, 2),          -- 수익가치
  asset_value DECIMAL(20, 2),           -- 자산가치
  income_weight DECIMAL(4, 2),          -- 수익가치 가중치 (보통 1.5)
  asset_weight DECIMAL(4, 2),           -- 자산가치 가중치 (보통 1)
  weighted_value DECIMAL(20, 2),        -- 가중평균 가치

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id)
);

CREATE INDEX idx_intrinsic_results_project ON public.intrinsic_results(project_id);

-- 17. Asset Results (자산가치)
CREATE TABLE public.asset_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

  -- 핵심 결과
  enterprise_value DECIMAL(20, 2),
  equity_value DECIMAL(20, 2),
  value_per_share DECIMAL(20, 2),

  -- 자산가치 특화 데이터
  total_assets DECIMAL(20, 2),          -- 총자산
  total_liabilities DECIMAL(20, 2),     -- 총부채
  net_asset_value DECIMAL(20, 2),       -- 순자산가치

  -- 자산별 공정가치
  land_fair_value DECIMAL(20, 2),
  building_fair_value DECIMAL(20, 2),
  equipment_fair_value DECIMAL(20, 2),
  intangible_fair_value DECIMAL(20, 2),
  investment_fair_value DECIMAL(20, 2),

  -- 부채 조정
  contingent_liabilities DECIMAL(20, 2),-- 우발부채

  -- 상세 내역
  asset_details JSONB,
  liability_details JSONB,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id)
);

CREATE INDEX idx_asset_results_project ON public.asset_results(project_id);

-- 18. Tax Results (상증세법)
CREATE TABLE public.tax_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

  -- 핵심 결과
  enterprise_value DECIMAL(20, 2),
  equity_value DECIMAL(20, 2),
  value_per_share DECIMAL(20, 2),

  -- 상증세법 특화 데이터
  avg_net_income_3yr DECIMAL(20, 2),    -- 3년 평균 순손익
  net_asset_value DECIMAL(20, 2),       -- 순자산가치
  income_value DECIMAL(20, 2),          -- 수익가치 (순손익 × 배수)

  -- 가중치 (업종별 상이)
  income_weight DECIMAL(4, 2),          -- 수익가치 가중치
  asset_weight DECIMAL(4, 2),           -- 자산가치 가중치

  -- 지분율 관련
  ownership_ratio DECIMAL(6, 4),        -- 지분율
  control_premium DECIMAL(6, 4),        -- 경영권 프리미엄
  minority_discount DECIMAL(6, 4),      -- 소수주주 할인

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id)
);

CREATE INDEX idx_tax_results_project ON public.tax_results(project_id);

-- ============================================
-- 19-23. Drafts 테이블 (5개 - 평가법별 분리)
-- ============================================

-- 19. DCF Drafts
CREATE TABLE public.dcf_drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,

  -- 9개 섹션 내용
  section_summary TEXT,          -- I. 요약
  section_overview TEXT,         -- II. 평가 개요
  section_company TEXT,          -- III. 회사 개요
  section_financial TEXT,        -- IV. 재무 분석
  section_methodology TEXT,      -- V. 평가 방법론
  section_results TEXT,          -- VI. 평가 결과
  section_sensitivity TEXT,      -- VII. 민감도 분석
  section_conclusion TEXT,       -- VIII. 결론
  section_appendix TEXT,         -- IX. 부록

  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  submitted_at TIMESTAMP WITH TIME ZONE,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_dcf_drafts_project ON public.dcf_drafts(project_id);

-- 20. Relative Drafts
CREATE TABLE public.relative_drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  section_summary TEXT,
  section_overview TEXT,
  section_company TEXT,
  section_financial TEXT,
  section_methodology TEXT,
  section_results TEXT,
  section_sensitivity TEXT,
  section_conclusion TEXT,
  section_appendix TEXT,
  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  submitted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_relative_drafts_project ON public.relative_drafts(project_id);

-- 21. Intrinsic Drafts
CREATE TABLE public.intrinsic_drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  section_summary TEXT,
  section_overview TEXT,
  section_company TEXT,
  section_financial TEXT,
  section_methodology TEXT,
  section_results TEXT,
  section_sensitivity TEXT,
  section_conclusion TEXT,
  section_appendix TEXT,
  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  submitted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_intrinsic_drafts_project ON public.intrinsic_drafts(project_id);

-- 22. Asset Drafts
CREATE TABLE public.asset_drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  section_summary TEXT,
  section_overview TEXT,
  section_company TEXT,
  section_financial TEXT,
  section_methodology TEXT,
  section_results TEXT,
  section_sensitivity TEXT,
  section_conclusion TEXT,
  section_appendix TEXT,
  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  submitted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_asset_drafts_project ON public.asset_drafts(project_id);

-- 23. Tax Drafts
CREATE TABLE public.tax_drafts (
  draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  version INT NOT NULL DEFAULT 1,
  section_summary TEXT,
  section_overview TEXT,
  section_company TEXT,
  section_financial TEXT,
  section_methodology TEXT,
  section_results TEXT,
  section_sensitivity TEXT,
  section_conclusion TEXT,
  section_appendix TEXT,
  generated_by TEXT NOT NULL CHECK (generated_by IN ('ai', 'accountant')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
  submitted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tax_drafts_project ON public.tax_drafts(project_id);

-- ============================================
-- 24-28. Revisions 테이블 (5개 - 평가법별 분리)
-- ============================================

-- 24. DCF Revisions
CREATE TABLE public.dcf_revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.dcf_drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL,          -- 수정 요청 섹션
  comment TEXT NOT NULL,          -- 수정 요청 내용
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  resolved_by UUID REFERENCES public.users(user_id),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_dcf_revisions_draft ON public.dcf_revisions(draft_id);

-- 25. Relative Revisions
CREATE TABLE public.relative_revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.relative_drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL,
  comment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  resolved_by UUID REFERENCES public.users(user_id),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_relative_revisions_draft ON public.relative_revisions(draft_id);

-- 26. Intrinsic Revisions
CREATE TABLE public.intrinsic_revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.intrinsic_drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL,
  comment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  resolved_by UUID REFERENCES public.users(user_id),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_intrinsic_revisions_draft ON public.intrinsic_revisions(draft_id);

-- 27. Asset Revisions
CREATE TABLE public.asset_revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.asset_drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL,
  comment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  resolved_by UUID REFERENCES public.users(user_id),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_asset_revisions_draft ON public.asset_revisions(draft_id);

-- 28. Tax Revisions
CREATE TABLE public.tax_revisions (
  revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID NOT NULL REFERENCES public.tax_drafts(draft_id) ON DELETE CASCADE,
  requested_by UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
  section TEXT NOT NULL,
  comment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
  resolved_by UUID REFERENCES public.users(user_id),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tax_revisions_draft ON public.tax_revisions(draft_id);

-- ============================================
-- 29-33. Reports 테이블 (5개 - 평가법별 분리)
-- ============================================

-- 29. DCF Reports
CREATE TABLE public.dcf_reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.dcf_drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT DEFAULT 'application/pdf',
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  downloaded_at TIMESTAMP WITH TIME ZONE,
  download_count INT DEFAULT 0
);

CREATE INDEX idx_dcf_reports_project ON public.dcf_reports(project_id);

-- 30. Relative Reports
CREATE TABLE public.relative_reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.relative_drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT DEFAULT 'application/pdf',
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  downloaded_at TIMESTAMP WITH TIME ZONE,
  download_count INT DEFAULT 0
);

CREATE INDEX idx_relative_reports_project ON public.relative_reports(project_id);

-- 31. Intrinsic Reports
CREATE TABLE public.intrinsic_reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.intrinsic_drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT DEFAULT 'application/pdf',
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  downloaded_at TIMESTAMP WITH TIME ZONE,
  download_count INT DEFAULT 0
);

CREATE INDEX idx_intrinsic_reports_project ON public.intrinsic_reports(project_id);

-- 32. Asset Reports
CREATE TABLE public.asset_reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.asset_drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT DEFAULT 'application/pdf',
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  downloaded_at TIMESTAMP WITH TIME ZONE,
  download_count INT DEFAULT 0
);

CREATE INDEX idx_asset_reports_project ON public.asset_reports(project_id);

-- 33. Tax Reports
CREATE TABLE public.tax_reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
  draft_id UUID NOT NULL REFERENCES public.tax_drafts(draft_id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT DEFAULT 'application/pdf',
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  downloaded_at TIMESTAMP WITH TIME ZONE,
  download_count INT DEFAULT 0
);

CREATE INDEX idx_tax_reports_project ON public.tax_reports(project_id);
