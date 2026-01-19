"""
뉴스 수집 실행 스크립트
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.weekly_collector import run_weekly_collection


async def main():
    print("=" * 50)
    print("스타트업 투자 뉴스 수집 시작")
    print("=" * 50)

    try:
        result = await run_weekly_collection(
            sources=None,  # 모든 소스 (naver, platum)
            max_pages=5    # 최근 5페이지
        )

        print("\n수집 완료!")
        print("-" * 50)
        print(f"크롤링한 뉴스: {result['news_crawled']}개")
        print(f"저장한 뉴스: {result['news_saved']}개")
        print(f"발견한 기업: {result['companies_found']}개")
        print(f"신규 기업: {result['new_companies']}개")

        if result['errors']:
            print(f"\n에러: {len(result['errors'])}개")
            for err in result['errors'][:5]:
                print(f"  - {err}")

    except Exception as e:
        print(f"\n수집 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
