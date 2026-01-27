-- 모의 프로젝트 데이터 삽입
-- 고객: FinderWorld (customer_id: C202601)
-- 각 평가방법별로 프로젝트 1개씩 (총 5개)
-- 프로젝트 ID 형식: {5자리 회사코드}-{YYMMDDHHmm}-{2자리 평가법코드}

-- 1. DCF 평가법 (DC)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270530-DC', 'C202601', 'TechStartup Co.', 'dcf', 'in_progress', 4);

-- 2. 상대가치평가법 (RV)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270531-RV', 'C202601', 'InnoVenture Ltd.', 'relative', 'in_progress', 4);

-- 3. 본질가치평가법 (IV)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270532-IV', 'C202601', 'GrowthHub Inc.', 'intrinsic', 'in_progress', 4);

-- 4. 자산가치평가법 (AV)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270533-AV', 'C202601', 'AssetTech Corp.', 'asset', 'in_progress', 4);

-- 5. 상증세법 (TX)
INSERT INTO projects (project_id, customer_id, company_name, valuation_method, status, current_step)
VALUES ('FINDE-2601270534-TX', 'C202601', 'FamilyBiz Ltd.', 'inheritance_tax', 'in_progress', 4);
