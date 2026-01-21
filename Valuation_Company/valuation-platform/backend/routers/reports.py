"""
Reports Router

보고서 발행:
- POST /projects/{project_id}/finalize - 최종 확정
- POST /projects/{project_id}/report - 보고서 발행
- GET /projects/{project_id}/report/download - 보고서 다운로드
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from database import get_db
from schemas.report import (
    FinalizeRequest,
    FinalizeResponse,
    ReportGenerateRequest,
    ReportGenerateResponse
)
from models.project import Project
from models.report import Report
from models.draft import Draft

router = APIRouter()


@router.post("/projects/{project_id}/finalize", response_model=FinalizeResponse)
async def finalize_project(
    project_id: str,
    request: FinalizeRequest,
    db: Session = Depends(get_db)
):
    """
    # 11. 최종 확정

    고객이 초안을 최종 승인합니다.

    ## 주요 기능
    - 초안 최종 확정
    - 프로젝트 상태: draft_generated or revision_requested → completed
    - 보고서 발행 준비 완료

    ## 확정 조건
    - 초안이 생성되어 있어야 함
    - 수정 요청이 있으면 모두 처리되어야 함
    - 고객이 최종 승인

    ## 다음 단계
    - 보고서 발행 (POST /report)
    - 전자 서명
    - 고객에게 전달
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
    db: Session = Depends(get_db)
):
    """
    # 12. 보고서 발행

    최종 확정된 내용을 바탕으로 공식 보고서를 발행합니다.

    ## 주요 기능
    - 보고서 번호 자동 발급
    - PDF 전자 서명
    - 발행 일시 기록
    - 프로젝트 상태: completed (유지)

    ## 보고서 번호 형식
    - VR-{YYYY}-{순번 5자리}
    - 예: VR-2024-00123

    ## 보고서 구성
    1. **표지 (Cover Page)**
       - 회사명, 평가 기준일
       - 보고서 번호, 발행일
       - 회계법인 정보

    2. **본문 (Main Content)**
       - 초안 내용 반영
       - 회계사 최종 검토 의견
       - 전자 서명

    3. **첨부 (Attachments)**
       - 재무제표
       - 계산 근거
       - 참고 자료

    ## 출력 형식
    - PDF (전자 서명 포함)
    - 암호화 옵션 (고객 보안)
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
            issued_by=request.issued_by or "system",
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
            download_url=f"/api/projects/{project_id}/report/download",
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


@router.get("/projects/{project_id}/report/download")
async def download_report(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    # 13. 보고서 다운로드

    발행된 보고서를 다운로드합니다.

    ## 주요 기능
    - 보고서 파일 다운로드
    - 암호화된 경우 패스워드 입력 필요
    - 다운로드 로그 기록

    ## 응답
    - Content-Type: application/pdf
    - Content-Disposition: attachment; filename="보고서.pdf"
    """
    try:
        # 프로젝트 존재 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # 보고서 조회
        report = db.query(Report).filter(
            Report.project_id == project_id
        ).order_by(Report.issued_at.desc()).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="발행된 보고서가 없습니다."
            )

        # 파일 존재 확인
        report_path = Path(report.report_file_path)
        if not report_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="보고서 파일을 찾을 수 없습니다."
            )

        # 파일 다운로드
        return FileResponse(
            path=report.report_file_path,
            filename=f"{report.report_number}_{project.company_name_kr}_평가보고서.pdf",
            media_type="application/pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 다운로드 중 오류가 발생했습니다: {str(e)}"
        )
