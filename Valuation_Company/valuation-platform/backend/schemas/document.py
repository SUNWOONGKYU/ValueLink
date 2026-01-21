"""
Document upload schemas

문서 업로드 관련 스키마
"""

from typing import List, Literal
from datetime import datetime
from pydantic import BaseModel, Field

from .common import ProjectStatusCode


# ========================================
# 5. 문서 업로드 (POST /projects/{project_id}/documents)
# ========================================

# 문서 카테고리
DocumentCategory = Literal[
    "financial",         # 재무제표
    "business_plan",     # 사업계획서
    "shareholder",       # 주주명부
    "capex",             # 자본적지출
    "working_capital",   # 운전자본
    "others"             # 기타
]

# 업로드 상태
UploadStatus = Literal["pending", "completed"]


class UploadedFileInfo(BaseModel):
    """업로드된 파일 정보"""
    file_id: str = Field(..., description="파일 ID")
    file_name: str = Field(..., description="파일명")
    category: DocumentCategory = Field(..., description="카테고리")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    uploaded_at: datetime = Field(..., description="업로드 시각")

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "doc_001",
                "file_name": "재무제표_2023.pdf",
                "category": "financial",
                "file_size": 15728640,
                "uploaded_at": "2026-01-20T11:00:00Z"
            }
        }


class UploadProgress(BaseModel):
    """업로드 진행 상황"""
    financial: UploadStatus = Field(default="pending", description="재무제표")
    business_plan: UploadStatus = Field(default="pending", description="사업계획서")
    shareholder: UploadStatus = Field(default="pending", description="주주명부")
    capex: UploadStatus = Field(default="pending", description="자본적지출")
    working_capital: UploadStatus = Field(default="pending", description="운전자본")
    others: UploadStatus = Field(default="pending", description="기타")

    class Config:
        json_schema_extra = {
            "example": {
                "financial": "completed",
                "business_plan": "completed",
                "shareholder": "completed",
                "capex": "pending",
                "working_capital": "pending",
                "others": "pending"
            }
        }


class DocumentUploadResponse(BaseModel):
    """문서 업로드 응답"""
    project_id: str
    uploaded_files: List[UploadedFileInfo] = Field(..., description="업로드된 파일 목록")
    upload_progress: UploadProgress = Field(..., description="업로드 진행 상황")
    status: ProjectStatusCode = Field(..., description="프로젝트 상태")
    message: str = Field(..., description="안내 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "uploaded_files": [
                    {
                        "file_id": "doc_001",
                        "file_name": "재무제표_2023.pdf",
                        "category": "financial",
                        "file_size": 15728640,
                        "uploaded_at": "2026-01-20T11:00:00Z"
                    }
                ],
                "upload_progress": {
                    "financial": "completed",
                    "business_plan": "completed",
                    "shareholder": "completed",
                    "capex": "pending",
                    "working_capital": "pending",
                    "others": "pending"
                },
                "status": "documents_uploaded",
                "message": "필수 서류 업로드가 완료되었습니다. AI 자료 수집을 시작합니다."
            }
        }
