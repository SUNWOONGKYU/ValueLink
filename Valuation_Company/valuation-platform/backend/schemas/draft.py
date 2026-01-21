"""
Draft and revision schemas

초안 생성 및 수정 요청 관련 스키마
"""

from typing import Optional, List, Literal, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field

from .common import ProjectStatusCode, ValuationMethodCode


# ========================================
# 11. 초안 생성 (POST /projects/{project_id}/draft)
# ========================================

class DraftRequest(BaseModel):
    """초안 생성 요청"""
    report_type: Literal["comprehensive", "single_method", "executive_summary"] = Field(
        default="comprehensive", description="보고서 유형"
    )
    include_appendix: bool = Field(default=True, description="부록 포함 여부")
    custom_notes: Optional[str] = Field(None, description="회계사 특별 메모")

    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "comprehensive",
                "include_appendix": True,
                "custom_notes": "특별 고려사항을 반영했습니다."
            }
        }


class DraftResponse(BaseModel):
    """초안 생성 응답"""
    project_id: str
    status: ProjectStatusCode
    draft_id: str = Field(..., description="초안 ID")
    draft_url: str = Field(..., description="초안 다운로드 URL")
    page_count: int = Field(..., description="페이지 수")
    generated_at: datetime
    customer_review_url: str = Field(..., description="고객 검토 URL")
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "draft_generated",
                "draft_id": "DRAFT-SAMSU-001",
                "draft_url": "https://api.valuelink.com/drafts/DRAFT-SAMSU-001.pdf",
                "page_count": 80,
                "generated_at": "2026-01-20T15:00:00Z",
                "customer_review_url": "https://valuelink.com/portal/SAMSU-2501191430-CP/review",
                "message": "초안이 생성되었습니다. 고객 검토를 요청합니다."
            }
        }


# ========================================
# 12. 수정 요청 (POST /projects/{project_id}/revisions)
# ========================================

class RevisionRequest(BaseModel):
    """수정 요청"""
    revision_type: Literal["assumption_change", "scope_change", "clarification"] = Field(
        ..., description="수정 유형"
    )
    requested_changes: Dict[str, Union[float, int, str, List[str]]] = Field(
        ..., description="요청된 변경 사항"
    )
    reason: str = Field(..., description="수정 요청 사유")
    supporting_documents: Optional[List[str]] = Field(None, description="근거 문서 ID 목록")
    customer_notes: Optional[str] = Field(None, description="고객 메모")

    class Config:
        json_schema_extra = {
            "example": {
                "revision_type": "assumption_change",
                "requested_changes": {
                    "wacc": 0.105,
                    "terminal_growth_rate": 0.03,
                    "comparable_companies": ["SK하이닉스", "DB하이텍", "LX세미콘"]
                },
                "reason": "시장 상황 변화를 반영해주세요.",
                "supporting_documents": ["doc_789"],
                "customer_notes": "비교기업 추가 요청"
            }
        }


class RevisionResponse(BaseModel):
    """수정 요청 응답"""
    project_id: str
    status: ProjectStatusCode
    revision_id: str = Field(..., description="수정 요청 ID")
    requested_at: datetime
    estimated_completion: datetime
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "revision_requested",
                "revision_id": "REV-001",
                "requested_at": "2026-01-20T16:00:00Z",
                "estimated_completion": "2026-01-21T10:00:00Z",
                "message": "수정 요청이 접수되었습니다. 회계사가 검토 후 재평가를 진행합니다."
            }
        }
