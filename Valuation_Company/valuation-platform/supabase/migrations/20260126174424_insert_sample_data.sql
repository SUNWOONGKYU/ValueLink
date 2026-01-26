-- 샘플 평가보고서 데이터 삽입
-- 출처: DART/KIND 실제 공시 자료

-- 1. 시프트업-테이블원 합병 (DCF)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry,
    valuation_method, valuation_amount_display, valuation_date,
    evaluator, report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '시프트업-테이블원', 'Shift Up-Table One', '게임/소프트웨어',
    'dcf', '합병 (100% 자회사 무증자)', '2024-09-30',
    '회계법인', 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20240930000640',

    '시프트업의 100% 자회사인 테이블원과의 합병 거래로, 무증자 합병 방식을 채택하였습니다. DCF 평가법을 활용하여 테이블원의 미래 현금흐름을 할인하여 기업가치를 산정하였으며, 합병비율은 1:0으로 결정되었습니다.',

    '본 평가는 자본시장과 금융투자업에 관한 법률 시행령 제176조의5에 따른 합병가액 산정을 목적으로 수행되었습니다.',

    'DCF(현금흐름할인법)을 주 평가법으로 사용하였으며, WACC는 업종 평균 및 재무구조를 반영하여 산정하였습니다. 영구성장률은 장기 GDP 성장률을 고려하여 보수적으로 적용하였습니다.',

    '테이블원의 기업가치는 향후 5개년 사업계획을 기반으로 산출된 잉여현금흐름을 할인하여 산정하였습니다. 100% 자회사 합병으로 합병비율은 1:0이며, 신주 발행은 없습니다.',

    '본 합병은 경영 효율화 및 조직 통합을 목적으로 하며, 평가 결과는 합리적인 가정 하에 산정되었다고 판단됩니다.',

    ARRAY['합병', '무증자', '자회사'],
    '{"합병비율": "1:0", "신주발행": "없음", "평가기준일": "2024-09-30"}'::jsonb
);

-- 2. NC소프트 분할 (DCF)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, ceo_name, founded_year, location,
    valuation_method, valuation_amount_display, valuation_date,
    evaluator, report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    'NC소프트', 'NCSOFT', '게임', '김택진', '1997', '경기',
    'dcf', '물적분할 (QA+IDS 사업부)', '2024-06-24',
    '회계법인', 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20240624000362',

    'NC소프트의 QA 사업부와 IDS 사업부를 물적분할하여 신설법인을 설립하는 거래입니다. DCF 평가법을 통해 분할 대상 사업부의 현금흐름을 분석하였으며, 분할가액은 순자산가치와 수익가치를 종합적으로 고려하여 산정하였습니다.',

    '본 평가는 회사의 물적분할 계획에 따라 분할 대상 사업부의 공정가치를 산정하기 위해 수행되었습니다.',

    'DCF 평가 시 분할 사업부의 독립적인 사업계획을 기반으로 하였으며, 할인율은 신설법인의 위험 프로필을 반영하여 산정하였습니다.',

    '분할 대상 사업부의 향후 5개년 예상 현금흐름을 할인한 결과, 신설법인의 기업가치를 산출하였습니다. 분할비율은 순자산 기준으로 결정되었습니다.',

    '본 분할은 사업부문 간 전문성 강화 및 독립 경영 체제 구축을 목적으로 하며, 평가 결과는 합리적이라고 판단됩니다.',

    ARRAY['분할', '물적분할', '사업부 분할'],
    '{"분할대상": "QA+IDS", "분할방식": "물적분할", "평가기준일": "2024-06-24"}'::jsonb
);

-- 3. 두산로보틱스 주식교환 (상대가치, PER 38배)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, ceo_name, founded_year, location,
    valuation_method, valuation_amount_display, valuation_date,
    evaluator, report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '두산로보틱스', 'Doosan Robotics', '로봇/제조', '류정훈', '2015', '경기',
    'relative', 'PER 38배', '2024-07-15',
    '회계법인', 'https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain&rcpNo=20240715000610',

    '두산로보틱스와 두산밥캣 간 주식교환 거래로, 상대가치평가법(PER 배수법)을 적용하여 교환가액을 산정하였습니다. 유사 상장기업 4개사(삼익THK, 라온테크, 화낙, 야스카와)의 평균 PER 배수를 산출하고, 경영권 프리미엄 43.7%를 가산하여 최종 PER 38배를 적용하였습니다.',

    '본 평가는 두산로보틱스와 두산밥캣 간 주식교환에 따른 교환가액 산정을 목적으로 수행되었습니다. 2026년 예상 순이익을 기준으로 평가하였습니다.',

    '상대가치평가법 중 PER 배수법을 주 평가법으로 사용하였으며, 비교기업은 로봇 및 정밀기계 업종 내 유사 상장기업으로 선정하였습니다. 비교기업 평균 PER은 27배이며, 경영권 프리미엄 43.7%를 반영하여 최종 PER 38배를 적용하였습니다.',

    '두산로보틱스의 2026년 예상 순이익에 PER 38배를 적용한 결과, 주당 가치를 산출하였습니다. 교환비율은 두산밥캣 보통주 1주당 두산로보틱스 주식 0.2345주로 결정되었습니다.',

    '본 주식교환은 양사 간 시너지 효과 및 경영 효율화를 목적으로 하며, 평가에 사용된 PER 배수 및 경영권 프리미엄은 시장 관행에 부합한다고 판단됩니다.',

    ARRAY['주식교환', 'PER', '경영권 프리미엄'],
    '{"PER": 38, "비교기업_평균_PER": 27, "경영권_프리미엄": 43.7, "예상순이익_기준연도": 2026}'::jsonb
);

-- 4. 고려아연 공개매수 (상대가치)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, ceo_name, founded_year, location,
    valuation_method, valuation_amount_display, valuation_date,
    evaluator, report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '고려아연', 'Korea Zinc', '비철금속', '최윤범', '1974', '서울',
    'relative', '공개매수 주당 83만원', '2024-09-26',
    'MBK파트너스, 영풍', 'https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain&rcpNo=20240926000001',

    'MBK파트너스와 영풍이 공동으로 진행하는 고려아연 공개매수 거래입니다. 공개매수가격은 주당 83만원으로 결정되었으며, 이는 공시일 기준 종가 대비 약 20% 프리미엄을 반영한 가격입니다. 상대가치평가 및 과거 거래가격을 종합적으로 고려하여 산정하였습니다.',

    '본 공개매수는 경영권 확보를 목적으로 하며, 공개매수 기간은 30일입니다. 공개매수 수량은 발행주식총수의 일정 비율로 제한됩니다.',

    '상대가치평가법을 활용하여 유사 비철금속 기업들의 PER, PBR 배수를 분석하였으며, 과거 M&A 거래 프리미엄 사례를 참고하였습니다.',

    '공개매수가 주당 83만원은 시장가 대비 합리적인 프리미엄을 반영한 가격으로, 주주들에게 공정한 매각 기회를 제공합니다.',

    '본 공개매수는 법적 절차에 따라 진행되며, 공개매수 가격은 시장 상황 및 기업 가치를 종합적으로 반영한 합리적인 수준이라고 판단됩니다.',

    ARRAY['공개매수', 'M&A', '경영권'],
    '{"공개매수가": 830000, "프리미엄": "약 20%", "공개매수자": "MBK+영풍"}'::jsonb
);

-- 5. 하이브-SM엔터 지분취득 (상대가치)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, location,
    valuation_method, valuation_amount_display, valuation_date,
    evaluator, report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '하이브-SM엔터테인먼트', 'HYBE-SM Entertainment', '엔터테인먼트', '서울',
    'relative', '지분취득', '2024-02-28',
    '회계법인', 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20240228801368',

    '하이브가 SM엔터테인먼트 지분을 취득하는 거래로, 상대가치평가법을 통해 SM엔터의 주당 가치를 산정하였습니다. 엔터테인먼트 업종 내 유사기업 비교 분석을 수행하였으며, SM엔터의 IP 가치 및 아티스트 포트폴리오를 정성적으로 평가하였습니다.',

    '본 평가는 하이브의 SM엔터 지분 취득에 따른 적정 거래가액 산정을 목적으로 수행되었습니다.',

    '상대가치평가법(PER, EV/EBITDA)을 사용하였으며, 비교기업으로는 JYP엔터, YG엔터 등 K-POP 엔터테인먼트 기업을 선정하였습니다.',

    'SM엔터의 예상 실적 및 유사기업 평균 배수를 적용하여 주당 가치를 산출하였으며, 지분 취득 거래가격은 시장 공정가치 범위 내에 있습니다.',

    '본 거래는 엔터테인먼트 산업 내 시너지 효과 및 글로벌 경쟁력 강화를 목적으로 하며, 평가 결과는 합리적이라고 판단됩니다.',

    ARRAY['지분취득', 'M&A', '엔터테인먼트'],
    '{"취득방식": "지분취득", "평가방법": "PER, EV/EBITDA"}'::jsonb
);

-- 6. RF시스템즈-교보SPAC 합병 (본질가치, 자본시장법)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry,
    valuation_method, valuation_amount_display, valuation_date,
    evaluator, report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    'RF시스템즈-교보12호스팩', 'RF Systems-Kyobo SPAC', '통신장비',
    'intrinsic', '합병 (자산×1 + 수익×1.5)/2.5', '2024-10-21',
    '이촌회계법인', 'https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain&rcpNo=20241021000879',

    'RF시스템즈와 교보12호스팩 간 합병 거래로, 자본시장법 시행령 제176조의5에 따른 본질가치평가법을 적용하였습니다. (자산가치 × 1 + 수익가치 × 1.5) ÷ 2.5 공식을 사용하여 RF시스템즈의 기업가치를 산정하였으며, 자산가치 40%, 수익가치 60% 비율로 가중평균하였습니다.',

    '본 평가는 자본시장과 금융투자업에 관한 법률에 따른 합병가액 산정을 목적으로 수행되었습니다. 외부 독립평가기관인 이촌회계법인이 평가를 수행하였습니다.',

    '본질가치평가법은 자산가치와 수익가치를 1:1.5 비율로 가중평균하는 방식입니다. 자산가치는 순자산 기준으로 산정하였으며, 수익가치는 과거 3개년 평균 순이익에 자기자본이익률(ROE)을 적용하여 계산하였습니다.',

    '(자산가치 × 1 + 수익가치 × 1.5) ÷ 2.5 공식을 적용한 결과, RF시스템즈의 기업가치를 산출하였습니다. 합병비율은 산정된 기업가치를 기준으로 결정되었습니다.',

    '본 합병은 SPAC 합병 절차에 따라 진행되며, 평가 방법은 자본시장법에서 규정한 방식을 준수하였습니다. 평가 결과는 법적 요건을 충족한다고 판단됩니다.',

    ARRAY['SPAC합병', '본질가치', '자본시장법'],
    '{"공식": "(자산×1 + 수익×1.5)/2.5", "자산가치_비중": 40, "수익가치_비중": 60, "평가기관": "이촌회계법인"}'::jsonb
);

-- 7. 클래시스-이루다 합병 (자산가치, NAV)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, location,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date,
    report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '클래시스-이루다', 'Classys-Iruda', '의료기기', '서울',
    'asset', 283500000000, '합병 (순자산 2,835억원)', '2024-07-18',
    'https://kind.krx.co.kr',

    '클래시스와 이루다의 합병 거래로, 자산가치평가법(NAV)을 적용하여 순자산가치 기준 기업가치를 산정하였습니다. 이루다의 순자산은 2,835억원으로 평가되었으며, 합병비율은 클래시스 1주당 이루다 0.1405237주로 결정되었습니다.',

    '본 평가는 클래시스-이루다 합병에 따른 합병가액 산정을 목적으로 수행되었습니다. 순자산가치 기준 평가를 통해 합병비율을 산출하였습니다.',

    '자산가치평가법은 기업의 순자산(총자산 - 총부채)을 기준으로 가치를 산정하는 방법입니다. 장부가액을 기준으로 하되, 주요 자산의 공정가치 조정을 반영하였습니다.',

    '이루다의 순자산가치는 2,835억원으로 평가되었으며, 클래시스와의 합병비율은 1:0.1405237로 산출되었습니다.',

    '본 합병은 양사 간 사업 통합 및 시너지 효과를 목적으로 하며, 순자산 기준 평가 결과는 합리적이라고 판단됩니다.',

    ARRAY['합병', 'NAV', '순자산가치'],
    '{"순자산": 283500000000, "합병비율": "1:0.1405237"}'::jsonb
);

-- 8. SK이노베이션-SK E&S 합병 (자산가치)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, location,
    valuation_method, valuation_amount_display, valuation_date,
    report_url,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    'SK이노베이션-SK E&S', 'SK Innovation-SK E&S', '에너지/화학', '서울',
    'asset', '합병 (자산 100조원 규모)', '2024-07-17',
    'https://kind.krx.co.kr',

    'SK이노베이션과 SK E&S의 대형 합병 거래로, 양사의 총자산 규모는 약 100조원에 달합니다. 자산가치평가법을 주 평가법으로 사용하였으며, 본질가치평가법과의 비교 검토를 통해 합병비율을 산정하였습니다. 합병비율은 SK이노베이션 1주당 SK E&S 1.1917417주로 결정되었습니다.',

    '본 평가는 SK이노베이션과 SK E&S 간 대형 합병 거래에 따른 합병가액 산정을 목적으로 수행되었습니다. 에너지 및 화학 산업 내 수직계열화 및 시너지 효과를 목적으로 합니다.',

    '자산가치평가법을 주 평가법으로 사용하되, 본질가치평가법(자산가치×40% + 수익가치×60%)과의 교차 검증을 수행하였습니다. 주요 자산의 공정가치 평가를 반영하였습니다.',

    '양사의 순자산가치를 산정하고, 시가 총액 및 본질가치와 비교한 결과, 합병비율 1:1.1917417이 적정하다고 판단하였습니다.',

    '본 합병은 에너지 산업 재편 및 탄소중립 전환을 목적으로 하며, 평가 결과는 다각적 검토를 거쳐 합리적으로 산정되었다고 판단됩니다. 다만, 시가와 본질가치 간 차이에 대한 논란이 일부 존재합니다.',

    ARRAY['합병', '대형합병', '에너지'],
    '{"총자산": "약 100조원", "합병비율": "1:1.1917417", "매출": "88조원"}'::jsonb
);

-- 9. 비상장법인 (상증세법평가법)
INSERT INTO valuation_reports (
    company_name, industry,
    valuation_method, valuation_amount_krw, valuation_amount_display, valuation_date,
    evaluator,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '비상장법인 (조심 사례)', '제조업',
    'inheritance_tax', 49500000000, '495억원', '2023-06-29',
    '조세심판원',

    '비상장주식 평가 관련 조세심판원 결정례로, 상속세 및 증여세법 시행령 제54조에 따른 보충적 평가방법을 적용하였습니다. (순손익가치 × 3 + 순자산가치 × 2) ÷ 5 공식을 사용하여 1주당 가치를 산정하였으며, 80% 하한선 규정(순자산가치의 80%)을 적용하였습니다.',

    '본 평가는 상속세 과세표준 산정을 목적으로 수행되었으며, 국세청과 납세자 간 평가액 차이에 대한 심판 사례입니다.',

    '상증세법 시행령 제54조의 보충적 평가방법은 (직전 3년간 순손익가치 × 3 + 순자산가치 × 2) ÷ 5 공식을 사용합니다. 순손익가치는 최근 3개년 평균 순손익에 가중치를 부여하여 계산하며, 순자산가치는 평가기준일 현재 장부가액을 기준으로 합니다. 단, 평가액이 순자산가치의 80%보다 낮을 경우 80% 금액을 최소값으로 적용합니다.',

    '보충적 평가방법 적용 결과 1주당 가치는 495만원으로 산정되었습니다. 이는 순자산가치의 80% 하한선을 상회하는 금액입니다.',

    '본 평가는 상증세법 규정에 따라 산정되었으며, DCF법 등 다른 평가방법은 시가로 인정되지 않습니다. 특수관계자 간 거래 시 저가 양수도에 따른 증여세 과세 사례입니다.',

    ARRAY['상속세', '증여세', '보충적평가', '비상장주식'],
    '{"공식": "(순손익×3 + 순자산×2)/5", "하한선": "순자산의 80%", "결정번호": "조심2023서0142"}'::jsonb
);

-- 10. 엔키노에이아이 (DCF, 기존 데이터)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, location,
    valuation_method, valuation_amount_krw, valuation_amount_display,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '엔키노에이아이', 'Enkino AI', 'AI/기술', '서울',
    'dcf', 16300000000, '163억원',

    'AI 기반 솔루션 개발 스타트업으로, DCF 평가법을 통해 향후 5개년 사업계획을 기반으로 기업가치를 산정하였습니다. 예상 연평균 성장률 25%, WACC 12%를 적용하여 현재가치를 할인한 결과, 기업가치는 163억원으로 평가되었습니다.',

    '본 평가는 시리즈 A 투자 유치를 목적으로 수행되었으며, AI 산업 성장성 및 기술 경쟁력을 반영하였습니다.',

    'DCF 평가 시 향후 5개년 매출 및 영업이익 전망을 기반으로 잉여현금흐름(FCF)을 추정하였습니다. WACC는 무위험수익률 3.5%, 시장위험 프리미엄 8.5%, 베타 1.3을 적용하여 산정하였습니다.',

    '기업가치는 163억원으로 산출되었으며, 보통주 1주당 가치는 32,600원입니다. 희석 후 주식가치는 시리즈 A 신주 발행을 고려하여 조정되었습니다.',

    'AI 산업의 높은 성장 가능성과 기술 경쟁력을 고려할 때, 평가 결과는 합리적이라고 판단됩니다.',

    ARRAY['스타트업', 'AI', '시리즈A'],
    '{"기업가치": 16300000000, "WACC": 12, "성장률": 25, "평가목적": "시리즈A 투자유치"}'::jsonb
);

-- 11. 삼성전자 (상대가치)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, ceo_name, founded_year, location, employee_count,
    valuation_method, valuation_amount_krw, valuation_amount_display,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '삼성전자', 'Samsung Electronics', '전기전자', '한종희', '1969', '경기', '267,800명',
    'relative', 578000000000000, '578조원',

    '글로벌 전자 산업을 선도하는 삼성전자의 기업가치를 상대가치평가법으로 산정하였습니다. 글로벌 반도체 및 가전 기업(TSMC, Intel, Sony 등) 대비 PER, PBR 배수를 비교 분석하였으며, 시가총액 기준 578조원으로 평가되었습니다.',

    '본 평가는 시장 공정가치 분석을 목적으로 수행되었으며, 글로벌 경쟁사 대비 상대적 가치를 평가하였습니다.',

    '상대가치평가법 중 PER, PBR, EV/EBITDA 배수를 종합적으로 적용하였습니다. 비교기업으로는 TSMC, Intel, Sony, LG전자 등을 선정하였습니다.',

    '삼성전자의 시가총액은 578조원으로, 이는 글로벌 반도체 업체 평균 PER 15배 수준에 해당합니다. 메모리 반도체 업황 및 AI 반도체 성장성을 고려한 적정 수준입니다.',

    '삼성전자는 메모리 반도체 분야 세계 1위 기업으로, 현재 밸류에이션은 업종 평균 대비 적정 수준이라고 판단됩니다.',

    ARRAY['대기업', '반도체', '글로벌'],
    '{"시가총액": 578000000000000, "PER": 15, "PBR": 1.2, "업종": "반도체"}'::jsonb
);

-- 12. 카카오 (본질가치)
INSERT INTO valuation_reports (
    company_name, company_name_en, industry, ceo_name, founded_year, location, employee_count,
    valuation_method, valuation_amount_krw, valuation_amount_display,
    executive_summary, evaluation_overview, methodology, valuation_results, conclusion,
    tags, key_metrics
) VALUES (
    '카카오', 'Kakao', '플랫폼/IT', '정신아', '2010', '경기', '7,500명',
    'intrinsic', 3100000000000, '3.1조원',

    '국내 대표 플랫폼 기업 카카오의 기업가치를 본질가치평가법으로 산정하였습니다. (자산가치 × 1 + 수익가치 × 1.5) ÷ 2.5 공식을 적용하여, 자산가치 40%, 수익가치 60% 비율로 가중평균한 결과 3.1조원으로 평가되었습니다.',

    '본 평가는 자본시장법에 따른 공정가치 평가를 목적으로 수행되었으며, 플랫폼 비즈니스의 자산 및 수익 구조를 종합적으로 반영하였습니다.',

    '본질가치평가법은 순자산가치와 수익가치를 1:1.5 비율로 가중평균합니다. 수익가치는 최근 3개년 평균 순이익을 기준으로 산정하였습니다.',

    '카카오의 순자산 기준 자산가치와 수익성 기반 수익가치를 종합한 결과, 기업가치는 3.1조원으로 산출되었습니다.',

    '플랫폼 비즈니스의 특성상 수익가치 비중이 높게 반영되었으며, 평가 결과는 합리적이라고 판단됩니다.',

    ARRAY['플랫폼', '대기업', '본질가치'],
    '{"기업가치": 3100000000000, "공식": "(자산×1 + 수익×1.5)/2.5", "자산가치_비중": 40, "수익가치_비중": 60}'::jsonb
);

COMMENT ON TABLE valuation_reports IS '실제 DART/KIND 공시 기반 평가보고서 샘플 데이터 (12개 기업)';
