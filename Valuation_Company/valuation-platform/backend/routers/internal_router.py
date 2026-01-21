"""
시스템/AI용 API 라우터

시스템 및 AI가 접근하는 내부 API:
1. AI 데이터 추출
2. 평가 계산
3. 통합 평가
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from database import get_db
from auth import get_system_user, User
from schemas.ai_extraction import AIExtractionRequest, AIExtractionResponse
from schemas.calculation import (
    CalculationRequest,
    CalculationResponse,
    IntegratedValuationRequest,
    IntegratedValuationResponse
)
from models.project import Project
from models.document import Document
from models.approval_point import ApprovalPoint
from models.valuation_result import ValuationResult

# 라우터 생성
router = APIRouter(
    prefix="/internal",
    tags=["Internal - 시스템/AI"]
)


@router.post("/projects/{project_id}/extract", response_model=AIExtractionResponse)
async def extract_data(
    project_id: str,
    request: AIExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_system_user)
):
    """
    # AI 데이터 추출

    업로드된 문서에서 평가에 필요한 데이터를 AI로 추출합니다.

    ## 권한
    - 시스템 내부 API만 가능

    ## 추출 데이터
    - 재무제표 (손익계산서, 재무상태표, 현금흐름표)
    - 주요 재무지표 (매출, 영업이익, 당기순이익 등)
    - 자산/부채 항목
    - 시장 정보 (비교 기업, 멀티플 등)

    ## 상태 변경
    - documents_uploaded → collecting
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
        if project.status != "documents_uploaded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AI 추출은 'documents_uploaded' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 업로드된 문서 조회
        documents = db.query(Document).filter(
            Document.project_id == project_id
        ).all()

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="업로드된 문서가 없습니다."
            )

        # TODO: 실제 AI 추출 로직 (Gemini, GPT-4 등)
        # 여기서는 더미 데이터 반환
        extracted_data = {
            "financials": {
                "revenue": [1000000000, 1200000000, 1500000000],
                "operating_income": [100000000, 150000000, 200000000],
                "net_income": [80000000, 120000000, 160000000]
            },
            "assets": {
                "total_assets": 5000000000,
                "current_assets": 2000000000,
                "non_current_assets": 3000000000
            },
            "liabilities": {
                "total_liabilities": 2000000000,
                "current_liabilities": 800000000,
                "non_current_liabilities": 1200000000
            },
            "market_data": {
                "comparable_companies": ["A사", "B사", "C사"],
                "average_per": 15.5,
                "average_pbr": 2.3
            }
        }

        # 프로젝트 상태 업데이트
        project.status = "collecting"

        db.commit()

        return AIExtractionResponse(
            project_id=project_id,
            extracted_data=extracted_data,
            extraction_method=request.extraction_method,
            confidence_score=0.95,
            status=project.status,
            extracted_at=datetime.utcnow(),
            message="데이터 추출이 완료되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 추출 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/calculate", response_model=CalculationResponse)
async def calculate_valuation(
    project_id: str,
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_system_user)
):
    """
    # 평가 계산

    선택된 평가법으로 기업가치를 계산합니다.

    ## 권한
    - 시스템 내부 API만 가능

    ## 5가지 평가법 (순서 고정)
    1. DCF평가법 (dcf)
    2. 상대가치평가법 (relative)
    3. 본질가치평가법 (capital_market_law)
    4. 자산가치평가법 (asset)
    5. 상증세법평가법 (inheritance_tax_law)

    ## 상태 변경
    - collecting → evaluating
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
        if project.status != "collecting":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"평가 계산은 'collecting' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # TODO: 실제 평가 엔진 호출
        # 여기서는 더미 결과 반환
        valuation_result = {
            "method": request.method,
            "enterprise_value": 10000000000,
            "equity_value": 7000000000,
            "value_per_share": 70000,
            "key_assumptions": {
                "wacc": 0.08,
                "terminal_growth": 0.02
            }
        }

        # 결과 저장
        result = ValuationResult(
            project_id=project_id,
            method=request.method,
            result=valuation_result,
            key_assumptions=valuation_result["key_assumptions"],
            calculation_date=datetime.utcnow()
        )

        db.add(result)

        # 프로젝트 상태 업데이트
        project.status = "evaluating"

        db.commit()
        db.refresh(result)

        return CalculationResponse(
            project_id=project_id,
            method=request.method,
            result=valuation_result,
            result_id=result.result_id,
            status=project.status,
            calculated_at=result.calculation_date,
            message=f"{request.method} 평가가 완료되었습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"평가 계산 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/projects/{project_id}/integrated-valuation", response_model=IntegratedValuationResponse)
async def integrated_valuation(
    project_id: str,
    request: IntegratedValuationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_system_user)
):
    """
    # 통합 평가

    여러 평가법의 결과를 종합하여 최종 의견을 도출합니다.

    ## 권한
    - 시스템 내부 API만 가능

    ## 통합 방법
    - 가중평균 (Weighted Average)
    - 범위 분석 (Range Analysis)
    - 전문가 조정 (Expert Adjustment)

    ## 상태 변경
    - evaluating → human_approval
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
        if project.status != "evaluating":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"통합 평가는 'evaluating' 상태에서만 가능합니다. (현재: {project.status})"
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

        # TODO: 실제 통합 로직
        # 여기서는 단순 가중평균
        total_value = sum(
            r.result.get("equity_value", 0) * request.weights.get(r.method, 1.0)
            for r in valuation_results
        )
        total_weight = sum(request.weights.get(r.method, 1.0) for r in valuation_results)
        final_value = total_value / total_weight if total_weight > 0 else 0

        integrated_result = {
            "final_value": final_value,
            "value_range": {
                "min": final_value * 0.9,
                "max": final_value * 1.1
            },
            "method_results": [
                {
                    "method": r.method,
                    "value": r.result.get("equity_value"),
                    "weight": request.weights.get(r.method, 1.0)
                }
                for r in valuation_results
            ]
        }

        # 22개 판단 포인트 생성
        # TODO: 실제 판단 포인트 생성 로직
        judgment_points = []
        for i in range(1, 23):
            point_id = f"JP{i:03d}"
            point = ApprovalPoint(
                project_id=project_id,
                point_id=point_id,
                point_name=f"판단포인트 {i}",
                display_name=f"판단포인트 {i}",
                category="재무" if i <= 12 else ("시장" if i <= 16 else ("자산" if i <= 19 else "법률")),
                importance="high" if i <= 5 else "medium",
                valuation_method=project.valuation_methods[0] if project.valuation_methods else "dcf",
                ai_value=1000000 * i,
                ai_rationale=f"AI 판단 근거 {i}",
                suggested_range={"min": 900000 * i, "max": 1100000 * i},
                status="pending"
            )
            db.add(point)
            judgment_points.append({
                "point_id": point_id,
                "point_name": f"판단포인트 {i}",
                "ai_value": 1000000 * i
            })

        # 프로젝트 상태 업데이트
        project.status = "human_approval"

        db.commit()

        return IntegratedValuationResponse(
            project_id=project_id,
            final_value=final_value,
            value_range=integrated_result["value_range"],
            method_results=integrated_result["method_results"],
            judgment_points=judgment_points,
            status=project.status,
            integrated_at=datetime.utcnow(),
            message="통합 평가가 완료되었습니다. 회계사가 22개 판단 포인트를 검토합니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통합 평가 중 오류가 발생했습니다: {str(e)}"
        )
