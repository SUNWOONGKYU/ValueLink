"""
Calculations Router

평가 계산 실행:
- POST /projects/{project_id}/calculate - 평가 계산 실행
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from database import get_db
from schemas.calculation import CalculationRequest, CalculationResponse
from models.project import Project
from models.valuation_result import ValuationResult

router = APIRouter()


async def calculate_dcf(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    DCF (Discounted Cash Flow) 평가

    TODO: 실제 DCF 엔진 연동 필요
    """
    # TODO: valuation_engine/dcf/dcf_engine.py 연동
    return {
        "enterprise_value": 10000000000,
        "equity_value": 7000000000,
        "wacc": 0.08,
        "terminal_growth_rate": 0.02,
        "free_cash_flows": [500000000, 600000000, 700000000, 800000000, 900000000]
    }


async def calculate_relative(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    상대가치평가법 (Relative Valuation)

    TODO: 실제 Relative 엔진 연동 필요
    """
    # TODO: valuation_engine/relative/relative_engine.py 연동
    return {
        "equity_value": 6500000000,
        "per_multiple": 15.2,
        "pbr_multiple": 1.8,
        "ev_ebitda_multiple": 8.5,
        "comparable_companies": ["경쟁사A", "경쟁사B", "경쟁사C"]
    }


async def calculate_asset(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    자산가치평가법 (Asset-based Valuation)

    TODO: 실제 Asset 엔진 연동 필요
    """
    # TODO: valuation_engine/asset/asset_engine.py 연동
    return {
        "net_asset_value": 5000000000,
        "adjusted_book_value": 5500000000,
        "liquidation_value": 4500000000
    }


async def calculate_capital_market_law(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    본질가치평가법

    TODO: 실제 본질가치 엔진 연동 필요
    """
    # TODO: valuation_engine/capital_market_law/cml_engine.py 연동
    return {
        "fair_value": 6800000000,
        "adjustment_factor": 1.0,
        "compliance_check": "pass"
    }


async def calculate_inheritance_tax_law(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    상속세법 평가 (Inheritance Tax Law Valuation)

    TODO: 실제 ITL 엔진 연동 필요
    """
    # TODO: valuation_engine/inheritance_tax_law/itl_engine.py 연동
    return {
        "tax_base_value": 6200000000,
        "net_asset_value": 5000000000,
        "earning_value": 7000000000,
        "weighted_average": 6200000000,
        "weight_ratio": {"net_asset": 0.4, "earning": 0.6}
    }


# 평가 방법별 계산 함수 매핑
CALCULATION_METHODS = {
    "dcf": calculate_dcf,
    "relative": calculate_relative,
    "asset": calculate_asset,
    "capital_market_law": calculate_capital_market_law,
    "inheritance_tax_law": calculate_inheritance_tax_law
}


@router.post("/projects/{project_id}/calculate", response_model=CalculationResponse)
async def calculate_valuation(
    project_id: str,
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """
    # 7. 평가 계산

    선택된 평가 방법으로 기업가치를 계산합니다.

    ## 지원 평가 방법
    1. **DCF평가법**
       - 미래 현금흐름 할인
       - WACC, Terminal Growth Rate 산정
       - 기업가치 및 주주가치 계산

    2. **상대가치평가법**
       - PER, PBR, EV/EBITDA 멀티플 적용
       - 유사 기업 비교
       - 시장 배수 활용

    3. **본질가치평가법**
       - 본질가치 산정
       - 공정가치 계산
       - 조정 계수 적용

    4. **자산가치평가법**
       - 순자산가치 (NAV) 계산
       - 청산가치 산정
       - 자산 재평가

    5. **상증세법평가법**
       - 순자산가치 + 수익가치 가중평균
       - 상속세 및 증여세법 기준
       - 세무 신고용

    ## 상태 전이
    - collecting → evaluating → human_approval

    ## 필수 입력
    - input_data: 평가에 필요한 데이터 (AI 추출 결과 + 수동 입력)
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
        if project.status not in ["collecting", "evaluating"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"계산은 'collecting' 또는 'evaluating' 상태에서만 가능합니다. (현재: {project.status})"
            )

        # 평가 방법 확인
        if not project.valuation_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="평가 방법이 지정되지 않았습니다."
            )

        # 프로젝트 상태 업데이트
        if project.status != "evaluating":
            project.status = "evaluating"

        # 각 평가 방법에 대해 계산 수행
        results = []
        for method in project.valuation_methods:
            if method not in CALCULATION_METHODS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"지원하지 않는 평가 방법입니다: {method}"
                )

            # 계산 수행
            calculation_func = CALCULATION_METHODS[method]
            result_data = await calculation_func(request.input_data)

            # 기존 결과 확인
            existing_result = db.query(ValuationResult).filter(
                ValuationResult.project_id == project_id,
                ValuationResult.method == method
            ).first()

            if existing_result:
                # 기존 결과 업데이트
                existing_result.result = result_data
                existing_result.calculation_status = "completed"
                existing_result.key_assumptions = request.input_data.get("assumptions", {})
                result = existing_result
            else:
                # 새 결과 생성
                result = ValuationResult(
                    project_id=project_id,
                    method=method,
                    calculation_status="completed",
                    result=result_data,
                    key_assumptions=request.input_data.get("assumptions", {})
                )
                db.add(result)

            results.append({
                "method": method,
                "result": result_data
            })

        db.commit()

        # 모든 평가가 완료되면 상태를 human_approval로 변경
        # (22개 판단 포인트 검토 단계)
        project.status = "human_approval"
        db.commit()

        return CalculationResponse(
            project_id=project_id,
            results=results,
            status=project.status,
            message=f"{len(results)}개 평가 방법의 계산이 완료되었습니다. 판단 포인트를 검토하세요."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계산 중 오류가 발생했습니다: {str(e)}"
        )
