"""
회계사용 API 라우터

회계사가 접근 가능한 API:
1. 22개 판단 포인트 조회
2. 판단 포인트 개별 승인
3. 판단 포인트 일괄 승인
4. 초안 생성
5. 최종 확정
6. 보고서 발행
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from auth import get_accountant_user, User
from schemas.approval import (
    ApprovalPointsListResponse,
    ApprovalPoint as ApprovalPointSchema,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    BatchApprovalRequest,
    BatchApprovalResponse
)
from schemas.draft import DraftGenerateRequest, DraftGenerateResponse
from schemas.report import (
    FinalizeRequest,
    FinalizeResponse,
    ReportGenerateRequest,
    ReportGenerateResponse
)
from models.project import Project
from models.approval_point import ApprovalPoint
from models.draft import Draft
from models.report import Report
from models.valuation_result import ValuationResult

# 라우터 생성
router = APIRouter(
    prefix="/accountant",
    tags=["Accountant - 회계사"]
)


@router.get("/projects/{project_id}/approval-points", response_model=ApprovalPointsListResponse)
async def list_approval_points(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_accountant_user)
):
    """
    # 1. 22개 판단 포인트 조회

    AI가 제안한 22개 판단 포인트를 조회합니다.

    ## 권한
    - 회계사만 가능
    - 배정된 프로젝트만 가능

    ## 22개 판단 포인트 카테고리
    - 재무 관련 (12개): JP001-JP012
    - 시장 관련 (4개): JP013-JP016
    - 자산 관련 (3개): JP017-JP019
    - 법률 관련 (3개): JP020-JP022
    """
    try:
        # 프로젝트 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # TODO: 배정된 회계사 확인
        # if project.assigned_accountant != current_user.email:
        #     raise HTTPException(status_code=403, detail="배정된 프로젝트가 아닙니다.")

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_accountant_user)
):
    """
    # 2. 판단 포인트 개별 승인

    개별 판단 포인트를 검토하고 승인/거부/커스텀 값 입력합니다.

    ## 권한
    - 회계사만 가능
    - 배정된 프로젝트만 가능

    ## 결정 옵션
    - approved: AI 제안 그대로 승인
    - custom: 커스텀 값 입력
    - rejected: 거부
    """
    try:
        # 프로젝트 및 판단 포인트 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        if project.status != "human_approval":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"판단 포인트 승인은 'human_approval' 상태에서만 가능합니다. (현재: {project.status})"
            )

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
        approval_point.approved_by = current_user.email
        approval_point.approved_at = datetime.utcnow()

        # TODO: 영향도 분석
        impact_analysis = {
            "value_change": 0,
            "value_change_percent": 0,
            "affected_methods": []
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_accountant_user)
):
    """
    # 3. 판단 포인트 일괄 승인

    여러 판단 포인트를 한 번에 승인합니다.

    ## 권한
    - 회계사만 가능
    """
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        if project.status != "human_approval":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"판단 포인트 승인은 'human_approval' 상태에서만 가능합니다. (현재: {project.status})"
            )

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

                approval_point.human_decision = decision.decision
                approval_point.custom_value = decision.custom_value
                approval_point.approval_rationale = decision.rationale
                approval_point.status = decision.decision
                approval_point.approved_by = current_user.email
                approval_point.approved_at = datetime.utcnow()

                success_count += 1

            except Exception as e:
                failed_count += 1
                errors.append({
                    "point_id": decision.point_id,
                    "error": str(e)
                })

        db.commit()

        # 모든 판단 포인트 처리되었는지 확인
        pending_points = db.query(ApprovalPoint).filter(
            ApprovalPoint.project_id == project_id,
            ApprovalPoint.status == "pending"
        ).count()

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


@router.post("/projects/{project_id}/draft", response_model=DraftGenerateResponse)
async def generate_draft(
    project_id: str,
    request: DraftGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_accountant_user)
):
    """
    # 4. 초안 생성

    평가 결과와 판단 포인트를 기반으로 보고서 초안을 생성합니다.

    ## 권한
    - 회계사만 가능

    ## 상태 변경
    - human_approval → draft_generated

    ## 초안 구성
    1. 요약 (Executive Summary)
    2. 기업 개요 (Company Overview)
    3. 평가 방법론 (Valuation Methodology)
    4. 평가 결과 (Valuation Results)
    5. 부록 (Appendix)
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
                detail=f"초안 생성은 'human_approval' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 모든 판단 포인트가 처리되었는지 확인
        pending_points = db.query(ApprovalPoint).filter(
            ApprovalPoint.project_id == project_id,
            ApprovalPoint.status == "pending"
        ).count()

        if pending_points > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"아직 처리되지 않은 판단 포인트가 {pending_points}개 있습니다."
            )

        # 평가 결과 조회
        valuation_results = db.query(ValuationResult).filter(
            ValuationResult.project_id == project_id
        ).all()

        if not valuation_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="평가 결과가 없습니다."
            )

        # 판단 포인트 조회
        approval_points = db.query(ApprovalPoint).filter(
            ApprovalPoint.project_id == project_id
        ).all()

        # 초안 콘텐츠 생성
        draft_content = {
            "executive_summary": {
                "company_name": project.company_name_kr,
                "valuation_date": str(project.valuation_date),
                "valuation_methods": project.valuation_methods,
                "final_value": 7000000000,  # TODO: 실제 계산값
                "value_range": {
                    "min": 6500000000,
                    "max": 7500000000
                }
            },
            "company_overview": {
                "business_number": project.business_number,
                "ceo": project.ceo_name,
                "industry": project.industry,
                "address": project.address
            },
            "valuation_results": [
                {
                    "method": result.method,
                    "value": result.result.get("equity_value") or result.result.get("enterprise_value"),
                    "key_assumptions": result.key_assumptions
                }
                for result in valuation_results
            ],
            "approval_decisions": [
                {
                    "point_id": ap.point_id,
                    "point_name": ap.point_name,
                    "ai_value": ap.ai_value,
                    "final_value": ap.custom_value or ap.ai_value,
                    "decision": ap.human_decision
                }
                for ap in approval_points
            ],
            "appendix": {
                "financial_statements": [],
                "market_analysis": [],
                "assumptions": []
            }
        }

        # 초안 저장
        draft = Draft(
            project_id=project_id,
            draft_version=1,
            content=draft_content,
            format=request.format,
            generated_by=current_user.email
        )

        db.add(draft)

        # 프로젝트 상태 업데이트
        project.status = "draft_generated"

        db.commit()
        db.refresh(draft)

        return DraftGenerateResponse(
            project_id=project_id,
            draft_id=draft.draft_id,
            draft_version=draft.draft_version,
            format=draft.format,
            preview_url=f"/api/accountant/projects/{project_id}/draft/{draft.draft_id}/preview",
            download_url=f"/api/accountant/projects/{project_id}/draft/{draft.draft_id}/download",
            status=project.status,
            generated_at=draft.generated_at,
            message="초안이 성공적으로 생성되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"초안 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/finalize", response_model=FinalizeResponse)
async def finalize_project(
    project_id: str,
    request: FinalizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_accountant_user)
):
    """
    # 5. 최종 확정

    고객이 초안을 최종 승인한 후 확정합니다.

    ## 권한
    - 회계사만 가능

    ## 상태 변경
    - draft_generated or revision_requested → completed

    ## 확정 조건
    - 초안이 생성되어 있어야 함
    - 수정 요청이 있으면 모두 처리되어야 함
    - 고객이 최종 승인
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
        if project.status not in ["draft_generated", "revision_requested"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"확정은 'draft_generated' 또는 'revision_requested' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 최신 초안 확인
        latest_draft = db.query(Draft).filter(
            Draft.project_id == project_id
        ).order_by(Draft.draft_version.desc()).first()

        if not latest_draft:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="초안이 생성되지 않았습니다."
            )

        # 프로젝트 상태 업데이트
        project.status = "completed"

        db.commit()

        return FinalizeResponse(
            project_id=project_id,
            status=project.status,
            final_draft_id=latest_draft.draft_id,
            finalized_at=datetime.utcnow(),
            message="프로젝트가 최종 확정되었습니다. 보고서를 발행하세요."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"확정 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/report", response_model=ReportGenerateResponse)
async def generate_report(
    project_id: str,
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_accountant_user)
):
    """
    # 6. 보고서 발행

    최종 확정된 내용을 바탕으로 공식 보고서를 발행합니다.

    ## 권한
    - 회계사만 가능

    ## 보고서 번호 형식
    - VR-{YYYY}-{순번 5자리}
    - 예: VR-2024-00123

    ## 보고서 구성
    1. 표지 (Cover Page)
    2. 본문 (Main Content)
    3. 첨부 (Attachments)

    ## 출력 형식
    - PDF (전자 서명 포함)
    - 암호화 옵션
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
        if project.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"보고서 발행은 'completed' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 최신 초안 확인
        latest_draft = db.query(Draft).filter(
            Draft.project_id == project_id
        ).order_by(Draft.draft_version.desc()).first()

        if not latest_draft:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="초안이 생성되지 않았습니다."
            )

        # 보고서 번호 생성
        year = datetime.now().year
        report_count = db.query(Report).filter(
            Report.report_number.like(f"VR-{year}-%")
        ).count()
        report_number = f"VR-{year}-{report_count + 1:05d}"

        # TODO: 실제 보고서 생성 (PDF)
        report_file_path = f"./reports/{project_id}_{report_number}.pdf"

        # 보고서 레코드 생성
        report = Report(
            project_id=project_id,
            draft_id=latest_draft.draft_id,
            report_number=report_number,
            report_file_path=report_file_path,
            format=request.format,
            issued_by=current_user.email,
            digital_signature=request.digital_signature,
            password_protected=request.password_protected
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return ReportGenerateResponse(
            project_id=project_id,
            report_id=report.report_id,
            report_number=report.report_number,
            download_url=f"/api/accountant/projects/{project_id}/report/download",
            issued_at=report.issued_at,
            message="보고서가 발행되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 발행 중 오류가 발생했습니다: {str(e)}"
        )
