"""
Common Pydantic schemas

공통으로 사용되는 스키마 정의
"""

from typing import Optional, List, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr


# ========================================
# 회사 정보
# ========================================

class CompanyInfo(BaseModel):
    """회사 기본 정보"""
    company_name_kr: str = Field(..., description="회사명 (한글)")
    company_name_en: str = Field(..., description="회사명 (영문)")
    business_number: str = Field(..., description="사업자등록번호", pattern=r'^\d{3}-\d{2}-\d{5}$')
    ceo_name: str = Field(..., description="대표자명")
    industry: str = Field(..., description="업종")
    industry_code: Optional[str] = Field(None, description="업종 코드 (예: C26)")
    founded_date: date = Field(..., description="설립일")
    is_listed: bool = Field(default=False, description="상장 여부")
    ticker: Optional[str] = Field(None, description="종목 코드 (상장사만)")
    shares_outstanding: Optional[int] = Field(None, description="발행 주식 수")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name_kr": "삼성전자",
                "company_name_en": "Samsung Electronics",
                "business_number": "124-81-00998",
                "ceo_name": "이재용",
                "industry": "전자제품 제조업",
                "industry_code": "C26",
                "founded_date": "1969-01-13",
                "is_listed": True,
                "ticker": "005930",
                "shares_outstanding": 5920370000
            }
        }


# ========================================
# 담당자 정보
# ========================================

class ContactInfo(BaseModel):
    """담당자 정보"""
    name: str = Field(..., description="담당자 이름")
    email: EmailStr = Field(..., description="이메일")
    phone: str = Field(..., description="전화번호", pattern=r'^\d{2,3}-\d{3,4}-\d{4}$')

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김담당",
                "email": "contact@samsung.com",
                "phone": "02-1234-5678"
            }
        }


# ========================================
# 평가 정보
# ========================================

# 평가법 코드
# 순서: 1.DCF평가법 2.상대가치평가법 3.본질가치평가법 4.자산가치평가법 5.상증세법평가법
ValuationMethodCode = Literal["dcf", "relative", "capital_market_law", "asset", "inheritance_tax_law"]

# 평가 목적 코드
ValuationPurposeCode = Literal["MA", "IPO", "investment", "merger", "inheritance", "liquidation", "comprehensive"]


class ValuationInfo(BaseModel):
    """평가 정보"""
    methods: List[ValuationMethodCode] = Field(..., description="평가법 목록")
    purpose: ValuationPurposeCode = Field(..., description="평가 목적")
    valuation_date: date = Field(..., description="평가 기준일")
    requirements: Optional[str] = Field(None, description="특별 고려사항")

    class Config:
        json_schema_extra = {
            "example": {
                "methods": ["dcf", "relative", "capital_market_law"],
                "purpose": "MA",
                "valuation_date": "2025-01-01",
                "requirements": "특별 고려사항"
            }
        }


# ========================================
# 프로젝트 상태
# ========================================

ProjectStatusCode = Literal[
    "requested",           # 평가 신청
    "quote_sent",          # 견적 발송
    "negotiating",         # 조건 협의 중
    "approved",            # 승인 완료
    "documents_uploaded",  # 자료 업로드
    "collecting",          # 자료 수집 중
    "evaluating",          # 평가 진행 중
    "human_approval",      # 회계사 승인 대기
    "draft_generated",     # 초안 생성 완료
    "revision_requested",  # 수정 요청
    "completed"            # 최종 확정
]


# ========================================
# 에러 응답
# ========================================

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    details: Optional[dict] = Field(None, description="상세 정보")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시각")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "INVALID_REQUEST",
                "message": "필수 필드가 누락되었습니다.",
                "details": {"missing_fields": ["company_name_kr", "business_number"]},
                "timestamp": "2026-01-20T10:00:00Z"
            }
        }
