-- 누락된 테이블만 생성

-- 1. investment_news_network_sources 테이블
CREATE TABLE IF NOT EXISTS investment_news_network_sources (
    id SERIAL PRIMARY KEY,
    rank INTEGER NOT NULL,
    category TEXT NOT NULL,
    source_number INTEGER UNIQUE NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    collection_method TEXT NOT NULL,
    rss_url TEXT,
    selector TEXT,
    is_active BOOLEAN DEFAULT true,
    expected_daily_count INTEGER,
    last_collected_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 초기 데이터 삽입
INSERT INTO investment_news_network_sources (rank, category, source_number, source_name, source_url, collection_method, rss_url, expected_daily_count) VALUES
(1, 'RSS', 9, '벤처스퀘어', 'https://www.venturesquare.net', 'RSS', 'https://www.venturesquare.net/feed', 15),
(2, 'RSS', 13, '아웃스탠딩', 'https://outstanding.kr', 'RSS', 'https://outstanding.kr/feed', 8),
(3, 'RSS', 10, '플래텀', 'https://platum.kr', 'RSS', 'https://platum.kr/feed', 8),
(4, 'RSS', 14, '비석세스', 'https://besuccess.com', 'RSS', 'https://besuccess.com/feed', 8),
(5, 'Web Scraping', 11, '스타트업투데이', 'https://startuptoday.kr', 'Web Scraping', NULL, 5),
(6, 'Web Scraping', 12, '스타트업엔', 'https://startupn.kr', 'Web Scraping', NULL, 4),
(7, 'Web Scraping', 22, '블로터', 'https://www.bloter.net', 'Web Scraping', NULL, 5),
(8, 'Web Scraping', 23, '이코노미스트', 'https://www.economist.co.kr', 'Web Scraping', NULL, 3),
(9, 'Web Scraping', 19, 'AI타임스', 'https://www.aitimes.com', 'Web Scraping', NULL, 4),
(10, 'Web Scraping', 21, '넥스트유니콘', 'https://www.nextunicorn.kr', 'Web Scraping', NULL, 5),
(11, 'VC Database', 8, '더브이씨', 'https://thevc.kr', 'Reference', NULL, 0)
ON CONFLICT (source_number) DO NOTHING;

-- 2. email_subscribers 테이블
CREATE TABLE IF NOT EXISTS email_subscribers (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    daily_news BOOLEAN DEFAULT true,
    weekly_insight BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    verification_token TEXT,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    last_sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. email_send_log 테이블
CREATE TABLE IF NOT EXISTS email_send_log (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER NOT NULL,
    email_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL,
    error_message TEXT,
    deals_count INTEGER,
    deals_ids INTEGER[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (subscriber_id) REFERENCES email_subscribers(id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_subscribers_active ON email_subscribers(is_active);
CREATE INDEX IF NOT EXISTS idx_sendlog_subscriber ON email_send_log(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_sendlog_sent ON email_send_log(sent_at DESC);
