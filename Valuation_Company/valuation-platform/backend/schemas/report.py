"""
Report generation schemas

최종 확정 및 보고서 발행 관련 스키마
"""

from typing import Optional, Literal, Dict
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from .common import ProjectStatusCode


# ========================================
# 14. 최종 확정 (POST /projects/{project_id}/finalize)
# ========================================

class FinalValuation(BaseModel):
    """최종 평가 결과"""
    enterprise_value: int = Field(..., description="기업가치")
    equity_value: int = Field(..., description="주주가치")
    value_per_share: float = Field(..., description="주당가치")


class FinalizeRequest(BaseModel):
    """최종 확정 요청"""
    final_approval: bool = Field(..., description="최종 승인 여부")
    accountant_comments: str = Field(..., description="회계사 의견")
    selected_valuation: Literal["integrated", "dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"] = Field(
        default="integrated", description="선택된 평가법"
    )
    report_type: Literal["comprehensive", "single_method", "executive_summary"] = Field(
        default="comprehensive", description="보고서 유형"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "final_approval": True,
                "accountant_comments": "모든 판단 포인트 검토 완료. 고객 수정 요청 반영 완료. 평가 결과 최종 확정 승인.",
                "selected_valuation": "integrated",
                "report_type": "comprehensive"
            }
        }


class FinalizeResponse(BaseModel):
    """최종 확정 응답"""
    project_id: str
    status: ProjectStatusCode
    final_valuation: FinalValuation
    selected_method: str = Field(..., description="선택된 평가법")
    weights: Optional[Dict[str, float]] = Field(None, description="평가법별 가중치 (통합 평가 시)")
    finalized_at: datetime
    finalized_by: EmailStr
    all_approval_points_completed: bool = Field(..., description="22개 포인트 승인 완료 여부")
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "completed",
                "final_valuation": {
                    "enterprise_value": 148200000000,
                    "equity_value": 148200000000,
                    "value_per_share": 14820
                },
                "selected_method": "integrated",
                "weights": {
                    "dcf": 0.30,
                    "relative": 0.25,
                    "asset": 0.20,
                    "capital_market_law": 0.15,
                    "inheritance_tax_law": 0.10
                },
                "finalized_at": "2026-01-20T17:00:00Z",
                "finalized_by": "kim@company.com",
                "all_approval_points_completed": True,
                "message": "평가가 최종 확정되었습니다. 보고서를 발행합니다."
            }
        }


# ========================================
# 15. 보고서 발행 (POST /projects/{project_id}/report)
# ========================================

class ReportRequest(BaseModel):
    """보고서 발행 요청"""
    report_type: Literal["comprehensive", "single_method", "executive_summary"] = Field(
        default="comprehensive", description="보고서 유형"
    )
    delivery_format: Literal["pdf", "docx", "both"] = Field(default="pdf", description="파일 형식")
    delivery_method: Literal["download", "email", "both"] = Field(default="download", description="전달 방법")
    include_appendix: bool = Field(default=True, description="부록 포함 여부")
    watermark: bool = Field(default=False, description="워터마크 포함 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "comprehensive",
                "delivery_format": "pdf",
                "delivery_method": "download",
                "include_appendix": True,
                "watermark": False
            }
        }


class ReportResponse(BaseModel):
    """보고서 발행 응답"""
    project_id: str
    report_id: str = Field(..., description="보고서 ID")
    report_url: str = Field(..., description="보고서 다운로드 URL")
    report_type: str = Field(..., description="보고서 유형")
    page_count: int = Field(..., description="페이지 수")
    generation_time: str = Field(..., description="생성 소요 시간")
    status: ProjectStatusCode
    issued_at: datetime
    issued_by: EmailStr
    expires_at: Optional[datetime] = Field(None, description="만료 일시")
    download_count: int = Field(default=0, description="다운로드 횟수")
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "report_id": "RPT-SAMSU-2501191430-CP-001",
                "report_url": "https://api.valuelink.com/reports/RPT-SAMSU-2501191430-CP-001.pdf",
                "report_type": "comprehensive",
                "page_count": 80,
                "generation_time": "45 seconds",
                "status": "completed",
                "issued_at": "2026-01-20T17:30:00Z",
                "issued_by": "kim@company.com",
                "expires_at": "2026-02-20T17:30:00Z",
                "download_count": 0,
                "message": "평가 보고서가 발행되었습니다."
            }
        }
