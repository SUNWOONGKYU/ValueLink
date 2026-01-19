"""
DCF (Discounted Cash Flow) Valuation Engine

This module implements a comprehensive DCF valuation engine for enterprise valuation.
It calculates enterprise value, equity value, and per-share value using FCFF methodology.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class FCFFProjection:
    """Free Cash Flow to Firm projection for a single period"""
    year: str
    revenue: float
    ebit: float
    tax_rate: float
    nopat: float  # Net Operating Profit After Tax
    depreciation: float
    capex: float
    working_capital_change: float
    fcff: float
    discount_period: float  # Years from valuation date


@dataclass
class WACCComponents:
    """Weighted Average Cost of Capital components"""
    # Cost of Equity (CAPM)
    risk_free_rate: float
    levered_beta: float
    market_risk_premium: float
    size_premium: float
    cost_of_equity: float

    # Cost of Debt
    pretax_cost_of_debt: float
    tax_rate: float
    aftertax_cost_of_debt: float

    # Capital Structure
    equity_to_capital: float  # E / (E + D)
    debt_to_capital: float    # D / (E + D)

    # Final WACC
    wacc: float


@dataclass
class NonOperatingItems:
    """Non-operating assets and liabilities"""
    non_operating_assets: float
    interest_bearing_debt: float


@dataclass
class DCFResult:
    """Complete DCF valuation result"""
    # Operating Value Components
    pv_cumulative: float  # PV of projected period FCFF
    pv_terminal: float    # PV of terminal value
    operating_value: float

    # Enterprise & Equity Value
    non_operating_assets: float
    enterprise_value: float
    interest_bearing_debt: float
    equity_value: float

    # Per Share Value
    shares_outstanding: int
    value_per_share: float

    # Detailed calculations
    fcff_projections: List[FCFFProjection]
    terminal_fcff: float
    terminal_growth_rate: float
    wacc: float

    # Breakdown by year
    pv_by_year: List[Dict[str, float]]


class DCFEngine:
    """
    DCF Valuation Engine

    Implements the Discounted Cash Flow methodology using:
    - FCFF (Free Cash Flow to Firm) approach
    - WACC (Weighted Average Cost of Capital) as discount rate
    - Gordon Growth Model for terminal value
    """

    def __init__(self):
        self.precision = 2  # Decimal places for rounding

    def calculate_wacc(self, components: WACCComponents) -> float:
        """
        Calculate Weighted Average Cost of Capital

        WACC = (E/V) × Ke + (D/V) × Kd × (1 - T)
        where Kd is already after-tax in our components
        """
        wacc = (
            components.equity_to_capital * components.cost_of_equity +
            components.debt_to_capital * components.aftertax_cost_of_debt
        )
        return wacc

    def calculate_cost_of_equity(
        self,
        risk_free_rate: float,
        levered_beta: float,
        market_risk_premium: float,
        size_premium: float = 0.0
    ) -> float:
        """
        Calculate Cost of Equity using CAPM

        Ke = Rf + β × MRP + Size Premium
        """
        ke = risk_free_rate + (levered_beta * market_risk_premium) + size_premium
        return ke

    def calculate_terminal_value(
        self,
        terminal_fcff: float,
        wacc: float,
        terminal_growth_rate: float
    ) -> float:
        """
        Calculate Terminal Value using Gordon Growth Model

        TV = Terminal FCFF × (1 + g) / (WACC - g)
        """
        if wacc <= terminal_growth_rate:
            raise ValueError(
                f"WACC ({wacc:.2%}) must be greater than "
                f"terminal growth rate ({terminal_growth_rate:.2%})"
            )

        terminal_value = terminal_fcff * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
        return terminal_value

    def discount_to_present_value(
        self,
        future_value: float,
        discount_rate: float,
        periods: float
    ) -> float:
        """
        Discount future cash flow to present value

        PV = FV / (1 + r)^n
        """
        pv = future_value / ((1 + discount_rate) ** periods)
        return pv

    def calculate_fcff(
        self,
        ebit: float,
        tax_rate: float,
        depreciation: float,
        capex: float,
        working_capital_change: float
    ) -> tuple[float, float]:
        """
        Calculate Free Cash Flow to Firm

        FCFF = NOPAT + Depreciation - CAPEX - ΔWC
        where NOPAT = EBIT × (1 - Tax Rate)
        """
        nopat = ebit * (1 - tax_rate)
        fcff = nopat + depreciation - capex - working_capital_change
        return nopat, fcff

    def run_valuation(
        self,
        fcff_projections: List[FCFFProjection],
        terminal_fcff: float,
        wacc_components: WACCComponents,
        terminal_growth_rate: float,
        non_operating_items: NonOperatingItems,
        shares_outstanding: int,
        terminal_discount_period: float
    ) -> DCFResult:
        """
        Run complete DCF valuation

        Args:
            fcff_projections: List of FCFF projections for explicit forecast period
            terminal_fcff: Terminal year FCFF for perpetuity calculation
            wacc_components: All WACC calculation components
            terminal_growth_rate: Perpetual growth rate for terminal value
            non_operating_items: Non-operating assets and interest-bearing debt
            shares_outstanding: Number of shares outstanding
            terminal_discount_period: Discount period for terminal value

        Returns:
            DCFResult with complete valuation breakdown
        """
        # Calculate WACC
        wacc = self.calculate_wacc(wacc_components)

        # Calculate PV of projected period FCFF
        pv_by_year = []
        pv_cumulative = 0.0

        for projection in fcff_projections:
            discount_factor = 1 / ((1 + wacc) ** projection.discount_period)
            pv = projection.fcff * discount_factor
            pv_cumulative += pv

            pv_by_year.append({
                'year': projection.year,
                'fcff': projection.fcff,
                'discount_period': projection.discount_period,
                'discount_factor': discount_factor,
                'pv': pv
            })

        # Calculate Terminal Value and its PV
        terminal_value = self.calculate_terminal_value(
            terminal_fcff,
            wacc,
            terminal_growth_rate
        )

        pv_terminal = self.discount_to_present_value(
            terminal_value,
            wacc,
            terminal_discount_period
        )

        pv_by_year.append({
            'year': 'Terminal',
            'fcff': terminal_fcff,
            'terminal_value': terminal_value,
            'discount_period': terminal_discount_period,
            'discount_factor': 1 / ((1 + wacc) ** terminal_discount_period),
            'pv': pv_terminal
        })

        # Calculate Operating Value
        operating_value = pv_cumulative + pv_terminal

        # Calculate Enterprise Value
        enterprise_value = operating_value + non_operating_items.non_operating_assets

        # Calculate Equity Value
        equity_value = enterprise_value - non_operating_items.interest_bearing_debt

        # Calculate Value Per Share
        value_per_share = equity_value / shares_outstanding

        return DCFResult(
            pv_cumulative=pv_cumulative,
            pv_terminal=pv_terminal,
            operating_value=operating_value,
            non_operating_assets=non_operating_items.non_operating_assets,
            enterprise_value=enterprise_value,
            interest_bearing_debt=non_operating_items.interest_bearing_debt,
            equity_value=equity_value,
            shares_outstanding=shares_outstanding,
            value_per_share=value_per_share,
            fcff_projections=fcff_projections,
            terminal_fcff=terminal_fcff,
            terminal_growth_rate=terminal_growth_rate,
            wacc=wacc,
            pv_by_year=pv_by_year
        )

    def format_result(self, result: DCFResult) -> str:
        """Format DCF result as readable text"""
        output = []
        output.append("=" * 80)
        output.append("DCF VALUATION RESULT")
        output.append("=" * 80)
        output.append("")

        output.append("OPERATING VALUE BREAKDOWN")
        output.append("-" * 80)
        output.append(f"PV of Projected Period:    {result.pv_cumulative:>20,.0f} won")
        output.append(f"PV of Terminal Value:      {result.pv_terminal:>20,.0f} won")
        output.append(f"Operating Value:           {result.operating_value:>20,.0f} won")
        output.append("")

        output.append("ENTERPRISE & EQUITY VALUE")
        output.append("-" * 80)
        output.append(f"Operating Value:           {result.operating_value:>20,.0f} won")
        output.append(f"+ Non-operating Assets:    {result.non_operating_assets:>20,.0f} won")
        output.append(f"= Enterprise Value:        {result.enterprise_value:>20,.0f} won")
        output.append(f"- Interest-bearing Debt:   {result.interest_bearing_debt:>20,.0f} won")
        output.append(f"= Equity Value:            {result.equity_value:>20,.0f} won")
        output.append("")

        output.append("PER SHARE VALUE")
        output.append("-" * 80)
        output.append(f"Equity Value:              {result.equity_value:>20,.0f} won")
        output.append(f"Shares Outstanding:        {result.shares_outstanding:>20,} shares")
        output.append(f"Value Per Share:           {result.value_per_share:>20,.0f} won")
        output.append("")

        output.append("KEY PARAMETERS")
        output.append("-" * 80)
        output.append(f"WACC:                      {result.wacc:>20.2%}")
        output.append(f"Terminal Growth Rate:      {result.terminal_growth_rate:>20.2%}")
        output.append("")

        output.append("CASH FLOW PRESENT VALUES BY YEAR")
        output.append("-" * 80)
        output.append(f"{'Year':<12} {'FCFF':>15} {'Period':>8} {'Factor':>8} {'PV':>15}")
        output.append("-" * 80)

        for pv_data in result.pv_by_year:
            year = pv_data['year']
            fcff = pv_data['fcff']
            period = pv_data['discount_period']
            factor = pv_data['discount_factor']
            pv = pv_data['pv']

            output.append(
                f"{year:<12} {fcff:>15,.0f} {period:>8.2f} {factor:>8.2f} {pv:>15,.0f}"
            )

        output.append("=" * 80)

        return "\n".join(output)


def create_fcff_projection(
    year: str,
    revenue: float,
    ebit: float,
    tax_rate: float,
    depreciation: float,
    capex: float,
    working_capital_change: float,
    discount_period: float
) -> FCFFProjection:
    """Helper function to create FCFF projection"""
    nopat = ebit * (1 - tax_rate)
    fcff = nopat + depreciation - capex - working_capital_change

    return FCFFProjection(
        year=year,
        revenue=revenue,
        ebit=ebit,
        tax_rate=tax_rate,
        nopat=nopat,
        depreciation=depreciation,
        capex=capex,
        working_capital_change=working_capital_change,
        fcff=fcff,
        discount_period=discount_period
    )
