-- Projects 테이블 삭제 후 재생성
DROP TABLE IF EXISTS projects CASCADE;

-- Projects 테이블 생성
CREATE TABLE projects (
    project_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    valuation_method VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    current_step INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_projects_customer ON projects(customer_id);
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
