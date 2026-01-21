"""
Human approval point schemas

22개 회계사 판단 포인트 관련 스키마
"""

from typing import Optional, List, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from .common import ProjectStatusCode, ValuationMethodCode


# ========================================
# 9. 회계사 판단 포인트 (GET /projects/{project_id}/approval-points)
# ========================================

# 판단 포인트 카테고리
ApprovalCategory = Literal["재무", "시장", "자산", "법률"]

# 중요도
ImportanceLevel = Literal["high", "medium", "low"]

# 승인 상태
ApprovalStatus = Literal["pending", "approved", "rejected", "custom"]


class ApprovalPoint(BaseModel):
    """회계사 판단 포인트"""
    point_id: str = Field(..., description="포인트 ID (JP001-JP022)", pattern=r'^JP\d{3}$')
    point_name: str = Field(..., description="포인트명 (영문)")
    display_name: str = Field(..., description="표시명 (한글)")
    category: ApprovalCategory = Field(..., description="카테고리")
    importance: ImportanceLevel = Field(..., description="중요도")
    valuation_method: ValuationMethodCode = Field(..., description="해당 평가법")

    # AI 제안
    ai_value: Union[float, int, str, List[str], dict] = Field(..., description="AI 제안 값")
    ai_rationale: str = Field(..., description="AI 근거 설명")
    suggested_range: Optional[List[Union[float, int]]] = Field(None, description="권장 범위")

    # 회계사 승인
    human_decision: Optional[ApprovalStatus] = Field(None, description="회계사 결정")
    custom_value: Optional[Union[float, int, str, List[str], dict]] = Field(None, description="회계사 수정값")
    status: ApprovalStatus = Field(default="pending", description="승인 상태")
    accountant_notes: Optional[str] = Field(None, description="회계사 메모")

    class Config:
        json_schema_extra = {
            "example": {
                "point_id": "JP001",
                "point_name": "revenue_growth_rate",
                "display_name": "매출 성장률",
                "category": "재무",
                "importance": "high",
                "valuation_method": "dcf",
                "ai_value": 0.05,
                "ai_rationale": "최근 5년 평균 성장률 4.8%를 기반으로 5%를 제안합니다.",
                "suggested_range": [0.03, 0.08],
                "human_decision": None,
                "custom_value": None,
                "status": "pending",
                "accountant_notes": None
            }
        }


class ApprovalPointsResponse(BaseModel):
    """판단 포인트 목록 응답"""
    project_id: str
    status: ProjectStatusCode
    total_points: int = Field(..., description="전체 포인트 수")
    approved_count: int = Field(..., description="승인 완료 수")
    pending_count: int = Field(..., description="승인 대기 수")
    approval_points: List[ApprovalPoint] = Field(..., description="판단 포인트 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "human_approval",
                "total_points": 22,
                "approved_count": 0,
                "pending_count": 22,
                "approval_points": [
                    {
                        "point_id": "JP001",
                        "point_name": "revenue_growth_rate",
                        "display_name": "매출 성장률",
                        "category": "재무",
                        "importance": "high",
                        "valuation_method": "dcf",
                        "ai_value": 0.05,
                        "ai_rationale": "최근 5년 평균 성장률 4.8%를 기반으로 5%를 제안합니다.",
                        "suggested_range": [0.03, 0.08],
                        "human_decision": None,
                        "custom_value": None,
                        "status": "pending",
                        "accountant_notes": None
                    }
                ]
            }
        }


# ========================================
# 10. 판단 포인트 승인 (POST /projects/{project_id}/approval-points/{point_id})
# ========================================

class ApprovalDecisionRequest(BaseModel):
    """판단 포인트 승인 요청"""
    human_decision: Literal["approved", "rejected", "custom"] = Field(..., description="회계사 결정")
    custom_value: Optional[Union[float, int, str, List[str], dict]] = Field(None, description="수정값 (custom 시 필수)")
    accountant_notes: str = Field(..., description="회계사 메모")
    supporting_documents: Optional[List[str]] = Field(None, description="근거 문서 ID 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "human_decision": "custom",
                "custom_value": 0.06,
                "accountant_notes": "시장 상황을 고려하여 6%로 조정",
                "supporting_documents": ["doc_123", "doc_456"]
            }
        }


class ValueChange(BaseModel):
    """가치 변화"""
    before: int
    after: int
    change_percent: float


class ImpactAnalysis(BaseModel):
    """영향 분석"""
    affected_valuations: List[ValuationMethodCode] = Field(..., description="영향받는 평가법")
    value_change: dict = Field(..., description="평가법별 가치 변화")


class ApprovalDecisionResponse(BaseModel):
    """판단 포인트 승인 응답"""
    point_id: str
    status: ApprovalStatus
    ai_value: Union[float, int, str, List[str], dict]
    human_decision: Literal["approved", "rejected", "custom"]
    custom_value: Optional[Union[float, int, str, List[str], dict]]
    approved_by: EmailStr
    approved_at: datetime
    accountant_notes: str
    impact_analysis: Optional[ImpactAnalysis] = None

    class Config:
        json_schema_extra = {
            "example": {
                "point_id": "JP001",
                "status": "approved",
                "ai_value": 0.05,
                "human_decision": "custom",
                "custom_value": 0.06,
                "approved_by": "kim@company.com",
                "approved_at": "2026-01-20T14:30:00Z",
                "accountant_notes": "시장 상황을 고려하여 6%로 조정",
                "impact_analysis": {
                    "affected_valuations": ["dcf", "capital_market_law"],
                    "value_change": {
                        "dcf": {
                            "before": 152300000000,
                            "after": 158500000000,
                            "change_percent": 0.041
                        },
                        "integrated": {
                            "before": 146000000000,
                            "after": 148200000000,
                            "change_percent": 0.015
                        }
                    }
                }
            }
        }


# ========================================
# 22개 판단 포인트 전체 목록
# ========================================

APPROVAL_POINTS_SPEC = [
    {"id": "JP001", "name": "revenue_growth_rate", "display": "매출 성장률", "category": "재무", "importance": "high", "method": "dcf"},
    {"id": "JP002", "name": "ebit_margin", "display": "영업이익률", "category": "재무", "importance": "medium", "method": "dcf"},
    {"id": "JP003", "name": "wacc_rate", "display": "WACC", "category": "재무", "importance": "high", "method": "dcf"},
    {"id": "JP004", "name": "terminal_growth_rate", "display": "영구성장률", "category": "재무", "importance": "medium", "method": "dcf"},
    {"id": "JP005", "name": "forecast_period", "display": "예측 기간", "category": "재무", "importance": "low", "method": "dcf"},
    {"id": "JP006", "name": "capex_rate", "display": "자본적지출률", "category": "재무", "importance": "medium", "method": "dcf"},
    {"id": "JP007", "name": "working_capital_change", "display": "운전자본 변화", "category": "재무", "importance": "medium", "method": "dcf"},
    {"id": "JP008", "name": "beta_coefficient", "display": "베타 계수", "category": "시장", "importance": "medium", "method": "dcf"},
    {"id": "JP009", "name": "comparable_companies", "display": "비교기업 목록", "category": "시장", "importance": "medium", "method": "relative"},
    {"id": "JP010", "name": "selected_multiple", "display": "선택 멀티플", "category": "시장", "importance": "medium", "method": "relative"},
    {"id": "JP011", "name": "industry_multiple", "display": "업종 멀티플", "category": "시장", "importance": "medium", "method": "relative"},
    {"id": "JP012", "name": "unlisted_discount", "display": "비상장 할인율", "category": "시장", "importance": "high", "method": "relative"},
    {"id": "JP013", "name": "land_building_appraisal", "display": "토지/건물 감정평가액", "category": "자산", "importance": "high", "method": "asset"},
    {"id": "JP014", "name": "patent_valuation", "display": "특허권 평가액", "category": "자산", "importance": "medium", "method": "asset"},
    {"id": "JP015", "name": "contingent_liabilities", "display": "우발채무", "category": "법률", "importance": "high", "method": "asset"},
    {"id": "JP016", "name": "allowance_for_bad_debts", "display": "대손충당금", "category": "재무", "importance": "medium", "method": "asset"},
    {"id": "JP017", "name": "inventory_nrv", "display": "재고자산 순실현가치", "category": "재무", "importance": "medium", "method": "asset"},
    {"id": "JP018", "name": "unlisted_equity_valuation", "display": "비상장주식 평가액", "category": "자산", "importance": "high", "method": "asset"},
    {"id": "JP019", "name": "income_value_method", "display": "수익가치 산정 방법", "category": "법률", "importance": "medium", "method": "capital_market_law"},
    {"id": "JP020", "name": "asset_income_weight", "display": "자산가치/수익가치 가중치", "category": "법률", "importance": "medium", "method": "capital_market_law"},
    {"id": "JP021", "name": "three_year_avg_income", "display": "최근 3년 평균 순손익", "category": "재무", "importance": "medium", "method": "inheritance_tax_law"},
    {"id": "JP022", "name": "ownership_ratio", "display": "지분율 및 주주 유형", "category": "법률", "importance": "high", "method": "inheritance_tax_law"},
]
