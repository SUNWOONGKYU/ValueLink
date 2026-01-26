-- 11점 점수 시스템 필드 추가
ALTER TABLE investment_news_articles
ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS has_amount BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS has_investors BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS has_stage BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS has_industry BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS has_location BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS has_employees BOOLEAN DEFAULT false;

-- 인덱스 추가 (점수 기반 정렬용)
CREATE INDEX IF NOT EXISTS idx_score ON investment_news_articles(score DESC);
CREATE INDEX IF NOT EXISTS idx_site_number_score ON investment_news_articles(site_number, score DESC);
