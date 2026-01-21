"""
Negotiation Model

조건 협의 내역
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class NegotiationType(str, enum.Enum):
    PRICE_ADJUSTMENT = "price_adjustment"  # 가격 조정
    SCOPE_CHANGE = "scope_change"          # 범위 변경
    TIMELINE_CHANGE = "timeline_change"    # 일정 변경


class RequesterType(str, enum.Enum):
    CUSTOMER = "customer"  # 고객
    ADMIN = "admin"        # 관리자


class Negotiation(Base, TimestampMixin):
    """협의 테이블"""
    __tablename__ = "negotiations"

    # Primary Key
    negotiation_id = Column(String(50), primary_key=True, comment="협의 ID (예: NEG-001)")

    # Foreign Key
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # 협의 내용
    negotiation_type = Column(SQLEnum(NegotiationType), nullable=False, comment="협의 유형")
    proposed_amount = Column(Integer, nullable=True, comment="제안 금액")
    proposed_scope = Column(ARRAY(String), nullable=True, comment="제안 범위 (평가법 목록)")
    message = Column(Text, nullable=False, comment="협의 메시지")
    requester = Column(SQLEnum(RequesterType), nullable=False, comment="요청자")

    # 응답 대기
    pending_response_from = Column(SQLEnum(RequesterType), nullable=False, comment="응답 대기 중인 측")

    # Relationship
    project = relationship("Project", back_populates="negotiations")

    def __repr__(self):
        return f"<Negotiation(negotiation_id='{self.negotiation_id}', project_id='{self.project_id}', type='{self.negotiation_type}')>"
