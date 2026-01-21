"""
Supabase 데이터 확인 스크립트
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase 클라이언트 생성
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def check_data():
    """Supabase 데이터 확인"""

    print("\n" + "=" * 70)
    print("[INFO] Supabase 데이터 확인")
    print("=" * 70)

    try:
        # 1. Projects 테이블 확인
        print("\n[1] Projects 테이블 확인...")
        projects = supabase.table("projects").select("*").execute()
        print(f"   총 프로젝트 수: {len(projects.data)}건")

        if len(projects.data) > 0:
            print(f"\n   최근 프로젝트 3건:")
            for i, project in enumerate(projects.data[:3], 1):
                print(f"   [{i}] {project['company_name_kr']} | {project['project_id']}")

        # 2. Valuation Results 테이블 확인
        print("\n[2] Valuation Results 테이블 확인...")
        results = supabase.table("valuation_results").select("*").execute()
        print(f"   총 평가 결과 수: {len(results.data)}건")

        # 평가법별 통계
        if len(results.data) > 0:
            methods = {}
            for result in results.data:
                method = result['method']
                methods[method] = methods.get(method, 0) + 1

            print(f"\n   평가법별 분포:")
            method_names = {
                "dcf": "DCF평가법",
                "relative": "상대가치평가법",
                "capital_market_law": "본질가치평가법",
                "asset": "자산가치평가법",
                "inheritance_tax_law": "상증세법평가법"
            }

            for method, count in methods.items():
                name = method_names.get(method, method)
                print(f"   - {name}: {count}건")

        print("\n" + "=" * 70)
        print("[SUCCESS] 데이터 확인 완료!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] 데이터 확인 실패: {e}")
        return False

if __name__ == "__main__":
    check_data()
