-- ========================================
-- Investment News Network Database Schema
-- ========================================

-- 1. 뉴스 소스 테이블 (11개 소스 관리)
CREATE TABLE investment_news_network_sources (
    id SERIAL PRIMARY KEY,
    rank INTEGER NOT NULL,                    -- 순위 (1-11)
    category TEXT NOT NULL,                   -- 'RSS', 'Web Scraping', 'VC Database'
    source_number INTEGER UNIQUE NOT NULL,    -- 고유 번호
    source_name TEXT NOT NULL,                -- 소스명 (예: 벤처스퀘어)
    source_url TEXT NOT NULL,                 -- URL
    collection_method TEXT NOT NULL,          -- 'RSS' 또는 'Web Scraping'
    rss_url TEXT,                             -- RSS 피드 URL (있는 경우)
    selector TEXT,                            -- CSS 선택자 (웹 스크래핑 시)
    is_active BOOLEAN DEFAULT true,           -- 활성화 여부
    expected_daily_count INTEGER,             -- 예상 일일 수집량
    last_collected_at TIMESTAMPTZ,            -- 마지막 수집 시간
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 초기 데이터 삽입
INSERT INTO investment_news_network_sources (rank, category, source_number, source_name, source_url, collection_method, rss_url, expected_daily_count) VALUES
-- Category 1: RSS Sources
(1, 'RSS', 9, '벤처스퀘어', 'https://www.venturesquare.net', 'RSS', 'https://www.venturesquare.net/feed', 15),
(2, 'RSS', 13, '아웃스탠딩', 'https://outstanding.kr', 'RSS', 'https://outstanding.kr/feed', 8),
(3, 'RSS', 10, '플래텀', 'https://platum.kr', 'RSS', 'https://platum.kr/feed', 8),
(4, 'RSS', 14, '비석세스', 'https://besuccess.com', 'RSS', 'https://besuccess.com/feed', 8),

-- Category 2: Web Scraping Sources
(5, 'Web Scraping', 11, '스타트업투데이', 'https://startuptoday.kr', 'Web Scraping', NULL, 5),
(6, 'Web Scraping', 12, '스타트업엔', 'https://startupn.kr', 'Web Scraping', NULL, 4),
(7, 'Web Scraping', 22, '블로터', 'https://www.bloter.net', 'Web Scraping', NULL, 5),
(8, 'Web Scraping', 23, '이코노미스트', 'https://www.economist.co.kr', 'Web Scraping', NULL, 3),
(9, 'Web Scraping', 19, 'AI타임스', 'https://www.aitimes.com', 'Web Scraping', NULL, 4),
(10, 'Web Scraping', 21, '넥스트유니콘', 'https://www.nextunicorn.kr', 'Web Scraping', NULL, 5),

-- Category 3: VC Database
(11, 'VC Database', 8, '더브이씨', 'https://thevc.kr', 'Reference', NULL, 0);


-- 2. 수집된 모든 기사 (중복 제거 안 함)
CREATE TABLE investment_news_articles (
    id SERIAL PRIMARY KEY,
    source_number INTEGER NOT NULL,           -- 소스 번호 (sources 테이블 참조)
    source_name TEXT NOT NULL,                -- 소스명
    source_url TEXT NOT NULL,                 -- 소스 URL
    article_title TEXT NOT NULL,              -- 기사 제목
    article_url TEXT UNIQUE NOT NULL,         -- 기사 URL (중복 체크용)
    published_date TIMESTAMPTZ,               -- 발행일
    content_snippet TEXT,                     -- 기사 요약/스니펫

    -- 기사 점수 (11점 만점)
    score INTEGER DEFAULT 0,                  -- 총 점수
    has_amount BOOLEAN DEFAULT false,         -- 투자금액 유무 (3점)
    has_investors BOOLEAN DEFAULT false,      -- 투자자 유무 (3점)
    has_stage BOOLEAN DEFAULT false,          -- 투자단계 유무 (2점)
    has_industry BOOLEAN DEFAULT false,       -- 업종 유무 (1점)
    has_location BOOLEAN DEFAULT false,       -- 지역 유무 (1점)
    has_employees BOOLEAN DEFAULT false,      -- 직원수 유무 (1점)

    -- 상태
    is_korean_company BOOLEAN,                -- 한국 기업 여부
    is_selected BOOLEAN DEFAULT false,        -- Deal 테이블 선정 여부
    selected_at TIMESTAMPTZ,                  -- 선정 시간

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    FOREIGN KEY (source_number) REFERENCES investment_news_network_sources(source_number)
);

-- 인덱스
CREATE INDEX idx_articles_source ON investment_news_articles(source_number);
CREATE INDEX idx_articles_published ON investment_news_articles(published_date DESC);
CREATE INDEX idx_articles_selected ON investment_news_articles(is_selected);
CREATE INDEX idx_articles_korean ON investment_news_articles(is_korean_company);


-- 3. 선정된 투자 딜 (기업별 최고 점수 기사만)
CREATE TABLE deals (
    id SERIAL PRIMARY KEY,

    -- 기사 정보
    article_id INTEGER UNIQUE,                -- investment_news_articles.id 참조
    news_title TEXT NOT NULL,                 -- 기사 제목
    news_url TEXT NOT NULL,                   -- 기사 URL
    news_date TIMESTAMPTZ,                    -- 기사 발행일
    site_name TEXT NOT NULL,                  -- 출처
    article_score INTEGER,                    -- 기사 점수 (11점 만점)

    -- 회사 정보 (Gemini 추출 + TheVC 보강)
    company_name TEXT NOT NULL,               -- 기업명
    ceo TEXT,                                 -- 대표자
    founded DATE,                             -- 설립일
    industry TEXT,                            -- 업종
    location TEXT,                            -- 위치
    employees INTEGER,                        -- 직원수
    description TEXT,                         -- 회사 설명

    -- 투자 정보 (Gemini 추출)
    investors TEXT,                           -- 투자자 (콤마 구분, TheVC로 검증)
    amount TEXT,                              -- 투자금액
    stage TEXT,                               -- 투자단계 (시드, 시리즈A 등)

    -- 데이터 출처
    gemini_extracted BOOLEAN DEFAULT true,    -- Gemini로 추출 여부
    thevc_enriched BOOLEAN DEFAULT false,     -- TheVC로 보강 여부
    naver_enriched BOOLEAN DEFAULT false,     -- Naver API로 보강 여부

    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    FOREIGN KEY (article_id) REFERENCES investment_news_articles(id)
);

-- 인덱스
CREATE INDEX idx_deals_company ON deals(company_name);
CREATE INDEX idx_deals_date ON deals(news_date DESC);
CREATE INDEX idx_deals_stage ON deals(stage);
CREATE INDEX idx_deals_created ON deals(created_at DESC);


-- 4. 이메일 구독자
CREATE TABLE email_subscribers (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,               -- 이메일 주소
    name TEXT,                                -- 이름 (선택)

    -- 구독 설정
    daily_news BOOLEAN DEFAULT true,          -- 일일 뉴스 구독 (월-토)
    weekly_insight BOOLEAN DEFAULT true,      -- 주간 인사이트 구독 (일요일)

    -- 상태
    is_active BOOLEAN DEFAULT true,           -- 구독 활성화 여부
    email_verified BOOLEAN DEFAULT false,     -- 이메일 인증 여부
    verification_token TEXT,                  -- 인증 토큰

    -- 메타데이터
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    last_sent_at TIMESTAMPTZ,                 -- 마지막 발송 시간
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_subscribers_active ON email_subscribers(is_active);
CREATE INDEX idx_subscribers_daily ON email_subscribers(daily_news) WHERE daily_news = true;
CREATE INDEX idx_subscribers_weekly ON email_subscribers(weekly_insight) WHERE weekly_insight = true;


-- 5. 이메일 발송 로그
CREATE TABLE email_send_log (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER NOT NULL,           -- 구독자 ID
    email_type TEXT NOT NULL,                 -- 'daily' 또는 'weekly'
    subject TEXT NOT NULL,                    -- 이메일 제목

    -- 발송 정보
    sent_at TIMESTAMPTZ DEFAULT NOW(),        -- 발송 시간
    status TEXT NOT NULL,                     -- 'sent', 'failed', 'bounced'
    error_message TEXT,                       -- 에러 메시지 (실패 시)

    -- 내용 정보
    deals_count INTEGER,                      -- 포함된 Deal 개수
    deals_ids INTEGER[],                      -- Deal ID 배열

    -- 메타데이터
    created_at TIMESTAMPTZ DEFAULT NOW(),

    FOREIGN KEY (subscriber_id) REFERENCES email_subscribers(id)
);

-- 인덱스
CREATE INDEX idx_sendlog_subscriber ON email_send_log(subscriber_id);
CREATE INDEX idx_sendlog_sent ON email_send_log(sent_at DESC);
CREATE INDEX idx_sendlog_status ON email_send_log(status);


-- ========================================
-- View: 최근 투자 뉴스 (Deal 페이지용)
-- ========================================
CREATE VIEW recent_investment_news AS
SELECT
    d.id,
    d.company_name,
    d.ceo,
    d.industry,
    d.investors,
    d.amount,
    d.stage,
    d.location,
    d.news_title,
    d.news_url,
    d.news_date,
    d.site_name,
    d.article_score,
    d.created_at
FROM deals d
ORDER BY d.news_date DESC, d.created_at DESC
LIMIT 100;


-- ========================================
-- View: 일일 수집 통계
-- ========================================
CREATE VIEW daily_collection_stats AS
SELECT
    DATE(created_at) as collection_date,
    source_name,
    COUNT(*) as total_articles,
    SUM(CASE WHEN is_korean_company = true THEN 1 ELSE 0 END) as korean_articles,
    SUM(CASE WHEN is_selected = true THEN 1 ELSE 0 END) as selected_articles,
    AVG(score) as avg_score
FROM investment_news_articles
GROUP BY DATE(created_at), source_name
ORDER BY collection_date DESC, source_name;


-- ========================================
-- View: 주간 인사이트 데이터
-- ========================================
CREATE VIEW weekly_insight AS
SELECT
    DATE_TRUNC('week', news_date) as week_start,
    COUNT(*) as total_deals,
    COUNT(DISTINCT company_name) as unique_companies,
    COUNT(DISTINCT stage) as stages_count,
    array_agg(DISTINCT stage) as stages,
    COUNT(DISTINCT industry) as industries_count,
    array_agg(DISTINCT industry) as industries,
    SUM(CASE WHEN amount IS NOT NULL THEN 1 ELSE 0 END) as deals_with_amount,
    COUNT(DISTINCT investors) as unique_investors
FROM deals
GROUP BY DATE_TRUNC('week', news_date)
ORDER BY week_start DESC;


-- ========================================
-- 유용한 쿼리
-- ========================================

-- 1. 오늘 수집된 기사 수
-- SELECT source_name, COUNT(*)
-- FROM investment_news_articles
-- WHERE DATE(created_at) = CURRENT_DATE
-- GROUP BY source_name;

-- 2. 기업별 최신 투자 뉴스
-- SELECT company_name, news_date, amount, stage, investors
-- FROM deals
-- ORDER BY news_date DESC
-- LIMIT 10;

-- 3. 투자 단계별 통계
-- SELECT stage, COUNT(*) as count, AVG(article_score) as avg_score
-- FROM deals
-- GROUP BY stage
-- ORDER BY count DESC;

-- 4. 소스별 선정률
-- SELECT
--     a.source_name,
--     COUNT(*) as total_articles,
--     SUM(CASE WHEN a.is_selected THEN 1 ELSE 0 END) as selected,
--     ROUND(100.0 * SUM(CASE WHEN a.is_selected THEN 1 ELSE 0 END) / COUNT(*), 2) as selection_rate
-- FROM investment_news_articles a
-- GROUP BY a.source_name
-- ORDER BY selection_rate DESC;

-- 5. 활성 구독자 수
-- SELECT
--     SUM(CASE WHEN daily_news THEN 1 ELSE 0 END) as daily_subscribers,
--     SUM(CASE WHEN weekly_insight THEN 1 ELSE 0 END) as weekly_subscribers
-- FROM email_subscribers
-- WHERE is_active = true;
