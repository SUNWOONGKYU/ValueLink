-- Deal 테이블 생성
CREATE TABLE IF NOT EXISTS deals (
    id BIGSERIAL PRIMARY KEY,

    -- 기업 정보
    company_name TEXT NOT NULL,
    industry TEXT,
    location TEXT,
    employees INTEGER,

    -- 투자 정보
    stage TEXT,
    investors TEXT,
    amount NUMERIC,  -- 투자금액 (억원)

    -- 뉴스 출처
    news_title TEXT,
    news_url TEXT,
    news_date DATE,
    site_name TEXT,

    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_deals_company_name ON deals(company_name);
CREATE INDEX IF NOT EXISTS idx_deals_news_date ON deals(news_date DESC);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals(created_at DESC);

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_deals_updated_at
    BEFORE UPDATE ON deals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) 설정
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
CREATE POLICY "Enable read access for all users" ON deals
    FOR SELECT
    USING (true);

-- 인증된 사용자만 삽입/수정/삭제 가능
CREATE POLICY "Enable insert for authenticated users only" ON deals
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable update for authenticated users only" ON deals
    FOR UPDATE
    USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Enable delete for authenticated users only" ON deals
    FOR DELETE
    USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');
