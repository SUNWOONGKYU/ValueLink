"""
상대가치평가법 엔진 (Relative Valuation Engine)
Market Approach - PER, PBR, PSR, EV/EBITDA

작성일: 2025-10-17
핵심 질문: "시장은 유사 기업을 얼마라고 평가할까?"
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class ValuationResult:
    """개별 평가 결과"""
    method: str  # "PER", "PBR", "PSR", "EV/EBITDA"
    multiple: float  # 사용한 배수
    value: float  # 산출 가치 (백만원)
    value_per_share: float  # 주당 가치 (원)
    confidence: str  # "High", "Medium", "Low"
    notes: str  # 추가 설명


class RelativeValuationEngine:
    """상대가치평가법 엔진"""

    def __init__(self):
        self.results: List[ValuationResult] = []

    def run_valuation(self,
                     company_data: Dict,
                     comparable_companies: Optional[List[Dict]] = None,
                     industry_benchmarks: Optional[Dict] = None) -> Dict:
        """
        전체 상대가치평가 실행

        Args:
            company_data: 대상 기업 재무 데이터
            comparable_companies: 비교기업 리스트
            industry_benchmarks: 업종 평균 배수

        Returns:
            {
                'per_valuation': {...},
                'pbr_valuation': {...},
                'psr_valuation': {...},
                'ev_ebitda_valuation': {...},
                'integrated': {...}
            }
        """
        results = {}

        # 1. PER 평가 (흑자 기업만)
        if company_data.get('net_income', 0) > 0:
            results['per_valuation'] = self.calculate_per_valuation(
                company_data, comparable_companies, industry_benchmarks
            )

        # 2. PBR 평가
        results['pbr_valuation'] = self.calculate_pbr_valuation(
            company_data, comparable_companies, industry_benchmarks
        )

        # 3. PSR 평가
        results['psr_valuation'] = self.calculate_psr_valuation(
            company_data, comparable_companies, industry_benchmarks
        )

        # 4. EV/EBITDA 평가
        if company_data.get('ebitda', 0) > 0:
            results['ev_ebitda_valuation'] = self.calculate_ev_ebitda_valuation(
                company_data, comparable_companies, industry_benchmarks
            )

        # 5. 통합 결과
        results['integrated'] = self.integrate_results(results, company_data)

        return results

    # ==================== PER 평가 ====================

    def calculate_per_valuation(self,
                               company_data: Dict,
                               comparables: Optional[List[Dict]] = None,
                               benchmarks: Optional[Dict] = None) -> Dict:
        """
        PER (Price-to-Earnings Ratio) 배수법 평가

        계산식: 기업가치 = 순이익 × PER

        PER 선택 우선순위:
            1. 비교기업 평균 PER
            2. 업종 평균 PER
            3. 시장 기본 PER (10배)
        """
        net_income = company_data['net_income']  # 백만원
        shares = company_data['shares_outstanding']

        # PER 결정
        if comparables and len(comparables) > 0:
            # 비교기업 PER 추출
            per_list = [c['per'] for c in comparables if c.get('per') and c['per'] > 0]

            if len(per_list) >= 3:
                # 이상치 제거
                per_clean = self._remove_outliers(per_list)

                # 평균 및 중위값
                per_mean = statistics.mean(per_clean)
                per_median = statistics.median(per_clean)

                # 중위값 선호 (평균은 극단값에 민감)
                per_selected = per_median
            else:
                per_selected = statistics.mean(per_list) if per_list else 10.0
                per_mean = per_selected
                per_median = per_selected

        elif benchmarks:
            per_selected = benchmarks.get('median_per', benchmarks.get('avg_per', 10.0))
            per_mean = benchmarks.get('avg_per')
            per_median = benchmarks.get('median_per')
        else:
            # 기본값: 한국 시장 평균 PER 10배
            per_selected = 10.0
            per_mean = 10.0
            per_median = 10.0

        # 조정: 성장률 고려
        growth_rate = company_data.get('growth_rate_3yr', 0)
        if growth_rate > 0.15:  # 15% 이상 고성장
            per_adjusted = per_selected * 1.2  # 20% 프리미엄
            adjustment_reason = f"고성장 (성장률 {growth_rate:.1%}) 20% 프리미엄"
        elif growth_rate < 0.05:  # 5% 미만 저성장
            per_adjusted = per_selected * 0.9  # 10% 할인
            adjustment_reason = f"저성장 (성장률 {growth_rate:.1%}) 10% 할인"
        else:
            per_adjusted = per_selected
            adjustment_reason = "조정 없음"

        # 가치 계산
        equity_value = net_income * per_adjusted  # 백만원
        value_per_share = (equity_value * 1_000_000) / shares  # 원

        return {
            'method': 'PER',
            'multiple_used': round(per_adjusted, 2),
            'net_income': net_income,
            'equity_value': round(equity_value, 0),
            'value_per_share': round(value_per_share, 0),
            'comparables_per_mean': round(per_mean, 2) if comparables else None,
            'comparables_per_median': round(per_median, 2) if comparables else None,
            'adjustment_factor': round(per_adjusted / per_selected, 2),
            'adjustment_reason': adjustment_reason,
            'confidence': 'High' if comparables else 'Medium'
        }

    # ==================== PBR 평가 ====================

    def calculate_pbr_valuation(self,
                               company_data: Dict,
                               comparables: Optional[List[Dict]] = None,
                               benchmarks: Optional[Dict] = None) -> Dict:
        """
        PBR (Price-to-Book Ratio) 배수법 평가

        계산식: 기업가치 = 순자산 × PBR

        적합성:
            - ROE > 자기자본비용이면 PBR > 1.0
            - 자산 집약 산업 (제조, 금융)
        """
        book_value = company_data['book_value']  # 백만원
        shares = company_data['shares_outstanding']
        roe = company_data.get('roe', 0)

        # PBR 결정
        if comparables and len(comparables) > 0:
            pbr_list = [c['pbr'] for c in comparables if c.get('pbr') and c['pbr'] > 0]

            if len(pbr_list) >= 3:
                pbr_clean = self._remove_outliers(pbr_list)
                pbr_selected = statistics.median(pbr_clean)
            else:
                pbr_selected = statistics.mean(pbr_list) if pbr_list else 1.0

        elif benchmarks:
            pbr_selected = benchmarks.get('median_pbr', benchmarks.get('avg_pbr', 1.0))
        else:
            pbr_selected = 1.0  # 기본값

        # 조정: ROE 고려
        # 이론: PBR = ROE / Ke (자기자본비용)
        if roe > 0.15:  # ROE 15% 이상
            pbr_adjusted = pbr_selected * 1.3
            adjustment_reason = f"고ROE ({roe:.1%}) 30% 프리미엄"
        elif roe < 0.08:  # ROE 8% 미만
            pbr_adjusted = pbr_selected * 0.8
            adjustment_reason = f"저ROE ({roe:.1%}) 20% 할인"
        else:
            pbr_adjusted = pbr_selected
            adjustment_reason = "조정 없음"

        # 가치 계산
        equity_value = book_value * pbr_adjusted
        value_per_share = (equity_value * 1_000_000) / shares

        return {
            'method': 'PBR',
            'multiple_used': round(pbr_adjusted, 2),
            'book_value': book_value,
            'equity_value': round(equity_value, 0),
            'value_per_share': round(value_per_share, 0),
            'roe': round(roe, 4),
            'adjustment_reason': adjustment_reason,
            'confidence': 'High' if comparables else 'Medium'
        }

    # ==================== PSR 평가 ====================

    def calculate_psr_valuation(self,
                               company_data: Dict,
                               comparables: Optional[List[Dict]] = None,
                               benchmarks: Optional[Dict] = None) -> Dict:
        """
        PSR (Price-to-Sales Ratio) 배수법 평가

        계산식: 기업가치 = 매출액 × PSR

        적합성:
            - 적자 기업 (순이익 음수)
            - 초기 성장 기업
            - 매출 기반 비즈니스
        """
        revenue = company_data['revenue']  # 백만원
        shares = company_data['shares_outstanding']

        # PSR 결정
        if comparables and len(comparables) > 0:
            psr_list = [c['psr'] for c in comparables if c.get('psr') and c['psr'] > 0]

            if len(psr_list) >= 3:
                psr_clean = self._remove_outliers(psr_list)
                psr_selected = statistics.median(psr_clean)
            else:
                psr_selected = statistics.mean(psr_list) if psr_list else 2.0

        elif benchmarks:
            psr_selected = benchmarks.get('median_psr', benchmarks.get('avg_psr', 2.0))
        else:
            # 산업별 기본값
            industry = company_data.get('industry', '')
            if 'SaaS' in industry or '소프트웨어' in industry:
                psr_selected = 5.0
            elif '유통' in industry or '플랫폼' in industry:
                psr_selected = 1.5
            else:
                psr_selected = 2.0

        # 가치 계산
        equity_value = revenue * psr_selected
        value_per_share = (equity_value * 1_000_000) / shares

        return {
            'method': 'PSR',
            'multiple_used': round(psr_selected, 2),
            'revenue': revenue,
            'equity_value': round(equity_value, 0),
            'value_per_share': round(value_per_share, 0),
            'confidence': 'Medium'  # PSR은 수익성 미반영
        }

    # ==================== EV/EBITDA 평가 ====================

    def calculate_ev_ebitda_valuation(self,
                                     company_data: Dict,
                                     comparables: Optional[List[Dict]] = None,
                                     benchmarks: Optional[Dict] = None) -> Dict:
        """
        EV/EBITDA 배수법 평가

        계산식:
            기업가치 (EV) = EBITDA × (EV/EBITDA 배수)
            주주가치 = EV - 순부채

        장점:
            - 자본구조 영향 배제
            - 국가 간 비교 가능 (세율 무관)
            - M&A에서 가장 많이 사용
        """
        ebitda = company_data['ebitda']  # 백만원
        shares = company_data['shares_outstanding']

        # 순부채 계산
        total_debt = company_data.get('total_debt', 0)
        cash = company_data.get('cash', 0)
        net_debt = total_debt - cash

        # EV/EBITDA 배수 결정
        if comparables and len(comparables) > 0:
            ev_ebitda_list = [c['ev_ebitda'] for c in comparables
                             if c.get('ev_ebitda') and c['ev_ebitda'] > 0]

            if len(ev_ebitda_list) >= 3:
                ev_ebitda_clean = self._remove_outliers(ev_ebitda_list)
                ev_ebitda_selected = statistics.median(ev_ebitda_clean)
            else:
                ev_ebitda_selected = statistics.mean(ev_ebitda_list) if ev_ebitda_list else 8.0

        elif benchmarks:
            ev_ebitda_selected = benchmarks.get('median_ev_ebitda',
                                               benchmarks.get('avg_ev_ebitda', 8.0))
        else:
            ev_ebitda_selected = 8.0  # 산업 평균

        # 가치 계산
        enterprise_value = ebitda * ev_ebitda_selected  # 기업가치
        equity_value = enterprise_value - net_debt  # 주주가치
        value_per_share = (equity_value * 1_000_000) / shares

        return {
            'method': 'EV/EBITDA',
            'multiple_used': round(ev_ebitda_selected, 2),
            'ebitda': ebitda,
            'enterprise_value': round(enterprise_value, 0),
            'net_debt': net_debt,
            'equity_value': round(equity_value, 0),
            'value_per_share': round(value_per_share, 0),
            'confidence': 'High'  # M&A 표준
        }

    # ==================== 유틸리티 함수 ====================

    def _remove_outliers(self, data: List[float]) -> List[float]:
        """
        IQR(Interquartile Range) 방법으로 이상치 제거

        IQR = Q3 - Q1
        하한 = Q1 - 1.5 × IQR
        상한 = Q3 + 1.5 × IQR
        """
        if len(data) < 4:
            return data

        sorted_data = sorted(data)
        q1 = statistics.quantiles(sorted_data, n=4)[0]  # 25%
        q3 = statistics.quantiles(sorted_data, n=4)[2]  # 75%
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [x for x in data if lower_bound <= x <= upper_bound]

    def integrate_results(self, results: Dict, company_data: Dict) -> Dict:
        """
        여러 평가법 결과를 통합하여 최종 가치 산정

        가중치:
            - PER: 40% (흑자 기업)
            - PBR: 20%
            - PSR: 10%
            - EV/EBITDA: 30%
        """
        values = []
        weights = []
        methods = []

        # PER (흑자 기업만)
        if 'per_valuation' in results:
            values.append(results['per_valuation']['equity_value'])
            weights.append(0.40)
            methods.append('PER')

        # PBR
        if 'pbr_valuation' in results:
            values.append(results['pbr_valuation']['equity_value'])
            weights.append(0.20)
            methods.append('PBR')

        # PSR
        if 'psr_valuation' in results:
            values.append(results['psr_valuation']['equity_value'])
            weights.append(0.10)
            methods.append('PSR')

        # EV/EBITDA
        if 'ev_ebitda_valuation' in results:
            values.append(results['ev_ebitda_valuation']['equity_value'])
            weights.append(0.30)
            methods.append('EV/EBITDA')

        # 가중치 정규화
        total_weight = sum(weights)
        weights_normalized = [w / total_weight for w in weights]

        # 가중평균
        weighted_avg = sum(v * w for v, w in zip(values, weights_normalized))

        # 범위
        min_value = min(values)
        max_value = max(values)

        # 주당 가치
        shares = company_data['shares_outstanding']
        value_per_share = (weighted_avg * 1_000_000) / shares

        return {
            'equity_value': round(weighted_avg, 0),
            'value_per_share': round(value_per_share, 0),
            'valuation_range': (round(min_value, 0), round(max_value, 0)),
            'methods_used': methods,
            'weights': dict(zip(methods, [round(w, 2) for w in weights_normalized])),
            'individual_values': dict(zip(methods, [round(v, 0) for v in values]))
        }


# ==================== 테스트 코드 ====================

if __name__ == "__main__":
    # 테스트 데이터
    company_data = {
        "company_name": "테크밸리",
        "industry": "소프트웨어",
        "revenue": 50_000,  # 500억
        "net_income": 6_000,  # 60억
        "book_value": 60_000,  # 600억
        "ebitda": 10_000,  # 100억
        "shares_outstanding": 1_000_000,
        "growth_rate_3yr": 0.25,
        "roe": 0.10,
        "total_debt": 10_000,
        "cash": 5_000,
    }

    comparables = [
        {"name": "A사", "per": 10.0, "pbr": 1.2, "psr": 2.5, "ev_ebitda": 7.5},
        {"name": "B사", "per": 12.0, "pbr": 1.5, "psr": 3.0, "ev_ebitda": 8.0},
        {"name": "C사", "per": 11.5, "pbr": 1.4, "psr": 2.8, "ev_ebitda": 7.8},
    ]

    # 엔진 실행
    engine = RelativeValuationEngine()
    results = engine.run_valuation(company_data, comparables)

    # 결과 출력
    print("=" * 60)
    print("상대가치평가 결과")
    print("=" * 60)

    if 'per_valuation' in results:
        per = results['per_valuation']
        print(f"\n[PER 평가]")
        print(f"  배수: {per['multiple_used']}배")
        print(f"  순이익: {per['net_income']:,}백만원")
        print(f"  기업가치: {per['equity_value']:,}백만원")
        print(f"  주당가치: {per['value_per_share']:,}원")
        print(f"  조정사유: {per['adjustment_reason']}")

    if 'pbr_valuation' in results:
        pbr = results['pbr_valuation']
        print(f"\n[PBR 평가]")
        print(f"  배수: {pbr['multiple_used']}배")
        print(f"  순자산: {pbr['book_value']:,}백만원")
        print(f"  기업가치: {pbr['equity_value']:,}백만원")
        print(f"  주당가치: {pbr['value_per_share']:,}원")

    if 'ev_ebitda_valuation' in results:
        ev = results['ev_ebitda_valuation']
        print(f"\n[EV/EBITDA 평가]")
        print(f"  배수: {ev['multiple_used']}배")
        print(f"  EBITDA: {ev['ebitda']:,}백만원")
        print(f"  기업가치 (EV): {ev['enterprise_value']:,}백만원")
        print(f"  순부채: {ev['net_debt']:,}백만원")
        print(f"  주주가치: {ev['equity_value']:,}백만원")
        print(f"  주당가치: {ev['value_per_share']:,}원")

    integrated = results['integrated']
    print(f"\n[통합 결과]")
    print(f"  최종 기업가치: {integrated['equity_value']:,}백만원")
    print(f"  주당 가치: {integrated['value_per_share']:,}원")
    print(f"  평가 범위: {integrated['valuation_range'][0]:,} ~ {integrated['valuation_range'][1]:,}백만원")
    print(f"  사용 방법: {', '.join(integrated['methods_used'])}")
    print(f"  가중치: {integrated['weights']}")

    print("\n" + "=" * 60)
