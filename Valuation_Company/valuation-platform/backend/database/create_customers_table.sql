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
