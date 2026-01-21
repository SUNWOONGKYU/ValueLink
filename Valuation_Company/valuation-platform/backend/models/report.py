"""
Report Model

발행된 보고서
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    """보고서 테이블"""
    __tablename__ = "reports"

    # Primary Key
    report_id = Column(String(100), primary_key=True, comment="보고서 ID (예: RPT-SAMSU-2501191430-CP-001)")

    # Foreign Key
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # 보고서 정보
    report_type = Column(String(50), nullable=False, comment="보고서 유형 (comprehensive, single_method, executive_summary)")
    delivery_format = Column(String(20), nullable=False, comment="파일 형식 (pdf, docx, both)")
    delivery_method = Column(String(20), nullable=False, comment="전달 방법 (download, email, both)")
    include_appendix = Column(Boolean, default=True, comment="부록 포함 여부")
    watermark = Column(Boolean, default=False, comment="워터마크 포함 여부")

    # 파일 정보
    report_url = Column(String(1000), nullable=True, comment="보고서 다운로드 URL")
    report_path = Column(String(1000), nullable=True, comment="보고서 저장 경로")
    page_count = Column(Integer, nullable=True, comment="페이지 수")
    generation_time = Column(String(50), nullable=True, comment="생성 소요 시간")

    # 발행 정보
    issued_at = Column(DateTime, nullable=True, comment="발행 시각")
    issued_by = Column(String(200), nullable=True, comment="발행자 이메일")
    expires_at = Column(DateTime, nullable=True, comment="만료 일시")
    download_count = Column(Integer, default=0, comment="다운로드 횟수")

    # Relationship
    project = relationship("Project", back_populates="reports")

    def __repr__(self):
        return f"<Report(report_id='{self.report_id}', project_id='{self.project_id}', type='{self.report_type}')>"
