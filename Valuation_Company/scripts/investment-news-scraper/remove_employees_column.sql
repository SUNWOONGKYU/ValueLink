-- Deal 테이블에서 employees 컬럼 삭제
-- 이유: 직원 수는 파악하기 어려워 실용성이 낮음

ALTER TABLE deals DROP COLUMN IF EXISTS employees;
