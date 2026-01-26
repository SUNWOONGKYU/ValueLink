-- ================================================================
-- Phase 0-1: projects 테이블에 평가법별 상태 필드 추가
-- ================================================================
-- 작성일: 2026-01-26
-- 목적: 여러 평가법 동시 신청 및 독립적 진행 관리
--
-- 상태 값:
--   - not_requested: 신청 안 함 (기본값)
--   - pending: 승인 대기 중
--   - approved: 승인됨
--   - in_progress: 진행 중
--   - completed: 완료
-- ================================================================

-- 1. DCF (현금흐름할인법) 상태 필드
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS dcf_status TEXT DEFAULT 'not_requested',
ADD COLUMN IF NOT EXISTS dcf_step INTEGER DEFAULT 1;

-- 2. Relative (상대가치평가법) 상태 필드
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS relative_status TEXT DEFAULT 'not_requested',
ADD COLUMN IF NOT EXISTS relative_step INTEGER DEFAULT 1;

-- 3. Intrinsic (본질가치평가법) 상태 필드
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS intrinsic_status TEXT DEFAULT 'not_requested',
ADD COLUMN IF NOT EXISTS intrinsic_step INTEGER DEFAULT 1;

-- 4. Asset (자산가치평가법) 상태 필드
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS asset_status TEXT DEFAULT 'not_requested',
ADD COLUMN IF NOT EXISTS asset_step INTEGER DEFAULT 1;

-- 5. Inheritance Tax (상속세및증여세법) 상태 필드
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS inheritance_tax_status TEXT DEFAULT 'not_requested',
ADD COLUMN IF NOT EXISTS inheritance_tax_step INTEGER DEFAULT 1;

-- 6. 상태 제약조건 추가 (유효한 값만 허용)
ALTER TABLE projects
ADD CONSTRAINT dcf_status_check
    CHECK (dcf_status IN ('not_requested', 'pending', 'approved', 'in_progress', 'completed')),
ADD CONSTRAINT relative_status_check
    CHECK (relative_status IN ('not_requested', 'pending', 'approved', 'in_progress', 'completed')),
ADD CONSTRAINT intrinsic_status_check
    CHECK (intrinsic_status IN ('not_requested', 'pending', 'approved', 'in_progress', 'completed')),
ADD CONSTRAINT asset_status_check
    CHECK (asset_status IN ('not_requested', 'pending', 'approved', 'in_progress', 'completed')),
ADD CONSTRAINT inheritance_tax_status_check
    CHECK (inheritance_tax_status IN ('not_requested', 'pending', 'approved', 'in_progress', 'completed'));

-- 7. 단계 제약조건 추가 (1~14만 허용)
ALTER TABLE projects
ADD CONSTRAINT dcf_step_check CHECK (dcf_step BETWEEN 1 AND 14),
ADD CONSTRAINT relative_step_check CHECK (relative_step BETWEEN 1 AND 14),
ADD CONSTRAINT intrinsic_step_check CHECK (intrinsic_step BETWEEN 1 AND 14),
ADD CONSTRAINT asset_step_check CHECK (asset_step BETWEEN 1 AND 14),
ADD CONSTRAINT inheritance_tax_step_check CHECK (inheritance_tax_step BETWEEN 1 AND 14);

-- 8. 인덱스 생성 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_projects_dcf_status ON projects(dcf_status);
CREATE INDEX IF NOT EXISTS idx_projects_relative_status ON projects(relative_status);
CREATE INDEX IF NOT EXISTS idx_projects_intrinsic_status ON projects(intrinsic_status);
CREATE INDEX IF NOT EXISTS idx_projects_asset_status ON projects(asset_status);
CREATE INDEX IF NOT EXISTS idx_projects_inheritance_tax_status ON projects(inheritance_tax_status);

-- ================================================================
-- 실행 후 확인 쿼리
-- ================================================================
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'projects'
-- ORDER BY ordinal_position;
