"""
Supabase를 통한 모의 데이터 삽입

5가지 평가법별로 5건씩 (총 25건)
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

def insert_mock_data():
    """5가지 평가법별로 모의 데이터 5건씩 삽입"""

    # 5가지 평가법 (순서 고정)
    methods = [
        ("dcf", "DCF평가법"),
        ("relative", "상대가치평가법"),
        ("capital_market_law", "본질가치평가법"),
        ("asset", "자산가치평가법"),
        ("inheritance_tax_law", "상증세법평가법")
    ]

    companies = [
        "테크스타트업 A", "바이오텍 B", "핀테크 C", "이커머스 D", "게임테크 E",
        "AI플랫폼 F", "헬스케어 G", "모빌리티 H", "에듀테크 I", "푸드테크 J",
        "클라우드 K", "블록체인 L", "로보틱스 M", "SaaS N", "마켓플레이스 O",
        "패션테크 P", "프롭테크 Q", "애그테크 R", "스포츠테크 S", "미디어테크 T",
        "뷰티테크 U", "펫테크 V", "여행테크 W", "물류테크 X", "HR테크 Y"
    ]

    purposes = ["MA", "IPO", "investment", "merger", "inheritance"]

    print("\n" + "=" * 70)
    print("[INFO] 모의 데이터 삽입 시작")
    print("=" * 70)

    total_projects = 0
    total_results = 0

    # 각 평가법별로 5건씩
    for method_idx, (method_code, method_name) in enumerate(methods):
        print(f"\n[{method_idx + 1}/5] {method_name} ({method_code}) - 5건 삽입 중...")
        print("-" * 70)

        for i in range(5):
            project_idx = method_idx * 5 + i
            company_name = companies[project_idx]

            # Project ID 생성 (고유성 보장)
            timestamp = datetime.now().strftime("%y%m%d%H%M%S")
            project_id = f"{company_name[:3]}-{timestamp}-{chr(65 + project_idx)}"

            # 1. Project 삽입
            project_data = {
                "project_id": project_id,
                "status": random.choice(["requested", "evaluating", "completed"]),
                "company_name_kr": company_name,
                "company_name_en": f"{company_name} Inc.",
                "business_registration_number": f"110-81-{10000 + project_idx:05d}",
                "representative_name": f"대표자 {chr(65 + project_idx)}",
                "valuation_purpose": purposes[i],
                "requested_methods": [method_code],
                "target_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            try:
                supabase.table("projects").insert(project_data).execute()
                total_projects += 1
                print(f"   [OK] [{total_projects:2d}] {company_name:20s} | {project_id}")
            except Exception as e:
                print(f"   [FAIL] [{total_projects:2d}] {company_name:20s} | 실패: {e}")
                continue

            # 2. Valuation Result 삽입
            base_value = random.randint(30, 150) * 100000000  # 30억 ~ 150억

            # 평가법별 특성 반영
            if method_code == "dcf":
                details = {
                    "wacc": round(random.uniform(0.08, 0.15), 4),
                    "growth_rate": round(random.uniform(0.02, 0.05), 4),
                    "terminal_value": int(base_value * 0.6),
                    "fcf_5years": [random.randint(5, 15) * 100000000 for _ in range(5)],
                    "formula": "DCF = Σ(FCF/(1+WACC)^t) + Terminal Value"
                }
            elif method_code == "relative":
                details = {
                    "per": round(random.uniform(10, 25), 2),
                    "pbr": round(random.uniform(1.5, 5), 2),
                    "psr": round(random.uniform(2, 8), 2),
                    "comparable_companies": ["유사기업A", "유사기업B", "유사기업C"],
                    "formula": "상대가치 = PER × EPS (또는 PBR × BPS)"
                }
            elif method_code == "capital_market_law":
                details = {
                    "nav": int(base_value * 0.7),
                    "earning_value": int(base_value * 1.1),
                    "nav_weight": 0.4,
                    "earning_weight": 0.6,
                    "formula": "(NAV × 1 + 수익가치 × 1.5) ÷ 2.5"
                }
            elif method_code == "asset":
                details = {
                    "total_assets": int(base_value * 1.5),
                    "total_liabilities": int(base_value * 0.5),
                    "nav": int(base_value),
                    "adjustment_method": "book_value",
                    "formula": "NAV = 총자산 - 총부채"
                }
            else:  # inheritance_tax_law
                details = {
                    "nav": int(base_value * 0.8),
                    "earning_value": int(base_value * 0.9),
                    "weighted_value": int(base_value * 0.85),
                    "discount_rate": 0.2 if random.random() > 0.5 else 0,
                    "formula": "(NAV × 3 + 수익가치 × 2) ÷ 5"
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
                print(f"      [VALUE] 기업가치: {base_value:,}원")
            except Exception as e:
                print(f"      [FAIL] Valuation Result 삽입 실패: {e}")

    print("\n" + "=" * 70)
    print("[COMPLETE] 모의 데이터 삽입 완료!")
    print("=" * 70)
    print(f"   [INFO] 총 프로젝트: {total_projects}건")
    print(f"   [INFO] 총 평가 결과: {total_results}건")
    print(f"   [INFO] 5가지 평가법 x 5건 = 25건")
    print("=" * 70)

if __name__ == "__main__":
    insert_mock_data()
