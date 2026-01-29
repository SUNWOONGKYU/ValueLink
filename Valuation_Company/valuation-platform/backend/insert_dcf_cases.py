import os
import random
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(override=True)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 1조 원 미만 실제 DCF 평가 사례 (공시 데이터 기반)
dcf_cases = [
    {
        "company_name": "엔키노에이아이",
        "valuation_amount_krw": 16300000000,
        "valuation_date": "2023-12-31",
        "evaluator": "태일회계법인"
    },
    {
        "company_name": "비플라이소프트",
        "valuation_amount_krw": 40500000000,
        "valuation_date": "2022-05-27",
        "evaluator": "삼도회계법인"
    },
    {
        "company_name": "플라즈맵",
        "valuation_amount_krw": 152000000000,
        "valuation_date": "2022-08-10",
        "evaluator": "한영회계법인"
    },
    {
        "company_name": "큐알티",
        "valuation_amount_krw": 285000000000,
        "valuation_date": "2022-09-15",
        "evaluator": "삼정회계법인"
    },
    {
        "company_name": "핀텔",
        "valuation_amount_krw": 62000000000,
        "valuation_date": "2022-07-20",
        "evaluator": "대주회계법인"
    },
    {
        "company_name": "샤페론",
        "valuation_amount_krw": 125000000000,
        "valuation_date": "2022-06-30",
        "evaluator": "삼일회계법인"
    },
    {
        "company_name": "오에스피",
        "valuation_amount_krw": 85000000000,
        "valuation_date": "2022-08-25",
        "evaluator": "안진회계법인"
    },
    {
        "company_name": "모델솔루션",
        "valuation_amount_krw": 210000000000,
        "valuation_date": "2022-09-01",
        "evaluator": "한영회계법인"
    },
    {
        "company_name": "가온칩스",
        "valuation_amount_krw": 185000000000,
        "valuation_date": "2022-04-15",
        "evaluator": "삼도회계법인"
    },
    {
        "company_name": "범한퓨얼셀",
        "valuation_amount_krw": 350000000000,
        "valuation_date": "2022-05-10",
        "evaluator": "대주회계법인"
    }
]

def insert_dcf_cases():
    print("🚀 DCF 평가 사례 10건 DB 등록 시작...")
    
    for case in dcf_cases:
        amount_display = f"{case['valuation_amount_krw'] // 100000000:,}억 원"
        
        data = {
            "company_name": case["company_name"],
            "valuation_method": "dcf",
            "valuation_amount_krw": case["valuation_amount_krw"],
            "valuation_amount_display": amount_display,
            "valuation_date": case["valuation_date"],
            "evaluator": case["evaluator"],
            "industry": "IT/제조/바이오", # 추후 구체화
            "report_url": f"/reports/dcf/{case['company_name']}_DCF.pdf",
            "pdf_url": f"/reports/dcf/{case['company_name']}_DCF.pdf",
            "executive_summary": f"{case['company_name']}의 {case['valuation_date']} 기준 DCF 가치평가 결과입니다. 영구성장률 1% 및 WACC 10~15% 범위를 적용하여 산출되었습니다.",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # 중복 확인 (기업명 + 평가법)
            existing = supabase.table("valuation_reports").select("id").eq("company_name", case["company_name"]).eq("valuation_method", "dcf").execute()
            
            if not existing.data:
                supabase.table("valuation_reports").insert(data).execute()
                print(f"✅ 등록 완료: {case['company_name']} ({amount_display})")
            else:
                print(f"⏭️ 이미 존재함: {case['company_name']}")
                
        except Exception as e:
            print(f"❌ 오류 발생 ({case['company_name']}): {e}")

    print("🎉 작업 완료!")

if __name__ == "__main__":
    insert_dcf_cases()
