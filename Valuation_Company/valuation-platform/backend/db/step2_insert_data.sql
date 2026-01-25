-- 2단계: 선웅규 회계사 데이터 삽입
INSERT INTO accountants (
    id,
    name,
    cpa_number,
    cpa_type,
    license_date,
    experience_years,
    current_position,
    current_company,
    bio,
    total_projects,
    completed_projects,
    is_active
) VALUES (
    'ACC001',
    '선웅규',
    '2353',
    'KICPA',
    '2010-06-01',
    15,
    '수석회계사',
    'ValueLink',
    '15년 경력의 기업가치평가 전문가입니다.',
    150,
    150,
    TRUE
);
