"""
Master Valuation Router

통합 평가:
- POST /projects/{project_id}/integrated-valuation - 5가지 평가법 통합 실행
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from database import get_db
from schemas.master_valuation import (
    IntegratedValuationRequest,
    IntegratedValuationResponse
)
from models.project import Project
from models.valuation_result import ValuationResult
from models.approval_point import ApprovalPoint

router = APIRouter()


async def run_master_valuation_engine(
    project: Project,
    input_data: Dict[str, Any],
    valuation_methods: List[str],
    approval_points: List[ApprovalPoint]
) -> Dict[str, Any]:
    """
    Master Valuation Engine 실행

    5가지 평가법을 통합하여 실행하고 최종 의견을 도출합니다.

    TODO: 실제 Master Valuation Engine 연동
    - 각 평가법 자동 실행
    - 22개 판단 포인트 자동 생성
    - 평가법별 가중치 적용
    - 최종 가치 범위 산정
    """
    # TODO: 실제 Master Valuation Engine 구현

    # 1. Valuation Selector: 적합한 평가법 조합 제안
    selector_recommendation = {
        "recommended_methods": valuation_methods,
        "weights": {
            "dcf": 0.4 if "dcf" in valuation_methods else 0,
            "relative": 0.3 if "relative" in valuation_methods else 0,
            "asset": 0.15 if "asset" in valuation_methods else 0,
            "capital_market_law": 0.1 if "capital_market_law" in valuation_methods else 0,
            "inheritance_tax_law": 0.05 if "inheritance_tax_law" in valuation_methods else 0
        },
        "rationale": "재무 안정성과 성장성을 고려한 DCF 중심 평가 추천"
    }

    # 2. 각 평가법 실행 (더미 데이터)
    method_results = {
        "dcf": {"equity_value": 7000000000} if "dcf" in valuation_methods else None,
        "relative": {"equity_value": 6500000000} if "relative" in valuation_methods else None,
        "asset": {"net_asset_value": 5000000000} if "asset" in valuation_methods else None,
        "capital_market_law": {"fair_value": 6800000000} if "capital_market_law" in valuation_methods else None,
        "inheritance_tax_law": {"tax_base_value": 6200000000} if "inheritance_tax_law" in valuation_methods else None
    }

    # 3. 22개 판단 포인트 자동 생성
    auto_generated_approval_points = [
        {
            "point_id": f"JP{i:03d}",
            "ai_value": f"AI_VALUE_{i}",
            "ai_rationale": f"AI가 제안하는 {i}번 판단 포인트 근거",
            "suggested_range": {"min": 0, "max": 100}
        }
        for i in range(1, 23)
    ]

    # 4. 가중평균 최종 가치
    weighted_value = sum(
        result.get("equity_value", result.get("fair_value", result.get("net_asset_value", result.get("tax_base_value", 0))))
        * selector_recommendation["weights"].get(method, 0)
        for method, result in method_results.items()
        if result
    )

    # 5. 가치 범위
    all_values = [
        result.get("equity_value", result.get("fair_value", result.get("net_asset_value", result.get("tax_base_value", 0))))
        for method, result in method_results.items()
        if result
    ]
    value_range = {
        "min": min(all_values) if all_values else 0,
        "max": max(all_values) if all_values else 0,
        "weighted_average": weighted_value
    }

    return {
        "selector_recommendation": selector_recommendation,
        "method_results": method_results,
        "approval_points": auto_generated_approval_points,
        "final_valuation": {
            "value_range": value_range,
            "recommended_value": weighted_value,
            "confidence_level": "high"
        }
    }


@router.post("/projects/{project_id}/integrated-valuation", response_model=IntegratedValuationResponse)
async def run_integrated_valuation(
    project_id: str,
    request: IntegratedValuationRequest,
    db: Session = Depends(get_db)
):
    """
    # 통합 평가 실행

    5가지 평가법을 자동으로 실행하고 22개 판단 포인트를 생성합니다.

    ## Master Valuation Engine 기능

    ### 1. Valuation Selector
    - 프로젝트 특성 분석 (업종, 규모, 성장 단계)
    - 적합한 평가법 조합 제안
    - 평가법별 가중치 제안

    ### 2. 자동 평가 실행
    - 5가지 평가법 병렬 실행
    - 1.DCF평가법 2.상대가치평가법 3.본질가치평가법 4.자산가치평가법 5.상증세법평가법
    - 각 평가법별 계산 결과 산출

    ### 3. 22개 판단 포인트 자동 생성
    - AI가 각 포인트의 값을 자동 제안
    - 제안 근거 (rationale) 제공
    - 추천 범위 (suggested_range) 제공
    - 회계사 승인 대기

    ### 4. 통합 결과 도출
    - 평가법별 가중평균
    - 가치 범위 (최소, 최대, 가중평균)
    - 최종 의견 (recommended_value)

    ## 사용 시나리오

    **시나리오 1: 빠른 평가 (One-Click Valuation)**
    - 문서 업로드 → 통합 평가 실행 (이 API)
    - AI가 모든 계산 및 판단 포인트 자동 생성
    - 회계사는 22개 포인트만 검토/승인
    - 초안 생성 → 완료

    **시나리오 2: 단계별 평가 (Step-by-Step)**
    - 문서 업로드 → AI 추출 → 수동 계산
    - 회계사가 각 평가법을 개별 실행
    - 판단 포인트 개별 입력
    - 초안 생성 → 완료

    ## 프로세스
    ```
    documents_uploaded
           ↓
    [통합 평가 API 호출]
           ↓
    collecting (AI 추출)
           ↓
    evaluating (5가지 평가법 실행)
           ↓
    human_approval (22개 포인트 생성)
    ```

    ## 응답
    - selector_recommendation: 평가법 선택 제안
    - method_results: 5가지 평가 결과
    - approval_points: 22개 판단 포인트 (AI 제안)
    - final_valuation: 통합 최종 가치
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
        if project.status not in ["documents_uploaded", "collecting", "evaluating"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"통합 평가는 'documents_uploaded' 이후 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 평가 방법 확인
        if not project.valuation_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="평가 방법이 지정되지 않았습니다."
            )

        # Master Valuation Engine 실행
        engine_result = await run_master_valuation_engine(
            project,
            request.input_data,
            project.valuation_methods,
            []  # 기존 approval points (없으면 빈 리스트)
        )

        # 1. 평가 결과 저장
        for method, result in engine_result["method_results"].items():
            if result is None:
                continue

            existing_result = db.query(ValuationResult).filter(
                ValuationResult.project_id == project_id,
                ValuationResult.method == method
            ).first()

            if existing_result:
                existing_result.result = result
                existing_result.calculation_status = "completed"
            else:
                new_result = ValuationResult(
                    project_id=project_id,
                    method=method,
                    calculation_status="completed",
                    result=result
                )
                db.add(new_result)

        # 2. 판단 포인트 생성
        for point_data in engine_result["approval_points"]:
            existing_point = db.query(ApprovalPoint).filter(
                ApprovalPoint.project_id == project_id,
                ApprovalPoint.point_id == point_data["point_id"]
            ).first()

            if not existing_point:
                new_point = ApprovalPoint(
                    project_id=project_id,
                    point_id=point_data["point_id"],
                    point_name=f"point_{point_data['point_id']}",
                    display_name=f"판단 포인트 {point_data['point_id']}",
                    category="재무",  # TODO: 실제 카테고리
                    importance="medium",
                    valuation_method=project.valuation_methods[0],
                    ai_value=point_data["ai_value"],
                    ai_rationale=point_data["ai_rationale"],
                    suggested_range=point_data.get("suggested_range"),
                    status="pending"
                )
                db.add(new_point)

        # 3. 프로젝트 상태 업데이트
        project.status = "human_approval"

        db.commit()

        return IntegratedValuationResponse(
            project_id=project_id,
            selector_recommendation=engine_result["selector_recommendation"],
            method_results=engine_result["method_results"],
            approval_points_count=len(engine_result["approval_points"]),
            final_valuation=engine_result["final_valuation"],
            status=project.status,
            message="통합 평가가 완료되었습니다. 22개 판단 포인트를 검토하세요."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통합 평가 중 오류가 발생했습니다: {str(e)}"
        )
