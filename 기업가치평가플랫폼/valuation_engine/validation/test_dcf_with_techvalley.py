# -*- coding: utf-8 -*-
"""
테크밸리 DCF 검증 스크립트
제작한 입력 데이터로 DCF 엔진 검증
"""
import sys
sys.path.append('..')

from dcf.dcf_engine import DCFEngine

# 테크밸리 입력 데이터 (단위: 백만원)
techvalley_inputs = {
    'company_id': 'TECHVALLEY',
    'company_name': '주식회사 테크밸리',
    'valuation_date': '2024-12-31',

    # 역사적 재무데이터 (2021-2023)
    'historical_financials': [
        {
            'year': 2021,
            'revenue': 8500,  # 85억
            'operating_income': 850,
            'net_income': 590,
            'depreciation': 300,
            'capex': 400,
            'working_capital_change': 150,
            'tax_rate': 0.22
        },
        {
            'year': 2022,
            'revenue': 12300,
            'operating_income': 1476,
            'net_income': 1020,
            'depreciation': 400,
            'capex': 500,
            'working_capital_change': 200,
            'tax_rate': 0.22
        },
        {
            'year': 2023,
            'revenue': 18500,
            'operating_income': 2775,
            'net_income': 1944,
            'depreciation': 400,
            'capex': 600,
            'working_capital_change': 300,
            'tax_rate': 0.22
        }
    ],

    # 예측 가정
    'assumptions': {
        'base_year': 2023,
        'revenue_growth': [0.440, 0.350, 0.300, 0.228, 0.200],  # 2024-2028
        'target_operating_margin': 0.160,  # 2024년부터 점진적 개선
        'tax_rate': 0.22,
        'depreciation_rate': 0.017,  # 매출액 대비 평균 1.7%
        'capex_rate': 0.030,  # 매출액 대비 평균 3.0%
        'wc_rate': 0.015,  # 매출 증가분 대비 운전자본 증가
        'terminal_growth': 0.025
    },

    # WACC 입력
    'wacc_inputs': {
        'risk_free_rate': 0.040,  # 4.0%
        'beta': 1.15,
        'market_premium': 0.070,  # 7.0%
        'cost_of_debt': 0.050,  # 5.0%
        'debt_ratio': 0.15,  # D/(D+E) = 15%
        'tax_rate': 0.22
    },

    # 조정 항목
    'adjustments': {
        'cash': 1200,  # 현금 12억
        'total_debt': 500,  # 차입금 5억
        'non_operating_assets': 0,
        'shares_outstanding': 1000000  # 발행주식 100만주
    }
}

# 예상 정답 (올바르게 재계산한 값)
expected_results = {
    'enterprise_value': 73521,  # 기업가치 735억
    'equity_value': 74221,  # 주주가치 742억
    'value_per_share': 74221,  # 주당가치 74,221원
    'wacc': 0.1083  # 10.83%
}

if __name__ == "__main__":
    print("=" * 80)
    print("테크밸리 DCF 평가 검증")
    print("=" * 80)

    # DCF 엔진 실행
    engine = DCFEngine()
    result = engine.run_valuation(techvalley_inputs)

    # 결과 비교
    print("\n" + "=" * 80)
    print("결과 비교")
    print("=" * 80)

    actual_ev = result['valuation_result']['enterprise_value']
    actual_equity = result['valuation_result']['equity_value']
    actual_vps = result['valuation_result']['value_per_share']
    actual_wacc = result['wacc']['wacc']

    print(f"\n[기업가치 (Enterprise Value)]")
    print(f"  예상: {expected_results['enterprise_value']:,.0f} 백만원")
    print(f"  실제: {actual_ev:,.0f} 백만원")
    print(f"  차이: {abs(actual_ev - expected_results['enterprise_value']):,.0f} 백만원")
    print(f"  오차율: {abs(actual_ev - expected_results['enterprise_value']) / expected_results['enterprise_value'] * 100:.2f}%")

    print(f"\n[주주가치 (Equity Value)]")
    print(f"  예상: {expected_results['equity_value']:,.0f} 백만원")
    print(f"  실제: {actual_equity:,.0f} 백만원")
    print(f"  차이: {abs(actual_equity - expected_results['equity_value']):,.0f} 백만원")
    print(f"  오차율: {abs(actual_equity - expected_results['equity_value']) / expected_results['equity_value'] * 100:.2f}%")

    print(f"\n[주당가치 (Value per Share)]")
    print(f"  예상: {expected_results['value_per_share']:,.0f}원")
    print(f"  실제: {actual_vps:,.0f}원")
    print(f"  차이: {abs(actual_vps - expected_results['value_per_share']):,.0f}원")
    print(f"  오차율: {abs(actual_vps - expected_results['value_per_share']) / expected_results['value_per_share'] * 100:.2f}%")

    print(f"\n[WACC]")
    print(f"  예상: {expected_results['wacc']:.4f} ({expected_results['wacc']:.2%})")
    print(f"  실제: {actual_wacc:.4f} ({actual_wacc:.2%})")
    print(f"  차이: {abs(actual_wacc - expected_results['wacc']):.4f}")

    # 검증 판단
    print("\n" + "=" * 80)
    print("검증 결과")
    print("=" * 80)

    tolerance = 0.01  # 1% 허용 오차

    ev_pass = abs(actual_ev - expected_results['enterprise_value']) / expected_results['enterprise_value'] < tolerance
    eq_pass = abs(actual_equity - expected_results['equity_value']) / expected_results['equity_value'] < tolerance
    vps_pass = abs(actual_vps - expected_results['value_per_share']) / expected_results['value_per_share'] < tolerance
    wacc_pass = abs(actual_wacc - expected_results['wacc']) < 0.0001

    print(f"기업가치 검증: {'✓ PASS' if ev_pass else '✗ FAIL'}")
    print(f"주주가치 검증: {'✓ PASS' if eq_pass else '✗ FAIL'}")
    print(f"주당가치 검증: {'✓ PASS' if vps_pass else '✗ FAIL'}")
    print(f"WACC 검증: {'✓ PASS' if wacc_pass else '✗ FAIL'}")

    if all([ev_pass, eq_pass, vps_pass, wacc_pass]):
        print("\n✓ 전체 검증 통과: DCF 엔진이 정상 작동합니다!")
    else:
        print("\n✗ 검증 실패: DCF 엔진 로직을 확인해주세요.")

    print("=" * 80)
