# Valuation Engines API

## 개요

ValueLink는 5개의 기업가치평가 방법을 지원합니다:

| # | Method | 한글명 | 주요 용도 |
|---|--------|--------|----------|
| 1 | DCF | 현금흐름할인법 | 성장 기업, 투자 유치 |
| 2 | Relative | 상대가치평가 | 상장사 비교, 빠른 평가 |
| 3 | Asset | 자산가치평가 | 부동산, 제조업 |
| 4 | Intrinsic | 내재가치평가 | 주식 투자, 가치 분석 |
| 5 | Tax | 세법상평가 | 상속/증여, 세무 목적 |

**Base URL**: `/api/valuation`

---

## 공통 응답 구조

모든 평가 API는 다음 구조로 응답합니다:

```json
{
  "result_id": "uuid",
  "project_id": "VL-2026-0001",
  "valuation_method": "dcf",
  "status": "completed",
  "enterprise_value": 150000000000,
  "equity_value": 145000000000,
  "value_per_share": 14500,
  "calculation_data": { ... },
  "sensitivity_analysis": { ... },
  "created_at": "2026-02-07T13:00:00Z"
}
```

---

## 1. DCF 평가 엔진 (Discounted Cash Flow)

현금흐름할인법을 사용하여 기업가치를 평가합니다.

### POST /api/valuation/dcf

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "input_data": {
    "revenue_forecast": {
      "year_1": 10000000000,
      "year_2": 12000000000,
      "year_3": 14400000000,
      "year_4": 17280000000,
      "year_5": 20736000000
    },
    "operating_margin": 0.15,
    "tax_rate": 0.22,
    "depreciation_rate": 0.05,
    "capex_rate": 0.08,
    "working_capital_change_rate": 0.02,
    "wacc": 0.12,
    "terminal_growth_rate": 0.03,
    "net_debt": 5000000000,
    "shares_outstanding": 10000000
  }
}
```

**Input Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| revenue_forecast | object | Yes | 5개년 매출 예측 |
| operating_margin | float | Yes | 영업이익률 (0~1) |
| tax_rate | float | Yes | 법인세율 (0~1) |
| depreciation_rate | float | Yes | 감가상각률 |
| capex_rate | float | Yes | 자본적지출률 |
| working_capital_change_rate | float | Yes | 운전자본변동률 |
| wacc | float | Yes | 가중평균자본비용 |
| terminal_growth_rate | float | Yes | 영구성장률 |
| net_debt | integer | Yes | 순차입금 |
| shares_outstanding | integer | Yes | 발행주식수 |

**Response**:
```json
{
  "result_id": "uuid",
  "project_id": "VL-2026-0001",
  "valuation_method": "dcf",
  "status": "completed",
  "enterprise_value": 150000000000,
  "equity_value": 145000000000,
  "value_per_share": 14500,
  "calculation_data": {
    "fcf_forecast": {
      "year_1": 500000000,
      "year_2": 600000000,
      "year_3": 720000000,
      "year_4": 864000000,
      "year_5": 1036800000
    },
    "pv_fcf": {
      "year_1": 446428571,
      "year_2": 478316326,
      "year_3": 512053571,
      "year_4": 548985714,
      "year_5": 588342857
    },
    "pv_fcf_sum": 2574127039,
    "terminal_value": 11853333333,
    "pv_terminal_value": 6726190476,
    "enterprise_value": 9300317515
  },
  "sensitivity_analysis": {
    "wacc_range": [0.10, 0.11, 0.12, 0.13, 0.14],
    "growth_range": [0.01, 0.02, 0.03, 0.04, 0.05],
    "value_matrix": [
      [18500, 17200, 16000, 14900, 13900],
      [19800, 18300, 17000, 15800, 14700],
      [21300, 19600, 18100, 16700, 15500],
      [23100, 21100, 19300, 17700, 16400],
      [25200, 22800, 20700, 18900, 17400]
    ]
  },
  "created_at": "2026-02-07T13:00:00Z"
}
```

---

## 2. Relative 평가 엔진 (상대가치평가)

비교 기업의 배수를 사용하여 기업가치를 평가합니다.

### POST /api/valuation/relative

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "input_data": {
    "target_company": {
      "revenue": 10000000000,
      "ebitda": 2000000000,
      "net_income": 1200000000,
      "book_value": 8000000000,
      "shares_outstanding": 10000000
    },
    "comparable_companies": [
      {
        "name": "A사",
        "ticker": "005930.KS",
        "market_cap": 50000000000,
        "revenue": 15000000000,
        "ebitda": 3000000000,
        "net_income": 1800000000,
        "book_value": 12000000000,
        "shares_outstanding": 5000000,
        "ev_revenue": 3.5,
        "ev_ebitda": 17.5,
        "per": 27.8,
        "pbr": 4.2
      },
      {
        "name": "B사",
        "ticker": "035420.KS",
        "market_cap": 30000000000,
        "revenue": 8000000000,
        "ebitda": 1600000000,
        "net_income": 960000000,
        "book_value": 6000000000,
        "shares_outstanding": 3000000,
        "ev_revenue": 4.0,
        "ev_ebitda": 20.0,
        "per": 31.3,
        "pbr": 5.0
      }
    ],
    "selected_multiples": ["ev_ebitda", "per", "pbr"],
    "weighting_method": "equal"
  }
}
```

**Response**:
```json
{
  "result_id": "uuid",
  "project_id": "VL-2026-0001",
  "valuation_method": "relative",
  "status": "completed",
  "enterprise_value": 37500000000,
  "equity_value": 35000000000,
  "value_per_share": 3500,
  "calculation_data": {
    "multiples_applied": {
      "ev_ebitda": {
        "average_multiple": 18.75,
        "target_ebitda": 2000000000,
        "implied_ev": 37500000000
      },
      "per": {
        "average_multiple": 29.55,
        "target_net_income": 1200000000,
        "implied_equity": 35460000000
      },
      "pbr": {
        "average_multiple": 4.6,
        "target_book_value": 8000000000,
        "implied_equity": 36800000000
      }
    },
    "valuation_summary": {
      "by_ev_ebitda": 35000000000,
      "by_per": 35460000000,
      "by_pbr": 36800000000,
      "average": 35753333333,
      "final_value": 35000000000
    }
  },
  "comparable_analysis": {
    "companies_used": 2,
    "multiples_used": ["ev_ebitda", "per", "pbr"],
    "weighting": "equal",
    "outliers_removed": 0
  },
  "created_at": "2026-02-07T13:00:00Z"
}
```

---

## 3. Asset 평가 엔진 (자산가치평가)

순자산가치를 기반으로 기업가치를 평가합니다.

### POST /api/valuation/asset

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "input_data": {
    "assets": {
      "current_assets": {
        "cash": 2000000000,
        "accounts_receivable": 3000000000,
        "inventory": 2500000000,
        "other_current": 500000000
      },
      "non_current_assets": {
        "property_plant_equipment": 15000000000,
        "intangible_assets": 3000000000,
        "investment_securities": 2000000000,
        "other_non_current": 1000000000
      }
    },
    "liabilities": {
      "current_liabilities": {
        "accounts_payable": 2000000000,
        "short_term_debt": 3000000000,
        "other_current": 1000000000
      },
      "non_current_liabilities": {
        "long_term_debt": 5000000000,
        "other_non_current": 500000000
      }
    },
    "adjustments": [
      {
        "item": "property_plant_equipment",
        "book_value": 15000000000,
        "fair_value": 20000000000,
        "adjustment_reason": "감정평가 결과 반영"
      },
      {
        "item": "intangible_assets",
        "book_value": 3000000000,
        "fair_value": 1500000000,
        "adjustment_reason": "특허권 상각 반영"
      }
    ],
    "shares_outstanding": 10000000
  }
}
```

**Response**:
```json
{
  "result_id": "uuid",
  "project_id": "VL-2026-0001",
  "valuation_method": "asset",
  "status": "completed",
  "enterprise_value": 22500000000,
  "equity_value": 22500000000,
  "value_per_share": 2250,
  "calculation_data": {
    "book_value_summary": {
      "total_assets": 29000000000,
      "total_liabilities": 11500000000,
      "net_asset_value_book": 17500000000
    },
    "fair_value_adjustments": {
      "property_plant_equipment": 5000000000,
      "intangible_assets": -1500000000,
      "total_adjustments": 3500000000
    },
    "adjusted_nav": {
      "book_nav": 17500000000,
      "adjustments": 3500000000,
      "deferred_tax_impact": -770000000,
      "final_nav": 20230000000
    }
  },
  "asset_breakdown": {
    "current_assets": 8000000000,
    "non_current_assets": 21000000000,
    "total_assets_adjusted": 29000000000,
    "current_liabilities": 6000000000,
    "non_current_liabilities": 5500000000,
    "total_liabilities": 11500000000
  },
  "created_at": "2026-02-07T13:00:00Z"
}
```

---

## 4. Intrinsic 평가 엔진 (내재가치평가)

배당할인모형(DDM) 또는 잔여이익모형(RIM)을 사용합니다.

### POST /api/valuation/intrinsic

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "input_data": {
    "model_type": "rim",
    "book_value_per_share": 8000,
    "eps_forecast": {
      "year_1": 1200,
      "year_2": 1400,
      "year_3": 1600,
      "year_4": 1800,
      "year_5": 2000
    },
    "cost_of_equity": 0.10,
    "terminal_roe": 0.12,
    "terminal_growth_rate": 0.03,
    "payout_ratio": 0.30,
    "shares_outstanding": 10000000
  }
}
```

**Model Types**:
- `ddm`: 배당할인모형 (Dividend Discount Model)
- `rim`: 잔여이익모형 (Residual Income Model)

**Response**:
```json
{
  "result_id": "uuid",
  "project_id": "VL-2026-0001",
  "valuation_method": "intrinsic",
  "status": "completed",
  "enterprise_value": null,
  "equity_value": 160000000000,
  "value_per_share": 16000,
  "calculation_data": {
    "model_used": "rim",
    "book_value_component": 8000,
    "residual_income_forecast": {
      "year_1": 400,
      "year_2": 600,
      "year_3": 800,
      "year_4": 1000,
      "year_5": 1200
    },
    "pv_residual_income": {
      "year_1": 364,
      "year_2": 496,
      "year_3": 601,
      "year_4": 683,
      "year_5": 745
    },
    "pv_sum": 2889,
    "terminal_residual_income": 17143,
    "pv_terminal": 10643,
    "intrinsic_value_per_share": 21532
  },
  "sensitivity_analysis": {
    "cost_of_equity_range": [0.08, 0.09, 0.10, 0.11, 0.12],
    "terminal_roe_range": [0.10, 0.11, 0.12, 0.13, 0.14],
    "value_matrix": [
      [24000, 26000, 28000, 30000, 32000],
      [20000, 22000, 24000, 26000, 28000],
      [17000, 19000, 21000, 23000, 25000],
      [15000, 17000, 19000, 21000, 23000],
      [13000, 15000, 17000, 19000, 21000]
    ]
  },
  "created_at": "2026-02-07T13:00:00Z"
}
```

---

## 5. Tax 평가 엔진 (세법상평가)

상속세 및 증여세법에 따른 비상장주식 평가입니다.

### POST /api/valuation/tax

**Request**:
```json
{
  "project_id": "VL-2026-0001",
  "input_data": {
    "valuation_date": "2026-02-07",
    "company_type": "medium",
    "industry_sector": "manufacturing",
    "financial_data": {
      "net_income_3years": [1000000000, 1200000000, 1500000000],
      "net_asset_value": 15000000000,
      "total_shares": 10000000,
      "treasury_shares": 0
    },
    "adjustment_items": {
      "non_operating_assets": 2000000000,
      "contingent_liabilities": 500000000,
      "unrealized_gains": 1000000000
    },
    "weighting": {
      "earning_weight": 3,
      "asset_weight": 2
    }
  }
}
```

**Company Types**:
- `small`: 소기업 (50억 미만)
- `medium`: 중기업 (50억~500억)
- `large`: 대기업 (500억 이상)

**Response**:
```json
{
  "result_id": "uuid",
  "project_id": "VL-2026-0001",
  "valuation_method": "tax",
  "status": "completed",
  "enterprise_value": null,
  "equity_value": 18000000000,
  "value_per_share": 1800,
  "calculation_data": {
    "earning_value": {
      "average_net_income": 1233333333,
      "earning_rate": 0.10,
      "earning_based_value": 12333333333,
      "per_share": 1233
    },
    "asset_value": {
      "adjusted_nav": 17500000000,
      "per_share": 1750
    },
    "weighted_value": {
      "earning_component": 7400000000,
      "asset_component": 7000000000,
      "total": 14400000000,
      "per_share": 1440
    },
    "final_adjustments": {
      "control_premium": 0.20,
      "liquidity_discount": 0.10,
      "final_value": 15840000000,
      "per_share": 1584
    }
  },
  "tax_law_reference": {
    "applicable_law": "상속세 및 증여세법 제63조",
    "valuation_method": "순손익가치와 순자산가치의 가중평균",
    "earning_rate": "10% (비상장주식)",
    "weighting_rule": "순손익가치 3 : 순자산가치 2"
  },
  "created_at": "2026-02-07T13:00:00Z"
}
```

---

## 공통 에러 응답

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "입력값이 유효하지 않습니다.",
    "details": {
      "field": "revenue_forecast",
      "reason": "5개년 데이터가 필요합니다.",
      "received": 3,
      "expected": 5
    }
  }
}
```

**에러 코드**:
| Code | Description |
|------|-------------|
| INVALID_INPUT | 입력값 오류 |
| MISSING_REQUIRED_FIELD | 필수 필드 누락 |
| CALCULATION_ERROR | 계산 오류 |
| COMPARABLE_NOT_FOUND | 비교 기업 없음 |
| INSUFFICIENT_DATA | 데이터 부족 |

---

## 평가 결과 조회

### GET /api/valuation/results

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | 프로젝트 ID |
| method | string | dcf, relative, asset, intrinsic, tax |

**Response**:
```json
{
  "results": [
    {
      "result_id": "uuid",
      "valuation_method": "dcf",
      "equity_value": 145000000000,
      "value_per_share": 14500,
      "status": "completed",
      "created_at": "2026-02-07T13:00:00Z"
    },
    {
      "result_id": "uuid",
      "valuation_method": "relative",
      "equity_value": 35000000000,
      "value_per_share": 3500,
      "status": "completed",
      "created_at": "2026-02-07T14:00:00Z"
    }
  ]
}
```

---

## 평가 결과 비교

### GET /api/valuation/comparison

여러 평가 방법의 결과를 비교합니다.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | 프로젝트 ID (필수) |

**Response**:
```json
{
  "project_id": "VL-2026-0001",
  "comparison": {
    "dcf": {
      "equity_value": 145000000000,
      "value_per_share": 14500
    },
    "relative": {
      "equity_value": 35000000000,
      "value_per_share": 3500
    },
    "asset": {
      "equity_value": 22500000000,
      "value_per_share": 2250
    }
  },
  "summary": {
    "min_value": 22500000000,
    "max_value": 145000000000,
    "average_value": 67500000000,
    "median_value": 35000000000,
    "recommended_range": {
      "low": 30000000000,
      "mid": 50000000000,
      "high": 100000000000
    }
  }
}
```

---

## 승인 포인트 (평가 엔진별)

각 평가 방법별 AI 승인 포인트:

| Method | Approval Points | Description |
|--------|-----------------|-------------|
| DCF | 8개 | 가정값 검증, WACC 검토, 성장률 확인 등 |
| Relative | 4개 | 비교 기업 선정, 배수 적정성 등 |
| Asset | 2개 | 공정가치 조정, 감정평가 검토 |
| Intrinsic | 6개 | ROE 예측, 할인율 검증 등 |
| Tax | 2개 | 세법 적용, 가중치 확인 |

**총 22개 AI 승인 포인트**

---

## 버전 정보

- **API Version**: v1
- **Last Updated**: 2026-02-07
- **Schema Version**: v4.0

---

**작성일**: 2026-02-07
**작성자**: Claude Code
