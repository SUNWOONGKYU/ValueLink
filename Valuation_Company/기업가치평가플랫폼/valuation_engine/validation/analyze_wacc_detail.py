# -*- coding: utf-8 -*-
"""
WACC 계산 상세 분석
예상: 9.65% vs 실제: 10.83% 차이 원인 규명
"""
import sys
sys.path.append('..')

from common.financial_math import FinancialCalculator

print("=" * 80)
print("WACC 계산 상세 분석")
print("=" * 80)

# 입력값
risk_free_rate = 0.040  # 4.0%
beta = 1.15
market_premium = 0.070  # 7.0%
cost_of_debt = 0.050  # 5.0%
debt_ratio = 0.15  # D/(D+E) = 15%
tax_rate = 0.22

print("\n입력 파라미터:")
print(f"  무위험이자율 (Rf) = {risk_free_rate:.4f} ({risk_free_rate:.2%})")
print(f"  베타 (β) = {beta:.2f}")
print(f"  시장위험프리미엄 (MRP) = {market_premium:.4f} ({market_premium:.2%})")
print(f"  타인자본비용 (Rd) = {cost_of_debt:.4f} ({cost_of_debt:.2%})")
print(f"  부채비율 D/(D+E) = {debt_ratio:.4f} ({debt_ratio:.2%})")
print(f"  법인세율 (T) = {tax_rate:.4f} ({tax_rate:.2%})")

print("\n" + "=" * 80)
print("1. 자기자본비용 (Cost of Equity) 계산")
print("=" * 80)

cost_of_equity = risk_free_rate + beta * market_premium
print(f"\nCAPM 공식: Re = Rf + β × MRP")
print(f"  Re = {risk_free_rate:.4f} + {beta:.2f} × {market_premium:.4f}")
print(f"  Re = {risk_free_rate:.4f} + {beta * market_premium:.4f}")
print(f"  Re = {cost_of_equity:.4f} ({cost_of_equity:.2%})")
print(f"\n예상값: 0.1205 (12.05%)")
print(f"검증: {abs(cost_of_equity - 0.1205) < 0.0001}")

print("\n" + "=" * 80)
print("2. 타인자본비용 세후 조정 (After-tax Cost of Debt)")
print("=" * 80)

after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
print(f"\n세후 타인자본비용: Rd × (1 - T)")
print(f"  Rd(AT) = {cost_of_debt:.4f} × (1 - {tax_rate:.4f})")
print(f"  Rd(AT) = {cost_of_debt:.4f} × {1 - tax_rate:.4f}")
print(f"  Rd(AT) = {after_tax_cost_of_debt:.4f} ({after_tax_cost_of_debt:.2%})")
print(f"\n예상값: 0.0390 (3.90%)")
print(f"검증: {abs(after_tax_cost_of_debt - 0.0390) < 0.0001}")

print("\n" + "=" * 80)
print("3. 가중치 계산")
print("=" * 80)

equity_ratio = 1 - debt_ratio
print(f"\n자기자본 비중: E/(E+D) = 1 - D/(D+E)")
print(f"  We = 1 - {debt_ratio:.4f}")
print(f"  We = {equity_ratio:.4f} ({equity_ratio:.2%})")
print(f"\n타인자본 비중: D/(D+E)")
print(f"  Wd = {debt_ratio:.4f} ({debt_ratio:.2%})")
print(f"\n예상: We = 0.85 (85%), Wd = 0.15 (15%)")
print(f"검증: {abs(equity_ratio - 0.85) < 0.0001 and abs(debt_ratio - 0.15) < 0.0001}")

print("\n" + "=" * 80)
print("4. WACC 계산")
print("=" * 80)

print(f"\nWACC 공식: WACC = We × Re + Wd × Rd × (1-T)")

# 방법 1: 직접 계산
wacc_direct = equity_ratio * cost_of_equity + debt_ratio * after_tax_cost_of_debt
print(f"\n[방법 1: 직접 계산]")
print(f"  WACC = {equity_ratio:.4f} × {cost_of_equity:.4f} + {debt_ratio:.4f} × {after_tax_cost_of_debt:.4f}")
print(f"  WACC = {equity_ratio * cost_of_equity:.4f} + {debt_ratio * after_tax_cost_of_debt:.4f}")
print(f"  WACC = {wacc_direct:.4f} ({wacc_direct:.2%})")

# 방법 2: financial_math 함수 사용
wacc_function = FinancialCalculator.wacc(risk_free_rate, beta, market_premium, cost_of_debt, debt_ratio, tax_rate)
print(f"\n[방법 2: financial_math.wacc() 함수]")
print(f"  WACC = {wacc_function:.4f} ({wacc_function:.2%})")

# 방법 3: 세후 타인자본비용을 명시적으로 분리
wacc_expanded = equity_ratio * cost_of_equity + debt_ratio * cost_of_debt * (1 - tax_rate)
print(f"\n[방법 3: 확장 공식]")
print(f"  WACC = {equity_ratio:.4f} × {cost_of_equity:.4f} + {debt_ratio:.4f} × {cost_of_debt:.4f} × {1-tax_rate:.4f}")
print(f"  WACC = {wacc_expanded:.4f} ({wacc_expanded:.2%})")

print(f"\n예상 WACC: 0.0965 (9.65%)")
print(f"\n계산 결과:")
print(f"  방법 1: {wacc_direct:.4f} ({wacc_direct:.2%})")
print(f"  방법 2: {wacc_function:.4f} ({wacc_function:.2%})")
print(f"  방법 3: {wacc_expanded:.4f} ({wacc_expanded:.2%})")

print("\n" + "=" * 80)
print("5. 손으로 계산한 예상값 검증")
print("=" * 80)

expected_wacc = 0.0965
actual_wacc = wacc_direct

print(f"\n예상 WACC: {expected_wacc:.4f} ({expected_wacc:.2%})")
print(f"실제 WACC: {actual_wacc:.4f} ({actual_wacc:.2%})")
print(f"차이: {actual_wacc - expected_wacc:.4f} ({(actual_wacc - expected_wacc):.2%})")
print(f"차이율: {(actual_wacc - expected_wacc) / expected_wacc * 100:.2f}%")

if abs(actual_wacc - expected_wacc) < 0.001:
    print("\n✓ WACC 계산이 정확합니다!")
else:
    print("\n✗ WACC 계산에 문제가 있습니다!")
    print("\n가능한 원인:")
    print("  1. 예상값 계산 오류 (손계산 실수)")
    print("  2. 입력 파라미터 불일치")
    print("  3. 공식 적용 방법 차이")

    # 역산해서 예상 WACC를 만드는 파라미터 찾기
    print("\n역산 분석:")
    print(f"  예상 WACC {expected_wacc:.4f}를 만들려면...")

    # Re를 고정하고 Rd를 조정
    required_rd_component = (expected_wacc - equity_ratio * cost_of_equity) / debt_ratio
    required_rd_before_tax = required_rd_component / (1 - tax_rate)
    print(f"\n  [시나리오 1] Re={cost_of_equity:.4f} 고정시")
    print(f"    필요한 Rd(세후) = {required_rd_component:.4f}")
    print(f"    필요한 Rd(세전) = {required_rd_before_tax:.4f} ({required_rd_before_tax:.2%})")

    # Rd를 고정하고 Re를 조정
    required_re = (expected_wacc - debt_ratio * after_tax_cost_of_debt) / equity_ratio
    print(f"\n  [시나리오 2] Rd={cost_of_debt:.4f} 고정시")
    print(f"    필요한 Re = {required_re:.4f} ({required_re:.2%})")

    # Beta를 조정
    required_beta = (required_re - risk_free_rate) / market_premium
    print(f"    필요한 Beta = {required_beta:.2f}")

    # 부채비율 조정
    # WACC = Re × (1-D) + Rd × (1-T) × D
    # WACC = Re - Re×D + Rd×(1-T)×D
    # WACC = Re + D × (Rd×(1-T) - Re)
    # D = (WACC - Re) / (Rd×(1-T) - Re)
    required_debt_ratio = (expected_wacc - cost_of_equity) / (after_tax_cost_of_debt - cost_of_equity)
    if 0 <= required_debt_ratio <= 1:
        print(f"\n  [시나리오 3] Re={cost_of_equity:.4f}, Rd={cost_of_debt:.4f} 고정시")
        print(f"    필요한 부채비율 = {required_debt_ratio:.4f} ({required_debt_ratio:.2%})")

print("\n" + "=" * 80)
print("6. DCF 엔진과 비교")
print("=" * 80)

# DCF 엔진 실행
from dcf.dcf_engine import DCFEngine

techvalley_inputs = {
    'company_id': 'TECHVALLEY',
    'company_name': '주식회사 테크밸리',
    'valuation_date': '2024-12-31',
    'historical_financials': [
        {'year': 2021, 'revenue': 8500, 'operating_income': 850, 'net_income': 590,
         'depreciation': 300, 'capex': 400, 'working_capital_change': 150, 'tax_rate': 0.22},
        {'year': 2022, 'revenue': 12300, 'operating_income': 1476, 'net_income': 1020,
         'depreciation': 400, 'capex': 500, 'working_capital_change': 200, 'tax_rate': 0.22},
        {'year': 2023, 'revenue': 18500, 'operating_income': 2775, 'net_income': 1944,
         'depreciation': 400, 'capex': 600, 'working_capital_change': 300, 'tax_rate': 0.22}
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

engine = DCFEngine()
result = engine.run_valuation(techvalley_inputs)
engine_wacc = result['wacc']['wacc']

print(f"\nDCF 엔진 WACC: {engine_wacc:.4f} ({engine_wacc:.2%})")
print(f"직접 계산 WACC: {wacc_direct:.4f} ({wacc_direct:.2%})")
print(f"차이: {abs(engine_wacc - wacc_direct):.6f}")

if abs(engine_wacc - wacc_direct) < 0.0001:
    print("\n✓ DCF 엔진의 WACC 계산은 정확합니다.")
    print("✗ 문제는 예상값(0.0965)이 잘못되었을 가능성이 높습니다.")
else:
    print("\n✗ DCF 엔진의 WACC 계산에 문제가 있습니다.")

print("\n" + "=" * 80)
