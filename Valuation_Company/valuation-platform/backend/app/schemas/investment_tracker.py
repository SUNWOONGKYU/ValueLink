"""
Investment Tracker Pydantic Schemas
API Request/Response validation

@task Investment Tracker
@description API 요청/응답 검증을 위한 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# Enums
# ============================================================

class InvestmentStage(str, Enum):
    """투자 단계"""
    SEED = "seed"
    PRE_A = "pre_a"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    LATER = "later"


class CollectionStatus(str, Enum):
    """수집 작업 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================
# Company Schemas
# ============================================================

class CompanyBase(BaseModel):
    """기업 기본 정보"""
    name_ko: str = Field(..., min_length=1, max_length=200, description="한글 기업명")
    name_en: Optional[str] = Field(None, max_length=200, description="영문 기업명")
    industry: Optional[str] = Field(None, max_length=100, description="업종/분야")
    sub_industry: Optional[str] = Field(None, max_length=100, description="세부 분야")
    website: Optional[str] = Field(None, max_length=500, description="웹사이트")
    email: Optional[str] = Field(None, max_length=200, description="이메일")
    phone: Optional[str] = Field(None, max_length=50, description="전화번호")
    address: Optional[str] = Field(None, max_length=500, description="주소")
    founded_year: Optional[int] = Field(None, ge=1900, le=2100, description="설립년도")
    employee_count: Optional[int] = Field(None, ge=0, description="직원수")
    description: Optional[str] = Field(None, description="기업 설명")


class CompanyCreate(CompanyBase):
    """기업 생성 요청"""
    pass


class CompanyUpdate(BaseModel):
    """기업 수정 요청"""
    name_ko: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    sub_industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    founded_year: Optional[int] = Field(None, ge=1900, le=2100)
    employee_count: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """기업 응답"""
    id: int
    latest_stage: Optional[InvestmentStage] = None
    latest_round_date: Optional[datetime] = None
    total_funding_krw: Optional[float] = Field(None, description="총 누적 투자금 (억원)")
    is_active: bool = True
    first_discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    """기업 목록 응답 (페이지네이션)"""
    items: List[CompanyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class InvestmentRoundResponse(BaseModel):
    """투자 라운드 응답"""
    id: int
    company_id: int
    stage: InvestmentStage
    round_date: Optional[datetime] = None
    investment_amount_krw: Optional[float] = Field(None, description="투자 금액 (억원)")
    valuation_pre_krw: Optional[float] = Field(None, description="Pre-money 밸류에이션 (억원)")
    valuation_post_krw: Optional[float] = Field(None, description="Post-money 밸류에이션 (억원)")
    lead_investor: Optional[str] = None
    investors: Optional[List[Dict[str, Any]]] = None
    remarks: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsResponse(BaseModel):
    """뉴스 응답 (간략)"""
    id: int
    source: str
    title: str
    published_at: Optional[datetime] = None
    ai_summary: Optional[str] = None
    source_url: str

    model_config = ConfigDict(from_attributes=True)


class CompanyDetailResponse(CompanyResponse):
    """기업 상세 응답 (투자 라운드, 뉴스 포함)"""
    investment_rounds: List[InvestmentRoundResponse] = []
    news: List[NewsResponse] = []


# ============================================================
# Investment Round Schemas
# ============================================================

class InvestmentRoundBase(BaseModel):
    """투자 라운드 기본 정보"""
    stage: InvestmentStage
    round_date: Optional[datetime] = None
    investment_amount_krw: Optional[float] = Field(None, ge=0, description="투자 금액 (억원)")
    valuation_pre_krw: Optional[float] = Field(None, ge=0, description="Pre-money 밸류에이션 (억원)")
    valuation_post_krw: Optional[float] = Field(None, ge=0, description="Post-money 밸류에이션 (억원)")
    lead_investor: Optional[str] = Field(None, max_length=200)
    investors: Optional[List[Dict[str, Any]]] = None
    remarks: Optional[str] = None
    source_url: Optional[str] = Field(None, max_length=1000)


class InvestmentRoundCreate(InvestmentRoundBase):
    """투자 라운드 생성 요청"""
    company_id: int


# ============================================================
# News Schemas
# ============================================================

class NewsBase(BaseModel):
    """뉴스 기본 정보"""
    source: str = Field(..., max_length=100)
    source_url: str = Field(..., max_length=1000)
    title: str = Field(..., max_length=500)
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = Field(None, max_length=200)


class NewsCreate(NewsBase):
    """뉴스 생성 요청"""
    collection_id: Optional[int] = None


class NewsDetailResponse(BaseModel):
    """뉴스 상세 응답"""
    id: int
    company_id: Optional[int] = None
    collection_id: Optional[int] = None
    source: str
    source_url: str
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    published_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NewsListResponse(BaseModel):
    """뉴스 목록 응답 (페이지네이션)"""
    items: List[NewsDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# Email Template Schemas
# ============================================================

class EmailTemplateBase(BaseModel):
    """이메일 템플릿 기본 정보"""
    subject: str = Field(..., max_length=500)
    body: str
    template_type: str = Field(default="initial", max_length=50)


class EmailTemplateCreate(EmailTemplateBase):
    """이메일 템플릿 생성 요청"""
    company_id: int
    generation_prompt: Optional[str] = None


class EmailTemplateResponse(EmailTemplateBase):
    """이메일 템플릿 응답"""
    id: int
    company_id: int
    generation_prompt: Optional[str] = None
    version: int = 1
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Collection Schemas
# ============================================================

class CollectionBase(BaseModel):
    """수집 작업 기본 정보"""
    collection_date: datetime
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2020, le=2100)


class CollectionCreate(CollectionBase):
    """수집 작업 생성 요청"""
    pass


class CollectionResponse(CollectionBase):
    """수집 작업 응답"""
    id: int
    status: CollectionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_news_crawled: int = 0
    total_companies_found: int = 0
    new_companies_added: int = 0
    emails_generated: int = 0
    error_count: int = 0
    error_log: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CollectionListResponse(BaseModel):
    """수집 작업 목록 응답"""
    items: List[CollectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# Dashboard Schemas
# ============================================================

class DashboardStats(BaseModel):
    """대시보드 통계"""
    total_companies: int = Field(..., description="전체 기업 수")
    total_news: int = Field(..., description="전체 뉴스 수")
    total_funding_krw: float = Field(..., description="총 투자 금액 (억원)")
    this_week_new_companies: int = Field(..., description="이번 주 신규 기업")
    this_week_new_news: int = Field(..., description="이번 주 신규 뉴스")

    # 업종별 분포
    industry_distribution: Dict[str, int] = Field(default_factory=dict, description="업종별 기업 수")

    # 투자 단계별 분포
    stage_distribution: Dict[str, int] = Field(default_factory=dict, description="투자 단계별 기업 수")

    # 최근 수집 정보
    last_collection_date: Optional[datetime] = None
    last_collection_status: Optional[CollectionStatus] = None


# ============================================================
# Filter Schemas
# ============================================================

class CompanyFilter(BaseModel):
    """기업 필터"""
    industry: Optional[str] = None
    stage: Optional[InvestmentStage] = None
    min_funding: Optional[float] = Field(None, ge=0, description="최소 투자 금액 (억원)")
    max_funding: Optional[float] = Field(None, ge=0, description="최대 투자 금액 (억원)")
    search: Optional[str] = Field(None, description="기업명 검색")
    is_active: Optional[bool] = None


class NewsFilter(BaseModel):
    """뉴스 필터"""
    source: Optional[str] = None
    company_id: Optional[int] = None
    is_processed: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = Field(None, description="제목/내용 검색")


# ============================================================
# Trigger Schemas
# ============================================================

class CollectionTriggerRequest(BaseModel):
    """수동 수집 실행 요청"""
    sources: Optional[List[str]] = Field(
        default=["naver", "platum"],
        description="수집할 소스 목록"
    )
    max_pages: Optional[int] = Field(default=3, ge=1, le=10, description="크롤링 페이지 수")


class CollectionTriggerResponse(BaseModel):
    """수집 실행 응답"""
    collection_id: int
    status: str
    message: str
