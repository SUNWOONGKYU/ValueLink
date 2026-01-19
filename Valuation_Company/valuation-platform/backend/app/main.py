import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.core.config import settings
from app.core.scheduler import start_scheduler, shutdown_scheduler, get_job_status

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # Startup
    logger.info("Starting Valuation Platform API")
    logger.info(f"Supabase URL configured: {bool(settings.SUPABASE_URL)}")

    # 스케줄러 시작
    if not settings.DEBUG:  # 프로덕션에서만 스케줄러 자동 시작
        start_scheduler()
        logger.info("Scheduler started (production mode)")
    else:
        logger.info("Scheduler not started (debug mode) - use /scheduler/start to enable")

    yield

    # Shutdown
    logger.info("Shutting down Valuation Platform API")
    shutdown_scheduler()


app = FastAPI(
    title="Valuation Platform API",
    description="기업가치평가 플랫폼 백엔드 API - AI 기반 가치평가 및 투자 트래커",
    version="0.2.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Valuation Platform API",
        "version": "0.2.0",
        "status": "running",
        "features": [
            "DCF Valuation",
            "Comparable Valuation",
            "Investment Tracker"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============================================================
# Scheduler Management Endpoints
# ============================================================

@app.get("/scheduler/status")
async def scheduler_status():
    """스케줄러 상태 조회"""
    return get_job_status()


@app.post("/scheduler/start")
async def start_scheduler_endpoint():
    """스케줄러 수동 시작"""
    start_scheduler()
    return {"status": "started", "jobs": get_job_status()["jobs"]}


@app.post("/scheduler/stop")
async def stop_scheduler_endpoint():
    """스케줄러 수동 중지"""
    shutdown_scheduler()
    return {"status": "stopped"}
