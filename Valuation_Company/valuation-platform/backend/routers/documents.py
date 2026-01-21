"""
Documents Router

문서 업로드 관리:
- POST /projects/{project_id}/documents - 문서 업로드
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path

from database import get_db
from schemas.document import DocumentUploadRequest, DocumentUploadResponse
from models.project import Project
from models.document import Document

router = APIRouter()

# 업로드 디렉토리 설정
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def save_uploaded_file(file: UploadFile, project_id: str) -> str:
    """
    업로드된 파일을 서버에 저장

    저장 경로: ./uploads/{project_id}/{timestamp}_{filename}
    """
    # 프로젝트별 디렉토리 생성
    project_dir = Path(UPLOAD_DIR) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # 파일명에 타임스탬프 추가 (중복 방지)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = project_dir / safe_filename

    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)


@router.post("/projects/{project_id}/documents", response_model=DocumentUploadResponse)
async def upload_documents(
    project_id: str,
    files: List[UploadFile] = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    # 5. 문서 업로드

    고객이 평가에 필요한 문서를 업로드합니다.

    ## 주요 기능
    - 재무제표, 감사보고서, 사업계획서 등 업로드
    - 파일 크기 제한 (기본 20MB)
    - 프로젝트 상태: approved → documents_uploaded

    ## 필수 입력
    - 파일 (1개 이상)
    - 문서 유형 (financial_statements, audit_report, business_plan, etc.)

    ## 지원 파일 형식
    - PDF, Excel (xlsx), Word (docx), 이미지 (jpg, png)
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
        if project.status not in ["approved", "documents_uploaded"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"문서 업로드는 'approved' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 파일 크기 확인
        uploaded_documents = []
        for file in files:
            # 파일 크기 체크
            file.file.seek(0, 2)  # 파일 끝으로 이동
            file_size = file.file.tell()  # 현재 위치 = 파일 크기
            file.file.seek(0)  # 다시 처음으로

            if file_size > MAX_UPLOAD_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"파일 '{file.filename}'이 너무 큽니다. (최대 {MAX_UPLOAD_SIZE_MB}MB)"
                )

            # 파일 저장
            file_path = save_uploaded_file(file, project_id)

            # DB에 문서 정보 저장
            document = Document(
                project_id=project_id,
                document_type=document_type,
                file_name=file.filename,
                file_path=file_path,
                file_size_kb=file_size // 1024,
                description=description
            )
            db.add(document)
            uploaded_documents.append(document)

        # 프로젝트 상태 업데이트
        if project.status != "documents_uploaded":
            project.status = "documents_uploaded"

        db.commit()

        # 응답 데이터 생성
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
