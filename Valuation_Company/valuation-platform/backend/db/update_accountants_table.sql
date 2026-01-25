-- 불필요한 컬럼 삭제
ALTER TABLE accountants DROP COLUMN IF EXISTS email;
ALTER TABLE accountants DROP COLUMN IF EXISTS phone;
ALTER TABLE accountants DROP COLUMN IF EXISTS awards;

-- 선웅규 회계사 데이터 업데이트
UPDATE accountants
SET
    name = '선웅규',
    cpa_number = '2353',
    cpa_type = 'KICPA',
    license_date = '2010-06-01',
    experience_years = 15,
    current_position = '수석회계사',
    current_company = 'ValueLink',
    specialties = '["DCF평가", "스타트업 기업가치평가", "IPO 준비"]'::jsonb,
    education = '[
        {"degree": "학사", "school": "연세대학교", "major": "경영학과", "year": 2005}
    ]'::jsonb,
    career = '[
        {
            "period": "2020년 - 현재",
            "company": "ValueLink",
            "position": "수석회계사",
            "description": "기업가치평가 총괄"
        },
        {
            "period": "2015년 - 2020년",
            "company": "호수회계법인",
            "position": "Manager",
            "description": "기업가치평가 업무"
        },
        {
            "period": "2012년 - 2015년",
            "company": "안근회계법인",
            "position": "Senior",
            "description": "기업가치평가 및 실사"
        },
        {
            "period": "2010년 - 2012년",
            "company": "세화회계법인",
            "position": "Staff",
            "description": "회계감사 및 평가 업무"
        },
        {
            "period": "2008년 - 2010년",
            "company": "삼일회계법인",
            "position": "Junior",
            "description": "회계감사 보조 업무"
        }
    ]'::jsonb,
    bio = '15년 경력의 기업가치평가 전문가입니다. DCF평가, 스타트업 평가, IPO 준비 자문을 전문으로 합니다.',
    total_projects = 150,
    completed_projects = 150,
    is_active = TRUE,
    updated_at = NOW()
WHERE id = 'ACC001';

-- 데이터 확인
SELECT
    id,
    name,
    experience_years,
    current_position,
    current_company,
    specialties,
    education,
    career
FROM accountants
WHERE id = 'ACC001';
