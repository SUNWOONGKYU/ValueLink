"""
Drafts Router

초안 생성:
- POST /projects/{project_id}/draft - 초안 생성
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from schemas.draft import DraftGenerateRequest, DraftGenerateResponse
from models.project import Project
from models.draft import Draft
from models.valuation_result import ValuationResult
from models.approval_point import ApprovalPoint

router = APIRouter()


async def generate_report_content(
    project: Project,
    valuation_results: list,
    approval_points: list,
    draft_config: dict
) -> dict:
    """
    보고서 초안 콘텐츠 생성

    TODO: 실제 보고서 생성 로직 구현
    - 템플릿 엔진 (Jinja2)
    - PDF 생성 (ReportLab)
    - Word 문서 생성 (python-docx)
    """
    # TODO: 실제 보고서 생성 로직
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

    return draft_content


@router.post("/projects/{project_id}/draft", response_model=DraftGenerateResponse)
async def generate_draft(
    project_id: str,
    request: DraftGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    # 9. 초안 생성

    평가 결과와 판단 포인트를 기반으로 보고서 초안을 생성합니다.

    ## 주요 기능
    - 평가 결과 요약
    - 회계사 결정 사항 반영
    - PDF/Word 형식 초안 생성
    - 프로젝트 상태: human_approval → draft_generated

    ## 초안 구성
    1. **요약 (Executive Summary)**
       - 평가 대상 기업 개요
       - 평가 결과 요약
       - 가치 범위

    2. **기업 개요 (Company Overview)**
       - 기본 정보
       - 사업 내용
       - 재무 현황

    3. **평가 방법론 (Valuation Methodology)**
       - 사용된 평가 방법
       - 주요 가정
       - 계산 과정

    4. **평가 결과 (Valuation Results)**
       - 방법별 평가액
       - 가중평균 또는 최종 의견
       - 민감도 분석

    5. **부록 (Appendix)**
       - 재무제표
       - 시장 분석
       - 참고 자료

    ## 출력 형식
    - PDF (기본)
    - Word (요청 시)
    - HTML (웹 뷰어용)
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
        draft_content = await generate_report_content(
            project,
            valuation_results,
            approval_points,
            request.draft_config
        )

        # 초안 저장
        draft = Draft(
            project_id=project_id,
            draft_version=1,
            content=draft_content,
            format=request.format,
            generated_by=request.generated_by or "system"
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
            preview_url=f"/api/projects/{project_id}/draft/{draft.draft_id}/preview",
            download_url=f"/api/projects/{project_id}/draft/{draft.draft_id}/download",
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
