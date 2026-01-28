ALTER TABLE deals ADD COLUMN IF NOT EXISTS number INTEGER;

WITH numbered_deals AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
    FROM deals
)
UPDATE deals SET number = numbered_deals.row_num
FROM numbered_deals WHERE deals.id = numbered_deals.id;

SELECT COUNT(*), MIN(number), MAX(number) FROM deals WHERE number IS NOT NULL;
