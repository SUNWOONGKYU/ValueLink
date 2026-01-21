"""
관리자용 API 라우터

관리자가 접근 가능한 API:
1. 견적서 발송
2. 협의
3. 승인 (계약 확정 + 회계사 배정)
4. 전체 프로젝트 조회
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from auth import get_admin_user, User
from schemas.project import (
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

# 라우터 생성
router = APIRouter(
    prefix="/admin",
    tags=["Admin - 관리자"]
)


@router.post("/projects/{project_id}/quote", response_model=QuoteResponse)
async def send_quote(
    project_id: str,
    request: QuoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    # 1. 견적서 발송

    고객의 평가 신청에 대해 견적서를 작성하여 발송합니다.

    ## 권한
    - 관리자만 가능

    ## 프로세스
    1. 평가법별 비용 및 소요 기간 산정
    2. 총 비용 계산
    3. 견적서 생성
    4. 고객에게 이메일 발송

    ## 상태 변경
    - requested → quote_sent
    """
    try:
        # 프로젝트 확인
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

        # 상태 업데이트
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    # 2. 협의

    고객과 조건 협의를 진행합니다.

    ## 권한
    - 관리자만 가능

    ## 협의 내용
    - 비용 조정
    - 일정 조정
    - 평가법 변경
    - 특별 요구사항

    ## 상태 변경
    - quote_sent → negotiating
    """
    try:
        # 프로젝트 확인
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

        # 상태 업데이트
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    # 3. 승인 (계약 확정 + 회계사 배정)

    고객이 견적을 승인하고 계약을 확정합니다.

    ## 권한
    - 관리자만 가능

    ## 프로세스
    1. 최종 비용 및 일정 확정
    2. 회계사 배정
    3. 계약서 작성
    4. 프로젝트 시작 가능 상태로 변경

    ## 상태 변경
    - negotiating → approved
    """
    try:
        # 프로젝트 확인
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

        # 견적서 확인
        quote = db.query(Quote).filter(Quote.project_id == project_id).first()
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="견적서가 존재하지 않습니다."
            )

        # 최종 비용 및 일정 업데이트
        if request.final_cost:
            quote.total_cost = request.final_cost
        if request.final_completion_date:
            quote.expected_completion_date = request.final_completion_date

        # 프로젝트 상태 및 배정 정보 업데이트
        project.status = "approved"
        project.assigned_accountant = request.assigned_accountant  # 회계사 배정
        project.final_amount = quote.total_cost
        project.contract_signed = True
        project.contract_date = datetime.utcnow().date()

        db.commit()

        return ApprovalResponse(
            project_id=project_id,
            status=project.status,
            final_cost=quote.total_cost,
            final_completion_date=quote.expected_completion_date,
            assigned_accountant=project.assigned_accountant,
            approved_at=datetime.utcnow(),
            message="프로젝트가 승인되었습니다. 고객은 이제 문서를 업로드할 수 있습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"승인 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/projects")
async def list_all_projects(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    # 4. 전체 프로젝트 조회

    모든 프로젝트 목록을 조회합니다.

    ## 권한
    - 관리자만 가능

    ## 필터
    - status: 상태별 필터링
    - skip: 페이지네이션 시작
    - limit: 한 페이지당 개수
    """
    try:
        query = db.query(Project)

        if status:
            query = query.filter(Project.status == status)

        total = query.count()
        projects = query.offset(skip).limit(limit).all()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "projects": [
                {
                    "project_id": p.project_id,
                    "company_name_kr": p.company_name_kr,
                    "status": p.status,
                    "valuation_methods": p.valuation_methods,
                    "created_at": p.created_at,
                    "assigned_accountant": p.assigned_accountant
                }
                for p in projects
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 조회 중 오류가 발생했습니다: {str(e)}"
        )
