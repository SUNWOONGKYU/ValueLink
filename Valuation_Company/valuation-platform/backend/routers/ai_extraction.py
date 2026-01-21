"""
AI Extraction Router

AI 데이터 추출:
- POST /projects/{project_id}/extract - AI로 문서에서 데이터 추출
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import get_db
from schemas.ai_extraction import AIExtractionRequest, AIExtractionResponse
from models.project import Project
from models.document import Document

router = APIRouter()


async def extract_data_with_ai(documents: list, extraction_target: str) -> Dict[str, Any]:
    """
    AI를 사용하여 문서에서 데이터 추출

    TODO: 실제 AI 엔진 연동 필요
    - OpenAI GPT-4 Vision API
    - Claude API
    - 또는 커스텀 OCR + NLP 파이프라인

    현재는 더미 데이터 반환
    """
    # TODO: 실제 AI 추출 로직 구현
    dummy_extracted_data = {
        "financial_data": {
            "revenue": {
                "2023": 1000000000,
                "2022": 800000000,
                "2021": 600000000
            },
            "operating_income": {
                "2023": 150000000,
                "2022": 120000000,
                "2021": 90000000
            },
            "net_income": {
                "2023": 100000000,
                "2022": 80000000,
                "2021": 60000000
            }
        },
        "balance_sheet": {
            "total_assets": 5000000000,
            "total_liabilities": 3000000000,
            "total_equity": 2000000000
        },
        "market_data": {
            "competitors": ["경쟁사A", "경쟁사B", "경쟁사C"],
            "market_share": 15.5
        }
    }

    return dummy_extracted_data


@router.post("/projects/{project_id}/extract", response_model=AIExtractionResponse)
async def extract_data_from_documents(
    project_id: str,
    request: AIExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    # 6. AI 데이터 추출

    업로드된 문서에서 AI를 사용하여 평가에 필요한 데이터를 자동 추출합니다.

    ## 주요 기능
    - OCR + NLP로 재무 데이터 추출
    - 재무제표, 감사보고서, 사업계획서 분석
    - 프로젝트 상태: documents_uploaded → collecting

    ## 추출 대상
    - financial_data: 재무 데이터 (매출, 영업이익, 순이익)
    - balance_sheet: 재무상태표 (자산, 부채, 자본)
    - market_data: 시장 데이터 (경쟁사, 시장점유율)
    - business_plan: 사업계획 (성장률, 투자계획)

    ## AI 엔진
    - OpenAI GPT-4 Vision API (문서 이미지 분석)
    - Claude API (재무 데이터 해석)
    - 커스텀 OCR 엔진 (한글 최적화)
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
        if project.status != "documents_uploaded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"데이터 추출은 'documents_uploaded' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 업로드된 문서 확인
        documents = db.query(Document).filter(
            Document.project_id == project_id
        ).all()

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="업로드된 문서가 없습니다."
            )

        # AI로 데이터 추출
        extracted_data = await extract_data_with_ai(
            documents,
            request.extraction_target
        )

        # 프로젝트 상태 업데이트
        project.status = "collecting"

        db.commit()

        return AIExtractionResponse(
            project_id=project_id,
            extracted_data=extracted_data,
            extraction_target=request.extraction_target,
            status=project.status,
            confidence_score=0.95,  # TODO: 실제 신뢰도 점수
            message="데이터가 성공적으로 추출되었습니다. 검토 후 계산을 진행하세요."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 추출 중 오류가 발생했습니다: {str(e)}"
        )
