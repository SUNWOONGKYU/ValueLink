"""
Quote Model

견적서 정보
"""

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Quote(Base, TimestampMixin):
    """견적서 테이블"""
    __tablename__ = "quotes"

    # Primary Key
    quote_id = Column(String(50), primary_key=True, comment="견적서 ID (예: QT-SAMSU-001)")

    # Foreign Key
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # 견적 내용
    quote_amount = Column(Integer, nullable=False, comment="견적 금액 (KRW)")
    currency = Column(String(10), default="KRW", comment="통화")
    estimated_duration = Column(String(50), nullable=False, comment="예상 소요 기간")
    payment_terms = Column(String(500), nullable=False, comment="결제 조건")
    included_services = Column(ARRAY(String), nullable=False, comment="포함 서비스 목록")
    valid_until = Column(Date, nullable=False, comment="견적 유효 기간")
    notes = Column(Text, nullable=True, comment="비고")

    # 발송 정보
    quote_url = Column(String(500), nullable=True, comment="견적서 다운로드 URL")
    sent_at = Column(DateTime, nullable=True, comment="발송 시각")

    # Relationship
    project = relationship("Project", back_populates="quotes")

    def __repr__(self):
        return f"<Quote(quote_id='{self.quote_id}', project_id='{self.project_id}', amount={self.quote_amount})>"
