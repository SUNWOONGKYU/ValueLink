# -*- coding: utf-8 -*-
"""
올바른 예상값 재계산
WACC = 10.83%로 재계산
"""

print("=" * 80)
print("테크밸리 DCF 예상값 재계산")
print("=" * 80)

# 입력 파라미터
print("\n[입력 파라미터]")
revenue_2023 = 18500
revenue_growth = [0.440, 0.350, 0.300, 0.228, 0.200]
target_margin = 0.160
tax_rate = 0.22
depreciation_rate = 0.017
capex_rate = 0.030
wc_rate = 0.015
terminal_growth = 0.025
wacc = 0.1083  # 올바른 WACC

print(f"기준연도 매출: {revenue_2023:,.0f}")
print(f"매출 성장률: {revenue_growth}")
print(f"목표 영업이익률: {target_margin:.1%}")
print(f"WACC: {wacc:.4f} ({wacc:.2%})")
print(f"영구성장률: {terminal_growth:.1%}")

# FCF 예측
print("\n" + "=" * 80)
print("FCF 예측")
print("=" * 80)

fcf_list = []
pv_fcf_list = []

prev_revenue = revenue_2023
for i, growth in enumerate(revenue_growth, start=1):
    year = 2023 + i

    # 매출
    revenue = prev_revenue * (1 + growth)

    # 영업이익 (목표 마진 사용)
    operating_income = revenue * target_margin

    # NOPAT
    nopat = operating_income * (1 - tax_rate)

    # 감가상각
    depreciation = revenue * depreciation_rate

    # CAPEX
    capex = revenue * capex_rate

    # 운전자본 증가
    revenue_increase = revenue - prev_revenue
    wc_change = revenue_increase * wc_rate

    # FCF = NOPAT + 감가상각 - CAPEX - 운전자본 증가
    fcf = nopat + depreciation - capex - wc_change

    # 현재가치
    discount_factor = 1 / (1 + wacc) ** i
    pv_fcf = fcf * discount_factor

    fcf_list.append(fcf)
    pv_fcf_list.append(pv_fcf)

    print(f"{year}: 매출={revenue:,.0f}, 영업이익={operating_income:,.0f}, "
          f"NOPAT={nopat:,.0f}, FCF={fcf:,.0f}, PV(FCF)={pv_fcf:,.0f}")

    prev_revenue = revenue

total_pv_fcf = sum(pv_fcf_list)
print(f"\nPV(FCF) 합계: {total_pv_fcf:,.0f}")

# 영구가치
print("\n" + "=" * 80)
print("영구가치 계산")
print("=" * 80)

last_fcf = fcf_list[-1]
fcf_perpetuity = last_fcf * (1 + terminal_growth)
capitalization_rate = wacc - terminal_growth
terminal_value = fcf_perpetuity / capitalization_rate

print(f"최종 FCF (2028): {last_fcf:,.0f}")
print(f"다음연도 FCF (2029): {fcf_perpetuity:,.0f}")
print(f"자본환원율 (WACC - g): {capitalization_rate:.4f}")
print(f"영구가치 (TV): {terminal_value:,.0f}")

# PV(TV)
pv_terminal_value = terminal_value / (1 + wacc) ** 5
print(f"PV(TV): {pv_terminal_value:,.0f}")

# 기업가치
print("\n" + "=" * 80)
print("기업가치")
print("=" * 80)

enterprise_value = total_pv_fcf + pv_terminal_value
print(f"PV(FCF): {total_pv_fcf:,.0f}")
print(f"PV(TV): {pv_terminal_value:,.0f}")
print(f"기업가치 (EV): {enterprise_value:,.0f}")

# 주주가치
print("\n" + "=" * 80)
print("주주가치")
print("=" * 80)

cash = 1200
total_debt = 500
net_debt = total_debt - cash
non_operating_assets = 0

equity_value = enterprise_value - net_debt + non_operating_assets

print(f"기업가치: {enterprise_value:,.0f}")
print(f"현금: {cash:,.0f}")
print(f"차입금: {total_debt:,.0f}")
print(f"순차입금: {net_debt:,.0f}")
print(f"비영업자산: {non_operating_assets:,.0f}")
print(f"주주가치: {equity_value:,.0f}")

# 주당가치
shares = 1_000_000
value_per_share = (equity_value * 1_000_000) / shares

print(f"\n발행주식수: {shares:,.0f}주")
print(f"주당가치: {value_per_share:,.0f}원")

print("\n" + "=" * 80)
print("올바른 예상값 요약")
print("=" * 80)

print(f"""
기업가치 (EV): {enterprise_value:,.0f} 백만원
주주가치: {equity_value:,.0f} 백만원
주당가치: {value_per_share:,.0f}원
WACC: {wacc:.4f} ({wacc:.2%})
""")

print("이 값들로 test_dcf_with_techvalley.py의 expected_results를 업데이트해야 합니다.")
print("=" * 80)
