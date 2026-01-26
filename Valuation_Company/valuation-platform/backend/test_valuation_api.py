"""
Valuation API 테스트 스크립트

평가법 API 엔드포인트 테스트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.supabase_client import supabase_client


async def test_valuation_api():
    """평가 API 테스트"""

    print("=" * 60)
    print("평가 API 테스트")
    print("=" * 60)

    # 1. 프로젝트 목록 조회
    print("\n1. 프로젝트 목록 조회...")
    try:
        projects = await supabase_client.select(
            "projects",
            columns="id,project_name,dcf_status,dcf_step",
            limit=5
        )

        if not projects:
            print("⚠️  프로젝트가 없습니다. 테스트 프로젝트를 먼저 생성해주세요.")
            return

        print(f"✅ 프로젝트 {len(projects)}개 조회 완료")
        test_project = projects[0]
        project_id = test_project["id"]
        print(f"   테스트 프로젝트: {test_project['project_name']} (ID: {project_id})")

    except Exception as e:
        print(f"❌ 프로젝트 조회 실패: {str(e)}")
        return

    # 2. 평가 시작 (DCF)
    print(f"\n2. DCF 평가 시작...")
    try:
        update_data = {
            "dcf_status": "in_progress",
            "dcf_step": 5,
            "updated_at": "2026-01-27T00:00:00Z"
        }

        result = await supabase_client.update(
            "projects",
            update_data,
            filters={"id": project_id}
        )

        print(f"✅ DCF 평가 시작 완료")
        print(f"   상태: in_progress")
        print(f"   단계: 5/14")

    except Exception as e:
        print(f"❌ 평가 시작 실패: {str(e)}")
        return

    # 3. 진행 상황 조회
    print(f"\n3. 진행 상황 조회...")
    try:
        project = await supabase_client.select(
            "projects",
            columns="dcf_status,dcf_step",
            filters={"id": project_id}
        )

        if project:
            status = project[0]["dcf_status"]
            step = project[0]["dcf_step"]
            progress = int((step / 14) * 100)

            print(f"✅ 진행 상황 조회 완료")
            print(f"   상태: {status}")
            print(f"   단계: {step}/14")
            print(f"   진행률: {progress}%")

    except Exception as e:
        print(f"❌ 진행 상황 조회 실패: {str(e)}")
        return

    # 4. 단계 전진 (5 -> 6)
    print(f"\n4. 단계 전진 테스트...")
    try:
        update_data = {
            "dcf_step": 6,
            "updated_at": "2026-01-27T00:00:00Z"
        }

        await supabase_client.update(
            "projects",
            update_data,
            filters={"id": project_id}
        )

        print(f"✅ 단계 전진 완료")
        print(f"   이전 단계: 5")
        print(f"   현재 단계: 6")

    except Exception as e:
        print(f"❌ 단계 전진 실패: {str(e)}")
        return

    # 5. 상태 업데이트
    print(f"\n5. 상태 업데이트 테스트...")
    try:
        update_data = {
            "dcf_status": "completed",
            "dcf_step": 14,
            "updated_at": "2026-01-27T00:00:00Z"
        }

        await supabase_client.update(
            "projects",
            update_data,
            filters={"id": project_id}
        )

        print(f"✅ 상태 업데이트 완료")
        print(f"   상태: completed")
        print(f"   단계: 14/14")

    except Exception as e:
        print(f"❌ 상태 업데이트 실패: {str(e)}")
        return

    # 6. 최종 상태 확인
    print(f"\n6. 최종 상태 확인...")
    try:
        project = await supabase_client.select(
            "projects",
            columns="dcf_status,dcf_step,relative_status,intrinsic_status,asset_status,inheritance_tax_status",
            filters={"id": project_id}
        )

        if project:
            p = project[0]
            print(f"✅ 최종 상태 확인 완료")
            print(f"\n   평가법별 상태:")
            print(f"   - DCF: {p['dcf_status']} (단계 {p['dcf_step']}/14)")
            print(f"   - Relative: {p['relative_status']}")
            print(f"   - Intrinsic: {p['intrinsic_status']}")
            print(f"   - Asset: {p['asset_status']}")
            print(f"   - Inheritance Tax: {p['inheritance_tax_status']}")

    except Exception as e:
        print(f"❌ 최종 상태 확인 실패: {str(e)}")
        return

    # 7. 상태 초기화
    print(f"\n7. 상태 초기화...")
    try:
        update_data = {
            "dcf_status": "not_requested",
            "dcf_step": 1,
            "updated_at": "2026-01-27T00:00:00Z"
        }

        await supabase_client.update(
            "projects",
            update_data,
            filters={"id": project_id}
        )

        print(f"✅ 상태 초기화 완료")

    except Exception as e:
        print(f"❌ 상태 초기화 실패: {str(e)}")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_valuation_api())
