-- Deal 테이블 생성
CREATE TABLE IF NOT EXISTS "Deal" (
    id BIGSERIAL PRIMARY KEY,
    기업명 TEXT NOT NULL,
    주요사업 TEXT,
    투자자 TEXT,
    투자단계 TEXT,
    투자금액 TEXT,
    지역 TEXT,
    직원수 TEXT,
    뉴스 TEXT,
    뉴스소스 TEXT,
    주차 TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_deal_company ON "Deal"(기업명);
CREATE INDEX IF NOT EXISTS idx_deal_week ON "Deal"(주차);
CREATE INDEX IF NOT EXISTS idx_deal_created ON "Deal"(created_at DESC);

-- 코멘트 추가
COMMENT ON TABLE "Deal" IS '투자 딜 테이블 - 센서블박스 위클리 등 투자유치 기업 정보';
COMMENT ON COLUMN "Deal".기업명 IS '투자 받은 기업명';
COMMENT ON COLUMN "Deal".주요사업 IS '기업의 주요 사업 (이전: 업종)';
COMMENT ON COLUMN "Deal".투자자 IS '투자자 (VC, 엔젤 등)';
COMMENT ON COLUMN "Deal".투자단계 IS '투자 단계 (시드, 시리즈A, 프리IPO 등)';
COMMENT ON COLUMN "Deal".투자금액 IS '투자 금액';
COMMENT ON COLUMN "Deal".뉴스 IS '관련 뉴스 기사 URL';
COMMENT ON COLUMN "Deal".뉴스소스 IS '뉴스 출처 (벤처스퀘어, 플래텀 등)';
COMMENT ON COLUMN "Deal".주차 IS '센서블박스 위클리 주차 (1주차, 2주차 등)';
