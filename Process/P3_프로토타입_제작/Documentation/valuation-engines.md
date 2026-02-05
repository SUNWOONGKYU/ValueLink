# ValueLink 평가 엔진 문서

**작성일**: 2026-02-05
**버전**: 1.0
**언어**: Python 3.11+
**프레임워크**: FastAPI

---

## 개요

ValueLink 플랫폼의 **5개 평가 엔진**을 문서화합니다.

### 엔진 목록

| # | 엔진명 | 파일 | 코드 줄 수 | 상태 |
|---|--------|------|----------|------|
| 1 | **DCF** | `dcf_engine.py` | 504줄 | ✅ 완료 |
| 2 | **Relative** | `relative_engine.py` | 487줄 | ✅ 완료 |
| 3 | **Asset** | `asset_engine.py` | 497줄 | ✅ 완료 |
| 4 | **Intrinsic** | `intrinsic_engine.py` | 258줄 | ✅ 완료 |
| 5 | **Tax** | `tax_engine.py` | 379줄 | ✅ 완료 |

**총 코드**: 2,125줄 (평가 엔진만)
**전체 코드**: 6,645줄 (Orchestrator 포함)

---

## 1. DCF 평가 엔진 (Discounted Cash Flow)

### 1.1 개요

**파일**: `backend/app/services/valuation_engine/dcf/dcf_engine.py`
**코드 줄 수**: 504줄
**방법론**: 현금흐름할인법

### 1.2 주요 기능

```
1. 5년 현금흐름 예측
2. WACC (가중평균자본비용) 계산
3. 영속가치 (Terminal Value) 계산
4. 기업가치 (Enterprise Value) 산출
5. 주당가치 (Per Share Value) 산출
```

### 1.3 입력 데이터

```python
class DCFInput:
    # 재무 데이터
    revenue: List[float]                # 매출 (3년치)
    operating_income: List[float]       # 영업이익 (3년치)
    net_income: List[float]             # 당기순이익 (3년치)
    total_assets: float                 # 총자산
    total_liabilities: float            # 총부채
    equity: float                       # 자본

    # 가정 데이터
    revenue_growth_rate: float          # 매출 성장률
    operating_margin: float             # 영업이익률
    tax_rate: float                     # 세율 (기본 22%)
    capex_rate: float                   # CAPEX 비율
    working_capital_change_rate: float  # 운전자본 변동률

    # WACC 계산
    risk_free_rate: float               # 무위험 이자율 (국고채)
    market_risk_premium: float          # 시장 위험 프리미엄
    beta: float                         # 베타
    debt_ratio: float                   # 부채 비율
    cost_of_debt: float                 # 부채 비용

    # 영속가치
    perpetual_growth_rate: float        # 영구 성장률 (기본 2%)

    # 기타
    shares_outstanding: int             # 발행 주식 수
```

### 1.4 계산 로직

#### Step 1: 자유현금흐름 (FCF) 예측

```python
def calculate_fcf(year: int, input_data: DCFInput) -> float:
    """
    자유현금흐름 = EBIT * (1 - 세율) + 감가상각 - CAPEX - 운전자본 변동
    """
    # 매출 예측
    revenue = input_data.revenue[-1] * (1 + input_data.revenue_growth_rate) ** year

    # EBIT (영업이익)
    ebit = revenue * input_data.operating_margin

    # NOPAT (세후영업이익)
    nopat = ebit * (1 - input_data.tax_rate)

    # 감가상각 (매출의 3% 가정)
    depreciation = revenue * 0.03

    # CAPEX (매출의 5% 가정 또는 입력값 사용)
    capex = revenue * input_data.capex_rate

    # 운전자본 변동
    working_capital_change = revenue * input_data.working_capital_change_rate

    # FCF 계산
    fcf = nopat + depreciation - capex - working_capital_change

    return fcf
```

#### Step 2: WACC (가중평균자본비용) 계산

```python
def calculate_wacc(input_data: DCFInput) -> float:
    """
    WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)

    E: 자본 시장가치
    D: 부채 시장가치
    V: 기업 가치 (E + D)
    Re: 자본 비용
    Rd: 부채 비용
    Tc: 법인세율
    """
    # CAPM으로 자본 비용 계산
    # Re = Rf + β * (Rm - Rf)
    cost_of_equity = (
        input_data.risk_free_rate +
        input_data.beta * input_data.market_risk_premium
    )

    # 부채/자본 비율
    debt_to_value = input_data.debt_ratio
    equity_to_value = 1 - debt_to_value

    # WACC 계산
    wacc = (
        equity_to_value * cost_of_equity +
        debt_to_value * input_data.cost_of_debt * (1 - input_data.tax_rate)
    )

    return wacc
```

#### Step 3: 현재가치 할인

```python
def discount_fcf(fcf_list: List[float], wacc: float) -> float:
    """
    각 연도 FCF를 현재가치로 할인
    PV = FCF / (1 + WACC)^t
    """
    pv_fcf = sum(
        fcf / (1 + wacc) ** (year + 1)
        for year, fcf in enumerate(fcf_list)
    )

    return pv_fcf
```

#### Step 4: 영속가치 (Terminal Value) 계산

```python
def calculate_terminal_value(fcf_year5: float, wacc: float, g: float) -> float:
    """
    영속가치 = FCF(Year 5) * (1 + g) / (WACC - g)

    fcf_year5: 5년차 FCF
    g: 영구 성장률 (일반적으로 2%)
    """
    tv = fcf_year5 * (1 + g) / (wacc - g)
    pv_tv = tv / (1 + wacc) ** 5

    return pv_tv
```

#### Step 5: 기업가치 및 주당가치 계산

```python
def calculate_valuation(input_data: DCFInput) -> DCFOutput:
    """
    기업가치 = PV(FCF 5년) + PV(영속가치)
    주당가치 = (기업가치 - 순부채) / 발행주식수
    """
    # 1. 5년 FCF 예측
    fcf_list = [calculate_fcf(year, input_data) for year in range(1, 6)]

    # 2. WACC 계산
    wacc = calculate_wacc(input_data)

    # 3. FCF 현재가치 할인
    pv_fcf = discount_fcf(fcf_list, wacc)

    # 4. 영속가치 계산
    pv_tv = calculate_terminal_value(fcf_list[-1], wacc, input_data.perpetual_growth_rate)

    # 5. 기업가치
    enterprise_value = pv_fcf + pv_tv

    # 6. 순부채
    net_debt = input_data.total_liabilities - (input_data.total_assets * 0.1)  # 현금성 자산 10% 가정

    # 7. 자본가치
    equity_value = enterprise_value - net_debt

    # 8. 주당가치
    value_per_share = equity_value / input_data.shares_outstanding

    return DCFOutput(
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        value_per_share=value_per_share,
        fcf_list=fcf_list,
        wacc=wacc,
        terminal_value=pv_tv
    )
```

### 1.5 출력 데이터

```python
class DCFOutput:
    enterprise_value: float              # 기업가치
    equity_value: float                  # 자본가치
    value_per_share: float               # 주당가치
    fcf_list: List[float]                # 5년 FCF 리스트
    wacc: float                          # WACC
    terminal_value: float                # 영속가치 현재가치
    pv_fcf: float                        # FCF 현재가치 합계

    # 세부 내역 (JSON)
    calculation_details: Dict = {
        "fcf_year_1": float,
        "fcf_year_2": float,
        "fcf_year_3": float,
        "fcf_year_4": float,
        "fcf_year_5": float,
        "pv_fcf": float,
        "terminal_value": float,
        "pv_terminal_value": float,
        "enterprise_value": float,
        "net_debt": float,
        "equity_value": float,
        "shares_outstanding": int,
        "value_per_share": float,
        "wacc": float,
        "cost_of_equity": float,
        "cost_of_debt": float,
    }
```

---

## 2. Relative 평가 엔진 (Comparable Company Analysis)

### 2.1 개요

**파일**: `backend/app/services/valuation_engine/relative/relative_engine.py`
**코드 줄 수**: 487줄
**방법론**: 상대가치 평가법 (유사 기업 비교)

### 2.2 주요 기능

```
1. 유사 기업 선정
2. 배수 계산 (P/E, P/S, EV/EBITDA)
3. 평균/중간값 산출
4. 평가 대상 기업가치 계산
```

### 2.3 입력 데이터

```python
class RelativeInput:
    # 평가 대상 기업
    company_name: str
    revenue: float                      # 매출
    net_income: float                   # 당기순이익
    ebitda: float                       # EBITDA
    shares_outstanding: int             # 발행 주식 수

    # 유사 기업 목록 (3~5개)
    comparable_companies: List[ComparableCompany]

    # 배수 선택
    multiples: List[str]                # ['pe', 'ps', 'ev_ebitda']

class ComparableCompany:
    name: str
    market_cap: float                   # 시가총액
    enterprise_value: float             # 기업가치
    revenue: float                      # 매출
    net_income: float                   # 당기순이익
    ebitda: float                       # EBITDA
```

### 2.4 계산 로직

#### Step 1: 유사 기업 배수 계산

```python
def calculate_multiples(comparable: ComparableCompany) -> Dict[str, float]:
    """
    P/E = 시가총액 / 당기순이익
    P/S = 시가총액 / 매출
    EV/EBITDA = 기업가치 / EBITDA
    """
    pe_ratio = comparable.market_cap / comparable.net_income if comparable.net_income > 0 else 0
    ps_ratio = comparable.market_cap / comparable.revenue if comparable.revenue > 0 else 0
    ev_ebitda = comparable.enterprise_value / comparable.ebitda if comparable.ebitda > 0 else 0

    return {
        'pe': pe_ratio,
        'ps': ps_ratio,
        'ev_ebitda': ev_ebitda
    }
```

#### Step 2: 평균/중간값 산출

```python
def calculate_average_multiples(comparables: List[ComparableCompany]) -> Dict[str, float]:
    """
    평균 배수 및 중간값 계산
    """
    multiples_list = [calculate_multiples(comp) for comp in comparables]

    pe_values = [m['pe'] for m in multiples_list if m['pe'] > 0]
    ps_values = [m['ps'] for m in multiples_list if m['ps'] > 0]
    ev_ebitda_values = [m['ev_ebitda'] for m in multiples_list if m['ev_ebitda'] > 0]

    return {
        'pe_mean': sum(pe_values) / len(pe_values) if pe_values else 0,
        'pe_median': sorted(pe_values)[len(pe_values) // 2] if pe_values else 0,
        'ps_mean': sum(ps_values) / len(ps_values) if ps_values else 0,
        'ps_median': sorted(ps_values)[len(ps_values) // 2] if ps_values else 0,
        'ev_ebitda_mean': sum(ev_ebitda_values) / len(ev_ebitda_values) if ev_ebitda_values else 0,
        'ev_ebitda_median': sorted(ev_ebitda_values)[len(ev_ebitda_values) // 2] if ev_ebitda_values else 0,
    }
```

#### Step 3: 평가 대상 기업가치 계산

```python
def calculate_valuation(input_data: RelativeInput) -> RelativeOutput:
    """
    평가 대상 기업가치 = 평균 배수 × 평가 대상 기업 지표
    """
    avg_multiples = calculate_average_multiples(input_data.comparable_companies)

    # P/E 기반 가치
    pe_valuation = avg_multiples['pe_mean'] * input_data.net_income

    # P/S 기반 가치
    ps_valuation = avg_multiples['ps_mean'] * input_data.revenue

    # EV/EBITDA 기반 가치
    ev_ebitda_valuation = avg_multiples['ev_ebitda_mean'] * input_data.ebitda

    # 평균 기업가치
    enterprise_value = (pe_valuation + ps_valuation + ev_ebitda_valuation) / 3

    # 주당가치 (시가총액 기준)
    value_per_share = pe_valuation / input_data.shares_outstanding

    return RelativeOutput(
        enterprise_value=enterprise_value,
        equity_value=pe_valuation,
        value_per_share=value_per_share,
        pe_valuation=pe_valuation,
        ps_valuation=ps_valuation,
        ev_ebitda_valuation=ev_ebitda_valuation,
        avg_multiples=avg_multiples
    )
```

---

## 3. Asset 평가 엔진 (Net Asset Value)

### 3.1 개요

**파일**: `backend/app/services/valuation_engine/asset/asset_engine.py`
**코드 줄 수**: 497줄
**방법론**: 자산가치 평가법 (순자산가치)

### 3.2 주요 기능

```
1. 자산 재평가 (부동산, 설비, 재고 등)
2. 부채 조정 (장부가치 → 시장가치)
3. 순자산가치 계산
```

### 3.3 입력 데이터

```python
class AssetInput:
    # 자산 항목
    current_assets: float               # 유동자산
    fixed_assets: float                 # 고정자산
    intangible_assets: float            # 무형자산

    # 자산 재평가
    real_estate_book_value: float       # 부동산 장부가치
    real_estate_market_value: float     # 부동산 시장가치
    equipment_book_value: float         # 설비 장부가치
    equipment_market_value: float       # 설비 시장가치
    inventory_book_value: float         # 재고 장부가치
    inventory_market_value: float       # 재고 시장가치

    # 부채 항목
    current_liabilities: float          # 유동부채
    long_term_liabilities: float        # 장기부채

    # 부채 조정
    debt_book_value: float              # 부채 장부가치
    debt_market_value: float            # 부채 시장가치

    # 기타
    shares_outstanding: int             # 발행 주식 수
```

### 3.4 계산 로직

```python
def calculate_valuation(input_data: AssetInput) -> AssetOutput:
    """
    순자산가치 = 재평가 후 자산 - 조정 후 부채
    """
    # 자산 재평가
    revalued_assets = (
        input_data.current_assets +
        input_data.real_estate_market_value +
        input_data.equipment_market_value +
        input_data.inventory_market_value +
        input_data.intangible_assets
    )

    # 부채 조정
    adjusted_liabilities = (
        input_data.current_liabilities +
        input_data.debt_market_value
    )

    # 순자산가치
    net_asset_value = revalued_assets - adjusted_liabilities

    # 주당 순자산가치
    nav_per_share = net_asset_value / input_data.shares_outstanding

    return AssetOutput(
        enterprise_value=net_asset_value,
        equity_value=net_asset_value,
        value_per_share=nav_per_share,
        revalued_assets=revalued_assets,
        adjusted_liabilities=adjusted_liabilities
    )
```

---

## 4. Intrinsic 평가 엔진 (Hybrid Method)

### 4.1 개요

**파일**: `backend/app/services/valuation_engine/intrinsic/intrinsic_engine.py`
**코드 줄 수**: 258줄
**방법론**: 본질가치 평가법 (수익가치 + 순자산가치 가중평균)

### 4.2 계산 로직

```python
def calculate_valuation(dcf_value: float, asset_value: float) -> IntrinsicOutput:
    """
    본질가치 = (수익가치 × 0.6) + (순자산가치 × 0.4)

    비상장기업 평가에 적합
    """
    intrinsic_value = (dcf_value * 0.6) + (asset_value * 0.4)

    return IntrinsicOutput(
        enterprise_value=intrinsic_value,
        equity_value=intrinsic_value,
        dcf_weight=0.6,
        asset_weight=0.4
    )
```

---

## 5. Tax 평가 엔진 (상증법 평가)

### 5.1 개요

**파일**: `backend/app/services/valuation_engine/tax/tax_engine.py`
**코드 줄 수**: 379줄
**방법론**: 상속세 및 증여세법 기준 평가

### 5.2 주요 기능

```
1. 최근 3년 순손익 평균 계산
2. 순자산가치 계산
3. 1주당 가액 산출 (3:2 가중평균)
```

### 5.3 계산 로직

```python
def calculate_valuation(input_data: TaxInput) -> TaxOutput:
    """
    상증법 기준 평가

    1주당 순손익가치 = (최근 3년 순이익 평균 ÷ 0.1) ÷ 발행주식수
    1주당 순자산가치 = 순자산 ÷ 발행주식수
    1주당 가액 = (1주당 순손익가치 × 3 + 1주당 순자산가치 × 2) ÷ 5
    """
    # 최근 3년 순이익 평균
    avg_net_income = sum(input_data.net_income_3years) / 3

    # 1주당 순손익가치
    earnings_per_share = (avg_net_income / 0.1) / input_data.shares_outstanding

    # 1주당 순자산가치
    net_asset_per_share = input_data.net_assets / input_data.shares_outstanding

    # 1주당 가액 (3:2 가중평균)
    value_per_share = (earnings_per_share * 3 + net_asset_per_share * 2) / 5

    # 총 기업가치
    enterprise_value = value_per_share * input_data.shares_outstanding

    return TaxOutput(
        enterprise_value=enterprise_value,
        equity_value=enterprise_value,
        value_per_share=value_per_share,
        earnings_per_share=earnings_per_share,
        net_asset_per_share=net_asset_per_share
    )
```

---

## 6. FastAPI 통합

### 6.1 API 엔드포인트

```python
# backend/app/api/v1/endpoints/valuation.py

@router.post("/valuation/dcf")
async def dcf_valuation(input_data: DCFInput) -> DCFOutput:
    """DCF 평가 API"""
    from app.services.valuation_engine.dcf import dcf_engine
    result = dcf_engine.calculate_valuation(input_data)
    return result

@router.post("/valuation/relative")
async def relative_valuation(input_data: RelativeInput) -> RelativeOutput:
    """상대가치 평가 API"""
    from app.services.valuation_engine.relative import relative_engine
    result = relative_engine.calculate_valuation(input_data)
    return result

@router.post("/valuation/asset")
async def asset_valuation(input_data: AssetInput) -> AssetOutput:
    """자산가치 평가 API"""
    from app.services.valuation_engine.asset import asset_engine
    result = asset_engine.calculate_valuation(input_data)
    return result

@router.post("/valuation/intrinsic")
async def intrinsic_valuation(
    dcf_value: float,
    asset_value: float
) -> IntrinsicOutput:
    """본질가치 평가 API"""
    from app.services.valuation_engine.intrinsic import intrinsic_engine
    result = intrinsic_engine.calculate_valuation(dcf_value, asset_value)
    return result

@router.post("/valuation/tax")
async def tax_valuation(input_data: TaxInput) -> TaxOutput:
    """상증법 평가 API"""
    from app.services.valuation_engine.tax import tax_engine
    result = tax_engine.calculate_valuation(input_data)
    return result
```

### 6.2 Vercel Serverless Function 래퍼 (계획)

```typescript
// api/valuation/dcf.ts
import { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // FastAPI 엔드포인트 호출
  const response = await fetch('https://fastapi.valuation.ai.kr/api/v1/valuation/dcf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req.body),
  });

  const result = await response.json();
  res.status(200).json(result);
}
```

---

## 7. 테스트

### 7.1 단위 테스트

```python
# backend/tests/test_dcf_engine.py

def test_dcf_calculation():
    input_data = DCFInput(
        revenue=[1000000000, 1200000000, 1400000000],
        operating_income=[150000000, 180000000, 210000000],
        net_income=[100000000, 120000000, 140000000],
        total_assets=2000000000,
        total_liabilities=800000000,
        equity=1200000000,
        revenue_growth_rate=0.15,
        operating_margin=0.15,
        tax_rate=0.22,
        capex_rate=0.05,
        working_capital_change_rate=0.02,
        risk_free_rate=0.03,
        market_risk_premium=0.06,
        beta=1.2,
        debt_ratio=0.4,
        cost_of_debt=0.04,
        perpetual_growth_rate=0.02,
        shares_outstanding=1000000
    )

    result = dcf_engine.calculate_valuation(input_data)

    assert result.enterprise_value > 0
    assert result.equity_value > 0
    assert result.value_per_share > 0
    assert len(result.fcf_list) == 5
```

---

## 요약

```
✅ 5개 평가 엔진 문서화 완료
✅ 총 2,125줄 코드
✅ 각 엔진별 입력/출력 명세
✅ 계산 로직 상세 설명
✅ FastAPI 통합 방법
✅ 테스트 방법
```

**재구축 전략**: Python 엔진 유지 + Vercel Edge Function 래퍼

**작성자**: Claude Code
**참조**: 기존 Python 코드 (backend/app/services/valuation_engine/)
**버전**: 1.0
**작성일**: 2026-02-05
