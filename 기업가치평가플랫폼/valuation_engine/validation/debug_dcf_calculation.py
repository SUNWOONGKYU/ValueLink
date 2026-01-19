# -*- coding: utf-8 -*-
"""
DCF 계산 상세 디버깅
"""
import sys
sys.path.append('..')

from dcf.dcf_engine import DCFEngine
import json

# 테크밸리 데이터
techvalley_inputs = {
    'company_id': 'TECHVALLEY',
    'company_name': '주식회사 테크밸리',
    'valuation_date': '2024-12-31',
    'historical_financials': [
        {
            'year': 2021,
            'revenue': 8500,
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
    'assumptions': {
        'base_year': 2023,
        'revenue_growth': [0.440, 0.350, 0.300, 0.228, 0.200],
        'target_operating_margin': 0.160,
        'tax_rate': 0.22,
        'depreciation_rate': 0.017,
        'capex_rate': 0.030,
        'wc_rate': 0.015,
        'terminal_growth': 0.025
    },
    'wacc_inputs': {
        'risk_free_rate': 0.040,
        'beta': 1.15,
        'market_premium': 0.070,
        'cost_of_debt': 0.050,
        'debt_ratio': 0.15,
        'tax_rate': 0.22
    },
    'adjustments': {
        'cash': 1200,
        'total_debt': 500,
        'non_operating_assets': 0,
        'shares_outstanding': 1000000
    }
}

print("=" * 80)
print("DCF 계산 상세 디버깅")
print("=" * 80)

# DCF 엔진 실행
engine = DCFEngine()
result = engine.run_valuation(techvalley_inputs)

print("\n" + "=" * 80)
print("1. WACC 상세 분석")
print("=" * 80)

wacc_components = result['wacc']
print(f"\n자기자본비용 (Re):")
print(f"  Rf = {wacc_components['components']['risk_free_rate']:.4f}")
print(f"  Beta = {wacc_components['components']['beta']:.2f}")
print(f"  MRP = {wacc_components['components']['market_premium']:.4f}")
print(f"  Re = Rf + Beta x MRP = {wacc_components['cost_of_equity']:.4f}")
print(f"  예상: 0.1205")

print(f"\n타인자본비용 (Rd):")
print(f"  Rd(세전) = {wacc_components['components']['cost_of_debt']:.4f}")
print(f"  세율 = {wacc_components['components']['tax_rate']:.2f}")
print(f"  Rd(세후) = {wacc_components['after_tax_cost_of_debt']:.4f}")
print(f"  예상: 0.0390")

print(f"\n가중치:")
print(f"  자기자본 비중 (E/(E+D)) = {wacc_components['equity_weight']:.2f}")
print(f"  타인자본 비중 (D/(E+D)) = {wacc_components['debt_weight']:.2f}")
print(f"  예상: 0.85 / 0.15")

print(f"\nWACC:")
print(f"  실제 = {wacc_components['wacc']:.4f} ({wacc_components['wacc']:.2%})")
print(f"  예상 = 0.0965 (9.65%)")
print(f"  차이 = {abs(wacc_components['wacc'] - 0.0965):.4f}")

print("\n" + "=" * 80)
print("2. 예측 재무제표 분석")
print("=" * 80)

print(f"\n{'연도':<10} {'매출액':>12} {'영업이익':>12} {'NOPAT':>12} {'FCF':>12}")
print("-" * 60)

for proj in result['projections']:
    print(f"{proj['year']:<10} {proj['revenue']:>12,.0f} {proj['operating_income']:>12,.0f} "
          f"{proj['nopat']:>12,.0f} {proj['fcf']:>12,.0f}")

print("\n예상 FCF:")
print("  2024E: 2,487")
print("  2025E: 3,730")
print("  2026E: 5,274")
print("  2027E: 6,840")
print("  2028E: 8,601")

print("\n" + "=" * 80)
print("3. 영구가치 분석")
print("=" * 80)

tv = result['terminal_value']
print(f"\n최종 FCF (2028): {tv['last_fcf']:,.0f}")
print(f"영구성장률: {tv['terminal_growth']:.2%}")
print(f"WACC: {wacc_components['wacc']:.4f}")
print(f"자본환원율 (WACC - g): {tv['capitalization_rate']:.4f}")
print(f"\nTV = FCF × (1+g) / (WACC-g)")
print(f"   = {tv['last_fcf']:,.0f} × 1.025 / {tv['capitalization_rate']:.4f}")
print(f"   = {tv['terminal_value']:,.0f}")
print(f"\n예상 TV: 123,014")
print(f"실제 TV: {tv['terminal_value']:,.0f}")
print(f"차이: {abs(tv['terminal_value'] - 123014):,.0f}")

print("\n" + "=" * 80)
print("4. 현재가치 할인 분석")
print("=" * 80)

print(f"\n{'연도':<10} {'FCF':>12} {'할인계수':>12} {'PV(FCF)':>12}")
print("-" * 50)

for pv in result['discounted_fcf']['pv_fcf_by_year']:
    print(f"{pv['year']:<10} {pv['fcf']:>12,.0f} {pv['discount_factor']:>12.4f} {pv['pv_fcf']:>12,.0f}")

print(f"\nPV(FCF) 합계: {result['discounted_fcf']['total_pv_fcf']:,.0f}")
print(f"예상: 19,532")

print(f"\nPV(TV): {tv['pv_terminal_value']:,.0f}")
print(f"예상: 77,659")

print("\n" + "=" * 80)
print("5. 기업가치 및 주주가치")
print("=" * 80)

ev_result = result['valuation_result']
print(f"\nPV(FCF): {ev_result['pv_fcf']:,.0f}")
print(f"PV(TV): {ev_result['pv_terminal_value']:,.0f}")
print(f"기업가치 (EV): {ev_result['enterprise_value']:,.0f}")
print(f"예상: 97,191")

print(f"\n현금: {techvalley_inputs['adjustments']['cash']:,.0f}")
print(f"차입금: {techvalley_inputs['adjustments']['total_debt']:,.0f}")
print(f"순차입금: {ev_result['net_debt']:,.0f}")
print(f"예상 순차입금: -700 (순현금)")

print(f"\n주주가치: {ev_result['equity_value']:,.0f}")
print(f"예상: 97,891")

print(f"\n주당가치: {ev_result['value_per_share']:,.0f}")
print(f"예상: 97,891원")

print("\n" + "=" * 80)
print("6. 문제점 요약")
print("=" * 80)

problems = []

if abs(wacc_components['wacc'] - 0.0965) > 0.001:
    problems.append(f"WACC 차이: {abs(wacc_components['wacc'] - 0.0965):.4f}")

if abs(ev_result['enterprise_value'] - 97191) / 97191 > 0.05:
    problems.append(f"기업가치 오차: {abs(ev_result['enterprise_value'] - 97191) / 97191 * 100:.1f}%")

if abs(ev_result['equity_value'] - 97891) / 97891 > 0.05:
    problems.append(f"주주가치 오차: {abs(ev_result['equity_value'] - 97891) / 97891 * 100:.1f}%")

if ev_result['value_per_share'] < 1000:
    problems.append(f"주당가치 계산 오류: {ev_result['value_per_share']:,.0f}원")

if problems:
    print("\n발견된 문제:")
    for i, prob in enumerate(problems, 1):
        print(f"  {i}. {prob}")
else:
    print("\n문제 없음!")

print("\n" + "=" * 80)
