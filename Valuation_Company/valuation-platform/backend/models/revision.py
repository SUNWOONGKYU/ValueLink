"""
Revision Model

수정 요청
"""

from sqlalchemy import Column, String, ForeignKey, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class RevisionType(str, enum.Enum):
    ASSUMPTION_CHANGE = "assumption_change"  # 가정 변경
    SCOPE_CHANGE = "scope_change"            # 범위 변경
    CLARIFICATION = "clarification"          # 명확화


class Revision(Base, TimestampMixin):
    """수정 요청 테이블"""
    __tablename__ = "revisions"

    # Primary Key
    revision_id = Column(String(50), primary_key=True, comment="수정 요청 ID (예: REV-001)")

    # Foreign Key
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # 수정 내용
    revision_type = Column(SQLEnum(RevisionType), nullable=False, comment="수정 유형")
    requested_changes = Column(JSONB, nullable=False, comment="""
        요청된 변경 사항 JSON:
        {
            "wacc": 0.105,
            "terminal_growth_rate": 0.03,
            "comparable_companies": ["SK하이닉스", "DB하이텍", "LX세미콘"]
        }
    """)
    reason = Column(Text, nullable=False, comment="수정 요청 사유")
    supporting_documents = Column(JSONB, nullable=True, comment="근거 문서 ID 목록 (배열)")
    customer_notes = Column(Text, nullable=True, comment="고객 메모")

    # 처리 정보
    requested_at = Column(DateTime, nullable=True, comment="요청 시각")
    estimated_completion = Column(DateTime, nullable=True, comment="예상 완료 시각")

    # Relationship
    project = relationship("Project", backref="revisions")

    def __repr__(self):
        return f"<Revision(revision_id='{self.revision_id}', project_id='{self.project_id}', type='{self.revision_type}')>"
