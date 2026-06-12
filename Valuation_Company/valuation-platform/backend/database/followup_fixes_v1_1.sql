-- ============================================================
-- 백호 후속과제 v1.1 — security 에이전트 권고 반영 (2026-06-12)
-- 선행: followup_fixes_v1.sql (실행 완료, 신규 9/9 + 회귀 28/28 PASS)
--
-- [M-1] 동일 user_id로 customers 복수 행 생성 가능 → 부분 UNIQUE 인덱스
--       (기존 데이터는 user_id NULL이라 충돌 없음)
-- [M-3] rate limit 트리거 TOCTOU(동시 요청 시 제한 초과) + 매 INSERT마다
--       전체 테이블 DELETE 정리 부하 → advisory lock 직렬화 + 정리 경량화
-- [M-2] NULL IP 통과(내부 service_role/SQL 에디터 경로)는 의도된 동작으로
--       위험 수용 유지 — service_role은 어차피 RLS 자체를 우회함
-- [L-1] customer_id 해시 충돌은 이론적 수준 → 스키마 개편 시 UUID 전환 예정
-- ============================================================

-- [M-1] 한 계정(user_id)당 customers 행 1개로 제한
CREATE UNIQUE INDEX IF NOT EXISTS uq_customers_user_id
    ON customers(user_id) WHERE user_id IS NOT NULL;

-- [M-3] 트리거 함수 개선: 동일 IP 동시 요청 직렬화 + 정리 경량화
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

    -- 헤더 없는 실행(SQL 에디터/service_role 내부 작업)은 제한하지 않음
    -- (service_role은 RLS 자체를 우회하므로 이 경로는 신뢰 영역 — M-2 위험 수용)
    IF client_ip IS NULL OR client_ip = '' THEN
        RETURN NEW;
    END IF;

    -- [M-3] 동일 IP의 동시 요청을 트랜잭션 단위로 직렬화 (TOCTOU 차단)
    PERFORM pg_advisory_xact_lock(hashtext('newsletter_rl_' || client_ip));

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

    -- [M-3] 정리 경량화: 본인 IP의 오래된 기록만 정리(인덱스 범위, 소량)
    --       + 2% 확률로만 전체 정리 (매 INSERT 전체 DELETE 부하 제거)
    DELETE FROM newsletter_subscribe_attempts
    WHERE ip = client_ip AND attempted_at < NOW() - INTERVAL '24 hours';

    IF random() < 0.02 THEN
        DELETE FROM newsletter_subscribe_attempts
        WHERE attempted_at < NOW() - INTERVAL '24 hours';
    END IF;

    RETURN NEW;
END;
$$;

REVOKE EXECUTE ON FUNCTION public.newsletter_rate_limit() FROM anon, authenticated, public;

-- ============================================================
-- [롤백] v1 직후 상태로 복구
-- ============================================================
-- DROP INDEX IF EXISTS uq_customers_user_id;
-- (트리거 함수는 followup_fixes_v1.sql의 정의를 재실행하면 원복)
