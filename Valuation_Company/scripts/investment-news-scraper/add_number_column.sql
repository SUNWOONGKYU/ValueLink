-- Deal 테이블에 number 칼럼 추가
ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;

-- 기존 레코드에 번호 할당 (created_at 순서로)
WITH numbered_deals AS (
    SELECT
        id,
        ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals
SET number = numbered_deals.row_num
FROM numbered_deals
WHERE deals.id = numbered_deals.id;

-- 확인
SELECT number, company_name, created_at
FROM deals
ORDER BY number
LIMIT 10;
