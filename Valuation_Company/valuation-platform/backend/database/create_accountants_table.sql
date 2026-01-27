-- Accountants (공인회계사) 테이블 생성
-- 평가를 수행하는 전문가 정보 관리

CREATE TABLE IF NOT EXISTS accountants (
    -- 기본 정보
    accountant_id VARCHAR(20) PRIMARY KEY,  -- ACC + timestamp 형식
    user_id UUID NOT NULL UNIQUE,

    -- 자격 정보
    license_number VARCHAR(50) NOT NULL UNIQUE,  -- 공인회계사 자격증 번호
    license_issue_date DATE,
    license_issuer VARCHAR(100) DEFAULT '한국공인회계사회',

    -- 학력 (배열)
    education TEXT[],

    -- 경력 (배열)
    career TEXT[],

    -- 전문 분야 (배열)
    specialization VARCHAR(100)[],  -- 예: DCF, 상대가치, 본질가치 등

    -- 프로필
    bio TEXT,  -- 소개
    profile_summary TEXT,  -- 간단 요약 (1-2문장)

    -- 통계
    rating DECIMAL(3,2) DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5.00),  -- 평점 (0.00 ~ 5.00)
    total_projects INTEGER DEFAULT 0,  -- 수행한 총 프로젝트 수
    completed_projects INTEGER DEFAULT 0,  -- 완료한 프로젝트 수

    -- 상태
    is_available BOOLEAN DEFAULT true,  -- 배정 가능 여부
    max_concurrent_projects INTEGER DEFAULT 3,  -- 동시 진행 가능한 최대 프로젝트 수

    -- 시스템 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 외래키
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_accountants_user_id ON accountants(user_id);
CREATE INDEX IF NOT EXISTS idx_accountants_license ON accountants(license_number);
CREATE INDEX IF NOT EXISTS idx_accountants_available ON accountants(is_available);
CREATE INDEX IF NOT EXISTS idx_accountants_rating ON accountants(rating);

-- RLS 활성화
ALTER TABLE accountants ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 (프로필은 모두 볼 수 있음)
CREATE POLICY "Allow public read access" ON accountants
    FOR SELECT USING (true);

-- 본인 정보 업데이트만 가능
CREATE POLICY "Allow accountants to update own data" ON accountants
    FOR UPDATE USING (
        auth.uid() IN (
            SELECT user_id FROM accountants WHERE user_id = auth.uid()
        )
    );

-- 삽입은 인증된 사용자만 (회원가입 시)
CREATE POLICY "Allow authenticated insert" ON accountants
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- 삭제는 본인 또는 관리자만
CREATE POLICY "Allow delete own or admin" ON accountants
    FOR DELETE USING (
        auth.uid() = user_id OR
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'admin'
        )
    );

-- 트리거: updated_at 자동 갱신
CREATE TRIGGER update_accountants_updated_at
    BEFORE UPDATE ON accountants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 함수: accountant_id 자동 생성
CREATE OR REPLACE FUNCTION generate_accountant_id()
RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN 'ACC' || FLOOR(EXTRACT(EPOCH FROM NOW()) * 1000)::TEXT;
END;
$$ LANGUAGE plpgsql;
