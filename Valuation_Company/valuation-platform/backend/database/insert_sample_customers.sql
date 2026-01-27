-- 모의 고객사 데이터 삽입
-- FinderWorld 고객사 (마이페이지 모든 필드 포함)

INSERT INTO customers (
    customer_id,
    email,
    company_name,
    ceo_name,
    industry,
    founded_date,
    business_number,
    employees,
    company_website,
    address,
    phone,
    fax
)
VALUES (
    'C202601',
    'admin@finderworld.com',
    'FinderWorld',
    '김대표',
    '소프트웨어 개발',
    '2020-01-15',
    '123-45-67890',
    50,
    'https://www.finderworld.com',
    '서울특별시 강남구 테헤란로 123',
    '02-1234-5678',
    '02-1234-5679'
);
