"""
Valuation calculation and results schemas

평가 실행, 결과, 시뮬레이션 관련 스키마
"""

from typing import Optional, List, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field

from .common import ProjectStatusCode, ValuationMethodCode, ValuationPurposeCode


# ========================================
# 8. 평가 실행 (POST /projects/{project_id}/calculate)
# ========================================

class CalculationRequest(BaseModel):
    """평가 실행 요청"""
    methods: List[ValuationMethodCode] = Field(..., description="실행할 평가법 목록")
    purpose: ValuationPurposeCode = Field(..., description="평가 목적")
    include_sensitivity: bool = Field(default=True, description="민감도 분석 포함 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "methods": ["dcf", "relative", "asset", "capital_market_law", "inheritance_tax_law"],
                "purpose": "comprehensive",
                "include_sensitivity": True
            }
        }


# ========================================
# 평가 결과 (각 평가법별)
# ========================================

class DCFResult(BaseModel):
    """DCF평가법 결과"""
    enterprise_value: int = Field(..., description="기업가치")
    equity_value: int = Field(..., description="주주가치")
    value_per_share: float = Field(..., description="주당가치")
    wacc: float = Field(..., description="WACC")
    terminal_growth: float = Field(..., description="영구성장률")
    pv_fcff: int = Field(..., description="FCFF 현재가치")
    pv_terminal_value: int = Field(..., description="Terminal Value 현재가치")
    terminal_value_percentage: float = Field(..., description="Terminal Value 비중")

    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_value": 152300000000,
                "equity_value": 152300000000,
                "value_per_share": 15230,
                "wacc": 0.112,
                "terminal_growth": 0.025,
                "pv_fcff": 50720000000,
                "pv_terminal_value": 107780000000,
                "terminal_value_percentage": 0.68
            }
        }


class RelativeResult(BaseModel):
    """상대가치평가법 결과"""
    per_valuation: int = Field(..., description="PER 기준 가치")
    pbr_valuation: int = Field(..., description="PBR 기준 가치")
    ev_ebitda_valuation: int = Field(..., description="EV/EBITDA 기준 가치")
    average_valuation: int = Field(..., description="평균 가치")
    value_per_share: float = Field(..., description="주당가치")
    selected_multiples: Dict[str, float] = Field(..., description="선택된 멀티플")

    class Config:
        json_schema_extra = {
            "example": {
                "per_valuation": 145000000000,
                "pbr_valuation": 138000000000,
                "ev_ebitda_valuation": 150000000000,
                "average_valuation": 144333000000,
                "value_per_share": 14433,
                "selected_multiples": {
                    "per": 18.5,
                    "pbr": 1.8,
                    "ev_ebitda": 10.2
                }
            }
        }


class AssetResult(BaseModel):
    """자산가치평가법 결과"""
    nav: int = Field(..., description="순자산가치")
    value_per_share: float = Field(..., description="주당가치")
    fair_value_adjustments: Dict[str, int] = Field(..., description="공정가치 조정")

    class Config:
        json_schema_extra = {
            "example": {
                "nav": 135000000000,
                "value_per_share": 13500,
                "fair_value_adjustments": {
                    "land_building": 15000000000,
                    "intangible_assets": -2000000000,
                    "contingent_liabilities": -5000000000
                }
            }
        }


class CapitalMarketLawResult(BaseModel):
    """본질가치평가법 결과"""
    intrinsic_value: int = Field(..., description="본질가치")
    value_per_share: float = Field(..., description="주당가치")
    asset_value: int = Field(..., description="자산가치")
    income_value: int = Field(..., description="수익가치")
    weight_asset: float = Field(..., description="자산가치 가중치")
    weight_income: float = Field(..., description="수익가치 가중치")

    class Config:
        json_schema_extra = {
            "example": {
                "intrinsic_value": 148000000000,
                "value_per_share": 14800,
                "asset_value": 135000000000,
                "income_value": 155000000000,
                "weight_asset": 0.40,
                "weight_income": 0.60
            }
        }


class InheritanceTaxLawResult(BaseModel):
    """상증세법평가법 결과"""
    valuation: int = Field(..., description="평가액")
    value_per_share: float = Field(..., description="주당가치")
    income_value: int = Field(..., description="수익가치")
    asset_value: int = Field(..., description="자산가치")
    weight_income: float = Field(..., description="수익가치 가중치")
    weight_asset: float = Field(..., description="자산가치 가중치")
    discount_rate: float = Field(..., description="할인율")
    shareholder_type: Literal["majority", "minority"] = Field(..., description="주주 유형")

    class Config:
        json_schema_extra = {
            "example": {
                "valuation": 140000000000,
                "value_per_share": 14000,
                "income_value": 150000000000,
                "asset_value": 125000000000,
                "weight_income": 0.60,
                "weight_asset": 0.40,
                "discount_rate": 0.20,
                "shareholder_type": "minority"
            }
        }


class ValuationRange(BaseModel):
    """가치 범위"""
    min: int = Field(..., description="최소값")
    max: int = Field(..., description="최대값")
    confidence_level: float = Field(..., description="신뢰 수준")


class IntegratedResult(BaseModel):
    """통합 평가 결과"""
    final_value: int = Field(..., description="최종 기업가치")
    final_value_per_share: float = Field(..., description="최종 주당가치")
    weights: Dict[str, float] = Field(..., description="평가법별 가중치")
    valuation_range: ValuationRange = Field(..., description="가치 범위")

    class Config:
        json_schema_extra = {
            "example": {
                "final_value": 146000000000,
                "final_value_per_share": 14600,
                "weights": {
                    "dcf": 0.30,
                    "relative": 0.25,
                    "asset": 0.20,
                    "capital_market_law": 0.15,
                    "inheritance_tax_law": 0.10
                },
                "valuation_range": {
                    "min": 135000000000,
                    "max": 155000000000,
                    "confidence_level": 0.80
                }
            }
        }


class CalculationResponse(BaseModel):
    """평가 실행 응답"""
    project_id: str
    status: ProjectStatusCode
    calculation_status: Literal["completed", "failed", "partial"]
    valuation_results: Dict[str, dict] = Field(..., description="평가법별 결과")
    integrated_result: IntegratedResult = Field(..., description="통합 결과")
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "status": "evaluating",
                "calculation_status": "completed",
                "valuation_results": {
                    "dcf": {
                        "enterprise_value": 152300000000,
                        "equity_value": 152300000000,
                        "value_per_share": 15230,
                        "wacc": 0.112,
                        "terminal_growth": 0.025,
                        "pv_fcff": 50720000000,
                        "pv_terminal_value": 107780000000,
                        "terminal_value_percentage": 0.68
                    },
                    "relative": {
                        "per_valuation": 145000000000,
                        "pbr_valuation": 138000000000,
                        "ev_ebitda_valuation": 150000000000,
                        "average_valuation": 144333000000,
                        "value_per_share": 14433,
                        "selected_multiples": {
                            "per": 18.5,
                            "pbr": 1.8,
                            "ev_ebitda": 10.2
                        }
                    },
                    "asset": {
                        "nav": 135000000000,
                        "value_per_share": 13500,
                        "fair_value_adjustments": {
                            "land_building": 15000000000,
                            "intangible_assets": -2000000000,
                            "contingent_liabilities": -5000000000
                        }
                    }
                },
                "integrated_result": {
                    "final_value": 146000000000,
                    "final_value_per_share": 14600,
                    "weights": {
                        "dcf": 0.30,
                        "relative": 0.25,
                        "asset": 0.20,
                        "capital_market_law": 0.15,
                        "inheritance_tax_law": 0.10
                    },
                    "valuation_range": {
                        "min": 135000000000,
                        "max": 155000000000,
                        "confidence_level": 0.80
                    }
                },
                "message": "평가가 완료되었습니다. 회계사 승인을 기다립니다."
            }
        }


# ========================================
# 12. 결과 미리보기 (GET /projects/{project_id}/preview)
# ========================================

class SensitivityMatrix(BaseModel):
    """민감도 분석 행렬"""
    parameters: List[str] = Field(..., description="분석 파라미터")
    wacc_range: List[float] = Field(..., description="WACC 범위")
    growth_range: List[float] = Field(..., description="성장률 범위")
    value_matrix: List[List[int]] = Field(..., description="가치 행렬")


class KeyAssumptions(BaseModel):
    """주요 가정"""
    dcf: Optional[Dict[str, any]] = None
    relative: Optional[Dict[str, any]] = None
    asset: Optional[Dict[str, any]] = None
    capital_market_law: Optional[Dict[str, any]] = None
    inheritance_tax_law: Optional[Dict[str, any]] = None


class PreviewResponse(BaseModel):
    """결과 미리보기 응답"""
    project_id: str
    current_status: ProjectStatusCode
    integrated_result: IntegratedResult
    method_results: Dict[str, dict]
    sensitivity_analysis: Optional[Dict[str, SensitivityMatrix]] = None
    key_assumptions: KeyAssumptions


# ========================================
# 13. 시뮬레이션 (POST /projects/{project_id}/simulate)
# ========================================

class SimulationRequest(BaseModel):
    """시뮬레이션 요청"""
    method: ValuationMethodCode = Field(..., description="시뮬레이션 대상 평가법")
    modified_assumptions: Dict[str, any] = Field(..., description="수정된 가정")

    class Config:
        json_schema_extra = {
            "example": {
                "method": "dcf",
                "modified_assumptions": {
                    "revenue_growth_rate": 0.07,
                    "ebit_margin": 0.16,
                    "wacc": 0.095,
                    "terminal_growth": 0.03
                }
            }
        }


class ImpactBreakdown(BaseModel):
    """영향 분석"""
    revenue_growth_impact: Optional[int] = None
    ebit_margin_impact: Optional[int] = None
    wacc_impact: Optional[int] = None
    terminal_growth_impact: Optional[int] = None


class SimulationResult(BaseModel):
    """시뮬레이션 결과"""
    original_value: int
    simulated_value: int
    change_amount: int
    change_percentage: float


class SimulationResponse(BaseModel):
    """시뮬레이션 응답"""
    project_id: str
    method: ValuationMethodCode
    simulation_result: SimulationResult
    impact_breakdown: ImpactBreakdown
    new_assumptions: Dict[str, any]

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "SAMSU-2501191430-CP",
                "method": "dcf",
                "simulation_result": {
                    "original_value": 158500000000,
                    "simulated_value": 175200000000,
                    "change_amount": 16700000000,
                    "change_percentage": 0.105
                },
                "impact_breakdown": {
                    "revenue_growth_impact": 6200000000,
                    "ebit_margin_impact": 3800000000,
                    "wacc_impact": 4500000000,
                    "terminal_growth_impact": 2200000000
                },
                "new_assumptions": {
                    "revenue_growth_rate": 0.07,
                    "ebit_margin": 0.16,
                    "wacc": 0.095,
                    "terminal_growth": 0.03
                }
            }
        }
