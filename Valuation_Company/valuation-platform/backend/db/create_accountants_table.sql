-- 공인회계사 테이블 생성
CREATE TABLE IF NOT EXISTS accountants (
    -- 기본 정보
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),

    -- 자격 정보
    cpa_number VARCHAR(50),
    cpa_type VARCHAR(50), -- 'KICPA', 'AICPA', 'KICPA+AICPA'
    license_date DATE,

    -- 경력 정보
    experience_years INT DEFAULT 0,
    current_position VARCHAR(100), -- '수석회계사', 'Manager' 등
    current_company VARCHAR(100),

    -- 전문 분야 (JSON 배열)
    specialties JSONB, -- ["DCF평가", "스타트업 평가", "IPO"]

    -- 학력 정보 (JSON 배열)
    education JSONB, -- [{"degree": "학사", "school": "서울대", "major": "경영학", "year": 2005}]

    -- 경력 정보 (JSON 배열)
    career JSONB, -- [{"period": "2020-현재", "company": "ValueLink", "position": "수석회계사", "description": "..."}]

    -- 프로필
    profile_image_url TEXT,
    bio TEXT,

    -- 실적
    total_projects INT DEFAULT 0,
    completed_projects INT DEFAULT 0,

    -- 수상 및 자격증 (JSON 배열)
    awards JSONB, -- [{"year": 2022, "title": "우수 평가사", "organization": "한국감정원"}]

    -- 활성화 상태
    is_active BOOLEAN DEFAULT TRUE,

    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_accountants_name ON accountants(name);
CREATE INDEX idx_accountants_email ON accountants(email);
CREATE INDEX idx_accountants_is_active ON accountants(is_active);

-- 샘플 데이터 삽입 (선웅규 회계사)
INSERT INTO accountants (
    id,
    name,
    email,
    phone,
    cpa_number,
    cpa_type,
    license_date,
    experience_years,
    current_position,
    current_company,
    specialties,
    education,
    career,
    profile_image_url,
    bio,
    total_projects,
    completed_projects,
    awards,
    is_active
) VALUES (
    'ACC001',
    '선웅규',
    'sunny@valuelink.com',
    '02-1234-5678',
    '2353',
    'KICPA+AICPA',
    '2010-06-01',
    15,
    '수석회계사',
    'ValueLink',
    '["DCF평가", "스타트업 기업가치평가", "IPO 준비"]'::jsonb,
    '[
        {"degree": "학사", "school": "서울대학교", "major": "경영학과", "year": 2005},
        {"degree": "석사", "school": "연세대학교", "major": "경영대학원", "year": 2008},
        {"degree": "자격증", "school": "미국 공인회계사", "major": "AICPA", "year": 2010}
    ]'::jsonb,
    '[
        {
            "period": "2020년 - 현재",
            "company": "ValueLink",
            "position": "수석회계사",
            "description": "기업가치평가 총괄"
        },
        {
            "period": "2015년 - 2020년",
            "company": "삼일회계법인",
            "position": "Manager",
            "description": "M&A 및 평가 업무"
        },
        {
            "period": "2010년 - 2015년",
            "company": "딜로이트 안진",
            "position": "Senior Consultant",
            "description": "기업가치평가 및 실사"
        }
    ]'::jsonb,
    '/assets/images/accountants/sunny.jpg',
    '15년 경력의 기업가치평가 전문가입니다. DCF평가, 스타트업 평가, IPO 준비 자문을 전문으로 합니다.',
    150,
    150,
    '[
        {"year": 2022, "title": "우수 평가사", "organization": "한국감정원"}
    ]'::jsonb,
    TRUE
);

-- 프로젝트별 담당 회계사 매핑 테이블
CREATE TABLE IF NOT EXISTS project_accountants (
    project_id VARCHAR(50) NOT NULL,
    accountant_id VARCHAR(50) NOT NULL REFERENCES accountants(id) ON DELETE CASCADE,
    assigned_date TIMESTAMP DEFAULT NOW(),
    role VARCHAR(50) DEFAULT 'primary', -- 'primary', 'reviewer', 'consultant'
    PRIMARY KEY (project_id, accountant_id, role)
);

-- 인덱스 생성
CREATE INDEX idx_project_accountants_project ON project_accountants(project_id);
CREATE INDEX idx_project_accountants_accountant ON project_accountants(accountant_id);

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_accountants_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_accountants_updated_at
    BEFORE UPDATE ON accountants
    FOR EACH ROW
    EXECUTE FUNCTION update_accountants_updated_at();

-- 코멘트 추가
COMMENT ON TABLE accountants IS '공인회계사 정보 테이블';
COMMENT ON COLUMN accountants.id IS '회계사 고유 ID';
COMMENT ON COLUMN accountants.specialties IS '전문 분야 (JSON 배열)';
COMMENT ON COLUMN accountants.education IS '학력 정보 (JSON 배열)';
COMMENT ON COLUMN accountants.career IS '경력 정보 (JSON 배열)';
COMMENT ON COLUMN accountants.awards IS '수상 및 자격증 (JSON 배열)';

COMMENT ON TABLE project_accountants IS '프로젝트별 담당 회계사 매핑 테이블';
