-- Projects 테이블 수정
-- 담당 공인회계사 필드 추가 및 누락된 필드 추가

-- 1. assigned_accountant_id 컬럼 추가
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS assigned_accountant_id VARCHAR(20);

-- 2. 외래키 제약 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_projects_accountant_id'
    ) THEN
        ALTER TABLE projects
        ADD CONSTRAINT fk_projects_accountant_id
        FOREIGN KEY (assigned_accountant_id) REFERENCES accountants(accountant_id) ON DELETE SET NULL;
    END IF;
END $$;

-- 3. assigned_accountant_id 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_projects_accountant ON projects(assigned_accountant_id);

-- 4. project-create.html에서 사용하는 누락된 필드 추가
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS company_name_kr VARCHAR(100),
ADD COLUMN IF NOT EXISTS company_name_en VARCHAR(100),
ADD COLUMN IF NOT EXISTS budget VARCHAR(50),  -- 예: "500만원"
ADD COLUMN IF NOT EXISTS valuation_date DATE,
ADD COLUMN IF NOT EXISTS purpose TEXT,
ADD COLUMN IF NOT EXISTS assigned_accountant VARCHAR(50);  -- 임시 필드 (호환성)

-- 5. 평가 방법별 상태 필드 추가 (project-create.html에서 사용)
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS dcf_status VARCHAR(20) DEFAULT 'not_selected',
ADD COLUMN IF NOT EXISTS relative_status VARCHAR(20) DEFAULT 'not_selected',
ADD COLUMN IF NOT EXISTS intrinsic_status VARCHAR(20) DEFAULT 'not_selected',
ADD COLUMN IF NOT EXISTS asset_status VARCHAR(20) DEFAULT 'not_selected',
ADD COLUMN IF NOT EXISTS tax_status VARCHAR(20) DEFAULT 'not_selected';

-- 6. 평가 결과 저장 필드 추가
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS valuation_results JSONB;

-- 7. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_projects_company_kr ON projects(company_name_kr);
CREATE INDEX IF NOT EXISTS idx_projects_company_en ON projects(company_name_en);
CREATE INDEX IF NOT EXISTS idx_projects_valuation_date ON projects(valuation_date);

-- 8. CHECK 제약 추가 (상태 값 검증)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_projects_status'
    ) THEN
        ALTER TABLE projects
        ADD CONSTRAINT chk_projects_status
        CHECK (status IN ('pending', 'approved', 'rejected', 'in_progress', 'completed', 'cancelled'));
    END IF;
END $$;

-- 9. CHECK 제약 추가 (평가 방법별 상태 검증)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_projects_method_status'
    ) THEN
        ALTER TABLE projects
        ADD CONSTRAINT chk_projects_method_status
        CHECK (
            dcf_status IN ('not_selected', 'pending', 'in_progress', 'completed') AND
            relative_status IN ('not_selected', 'pending', 'in_progress', 'completed') AND
            intrinsic_status IN ('not_selected', 'pending', 'in_progress', 'completed') AND
            asset_status IN ('not_selected', 'pending', 'in_progress', 'completed') AND
            tax_status IN ('not_selected', 'pending', 'in_progress', 'completed')
        );
    END IF;
END $$;

-- 10. 컬럼 설명 추가
COMMENT ON COLUMN projects.assigned_accountant_id IS '담당 공인회계사 ID (accountants 테이블 참조)';
COMMENT ON COLUMN projects.company_name_kr IS '회사명 (국문)';
COMMENT ON COLUMN projects.company_name_en IS '회사명 (영문)';
COMMENT ON COLUMN projects.budget IS '고객 예산';
COMMENT ON COLUMN projects.valuation_date IS '평가 기준일';
COMMENT ON COLUMN projects.purpose IS '평가 목적';
COMMENT ON COLUMN projects.valuation_results IS '평가 결과 (JSON 형식)';
COMMENT ON COLUMN projects.dcf_status IS 'DCF 평가 진행 상태';
COMMENT ON COLUMN projects.relative_status IS '상대가치 평가 진행 상태';
COMMENT ON COLUMN projects.intrinsic_status IS '본질가치 평가 진행 상태';
COMMENT ON COLUMN projects.asset_status IS '자산가치 평가 진행 상태';
COMMENT ON COLUMN projects.tax_status IS '상증세법 평가 진행 상태';
