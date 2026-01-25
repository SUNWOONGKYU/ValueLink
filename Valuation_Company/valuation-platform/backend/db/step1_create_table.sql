-- 1단계: 테이블 생성
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
