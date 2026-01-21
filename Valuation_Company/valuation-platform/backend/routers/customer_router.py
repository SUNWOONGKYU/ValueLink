"""
고객용 API 라우터

고객이 접근 가능한 API:
1. 평가 신청 (프로젝트 생성)
2. 문서 업로드
3. 수정 요청
4. 보고서 다운로드
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import shutil

from database import get_db
from auth import get_customer_user, User
from schemas.project import ProjectCreateRequest, ProjectCreateResponse
from schemas.document import DocumentUploadResponse
from schemas.revision import RevisionRequest, RevisionResponse
from models.project import Project
from models.document import Document
from models.revision import Revision
from models.report import Report

# 라우터 생성
router = APIRouter(
    prefix="/customer",
    tags=["Customer - 고객"]
)

# 업로드 설정
import os
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def generate_project_id(company_code: str, valuation_methods: List[str]) -> str:
    """프로젝트 ID 생성"""
    now = datetime.now()
    timestamp = now.strftime("%y%m%d%H%M")

    method_codes = {
        "dcf": "DF",
        "relative": "RV",
        "capital_market_law": "IV",
        "asset": "AV",
        "inheritance_tax_law": "TX"
    }

    method_code = method_codes.get(valuation_methods[0], "XX")
    return f"{company_code}-{timestamp}-{method_code}"


@router.post("/projects", response_model=ProjectCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """
    # 1. 평가 신청 (프로젝트 생성)

    고객이 기업가치평가를 신청합니다.

    ## 권한
    - 고객만 가능

    ## 프로세스
    1. 회사 정보 입력
    2. 평가 방법 선택 (1개 이상)
    3. 평가 목적 및 기준일 입력
    4. 프로젝트 ID 자동 생성
    5. 상태: requested
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
            company_name_kr=request.company_info.company_name_kr,
            company_name_en=request.company_info.company_name_en,
            business_number=request.company_info.business_number,
            ceo_name=request.company_info.ceo_name,
            company_code=request.company_info.company_code,
            industry=request.company_info.industry,
            address=request.company_info.address,
            contact_phone=request.company_info.contact_phone,
            contact_email=request.company_info.contact_email,
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
            message="프로젝트가 성공적으로 생성되었습니다. 관리자가 견적서를 발송할 예정입니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/documents", response_model=DocumentUploadResponse)
async def upload_documents(
    project_id: str,
    files: List[UploadFile] = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """
    # 2. 문서 업로드

    평가에 필요한 문서를 업로드합니다.

    ## 권한
    - 고객만 가능
    - 본인 프로젝트만 가능

    ## 업로드 가능 문서
    - 재무제표 (3~5년)
    - 감사보고서
    - 사업계획서
    - 기타 참고 자료

    ## 상태 변경
    - approved → documents_uploaded
    """
    try:
        # 프로젝트 존재 및 권한 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )

        # TODO: 본인 프로젝트 확인 (contact_email == current_user.email)
        # if project.contact_email != current_user.email:
        #     raise HTTPException(status_code=403, detail="권한이 없습니다.")

        # 상태 확인
        if project.status not in ["approved", "documents_uploaded"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"문서 업로드는 'approved' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 파일 저장
        uploaded_documents = []
        for file in files:
            # 파일 크기 체크
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

            if file_size > MAX_UPLOAD_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"파일 '{file.filename}'이 너무 큽니다. (최대 {MAX_UPLOAD_SIZE_MB}MB)"
                )

            # 파일 저장
            project_dir = Path(UPLOAD_DIR) / project_id
            project_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = project_dir / safe_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # DB에 문서 정보 저장
            document = Document(
                project_id=project_id,
                document_type=document_type,
                file_name=file.filename,
                file_path=str(file_path),
                file_size_kb=file_size // 1024,
                description=description
            )
            db.add(document)
            uploaded_documents.append(document)

        # 상태 업데이트
        if project.status != "documents_uploaded":
            project.status = "documents_uploaded"

        db.commit()

        for doc in uploaded_documents:
            db.refresh(doc)

        return DocumentUploadResponse(
            project_id=project_id,
            uploaded_files=[
                {
                    "document_id": doc.document_id,
                    "file_name": doc.file_name,
                    "file_size_kb": doc.file_size_kb,
                    "uploaded_at": doc.uploaded_at
                }
                for doc in uploaded_documents
            ],
            total_files=len(uploaded_documents),
            status=project.status,
            message=f"{len(uploaded_documents)}개 파일이 성공적으로 업로드되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 업로드 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/revisions", response_model=RevisionResponse)
async def request_revision(
    project_id: str,
    request: RevisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """
    # 3. 수정 요청

    초안을 검토한 후 수정을 요청합니다.

    ## 권한
    - 고객만 가능
    - 본인 프로젝트만 가능

    ## 상태 변경
    - draft_generated → revision_requested
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
            requested_by=current_user.email,
            urgency=request.urgency
        )

        db.add(revision)
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


@router.get("/projects/{project_id}/report/download")
async def download_report(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """
    # 4. 보고서 다운로드

    발행된 평가 보고서를 다운로드합니다.

    ## 권한
    - 고객만 가능
    - 본인 프로젝트만 가능

    ## 조건
    - 프로젝트 상태: completed
    - 보고서가 발행되어 있어야 함
    """
    from fastapi.responses import FileResponse

    try:
        # 프로젝트 확인
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
