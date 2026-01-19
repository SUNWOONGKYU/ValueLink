"""
Weekly Collection Task
주간 수집 작업 태스크

@task Investment Tracker
@description 수동/자동 주간 수집 트리거
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List

from app.services.weekly_collector import run_weekly_collection

logger = logging.getLogger(__name__)


async def trigger_manual_collection(
    sources: Optional[List[str]] = None,
    max_pages: int = 3
) -> Dict[str, Any]:
    """
    수동 수집 실행

    Args:
        sources: 수집할 소스 목록 (None이면 전체)
        max_pages: 크롤링 최대 페이지 수

    Returns:
        수집 결과 통계
    """
    logger.info(f"Manual collection triggered with sources={sources}, max_pages={max_pages}")

    try:
        result = await run_weekly_collection(
            sources=sources,
            max_pages=max_pages
        )
        logger.info(f"Manual collection completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Manual collection failed: {e}")
        raise


def run_collection_sync(
    sources: Optional[List[str]] = None,
    max_pages: int = 3
) -> Dict[str, Any]:
    """
    동기 방식 수집 실행 (CLI 등에서 사용)

    Args:
        sources: 수집할 소스 목록
        max_pages: 크롤링 최대 페이지 수

    Returns:
        수집 결과 통계
    """
    return asyncio.run(trigger_manual_collection(sources, max_pages))


if __name__ == "__main__":
    # CLI에서 직접 실행
    import sys

    sources = None
    max_pages = 3

    if len(sys.argv) > 1:
        sources = sys.argv[1].split(",")
    if len(sys.argv) > 2:
        max_pages = int(sys.argv[2])

    result = run_collection_sync(sources, max_pages)
    print(f"Collection result: {result}")
