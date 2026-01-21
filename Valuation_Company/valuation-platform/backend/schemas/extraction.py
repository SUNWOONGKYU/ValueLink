"""
Data extraction and auto-collection schemas

AI 데이터 추출 및 자동 수집 관련 스키마
"""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field

from .common import ProjectStatusCode


# ========================================
# 6. AI 데이터 추출 (POST /projects/{project_id}/extract)
# ========================================

class ExtractionRequest(BaseModel):
    """데이터 추출 요청"""
    extraction_type: Literal["comprehensive", "quick"] = Field(
        default="comprehensive", description="추출 유형"
    )
    use_ocr: bool = Field(default=True, description="OCR 사용 여부")
    validate_data: bool = Field(default=True, description="데이터 검증 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "extraction_type": "comprehensive",
                "use_ocr": True,
                "validate_data": True
            }
        }


class ExtractedCompanyData(BaseModel):
    """추출된 회사 데이터"""
    name: str
    ticker: Optional[str] = None
    is_listed: bool
    industry: str
    shares_outstanding: Optional[int] = None


class ExtractedFinancials(BaseModel):
    """추출된 재무 데이터"""
    revenue: List[int] = Field(..., description="매출액 (최근 5년)")
    ebit: List[int] = Field(..., description="영업이익 (최근 5년)")
    net_income: List[int] = Field(..., description="순이익 (최근 5년)")
    capex: List[int] = Field(..., description="자본적지출 (최근 5년)")
    depreciation: List[int] = Field(..., description="감가상각비 (최근 5년)")


class ExtractedBalanceSheet(BaseModel):
    """추출된 재무상태표 데이터"""
    total_assets: int
    total_liabilities: int
    equity: int
    current_assets: int
    fixed_assets: int
    intangible_assets: int
    investment_assets: int


class ExtractedCapitalStructure(BaseModel):
    """추출된 자본 구조"""
    debt: int
    interest_bearing_debt: int
    cash: int


class ConfidenceScores(BaseModel):
    """신뢰도 점수"""
    financials: float = Field(..., ge=0, le=1, description="재무 데이터 신뢰도")
    balance_sheet: float = Field(..., ge=0, le=1, description="재무상태표 신뢰도")
    capital_structure: float = Field(..., ge=0, le=1, description="자본 구조 신뢰도")


class ExtractionResponse(BaseModel):
    """데이터 추출 응답"""
    project_id: str
    extraction_status: Literal["completed", "failed", "partial"]
    extracted_data: dict = Field(..., description="추출된 데이터")
    confidence_scores: ConfidenceScores

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "extraction_status": "completed",
                "extracted_data": {
                    "company": {
                        "name": "삼성전자",
                        "ticker": "005930",
                        "is_listed": True,
                        "industry": "전자제품 제조업",
                        "shares_outstanding": 5920370000
                    },
                    "financials": {
                        "revenue": [258937700, 243770400, 236806700, 229234200, 206205700],
                        "ebit": [43372600, 47854000, 58886800, 61186600, 51630000],
                        "net_income": [34451400, 26408100, 44344700, 39895100, 26263700],
                        "capex": [28481900, 32784300, 48133000, 53625400, 43113600],
                        "depreciation": [24336300, 27695200, 29095000, 30562900, 31747800]
                    },
                    "balance_sheet": {
                        "total_assets": 378333900,
                        "total_liabilities": 92970000,
                        "equity": 285363900,
                        "current_assets": 141482500,
                        "fixed_assets": 184843200,
                        "intangible_assets": 10285400,
                        "investment_assets": 41722800
                    },
                    "capital_structure": {
                        "debt": 97018900,
                        "interest_bearing_debt": 46707100,
                        "cash": 56678500
                    }
                },
                "confidence_scores": {
                    "financials": 0.95,
                    "balance_sheet": 0.92,
                    "capital_structure": 0.88
                }
            }
        }


# ========================================
# 7. AI 자동 수집 (POST /projects/{project_id}/auto-collect)
# ========================================

class MarketData(BaseModel):
    """시장 데이터"""
    risk_free_rate: float = Field(..., description="무위험이자율")
    risk_free_rate_source: str = Field(..., description="무위험이자율 출처")
    market_risk_premium: float = Field(..., description="시장위험프리미엄")
    market_risk_premium_source: str = Field(..., description="시장위험프리미엄 출처")


class IndustryData(BaseModel):
    """업종 데이터"""
    industry_beta: float = Field(..., description="업종 베타")
    industry_beta_source: str = Field(..., description="업종 베타 출처")
    industry_per: float = Field(..., description="업종 PER")
    industry_pbr: float = Field(..., description="업종 PBR")
    industry_roe: float = Field(..., description="업종 ROE")


class ComparableCompany(BaseModel):
    """비교 기업"""
    name: str
    ticker: str
    per: float
    pbr: float
    ev_ebitda: float
    market_cap: int


class AutoCollectResponse(BaseModel):
    """자동 수집 응답"""
    project_id: str
    status: ProjectStatusCode
    collected_data: dict = Field(..., description="수집된 데이터")
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "collecting",
                "collected_data": {
                    "market_data": {
                        "risk_free_rate": 0.035,
                        "risk_free_rate_source": "한국은행 API (3년 국고채, 2026-01-20)",
                        "market_risk_premium": 0.065,
                        "market_risk_premium_source": "역사적 평균 (1980-2025)"
                    },
                    "industry_data": {
                        "industry_beta": 1.15,
                        "industry_beta_source": "KOSPI 전자업종 평균",
                        "industry_per": 18.5,
                        "industry_pbr": 1.8,
                        "industry_roe": 0.09
                    },
                    "comparable_companies": [
                        {
                            "name": "SK하이닉스",
                            "ticker": "000660",
                            "per": 15.2,
                            "pbr": 1.3,
                            "ev_ebitda": 7.5,
                            "market_cap": 75000000
                        },
                        {
                            "name": "DB하이텍",
                            "ticker": "000990",
                            "per": 18.5,
                            "pbr": 1.5,
                            "ev_ebitda": 8.2,
                            "market_cap": 3500000
                        }
                    ]
                },
                "message": "자료 수집이 완료되었습니다. 평가를 시작합니다."
            }
        }
