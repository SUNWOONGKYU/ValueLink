-- =============================================================================
-- ValueLink schema-v5-code-truth.sql
-- =============================================================================
-- 작성: 2026-06-11 (Alpha 분대 / ValueLink-platoon)
-- 근거: C:\ValueLink 코드 전수 역분석. "코드가 유일한 스키마 진실 소스" 원칙.
--       (전략: _WorkLog/2026_06_11__16.00_DB복구전략_연구결과.md — c-수정안)
--
-- 적용 대상: Supabase(PostgreSQL).
-- 성격: 멱등(IF NOT EXISTS) · 비파괴(DROP 금지, 구 테이블은 _legacy rename 보관).
--
-- 섹션 구성:
--   ① 구 valuation_results · projects → _legacy rename (IF EXISTS 가드)
--   ② 14테이블 CREATE (코드-진실)
--   ③ 인덱스
--   ④ RLS 정책
--   ⑤ updated_at 트리거
--
-- 역분석 출처(테이블 → 근거 파일):
--   valuation_results     : app/valuation-results/{dcf,relative,asset,intrinsic,tax}/page.tsx
--                           + types/valuation.ts (JSONB 형태)
--   projects              : app/api/projects/route.ts, app/projects/list|[id]/page.tsx,
--                           app/mypage/{customer,accountant}/page.tsx,
--                           app/api/evaluation-requests/route.ts (insert),
--                           lib/workflow/step-validator.ts (method 컬럼)
--   valuation_projects    : app/api/valuation/route.ts(owner_id), lib/workflow/workflow-manager.ts
--   evaluation_requests   : app/api/evaluation-requests/route.ts  (v4 정의 코드 대조 일치)
--   project_history       : app/api/project-history/route.ts      (v4 정의 코드 대조 일치)
--   support_cases         : app/mypage/supporter/page.tsx
--   partner_referrals     : app/mypage/partner/page.tsx
--   deal_news             : app/mypage/investor/page.tsx
--   investor_watchlist    : app/mypage/investor/page.tsx
--   workflow_approvals    : lib/workflow/workflow-manager.ts
--
-- 주의: approval_points / users / customers / accountants 는 실DB에 이미 존재(드라이런 확인)
--       → 이 파일은 건드리지 않는다. FK 대상(users.user_id UUID)으로만 참조한다.
-- =============================================================================


-- =============================================================================
-- ① 구 테이블 _legacy 보관 (비파괴)
-- =============================================================================
-- 구 valuation_results(method, calculation_details JSONB) · projects(customer_id 기준)는
-- 코드 기대 스키마와 불일치한다. DROP 하지 않고 _legacy 로 rename 하여 데이터를 보존한다.
-- 신규 동일명 테이블이 이미 존재하면(=재실행) rename 을 건너뛴다.

DO $$
BEGIN
  -- valuation_results: 구 스키마에 'method' 컬럼이 있으면 구 테이블로 판정 → 보관
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'valuation_results' AND column_name = 'method'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'valuation_results_legacy'
  ) THEN
    ALTER TABLE public.valuation_results RENAME TO valuation_results_legacy;
    RAISE NOTICE 'Renamed legacy valuation_results -> valuation_results_legacy';
  END IF;

  -- projects: 구 스키마에 'customer_id' 컬럼이 있으면 구 테이블로 판정 → 보관
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'projects' AND column_name = 'customer_id'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'projects_legacy'
  ) THEN
    ALTER TABLE public.projects RENAME TO projects_legacy;
    RAISE NOTICE 'Renamed legacy projects -> projects_legacy';
  END IF;
END $$;


-- =============================================================================
-- ② 14테이블 CREATE (코드-진실)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- A1. evaluation_requests — 평가 요청 (v4 정의 재사용, 코드 대조 일치)
--     코드: app/api/evaluation-requests/route.ts
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.evaluation_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,

    -- 기업 정보
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    revenue BIGINT,
    employees INTEGER,
    founded_date DATE,
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 평가 요청 정보
    valuation_purpose VARCHAR(50),
    requested_methods TEXT[],
    target_date DATE,
    requirements TEXT,
    budget_min INTEGER,
    budget_max INTEGER,

    -- 승인 상태
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_id UUID REFERENCES public.users(user_id),
    admin_comment TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A2. projects — 진행 중 프로젝트
--     PK project_id VARCHAR(50) (코드 generateProjectId: 'VL-YYYYMMDD-XXXX').
--     FK accountant_id 는 join alias 'projects_accountant_id_fkey' 로 명시 참조됨
--     (app/api/projects/route.ts: users!projects_accountant_id_fkey) → 제약명 고정 필수.
--     'method' 컬럼은 lib/workflow/step-validator.ts 가 select 함 → nullable 추가.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    project_id VARCHAR(50) PRIMARY KEY,
    request_id UUID REFERENCES public.evaluation_requests(request_id),
    user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    accountant_id UUID
        CONSTRAINT projects_accountant_id_fkey REFERENCES public.users(user_id) ON DELETE SET NULL,

    -- 기업 정보 (evaluation_requests 에서 복사)
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    revenue BIGINT,
    employees INTEGER,
    founded_date DATE,
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 평가 정보
    valuation_purpose VARCHAR(50),
    requested_methods TEXT[],
    method VARCHAR(30),            -- step-validator: `${method}_reports` 테이블명 도출용
    target_date DATE,
    requirements TEXT,
    budget_min INTEGER,
    budget_max INTEGER,

    -- 결제 정보 (step-validator: agreed_price, deposit_amount, deposit_paid_at, balance_paid_at)
    agreed_price INTEGER,
    deposit_amount INTEGER DEFAULT 0,
    deposit_paid_at TIMESTAMP WITH TIME ZONE,
    balance_paid_at TIMESTAMP WITH TIME ZONE,

    -- 진행 상태
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    current_step INTEGER DEFAULT 1,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A3. project_history — 완료된 프로젝트 (v4 정의 재사용, 코드 대조 일치)
--     코드: app/api/project-history/route.ts (history_id, project_id, completed_at)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.project_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL,
    request_id UUID,
    user_id UUID NOT NULL REFERENCES public.users(user_id),
    accountant_id UUID REFERENCES public.users(user_id),

    -- 기업 정보
    company_name_kr VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    business_registration_number VARCHAR(20),
    representative_name VARCHAR(100),
    industry VARCHAR(100),
    company_website VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 평가 정보
    valuation_purpose VARCHAR(50),
    completed_methods TEXT[],

    -- 결제 정보
    total_paid INTEGER,

    -- 완료 정보
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 최종 결과 요약
    final_values JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A4. valuation_projects — 워크플로 엔진 상태 (projects 와 별개 엔티티)
--     코드: app/api/valuation/route.ts, lib/workflow/workflow-manager.ts
--     select: project_id, status, current_step, progress, owner_id, updated_at
--     status 값: in_progress / human_approval / ... (workflow-manager ProjectStatus)
--     owner_id 는 권한 체크 주체(auth user) → users.user_id 참조.
--     코드에 INSERT 없음(외부 프로세스/트리거가 생성) → 표준 컬럼만 정의.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.valuation_projects (
    project_id VARCHAR(50) PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'in_progress',
    current_step INTEGER NOT NULL DEFAULT 1,
    progress NUMERIC DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A5. workflow_approvals — 단계별 승인 기록
--     코드: lib/workflow/workflow-manager.ts
--     select: id, project_id, step_number, status (status='approved' 체크)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workflow_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL,
    step_number INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected')),
    approved_by UUID REFERENCES public.users(user_id),
    rationale TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A6. valuation_results — 통합 평가 결과 (메서드별 개별 컬럼 + JSONB)
--     코드(진실): app/valuation-results/{dcf,relative,asset,intrinsic,tax}/page.tsx select
--     + types/valuation.ts (JSONB 컬럼의 형태)
--     단일 테이블 + valuation_method 로 메서드 구분. 모든 메서드 컬럼 nullable
--     (메서드별로 일부만 채워짐). 공통 컬럼은 5개 페이지 전부가 select.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.valuation_results (
    -- 공통 (BaseValuationResult — 5개 페이지 공통 select)
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(50) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    valuation_method VARCHAR(20) NOT NULL
        CHECK (valuation_method IN ('dcf', 'relative', 'asset', 'intrinsic', 'tax')),
    valuation_date DATE NOT NULL,
    shares_outstanding BIGINT,
    enterprise_value NUMERIC,
    equity_value NUMERIC,
    value_per_share NUMERIC,

    -- DCF (dcf/page.tsx)
    wacc_components JSONB,             -- WACCComponents
    fcff_projections JSONB,            -- FCFFYearData[]
    terminal_growth_rate NUMERIC,
    terminal_value NUMERIC,
    pv_terminal_value NUMERIC,
    pv_fcff_sum NUMERIC,
    operating_value NUMERIC,
    non_operating_assets NUMERIC,
    interest_bearing_debt NUMERIC,
    sensitivity_analysis JSONB,        -- { wacc_range, growth_range, value_matrix }

    -- Relative (relative/page.tsx)
    target_financials JSONB,           -- { net_income, equity, revenue, ebitda, net_debt }
    comparable_companies JSONB,        -- ComparableCompany[]
    average_multiples JSONB,           -- { per, pbr, psr, ev_ebitda, ev_sales }
    calc_method VARCHAR(10),           -- 'average' | 'median'
    weights JSONB,                     -- MultipleWeights
    per_share_values JSONB,            -- MultipleValues
    weighted_market_cap NUMERIC,
    liquidity_discount NUMERIC,
    discounted_value_per_share NUMERIC,

    -- Asset (asset/page.tsx)
    current_assets JSONB,              -- BalanceSheetItem[]
    non_current_assets JSONB,          -- BalanceSheetItem[]
    current_liabilities JSONB,         -- BalanceSheetItem[]
    non_current_liabilities JSONB,     -- BalanceSheetItem[]
    totals JSONB,                      -- AssetResult.totals
    nav_discount_rate NUMERIC,
    navps_original NUMERIC,
    navps_adjusted NUMERIC,

    -- Intrinsic (intrinsic/page.tsx)
    industry VARCHAR(100),
    capitalization_rate NUMERIC,
    income_3years JSONB,               -- { year1, year2, year3, average }
    nav_value NUMERIC,
    income_value NUMERIC,
    per_share_income_value NUMERIC,
    per_share_asset_value NUMERIC,
    asset_weight NUMERIC,
    income_weight NUMERIC,
    intrinsic_value_per_share NUMERIC,

    -- Tax (tax/page.tsx)
    company_type VARCHAR(20),          -- 'general' | 'realestate'
    yearly_profits JSONB,              -- YearlyProfitData[]
    weighted_avg_profit NUMERIC,
    discount_rate NUMERIC,
    profit_value_per_share NUMERIC,
    total_assets NUMERIC,
    total_liabilities NUMERIC,
    net_assets NUMERIC,
    asset_value_per_share NUMERIC,
    profit_weight NUMERIC,
    final_value_per_share NUMERIC,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A7. support_cases — 서포터 마이페이지 (CS 케이스)
--     코드: app/mypage/supporter/page.tsx
--     select: id, title, description, category, priority, status, requester_name,
--             requester_email, assigned_at, resolved_at, resolution_note
--     filter: supporter_id ; order: assigned_at
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.support_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supporter_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    priority VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    requester_name VARCHAR(100),
    requester_email VARCHAR(255),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A8. partner_referrals — 파트너 마이페이지 (추천/커미션)
--     코드: app/mypage/partner/page.tsx
--     select: id, referred_company_name, referred_email, status, commission_amount,
--             commission_status, referred_at, converted_at, notes
--     filter: partner_id ; order: referred_at
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.partner_referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    referred_company_name VARCHAR(200),
    referred_email VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    commission_amount NUMERIC DEFAULT 0,
    commission_status VARCHAR(20) DEFAULT 'pending',
    referred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    converted_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A9. deal_news — 투자자 마이페이지 (딜/투자 뉴스, 전체 공개)
--     코드: app/mypage/investor/page.tsx
--     select: id, company_name, industry, investment_stage, investor_names,
--             investment_amount, region, published_at, source_url, created_at
--     filter: published_at (gte) ; order: published_at
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.deal_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    investment_stage VARCHAR(50),
    investor_names TEXT[],
    investment_amount BIGINT,
    region VARCHAR(100),
    published_at TIMESTAMP WITH TIME ZONE,
    source_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- A10. investor_watchlist — 투자자 관심 기업
--     코드: app/mypage/investor/page.tsx
--     select: id, company_name, industry, last_deal_date, total_funding, notes
--     filter: user_id ; order: created_at
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.investor_watchlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    last_deal_date DATE,
    total_funding BIGINT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- =============================================================================
-- ③ 인덱스
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_eval_requests_user      ON public.evaluation_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_eval_requests_status    ON public.evaluation_requests(status);

CREATE INDEX IF NOT EXISTS idx_projects_user           ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_accountant     ON public.projects(accountant_id);
CREATE INDEX IF NOT EXISTS idx_projects_status         ON public.projects(status);

CREATE INDEX IF NOT EXISTS idx_project_history_user    ON public.project_history(user_id);
CREATE INDEX IF NOT EXISTS idx_project_history_proj    ON public.project_history(project_id);
CREATE INDEX IF NOT EXISTS idx_project_history_done    ON public.project_history(completed_at DESC);

CREATE INDEX IF NOT EXISTS idx_valproj_owner           ON public.valuation_projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_valproj_status          ON public.valuation_projects(status);

CREATE INDEX IF NOT EXISTS idx_wf_approvals_proj_step  ON public.workflow_approvals(project_id, step_number);

CREATE INDEX IF NOT EXISTS idx_valresults_proj_method  ON public.valuation_results(project_id, valuation_method);
CREATE INDEX IF NOT EXISTS idx_valresults_created      ON public.valuation_results(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_support_cases_supporter ON public.support_cases(supporter_id);
CREATE INDEX IF NOT EXISTS idx_support_cases_status    ON public.support_cases(status);

CREATE INDEX IF NOT EXISTS idx_partner_referrals_part  ON public.partner_referrals(partner_id);

CREATE INDEX IF NOT EXISTS idx_deal_news_published     ON public.deal_news(published_at DESC);

CREATE INDEX IF NOT EXISTS idx_investor_watchlist_user ON public.investor_watchlist(user_id);


-- =============================================================================
-- ④ RLS 정책 (rls-policies.sql 관례: auth.uid() 기반 소유권)
-- =============================================================================
ALTER TABLE public.evaluation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects            ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_history     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.valuation_projects  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_approvals  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.valuation_results   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_cases       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.partner_referrals   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_news           ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investor_watchlist  ENABLE ROW LEVEL SECURITY;

-- Postgres 는 CREATE POLICY IF NOT EXISTS 를 지원하지 않으므로 DROP IF EXISTS 후 생성(멱등).
DO $$
BEGIN
  -- evaluation_requests: 본인 요청만
  DROP POLICY IF EXISTS "eval_req_owner" ON public.evaluation_requests;
  CREATE POLICY "eval_req_owner" ON public.evaluation_requests FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

  -- projects: 소유자 또는 배정 회계사
  DROP POLICY IF EXISTS "projects_owner_or_accountant" ON public.projects;
  CREATE POLICY "projects_owner_or_accountant" ON public.projects FOR ALL
    USING (auth.uid() = user_id OR auth.uid() = accountant_id)
    WITH CHECK (auth.uid() = user_id OR auth.uid() = accountant_id);

  -- project_history: 소유자 또는 회계사 (읽기 중심)
  DROP POLICY IF EXISTS "project_history_owner" ON public.project_history;
  CREATE POLICY "project_history_owner" ON public.project_history FOR SELECT
    USING (auth.uid() = user_id OR auth.uid() = accountant_id);

  -- valuation_projects: owner 만
  DROP POLICY IF EXISTS "valproj_owner" ON public.valuation_projects;
  CREATE POLICY "valproj_owner" ON public.valuation_projects FOR ALL
    USING (auth.uid() = owner_id) WITH CHECK (auth.uid() = owner_id);

  -- workflow_approvals: 해당 valuation_project 의 owner
  DROP POLICY IF EXISTS "wf_approvals_owner" ON public.workflow_approvals;
  CREATE POLICY "wf_approvals_owner" ON public.workflow_approvals FOR ALL
    USING (EXISTS (
      SELECT 1 FROM public.valuation_projects vp
      WHERE vp.project_id = workflow_approvals.project_id AND vp.owner_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
      SELECT 1 FROM public.valuation_projects vp
      WHERE vp.project_id = workflow_approvals.project_id AND vp.owner_id = auth.uid()
    ));

  -- valuation_results: 해당 project 의 소유자/회계사
  DROP POLICY IF EXISTS "valresults_project_member" ON public.valuation_results;
  CREATE POLICY "valresults_project_member" ON public.valuation_results FOR ALL
    USING (EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.project_id = valuation_results.project_id
        AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid())
    ))
    WITH CHECK (EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.project_id = valuation_results.project_id
        AND (p.user_id = auth.uid() OR p.accountant_id = auth.uid())
    ));

  -- support_cases: 배정된 서포터만
  DROP POLICY IF EXISTS "support_cases_supporter" ON public.support_cases;
  CREATE POLICY "support_cases_supporter" ON public.support_cases FOR ALL
    USING (auth.uid() = supporter_id) WITH CHECK (auth.uid() = supporter_id);

  -- partner_referrals: 파트너 본인
  DROP POLICY IF EXISTS "partner_referrals_partner" ON public.partner_referrals;
  CREATE POLICY "partner_referrals_partner" ON public.partner_referrals FOR ALL
    USING (auth.uid() = partner_id) WITH CHECK (auth.uid() = partner_id);

  -- deal_news: 전체 공개 읽기 (코드가 user 필터 없이 전체 count/list 조회)
  DROP POLICY IF EXISTS "deal_news_read_all" ON public.deal_news;
  CREATE POLICY "deal_news_read_all" ON public.deal_news FOR SELECT
    USING (auth.role() = 'authenticated');

  -- investor_watchlist: 본인 관심 목록
  DROP POLICY IF EXISTS "investor_watchlist_owner" ON public.investor_watchlist;
  CREATE POLICY "investor_watchlist_owner" ON public.investor_watchlist FOR ALL
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
END $$;


-- =============================================================================
-- ⑤ updated_at 트리거 (triggers-v4.sql 관례: update_updated_at_column())
-- =============================================================================
-- 함수가 없을 수 있으므로 멱등 정의(이미 있으면 REPLACE).
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- updated_at 컬럼이 있는 테이블에만 트리거 부착. CREATE TRIGGER 는 IF NOT EXISTS 미지원
-- → 멱등 보장 위해 DROP 후 생성.
DO $$
DECLARE
  t TEXT;
  tables TEXT[] := ARRAY[
    'evaluation_requests', 'projects', 'valuation_projects', 'workflow_approvals',
    'valuation_results', 'support_cases', 'partner_referrals', 'investor_watchlist'
  ];
BEGIN
  FOREACH t IN ARRAY tables LOOP
    EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON public.%I;', t, t);
    EXECUTE format(
      'CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON public.%I
       FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();', t, t);
  END LOOP;
END $$;

-- project_history, deal_news 는 updated_at 컬럼이 없으므로 트리거 제외.

-- =============================================================================
-- END OF schema-v5-code-truth.sql
-- =============================================================================
