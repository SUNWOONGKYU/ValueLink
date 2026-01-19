"""
Investment Tracker API Endpoints
스타트업 투자 트래커 API (Supabase 버전)

@task Investment Tracker
@description 기업, 뉴스, 이메일, 수집 관련 API 엔드포인트
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from app.core.config import settings
from app.schemas.investment_tracker import (
    CompanyResponse,
    CompanyListResponse,
    CompanyDetailResponse,
    CompanyCreate,
    CompanyUpdate,
    InvestmentRoundResponse,
    NewsDetailResponse,
    NewsListResponse,
    EmailTemplateResponse,
    CollectionResponse,
    CollectionListResponse,
    CollectionTriggerRequest,
    CollectionTriggerResponse,
    DashboardStats,
    InvestmentStage
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Supabase 클라이언트가 설정되어 있는지 확인
def get_supabase():
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    from app.db.supabase_client import supabase_client
    return supabase_client


# ============================================================
# Dashboard
# ============================================================

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """대시보드 통계 조회"""
    client = get_supabase()

    if not client:
        # Supabase 미설정 시 샘플 데이터 반환
        return DashboardStats(
            total_companies=0,
            total_news=0,
            total_funding_krw=0.0,
            this_week_new_companies=0,
            this_week_new_news=0,
            industry_distribution={},
            stage_distribution={},
            last_collection_date=None,
            last_collection_status=None
        )

    try:
        stats = await client.get_dashboard_stats()
        return DashboardStats(**stats)
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Companies
# ============================================================

@router.get("/companies", response_model=CompanyListResponse)
async def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    stage: Optional[InvestmentStage] = None,
    search: Optional[str] = None
):
    """기업 목록 조회"""
    client = get_supabase()

    if not client:
        return CompanyListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )

    try:
        result = await client.get_companies(
            page=page,
            page_size=page_size,
            industry=industry,
            stage=stage.value if stage else None,
            search=search
        )

        return CompanyListResponse(
            items=[CompanyResponse(**c) for c in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"List companies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/{company_id}", response_model=CompanyDetailResponse)
async def get_company_detail(company_id: int):
    """기업 상세 조회"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        company = await client.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # 투자 라운드
        rounds = await client.get_investment_rounds(company_id)

        # 뉴스
        news_result = await client.get_news(company_id=company_id, page_size=10)

        return CompanyDetailResponse(
            **company,
            investment_rounds=[InvestmentRoundResponse(**r) for r in rounds],
            news=[NewsDetailResponse(**n) for n in news_result["items"]]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get company error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/companies", response_model=CompanyResponse)
async def create_company(company_data: CompanyCreate):
    """기업 생성"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        # 중복 확인
        existing = await client.get_company_by_name(company_data.name_ko)
        if existing:
            raise HTTPException(status_code=400, detail="Company already exists")

        company = await client.create_company(company_data.model_dump())
        return CompanyResponse(**company)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create company error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, update_data: CompanyUpdate):
    """기업 수정"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        company = await client.update_company(
            company_id,
            update_data.model_dump(exclude_unset=True)
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return CompanyResponse(**company)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update company error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Email Templates
# ============================================================

@router.get("/companies/{company_id}/email-template", response_model=EmailTemplateResponse)
async def get_company_email_template(company_id: int):
    """기업의 이메일 템플릿 조회"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=404, detail="Email template not found")

    try:
        template = await client.get_email_template(company_id)
        if not template:
            raise HTTPException(status_code=404, detail="Email template not found")

        return EmailTemplateResponse(**template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get email template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/companies/{company_id}/email-template/regenerate", response_model=EmailTemplateResponse)
async def regenerate_email_template(
    company_id: int,
    feedback: Optional[str] = None
):
    """이메일 템플릿 재생성"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        company = await client.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # 이메일 생성
        from app.services.email_generator import email_generator

        # 최근 투자 라운드
        rounds = await client.get_investment_rounds(company_id)
        latest_round = rounds[0] if rounds else None

        # 기존 템플릿
        existing = await client.get_email_template(company_id)

        if feedback and existing:
            from app.services.email_generator import GeneratedEmail
            original = GeneratedEmail(
                subject=existing["subject"],
                body=existing["body"],
                template_type=existing.get("template_type", "initial"),
                generation_prompt=existing.get("generation_prompt", "")
            )
            # 피드백 기반 재생성 (추후 구현)
            generated = original
        else:
            # 새로 생성
            class MockCompany:
                def __init__(self, data):
                    self.name_ko = data.get("name_ko", "")
                    self.name_en = data.get("name_en")
                    self.industry = data.get("industry")
                    self.sub_industry = data.get("sub_industry")
                    self.description = data.get("description")

            generated = await email_generator.generate_initial_email(
                MockCompany(company),
                None
            )

        # 새 템플릿 저장
        new_version = (existing.get("version", 0) if existing else 0) + 1

        template = await client.create_email_template({
            "company_id": company_id,
            "subject": generated.subject,
            "body": generated.body,
            "template_type": generated.template_type,
            "generation_prompt": generated.generation_prompt,
            "version": new_version,
            "is_active": True
        })

        return EmailTemplateResponse(**template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Regenerate email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# News
# ============================================================

@router.get("/news", response_model=NewsListResponse)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    company_id: Optional[int] = None,
    search: Optional[str] = None
):
    """뉴스 목록 조회"""
    client = get_supabase()

    if not client:
        return NewsListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )

    try:
        result = await client.get_news(
            page=page,
            page_size=page_size,
            source=source,
            company_id=company_id
        )

        return NewsListResponse(
            items=[NewsDetailResponse(**n) for n in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"List news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/{news_id}", response_model=NewsDetailResponse)
async def get_news_detail(news_id: int):
    """뉴스 상세 조회"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=404, detail="News not found")

    try:
        result = await client.select("investment_news", filters={"id": news_id})
        if not result:
            raise HTTPException(status_code=404, detail="News not found")

        return NewsDetailResponse(**result[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Collections
# ============================================================

@router.get("/collections", response_model=CollectionListResponse)
async def list_collections(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    """수집 작업 이력 조회"""
    client = get_supabase()

    if not client:
        return CollectionListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )

    try:
        result = await client.get_collections(page=page, page_size=page_size)

        return CollectionListResponse(
            items=[CollectionResponse(**c) for c in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"List collections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections/trigger", response_model=CollectionTriggerResponse)
async def trigger_collection(
    request: CollectionTriggerRequest,
    background_tasks: BackgroundTasks
):
    """수동 수집 실행 트리거"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        # 수집 레코드 생성
        now = datetime.utcnow()
        iso_calendar = now.isocalendar()

        collection = await client.create_collection({
            "collection_date": now.isoformat(),
            "week_number": iso_calendar.week,
            "year": iso_calendar.year,
            "status": "pending"
        })

        # 백그라운드 작업 (추후 구현)
        # background_tasks.add_task(run_weekly_collection, ...)

        return CollectionTriggerResponse(
            collection_id=collection["id"],
            status="started",
            message="Collection started in background"
        )
    except Exception as e:
        logger.error(f"Trigger collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection_detail(collection_id: int):
    """수집 작업 상세 조회"""
    client = get_supabase()

    if not client:
        raise HTTPException(status_code=404, detail="Collection not found")

    try:
        result = await client.select("weekly_collections", filters={"id": collection_id})
        if not result:
            raise HTTPException(status_code=404, detail="Collection not found")

        return CollectionResponse(**result[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Utility
# ============================================================

@router.get("/industries")
async def list_industries():
    """업종 목록 조회"""
    client = get_supabase()

    if not client:
        return {"industries": []}

    try:
        companies = await client.select("startup_companies", columns="industry")
        industries = list(set(c.get("industry") for c in companies if c.get("industry")))
        return {"industries": sorted(industries)}
    except Exception as e:
        logger.error(f"List industries error: {e}")
        return {"industries": []}


@router.get("/stages")
async def list_stages():
    """투자 단계 목록 조회"""
    return {
        "stages": [
            {"value": "seed", "label": "시드"},
            {"value": "pre_a", "label": "프리A"},
            {"value": "series_a", "label": "시리즈A"},
            {"value": "series_b", "label": "시리즈B"},
            {"value": "series_c", "label": "시리즈C"},
            {"value": "later", "label": "시리즈C+"}
        ]
    }
