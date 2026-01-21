"""
Approval Point Model

22개 회계사 판단 포인트
"""

from sqlalchemy import Column, String, ForeignKey, Text, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class ApprovalCategory(str, enum.Enum):
    FINANCIAL = "재무"  # 재무
    MARKET = "시장"     # 시장
    ASSET = "자산"      # 자산
    LEGAL = "법률"      # 법률


class ImportanceLevel(str, enum.Enum):
    HIGH = "high"      # 높음
    MEDIUM = "medium"  # 중간
    LOW = "low"        # 낮음


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"    # 승인 대기
    APPROVED = "approved"  # 승인됨
    REJECTED = "rejected"  # 거부됨
    CUSTOM = "custom"      # 수정됨


class ApprovalPoint(Base, TimestampMixin):
    """판단 포인트 테이블"""
    __tablename__ = "approval_points"

    # Primary Key (복합키)
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)
    point_id = Column(String(10), primary_key=True, comment="포인트 ID (JP001-JP022)")

    # 포인트 정보
    point_name = Column(String(100), nullable=False, comment="포인트명 (영문)")
    display_name = Column(String(100), nullable=False, comment="표시명 (한글)")
    category = Column(SQLEnum(ApprovalCategory), nullable=False, comment="카테고리")
    importance = Column(SQLEnum(ImportanceLevel), nullable=False, comment="중요도")
    valuation_method = Column(String(50), nullable=False, comment="해당 평가법")

    # AI 제안
    ai_value = Column(JSONB, nullable=False, comment="AI 제안 값 (다양한 타입 지원)")
    ai_rationale = Column(Text, nullable=False, comment="AI 근거 설명")
    suggested_range = Column(JSONB, nullable=True, comment="권장 범위 (배열)")

    # 회계사 승인
    human_decision = Column(SQLEnum(ApprovalStatus), nullable=True, comment="회계사 결정")
    custom_value = Column(JSONB, nullable=True, comment="회계사 수정값")
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, comment="승인 상태")
    accountant_notes = Column(Text, nullable=True, comment="회계사 메모")
    approved_by = Column(String(200), nullable=True, comment="승인자 이메일")
    approved_at = Column(DateTime, nullable=True, comment="승인 시각")

    # 근거 문서
    supporting_documents = Column(JSONB, nullable=True, comment="근거 문서 ID 목록 (배열)")

    # 영향 분석
    impact_analysis = Column(JSONB, nullable=True, comment="영향 분석 결과")

    # Relationship
    project = relationship("Project", back_populates="approval_points")

    def __repr__(self):
        return f"<ApprovalPoint(project_id='{self.project_id}', point_id='{self.point_id}', status='{self.status}')>"
