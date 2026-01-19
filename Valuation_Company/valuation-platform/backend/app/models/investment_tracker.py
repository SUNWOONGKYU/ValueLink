"""
Investment Tracker Database Models
5 Tables for startup investment tracking

@task Investment Tracker
@description 스타트업 투자 추적을 위한 데이터베이스 모델
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    ForeignKey, DateTime, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.base_class import Base


class InvestmentStage(str, Enum):
    """투자 단계"""
    SEED = "seed"
    PRE_A = "pre_a"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    LATER = "later"


class CollectionStatus(str, Enum):
    """수집 작업 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class StartupCompany(Base):
    """
    Table 1: 스타트업 기업 마스터
    기업 기본 정보 저장
    """
    __tablename__ = "startup_companies"

    id = Column(Integer, primary_key=True, index=True)

    # 기본 정보
    name_ko = Column(String(200), nullable=False, index=True)  # 한글 기업명
    name_en = Column(String(200), nullable=True)               # 영문 기업명
    industry = Column(String(100), nullable=True)              # 업종/분야
    sub_industry = Column(String(100), nullable=True)          # 세부 분야

    # 연락처 정보 (영업용)
    website = Column(String(500), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)

    # 기업 상세
    founded_year = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)                  # 기업 설명

    # 최근 투자 정보 (요약)
    latest_stage = Column(SQLEnum(InvestmentStage), nullable=True)
    latest_round_date = Column(DateTime, nullable=True)
    total_funding_krw = Column(Float, nullable=True)           # 총 누적 투자금 (억원)

    # 메타데이터
    is_active = Column(Boolean, default=True)
    first_discovered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    investment_rounds = relationship("InvestmentRound", back_populates="company", cascade="all, delete-orphan")
    news = relationship("InvestmentNews", back_populates="company", cascade="all, delete-orphan")
    email_templates = relationship("EmailTemplate", back_populates="company", cascade="all, delete-orphan")


class InvestmentRound(Base):
    """
    Table 2: 투자 라운드 정보
    각 투자 라운드의 상세 정보
    """
    __tablename__ = "investment_rounds"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("startup_companies.id", ondelete="CASCADE"), nullable=False)

    # 투자 라운드 정보
    stage = Column(SQLEnum(InvestmentStage), nullable=False)   # 투자 단계
    round_date = Column(DateTime, nullable=True)               # 투자 일자

    # 금액 정보 (억원 단위)
    investment_amount_krw = Column(Float, nullable=True)       # 투자 금액
    valuation_pre_krw = Column(Float, nullable=True)           # Pre-money 밸류에이션
    valuation_post_krw = Column(Float, nullable=True)          # Post-money 밸류에이션

    # 투자자 정보
    lead_investor = Column(String(200), nullable=True)         # 리드 투자자
    investors = Column(JSON, nullable=True)                    # 참여 투자자 목록 [{"name": "", "type": "VC/Angel"}]

    # 상세 정보
    remarks = Column(Text, nullable=True)                      # 비고
    source_url = Column(String(1000), nullable=True)           # 출처 URL

    # Relationships
    company = relationship("StartupCompany", back_populates="investment_rounds")


class InvestmentNews(Base):
    """
    Table 3: 투자 뉴스 원문 및 AI 추출 데이터
    크롤링한 뉴스와 AI 파싱 결과
    """
    __tablename__ = "investment_news"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("startup_companies.id", ondelete="SET NULL"), nullable=True)
    collection_id = Column(Integer, ForeignKey("weekly_collections.id", ondelete="SET NULL"), nullable=True)

    # 뉴스 원문 정보
    source = Column(String(100), nullable=False)               # 출처 (naver, platum, venturesquare)
    source_url = Column(String(1000), nullable=False, unique=True)  # 원문 URL
    title = Column(String(500), nullable=False)                # 뉴스 제목
    content = Column(Text, nullable=True)                      # 뉴스 본문
    published_at = Column(DateTime, nullable=True)             # 발행일
    author = Column(String(200), nullable=True)                # 작성자

    # AI 추출 데이터 (Gemini)
    ai_summary = Column(Text, nullable=True)                   # AI 요약
    ai_extracted_data = Column(JSON, nullable=True)            # AI 추출 구조화 데이터
    # {
    #   "company_name": "",
    #   "investment_amount": 0,
    #   "valuation": 0,
    #   "stage": "",
    #   "investors": [],
    #   "industry": ""
    # }

    # 처리 상태
    is_processed = Column(Boolean, default=False)              # AI 처리 완료 여부
    processing_error = Column(Text, nullable=True)             # 처리 오류 메시지

    # Relationships
    company = relationship("StartupCompany", back_populates="news")
    collection = relationship("WeeklyCollection", back_populates="news")


class EmailTemplate(Base):
    """
    Table 4: AI 생성 이메일 템플릿
    Claude로 생성한 맞춤형 영업 이메일
    """
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("startup_companies.id", ondelete="CASCADE"), nullable=False)

    # 이메일 내용
    subject = Column(String(500), nullable=False)              # 이메일 제목
    body = Column(Text, nullable=False)                        # 이메일 본문

    # 생성 정보
    template_type = Column(String(50), default="initial")      # 템플릿 유형 (initial, follow_up)
    generation_prompt = Column(Text, nullable=True)            # 생성에 사용된 프롬프트

    # 메타데이터
    version = Column(Integer, default=1)                       # 버전 번호
    is_active = Column(Boolean, default=True)                  # 활성화 여부

    # Relationships
    company = relationship("StartupCompany", back_populates="email_templates")


class WeeklyCollection(Base):
    """
    Table 5: 주간 수집 작업 이력
    매주 일요일 수집 작업의 기록
    """
    __tablename__ = "weekly_collections"

    id = Column(Integer, primary_key=True, index=True)

    # 수집 정보
    collection_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    week_number = Column(Integer, nullable=False)              # 연도 내 주차
    year = Column(Integer, nullable=False)

    # 상태
    status = Column(SQLEnum(CollectionStatus), default=CollectionStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 수집 통계
    total_news_crawled = Column(Integer, default=0)            # 크롤링한 뉴스 수
    total_companies_found = Column(Integer, default=0)         # 발견한 기업 수
    new_companies_added = Column(Integer, default=0)           # 신규 추가 기업 수
    emails_generated = Column(Integer, default=0)              # 생성된 이메일 수

    # 오류 정보
    error_count = Column(Integer, default=0)                   # 오류 발생 수
    error_log = Column(JSON, nullable=True)                    # 오류 상세 로그

    # Relationships
    news = relationship("InvestmentNews", back_populates="collection")
