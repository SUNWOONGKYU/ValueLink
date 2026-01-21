"""
실제 검증 데이터 기반 모의 데이터 삽입

5가지 평가법별로 실제 사례 데이터 사용:
1. DCF - 엔키노에이아이
2. 상대가치 - 삼성전자
3. 자본시장법 - 카카오
4. 자산가치 - 클래시스
5. 상증세법 - 조세심판 사례
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

# Supabase 클라이언트 생성
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def insert_realistic_data():
    """실제 검증 데이터 기반 모의 데이터 삽입"""

    print("\n" + "=" * 70)
    print("[INFO] 실제 사례 기반 모의 데이터 삽입 시작")
    print("=" * 70)

    # 실제 검증 사례 데이터
    realistic_cases = [
        # 1. DCF - 엔키노에이아이
        {
            "project_id": "DCF-ENKINOAI-001",
            "company_name_kr": "엔키노에이아이",
            "company_name_en": "Enkinoai Inc.",
            "valuation_purpose": "investment",
            "method": "dcf",
            "enterprise_value": 16346048693,  # 163억
            "equity_value": 15729119359,      # 157억
            "value_per_share": 2140,
            "details": {
                "wacc": 0.1381,
                "growth_rate": 0.01,
                "terminal_value": 10610977073,
                "fcf_5years": [307656633, 938459720, 2144403665, 2184583081, 2257314651],
                "pv_cumulative": 5605401153,
                "pv_terminal": 10610977073,
                "formula": "DCF = Σ(FCF/(1+WACC)^t) + Terminal Value"
            }
        },
        # 2. 상대가치 - 삼성전자
        {
            "project_id": "REL-SAMSUNG-001",
            "company_name_kr": "삼성전자",
            "company_name_en": "Samsung Electronics",
            "valuation_purpose": "MA",
            "method": "relative",
            "enterprise_value": 578348600000000,  # 578조 (시가총액)
            "equity_value": 578348600000000,
            "value_per_share": 97700,  # 2025년 1월 기준 추정
            "details": {
                "per": 19.74,
                "pbr": 1.69,
                "roe": 0.0903,
                "net_income": 34451400000000,  # 34조
                "book_value": 391687600000000,  # 391조
                "comparable_companies": ["SK하이닉스", "DB하이텍", "LG전자"],
                "formula": "시가총액 = PER × 순이익"
            }
        },
        # 3. 자본시장법 - 카카오
        {
            "project_id": "CML-KAKAO-001",
            "company_name_kr": "카카오",
            "company_name_en": "Kakao Corp.",
            "valuation_purpose": "merger",
            "method": "capital_market_law",
            "enterprise_value": 3134508000000,  # 3.1조
            "equity_value": 3134508000000,
            "value_per_share": 113429,
            "details": {
                "asset_value_per_share": 6472,
                "income_value_per_share": 184706,
                "asset_weight": 0.4,
                "income_weight": 0.6,
                "formula": "(자산가치 × 1 + 수익가치 × 1.5) ÷ 2.5"
            }
        },
        # 4. 자산가치 - 클래시스
        {
            "project_id": "NAV-CLASSYS-001",
            "company_name_kr": "클래시스",
            "company_name_en": "CLASSYS Inc.",
            "valuation_purpose": "merger",
            "method": "asset",
            "enterprise_value": 283500000000,  # 2,835억
            "equity_value": 283500000000,
            "value_per_share": 52774,
            "details": {
                "total_assets": 375400000000,
                "total_liabilities": 91900000000,
                "nav": 283500000000,
                "outstanding_shares": 5371973,
                "adjustment_method": "book_value",
                "formula": "NAV = 총자산 - 총부채"
            }
        },
        # 5. 상증세법 - 조세심판 사례
        {
            "project_id": "ITL-CASE-001",
            "company_name_kr": "비상장법인(조심2022중6580)",
            "company_name_en": "Private Company Case",
            "valuation_purpose": "inheritance",
            "method": "inheritance_tax_law",
            "enterprise_value": 495000000,  # 4.95억
            "equity_value": 495000000,
            "value_per_share": 110000,
            "details": {
                "net_income_value_per_share": 150000,
                "net_asset_value_per_share": 50000,
                "income_weight": 0.6,
                "asset_weight": 0.4,
                "weighted_value": 110000,
                "controlling_premium": 0,
                "minority_discount": 0,
                "formula": "(순손익가치 × 3 + 순자산가치 × 2) ÷ 5"
            }
        }
    ]

    total_projects = 0
    total_results = 0

    for idx, case in enumerate(realistic_cases, 1):
        method_name = {
            "dcf": "DCF평가법",
            "relative": "상대가치평가법",
            "capital_market_law": "본질가치평가법",
            "asset": "자산가치평가법",
            "inheritance_tax_law": "상증세법평가법"
        }[case["method"]]

        print(f"\n[{idx}/5] {method_name} - {case['company_name_kr']}")
        print("-" * 70)

        # 1. Project 삽입
        project_data = {
            "project_id": case["project_id"],
            "status": "completed",
            "company_name_kr": case["company_name_kr"],
            "company_name_en": case["company_name_en"],
            "business_registration_number": f"110-81-{10000 + idx:05d}",
            "representative_name": f"대표이사 {chr(65 + idx)}",
            "valuation_purpose": case["valuation_purpose"],
            "requested_methods": [case["method"]],
            "target_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
            "actual_completion_date": datetime.now().date().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        try:
            supabase.table("projects").insert(project_data).execute()
            total_projects += 1
            print(f"   [OK] Project: {case['company_name_kr']}")
        except Exception as e:
            print(f"   [FAIL] Project 삽입 실패: {e}")
            continue

        # 2. Valuation Result 삽입
        valuation_data = {
            "project_id": case["project_id"],
            "method": case["method"],
            "enterprise_value": case["enterprise_value"],
            "equity_value": case["equity_value"],
            "value_per_share": case["value_per_share"],
            "calculation_details": case["details"],
            "created_at": datetime.now().isoformat()
        }

        try:
            supabase.table("valuation_results").insert(valuation_data).execute()
            total_results += 1
            print(f"   [OK] 기업가치: {case['enterprise_value']:,}원")
            print(f"   [OK] 주당가치: {case['value_per_share']:,}원")
        except Exception as e:
            print(f"   [FAIL] Valuation Result 삽입 실패: {e}")

    # 추가 모의 데이터 (각 평가법별로 4건씩 더 추가)
    print("\n[추가] 각 평가법별 추가 모의 데이터 삽입...")
    print("-" * 70)

    methods = [
        ("dcf", "DCF평가법"),
        ("relative", "상대가치평가법"),
        ("capital_market_law", "본질가치평가법"),
        ("asset", "자산가치평가법"),
        ("inheritance_tax_law", "상증세법평가법")
    ]

    companies = [
        "테크스타트업", "바이오텍", "핀테크", "이커머스",
        "AI플랫폼", "헬스케어", "모빌리티", "에듀테크",
        "푸드테크", "클라우드", "블록체인", "로보틱스",
        "SaaS", "마켓플레이스", "패션테크", "프롭테크",
        "애그테크", "스포츠테크", "미디어테크", "뷰티테크"
    ]

    purposes = ["MA", "IPO", "investment", "merger", "inheritance"]

    for method_idx, (method_code, method_name) in enumerate(methods):
        for i in range(4):  # 각 평가법별로 4건 추가 (총 20건)
            company_idx = method_idx * 4 + i
            company_name = f"{companies[company_idx]} {chr(65 + company_idx)}"

            timestamp = datetime.now().strftime("%y%m%d%H%M%S")
            project_id = f"{method_code.upper()}-{timestamp}-{chr(65 + company_idx)}"

            # Project 삽입
            project_data = {
                "project_id": project_id,
                "status": random.choice(["requested", "evaluating", "completed"]),
                "company_name_kr": company_name,
                "company_name_en": f"{company_name} Inc.",
                "business_registration_number": f"110-81-{20000 + company_idx:05d}",
                "representative_name": f"대표 {chr(65 + company_idx)}",
                "valuation_purpose": purposes[i],
                "requested_methods": [method_code],
                "target_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            try:
                supabase.table("projects").insert(project_data).execute()
                total_projects += 1
            except Exception as e:
                continue

            # Valuation Result 삽입
            base_value = random.randint(30, 150) * 100000000

            if method_code == "dcf":
                details = {
                    "wacc": round(random.uniform(0.08, 0.15), 4),
                    "growth_rate": round(random.uniform(0.02, 0.05), 4),
                    "terminal_value": int(base_value * 0.6),
                    "fcf_5years": [random.randint(5, 15) * 100000000 for _ in range(5)]
                }
            elif method_code == "relative":
                details = {
                    "per": round(random.uniform(10, 25), 2),
                    "pbr": round(random.uniform(1.5, 5), 2),
                    "comparable_companies": ["유사기업A", "유사기업B"]
                }
            elif method_code == "capital_market_law":
                details = {
                    "asset_value_per_share": random.randint(5000, 20000),
                    "income_value_per_share": random.randint(50000, 200000),
                    "asset_weight": 0.4,
                    "income_weight": 0.6
                }
            elif method_code == "asset":
                details = {
                    "total_assets": int(base_value * 1.5),
                    "total_liabilities": int(base_value * 0.5),
                    "nav": int(base_value)
                }
            else:  # inheritance_tax_law
                details = {
                    "net_income_value_per_share": random.randint(80000, 150000),
                    "net_asset_value_per_share": random.randint(40000, 80000),
                    "income_weight": 0.6,
                    "asset_weight": 0.4
                }

            valuation_data = {
                "project_id": project_id,
                "method": method_code,
                "enterprise_value": base_value,
                "equity_value": int(base_value * random.uniform(0.85, 0.95)),
                "value_per_share": random.randint(5000, 50000),
                "calculation_details": details,
                "created_at": datetime.now().isoformat()
            }

            try:
                supabase.table("valuation_results").insert(valuation_data).execute()
                total_results += 1
            except Exception as e:
                pass

    print("\n" + "=" * 70)
    print("[COMPLETE] 실제 사례 기반 모의 데이터 삽입 완료!")
    print("=" * 70)
    print(f"   [INFO] 총 프로젝트: {total_projects}건")
    print(f"   [INFO] 총 평가 결과: {total_results}건")
    print(f"   [INFO] 실제 검증 사례: 5건 + 추가 모의: 20건 = 25건")
    print("=" * 70)

if __name__ == "__main__":
    insert_realistic_data()
