# 기업가치평가 플랫폼 마스터 플랜

**작성일**: 2025-10-17
**목표**: 5가지 평가법을 모두 구현한 종합 평가 플랫폼

---

## 현재 상황

### ✅ 완료된 작업
- **DCF 평가법 엔진**: 완전히 구현 및 검증 완료 (오차율 0.03%)
- **시뮬레이션 검증**: 합성 데이터로 완벽 검증
- **버그 수정**: 주당가치 단위 변환 버그 수정

### ❌ 누락된 작업
- **나머지 4가지 평가법 엔진**: 미구현
  1. 상대가치평가법 (PER, PBR, EV/EBITDA)
  2. 자산가치평가법 (NAV)
  3. 자본시장법 평가법
  4. 상증세법 평가법

---

## 5가지 평가법 개요

### 1. DCF 평가법 ✅ (완료)

**핵심 질문**: "이 기업이 미래에 얼마나 벌까?"

**계산 공식**:
```
기업가치 = Σ(FCF ÷ (1+WACC)^t) + Terminal Value
```

**장점**:
- 이론적으로 가장 정교
- 기업 고유 가치 반영
- 전략적 의사결정 유용

**단점**:
- 미래 예측의 불확실성
- 할인율 산정 주관적
- 시간과 노력 多

**적합 상황**:
- M&A 기본 평가
- 안정적 성장기업
- 내부 의사결정

**구현 상태**: ✅ **완료** (valuation_engine/dcf/)

---

### 2. 상대가치평가법 (시장접근법)

**핵심 질문**: "시장은 유사 기업을 얼마라고 평가할까?"

**계산 공식**:
```
기업가치 = 재무지표 × 업종 평균 배수

주요 배수:
- PER (Price-to-Earnings Ratio) = 시가총액 / 순이익
- PBR (Price-to-Book Ratio) = 시가총액 / 순자산
- PSR (Price-to-Sales Ratio) = 시가총액 / 매출액
- EV/EBITDA = 기업가치 / EBITDA
- EV/Sales = 기업가치 / 매출액
```

**장점**:
- 빠르고 직관적
- 시장 현실 반영
- 객관적 비교 가능

**단점**:
- 비교기업 찾기 어려움
- 시장 왜곡 영향
- 기업 특성 반영 제한

**적합 상황**:
- IPO 공모가 산정
- 빠른 의사결정
- 시장성 검증

**구현 계획**:
```python
class RelativeValuationEngine:
    def calculate_per_valuation(self, net_income, industry_per):
        """PER 배수법 평가"""
        return net_income * industry_per

    def calculate_pbr_valuation(self, book_value, industry_pbr):
        """PBR 배수법 평가"""
        return book_value * industry_pbr

    def calculate_ev_ebitda(self, ebitda, industry_multiple):
        """EV/EBITDA 배수법 평가"""
        return ebitda * industry_multiple
```

**필요 데이터**:
- 대상 기업 재무지표 (순이익, 순자산, 매출, EBITDA)
- 업종별 평균 배수 (DB 또는 API)
- 유사 상장기업 데이터

---

### 3. 자산가치평가법 (순자산가치법, NAV)

**핵심 질문**: "지금 자산을 모두 팔면 얼마를 받을 수 있을까?"

**계산 공식**:
```
순자산가치 (NAV) = 자산 시가 - 부채 시가

상세:
NAV = (유동자산 + 유형자산 + 무형자산 + 투자자산)
      - (유동부채 + 비유동부채)

* 각 항목을 시가(공정가치)로 재평가
```

**장점**:
- 객관적이고 검증 가능
- 하한선(Floor) 제시
- 자산 중심 명확

**단점**:
- 무형자산 평가 어려움
- 수익력 미반영
- 계속기업 가치 누락

**적합 상황**:
- 부동산/지주회사
- 청산/구조조정
- 담보가치 산정

**구현 계획**:
```python
class AssetValuationEngine:
    def calculate_nav(self, balance_sheet, fair_value_adjustments):
        """순자산가치 평가"""
        # 1. 자산 시가 평가
        current_assets_fv = self.fair_value_current_assets(...)
        fixed_assets_fv = self.fair_value_fixed_assets(...)
        intangible_assets_fv = self.fair_value_intangibles(...)

        # 2. 부채 시가 평가
        liabilities_fv = self.fair_value_liabilities(...)

        # 3. NAV 계산
        nav = (current_assets_fv + fixed_assets_fv + intangible_assets_fv)
              - liabilities_fv

        return nav
```

**필요 데이터**:
- 재무상태표 (자산/부채 명세)
- 부동산 감정평가서
- 유가증권 시가
- 무형자산 평가 (영업권, 특허 등)

---

### 4. 자본시장법 평가법

**핵심 질문**: "자본시장법이 요구하는 법정 가치는?"

**계산 공식**:
```
자본시장법 평가 = (자산가치 × 1 + 수익가치 × 1.5) ÷ 2.5

여기서:
- 자산가치 = 순자산 시가
- 수익가치 = (최근 3년 평균 순이익 × 10) 또는 DCF 결과
```

**장점**:
- 법적 강제성과 객관성
- 표준화된 방법론
- 분쟁 해결 기준

**단점**:
- 획일적 비율 적용 (1:1.5)
- 기업 특성 반영 제한
- 외부기관 평가 필수

**적합 상황**:
- 합병/분할
- 주식매수청구권 행사
- Pre-IPO 증자

**구현 계획**:
```python
class CapitalMarketLawEngine:
    def calculate_valuation(self, asset_value, income_value):
        """자본시장법 평가"""
        # 가중평균: 자산가치 × 1, 수익가치 × 1.5
        valuation = (asset_value * 1.0 + income_value * 1.5) / 2.5
        return valuation

    def calculate_income_value_method1(self, net_income_3yr_avg):
        """수익가치 방법1: 평균순이익 × 10"""
        return net_income_3yr_avg * 10

    def calculate_income_value_method2(self, dcf_value):
        """수익가치 방법2: DCF 결과 사용"""
        return dcf_value
```

**필요 데이터**:
- 순자산 시가 (자산가치평가법 결과)
- 최근 3년 순이익
- DCF 평가 결과 (선택)

---

### 5. 상증세법 평가법

**핵심 질문**: "상속세 및 증여세법상 평가액은?"

**계산 공식**:
```
상증세법 평가 = (순손익가치 × 3 + 순자산가치 × 2) ÷ 5

여기서:
- 순손익가치 = 최근 3년 평균 순손익 × 3 ÷ 0.10
  (할인율 10% 적용, 영구가치 개념)

- 순자산가치 = 순자산 장부가 (또는 시가)
```

**추가 조정**:
- 최대주주 할증: +20% (지배주주)
- 소액주주 할인: -10% ~ -30%
- 유동성 할인: -20% ~ -30%

**장점**:
- 법적 근거 명확
- 세무 리스크 최소화
- 가업승계 활용

**단점**:
- 세무 목적에 국한
- 할인/할증 복잡
- 시장가치와 괴리

**적합 상황**:
- 상속/증여세 신고
- 가업승계 계획
- 세무 가격 산정

**구현 계획**:
```python
class InheritanceTaxLawEngine:
    def calculate_valuation(self, net_income_3yr, net_assets,
                           controlling_premium=False,
                           minority_discount=0):
        """상증세법 평가"""
        # 1. 순손익가치 계산
        income_value = (net_income_3yr / 3) * 3 / 0.10

        # 2. 순자산가치
        asset_value = net_assets

        # 3. 가중평균
        base_value = (income_value * 3 + asset_value * 2) / 5

        # 4. 할증/할인 적용
        if controlling_premium:
            base_value *= 1.20  # 지배주주 할증
        else:
            base_value *= (1 - minority_discount)  # 소액주주 할인

        return base_value
```

**필요 데이터**:
- 최근 3년 순손익 (세무조정 후)
- 순자산 장부가액 (또는 시가)
- 지배주주/소액주주 구분
- 유동성 할인율

---

## 전체 엔진 아키텍처

### 디렉토리 구조

```
valuation_engine/
├── dcf/                          ✅ 완료
│   ├── dcf_engine.py
│   └── dcf_models.py
│
├── relative/                     🔨 작업 필요
│   ├── relative_engine.py
│   ├── multiples_calculator.py
│   └── industry_data.py
│
├── asset/                        🔨 작업 필요
│   ├── asset_engine.py
│   ├── fair_value_adjuster.py
│   └── appraisal_integration.py
│
├── capital_market_law/           🔨 작업 필요
│   ├── cml_engine.py
│   └── cml_calculator.py
│
├── inheritance_tax_law/          🔨 작업 필요
│   ├── itl_engine.py
│   ├── tax_adjustments.py
│   └── discount_premium.py
│
├── common/                       ✅ 완료
│   ├── financial_math.py
│   └── validators.py
│
└── master/                       🆕 신규
    ├── master_engine.py          # 5가지 평가법 통합
    ├── valuation_selector.py     # 상황별 평가법 선택
    └── cross_checker.py          # 교차 검증
```

---

## Master Engine 설계

### 통합 평가 엔진

```python
# master/master_engine.py

class MasterValuationEngine:
    """5가지 평가법을 통합 실행하는 마스터 엔진"""

    def __init__(self):
        self.dcf_engine = DCFEngine()
        self.relative_engine = RelativeValuationEngine()
        self.asset_engine = AssetValuationEngine()
        self.cml_engine = CapitalMarketLawEngine()
        self.itl_engine = InheritanceTaxLawEngine()

    def run_all_methods(self, company_data, purpose='general'):
        """모든 평가법 실행"""
        results = {}

        # 1. DCF 평가
        results['dcf'] = self.dcf_engine.run_valuation(company_data)

        # 2. 상대가치평가
        results['relative'] = self.relative_engine.run_valuation(company_data)

        # 3. 자산가치평가
        results['asset'] = self.asset_engine.run_valuation(company_data)

        # 4. 자본시장법 평가
        results['capital_market_law'] = self.cml_engine.run_valuation(
            asset_value=results['asset']['nav'],
            income_value=results['dcf']['enterprise_value']
        )

        # 5. 상증세법 평가
        results['inheritance_tax_law'] = self.itl_engine.run_valuation(company_data)

        # 6. 통합 결과
        results['integrated'] = self.integrate_results(results, purpose)

        return results

    def integrate_results(self, results, purpose):
        """평가 목적에 따라 최종 가치 결정"""
        selector = ValuationSelector()
        return selector.select_final_value(results, purpose)
```

### 평가법 선택기

```python
# master/valuation_selector.py

class ValuationSelector:
    """상황별로 적절한 평가법을 선택하고 가중치 부여"""

    def select_final_value(self, results, purpose):
        """평가 목적에 따른 최종 가치 산정"""

        if purpose == 'MA':  # M&A
            # DCF 50%, 상대가치 30%, 자산가치 20%
            weights = {'dcf': 0.50, 'relative': 0.30, 'asset': 0.20}

        elif purpose == 'IPO':  # 기업공개
            # 상대가치 60%, DCF 40%
            weights = {'relative': 0.60, 'dcf': 0.40}

        elif purpose == 'merger':  # 합병
            # 자본시장법 100% (법적 요구)
            weights = {'capital_market_law': 1.00}

        elif purpose == 'inheritance':  # 상속/증여
            # 상증세법 100% (세무 신고)
            weights = {'inheritance_tax_law': 1.00}

        elif purpose == 'liquidation':  # 청산
            # 자산가치 100%
            weights = {'asset': 1.00}

        else:  # 일반적인 경우
            # 5가지 평균
            weights = {
                'dcf': 0.30,
                'relative': 0.25,
                'asset': 0.20,
                'capital_market_law': 0.15,
                'inheritance_tax_law': 0.10
            }

        # 가중평균 계산
        final_value = 0
        for method, weight in weights.items():
            if method in results:
                final_value += results[method]['enterprise_value'] * weight

        return {
            'final_value': final_value,
            'weights': weights,
            'individual_results': results
        }
```

---

## 웹사이트 메뉴 재설계

### 수정된 메뉴 구조

```
🏠 홈

📚 DCF 교육센터
  ├─ Chapter 1: 기업가치평가 개요 (5가지 평가법 소개)
  ├─ Chapter 2: DCF 평가법
  ├─ Chapter 3: 상대가치평가법
  ├─ Chapter 4: 자산가치평가법
  ├─ Chapter 5: 자본시장법 평가법
  ├─ Chapter 6: 상증세법 평가법
  └─ Chapter 7: 5대 평가법 비교 및 선택

🧮 무료 시뮬레이터
  ├─ DCF 계산기 ✅
  ├─ WACC 계산기 ✅
  ├─ PER/PBR 계산기 🆕
  ├─ NAV 계산기 🆕
  ├─ 자본시장법 계산기 🆕
  └─ 상증세법 계산기 🆕

📊 평가보고서 신청
  ├─ 종합 평가 (5가지 방법 모두)    ← 추천
  ├─ DCF 평가만
  ├─ 상대가치평가만
  ├─ 자산가치평가만
  ├─ 자본시장법 평가 (합병/분할용)
  └─ 상증세법 평가 (상속/증여용)

💼 내 프로젝트

💳 가격
  ├─ 단일 평가법: 50만원
  ├─ 종합 평가 (5가지): 150만원 (70% 할인!)
  └─ 프로 구독: 월 200만원 (5건)

ℹ️ 고객지원

👤 내 계정
```

---

## 가격 정책 재설계

### 평가법별 가격

| 평가법 | 단독 가격 | 소요 시간 | 페이지 수 |
|--------|----------|-----------|-----------|
| DCF 평가법 | 50만원 | 36분 | 35p |
| 상대가치평가법 | 30만원 | 15분 | 20p |
| 자산가치평가법 | 40만원 | 25분 | 25p |
| 자본시장법 평가법 | 60만원 | 40분 | 40p |
| 상증세법 평가법 | 40만원 | 20분 | 25p |
| **종합 평가 (5가지)** | **150만원** | **60분** | **80p** |

**할인율**: 종합 평가 시 개별 합계 220만원 → 150만원 (32% 할인)

---

## 보고서 구조 재설계

### 종합 평가보고서 (80페이지)

```
I. 평가 개요 (5p)
   - 평가 대상 및 목적
   - 평가 기준일
   - 평가 방법론 개요
   - 5가지 평가법 요약표

II. 회사 개요 (10p)
   - 회사 연혁
   - 사업 모델
   - 재무 현황
   - 산업 분석

III. 평가법 1: DCF 평가 (15p)
   - WACC 계산
   - FCF 예측
   - 영구가치
   - 평가 결과

IV. 평가법 2: 상대가치평가 (10p)
   - 비교기업 선정
   - 배수 계산
   - 평가 결과

V. 평가법 3: 자산가치평가 (10p)
   - 자산 시가 평가
   - 부채 시가 평가
   - NAV 계산

VI. 평가법 4: 자본시장법 평가 (8p)
   - 자산가치 산정
   - 수익가치 산정
   - 법정 평가액

VII. 평가법 5: 상증세법 평가 (8p)
   - 순손익가치
   - 순자산가치
   - 할증/할인 적용

VIII. 평가 결과 종합 (10p)
   - 5가지 평가 결과 비교
   - 교차 검증
   - 최종 가치 산정
   - 민감도 분석

IX. 결론 및 의견 (4p)
   - 최종 평가 의견
   - 한계점 및 유의사항
```

---

## 개발 로드맵

### Phase 1: 엔진 개발 (4주)

**Week 1: 상대가치평가법 엔진**
- [ ] RelativeValuationEngine 클래스 개발
- [ ] 업종별 배수 DB 구축
- [ ] PER, PBR, PSR, EV/EBITDA 계산
- [ ] 테스트 및 검증

**Week 2: 자산가치평가법 엔진**
- [ ] AssetValuationEngine 클래스 개발
- [ ] 공정가치 조정 로직
- [ ] NAV 계산
- [ ] 테스트 및 검증

**Week 3: 법정 평가법 엔진 (2개)**
- [ ] CapitalMarketLawEngine 개발
- [ ] InheritanceTaxLawEngine 개발
- [ ] 할인/할증 로직
- [ ] 테스트 및 검증

**Week 4: 통합 및 마스터 엔진**
- [ ] MasterValuationEngine 개발
- [ ] ValuationSelector 개발
- [ ] CrossChecker 개발
- [ ] 전체 통합 테스트

### Phase 2: 웹사이트 개발 (4주)

**Week 5-6: 시뮬레이터 확장**
- [ ] PER/PBR 계산기
- [ ] NAV 계산기
- [ ] 자본시장법 계산기
- [ ] 상증세법 계산기

**Week 7: 교육 콘텐츠 통합**
- [ ] 5가지 평가법 전체 강의 업로드
- [ ] PDF 교재 생성 (전체 200p)
- [ ] 동영상 강의 제작

**Week 8: 신청 프로세스**
- [ ] 평가법 선택 UI
- [ ] 결제 시스템 통합
- [ ] 보고서 생성 자동화

### Phase 3: 테스트 및 출시 (2주)

**Week 9: 베타 테스트**
- [ ] 실제 기업 데이터로 테스트
- [ ] 5가지 평가법 교차 검증
- [ ] 버그 수정

**Week 10: 정식 출시**
- [ ] 마케팅 자료 준비
- [ ] 공식 론칭
- [ ] 고객 지원 체계 구축

---

## 우선순위

### 🔥 최우선 작업 (이번 주)

1. **상대가치평가법 엔진 개발** - 가장 쉽고 빠름
2. **PER/PBR 시뮬레이터** - 사용자 체험 중요
3. **교육 콘텐츠 정리** - 이미 있는 자료 통합

### 📌 차순위 작업 (다음 주)

1. 자산가치평가법 엔진
2. 법정 평가법 엔진 (2개)
3. 마스터 엔진 통합

### 🎯 최종 목표

**"문서만 업로드하면 AI가 5가지 방법으로 평가하고 80페이지 종합 보고서를 60분 만에 생성"**

---

**완성!** 이제 5가지 평가법을 모두 구현해야 합니다.
