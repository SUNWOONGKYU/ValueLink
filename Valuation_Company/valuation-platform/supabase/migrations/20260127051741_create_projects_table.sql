-- Projects 테이블 삭제 후 재생성
DROP TABLE IF EXISTS projects CASCADE;

-- Projects 테이블 생성
CREATE TABLE projects (
    project_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    valuation_method VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    current_step INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_projects_customer ON projects(customer_name);
CREATE INDEX IF NOT EXISTS idx_projects_method ON projects(valuation_method);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- RLS 활성화
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책
CREATE POLICY "Allow public read access" ON projects
    FOR SELECT USING (true);

-- 삽입/업데이트/삭제는 인증된 사용자만
CREATE POLICY "Allow authenticated insert" ON projects
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated update" ON projects
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated delete" ON projects
    FOR DELETE USING (auth.role() = 'authenticated');
-- 모의 프로젝트 데이터 삽입
-- 고객: FinderWorld
-- 평가방법별로 1개씩 총 5개 프로젝트

-- 1. DCF 평가법
INSERT INTO projects (project_id, customer_name, company_name, valuation_method, status, current_step)
VALUES ('PROJ-DCF-001', 'FinderWorld', 'FinderWorld Inc.', 'dcf', 'in_progress', 6);

-- 2. 상대가치평가법
INSERT INTO projects (project_id, customer_name, company_name, valuation_method, status, current_step)
VALUES ('PROJ-REL-001', 'FinderWorld', 'FinderWorld Inc.', 'relative', 'in_progress', 6);

-- 3. 본질가치평가법
INSERT INTO projects (project_id, customer_name, company_name, valuation_method, status, current_step)
VALUES ('PROJ-INT-001', 'FinderWorld', 'FinderWorld Inc.', 'intrinsic', 'in_progress', 6);

-- 4. 자산가치평가법
INSERT INTO projects (project_id, customer_name, company_name, valuation_method, status, current_step)
VALUES ('PROJ-AST-001', 'FinderWorld', 'FinderWorld Inc.', 'asset', 'in_progress', 6);

-- 5. 상증세법
INSERT INTO projects (project_id, customer_name, company_name, valuation_method, status, current_step)
VALUES ('PROJ-TAX-001', 'FinderWorld', 'FinderWorld Inc.', 'inheritance_tax', 'in_progress', 6);
