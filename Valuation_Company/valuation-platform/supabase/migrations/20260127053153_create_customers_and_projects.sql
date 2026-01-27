-- Customers (고객사/회원) 테이블 생성
-- 마이페이지(mypage.html)의 모든 필드 포함

CREATE TABLE IF NOT EXISTS customers (
    -- 기본 정보
    customer_id VARCHAR(20) PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,

    -- 회사 정보 (마이페이지 필드)
    company_name VARCHAR(100) NOT NULL,
    ceo_name VARCHAR(50) NOT NULL,
    industry VARCHAR(100),
    founded_date DATE,
    business_number VARCHAR(20) NOT NULL,
    employees INTEGER,
    company_website VARCHAR(200),

    -- 연락처 정보
    address TEXT,
    phone VARCHAR(20),
    fax VARCHAR(20),

    -- 시스템 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_company_name ON customers(company_name);
CREATE INDEX IF NOT EXISTS idx_customers_business_number ON customers(business_number);

-- RLS 활성화
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책
CREATE POLICY "Allow public read access" ON customers
    FOR SELECT USING (true);

-- 삽입/업데이트/삭제는 인증된 사용자만
CREATE POLICY "Allow authenticated insert" ON customers
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated update" ON customers
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated delete" ON customers
    FOR DELETE USING (auth.role() = 'authenticated');
-- 모의 고객사 데이터 삽입
-- FinderWorld 고객사 (마이페이지 모든 필드 포함)

INSERT INTO customers (
    customer_id,
    email,
    company_name,
    ceo_name,
    industry,
    founded_date,
    business_number,
    employees,
    company_website,
    address,
    phone,
    fax
)
VALUES (
    'C202601',
    'admin@finderworld.com',
    'FinderWorld',
    '김대표',
    '소프트웨어 개발',
    '2020-01-15',
    '123-45-67890',
    50,
    'https://www.finderworld.com',
    '서울특별시 강남구 테헤란로 123',
    '02-1234-5678',
    '02-1234-5679'
);
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
-- 모의 프로젝트 데이터 삽입
-- 고객: FinderWorld (customer_id: C202601)
-- 각 평가방법별로 프로젝트 1개씩 (총 5개)
-- 프로젝트 ID 형식: {5자리 회사코드}-{YYMMDDHHmm}-{2자리 평가법코드}

-- 1. DCF 평가법 (DC)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270530-DC', 'C202601', 'TechStartup Co.', 'dcf', 'in_progress', 4);

-- 2. 상대가치평가법 (RV)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270531-RV', 'C202601', 'InnoVenture Ltd.', 'relative', 'in_progress', 4);

-- 3. 본질가치평가법 (IV)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270532-IV', 'C202601', 'GrowthHub Inc.', 'intrinsic', 'in_progress', 4);

-- 4. 자산가치평가법 (AV)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270533-AV', 'C202601', 'AssetTech Corp.', 'asset', 'in_progress', 4);

-- 5. 상증세법 (TX)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270534-TX', 'C202601', 'FamilyBiz Ltd.', 'inheritance_tax', 'in_progress', 4);
