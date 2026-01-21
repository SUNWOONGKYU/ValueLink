"""
Document Model

업로드된 문서
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class DocumentCategory(str, enum.Enum):
    FINANCIAL = "financial"              # 재무제표
    BUSINESS_PLAN = "business_plan"      # 사업계획서
    SHAREHOLDER = "shareholder"          # 주주명부
    CAPEX = "capex"                      # 자본적지출
    WORKING_CAPITAL = "working_capital"  # 운전자본
    OTHERS = "others"                    # 기타


class Document(Base, TimestampMixin):
    """문서 테이블"""
    __tablename__ = "documents"

    # Primary Key
    file_id = Column(String(50), primary_key=True, comment="파일 ID")

    # Foreign Key
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # 파일 정보
    file_name = Column(String(500), nullable=False, comment="파일명")
    category = Column(SQLEnum(DocumentCategory), nullable=False, comment="카테고리")
    file_size = Column(Integer, nullable=False, comment="파일 크기 (bytes)")
    file_path = Column(String(1000), nullable=False, comment="저장 경로")
    file_url = Column(String(1000), nullable=True, comment="다운로드 URL")

    # Relationship
    project = relationship("Project", back_populates="documents")

    def __repr__(self):
        return f"<Document(file_id='{self.file_id}', project_id='{self.project_id}', category='{self.category}')>"
