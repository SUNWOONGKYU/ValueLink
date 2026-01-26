-- valuation_reports 테이블에 공개 읽기 권한 부여
-- Row Level Security (RLS) 정책 설정

-- RLS 활성화
ALTER TABLE valuation_reports ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 추가 (누구나 조회 가능)
CREATE POLICY "Enable read access for all users" ON valuation_reports
    FOR SELECT
    USING (true);

-- 정책 확인
COMMENT ON POLICY "Enable read access for all users" ON valuation_reports IS '모든 사용자가 평가보고서를 조회할 수 있습니다 (공개 샘플 데이터)';
