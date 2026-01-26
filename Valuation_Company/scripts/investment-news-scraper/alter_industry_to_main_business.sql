-- Deal 테이블 컬럼명 변경: industry → main_business
-- 2026-01-27

-- 1. 컬럼명 변경
ALTER TABLE deals
RENAME COLUMN industry TO main_business;

-- 2. 컬럼 코멘트 추가
COMMENT ON COLUMN deals.main_business IS '기업의 주요 사업 (이전: 업종/industry)';
