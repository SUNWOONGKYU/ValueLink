"""
Draft Model

평가서 초안
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Draft(Base, TimestampMixin):
    """초안 테이블"""
    __tablename__ = "drafts"

    # Primary Key
    draft_id = Column(String(50), primary_key=True, comment="초안 ID (예: DRAFT-SAMSU-001)")

    # Foreign Key
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # 초안 정보
    report_type = Column(String(50), nullable=False, comment="보고서 유형 (comprehensive, single_method, executive_summary)")
    include_appendix = Column(Boolean, default=True, comment="부록 포함 여부")
    custom_notes = Column(Text, nullable=True, comment="회계사 특별 메모")

    # 파일 정보
    draft_url = Column(String(1000), nullable=True, comment="초안 다운로드 URL")
    draft_path = Column(String(1000), nullable=True, comment="초안 저장 경로")
    page_count = Column(Integer, nullable=True, comment="페이지 수")

    # 생성 정보
    generated_at = Column(DateTime, nullable=True, comment="생성 시각")
    customer_review_url = Column(String(1000), nullable=True, comment="고객 검토 URL")

    # Relationship
    project = relationship("Project", back_populates="drafts")

    def __repr__(self):
        return f"<Draft(draft_id='{self.draft_id}', project_id='{self.project_id}', type='{self.report_type}')>"
