"""
Revisions Router

수정 요청 관리:
- POST /projects/{project_id}/revisions - 수정 요청
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.revision import RevisionRequest, RevisionResponse
from models.project import Project
from models.revision import Revision

router = APIRouter()


@router.post("/projects/{project_id}/revisions", response_model=RevisionResponse)
async def request_revision(
    project_id: str,
    request: RevisionRequest,
    db: Session = Depends(get_db)
):
    """
    # 10. 수정 요청 (선택 사항)

    고객이 초안을 검토한 후 수정을 요청합니다.

    ## 주요 기능
    - 수정 요청 사항 기록
    - 프로젝트 상태: draft_generated → revision_requested
    - 회계사가 수정 후 다시 초안 생성

    ## 수정 요청 유형
    - **calculation**: 계산 수정 (가정, 데이터 오류)
    - **content**: 내용 수정 (설명, 표현)
    - **format**: 형식 수정 (레이아웃, 디자인)
    - **data**: 데이터 수정 (오탈자, 정보 추가)

    ## 프로세스
    1. 고객이 수정 요청
    2. 상태: draft_generated → revision_requested
    3. 회계사가 수정 작업 수행
    4. 수정 완료 후 다시 초안 생성 (POST /draft)
    5. 최종 승인 시 완료 처리 (POST /finalize)

    ## 수정 이력
    - 모든 수정 요청은 revision 테이블에 기록
    - 수정 전/후 비교 가능
    - 변경 사항 추적
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
                detail=f"수정 요청은 'draft_generated' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 수정 요청 생성
        revision = Revision(
            project_id=project_id,
            revision_type=request.revision_type,
            description=request.description,
            specific_sections=request.specific_sections,
            requested_by=request.requested_by,
            urgency=request.urgency
        )

        db.add(revision)

        # 프로젝트 상태 업데이트
        project.status = "revision_requested"

        db.commit()
        db.refresh(revision)

        return RevisionResponse(
            project_id=project_id,
            revision_id=revision.revision_id,
            revision_type=revision.revision_type,
            status=project.status,
            requested_at=revision.requested_at,
            message="수정 요청이 접수되었습니다. 회계사가 검토 후 수정하겠습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"수정 요청 처리 중 오류가 발생했습니다: {str(e)}"
        )
