-- 공인회계사 테이블 생성 (간소화 버전)
CREATE TABLE IF NOT EXISTS accountants (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cpa_number VARCHAR(50),
    cpa_type VARCHAR(50),
    license_date DATE,
    experience_years INT DEFAULT 0,
    current_position VARCHAR(100),
    current_company VARCHAR(100),
    specialties JSONB,
    education JSONB,
    career JSONB,
    profile_image_url TEXT,
    bio TEXT,
    total_projects INT DEFAULT 0,
    completed_projects INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_accountants_name ON accountants(name);
CREATE INDEX IF NOT EXISTS idx_accountants_is_active ON accountants(is_active);

-- 프로젝트별 담당 회계사 매핑 테이블
CREATE TABLE IF NOT EXISTS project_accountants (
    project_id VARCHAR(50) NOT NULL,
    accountant_id VARCHAR(50) NOT NULL REFERENCES accountants(id) ON DELETE CASCADE,
    assigned_date TIMESTAMP DEFAULT NOW(),
    role VARCHAR(50) DEFAULT 'primary',
    PRIMARY KEY (project_id, accountant_id, role)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_project_accountants_project ON project_accountants(project_id);
CREATE INDEX IF NOT EXISTS idx_project_accountants_accountant ON project_accountants(accountant_id);

-- 선웅규 회계사 데이터 삽입
INSERT INTO accountants (
    id,
    name,
    cpa_number,
    cpa_type,
    license_date,
    experience_years,
    current_position,
    current_company,
    specialties,
    education,
    career,
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
    '["DCF평가", "스타트업 기업가치평가", "IPO 준비"]',
    '[{"degree": "학사", "school": "연세대학교", "major": "경영학과", "year": 2005}]',
    '[{"period": "2020년 - 현재", "company": "ValueLink", "position": "수석회계사", "description": "기업가치평가 총괄"}, {"period": "2015년 - 2020년", "company": "호수회계법인", "position": "Manager", "description": "기업가치평가 업무"}, {"period": "2012년 - 2015년", "company": "안근회계법인", "position": "Senior", "description": "기업가치평가 및 실사"}, {"period": "2010년 - 2012년", "company": "세화회계법인", "position": "Staff", "description": "회계감사 및 평가 업무"}, {"period": "2008년 - 2010년", "company": "삼일회계법인", "position": "Junior", "description": "회계감사 보조 업무"}]',
    '15년 경력의 기업가치평가 전문가입니다. DCF평가, 스타트업 평가, IPO 준비 자문을 전문으로 합니다.',
    150,
    150,
    TRUE
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    cpa_number = EXCLUDED.cpa_number,
    cpa_type = EXCLUDED.cpa_type,
    license_date = EXCLUDED.license_date,
    experience_years = EXCLUDED.experience_years,
    current_position = EXCLUDED.current_position,
    current_company = EXCLUDED.current_company,
    specialties = EXCLUDED.specialties,
    education = EXCLUDED.education,
    career = EXCLUDED.career,
    bio = EXCLUDED.bio,
    total_projects = EXCLUDED.total_projects,
    completed_projects = EXCLUDED.completed_projects,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- 데이터 확인
SELECT * FROM accountants WHERE id = 'ACC001';
