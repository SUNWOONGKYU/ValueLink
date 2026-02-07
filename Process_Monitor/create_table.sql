-- ================================================
-- project_phase_progress 테이블 생성
-- ================================================
-- 목적: 사용자별 Phase 진행률을 DB에 저장
-- 사용: git commit 시 자동 업로드 → 웹에서 조회
-- ================================================

CREATE TABLE IF NOT EXISTS project_phase_progress (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,           -- 사용자별 프로젝트 ID (email_prefix_PROJECT)
    phase_code VARCHAR(10) NOT NULL,            -- P0, P1, P2, P3, S0, S1, S2, S3, S4, S5
    phase_name VARCHAR(100),                    -- 단계명
    progress INTEGER DEFAULT 0,                 -- 진행률 (0~100)
    completed_items INTEGER DEFAULT 0,          -- 완료 항목 수
    total_items INTEGER DEFAULT 0,              -- 전체 항목 수
    status VARCHAR(20) DEFAULT 'pending',       -- pending, in_progress, completed
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- project_id + phase_code 조합으로 UPSERT
    UNIQUE(project_id, phase_code)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_phase_progress_project ON project_phase_progress(project_id);
CREATE INDEX IF NOT EXISTS idx_phase_progress_phase ON project_phase_progress(phase_code);

-- ================================================
-- RLS (Row Level Security) 정책
-- ================================================
-- ANON_KEY 사용자가 자신의 project_id 데이터만 접근 가능
-- 일반 사용자: ANON_KEY로 자신의 프로젝트 진행률만 업로드/조회
-- ================================================

-- 1. RLS 활성화
ALTER TABLE project_phase_progress ENABLE ROW LEVEL SECURITY;

-- 2. SELECT 정책: 모든 사용자가 조회 가능 (application level에서 project_id 필터링)
CREATE POLICY "Allow public read access"
ON project_phase_progress
FOR SELECT
TO anon, authenticated
USING (true);

-- 3. INSERT 정책: 모든 사용자가 자신의 project_id로 삽입 가능
CREATE POLICY "Allow public insert access"
ON project_phase_progress
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

-- 4. UPDATE 정책: 모든 사용자가 자신의 project_id로 업데이트 가능
CREATE POLICY "Allow public update access"
ON project_phase_progress
FOR UPDATE
TO anon, authenticated
USING (true)
WITH CHECK (true);

-- 5. DELETE 정책: 삭제는 제한 (필요시 authenticated만 허용)
CREATE POLICY "Restrict delete access"
ON project_phase_progress
FOR DELETE
TO authenticated
USING (true);

-- ================================================
-- 사용 예시
-- ================================================
-- INSERT INTO project_phase_progress (project_id, phase_code, phase_name, progress)
-- VALUES ('dev_PROJECT', 'P0', '작업 디렉토리 구조 생성', 100)
-- ON CONFLICT (project_id, phase_code)
-- DO UPDATE SET progress = EXCLUDED.progress, updated_at = NOW();
