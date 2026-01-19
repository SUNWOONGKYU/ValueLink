"""
DCF Engine Verification Script - Enkinoai Valuation

This script verifies the DCF engine accuracy using real evaluation data from:
태일회계법인 (TAEIL Accounting Corporation)
FY25 엔키노에이아이 기업가치 평가보고서 (2025.06.30)
"""

from dcf_engine import (
    DCFEngine,
    FCFFProjection,
    WACCComponents,
    NonOperatingItems,
    create_fcff_projection
)


def main():
    """Run DCF verification with Enkinoai real evaluation data"""

    print("=" * 80)
    print("DCF ENGINE VERIFICATION - ENKINOAI")
    print("=" * 80)
    print("Evaluation Date: 2025-06-30")
    print("Evaluator: 태일회계법인 (TAEIL Accounting Corporation)")
    print("=" * 80)
    print()

    # ========================================================================
    # ACTUAL EVALUATION REPORT DATA
    # ========================================================================

    # Target Results from Real Report (Pages 6-7)
    actual_results = {
        'operating_value': 16_216_378_227,
        'pv_cumulative': 5_605_401_153,
        'pv_terminal': 10_610_977_073,
        'non_operating_assets': 129_670_466,
        'enterprise_value': 16_346_048_693,
        'interest_bearing_debt': 616_929_334,
        'equity_value': 15_729_119_359,
        'shares_outstanding': 7_350_000,
        'value_per_share': 2_140
    }

    # ========================================================================
    # WACC COMPONENTS (Pages 11-13)
    # ========================================================================

    wacc_components = WACCComponents(
        # Cost of Equity (CAPM Model)
        risk_free_rate=0.0281,      # 2.81%
        levered_beta=0.911,
        market_risk_premium=0.09,   # 9.00%
        size_premium=0.0375,        # 3.75%
        cost_of_equity=0.1476,      # 14.76% (Rf + β×MRP + SP)

        # Cost of Debt
        pretax_cost_of_debt=0.0919, # 9.19%
        tax_rate=0.2090,            # 20.90%
        aftertax_cost_of_debt=0.0727,  # 7.27%

        # Capital Structure
        equity_to_capital=0.8726,   # 87.26%
        debt_to_capital=0.1274,     # 12.74%

        # WACC
        wacc=0.1381                 # 13.81%
    )

    # ========================================================================
    # FCFF PROJECTIONS (Pages 8-10)
    # ========================================================================

    # Year 2025.06F (6 months, discount period = 0.25 years)
    fcff_2025_06 = create_fcff_projection(
        year='2025.06F',
        revenue=780_219_575,
        ebit=306_057_598,
        tax_rate=0.0,               # No tax in first period
        depreciation=52_435_785,
        capex=50_836_751,
        working_capital_change=0,
        discount_period=0.25
    )

    # Year 2026.12
    fcff_2026 = create_fcff_projection(
        year='2026.12',
        revenue=2_437_791_252,
        ebit=1_249_424_517,
        tax_rate=0.1914,            # 239,129,724 / 1,249,424,517 = 19.14%
        depreciation=127_894_459,
        capex=199_729_533,
        working_capital_change=0,
        discount_period=1.00
    )

    # Year 2027.12
    fcff_2027 = create_fcff_projection(
        year='2027.12',
        revenue=3_948_486_033,
        ebit=2_702_544_486,
        tax_rate=0.2008,            # 542,831,798 / 2,702,544,486 = 20.08%
        depreciation=155_828_047,
        capex=171_137_071,
        working_capital_change=0,
        discount_period=2.00
    )

    # Year 2028.12
    fcff_2028 = create_fcff_projection(
        year='2028.12',
        revenue=4_039_301_212,
        ebit=2_749_590_973,
        tax_rate=0.2010,            # 552,664,513 / 2,749,590,973 = 20.10%
        depreciation=169_202_676,
        capex=181_546_054,
        working_capital_change=0,
        discount_period=3.00
    )

    # Year 2029.12
    fcff_2029 = create_fcff_projection(
        year='2029.12',
        revenue=4_136_244_441,
        ebit=2_826_951_271,
        tax_rate=0.2013,            # 568,832,816 / 2,826,951,271 = 20.13%
        depreciation=157_504_010,
        capex=158_307_815,
        working_capital_change=0,
        discount_period=4.00
    )

    fcff_projections = [
        fcff_2025_06,
        fcff_2026,
        fcff_2027,
        fcff_2028,
        fcff_2029
    ]

    # Terminal Year FCFF
    terminal_fcff = 2_280_479_640
    terminal_growth_rate = 0.01  # 1.00%
    terminal_discount_period = 4.00

    # ========================================================================
    # NON-OPERATING ITEMS (Page 10)
    # ========================================================================

    non_operating_items = NonOperatingItems(
        non_operating_assets=129_670_466,
        interest_bearing_debt=616_929_334
    )

    shares_outstanding = 7_350_000

    # ========================================================================
    # RUN DCF ENGINE
    # ========================================================================

    engine = DCFEngine()

    print("Running DCF Engine...")
    print()

    result = engine.run_valuation(
        fcff_projections=fcff_projections,
        terminal_fcff=terminal_fcff,
        wacc_components=wacc_components,
        terminal_growth_rate=terminal_growth_rate,
        non_operating_items=non_operating_items,
        shares_outstanding=shares_outstanding,
        terminal_discount_period=terminal_discount_period
    )

    # ========================================================================
    # DISPLAY ENGINE RESULT
    # ========================================================================

    print(engine.format_result(result))
    print()

    # ========================================================================
    # COMPARISON WITH ACTUAL REPORT
    # ========================================================================

    print("=" * 80)
    print("VERIFICATION RESULTS - COMPARISON WITH ACTUAL REPORT")
    print("=" * 80)
    print()

    comparisons = [
        ('PV of Projected Period', result.pv_cumulative, actual_results['pv_cumulative']),
        ('PV of Terminal Value', result.pv_terminal, actual_results['pv_terminal']),
        ('Operating Value', result.operating_value, actual_results['operating_value']),
        ('Non-operating Assets', result.non_operating_assets, actual_results['non_operating_assets']),
        ('Enterprise Value', result.enterprise_value, actual_results['enterprise_value']),
        ('Interest-bearing Debt', result.interest_bearing_debt, actual_results['interest_bearing_debt']),
        ('Equity Value', result.equity_value, actual_results['equity_value']),
        ('Value Per Share', result.value_per_share, actual_results['value_per_share'])
    ]

    print(f"{'Item':<25} {'Engine Result':>20} {'Actual Report':>20} {'Error %':>12}")
    print("=" * 80)

    max_error = 0.0
    error_details = []

    for item, engine_value, actual_value in comparisons:
        error_pct = ((engine_value - actual_value) / actual_value * 100) if actual_value != 0 else 0
        max_error = max(max_error, abs(error_pct))

        error_details.append({
            'item': item,
            'engine': engine_value,
            'actual': actual_value,
            'error': error_pct
        })

        print(f"{item:<25} {engine_value:>20,.0f} {actual_value:>20,.0f} {error_pct:>11.2f}%")

    print("=" * 80)
    print()

    # ========================================================================
    # ERROR ANALYSIS
    # ========================================================================

    print("ERROR ANALYSIS")
    print("-" * 80)
    print(f"Maximum Error: {max_error:.2f}%")
    print(f"Acceptable Error Range: ±5.00%")
    print()

    if max_error <= 5.0:
        print("[PASS] VERIFICATION PASSED - All errors within acceptable range (+-5%)")
    else:
        print("[FAIL] VERIFICATION FAILED - Errors exceed acceptable range")
        print()
        print("Items with errors > 5%:")
        for detail in error_details:
            if abs(detail['error']) > 5.0:
                print(f"  - {detail['item']}: {detail['error']:.2f}%")

    print()

    # ========================================================================
    # DETAILED FCFF VERIFICATION
    # ========================================================================

    print("=" * 80)
    print("FCFF CALCULATION VERIFICATION")
    print("=" * 80)
    print()

    # Actual FCFF from report (Page 9)
    actual_fcff = {
        '2025.06F': 307_656_633,
        '2026.12': 938_459_720,
        '2027.12': 2_144_403_665,
        '2028.12': 2_184_583_081,
        '2029.12': 2_257_314_651
    }

    print(f"{'Year':<12} {'Engine FCFF':>15} {'Actual FCFF':>15} {'Error %':>10}")
    print("-" * 80)

    for projection in fcff_projections:
        actual = actual_fcff[projection.year]
        error = ((projection.fcff - actual) / actual * 100) if actual != 0 else 0
        print(f"{projection.year:<12} {projection.fcff:>15,.0f} {actual:>15,.0f} {error:>9.2f}%")

    print()

    # ========================================================================
    # PV CALCULATION VERIFICATION
    # ========================================================================

    print("=" * 80)
    print("PRESENT VALUE CALCULATION VERIFICATION")
    print("=" * 80)
    print()

    # Actual PV from report (Page 10)
    actual_pv = {
        '2025.06F': 297_866_167,
        '2026.12': 824_584_588,
        '2027.12': 1_655_562_932,
        '2028.12': 1_481_928_655,
        '2029.12': 1_345_458_810,
        'Terminal': 10_610_977_073
    }

    print(f"{'Year':<12} {'Engine PV':>15} {'Actual PV':>15} {'Error %':>10}")
    print("-" * 80)

    for pv_data in result.pv_by_year:
        year = pv_data['year']
        engine_pv = pv_data['pv']
        actual = actual_pv.get(year, 0)
        if actual > 0:
            error = ((engine_pv - actual) / actual * 100)
            print(f"{year:<12} {engine_pv:>15,.0f} {actual:>15,.0f} {error:>9.2f}%")

    print()
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
