-- Migration: Add dashboard fields based on THE VC, 혁신의숲, Crunchbase research
-- Date: 2026-01-19
-- Description: 대시보드 개선을 위한 새 필드 추가

-- ============================================================
-- startup_companies 테이블에 새 필드 추가
-- ============================================================

-- 지역 (서울 강남, 경기 판교 등)
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS region VARCHAR(100);

-- 직원 수
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS employee_count INTEGER;

-- 설립 연도
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS founded_year INTEGER;

-- 회사 홈페이지 URL
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS website_url VARCHAR(500);

-- 누적 투자 금액 (라운드 합계)
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS cumulative_funding_krw BIGINT DEFAULT 0;

-- 최근 투자 단계 (시드, 프리A, 시리즈A 등)
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS latest_stage VARCHAR(50);

-- 최근 투자 날짜
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS latest_round_date DATE;

-- 대표자 이름
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS ceo_name VARCHAR(100);

-- 간략 설명 (비즈니스 한 줄 요약)
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS description TEXT;

-- 로고 URL
ALTER TABLE startup_companies
ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);


-- ============================================================
-- investment_news 테이블에 새 필드 추가
-- ============================================================

-- 뉴스 원문 URL이 이미 source_url로 있음, 추가 없음


-- ============================================================
-- investment_rounds 테이블에 새 필드 추가
-- ============================================================

-- 참여 투자자 목록 (JSON 배열)
ALTER TABLE investment_rounds
ADD COLUMN IF NOT EXISTS co_investors JSONB DEFAULT '[]';


-- ============================================================
-- 인덱스 추가
-- ============================================================

-- 지역 필터용 인덱스
CREATE INDEX IF NOT EXISTS idx_companies_region
ON startup_companies(region);

-- 설립 연도 인덱스
CREATE INDEX IF NOT EXISTS idx_companies_founded_year
ON startup_companies(founded_year);

-- 직원 수 인덱스
CREATE INDEX IF NOT EXISTS idx_companies_employee_count
ON startup_companies(employee_count);

-- 최근 투자 단계 인덱스
CREATE INDEX IF NOT EXISTS idx_companies_latest_stage
ON startup_companies(latest_stage);


-- ============================================================
-- 코멘트 추가
-- ============================================================

COMMENT ON COLUMN startup_companies.region IS '회사 소재지 (서울 강남, 경기 판교 등)';
COMMENT ON COLUMN startup_companies.employee_count IS '임직원 수';
COMMENT ON COLUMN startup_companies.founded_year IS '설립 연도';
COMMENT ON COLUMN startup_companies.website_url IS '회사 홈페이지 URL';
COMMENT ON COLUMN startup_companies.cumulative_funding_krw IS '누적 투자금액 (원)';
COMMENT ON COLUMN startup_companies.latest_stage IS '최근 투자 단계 (seed, pre_a, series_a 등)';
COMMENT ON COLUMN startup_companies.latest_round_date IS '최근 투자 발표 날짜';
COMMENT ON COLUMN startup_companies.ceo_name IS '대표자 이름';
COMMENT ON COLUMN startup_companies.description IS '비즈니스 한 줄 설명';
COMMENT ON COLUMN startup_companies.logo_url IS '회사 로고 이미지 URL';
COMMENT ON COLUMN investment_rounds.co_investors IS '공동 투자자 목록 (JSON 배열)';
