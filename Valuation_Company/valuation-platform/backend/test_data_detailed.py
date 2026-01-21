"""
Supabase 데이터 상세 테스트
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def test_data_detailed():
    """각 평가법별 데이터 상세 확인"""

    print("\n" + "=" * 80)
    print("SUPABASE 데이터 상세 테스트")
    print("=" * 80)

    # 1. 전체 프로젝트 확인
    print("\n[1] 전체 프로젝트 확인")
    print("-" * 80)

    projects = supabase.table("projects").select("*").execute()
    print(f"총 프로젝트 수: {len(projects.data)}건")

    # 2. 각 평가법별 확인
    methods = {
        "dcf": "DCF평가법",
        "relative": "상대가치평가법",
        "capital_market_law": "본질가치평가법",
        "asset": "자산가치평가법",
        "inheritance_tax_law": "상증세법평가법"
    }

    print("\n[2] 평가법별 분류")
    print("-" * 80)

    for method_code, method_name in methods.items():
        results = supabase.table("valuation_results")\
            .select("project_id, method, enterprise_value, value_per_share")\
            .eq("method", method_code)\
            .execute()

        print(f"\n{method_name}: {len(results.data)}건")

        for idx, result in enumerate(results.data, 1):
            ev = result['enterprise_value']
            vps = result['value_per_share']

            # 금액 포맷팅
            if ev >= 1_000_000_000_000:
                ev_str = f"{ev/1_000_000_000_000:.1f}조"
            elif ev >= 100_000_000:
                ev_str = f"{ev/100_000_000:.0f}억"
            else:
                ev_str = f"{ev:,}원"

            print(f"  [{idx}] {result['project_id'][:20]:20s} | 기업가치: {ev_str:>10s} | 주당: {vps:>10,}원")

    # 3. 실제 검증 사례 확인
    print("\n[3] 실제 검증 사례 확인")
    print("-" * 80)

    verified_cases = [
        "DCF-ENKINOAI-001",
        "REL-SAMSUNG-001",
        "CML-KAKAO-001",
        "NAV-CLASSYS-001",
        "ITL-CASE-001"
    ]

    for project_id in verified_cases:
        project = supabase.table("projects")\
            .select("*, valuation_results(*)")\
            .eq("project_id", project_id)\
            .execute()

        if project.data:
            p = project.data[0]
            r = p['valuation_results'][0] if p['valuation_results'] else None

            if r:
                ev = r['enterprise_value']
                if ev >= 1_000_000_000_000:
                    ev_str = f"{ev/1_000_000_000_000:.1f}조"
                elif ev >= 100_000_000:
                    ev_str = f"{ev/100_000_000:.0f}억"
                else:
                    ev_str = f"{ev:,}원"

                print(f"✅ {p['company_name_kr']:20s} | {ev_str:>10s} | {r['value_per_share']:>10,}원")
        else:
            print(f"❌ {project_id} - 데이터 없음")

    # 4. calculation_details 샘플 확인
    print("\n[4] calculation_details 샘플 확인 (DCF)")
    print("-" * 80)

    dcf_result = supabase.table("valuation_results")\
        .select("project_id, calculation_details")\
        .eq("method", "dcf")\
        .limit(1)\
        .execute()

    if dcf_result.data:
        details = dcf_result.data[0]['calculation_details']
        print(f"Project: {dcf_result.data[0]['project_id']}")
        print(f"Details Keys: {list(details.keys())}")
        print(f"WACC: {details.get('wacc', 'N/A')}")
        print(f"Growth Rate: {details.get('growth_rate', 'N/A')}")
        print(f"Terminal Value: {details.get('terminal_value', 'N/A'):,}")

    # 5. 상태별 통계
    print("\n[5] 상태별 통계")
    print("-" * 80)

    statuses = {}
    for p in projects.data:
        status = p['status']
        statuses[status] = statuses.get(status, 0) + 1

    for status, count in statuses.items():
        print(f"  {status:15s}: {count}건")

    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80)

if __name__ == "__main__":
    test_data_detailed()
