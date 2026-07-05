-- ================================================================
-- 투자 뉴스 스크래핑 시스템 - Supabase 테이블 생성 SQL
-- 작성일: 2026-01-25
-- 용도: 국내 투자유치 뉴스 수집 및 랭킹
-- ================================================================

-- ================================================================
-- 테이블 1: investment_news_articles (뉴스 기사 저장)
-- ================================================================

CREATE TABLE IF NOT EXISTS investment_news_articles (
    id SERIAL PRIMARY KEY,
    site_number INTEGER NOT NULL CHECK (site_number >= 8 AND site_number <= 26),
    site_name TEXT NOT NULL,
    site_url TEXT NOT NULL,
    article_title TEXT NOT NULL,
    article_url TEXT NOT NULL UNIQUE,
    published_date DATE NOT NULL,
    content_snippet TEXT,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 인덱스 (성능 최적화)
    CONSTRAINT unique_article_url UNIQUE (article_url)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_articles_site_number ON investment_news_articles(site_number);
CREATE INDEX IF NOT EXISTS idx_articles_published_date ON investment_news_articles(published_date);
CREATE INDEX IF NOT EXISTS idx_articles_collected_at ON investment_news_articles(collected_at);

-- 코멘트 추가
COMMENT ON TABLE investment_news_articles IS '투자유치 뉴스 기사 원본 데이터';
COMMENT ON COLUMN investment_news_articles.site_number IS '사이트 번호 (8-26)';
COMMENT ON COLUMN investment_news_articles.site_name IS '사이트명 (예: 벤처스퀘어)';
COMMENT ON COLUMN investment_news_articles.site_url IS '사이트 URL';
COMMENT ON COLUMN investment_news_articles.article_title IS '기사 제목';
COMMENT ON COLUMN investment_news_articles.article_url IS '기사 URL (UNIQUE)';
COMMENT ON COLUMN investment_news_articles.published_date IS '기사 발행일';
COMMENT ON COLUMN investment_news_articles.content_snippet IS '기사 내용 발췌 (선택 사항)';
COMMENT ON COLUMN investment_news_articles.collected_at IS '수집 시간';


-- ================================================================
-- 테이블 2: investment_news_ranking (사이트별 집계 및 랭킹)
-- ================================================================

CREATE TABLE IF NOT EXISTS investment_news_ranking (
    id SERIAL PRIMARY KEY,
    site_number INTEGER NOT NULL UNIQUE CHECK (site_number >= 8 AND site_number <= 26),
    site_name TEXT NOT NULL,
    site_url TEXT NOT NULL,
    news_count INTEGER DEFAULT 0,
    rank INTEGER,
    period_start DATE DEFAULT '2026-01-01',
    period_end DATE DEFAULT CURRENT_DATE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_site_number UNIQUE (site_number)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_ranking_rank ON investment_news_ranking(rank);
CREATE INDEX IF NOT EXISTS idx_ranking_news_count ON investment_news_ranking(news_count DESC);

-- 코멘트 추가
COMMENT ON TABLE investment_news_ranking IS '사이트별 뉴스 건수 집계 및 랭킹';
COMMENT ON COLUMN investment_news_ranking.site_number IS '사이트 번호 (8-26, UNIQUE)';
COMMENT ON COLUMN investment_news_ranking.site_name IS '사이트명';
COMMENT ON COLUMN investment_news_ranking.site_url IS '사이트 URL';
COMMENT ON COLUMN investment_news_ranking.news_count IS '뉴스 건수';
COMMENT ON COLUMN investment_news_ranking.rank IS '랭킹 (1-19)';
COMMENT ON COLUMN investment_news_ranking.period_start IS '집계 시작일';
COMMENT ON COLUMN investment_news_ranking.period_end IS '집계 종료일';
COMMENT ON COLUMN investment_news_ranking.last_updated IS '마지막 업데이트 시간';


-- ================================================================
-- 초기 데이터: 19개 사이트 등록
-- ================================================================

INSERT INTO investment_news_ranking (site_number, site_name, site_url) VALUES
    (8, '더브이씨', 'thevc.kr'),
    (9, '벤처스퀘어', 'www.venturesquare.net'),
    (10, '플래텀', 'platum.kr'),
    (11, '스타트업투데이', 'startuptoday.kr'),
    (12, '스타트업엔', 'startupn.kr'),
    (13, '아웃스탠딩', 'outstanding.kr'),
    (14, '모비인사이드', 'mobiinside.co.kr'),
    (15, '지디넷코리아', 'www.zdnet.co.kr'),
    (16, '더벨', 'www.thebell.co.kr'),
    (17, '넥스트유니콘', 'nextunicorn.kr'),
    (18, '테크월드뉴스', 'www.epnc.co.kr'),
    (19, 'AI타임스', 'www.aitimes.com'),
    (20, '벤처경영신문', 'www.vmnews.co.kr'),
    (21, '뉴스톱', 'www.newstopkorea.com'),
    (22, '블로터', 'www.bloter.net'),
    (23, '이코노미스트', 'www.economist.co.kr'),
    (24, '매일경제 MK테크리뷰', 'www.mk.co.kr/news/it'),
    (25, '다음뉴스 벤처/스타트업', 'news.daum.net/section/2/venture'),
    (26, '대한민국 정책브리핑', 'www.korea.kr')
ON CONFLICT (site_number) DO NOTHING;


-- ================================================================
-- 유틸리티 뷰: 최신 랭킹 조회
-- ================================================================

CREATE OR REPLACE VIEW v_latest_ranking AS
SELECT
    rank,
    site_number,
    site_name,
    site_url,
    news_count,
    period_start,
    period_end,
    last_updated
FROM investment_news_ranking
ORDER BY rank ASC NULLS LAST, news_count DESC;

COMMENT ON VIEW v_latest_ranking IS '최신 뉴스 사이트 랭킹 뷰';


-- ================================================================
-- 함수: 랭킹 자동 업데이트
-- ================================================================

CREATE OR REPLACE FUNCTION update_news_ranking()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- 사이트별 뉴스 건수 집계 및 랭킹 계산
    WITH ranked_sites AS (
        SELECT
            site_number,
            site_name,
            site_url,
            COUNT(*) as news_count,
            RANK() OVER (ORDER BY COUNT(*) DESC) as rank
        FROM investment_news_articles
        WHERE published_date BETWEEN '2026-01-01' AND CURRENT_DATE
        GROUP BY site_number, site_name, site_url
    )
    -- 랭킹 테이블 업데이트
    UPDATE investment_news_ranking r
    SET
        news_count = rs.news_count,
        rank = rs.rank,
        period_end = CURRENT_DATE,
        last_updated = NOW()
    FROM ranked_sites rs
    WHERE r.site_number = rs.site_number;

    -- 뉴스가 없는 사이트는 0건, 랭킹 NULL 유지
    UPDATE investment_news_ranking
    SET
        news_count = 0,
        rank = NULL,
        last_updated = NOW()
    WHERE site_number NOT IN (
        SELECT DISTINCT site_number
        FROM investment_news_articles
        WHERE published_date BETWEEN '2026-01-01' AND CURRENT_DATE
    );
END;
$$;

COMMENT ON FUNCTION update_news_ranking() IS '사이트별 뉴스 건수 집계 및 랭킹 자동 업데이트';


-- ================================================================
-- 사용 예시
-- ================================================================

-- 1. 랭킹 업데이트 실행
-- SELECT update_news_ranking();

-- 2. 최신 랭킹 조회
-- SELECT * FROM v_latest_ranking;

-- 3. 특정 사이트 뉴스 목록
-- SELECT article_title, article_url, published_date
-- FROM investment_news_articles
-- WHERE site_number = 9
-- ORDER BY published_date DESC;

-- 4. 날짜별 뉴스 건수
-- SELECT published_date, COUNT(*) as daily_count
-- FROM investment_news_articles
-- GROUP BY published_date
-- ORDER BY published_date DESC;


-- ================================================================
-- Row Level Security (RLS) 설정 (선택 사항)
-- ================================================================

-- RLS 활성화
-- ALTER TABLE investment_news_articles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE investment_news_ranking ENABLE ROW LEVEL SECURITY;

-- 읽기 정책 (모든 사용자)
-- CREATE POLICY "Allow read access to all users" ON investment_news_articles
--     FOR SELECT USING (true);

-- CREATE POLICY "Allow read access to all users" ON investment_news_ranking
--     FOR SELECT USING (true);

-- 쓰기 정책 (인증된 사용자만)
-- CREATE POLICY "Allow insert for authenticated users" ON investment_news_articles
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- CREATE POLICY "Allow update for authenticated users" ON investment_news_ranking
--     FOR UPDATE USING (auth.role() = 'authenticated');


-- ================================================================
-- 완료 메시지
-- ================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ 테이블 생성 완료: investment_news_articles, investment_news_ranking';
    RAISE NOTICE '✅ 초기 데이터 삽입 완료: 19개 사이트 등록';
    RAISE NOTICE '✅ 뷰 생성 완료: v_latest_ranking';
    RAISE NOTICE '✅ 함수 생성 완료: update_news_ranking()';
    RAISE NOTICE '';
    RAISE NOTICE '다음 단계:';
    RAISE NOTICE '1. Python 스크립트로 뉴스 데이터 수집';
    RAISE NOTICE '2. SELECT update_news_ranking(); 실행하여 랭킹 업데이트';
    RAISE NOTICE '3. SELECT * FROM v_latest_ranking; 실행하여 결과 확인';
END $$;
