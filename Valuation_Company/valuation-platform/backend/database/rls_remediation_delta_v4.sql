-- ============================================================
-- RLS Remediation Delta v4 (2026-06-15)
-- 종합 보안평가 후속: 서브에이전트 감사에서 발견된 2건 보정
--   [C3-HIGH] users_insert_signup: 임의 user_id 삽입(타인 사칭) 차단
--   [H1-MED ] accountants_select_public: 공개 범위를 배정가능 회계사로 축소
-- 비파괴(정책 교체만, 데이터 변경 없음). 하단 롤백 포함.
-- 적용: Supabase Dashboard > SQL Editor 에 붙여넣고 Run.
-- ============================================================

-- ── [C3] users INSERT: 본인(auth.uid()) 행만, 허용 역할만 ──
-- 이메일 확인 ON 환경에서 프로필 INSERT는 "최초 로그인"(세션 존재) 시 일어나므로
-- auth.uid() 가 항상 세팅됨 → 정상 가입 흐름 영향 없음.
DROP POLICY IF EXISTS "users_insert_signup" ON users;
CREATE POLICY "users_insert_signup" ON users
    FOR INSERT WITH CHECK (
        user_id = auth.uid()
        AND role IN ('customer', 'investor', 'partner', 'supporter')
    );
-- users_insert_admin (admin 임의 생성)은 v2 그대로 유지.

-- ── [H1] accountants 공개 조회: 배정가능(is_available) 회계사로 범위 축소 ──
-- 공개 디렉터리 성격은 유지하되, 비활성/비공개 회계사 행 노출을 줄인다.
-- (RLS는 행 단위이므로 컬럼 제한은 별도 GRANT 검토 — 프론트 호환 위해 본 델타에선 컬럼 유지)
DROP POLICY IF EXISTS "accountants_select_public" ON accountants;
CREATE POLICY "accountants_select_public" ON accountants
    FOR SELECT USING (is_available = true);

-- ============================================================
-- 롤백 (이전 v3 상태로 복원하려면 아래 실행)
-- ============================================================
-- DROP POLICY IF EXISTS "users_insert_signup" ON users;
-- CREATE POLICY "users_insert_signup" ON users
--     FOR INSERT WITH CHECK (role IN ('customer','investor','partner','supporter'));
-- DROP POLICY IF EXISTS "accountants_select_public" ON accountants;
-- CREATE POLICY "accountants_select_public" ON accountants
--     FOR SELECT USING (true);
