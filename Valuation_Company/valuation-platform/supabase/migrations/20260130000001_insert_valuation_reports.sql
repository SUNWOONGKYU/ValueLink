-- valuation_reports 테이블에 샘플 데이터 삽입
-- Link 페이지에 표시될 평가받은 기업 목록

-- 기존 데이터 삭제 (선택적)
-- DELETE FROM valuation_reports;

-- 1. 엔키노에이아이 (DCF평가법)
INSERT INTO valuation_reports (
    company_name, ceo_name, industry, founded_year, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date
) VALUES (
    '엔키노에이아이', NULL, 'AI/기술', NULL, '서울',
    'dcf', 16300000000, '163억원', '2025-12-15'
);

-- 2. 삼성전자 (상대가치평가법)
INSERT INTO valuation_reports (
    company_name, ceo_name, industry, founded_year, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date
) VALUES (
    '삼성전자', '한종희', '전기전자', '1969년', '경기',
    'relative', 578000000000000, '578조원', '2026-01-10'
);

-- 3. 두산로보틱스 (상대가치평가법)
INSERT INTO valuation_reports (
    company_name, ceo_name, industry, founded_year, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date
) VALUES (
    '두산로보틱스', '류정훈', '로봇/제조', '2015년', '경기',
    'relative', NULL, 'PER 38배', '2026-01-08'
);

-- 4. 카카오 (본질가치평가법)
INSERT INTO valuation_reports (
    company_name, ceo_name, industry, founded_year, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date
) VALUES (
    '카카오', '정신아', '플랫폼/IT', '2010년', '경기',
    'intrinsic', 3100000000000, '3.1조원', '2026-01-05'
);

-- 5. 클래시스 (자산가치평가법)
INSERT INTO valuation_reports (
    company_name, ceo_name, industry, founded_year, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date
) VALUES (
    '클래시스', NULL, '의료기기', NULL, '서울',
    'asset', 283500000000, '2,835억원', '2025-11-20'
);

-- 6. 비상장법인 (상증세법평가법)
INSERT INTO valuation_reports (
    company_name, ceo_name, industry, founded_year, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date
) VALUES (
    '비상장법인 (조심사례)', NULL, NULL, NULL, NULL,
    'inheritance_tax', 49500000000, '495억원', '2025-10-30'
);
