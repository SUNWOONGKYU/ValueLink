-- ============================================================
-- 백호 작전 후속과제 v1 — 2026-06-12
-- 선행: rls_remediation_delta_v3.sql (실행 완료, 28/28 검증 PASS)
--
-- [과제 1] newsletter_subscribers anon INSERT 무제한 (v3에서 위험 수용,
--          후속 과제로 기록) → DB 트리거 기반 IP rate limiting 적용
--          (프론트엔드 단독 제한은 우회 가능 → DB 레벨이 단일 방어선)
--
-- [과제 2] 고객 가입 시 회사 추가정보 저장 실패 (register.html → customers)
--          실DB 스키마 불일치 4건 + RLS 차단 1건:
--          ① user_id 컬럼 없음 (alter_customers_table.sql 미적용)
--          ② company_name_en 컬럼 없음
--          ③ customer_id PK(VARCHAR 20) DEFAULT 없음 → INSERT 실패
--          ④ email NOT NULL인데 register.html이 미전송 (프론트 수정으로 해결)
--          ⑤ v3에서 customers INSERT admin 전용 → 가입자 본인 INSERT 차단
--             → '본인 행(user_id = auth.uid()) + customer 역할'만 허용하는
--               정책 추가 (admin 전용 정책은 유지, OR 결합)
-- ============================================================


-- ============================================================
-- [과제 2-①②] customers 스키마 보강 (비파괴: ADD COLUMN만)
-- ============================================================
ALTER TABLE customers ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS company_name_en VARCHAR(100);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_customers_user_id'
    ) THEN
        ALTER TABLE customers
        ADD CONSTRAINT fk_customers_user_id
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);

COMMENT ON COLUMN customers.user_id IS 'users 테이블과 연결하는 외래키 (가입자 본인 식별)';
COMMENT ON COLUMN customers.company_name_en IS '영문 회사명 (평가 신청 시 필요)';


-- ============================================================
-- [과제 2-③] customer_id DEFAULT 부여 (비파괴: DEFAULT 추가만)
-- 형식: 'C' + 13자리 hex = 14자 (VARCHAR(20) 내)
-- ============================================================
ALTER TABLE customers
    ALTER COLUMN customer_id
    SET DEFAULT 'C' || upper(substr(md5(random()::text || clock_timestamp()::text), 1, 13));


-- ============================================================
-- [과제 2-⑤] customers — 가입자 본인 행 INSERT 허용
-- (customers_insert_admin은 유지 — Postgres RLS는 정책 간 OR 결합)
-- 본인(user_id = auth.uid()) + users.role = 'customer'일 때만 허용
-- → 타사 행 생성 불가, 회계사/투자자 등 타 역할 생성 불가
-- ============================================================
DROP POLICY IF EXISTS "customers_insert_own" ON customers;
CREATE POLICY "customers_insert_own" ON customers
    FOR INSERT WITH CHECK (
        user_id = auth.uid()
        AND public.get_my_role() = 'customer'
    );


-- ============================================================
-- [과제 1] newsletter_subscribers — IP 기반 rate limiting
-- 정책: 동일 IP가 1시간 내 5회 초과 구독 시도 시 차단
-- PostgREST의 request.headers에서 IP 추출 (헤더 없는 내부 실행은 통과)
-- ============================================================

-- 시도 기록 테이블 (RLS 활성 + 정책 없음 → API로 직접 접근 불가,
-- SECURITY DEFINER 트리거 함수만 기록/조회)
CREATE TABLE IF NOT EXISTS newsletter_subscribe_attempts (
    id BIGSERIAL PRIMARY KEY,
    ip TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE newsletter_subscribe_attempts ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_nsa_ip_time
    ON newsletter_subscribe_attempts(ip, attempted_at);

CREATE OR REPLACE FUNCTION public.newsletter_rate_limit()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    client_ip TEXT;
    recent_count INT;
BEGIN
    -- PostgREST 요청 헤더에서 클라이언트 IP 추출
    BEGIN
        client_ip := COALESCE(
            current_setting('request.headers', true)::json->>'x-real-ip',
            NULLIF(split_part(
                COALESCE(current_setting('request.headers', true)::json->>'x-forwarded-for', ''),
                ',', 1), '')
        );
    EXCEPTION WHEN OTHERS THEN
        client_ip := NULL;
    END;

    -- 헤더 없는 실행(SQL 에디터/서비스롤 내부 작업)은 제한하지 않음
    IF client_ip IS NULL OR client_ip = '' THEN
        RETURN NEW;
    END IF;

    SELECT COUNT(*) INTO recent_count
    FROM newsletter_subscribe_attempts
    WHERE ip = client_ip
      AND attempted_at > NOW() - INTERVAL '1 hour';

    IF recent_count >= 5 THEN
        RAISE EXCEPTION 'rate_limit_exceeded'
            USING HINT = '구독 시도가 너무 잦습니다. 1시간 후 다시 시도해주세요.',
                  ERRCODE = 'P0001';
    END IF;

    INSERT INTO newsletter_subscribe_attempts (ip) VALUES (client_ip);

    -- 24시간 지난 기록 정리 (테이블 비대화 방지)
    DELETE FROM newsletter_subscribe_attempts
    WHERE attempted_at < NOW() - INTERVAL '24 hours';

    RETURN NEW;
END;
$$;

-- anon이 함수를 직접 호출하지 못하도록 차단 (트리거 경유만 허용)
REVOKE EXECUTE ON FUNCTION public.newsletter_rate_limit() FROM anon, authenticated, public;

DROP TRIGGER IF EXISTS trg_newsletter_rate_limit ON newsletter_subscribers;
CREATE TRIGGER trg_newsletter_rate_limit
    BEFORE INSERT ON newsletter_subscribers
    FOR EACH ROW EXECUTE FUNCTION public.newsletter_rate_limit();


-- ============================================================
-- [롤백] 문제 발생 시 아래 실행으로 v3 직후 상태로 복구 (데이터 무손실)
-- ============================================================
-- -- 과제 1 롤백
-- DROP TRIGGER IF EXISTS trg_newsletter_rate_limit ON newsletter_subscribers;
-- DROP FUNCTION IF EXISTS public.newsletter_rate_limit();
-- DROP TABLE IF EXISTS newsletter_subscribe_attempts;
--
-- -- 과제 2 롤백 (컬럼은 데이터 보존 위해 유지 권장, 정책/DEFAULT만 제거)
-- DROP POLICY IF EXISTS "customers_insert_own" ON customers;
-- ALTER TABLE customers ALTER COLUMN customer_id DROP DEFAULT;
-- -- (완전 롤백이 꼭 필요하면: ALTER TABLE customers DROP CONSTRAINT fk_customers_user_id;
-- --  ALTER TABLE customers DROP COLUMN user_id; ALTER TABLE customers DROP COLUMN company_name_en;)
