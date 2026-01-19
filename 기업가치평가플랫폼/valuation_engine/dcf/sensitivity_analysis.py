"""
DCF 민감도 분석 모듈

WACC와 영구성장률 변화에 따른 주당가치 변동 분석

Author: Valuation Engine Team
Date: 2025-10-17
"""

import sys
sys.path.append('..')

from typing import List, Dict, Tuple
import numpy as np
from common.financial_math import FinancialCalculator


class SensitivityAnalyzer:
    """민감도 분석 클래스"""

    def __init__(self):
        self.calc = FinancialCalculator()

    def create_wacc_growth_matrix(self,
                                  projections: List[Dict],
                                  base_wacc: float,
                                  base_growth: float,
                                  adjustments: Dict,
                                  wacc_range: Tuple[float, float] = (-0.02, 0.02),
                                  growth_range: Tuple[float, float] = (-0.01, 0.01),
                                  steps: int = 5) -> Dict:
        """
        WACC vs 영구성장률 민감도 분석 매트릭스 생성

        Args:
            projections: FCF 예측 데이터
            base_wacc: 기준 WACC
            base_growth: 기준 영구성장률
            adjustments: 조정 항목 (순부채, 주식수 등)
            wacc_range: WACC 변동 범위 (min, max)
            growth_range: 성장률 변동 범위 (min, max)
            steps: 단계 수

        Returns:
            Dict: 민감도 분석 결과
                {
                    'wacc_values': [0.075, 0.085, 0.095, 0.105, 0.115],
                    'growth_values': [0.02, 0.025, 0.03, 0.035, 0.04],
                    'value_matrix': [[...], [...], ...],
                    'base_case': {...}
                }
        """
        # WACC 범위
        wacc_min = base_wacc + wacc_range[0]
        wacc_max = base_wacc + wacc_range[1]
        wacc_values = np.linspace(wacc_min, wacc_max, steps).tolist()

        # 성장률 범위
        growth_min = base_growth + growth_range[0]
        growth_max = base_growth + growth_range[1]
        growth_values = np.linspace(growth_min, growth_max, steps).tolist()

        # FCF 추출
        fcf_list = [p['fcf'] for p in projections]
        last_fcf = fcf_list[-1]
        periods = len(projections)

        # 순부채 및 주식수
        net_debt = adjustments.get('total_debt', 0) - adjustments.get('cash', 0)
        non_op_assets = adjustments.get('non_operating_assets', 0)
        shares = adjustments['shares_outstanding']

        # 매트릭스 계산
        value_matrix = []

        for wacc in wacc_values:
            row = []
            for growth in growth_values:
                # 무효한 조합 (WACC <= 성장률)
                if wacc <= growth:
                    row.append(None)
                    continue

                # PV(FCF) 계산
                pv_fcf = sum(fcf / (1 + wacc) ** (t + 1)
                           for t, fcf in enumerate(fcf_list))

                # Terminal Value 계산
                fcf_next = last_fcf * (1 + growth)
                tv = fcf_next / (wacc - growth)
                pv_tv = tv / (1 + wacc) ** periods

                # 기업가치
                ev = pv_fcf + pv_tv

                # 주주가치
                equity_value = ev - net_debt + non_op_assets

                # 주당가치
                value_per_share = equity_value / shares

                row.append(int(value_per_share))

            value_matrix.append(row)

        # 기준 케이스 계산
        base_pv_fcf = sum(fcf / (1 + base_wacc) ** (t + 1)
                         for t, fcf in enumerate(fcf_list))
        base_fcf_next = last_fcf * (1 + base_growth)
        base_tv = base_fcf_next / (base_wacc - base_growth)
        base_pv_tv = base_tv / (1 + base_wacc) ** periods
        base_ev = base_pv_fcf + base_pv_tv
        base_equity = base_ev - net_debt + non_op_assets
        base_value_per_share = base_equity / shares

        return {
            'wacc_values': wacc_values,
            'growth_values': growth_values,
            'value_matrix': value_matrix,
            'base_case': {
                'wacc': base_wacc,
                'growth': base_growth,
                'value_per_share': base_value_per_share,
                'pv_fcf': base_pv_fcf,
                'pv_tv': base_pv_tv
            }
        }

    def calculate_key_sensitivities(self,
                                   sensitivity_result: Dict) -> Dict:
        """
        주요 민감도 지표 계산

        Returns:
            Dict: 민감도 요약
                - WACC 1% 변동 시 가치 변화율
                - 성장률 0.5% 변동 시 가치 변화율
                - 최대/최소 가치 범위
        """
        matrix = sensitivity_result['value_matrix']
        wacc_values = sensitivity_result['wacc_values']
        growth_values = sensitivity_result['growth_values']
        base_value = sensitivity_result['base_case']['value_per_share']

        # 중앙값 찾기 (base case)
        mid_wacc_idx = len(wacc_values) // 2
        mid_growth_idx = len(growth_values) // 2

        # WACC 민감도 (성장률 고정)
        if mid_wacc_idx > 0 and mid_wacc_idx < len(wacc_values) - 1:
            value_at_wacc_minus_1pct = matrix[mid_wacc_idx - 1][mid_growth_idx]
            value_at_wacc_plus_1pct = matrix[mid_wacc_idx + 1][mid_growth_idx]

            if value_at_wacc_minus_1pct and value_at_wacc_plus_1pct:
                wacc_sensitivity = ((value_at_wacc_minus_1pct - value_at_wacc_plus_1pct) /
                                   base_value)
        else:
            wacc_sensitivity = None

        # 성장률 민감도 (WACC 고정)
        if mid_growth_idx > 0 and mid_growth_idx < len(growth_values) - 1:
            value_at_growth_minus = matrix[mid_wacc_idx][mid_growth_idx - 1]
            value_at_growth_plus = matrix[mid_wacc_idx][mid_growth_idx + 1]

            if value_at_growth_minus and value_at_growth_plus:
                growth_sensitivity = ((value_at_growth_plus - value_at_growth_minus) /
                                     base_value)
        else:
            growth_sensitivity = None

        # 최대/최소 범위
        valid_values = [v for row in matrix for v in row if v is not None]
        max_value = max(valid_values) if valid_values else None
        min_value = min(valid_values) if valid_values else None

        value_range = (max_value - min_value) if (max_value and min_value) else None
        range_percentage = (value_range / base_value) if value_range else None

        return {
            'wacc_sensitivity_pct': wacc_sensitivity * 100 if wacc_sensitivity else None,
            'growth_sensitivity_pct': growth_sensitivity * 100 if growth_sensitivity else None,
            'max_value': max_value,
            'min_value': min_value,
            'value_range': value_range,
            'range_percentage': range_percentage * 100 if range_percentage else None,
            'base_value': base_value
        }

    def scenario_analysis(self,
                         projections: List[Dict],
                         base_wacc: float,
                         base_growth: float,
                         adjustments: Dict) -> Dict:
        """
        시나리오 분석 (낙관/기준/비관)

        Returns:
            Dict: 3가지 시나리오 결과
        """
        scenarios = {
            'bull_case': {  # 낙관적
                'wacc': base_wacc - 0.01,  # WACC -1%p
                'growth': base_growth + 0.005,  # 성장률 +0.5%p
                'description': '낙관적 시나리오 (저 WACC, 고성장)'
            },
            'base_case': {  # 기준
                'wacc': base_wacc,
                'growth': base_growth,
                'description': '기준 시나리오'
            },
            'bear_case': {  # 비관적
                'wacc': base_wacc + 0.01,  # WACC +1%p
                'growth': base_growth - 0.005,  # 성장률 -0.5%p
                'description': '비관적 시나리오 (고 WACC, 저성장)'
            }
        }

        fcf_list = [p['fcf'] for p in projections]
        last_fcf = fcf_list[-1]
        periods = len(projections)
        net_debt = adjustments.get('total_debt', 0) - adjustments.get('cash', 0)
        non_op_assets = adjustments.get('non_operating_assets', 0)
        shares = adjustments['shares_outstanding']

        results = {}

        for scenario_name, params in scenarios.items():
            wacc = params['wacc']
            growth = params['growth']

            # PV(FCF)
            pv_fcf = sum(fcf / (1 + wacc) ** (t + 1)
                        for t, fcf in enumerate(fcf_list))

            # Terminal Value
            fcf_next = last_fcf * (1 + growth)
            tv = fcf_next / (wacc - growth)
            pv_tv = tv / (1 + wacc) ** periods

            # 기업가치
            ev = pv_fcf + pv_tv

            # 주주가치
            equity_value = ev - net_debt + non_op_assets
            value_per_share = equity_value / shares

            results[scenario_name] = {
                'description': params['description'],
                'wacc': wacc,
                'growth': growth,
                'pv_fcf': pv_fcf,
                'pv_tv': pv_tv,
                'enterprise_value': ev,
                'equity_value': equity_value,
                'value_per_share': value_per_share
            }

        return results


# 테스트
if __name__ == "__main__":
    print("=" * 80)
    print("Sensitivity Analysis - Test")
    print("=" * 80)

    # 샘플 데이터
    test_projections = [
        {'year': 2025, 'fcf': 14000000000},
        {'year': 2026, 'fcf': 15000000000},
        {'year': 2027, 'fcf': 16000000000},
        {'year': 2028, 'fcf': 16500000000},
        {'year': 2029, 'fcf': 16891226352}
    ]

    test_adjustments = {
        'cash': 10000000000,
        'total_debt': 30000000000,
        'non_operating_assets': 5000000000,
        'shares_outstanding': 10000000
    }

    analyzer = SensitivityAnalyzer()

    # 민감도 분석
    print("\n[1] WACC vs 성장률 민감도 분석")
    sensitivity = analyzer.create_wacc_growth_matrix(
        projections=test_projections,
        base_wacc=0.0945,
        base_growth=0.03,
        adjustments=test_adjustments
    )

    print(f"\nBase Case 주당가치: {sensitivity['base_case']['value_per_share']:,.0f}원")
    print(f"\nWACC 범위: {sensitivity['wacc_values'][0]:.2%} ~ {sensitivity['wacc_values'][-1]:.2%}")
    print(f"성장률 범위: {sensitivity['growth_values'][0]:.2%} ~ {sensitivity['growth_values'][-1]:.2%}")

    # 민감도 매트릭스 출력
    print("\n민감도 매트릭스 (주당가치, 원):")
    print(f"{'WACC\\성장률':<12}", end="")
    for g in sensitivity['growth_values']:
        print(f"{g:>10.1%}", end="")
    print()

    for i, wacc in enumerate(sensitivity['wacc_values']):
        print(f"{wacc:<12.2%}", end="")
        for value in sensitivity['value_matrix'][i]:
            if value:
                print(f"{value:>10,}", end="")
            else:
                print(f"{'N/A':>10}", end="")
        print()

    # 주요 민감도 지표
    print("\n[2] 주요 민감도 지표")
    key_sens = analyzer.calculate_key_sensitivities(sensitivity)
    print(f"WACC 1%p 변동 시 가치 변화: {key_sens['wacc_sensitivity_pct']:.2f}%")
    print(f"성장률 0.5%p 변동 시 가치 변화: {key_sens['growth_sensitivity_pct']:.2f}%")
    print(f"최대값: {key_sens['max_value']:,.0f}원")
    print(f"최소값: {key_sens['min_value']:,.0f}원")
    print(f"가치 범위: {key_sens['range_percentage']:.2f}%")

    # 시나리오 분석
    print("\n[3] 시나리오 분석")
    scenarios = analyzer.scenario_analysis(
        projections=test_projections,
        base_wacc=0.0945,
        base_growth=0.03,
        adjustments=test_adjustments
    )

    for scenario_name, result in scenarios.items():
        print(f"\n{scenario_name.upper()}: {result['description']}")
        print(f"  WACC: {result['wacc']:.2%}, 성장률: {result['growth']:.2%}")
        print(f"  주당가치: {result['value_per_share']:,.0f}원")

    print("\n" + "=" * 80)
