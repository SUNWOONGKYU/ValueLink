"""
Approvals Router

22개 판단 포인트 관리:
- GET /projects/{project_id}/approval-points - 판단 포인트 목록 조회
- POST /projects/{project_id}/approval-points/{point_id}/approve - 개별 승인
- POST /projects/{project_id}/approval-points/batch-approve - 일괄 승인
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from schemas.approval import (
    ApprovalPointsListResponse,
    ApprovalPoint as ApprovalPointSchema,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    BatchApprovalRequest,
    BatchApprovalResponse
)
from models.project import Project
from models.approval_point import ApprovalPoint

router = APIRouter()


@router.get("/projects/{project_id}/approval-points", response_model=ApprovalPointsListResponse)
async def list_approval_points(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    # 8-1. 판단 포인트 목록 조회

    AI가 제안한 22개 판단 포인트를 조회합니다.

    ## 22개 판단 포인트
    ### 재무 관련 (12개)
    - JP001: 매출 성장률
    - JP002: 영업이익률
    - JP003: WACC (가중평균자본비용)
    - JP004: 할인율
    - JP005: 영구성장률
    - JP006: 추정 기간
    - JP007: 운전자본 가정
    - JP008: CAPEX 가정
    - JP009: 법인세율
    - JP010: 순차입금 조정
    - JP011: 비영업자산 처리
    - JP012: 소수주주지분 처리

    ### 시장 관련 (4개)
    - JP013: 유사 기업 선정
    - JP014: PER 배수 선택
    - JP015: PBR 배수 선택
    - JP016: EV/EBITDA 배수 선택

    ### 자산 관련 (3개)
    - JP017: 자산 재평가 필요 여부
    - JP018: 무형자산 평가
    - JP019: 부채 조정

    ### 법률 관련 (3개)
    - JP020: 본질가치평가법 조정계수
    - JP021: 상증세법평가법 가중치 (순자산:수익)
    - JP022: 할증/할인율 적용

    ## 응답
    - AI 제안값 (ai_value)
    - AI 근거 (ai_rationale)
    - 회계사 결정 (human_decision)
    - 커스텀 값 (custom_value)
    """
    try:
        # 프로젝트 존재 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # 판단 포인트 조회
        approval_points = db.query(ApprovalPoint).filter(
            ApprovalPoint.project_id == project_id
        ).all()

        if not approval_points:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="판단 포인트가 생성되지 않았습니다."
            )

        # 응답 데이터 생성
        points_data = [
            ApprovalPointSchema(
                point_id=ap.point_id,
                point_name=ap.point_name,
                display_name=ap.display_name,
                category=ap.category,
                importance=ap.importance,
                valuation_method=ap.valuation_method,
                ai_value=ap.ai_value,
                ai_rationale=ap.ai_rationale,
                suggested_range=ap.suggested_range,
                human_decision=ap.human_decision,
                custom_value=ap.custom_value,
                approved_by=ap.approved_by,
                approved_at=ap.approved_at
            )
            for ap in approval_points
        ]

        # 통계
        total = len(points_data)
        approved = sum(1 for p in points_data if p.human_decision == "approved")
        rejected = sum(1 for p in points_data if p.human_decision == "rejected")
        pending = sum(1 for p in points_data if p.human_decision is None or p.human_decision == "pending")

        return ApprovalPointsListResponse(
            project_id=project_id,
            approval_points=points_data,
            total_points=total,
            approved_count=approved,
            rejected_count=rejected,
            pending_count=pending
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"판단 포인트 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/projects/{project_id}/approval-points/{point_id}/approve",
    response_model=ApprovalDecisionResponse
)
async def approve_point(
    project_id: str,
    point_id: str,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db)
):
    """
    # 8-2. 개별 판단 포인트 승인

    회계사가 개별 판단 포인트를 검토하고 승인/거부합니다.

    ## 결정 옵션
    - **approved**: AI 제안을 그대로 승인
    - **custom**: 커스텀 값을 입력하여 승인
    - **rejected**: 거부 (사유 필수)

    ## 영향도 분석
    - 변경 시 최종 기업가치에 미치는 영향을 자동 계산
    - 민감도 분석 결과 제공
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
        if project.status != "human_approval":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"판단 포인트 승인은 'human_approval' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 판단 포인트 조회
        approval_point = db.query(ApprovalPoint).filter(
            ApprovalPoint.project_id == project_id,
            ApprovalPoint.point_id == point_id
        ).first()

        if not approval_point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"판단 포인트를 찾을 수 없습니다: {point_id}"
            )

        # 결정 업데이트
        approval_point.human_decision = request.decision
        approval_point.custom_value = request.custom_value
        approval_point.approval_rationale = request.rationale
        approval_point.status = request.decision
        approval_point.approved_by = request.approved_by
        approval_point.approved_at = datetime.utcnow()

        # TODO: 영향도 분석 계산
        impact_analysis = {
            "value_change": 0,  # 기업가치 변화
            "value_change_percent": 0,  # 변화율
            "affected_methods": []  # 영향받는 평가법
        }
        approval_point.impact_analysis = impact_analysis

        db.commit()
        db.refresh(approval_point)

        return ApprovalDecisionResponse(
            project_id=project_id,
            point_id=point_id,
            decision=approval_point.human_decision,
            final_value=approval_point.custom_value or approval_point.ai_value,
            impact_analysis=impact_analysis,
            approved_at=approval_point.approved_at,
            message="판단 포인트가 처리되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"판단 포인트 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/approval-points/batch-approve", response_model=BatchApprovalResponse)
async def batch_approve_points(
    project_id: str,
    request: BatchApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    # 8-3. 일괄 승인

    여러 판단 포인트를 한 번에 승인합니다.

    ## 사용 시나리오
    - AI 제안을 대부분 승인하는 경우
    - 특정 카테고리를 일괄 승인하는 경우
    - 중요도가 낮은 항목을 빠르게 처리하는 경우

    ## 처리 결과
    - 성공/실패 개수
    - 실패한 항목의 상세 오류
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
        if project.status != "human_approval":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"판단 포인트 승인은 'human_approval' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 각 결정 처리
        success_count = 0
        failed_count = 0
        errors = []

        for decision in request.decisions:
            try:
                approval_point = db.query(ApprovalPoint).filter(
                    ApprovalPoint.project_id == project_id,
                    ApprovalPoint.point_id == decision.point_id
                ).first()

                if not approval_point:
                    failed_count += 1
                    errors.append({
                        "point_id": decision.point_id,
                        "error": "판단 포인트를 찾을 수 없습니다."
                    })
                    continue

                # 결정 업데이트
                approval_point.human_decision = decision.decision
                approval_point.custom_value = decision.custom_value
                approval_point.approval_rationale = decision.rationale
                approval_point.status = decision.decision
                approval_point.approved_by = request.approved_by
                approval_point.approved_at = datetime.utcnow()

                success_count += 1

            except Exception as e:
                failed_count += 1
                errors.append({
                    "point_id": decision.point_id,
                    "error": str(e)
                })

        db.commit()

        # 모든 판단 포인트가 처리되었는지 확인
        pending_points = db.query(ApprovalPoint).filter(
            ApprovalPoint.project_id == project_id,
            ApprovalPoint.status == "pending"
        ).count()

        # 모두 처리되었으면 상태를 draft_generated로 변경
        if pending_points == 0:
            project.status = "draft_generated"
            db.commit()
            message = f"{success_count}개 항목이 승인되었습니다. 초안 생성을 진행하세요."
        else:
            message = f"{success_count}개 항목이 승인되었습니다. (대기 중: {pending_points}개)"

        return BatchApprovalResponse(
            project_id=project_id,
            success_count=success_count,
            failed_count=failed_count,
            errors=errors if errors else None,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일괄 승인 처리 중 오류가 발생했습니다: {str(e)}"
        )
