"""
Project management schemas

프로젝트 생성, 견적, 협의, 승인 관련 스키마
"""

from typing import Optional, List, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr

from .common import CompanyInfo, ContactInfo, ValuationInfo, ProjectStatusCode, ValuationMethodCode


# ========================================
# 1. 프로젝트 생성 (POST /projects)
# ========================================

class ProjectCreateRequest(BaseModel):
    """프로젝트 생성 요청"""
    company_info: CompanyInfo
    contact: ContactInfo
    valuation: ValuationInfo

    class Config:
        json_schema_extra = {
            "example": {
                "company_info": {
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
                },
                "contact": {
                    "name": "김담당",
                    "email": "contact@samsung.com",
                    "phone": "02-1234-5678"
                },
                "valuation": {
                    "methods": ["dcf", "relative", "asset"],
                    "purpose": "MA",
                    "valuation_date": "2025-01-01",
                    "requirements": "특별 고려사항"
                }
            }
        }


class ProjectCreateResponse(BaseModel):
    """프로젝트 생성 응답"""
    project_id: str = Field(..., description="프로젝트 ID (예: SAMSU-2501191430-CP)")
    status: ProjectStatusCode = Field(..., description="프로젝트 상태")
    created_at: datetime = Field(..., description="생성 시각")
    customer_portal_url: str = Field(..., description="고객 포털 URL")
    methods: List[ValuationMethodCode] = Field(..., description="선택된 평가법 목록")
    message: str = Field(..., description="안내 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "requested",
                "created_at": "2026-01-19T14:30:00Z",
                "customer_portal_url": "https://valuelink.com/portal/SAMSU-2501191430-CP",
                "methods": ["dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"],
                "message": "평가 신청이 접수되었습니다. 견적서를 발송해드리겠습니다."
            }
        }


# ========================================
# 2. 견적서 발송 (POST /projects/{project_id}/quote)
# ========================================

class QuoteRequest(BaseModel):
    """견적서 발송 요청"""
    quote_amount: int = Field(..., description="견적 금액 (KRW)", gt=0)
    currency: str = Field(default="KRW", description="통화")
    estimated_duration: str = Field(..., description="예상 소요 기간 (예: '7 days')")
    payment_terms: str = Field(..., description="결제 조건")
    included_services: List[str] = Field(..., description="포함 서비스 목록")
    valid_until: date = Field(..., description="견적 유효 기간")
    notes: Optional[str] = Field(None, description="비고")

    class Config:
        json_schema_extra = {
            "example": {
                "quote_amount": 1500000,
                "currency": "KRW",
                "estimated_duration": "7 days",
                "payment_terms": "계약금 50% + 완료 후 50%",
                "included_services": [
                    "5가지 평가법 종합 평가",
                    "80페이지 종합 보고서",
                    "민감도 분석",
                    "1회 무료 수정"
                ],
                "valid_until": "2026-01-27",
                "notes": "추가 요청사항이 있으시면 협의 가능합니다."
            }
        }


class QuoteResponse(BaseModel):
    """견적서 발송 응답"""
    project_id: str
    status: ProjectStatusCode
    quote_id: str = Field(..., description="견적서 ID")
    quote_url: str = Field(..., description="견적서 다운로드 URL")
    sent_at: datetime
    valid_until: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "quote_sent",
                "quote_id": "QT-SAMSU-001",
                "quote_url": "https://valuelink.com/quotes/QT-SAMSU-001.pdf",
                "sent_at": "2026-01-19T15:00:00Z",
                "valid_until": "2026-01-27T00:00:00Z"
            }
        }


# ========================================
# 3. 조건 협의 (POST /projects/{project_id}/negotiate)
# ========================================

class NegotiationRequest(BaseModel):
    """조건 협의 요청"""
    negotiation_type: Literal["price_adjustment", "scope_change", "timeline_change"] = Field(
        ..., description="협의 유형"
    )
    proposed_amount: Optional[int] = Field(None, description="제안 금액")
    proposed_scope: Optional[List[ValuationMethodCode]] = Field(None, description="제안 범위")
    message: str = Field(..., description="협의 메시지")
    requester: Literal["customer", "admin"] = Field(..., description="요청자")

    class Config:
        json_schema_extra = {
            "example": {
                "negotiation_type": "price_adjustment",
                "proposed_amount": 1200000,
                "proposed_scope": ["dcf", "relative", "asset"],
                "message": "예산 내에서 3가지 평가법으로 조정 가능할까요?",
                "requester": "customer"
            }
        }


class NegotiationResponse(BaseModel):
    """조건 협의 응답"""
    project_id: str
    status: ProjectStatusCode
    negotiation_id: str = Field(..., description="협의 ID")
    updated_at: datetime
    pending_response_from: Literal["customer", "admin"]

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "negotiating",
                "negotiation_id": "NEG-001",
                "updated_at": "2026-01-19T16:00:00Z",
                "pending_response_from": "admin"
            }
        }


# ========================================
# 4. 계약 확정 및 회계사 배정 (POST /projects/{project_id}/approve)
# ========================================

class AccountantInfo(BaseModel):
    """회계사 정보"""
    email: EmailStr
    name: str
    specialization: Optional[List[str]] = None


class ApprovalRequest(BaseModel):
    """계약 확정 요청"""
    final_amount: int = Field(..., description="최종 금액", gt=0)
    final_scope: List[ValuationMethodCode] = Field(..., description="최종 평가법 범위")
    payment_terms: str = Field(..., description="결제 조건")
    assigned_accountant: EmailStr = Field(..., description="배정 회계사 이메일")
    reviewer: EmailStr = Field(..., description="검토자 이메일")
    contract_signed: bool = Field(..., description="계약서 서명 여부")
    contract_date: date = Field(..., description="계약일")

    class Config:
        json_schema_extra = {
            "example": {
                "final_amount": 1500000,
                "final_scope": ["dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"],
                "payment_terms": "계약금 50% + 완료 후 50%",
                "assigned_accountant": "kim@company.com",
                "reviewer": "choi@company.com",
                "contract_signed": True,
                "contract_date": "2026-01-20"
            }
        }


class ApprovalResponse(BaseModel):
    """계약 확정 응답"""
    project_id: str
    status: ProjectStatusCode
    assigned_accountant: AccountantInfo
    reviewer: AccountantInfo
    approved_at: datetime
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "approved",
                "assigned_accountant": {
                    "email": "kim@company.com",
                    "name": "김회계사",
                    "specialization": ["DCF", "상대가치"]
                },
                "reviewer": {
                    "email": "choi@company.com",
                    "name": "최검토자"
                },
                "approved_at": "2026-01-20T10:00:00Z",
                "message": "계약이 확정되었습니다. 고객님께서 자료를 업로드해주시기 바랍니다."
            }
        }
