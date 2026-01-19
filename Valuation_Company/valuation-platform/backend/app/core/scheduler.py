"""
Scheduler Configuration
APScheduler를 사용한 주간 작업 스케줄링

@task Investment Tracker
@description 매주 일요일 오전 6시 자동 수집 스케줄러
"""
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.core.config import settings

logger = logging.getLogger(__name__)

# 스케줄러 인스턴스
scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """스케줄러 인스턴스 반환"""
    global scheduler

    if scheduler is None:
        # 스케줄러 설정
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': True,  # 놓친 작업 하나로 통합
            'max_instances': 1,  # 동시에 하나만 실행
            'misfire_grace_time': 3600  # 1시간 내 실행 허용
        }

        scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Seoul'
        )

    return scheduler


async def weekly_collection_job():
    """
    주간 수집 작업
    매주 일요일 오전 6시 (KST) 실행
    """
    logger.info("Starting scheduled weekly collection")

    try:
        from app.services.weekly_collector import run_weekly_collection

        result = await run_weekly_collection(
            sources=["naver", "platum"],
            max_pages=3
        )

        logger.info(f"Scheduled collection completed: {result}")

    except Exception as e:
        logger.error(f"Scheduled collection failed: {e}")
        raise


def setup_jobs(scheduler: AsyncIOScheduler) -> None:
    """스케줄 작업 등록"""

    # 주간 수집 작업 (매주 일요일 오전 6시 KST)
    scheduler.add_job(
        weekly_collection_job,
        trigger=CronTrigger(
            day_of_week='sun',  # 일요일
            hour=6,             # 오전 6시
            minute=0,
            timezone='Asia/Seoul'
        ),
        id='weekly_investment_collection',
        name='Weekly Investment News Collection',
        replace_existing=True
    )

    logger.info("Scheduled jobs registered")


def start_scheduler() -> None:
    """스케줄러 시작"""
    global scheduler

    scheduler = get_scheduler()
    setup_jobs(scheduler)

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

        # 등록된 작업 목록 로깅
        for job in scheduler.get_jobs():
            logger.info(f"Registered job: {job.name} - Next run: {job.next_run_time}")


def shutdown_scheduler() -> None:
    """스케줄러 종료"""
    global scheduler

    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown")


def get_job_status() -> dict:
    """스케줄러 및 작업 상태 조회"""
    global scheduler

    if scheduler is None:
        return {"status": "not_initialized", "jobs": []}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })

    return {
        "status": "running" if scheduler.running else "stopped",
        "jobs": jobs
    }


async def trigger_job_now(job_id: str) -> bool:
    """
    작업 즉시 실행 (테스트/수동 실행용)

    Args:
        job_id: 작업 ID

    Returns:
        실행 성공 여부
    """
    global scheduler

    if scheduler is None:
        return False

    job = scheduler.get_job(job_id)
    if job:
        # 즉시 실행
        scheduler.modify_job(job_id, next_run_time=datetime.now())
        logger.info(f"Job {job_id} triggered for immediate execution")
        return True

    return False
