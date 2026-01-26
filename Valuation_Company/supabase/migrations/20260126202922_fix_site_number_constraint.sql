-- 기존 constraint 제거
ALTER TABLE investment_news_articles
DROP CONSTRAINT IF EXISTS investment_news_articles_site_number_check;

-- 새 constraint 추가 (1-100 범위)
ALTER TABLE investment_news_articles
ADD CONSTRAINT investment_news_articles_site_number_check
CHECK (site_number >= 1 AND site_number <= 100);
