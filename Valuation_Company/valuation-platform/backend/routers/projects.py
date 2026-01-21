"""
Projects Router

프로젝트 생명주기 관리:
- POST /projects - 프로젝트 생성
- POST /projects/{project_id}/quote - 견적서 발송
- POST /projects/{project_id}/negotiate - 협의
- POST /projects/{project_id}/approve - 승인
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from schemas.project import (
    ProjectCreateRequest,
    ProjectCreateResponse,
    QuoteRequest,
    QuoteResponse,
    NegotiationRequest,
    NegotiationResponse,
    ApprovalRequest,
    ApprovalResponse
)
from models.project import Project
from models.quote import Quote
from models.negotiation import Negotiation

router = APIRouter()


def generate_project_id(company_code: str, valuation_methods: List[str]) -> str:
    """
    프로젝트 ID 생성
    형식: {5자리 회사코드}-{YYMMDDHHmm}-{2자리 평가법코드}
    """
    now = datetime.now()
    timestamp = now.strftime("%y%m%d%H%M")

    # 평가법 코드 매핑 (순서: 1.DCF평가법 2.상대가치평가법 3.본질가치평가법 4.자산가치평가법 5.상증세법평가법)
    method_codes = {
        "dcf": "DF",                      # 1. DCF평가법
        "relative": "RV",                 # 2. 상대가치평가법
        "capital_market_law": "IV",       # 3. 본질가치평가법 (Intrinsic Value)
        "asset": "AV",                    # 4. 자산가치평가법
        "inheritance_tax_law": "TX"       # 5. 상증세법평가법
    }

    # 여러 평가법이면 첫 번째 평가법 사용
    method_code = method_codes.get(valuation_methods[0], "XX")

    return f"{company_code}-{timestamp}-{method_code}"


@router.post("/projects", response_model=ProjectCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    db: Session = Depends(get_db)
):
    """
    # 1. 프로젝트 생성

    고객이 평가 의뢰를 요청하면 새 프로젝트를 생성합니다.

    ## 주요 기능
    - 프로젝트 ID 자동 생성
    - 회사 정보 및 평가 정보 저장
    - 상태: requested

    ## 필수 입력
    - 회사 기본 정보
    - 평가 방법 (1개 이상)
    - 평가 목적 및 기준일
    """
    try:
        # 사업자번호 중복 체크
        existing = db.query(Project).filter(
            Project.business_number == request.company_info.business_number
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 해당 사업자번호로 등록된 프로젝트가 있습니다."
            )

        # 프로젝트 ID 생성
        project_id = generate_project_id(
            request.company_info.company_code,
            request.valuation_methods
        )

        # 프로젝트 생성
        project = Project(
            project_id=project_id,
            status="requested",
            # Company info
            company_name_kr=request.company_info.company_name_kr,
            company_name_en=request.company_info.company_name_en,
            business_number=request.company_info.business_number,
            ceo_name=request.company_info.ceo_name,
            company_code=request.company_info.company_code,
            industry=request.company_info.industry,
            address=request.company_info.address,
            contact_phone=request.company_info.contact_phone,
            contact_email=request.company_info.contact_email,
            # Evaluation info
            valuation_methods=request.valuation_methods,
            valuation_purpose=request.valuation_purpose,
            valuation_date=request.valuation_date,
            urgency=request.urgency,
            special_notes=request.special_notes
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return ProjectCreateResponse(
            project_id=project.project_id,
            status=project.status,
            company_name_kr=project.company_name_kr,
            valuation_methods=project.valuation_methods,
            created_at=project.created_at,
            message="프로젝트가 성공적으로 생성되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/quote", response_model=QuoteResponse)
async def send_quote(
    project_id: str,
    request: QuoteRequest,
    db: Session = Depends(get_db)
):
    """
    # 2. 견적서 발송

    회계사가 평가 견적서를 작성하여 발송합니다.

    ## 주요 기능
    - 평가법별 비용 및 소요 기간 산정
    - 견적서 생성 및 저장
    - 프로젝트 상태: requested → quote_sent

    ## 필수 입력
    - 평가법별 비용 및 기간
    - 총 비용 및 예상 완료일
    """
    try:
        # 프로젝트 존재 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # 상태 확인
        if project.status != "requested":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"견적서는 'requested' 상태에서만 발송할 수 있습니다. (현재: {project.status})"
            )

        # 견적서 생성
        quote = Quote(
            project_id=project_id,
            method_costs=request.method_costs,
            total_cost=request.total_cost,
            estimated_duration_days=request.estimated_duration_days,
            expected_completion_date=request.expected_completion_date,
            terms_and_conditions=request.terms_and_conditions,
            validity_period_days=request.validity_period_days
        )

        # 프로젝트 상태 업데이트
        project.status = "quote_sent"

        db.add(quote)
        db.commit()
        db.refresh(quote)

        return QuoteResponse(
            quote_id=quote.quote_id,
            project_id=project_id,
            total_cost=quote.total_cost,
            expected_completion_date=quote.expected_completion_date,
            status=project.status,
            created_at=quote.created_at,
            message="견적서가 성공적으로 발송되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"견적서 발송 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/negotiate", response_model=NegotiationResponse)
async def negotiate_quote(
    project_id: str,
    request: NegotiationRequest,
    db: Session = Depends(get_db)
):
    """
    # 3. 협의

    고객과 회계사 간 견적 협의를 진행합니다.

    ## 주요 기능
    - 협의 내역 기록
    - 비용/기간 조정
    - 프로젝트 상태: quote_sent → negotiating

    ## 협의 종료 조건
    - 합의 도달 시: 상태 유지 (negotiating)
    - 고객이 승인하면 다음 단계로 진행
    """
    try:
        # 프로젝트 존재 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # 상태 확인
        if project.status not in ["quote_sent", "negotiating"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"협의는 'quote_sent' 또는 'negotiating' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 협의 내역 생성
        negotiation = Negotiation(
            project_id=project_id,
            requester=request.requester,
            request_type=request.request_type,
            content=request.content,
            proposed_cost=request.proposed_cost,
            proposed_duration_days=request.proposed_duration_days
        )

        # 프로젝트 상태 업데이트
        if project.status != "negotiating":
            project.status = "negotiating"

        db.add(negotiation)
        db.commit()
        db.refresh(negotiation)

        return NegotiationResponse(
            negotiation_id=negotiation.negotiation_id,
            project_id=project_id,
            status=project.status,
            created_at=negotiation.created_at,
            message="협의 내역이 저장되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"협의 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/approve", response_model=ApprovalResponse)
async def approve_project(
    project_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    # 4. 고객 승인

    고객이 최종 견적을 승인합니다.

    ## 주요 기능
    - 최종 비용 및 일정 확정
    - 프로젝트 상태: negotiating → approved
    - 다음 단계: 문서 업로드 대기

    ## 필수 입력
    - 최종 합의 비용
    - 최종 완료 예정일
    """
    try:
        # 프로젝트 존재 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # 상태 확인
        if project.status not in ["quote_sent", "negotiating"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"승인은 'quote_sent' 또는 'negotiating' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 최종 견적 정보가 있는지 확인
        quote = db.query(Quote).filter(Quote.project_id == project_id).first()
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="견적서가 존재하지 않습니다."
            )

        # 최종 비용 및 일정 업데이트 (협의를 통해 변경되었을 수 있음)
        if request.final_cost:
            quote.total_cost = request.final_cost
        if request.final_completion_date:
            quote.expected_completion_date = request.final_completion_date

        # 프로젝트 상태 업데이트
        project.status = "approved"

        db.commit()

        return ApprovalResponse(
            project_id=project_id,
            status=project.status,
            final_cost=quote.total_cost,
            final_completion_date=quote.expected_completion_date,
            approved_at=datetime.utcnow(),
            message="프로젝트가 승인되었습니다. 문서를 업로드해주세요."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"승인 처리 중 오류가 발생했습니다: {str(e)}"
        )
