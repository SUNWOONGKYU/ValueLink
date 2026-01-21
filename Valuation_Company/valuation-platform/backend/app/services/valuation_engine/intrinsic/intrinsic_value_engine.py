"""
본질가치 평가법 엔진 (Intrinsic Value Valuation Engine)
자산가치와 수익가치의 가중평균 기반 평가

작성일: 2025-10-17
최종 수정: 2026-01-20
핵심 질문: "기업의 본질적인 가치는 얼마인가?"
"""

from typing import Dict, Optional


class CapitalMarketLawEngine:
    """자본시장법 평가법 엔진"""

    def __init__(self):
        pass

    def run_valuation(self,
                     asset_value: float,
                     income_value: float,
                     purpose: str = '합병') -> Dict:
        """
        자본시장법 평가 실행

        법적 근거: 자본시장법 시행령 제176조의5
        계산식: (자산가치 × 1 + 수익가치 × 1.5) ÷ 2.5

        Args:
            asset_value: 자산가치 (백만원) - NAV 또는 순자산 시가
            income_value: 수익가치 (백만원) - DCF 결과 또는 순이익×10
            purpose: 평가 목적 ('합병', '분할', '주식매수청구권' 등)

        Returns:
            {
                'cml_value': 자본시장법 평가액,
                'asset_value': 자산가치,
                'income_value': 수익가치,
                'asset_weight': 자산가치 가중치 (1),
                'income_weight': 수익가치 가중치 (1.5),
                'divisor': 제수 (2.5),
                'value_per_share': 주당 가치,
                'purpose': 평가 목적,
                'legal_basis': 법적 근거
            }
        """

        # 1. 자본시장법 평가액 계산
        asset_weight = 1.0
        income_weight = 1.5
        divisor = 2.5

        cml_value = (asset_value * asset_weight + income_value * income_weight) / divisor

        return {
            'cml_value': round(cml_value, 0),
            'asset_value': round(asset_value, 0),
            'income_value': round(income_value, 0),
            'asset_weight': asset_weight,
            'income_weight': income_weight,
            'divisor': divisor,
            'purpose': purpose,
            'legal_basis': '자본시장과 금융투자업에 관한 법률 시행령 제176조의5',
            'formula': f'({asset_value:,.0f} × {asset_weight} + {income_value:,.0f} × {income_weight}) ÷ {divisor}',
            'calculation_breakdown': {
                'asset_weighted': round(asset_value * asset_weight, 0),
                'income_weighted': round(income_value * income_weight, 0),
                'sum': round(asset_value * asset_weight + income_value * income_weight, 0)
            }
        }

    def calculate_income_value_method1(self, net_income_3yr_avg: float) -> float:
        """
        수익가치 방법 1: 평균 순이익 × 10

        Args:
            net_income_3yr_avg: 최근 3년 평균 순이익 (백만원)

        Returns:
            수익가치 (백만원)
        """
        return net_income_3yr_avg * 10

    def calculate_income_value_method2(self, dcf_value: float) -> float:
        """
        수익가치 방법 2: DCF 평가 결과 사용

        Args:
            dcf_value: DCF로 산출한 기업가치 (백만원)

        Returns:
            수익가치 (백만원)
        """
        return dcf_value

    def calculate_value_per_share(self, cml_value: float, shares_outstanding: int) -> float:
        """
        주당 가치 계산

        Args:
            cml_value: 자본시장법 평가액 (백만원)
            shares_outstanding: 발행주식수

        Returns:
            주당 가치 (원)
        """
        return (cml_value * 1_000_000) / shares_outstanding

    def generate_full_report(self,
                            asset_value: float,
                            income_value: float,
                            shares_outstanding: int,
                            purpose: str = '합병',
                            income_method: str = 'DCF') -> Dict:
        """
        자본시장법 평가 전체 보고서 생성

        Args:
            asset_value: 자산가치 (백만원)
            income_value: 수익가치 (백만원)
            shares_outstanding: 발행주식수
            purpose: 평가 목적
            income_method: 수익가치 산정 방법 ('DCF' or '평균순이익×10')

        Returns:
            전체 보고서 Dict
        """
        # 1. 자본시장법 평가
        result = self.run_valuation(asset_value, income_value, purpose)

        # 2. 주당 가치
        value_per_share = self.calculate_value_per_share(result['cml_value'], shares_outstanding)

        # 3. 보고서 통합
        report = {
            **result,
            'value_per_share': round(value_per_share, 0),
            'shares_outstanding': shares_outstanding,
            'income_method': income_method,
            'summary': self._generate_summary(result, value_per_share, purpose)
        }

        return report

    def _generate_summary(self, result: Dict, value_per_share: float, purpose: str) -> str:
        """평가 요약 텍스트 생성"""
        summary = f"""
╔════════════════════════════════════════════════════════════╗
║           자본시장법 평가 요약                              ║
╠════════════════════════════════════════════════════════════╣
║ 평가 목적: {purpose}
║ 법적 근거: {result['legal_basis']}
║
║ [계산 과정]
║ • 자산가치: {result['asset_value']:,}백만원 (가중치 {result['asset_weight']})
║ • 수익가치: {result['income_value']:,}백만원 (가중치 {result['income_weight']})
║
║ • 가중합계: {result['calculation_breakdown']['sum']:,}백만원
║ • 제수: {result['divisor']}
║
║ [최종 평가액]
║ • 기업가치: {result['cml_value']:,}백만원
║ • 주당가치: {value_per_share:,.0f}원
╚════════════════════════════════════════════════════════════╝
        """
        return summary.strip()


# ==================== 테스트 코드 ====================

if __name__ == "__main__":
    # 테스트 데이터
    print("=" * 60)
    print("자본시장법 평가 테스트")
    print("=" * 60)

    # Case 1: DCF 수익가치 사용
    print("\n[Case 1: DCF 수익가치 사용]")

    asset_value = 74_221  # NAV 742억
    dcf_value = 73_545  # DCF 기업가치 735억
    shares = 1_000_000

    engine = CapitalMarketLawEngine()
    result = engine.generate_full_report(
        asset_value=asset_value,
        income_value=dcf_value,
        shares_outstanding=shares,
        purpose='합병',
        income_method='DCF'
    )

    print(result['summary'])
    print(f"\n계산식: {result['formula']}")

    # Case 2: 평균순이익 × 10 방법
    print("\n" + "=" * 60)
    print("\n[Case 2: 평균순이익 × 10 방법]")

    net_income_3yr_avg = 11_667  # 3년 평균 순이익 117억 (100억, 120억, 130억)
    income_value_method1 = engine.calculate_income_value_method1(net_income_3yr_avg)

    result2 = engine.generate_full_report(
        asset_value=asset_value,
        income_value=income_value_method1,
        shares_outstanding=shares,
        purpose='주식매수청구권',
        income_method='평균순이익×10'
    )

    print(result2['summary'])

    # Case 3: 비교
    print("\n" + "=" * 60)
    print("\n[두 방법 비교]")
    print(f"• DCF 방법: {result['cml_value']:,}백만원 ({result['value_per_share']:,}원/주)")
    print(f"• 평균순이익×10 방법: {result2['cml_value']:,}백만원 ({result2['value_per_share']:,}원/주)")
    print(f"• 차이: {result2['cml_value'] - result['cml_value']:+,}백만원 "
          f"({(result2['cml_value'] / result['cml_value'] - 1) * 100:+.1f}%)")

    print("\n" + "=" * 60)

    # Case 4: 실전 예시 - 분할
    print("\n[Case 4: 실전 예시 - 회사 분할]")

    asset_value_company_a = 100_000  # 분할 전 자산가치 1,000억
    dcf_value_company_a = 150_000  # 분할 전 DCF 1,500억
    shares_company_a = 2_000_000

    result_before = engine.generate_full_report(
        asset_value=asset_value_company_a,
        income_value=dcf_value_company_a,
        shares_outstanding=shares_company_a,
        purpose='분할 전 평가',
        income_method='DCF'
    )

    print(f"\n분할 전 평가:")
    print(f"  기업가치: {result_before['cml_value']:,}백만원")
    print(f"  주당가치: {result_before['value_per_share']:,}원")

    # 분할 후 (60:40 비율)
    asset_value_new_a = asset_value_company_a * 0.6
    income_value_new_a = dcf_value_company_a * 0.6

    asset_value_new_b = asset_value_company_a * 0.4
    income_value_new_b = dcf_value_company_a * 0.4

    result_new_a = engine.run_valuation(asset_value_new_a, income_value_new_a, '분할 후 A사')
    result_new_b = engine.run_valuation(asset_value_new_b, income_value_new_b, '분할 후 B사')

    print(f"\n분할 후 평가:")
    print(f"  A사 (60%): {result_new_a['cml_value']:,}백만원")
    print(f"  B사 (40%): {result_new_b['cml_value']:,}백만원")
    print(f"  합계: {result_new_a['cml_value'] + result_new_b['cml_value']:,}백만원")
    print(f"  분할 전과 차이: {(result_new_a['cml_value'] + result_new_b['cml_value']) - result_before['cml_value']:+,}백만원")

    print("\n" + "=" * 60)
