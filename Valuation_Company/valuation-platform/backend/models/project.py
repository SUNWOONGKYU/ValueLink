"""
Project Model

프로젝트 기본 정보
"""

from sqlalchemy import Column, String, Date, Boolean, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


# Enum 정의
class ProjectStatus(str, enum.Enum):
    REQUESTED = "requested"                # 평가 신청
    QUOTE_SENT = "quote_sent"              # 견적 발송
    NEGOTIATING = "negotiating"            # 조건 협의 중
    APPROVED = "approved"                  # 승인 완료
    DOCUMENTS_UPLOADED = "documents_uploaded"  # 자료 업로드
    COLLECTING = "collecting"              # 자료 수집 중
    EVALUATING = "evaluating"              # 평가 진행 중
    HUMAN_APPROVAL = "human_approval"      # 회계사 승인 대기
    DRAFT_GENERATED = "draft_generated"    # 초안 생성 완료
    REVISION_REQUESTED = "revision_requested"  # 수정 요청
    COMPLETED = "completed"                # 최종 확정


class ValuationPurpose(str, enum.Enum):
    MA = "MA"                      # M&A
    IPO = "IPO"                    # 기업공개
    INVESTMENT = "investment"      # 투자유치
    MERGER = "merger"              # 합병
    INHERITANCE = "inheritance"    # 상속/증여
    LIQUIDATION = "liquidation"    # 청산
    COMPREHENSIVE = "comprehensive"  # 종합 평가


class Project(Base, TimestampMixin):
    """프로젝트 테이블"""
    __tablename__ = "projects"

    # Primary Key
    project_id = Column(String(50), primary_key=True, comment="프로젝트 ID (예: SAMSU-2501191430-CP)")

    # 프로젝트 상태
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.REQUESTED, comment="프로젝트 상태")

    # 회사 정보
    company_name_kr = Column(String(200), nullable=False, comment="회사명 (한글)")
    company_name_en = Column(String(200), nullable=False, comment="회사명 (영문)")
    business_number = Column(String(20), nullable=False, unique=True, comment="사업자등록번호")
    ceo_name = Column(String(100), nullable=False, comment="대표자명")
    industry = Column(String(200), nullable=False, comment="업종")
    industry_code = Column(String(10), nullable=True, comment="업종 코드")
    founded_date = Column(Date, nullable=False, comment="설립일")
    is_listed = Column(Boolean, default=False, comment="상장 여부")
    ticker = Column(String(20), nullable=True, comment="종목 코드")
    shares_outstanding = Column(Integer, nullable=True, comment="발행 주식 수")

    # 담당자 정보
    contact_name = Column(String(100), nullable=False, comment="담당자 이름")
    contact_email = Column(String(200), nullable=False, comment="담당자 이메일")
    contact_phone = Column(String(20), nullable=False, comment="담당자 전화번호")

    # 평가 정보
    # 순서: 1.DCF평가법(dcf) 2.상대가치평가법(relative) 3.본질가치평가법(capital_market_law) 4.자산가치평가법(asset) 5.상증세법평가법(inheritance_tax_law)
    valuation_methods = Column(ARRAY(String), nullable=False, comment="평가법 목록")
    valuation_purpose = Column(SQLEnum(ValuationPurpose), nullable=False, comment="평가 목적")
    valuation_date = Column(Date, nullable=False, comment="평가 기준일")
    requirements = Column(Text, nullable=True, comment="특별 고려사항")

    # 배정 정보
    assigned_accountant = Column(String(200), nullable=True, comment="배정 회계사 이메일")
    reviewer = Column(String(200), nullable=True, comment="검토자 이메일")

    # 계약 정보
    final_amount = Column(Integer, nullable=True, comment="최종 금액")
    payment_terms = Column(String(500), nullable=True, comment="결제 조건")
    contract_signed = Column(Boolean, default=False, comment="계약서 서명 여부")
    contract_date = Column(Date, nullable=True, comment="계약일")

    # 고객 포털 URL
    customer_portal_url = Column(String(500), nullable=True, comment="고객 포털 URL")

    # Relationships
    quotes = relationship("Quote", back_populates="project", cascade="all, delete-orphan")
    negotiations = relationship("Negotiation", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    approval_points = relationship("ApprovalPoint", back_populates="project", cascade="all, delete-orphan")
    valuation_results = relationship("ValuationResult", back_populates="project", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(project_id='{self.project_id}', company='{self.company_name_kr}', status='{self.status}')>"
