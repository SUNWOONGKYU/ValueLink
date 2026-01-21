"""
API 통합 테스트 (Backend → Supabase)
Frontend에서 사용할 API 엔드포인트를 Python으로 테스트
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

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add(self, name, passed, details=None):
        self.tests.append({
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "details": details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        for test in self.tests:
            status_icon = "[OK]" if test["status"] == "PASS" else "[FAIL]"
            print(f"  {status_icon} {test['name']:50s} [{test['status']}]")
            if test["details"]:
                print(f"     -> {test['details']}")
        print("\n" + "-" * 80)
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"  Passed: {self.passed}/{total} ({success_rate:.1f}%)")
        print("=" * 80)

def test_all():
    results = TestResults()

    print("\n" + "=" * 80)
    print("API INTEGRATION TESTS")
    print("=" * 80)

    # Test 1: 연결 테스트
    print("\n[TEST 1] Supabase 연결 테스트...")
    try:
        response = supabase.table("projects").select("count").execute()
        results.add("Supabase 연결", True, "연결 성공")
    except Exception as e:
        results.add("Supabase 연결", False, str(e))

    # Test 2: 전체 프로젝트 조회
    print("[TEST 2] 전체 프로젝트 조회...")
    try:
        response = supabase.table("projects").select("*").execute()
        count = len(response.data)
        expected = 25
        passed = count == expected
        results.add("전체 프로젝트 조회", passed, f"{count}건 (예상: {expected}건)")
    except Exception as e:
        results.add("전체 프로젝트 조회", False, str(e))

    # Test 3: Projects + Valuation Results JOIN
    print("[TEST 3] JOIN 조회 테스트...")
    try:
        response = supabase.table("projects")\
            .select("*, valuation_results(*)")\
            .limit(5)\
            .execute()

        has_join_data = all(p.get('valuation_results') for p in response.data)
        results.add("JOIN 조회", has_join_data, f"{len(response.data)}건 조회됨")
    except Exception as e:
        results.add("JOIN 조회", False, str(e))

    # Test 4: 평가법별 필터링
    print("[TEST 4] 평가법별 필터링...")
    methods = {
        "dcf": "DCF평가법",
        "relative": "상대가치평가법",
        "capital_market_law": "본질가치평가법",
        "asset": "자산가치평가법",
        "inheritance_tax_law": "상증세법평가법"
    }

    all_correct = True
    for method_code, method_name in methods.items():
        try:
            response = supabase.table("valuation_results")\
                .select("project_id")\
                .eq("method", method_code)\
                .execute()

            count = len(response.data)
            expected = 5
            if count != expected:
                all_correct = False
                results.add(f"필터: {method_name}", False, f"{count}건 (예상: {expected}건)")
            else:
                print(f"  [OK] {method_name}: {count}")
        except Exception as e:
            all_correct = False
            results.add(f"필터: {method_name}", False, str(e))

    if all_correct:
        results.add("평가법별 필터링", True, "모든 평가법이 5건씩")

    # Test 5: 실제 검증 사례 확인
    print("[TEST 5] 실제 검증 사례 확인...")
    verified_cases = {
        "DCF-ENKINOAI-001": ("엔키노에이아이", 2140),
        "REL-SAMSUNG-001": ("삼성전자", 97700),
        "CML-KAKAO-001": ("카카오", 113429),
        "NAV-CLASSYS-001": ("클래시스", 52774),
        "ITL-CASE-001": ("비상장법인", 110000)  # 실제 이름: "비상장법인(조심2022중6580)"
    }

    verified_count = 0
    for project_id, (expected_name, expected_vps) in verified_cases.items():
        try:
            response = supabase.table("projects")\
                .select("company_name_kr, valuation_results(value_per_share)")\
                .eq("project_id", project_id)\
                .execute()

            if response.data:
                data = response.data[0]
                actual_name = data['company_name_kr']
                actual_vps = data['valuation_results'][0]['value_per_share']

                name_match = expected_name in actual_name
                vps_match = actual_vps == expected_vps

                if name_match and vps_match:
                    verified_count += 1
                    print(f"  [OK] {expected_name}: {actual_vps:,}")
                else:
                    print(f"  [FAIL] {expected_name}: mismatch")
        except Exception as e:
            print(f"  [FAIL] {project_id}: {e}")

    results.add("실제 검증 사례", verified_count == 5, f"{verified_count}/5 확인됨")

    # Test 6: 상태별 통계
    print("[TEST 6] 상태별 통계...")
    try:
        response = supabase.table("projects").select("status").execute()
        statuses = {}
        for p in response.data:
            status = p['status']
            statuses[status] = statuses.get(status, 0) + 1

        print(f"  requested: {statuses.get('requested', 0)}건")
        print(f"  evaluating: {statuses.get('evaluating', 0)}건")
        print(f"  completed: {statuses.get('completed', 0)}건")

        results.add("상태별 통계", True, f"총 {len(response.data)}건 분류됨")
    except Exception as e:
        results.add("상태별 통계", False, str(e))

    # Test 7: calculation_details JSON 필드
    print("[TEST 7] calculation_details JSON 필드...")
    try:
        response = supabase.table("valuation_results")\
            .select("project_id, method, calculation_details")\
            .eq("method", "dcf")\
            .limit(1)\
            .execute()

        if response.data:
            details = response.data[0]['calculation_details']
            has_wacc = 'wacc' in details
            has_growth = 'growth_rate' in details

            passed = has_wacc and has_growth
            results.add("JSON 필드 구조", passed, f"WACC: {has_wacc}, Growth: {has_growth}")
    except Exception as e:
        results.add("JSON 필드 구조", False, str(e))

    # Test 8: 정렬 테스트 (최신순)
    print("[TEST 8] 정렬 테스트...")
    try:
        response = supabase.table("projects")\
            .select("project_id, created_at")\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()

        # 날짜가 내림차순인지 확인
        dates = [p['created_at'] for p in response.data]
        is_sorted = dates == sorted(dates, reverse=True)

        results.add("정렬 (최신순)", is_sorted, f"{len(dates)}건 정렬 확인")
    except Exception as e:
        results.add("정렬 (최신순)", False, str(e))

    # 요약 출력
    results.print_summary()

    return results

if __name__ == "__main__":
    test_all()
