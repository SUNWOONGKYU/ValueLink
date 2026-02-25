# 샘플 데이터 세트

**작성일**: 2026-02-23
**버전**: 1.0
**목적**: 실전 예시를 통한 평가 방법론 이해 및 활용

---

## 목차
1. [IT 스타트업 (DCF 평가)](#it-스타트업-dcf-평가)
2. [제조업 (Relative 평가)](#제조업-relative-평가)
3. [부동산 임대업 (Asset 평가)](#부동산-임대업-asset-평가)

---

## IT 스타트업 (DCF 평가)

### 1. 회사 정보

```json
{
  "company": {
    "name_kr": "테크이노 주식회사",
    "name_en": "TechInno Inc.",
    "founded": "2021-03-15",
    "industry": "IT - 인공지능 (AI)",
    "business": "AI 기반 헬스케어 솔루션 개발",
    "headquarters": "서울 강남구 판교",
    "employees": 50,
    "ceo": "김철수",
    "website": "www.technoo.ai.kr"
  },
  "financial_summary": {
    "revenue_2023": 2500000000,
    "revenue_2024": 3500000000,
    "revenue_2025": 5000000000,
    "growth_rate_avg": 0.41,
    "profitability": "적자 → 흑자 전환 (2025)"
  }
}
```

### 2. 재무 데이터 (히스토리)

```json
{
  "historical_financials": {
    "2023": {
      "revenue": 2500000000,
      "cogs": 1000000000,
      "gross_profit": 1500000000,
      "gross_margin": 0.60,
      "opex": 1200000000,
      "ebitda": 300000000,
      "ebitda_margin": 0.12,
      "depreciation": 50000000,
      "operating_income": 250000000,
      "tax": 0,
      "net_income": 250000000,
      "net_margin": 0.10,
      "cash_from_operations": 200000000,
      "capex": 150000000,
      "free_cash_flow": 50000000
    },
    "2024": {
      "revenue": 3500000000,
      "cogs": 1400000000,
      "gross_profit": 2100000000,
      "gross_margin": 0.60,
      "opex": 1500000000,
      "ebitda": 600000000,
      "ebitda_margin": 0.17,
      "depreciation": 60000000,
      "operating_income": 540000000,
      "tax": 118800000,
      "net_income": 421200000,
      "net_margin": 0.12,
      "cash_from_operations": 380000000,
      "capex": 200000000,
      "free_cash_flow": 180000000
    },
    "2025": {
      "revenue": 5000000000,
      "cogs": 2000000000,
      "gross_profit": 3000000000,
      "gross_margin": 0.60,
      "opex": 1750000000,
      "ebitda": 1250000000,
      "ebitda_margin": 0.25,
      "depreciation": 70000000,
      "operating_income": 1180000000,
      "tax": 259600000,
      "net_income": 920400000,
      "net_margin": 0.18,
      "cash_from_operations": 800000000,
      "capex": 250000000,
      "free_cash_flow": 550000000
    }
  }
}
```

### 3. DCF 평가 입력 데이터

```json
{
  "dcf_inputs": {
    "current_revenue": 5000000000,
    "comment": "2025년 최종 확정 재무제표 기준",

    "growth_assumptions": {
      "year_1_to_5_growth_rate": 0.30,
      "reasoning": "역사적 평균 41% 대비 보수적 30% 설정 (시장 성숙화 감안)",
      "industry_comparison": {
        "industry_average": 0.35,
        "company_position": "평균 이하 (보수적)"
      }
    },

    "margin_assumptions": {
      "gross_margin": 0.60,
      "ebitda_margin": 0.25,
      "reasoning": "2025년 실적(25%) 유지 (규모의 경제 추가 반영 미포함)"
    },

    "investment_assumptions": {
      "capex_percent_of_revenue": 0.08,
      "comment": "매출의 8% (과거 평균 7% 대비 약간 상향)",
      "nwc_change_percent": 0.02,
      "comment2": "운영자본 변화 (매출 2%)"
    },

    "discount_rate": {
      "wacc": 0.15,
      "components": {
        "risk_free_rate": 0.04,
        "comment1": "국고채 3년 수익률",
        "equity_risk_premium": 0.08,
        "comment2": "장기 평균 equity risk premium",
        "company_specific_premium": 0.03,
        "comment3": "스타트업 리스크"
      },
      "reasoning": "스타트업(높은 리스크) 대비 중간~고 수준의 할인율"
    },

    "perpetual_growth": 0.03,
    "comment3": "장기 GDP 성장률과 유사"
  }
}
```

### 4. DCF 계산 상세 과정

#### Step 1: 5년 매출 예측

```
기준: 2025년 매출 50억원 + 연 30% 성장 가정

Year 1 (2026): 50억 × (1 + 0.30) = 65억원
Year 2 (2027): 65억 × (1 + 0.30) = 84.5억원
Year 3 (2028): 84.5억 × (1 + 0.30) = 109.85억원
Year 4 (2029): 109.85억 × (1 + 0.30) = 142.805억원
Year 5 (2030): 142.805억 × (1 + 0.30) = 185.6465억원

실무 팁: 매출 예측 과도 낙관 금지, 산업 성장률과 비교하여 타당성 검증
```

#### Step 2: 자유 현금흐름 (FCF) 계산

```
Year 1 계산:
┌────────────────────────────────────────────────────┐
│ 매출: 65억원                                         │
│ COGS (40%): -26억원                                │
│ 매출원가 후 이익: 39억원                             │
│ OpEx (35% of Revenue): -22.75억원                  │
│ EBITDA: 16.25억원                                  │
│ 감가상각비: -0.5억원                                │
│ 영업이익 (EBIT): 15.75억원                          │
│ 세금 (22%): -3.465억원                             │
│ NOPAT: 12.285억원 (세후 영업 이익)                 │
│ + 감가상각비: +0.5억원 (현금 항목 아님)             │
│ - CapEx (8% of Revenue): -5.2억원                  │
│ - 운영자본 증가 (2%): -1.3억원                     │
│ = FCF: 6.285억원 ✓                                │
└────────────────────────────────────────────────────┘

Year 1 FCF: 6.285억원

(동일 프로세스로 Year 2-5 계산)
```

**5년 FCF 추이**:
```
Year 1: 6.285억원
Year 2: 8.169억원 (증가율: 30%)
Year 3: 10.619억원
Year 4: 13.805억원
Year 5: 17.947억원
```

#### Step 3: DCF (현재가치 할인)

```
공식: PV = FCF / (1 + WACC)^n

Year 1 PV: 6.285억 / (1.15)^1 = 5.465억원
Year 2 PV: 8.169억 / (1.15)^2 = 6.170억원
Year 3 PV: 10.619억 / (1.15)^3 = 6.999억원
Year 4 PV: 13.805억 / (1.15)^4 = 7.878억원
Year 5 PV: 17.947억 / (1.15)^5 = 8.913억원
─────────────────────────────────────────
DCF 합계: 35.425억원

실무 팁: WACC (할인율)가 높을수록 현재가치는 낮아집니다.
         스타트업은 높은 리스크로 인해 높은 WACC (12-18%) 적용
```

#### Step 4: Terminal Value (종료가치) 계산

```
Gordon Growth Model 사용:

Terminal Value (Year 5 기준):
= FCF_Year5 × (1 + g) / (WACC - g)
= 17.947억 × (1 + 0.03) / (0.15 - 0.03)
= 17.947억 × 1.03 / 0.12
= 18.487억 / 0.12
= 154.058억원 (Year 5 기준)

현재가치 (PV of Terminal Value):
= 154.058억 / (1.15)^5
= 154.058억 / 2.0114
= 76.575억원

실무 팁: Terminal Value는 전체 기업 가치의 60-70%를 차지
         과도한 성장률 가정 주의 (보통 GDP 성장률 수준)
```

#### Step 5: 기업 가치 (Enterprise Value) 계산

```
Enterprise Value = DCF 합계 + PV(Terminal Value)
                 = 35.425억 + 76.575억
                 = 112억원

이는 순수 사업 가치만을 나타냅니다.
```

#### Step 6: 주주 가치 (Equity Value) 계산

```
Equity Value = Enterprise Value + 현금 - 부채

가정:
- 현금: 10억원 (현금흐름 분석 기반)
- 부채: 5억원 (은행 대출)

Equity Value = 112억 + 10억 - 5억
             = 117억원 ✓

주주 가치: 117억원
(원래 투자자 × 보유 지분 = 개인별 가치)

예: 창업자 60% 보유 → 개인 가치 = 70.2억원
   VC 투자자 40% 보유 → 개인 가치 = 46.8억원
```

### 5. 민감도 분석

```
WACC (할인율) vs 성장률 매트릭스
─────────────────────────────────────────────────────────
             매출 성장 15%    20%        25%       30% (기본)
─────────────────────────────────────────────────────────
WACC 12%      180억          210억      240억     270억
WACC 13%      160억          185억      210억     235억
WACC 14%      140억          160억      180억     200억
WACC 15%      120억          135억      150억     165억 (기본)
WACC 16%      105억          118억      130억     140억
WACC 17%      92억           102억      112억     120억
─────────────────────────────────────────────────────────

해석:
- 상승 시나리오: WACC 12% + 성장 30% → 270억원 (+130%)
- 기본 시나리오: WACC 15% + 성장 30% → 165억원
- 하강 시나리오: WACC 17% + 성장 15% → 92억원 (-45%)

범위: 92억원 ~ 270억원
기본: 165억원 (중간값 상단)
```

### 6. 결론 및 투자 평가

```json
{
  "valuation_result": {
    "enterprise_value": 11200000000,
    "equity_value": 11700000000,
    "valuation_method": "DCF",
    "reliability": "High (★★★★★)",
    "reasoning": "3년 재무제표 + 명확한 성장 트렌드 + 긍정적 현금흐름"
  },

  "comparable_analysis": {
    "comparable_companies": [
      {
        "name": "경쟁사 A (상장사)",
        "market_cap": 2000억원,
        "revenue": 8000000000,
        "pe_ratio": 25,
        "ev_ebitda": 18
      },
      {
        "name": "경쟁사 B (스타트업)",
        "valuation": 1500억원,
        "revenue": 6000000000,
        "revenue_multiple": 2.5
      }
    ],

    "relative_valuation": {
      "dcf_valuation": 11700000000,
      "multiple_based": {
        "revenue_multiple_3.0x": 15000000000,
        "comment": "경쟁사 평균 3.0배"
      },
      "average": 13350000000
    }
  },

  "investment_rationale": {
    "strengths": [
      "높은 성장률 (연 30%+)",
      "우수한 수익성 (EBITDA 마진 25%)",
      "강한 현금 생성 능력 (FCF/Revenue 11%)",
      "AI 산업 성장 추세 (2024-2030 CAGR 35%)"
    ],

    "risks": [
      "높은 번인율 (초기 스타트업)",
      "경쟁 심화 위험",
      "고객 집중 리스크",
      "규제 리스크 (의료 AI)"
    ],

    "recommendation": "POSITIVE (긍정적)",
    "target_investor": "Growth-focused VC / PE",
    "valuation_fairness": "Fairly Valued (공정가치)",
    "rationale": "성장률 대비 적절한 평가가"
  }
}
```

---

## 제조업 (Relative 평가)

### 1. 회사 정보

```json
{
  "company": {
    "name_kr": "정밀부품 주식회사",
    "industry": "제조업 - 반도체 부품",
    "business": "고급 반도체 테스트 부품 제조",
    "founded": "2005",
    "headquarters": "경기도 이천",
    "employees": 150,
    "market_position": "국내 점유율 35%"
  },
  "current_financials": {
    "revenue": 15000000000,
    "ebitda": 2250000000,
    "net_income": 1350000000,
    "equity": 8000000000
  }
}
```

### 2. 비교 회사 선정

```json
{
  "comparable_companies": [
    {
      "rank": 1,
      "name": "글로벌테크 (상장)",
      "stock_price": 55000,
      "shares": 30000000,
      "market_cap": 165000000000,
      "revenue": 40000000000,
      "ebitda": 6400000000,
      "net_income": 3200000000,
      "pe_ratio": 51.6,
      "ev_revenue": 4.125,
      "ev_ebitda": 25.8,
      "roe": 0.40,
      "similarity_score": 0.85
    },
    {
      "rank": 2,
      "name": "정밀산업 (상장)",
      "stock_price": 32000,
      "shares": 50000000,
      "market_cap": 160000000000,
      "revenue": 50000000000,
      "ebitda": 7000000000,
      "net_income": 3500000000,
      "pe_ratio": 45.7,
      "ev_revenue": 3.2,
      "ev_ebitda": 22.9,
      "roe": 0.44,
      "similarity_score": 0.90
    },
    {
      "rank": 3,
      "name": "첨단부품 (상장)",
      "stock_price": 28000,
      "shares": 20000000,
      "market_cap": 56000000000,
      "revenue": 18000000000,
      "ebitda": 2700000000,
      "net_income": 1350000000,
      "pe_ratio": 41.5,
      "ev_revenue": 3.11,
      "ev_ebitda": 20.7,
      "roe": 0.17,
      "similarity_score": 0.88
    }
  ],

  "average_multiples": {
    "pe_ratio": 46.3,
    "ev_revenue": 3.5,
    "ev_ebitda": 23.1,
    "price_to_book": 2.0,
    "roe": 0.34
  }
}
```

### 3. Relative 평가 계산

```
방법: 비교 회사의 멀티플 × 대상 회사의 재무지표

Step 1: 넷 이익 기반 PE 평가
────────────────────────────
PE 멀티플 (평균): 46.3배
대상사 순이익: 13.5억원
───────────────────
Valuation (PE): 13.5억 × 46.3 = 624.55억원

Step 2: 매출 기반 EV/Revenue 평가
──────────────────────────────
EV/Revenue (평균): 3.5배
대상사 매출: 150억원
──────────────────
Enterprise Value: 150억 × 3.5 = 525억원

Step 3: EBITDA 기반 EV/EBITDA 평가
────────────────────────────────
EV/EBITDA (평균): 23.1배
대상사 EBITDA: 22.5억원
─────────────────────
Enterprise Value: 22.5억 × 23.1 = 519.75억원

Step 4: 부채 조정
────────────────
부채 금액: 50억원
현금 잔액: 10억원
─────────────────

Equity Value 계산:
- PE 기반: 624.55억원
- EV/Revenue → Equity: 525억 - 50억 + 10억 = 485억원
- EV/EBITDA → Equity: 519.75억 - 50억 + 10억 = 479.75억원

평균 Equity Value: (624.55 + 485 + 479.75) / 3 = 529.77억원
```

### 4. 최종 평가

```json
{
  "relative_valuation_result": {
    "pe_based": 62455000000,
    "ev_revenue_based": 48500000000,
    "ev_ebitda_based": 47975000000,
    "average_valuation": 52976667000,
    "recommendation": 53000000000,

    "multiple_analysis": {
      "target_pe": 46.3,
      "our_pe_implied": 39.3,
      "conclusion": "시장보다 약간 저평가"
    }
  }
}
```

---

## 부동산 임대업 (Asset 평가)

### 1. 회사 정보

```json
{
  "company": {
    "name_kr": "부동산투자 주식회사",
    "business": "서울시 강남 상가 임대 사업",
    "portfolio": "강남 3구 상가 5개동"
  },

  "asset_portfolio": {
    "real_estate": [
      {
        "id": "강남1",
        "location": "강남구 테헤란로 123",
        "building_area": 5000,
        "land_area": 2500,
        "stories": 5,
        "rent_units": 20,
        "monthly_rent_total": 50000000,
        "annual_rent": 600000000,
        "property_value": 10000000000,
        "acquisition_cost": 8000000000
      },
      {
        "id": "강남2",
        "location": "강남구 역삼로 456",
        "building_area": 3000,
        "land_area": 1500,
        "stories": 3,
        "rent_units": 12,
        "monthly_rent_total": 30000000,
        "annual_rent": 360000000,
        "property_value": 6000000000,
        "acquisition_cost": 5000000000
      }
    ]
  }
}
```

### 2. Asset 평가 계산

```
Asset 평가 = 자산 가치 + 영업권 - 부채

┌────────────────────────────────────────────────┐
│ 1. 실물 자산 (부동산) 가치 평가                   │
├────────────────────────────────────────────────┤
│                                                │
│ 부동산 1: 강남1                                │
│   현재 공시지가: 10,000백만원                  │
│   평가액 조정: 1.1배 (프리미엄)                │
│   = 11,000백만원                              │
│                                                │
│ 부동산 2: 강남2                                │
│   현재 공시지가: 6,000백만원                   │
│   평가액 조정: 1.0배 (보수적)                  │
│   = 6,000백만원                               │
│                                                │
│ 소계: 17,000백만원                             │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 2. 영업권 (Goodwill) 평가                       │
├────────────────────────────────────────────────┤
│                                                │
│ 임대사업 현황:                                 │
│   - 총 임대료: 960백만원/년 (2개 건물)        │
│   - 임대료 성장률: 연 3%                      │
│   - 임차인 만족도: 95% (높음)                 │
│   - 공실률: 5% (매우 낮음)                    │
│                                                │
│ 영업권 평가:                                   │
│   기본: 순임대료 × 5배                        │
│   = (960백만 × 0.95) × 5                     │
│   = 912백만 × 5                              │
│   = 4,560백만원                               │
│                                                │
│ 조정: 우수한 임차인 구성 → 1.2배 상향조정      │
│   = 4,560백만 × 1.2                          │
│   = 5,472백만원                               │
│                                                │
│ 소계: 5,472백만원                              │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 3. 차용금 (부채)                                │
├────────────────────────────────────────────────┤
│                                                │
│ 은행 대출금:                                   │
│   - 부동산 1 관련 차입: 3,000백만원            │
│   - 부동산 2 관련 차입: 1,500백만원            │
│                                                │
│ 소계 부채: 4,500백만원                         │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 최종 자산 평가 (Asset Valuation)               │
├────────────────────────────────────────────────┤
│                                                │
│ 실물자산가치:        17,000백만원              │
│ + 영업권:              5,472백만원              │
│ - 부채:               -4,500백만원              │
│ ─────────────────────────────                │
│ = 순자산 (Equity):    17,972백만원 ≈ 180억원  │
│                                                │
│ 최종 평가가: 약 180억원                        │
└────────────────────────────────────────────────┘
```

### 3. 수익 기반 추가 검증

```
부동산 임대사업 수익 분석:

연 임대수익: 960백만원
운영비 (20%): -192백만원
순수익: 768백만원

수익률 분석:
- 순수익 / 순자산 = 768백만 / 17,972백만
- = 4.3% (연 수익률)

비교:
- 일반 부동산 투자: 2-3% (서울)
- 우수 물건: 3-5%
- 본 물건: 4.3% (우수 수준)

결론: 수익성 양호, Asset 평가 타당
```

### 4. 최종 평가

```json
{
  "asset_valuation_result": {
    "real_estate_value": 17000000000,
    "goodwill": 5472000000,
    "total_assets": 22472000000,
    "debt": 4500000000,
    "equity_value": 17972000000,
    "valuation_rounded": 18000000000,

    "valuation_method": "Asset-Based",
    "reliability": "Medium-High (★★★★☆)",
    "reasoning": "명확한 자산 가치 + 안정적 수익",

    "rental_yield": 0.043,
    "comment": "4.3% 연수익률 (우수 수준)"
  }
}
```

---

## 세 가지 평가 방법 비교

### 요약표

| 항목 | IT 스타트업 (DCF) | 제조업 (Relative) | 부동산 (Asset) |
|------|------------------|-----------------|-----------------|
| **평가가** | 117억원 | 53억원 | 180억원 |
| **적합성** | ★★★★★ | ★★★★★ | ★★★★★ |
| **신뢰도** | 높음 | 중상 | 중상 |
| **특징** | 성장성 중심 | 시장 비교 | 자산 중심 |
| **필요 정보** | 재무제표 + 계획 | 비교사 정보 | 자산 정보 |
| **비용** | 높음 (1.5배) | 기본 (1.0배) | 중간 (1.2배) |
| **소요시간** | 3주 | 2주 | 2주 |

### 선택 가이드

```
상황별 추천 평가 방법:

1. 빠른 성장 기업?
   → DCF (성장성 반영)

2. 안정적 기업?
   → Relative (시장 비교)

3. 자산 중심 사업?
   → Asset (자산 가치)

4. 금융 기업?
   → Intrinsic (ROE 중심)

5. 세무 용도?
   → Tax (법적 기준)

6. 확실하지 않으면?
   → 복수 방법 (2-3개) 병행
```

---

## 실무 팁

### 1. 데이터 품질 확인

```
✓ 재무제표 사용 전 체크리스트:
  - [ ] 공인 회계감사 완료?
  - [ ] 세무 신고와 일치?
  - [ ] 감사 지적 사항 없음?
  - [ ] 최신 데이터 (6개월 내)?
```

### 2. 가정의 보수성

```
평가 시 가정은 보수적으로:

성장률: 산업 평균 - 2~3%
마진율: 과거 평균 (개선 미반영)
할인율: 평균 + 1~2% (리스크 반영)

결과: 저평가 가능성 → 안전 마진
```

### 3. 민감도 분석의 활용

```
평가 결과 제시:
- 최악 시나리오: 92억원
- 기본 시나리오: 117억원
- 최고 시나리오: 270억원

→ 투자자: "90억 ~270억 범위, 기본값 117억"
   (단순 숫자보다 범위 제시가 신뢰도 높음)
```

### 4. 외부 검증

```
평가 완료 후:

1. 업계 전문가 의견 수렴
2. 비슷한 회사 실거래 비교
3. 시장 컨센서스 확인
4. 투자자 반응 추적

→ 평가의 정확성 검증
```

---

## JSON 템플릿 (실제 사용용)

### DCF 평가 입력 템플릿

```json
{
  "evaluation": {
    "company_name": "평가 대상 회사",
    "evaluation_date": "2026-02-23",
    "method": "DCF",

    "financials": {
      "current_revenue": 0,
      "net_income": 0,
      "free_cash_flow": 0
    },

    "assumptions": {
      "revenue_growth_years_1_5": 0.0,
      "ebitda_margin": 0.0,
      "tax_rate": 0.22,
      "capex_percent_revenue": 0.0,
      "nwc_change_percent": 0.0,
      "wacc": 0.12,
      "perpetual_growth": 0.03
    },

    "output": {
      "enterprise_value": 0,
      "equity_value": 0,
      "valuation_range_low": 0,
      "valuation_range_high": 0
    }
  }
}
```

---

## 추가 리소스

- **코드 스타일 가이드**: `code-style-guide.md`
- **사용자 가이드**: `user-guide-enhanced.md`
- **14단계 워크플로우**: `user-guide-enhanced.md` 섹션 참고

---

**최종 업데이트**: 2026-02-23
**버전**: 1.0 (초판)
**다음 업데이트 예정**: 2026-05-23

**문의**: contact@valuelink.co.kr
