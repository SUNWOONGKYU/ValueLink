-- 3단계: JSON 데이터 업데이트
UPDATE accountants SET specialties = '["DCF평가", "스타트업 기업가치평가", "IPO 준비"]'::jsonb WHERE id = 'ACC001';

UPDATE accountants SET education = '[{"degree": "학사", "school": "연세대학교", "major": "경영학과", "year": 2005}]'::jsonb WHERE id = 'ACC001';

UPDATE accountants SET career = '[
    {"period": "2020년 - 현재", "company": "ValueLink", "position": "수석회계사", "description": "기업가치평가 총괄"},
    {"period": "2015년 - 2020년", "company": "호수회계법인", "position": "Manager", "description": "기업가치평가 업무"},
    {"period": "2012년 - 2015년", "company": "안근회계법인", "position": "Senior", "description": "기업가치평가 및 실사"},
    {"period": "2010년 - 2012년", "company": "세화회계법인", "position": "Staff", "description": "회계감사 및 평가 업무"},
    {"period": "2008년 - 2010년", "company": "삼일회계법인", "position": "Junior", "description": "회계감사 보조 업무"}
]'::jsonb WHERE id = 'ACC001';
