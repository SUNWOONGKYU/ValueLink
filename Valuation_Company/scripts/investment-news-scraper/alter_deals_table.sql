-- Deal 테이블에 필드 추가
ALTER TABLE deals ADD COLUMN IF NOT EXISTS ceo TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS founded DATE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS total_funding NUMERIC;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_deals_founded ON deals(founded);
CREATE INDEX IF NOT EXISTS idx_deals_industry ON deals(industry);
