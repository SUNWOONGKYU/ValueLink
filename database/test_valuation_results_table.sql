/**
 * @description 테스트 평가 결과 저장 테이블
 *
 * 3개 모의 기업의 5개 평가 방법별 결과를 저장
 */

-- 테이블 생성
CREATE TABLE IF NOT EXISTS test_valuation_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 기업 정보
    company_id VARCHAR(50) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    situation VARCHAR(100),

    -- 평가 정보
    method VARCHAR(20) NOT NULL,

    -- 평가 결과
    enterprise_value BIGINT,
    equity_value BIGINT,
    share_price INTEGER,

    -- 상세 내역 (JSONB)
    details JSONB,

    -- 초안 섹션 (JSONB)
    draft_sections JSONB,

    -- 메타데이터
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),

    -- 인덱스를 위한 제약조건
    UNIQUE(company_id, method)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_test_valuation_company ON test_valuation_results(company_id);
CREATE INDEX IF NOT EXISTS idx_test_valuation_method ON test_valuation_results(method);
CREATE INDEX IF NOT EXISTS idx_test_valuation_created ON test_valuation_results(created_at DESC);

-- RLS 정책 (모든 사용자 읽기 가능)
ALTER TABLE test_valuation_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Allow public read access"
ON test_valuation_results FOR SELECT
USING (true);

CREATE POLICY IF NOT EXISTS "Allow insert for authenticated users"
ON test_valuation_results FOR INSERT
TO authenticated
WITH CHECK (true);

COMMENT ON TABLE test_valuation_results IS '테스트 평가 결과 저장 테이블 - 3개 모의 기업의 평가 데이터';
