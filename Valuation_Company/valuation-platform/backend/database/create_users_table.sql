-- Users (사용자 역할 관리) 테이블 생성
-- Supabase auth.users와 연결하여 역할(role) 관리
-- 6가지 역할: customer, accountant, admin, investor, partner, supporter

CREATE TABLE IF NOT EXISTS users (
    -- 기본 정보
    user_id UUID PRIMARY KEY,  -- Supabase auth.users.id와 동일
    email VARCHAR(100) UNIQUE NOT NULL,

    -- 역할 관리 (핵심!)
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'accountant', 'admin', 'investor', 'partner', 'supporter')),

    -- 개인 정보
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    profile_image_url TEXT,

    -- 상태 관리
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,

    -- 시스템 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 (이메일과 역할은 공개)
CREATE POLICY "Allow public read access" ON users
    FOR SELECT USING (true);

-- 삽입은 인증된 사용자만 (회원가입 시)
CREATE POLICY "Allow authenticated insert" ON users
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- 본인 정보 업데이트만 가능
CREATE POLICY "Allow users to update own data" ON users
    FOR UPDATE USING (auth.uid() = user_id);

-- 삭제는 관리자만
CREATE POLICY "Allow admin to delete users" ON users
    FOR DELETE USING (
        auth.uid() IN (
            SELECT user_id FROM users WHERE role = 'admin'
        )
    );

-- 트리거: updated_at 자동 갱신
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
