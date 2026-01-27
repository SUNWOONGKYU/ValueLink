-- Customers 테이블 수정
-- users 테이블과 연결 및 영문 회사명 추가

-- 1. user_id 컬럼 추가
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS user_id UUID;

-- 2. company_name_en 컬럼 추가 (영문 회사명)
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS company_name_en VARCHAR(100);

-- 3. user_id 외래키 제약 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_customers_user_id'
    ) THEN
        ALTER TABLE customers
        ADD CONSTRAINT fk_customers_user_id
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    END IF;
END $$;

-- 4. user_id 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);

-- 5. company_name_en 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_customers_company_name_en ON customers(company_name_en);

-- 6. 기존 데이터 마이그레이션 가이드 (주석)
-- 기존 customers 데이터가 있다면:
-- 1) users 테이블에 해당 email로 레코드 생성
-- 2) customers.user_id를 users.user_id로 업데이트
--
-- 예시:
-- INSERT INTO users (user_id, email, role, name, created_at)
-- SELECT
--     gen_random_uuid(),  -- 새 UUID 생성
--     email,
--     'customer',
--     (SELECT split_part(ceo_name, ' ', 1)),  -- 대표자명에서 성 추출
--     created_at
-- FROM customers
-- WHERE NOT EXISTS (
--     SELECT 1 FROM users WHERE users.email = customers.email
-- );
--
-- UPDATE customers c
-- SET user_id = u.user_id
-- FROM users u
-- WHERE c.email = u.email AND c.user_id IS NULL;

-- 7. 향후 user_id를 NOT NULL로 변경 (데이터 마이그레이션 후)
-- ALTER TABLE customers ALTER COLUMN user_id SET NOT NULL;

COMMENT ON COLUMN customers.user_id IS 'users 테이블과 연결하는 외래키';
COMMENT ON COLUMN customers.company_name_en IS '영문 회사명 (평가 신청 시 필요)';
