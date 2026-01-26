-- 평가보고서 테이블 생성
-- 샘플 보고서 데이터 저장용

CREATE TABLE IF NOT EXISTS valuation_reports (
    id SERIAL PRIMARY KEY,

    -- 기업 기본 정보
    company_name VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    industry VARCHAR(100),
    ceo_name VARCHAR(100),
    founded_year VARCHAR(20),
    location VARCHAR(100),
    employee_count VARCHAR(50),

    -- 평가 정보
    valuation_method VARCHAR(50) NOT NULL,  -- 'dcf', 'relative', 'intrinsic', 'asset', 'inheritance_tax'
    valuation_amount_krw BIGINT,
    valuation_amount_display VARCHAR(100),  -- "PER 38배", "합병", "공개매수 83만원" 등 표시용
    valuation_date DATE,
    evaluator VARCHAR(200),  -- 평가기관 (한미회계법인, 이촌회계법인 등)

    -- 평가보고서 주요 섹션 (9개 중 핵심)
    executive_summary TEXT,           -- 1. 요약
    evaluation_overview TEXT,         -- 2. 평가 개요
    company_analysis TEXT,            -- 3. 회사 개요 및 산업 분석
    financial_summary TEXT,           -- 4. 재무 분석 (요약)
    methodology TEXT,                 -- 5. 평가 방법론 및 가정
    valuation_results TEXT,           -- 6. 평가 결과
    sensitivity_analysis TEXT,        -- 7. 민감도 분석
    conclusion TEXT,                  -- 8. 결론
    appendix TEXT,                    -- 9. 부록

    -- 외부 링크
    report_url VARCHAR(500),  -- DART/KIND 원본 공시 링크
    pdf_url VARCHAR(500),     -- PDF 파일 URL (있는 경우)

    -- 추가 메타데이터
    tags TEXT[],              -- 태그 배열: ['합병', 'SPAC', 'IPO' 등]
    key_metrics JSONB,        -- 주요 지표 JSON: {"PER": 38, "PBR": 5.2, "성장률": 15}

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX idx_valuation_reports_company_name ON valuation_reports(company_name);
CREATE INDEX idx_valuation_reports_method ON valuation_reports(valuation_method);
CREATE INDEX idx_valuation_reports_date ON valuation_reports(valuation_date DESC);

-- 업데이트 시간 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_valuation_reports_updated_at
    BEFORE UPDATE ON valuation_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 코멘트 추가
COMMENT ON TABLE valuation_reports IS '기업 평가보고서 샘플 데이터 (DART/KIND 수집)';
COMMENT ON COLUMN valuation_reports.valuation_method IS 'dcf: DCF평가법, relative: 상대가치평가법, intrinsic: 본질가치평가법, asset: 자산가치평가법, inheritance_tax: 상증세법평가법';
COMMENT ON COLUMN valuation_reports.key_metrics IS 'JSON 형식의 주요 지표: {"PER": 38, "PBR": 5.2, "WACC": 8.5, "성장률": 15}';
