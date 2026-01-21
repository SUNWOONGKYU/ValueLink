"""
Valuation Result Model

평가 결과 (5가지 평가법)
"""

from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class ValuationMethod(str, enum.Enum):
    """평가법 (순서 고정: 1→2→3→4→5)"""
    DCF = "dcf"                              # 1. DCF평가법
    RELATIVE = "relative"                    # 2. 상대가치평가법
    CAPITAL_MARKET_LAW = "capital_market_law"  # 3. 본질가치평가법
    ASSET = "asset"                          # 4. 자산가치평가법
    INHERITANCE_TAX_LAW = "inheritance_tax_law"  # 5. 상증세법평가법


class CalculationStatus(str, enum.Enum):
    PENDING = "pending"      # 대기 중
    RUNNING = "running"      # 실행 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"        # 실패
    PARTIAL = "partial"      # 일부 완료


class ValuationResult(Base, TimestampMixin):
    """평가 결과 테이블"""
    __tablename__ = "valuation_results"

    # Primary Key (복합키)
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)
    method = Column(SQLEnum(ValuationMethod), primary_key=True, comment="평가법")

    # 계산 상태
    calculation_status = Column(SQLEnum(CalculationStatus), default=CalculationStatus.PENDING, comment="계산 상태")

    # 평가 결과 (JSONB로 저장)
    result = Column(JSONB, nullable=True, comment="""
        평가 결과 JSON (순서 고정):
        1. dcf: {enterprise_value, equity_value, value_per_share, wacc, terminal_growth, pv_fcff, pv_terminal_value}
        2. relative: {per_valuation, pbr_valuation, ev_ebitda_valuation, average_valuation, value_per_share}
        3. capital_market_law: {intrinsic_value, value_per_share, asset_value, income_value}
        4. asset: {nav, value_per_share, fair_value_adjustments}
        5. inheritance_tax_law: {valuation, value_per_share, income_value, asset_value}
    """)

    # 민감도 분석 (선택)
    sensitivity_analysis = Column(JSONB, nullable=True, comment="민감도 분석 결과")

    # 주요 가정
    key_assumptions = Column(JSONB, nullable=True, comment="주요 가정")

    # 에러 정보 (실패 시)
    error_message = Column(String(1000), nullable=True, comment="에러 메시지")

    # Relationship
    project = relationship("Project", back_populates="valuation_results")

    def __repr__(self):
        return f"<ValuationResult(project_id='{self.project_id}', method='{self.method}', status='{self.calculation_status}')>"
