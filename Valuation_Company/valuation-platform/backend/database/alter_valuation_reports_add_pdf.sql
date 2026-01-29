-- valuation_reports 테이블에 필드 추가
-- 평가 기준일 및 PDF 보고서 경로

ALTER TABLE valuation_reports 
ADD COLUMN IF NOT EXISTS evaluation_date DATE,
ADD COLUMN IF NOT EXISTS report_pdf_path VARCHAR(500);

-- 설명: 
-- evaluation_date: 평가보고서상의 평가 기준일 (예: 2023-12-31)
-- report_pdf_path: 저장된 PDF 파일의 상대 경로 (예: /reports/dcf/Kakao_DCF_20231231.pdf)
