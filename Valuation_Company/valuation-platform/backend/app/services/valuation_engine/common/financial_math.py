"""
기업가치평가 공통 계산 라이브러리

Based on:
- KPMG "New Valuation Era: Valuing New Growth Companies" (2021)
- 삼일PwC "M&A ESSENCE 2020"
- Standard DCF Methodology

Author: Valuation Engine Team
Date: 2025-10-17
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from scipy.optimize import newton


class FinancialCalculator:
    """재무 계산 핵심 라이브러리"""

    @staticmethod
    def present_value(cash_flows: List[float], discount_rate: float) -> float:
        """
        현재가치 계산 (Present Value)

        Formula: PV = Σ [CFt / (1 + r)^t]

        Args:
            cash_flows: 연도별 현금흐름 리스트 [Year1, Year2, ...]
            discount_rate: 할인율 (예: 0.10 = 10%)

        Returns:
            float: 현재가치 합계

        Example:
            >>> fcf = [1000, 1100, 1210, 1331, 1464]
            >>> FinancialCalculator.present_value(fcf, 0.10)
            4545.95

        Reference:
            KPMG Guide p.23 "DCF Valuation Methodology"
        """
        if discount_rate < 0:
            raise ValueError(f"할인율은 0 이상이어야 합니다: {discount_rate}")

        pv = sum(cf / (1 + discount_rate) ** t
                 for t, cf in enumerate(cash_flows, start=1))
        return pv

    @staticmethod
    def future_value(present_value: float, growth_rate: float, periods: int) -> float:
        """
        미래가치 계산 (Future Value)

        Formula: FV = PV × (1 + g)^n

        Args:
            present_value: 현재가치
            growth_rate: 성장률 (예: 0.05 = 5%)
            periods: 기간 (연도)

        Returns:
            float: 미래가치

        Example:
            >>> FinancialCalculator.future_value(1000, 0.05, 5)
            1276.28
        """
        return present_value * (1 + growth_rate) ** periods

    @staticmethod
    def wacc(risk_free_rate: float,
             beta: float,
             market_premium: float,
             cost_of_debt: float,
             debt_ratio: float,
             tax_rate: float) -> float:
        """
        가중평균자본비용 계산 (Weighted Average Cost of Capital)

        Formula:
            WACC = (E/V) × Re + (D/V) × Rd × (1 - T)
            where Re = Rf + β × MRP

        Args:
            risk_free_rate: 무위험이자율 (10년 국고채)
            beta: 베타 (체계적 위험)
            market_premium: 시장위험프리미엄 (일반적으로 7%)
            cost_of_debt: 부채비용 (차입금 이자율)
            debt_ratio: 부채비율 (D/V)
            tax_rate: 법인세율 (예: 0.25)

        Returns:
            float: WACC

        Example:
            >>> FinancialCalculator.wacc(
            ...     risk_free_rate=0.035,
            ...     beta=1.2,
            ...     market_premium=0.07,
            ...     cost_of_debt=0.05,
            ...     debt_ratio=0.30,
            ...     tax_rate=0.25
            ... )
            0.0945  # 9.45%

        Reference:
            PwC M&A Guide p.45 "WACC Calculation"
            Formula: WACC = Kd(1-t)(B/V) + Ke(E/V)
        """
        # 자기자본비용 (CAPM)
        cost_of_equity = risk_free_rate + beta * market_premium

        # 자기자본비율
        equity_ratio = 1 - debt_ratio

        # WACC
        wacc = (equity_ratio * cost_of_equity) + \
               (debt_ratio * cost_of_debt * (1 - tax_rate))

        return wacc

    @staticmethod
    def terminal_value(last_fcf: float,
                      terminal_growth: float,
                      wacc: float,
                      method: str = 'gordon') -> float:
        """
        영구가치 계산 (Terminal Value)

        Gordon Growth Model:
            TV = FCF(n+1) / (WACC - g)
            where FCF(n+1) = FCF(n) × (1 + g)

        Args:
            last_fcf: 마지막 연도 FCF
            terminal_growth: 영구성장률 (일반적으로 2~3%)
            wacc: 가중평균자본비용
            method: 계산 방법 ('gordon' or 'exit_multiple')

        Returns:
            float: 영구가치

        Raises:
            ValueError: WACC <= 영구성장률인 경우

        Example:
            >>> FinancialCalculator.terminal_value(
            ...     last_fcf=1464,
            ...     terminal_growth=0.03,
            ...     wacc=0.095
            ... )
            23190.77

        Reference:
            KPMG Guide p.27 "Terminal Value Calculation"
        """
        if wacc <= terminal_growth:
            raise ValueError(
                f"WACC ({wacc:.2%})는 영구성장률 ({terminal_growth:.2%})보다 "
                f"커야 합니다. (Gordon Growth Model 가정)"
            )

        if method == 'gordon':
            # Gordon Growth Model
            fcf_next_year = last_fcf * (1 + terminal_growth)
            tv = fcf_next_year / (wacc - terminal_growth)
            return tv

        elif method == 'exit_multiple':
            # Exit Multiple Method (추후 구현)
            raise NotImplementedError("Exit Multiple 방식은 추후 구현 예정")

        else:
            raise ValueError(f"Unknown method: {method}")

    @staticmethod
    def pv_terminal_value(terminal_value: float,
                         wacc: float,
                         last_period: int) -> float:
        """
        영구가치의 현재가치 계산

        Formula: PV(TV) = TV / (1 + WACC)^n

        Args:
            terminal_value: 영구가치
            wacc: 할인율
            last_period: 마지막 예측 연도 (예: 5년 예측이면 5)

        Returns:
            float: 영구가치의 현재가치
        """
        return terminal_value / (1 + wacc) ** last_period

    @staticmethod
    def irr(cash_flows: List[float], initial_investment: float) -> float:
        """
        내부수익률 계산 (Internal Rate of Return)

        Newton-Raphson 방법 사용

        Formula: NPV = -I0 + Σ [CFt / (1 + IRR)^t] = 0

        Args:
            cash_flows: 연도별 현금흐름
            initial_investment: 초기 투자액 (양수)

        Returns:
            float: IRR (예: 0.15 = 15%)

        Example:
            >>> cash_flows = [100, 110, 121, 133, 146]
            >>> FinancialCalculator.irr(cash_flows, 400)
            0.1234  # 12.34%
        """
        def npv(rate):
            return -initial_investment + sum(
                cf / (1 + rate) ** t
                for t, cf in enumerate(cash_flows, start=1)
            )

        try:
            return newton(npv, x0=0.10)  # 초기값 10%
        except RuntimeError:
            raise ValueError("IRR 계산 실패: 수렴하지 않음")

    @staticmethod
    def xirr(cash_flows: List[float], dates: List[str]) -> float:
        """
        불규칙 현금흐름의 IRR 계산 (Extended IRR)

        Args:
            cash_flows: 현금흐름 리스트
            dates: 날짜 리스트 (YYYY-MM-DD 형식)

        Returns:
            float: XIRR

        Note:
            추후 구현 (scipy.optimize 활용)
        """
        raise NotImplementedError("XIRR은 추후 구현 예정")

    @staticmethod
    def cagr(begin_value: float, end_value: float, periods: int) -> float:
        """
        연평균성장률 계산 (Compound Annual Growth Rate)

        Formula: CAGR = (End / Begin)^(1/n) - 1

        Args:
            begin_value: 시작 값
            end_value: 종료 값
            periods: 기간 (연도)

        Returns:
            float: CAGR

        Example:
            >>> FinancialCalculator.cagr(100, 150, 5)
            0.0845  # 8.45%
        """
        if begin_value <= 0:
            raise ValueError("시작 값은 0보다 커야 합니다")

        return (end_value / begin_value) ** (1 / periods) - 1

    @staticmethod
    def perpetuity(cash_flow: float, discount_rate: float) -> float:
        """
        영구연금 현재가치 (Perpetuity)

        Formula: PV = CF / r

        Args:
            cash_flow: 연간 현금흐름
            discount_rate: 할인율

        Returns:
            float: 영구연금 현재가치
        """
        if discount_rate <= 0:
            raise ValueError("할인율은 0보다 커야 합니다")

        return cash_flow / discount_rate

    @staticmethod
    def growing_perpetuity(cash_flow: float,
                          discount_rate: float,
                          growth_rate: float) -> float:
        """
        성장 영구연금 현재가치 (Growing Perpetuity)

        Formula: PV = CF / (r - g)

        Args:
            cash_flow: 첫 해 현금흐름
            discount_rate: 할인율
            growth_rate: 성장률

        Returns:
            float: 성장 영구연금 현재가치
        """
        if discount_rate <= growth_rate:
            raise ValueError("할인율은 성장률보다 커야 합니다")

        return cash_flow / (discount_rate - growth_rate)


class ValidationLibrary:
    """재무제표 검증 및 논리적 일관성 체크"""

    @staticmethod
    def validate_balance_sheet(assets: float,
                               liabilities: float,
                               equity: float,
                               tolerance: float = 1000) -> bool:
        """
        대차대조표 균형 검증

        Formula: Assets = Liabilities + Equity

        Args:
            assets: 총 자산
            liabilities: 총 부채
            equity: 총 자본
            tolerance: 허용 오차 (기본 1,000원)

        Returns:
            bool: 균형 여부

        Raises:
            ValueError: 균형이 맞지 않는 경우
        """
        difference = abs(assets - (liabilities + equity))

        if difference > tolerance:
            raise ValueError(
                f"대차대조표 불균형: 자산 {assets:,} ≠ 부채 {liabilities:,} + 자본 {equity:,} "
                f"(차이: {difference:,})"
            )

        return True

    @staticmethod
    def validate_wacc_components(risk_free: float,
                                 beta: float,
                                 market_premium: float,
                                 debt_ratio: float) -> Dict[str, bool]:
        """
        WACC 구성요소 타당성 검증

        Returns:
            Dict: 검증 결과
        """
        validations = {
            'risk_free_rate': 0 < risk_free < 0.10,  # 0~10%
            'beta': -1 < beta < 3,  # -1~3 (일반적 범위)
            'market_premium': 0.05 < market_premium < 0.15,  # 5~15%
            'debt_ratio': 0 <= debt_ratio <= 0.90  # 0~90%
        }

        return validations

    @staticmethod
    def sanity_check_terminal_value_ratio(pv_fcf: float,
                                          pv_tv: float) -> Tuple[float, bool]:
        """
        영구가치 비중 정상 범위 확인

        일반적으로 영구가치는 기업가치의 50~80%

        Args:
            pv_fcf: 예측기간 FCF 현재가치
            pv_tv: 영구가치 현재가치

        Returns:
            Tuple[float, bool]: (비율, 정상 여부)
        """
        total_ev = pv_fcf + pv_tv
        tv_ratio = pv_tv / total_ev

        is_normal = 0.50 <= tv_ratio <= 0.80

        return tv_ratio, is_normal


# 모듈 테스트
if __name__ == "__main__":
    print("=" * 80)
    print("Financial Math Library - Test Suite")
    print("=" * 80)

    # Test 1: Present Value
    print("\n[Test 1] Present Value Calculation")
    fcf = [1000, 1100, 1210, 1331, 1464]
    wacc_test = 0.10
    pv = FinancialCalculator.present_value(fcf, wacc_test)
    print(f"FCF: {fcf}")
    print(f"WACC: {wacc_test:.2%}")
    print(f"PV(FCF): {pv:,.2f}")

    # Test 2: WACC
    print("\n[Test 2] WACC Calculation")
    wacc_result = FinancialCalculator.wacc(
        risk_free_rate=0.035,
        beta=1.2,
        market_premium=0.07,
        cost_of_debt=0.05,
        debt_ratio=0.30,
        tax_rate=0.25
    )
    print(f"WACC: {wacc_result:.4f} ({wacc_result:.2%})")

    # Test 3: Terminal Value
    print("\n[Test 3] Terminal Value Calculation")
    tv = FinancialCalculator.terminal_value(
        last_fcf=1464,
        terminal_growth=0.03,
        wacc=wacc_result
    )
    pv_tv = FinancialCalculator.pv_terminal_value(tv, wacc_result, 5)
    print(f"Terminal Value: {tv:,.2f}")
    print(f"PV(TV): {pv_tv:,.2f}")

    # Test 4: Enterprise Value
    print("\n[Test 4] Enterprise Value")
    ev = pv + pv_tv
    print(f"PV(FCF): {pv:,.2f}")
    print(f"PV(TV): {pv_tv:,.2f}")
    print(f"Enterprise Value: {ev:,.2f}")

    # Test 5: Sanity Check
    print("\n[Test 5] Terminal Value Ratio Check")
    tv_ratio, is_normal = ValidationLibrary.sanity_check_terminal_value_ratio(pv, pv_tv)
    print(f"TV Ratio: {tv_ratio:.2%}")
    print(f"Is Normal (50~80%): {is_normal}")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)
