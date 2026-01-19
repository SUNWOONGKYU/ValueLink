-- ================================================================
-- PROJECT SAL GRID - Supabase Schema
-- 버전: v4.0 (템플릿/실전 테이블 분리)
-- 생성일: 2025-11-27
-- 기준: PROJECT_GRID_22_ATTRIBUTES_FINAL.md (원본 22개 속성 순서 그대로)
-- ================================================================
--
-- 테이블 구조:
--   1. project_sal_grid_tasks_template  - 템플릿 Task (범용 예시)
--   2. project_tasks                    - 실전 Task (Your Project)
--   3. stage_verification               - Stage Gate 검증
--
-- ================================================================
--
-- 📌 상세 규칙 파일 (.claude/rules/) - 2025-12-19:
--   Grid 데이터 작성 시 반드시 참조하세요!
--
--   - 04_grid-writing.md    : Grid 22개 속성 작성 규칙
--   - 05_execution-process.md : 6단계 실행 프로세스
--   - 06_verification.md    : Task/Stage Gate 검증 기준
--
-- ================================================================

-- ================================================================
-- 1. 템플릿 테이블 (project_sal_grid_tasks_template)
-- ================================================================

DROP TABLE IF EXISTS project_sal_grid_tasks_template CASCADE;

CREATE TABLE project_sal_grid_tasks_template (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- ========================================
    -- [1-4] Basic Info (기본 정보)
    -- ========================================

    -- #1 Stage (단계)
    stage INTEGER NOT NULL CHECK (stage >= 1 AND stage <= 6),
    -- 템플릿: 1=기획, 2=프로토타입, 3=개발준비, 4=개발, 5=운영, 6=확장

    -- #2 Area (영역)
    area VARCHAR(30) NOT NULL,
    -- 표준 11개 영역: M, U, F, BI, BA, D, S, T, O, E, C

    -- #3 Task ID (작업ID)
    task_id VARCHAR(20) UNIQUE NOT NULL,
    -- 형식: S[Stage][Area][Number][병렬기호]

    -- #4 Task Name (업무명)
    task_name TEXT NOT NULL,

    -- ========================================
    -- [5-9] Task Definition (작업 정의)
    -- ========================================

    task_instruction TEXT,
    task_agent VARCHAR(100),
    tools TEXT,
    execution_type VARCHAR(20) NOT NULL DEFAULT 'AI-Only',
    dependencies TEXT,

    -- ========================================
    -- [10-13] Task Execution (작업 실행)
    -- ========================================

    task_progress INTEGER DEFAULT 0 CHECK (task_progress >= 0 AND task_progress <= 100),
    task_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    generated_files TEXT,
    modification_history TEXT,

    -- ========================================
    -- [14-15] Verification Definition (검증 정의)
    -- ========================================

    verification_instruction TEXT,
    verification_agent VARCHAR(100),

    -- ========================================
    -- [16-19] Verification Execution (검증 실행)
    -- ========================================

    test JSONB,
    build JSONB,
    integration_verification JSONB,
    blockers JSONB,

    -- ========================================
    -- [20-22] Verification Completion (검증 완료)
    -- ========================================

    comprehensive_verification TEXT,
    verification_status VARCHAR(20) DEFAULT 'Not Verified',
    remarks TEXT,

    -- 시스템 필드
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 템플릿 테이블 인덱스
CREATE INDEX idx_template_task_id ON project_sal_grid_tasks_template(task_id);
CREATE INDEX idx_template_stage ON project_sal_grid_tasks_template(stage);
CREATE INDEX idx_template_area ON project_sal_grid_tasks_template(area);
CREATE INDEX idx_template_task_status ON project_sal_grid_tasks_template(task_status);

-- 템플릿 테이블 RLS
ALTER TABLE project_sal_grid_tasks_template ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read on template"
    ON project_sal_grid_tasks_template FOR SELECT TO public USING (true);

CREATE POLICY "Allow public write on template"
    ON project_sal_grid_tasks_template FOR ALL TO public USING (true) WITH CHECK (true);


-- ================================================================
-- 2. 실전 테이블 (project_tasks) - Your Project 프로덕션용
-- ================================================================

DROP TABLE IF EXISTS project_tasks CASCADE;

CREATE TABLE project_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- ========================================
    -- [1-4] Basic Info (기본 정보)
    -- ========================================

    -- #1 Stage (단계)
    stage INTEGER NOT NULL CHECK (stage >= 1 AND stage <= 6),
    -- Your Project: 1=프로토타입, 2=개발준비, 3=개발1차, 4=개발2차, 5=개발3차, 6=운영

    -- #2 Area (영역)
    area VARCHAR(30) NOT NULL,
    -- 표준 11개 영역: M, U, F, BI, BA, D, S, T, O, E, C

    -- #3 Task ID (작업ID)
    task_id VARCHAR(20) UNIQUE NOT NULL,
    -- 형식: S[Stage][Area][Number][병렬기호]

    -- #4 Task Name (업무명)
    task_name TEXT NOT NULL,

    -- ========================================
    -- [5-9] Task Definition (작업 정의)
    -- ========================================

    task_instruction TEXT,
    task_agent VARCHAR(100),
    tools TEXT,
    execution_type VARCHAR(20) NOT NULL DEFAULT 'AI-Only',
    dependencies TEXT,

    -- ========================================
    -- [10-13] Task Execution (작업 실행)
    -- ========================================

    task_progress INTEGER DEFAULT 0 CHECK (task_progress >= 0 AND task_progress <= 100),
    task_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    generated_files TEXT,
    modification_history TEXT,

    -- ========================================
    -- [14-15] Verification Definition (검증 정의)
    -- ========================================

    verification_instruction TEXT,
    verification_agent VARCHAR(100),

    -- ========================================
    -- [16-19] Verification Execution (검증 실행)
    -- ========================================

    test JSONB,
    build JSONB,
    integration_verification JSONB,
    blockers JSONB,

    -- ========================================
    -- [20-22] Verification Completion (검증 완료)
    -- ========================================

    comprehensive_verification TEXT,
    verification_status VARCHAR(20) DEFAULT 'Not Verified',
    remarks TEXT,

    -- 시스템 필드
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 실전 테이블 인덱스
CREATE INDEX idx_project_task_id ON project_tasks(task_id);
CREATE INDEX idx_project_stage ON project_tasks(stage);
CREATE INDEX idx_project_area ON project_tasks(area);
CREATE INDEX idx_project_task_status ON project_tasks(task_status);
CREATE INDEX idx_project_verification_status ON project_tasks(verification_status);

-- 실전 테이블 RLS
ALTER TABLE project_tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read on project_tasks"
    ON project_tasks FOR SELECT TO public USING (true);

CREATE POLICY "Allow public write on project_tasks"
    ON project_tasks FOR ALL TO public USING (true) WITH CHECK (true);


-- ================================================================
-- 3. Stage Gate 테이블 (Stage 검증용)
-- ================================================================

DROP TABLE IF EXISTS stage_verification CASCADE;

CREATE TABLE stage_verification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stage_name VARCHAR(50) NOT NULL,
    project_id VARCHAR(50),  -- 'TEMPLATE' 또는 'YOUR_PROJECT'

    -- 검증 정의
    stage_verification_order TEXT,
    stage_verification_agent VARCHAR(100),

    -- 1차: AI 자동 검증
    auto_verification_status VARCHAR(20) DEFAULT 'Not Verified',
    auto_verification_result TEXT,
    auto_verification_date TIMESTAMPTZ,

    -- 2차: Project Owner 수동 검증
    manual_verification_status VARCHAR(20) DEFAULT 'Not Verified',
    manual_verification_comment TEXT,
    manual_verification_date TIMESTAMPTZ,

    -- Stage Gate 최종 상태
    stage_gate_status VARCHAR(20) DEFAULT 'Not Started',
    -- 값: Not Started | AI Verified | Approved | Rejected

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage Verification RLS
ALTER TABLE stage_verification ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read on stage_verification"
    ON stage_verification FOR SELECT TO public USING (true);

CREATE POLICY "Allow public write on stage_verification"
    ON stage_verification FOR ALL TO public USING (true) WITH CHECK (true);


-- ================================================================
-- 4. 트리거 (자동 업데이트)
-- ================================================================

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 템플릿 테이블 트리거
CREATE TRIGGER update_template_tasks_modtime
    BEFORE UPDATE ON project_sal_grid_tasks_template
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- 실전 테이블 트리거
CREATE TRIGGER update_project_tasks_modtime
    BEFORE UPDATE ON project_tasks
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Stage Verification 트리거
CREATE TRIGGER update_stage_verification_modtime
    BEFORE UPDATE ON stage_verification
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();


-- ================================================================
-- 완료!
-- ================================================================
--
-- 테이블 구조:
--   1. project_sal_grid_tasks_template  - 템플릿 Task (범용 예시)
--   2. project_tasks                    - 실전 Task (Your Project)
--   3. stage_verification               - Stage Gate 검증
--
-- 실행 순서:
--   1. 이 파일 실행 (테이블 생성)
--   2. TEMPLATE_complete_setup.sql 또는 TEMPLATE_STANDARD_PROJECT_SAL_GRID.sql (템플릿 데이터)
--   3. PROJECT_TASKS_DATA.sql (실전 데이터)
--
-- ================================================================
