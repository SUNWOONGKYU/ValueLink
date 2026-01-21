"""
DCF (Discounted Cash Flow) 평가 엔진

Based on:
- KPMG "New Valuation Era" DCF Methodology
- 삼일PwC "M&A ESSENCE 2020" Chapter 3
- Standard Corporate Finance Theory

Author: Valuation Engine Team
Date: 2025-10-17
Version: 1.0
"""

import sys
sys.path.append('..')

from typing import List, Dict, Optional
from datetime import datetime
from common.financial_math import FinancialCalculator, ValidationLibrary


class DCFEngine:
    """DCF 평가 엔진 핵심 클래스"""

    def __init__(self):
        self.calc = FinancialCalculator()
        self.validator = ValidationLibrary()

    def normalize_financials(self, raw_financials: List[Dict]) -> Dict:
        """
        과거 재무제표 정규화

        목적:
        - 일회성 손익 제거
        - 회계기준 통일
        - 정상화된 EBIT, FCF 산출

        Args:
            raw_financials: 과거 3~5년 재무제표
                [{
                    'year': 2022,
                    'revenue': 100000000000,
                    'operating_income': 15000000000,
                    'net_income': 10000000000,
                    'depreciation': 3000000000,
                    'capex': 5000000000,
                    'working_capital_change': 2000000000,
                    'tax_rate': 0.25,
                    'one_time_items': [500000000, -300000000]  # 일회성 손익
                }, ...]

        Returns:
            Dict: 정규화된 재무 데이터
        """
        normalized = {
            'years': [],
            'revenues': [],
            'operating_income': [],
            'net_income': [],
            'fcf': [],
            'operating_margin': [],
            'fcf_conversion': []
        }

        for year_data in raw_financials:
            year = year_data['year']
            revenue = year_data['revenue']

            # 영업이익 정규화 (일회성 손익 제거)
            adjusted_oi = year_data['operating_income']
            if 'one_time_items' in year_data:
                adjusted_oi -= sum(year_data['one_time_items'])

            # NOPAT 계산 (Net Operating Profit After Tax)
            tax_rate = year_data.get('tax_rate', 0.25)
            nopat = adjusted_oi * (1 - tax_rate)

            # FCF 계산
            depreciation = year_data.get('depreciation', 0)
            capex = year_data.get('capex', 0)
            wc_change = year_data.get('working_capital_change', 0)

            fcf = nopat + depreciation - capex - wc_change

            # 저장
            normalized['years'].append(year)
            normalized['revenues'].append(revenue)
            normalized['operating_income'].append(adjusted_oi)
            normalized['net_income'].append(year_data.get('net_income', 0))
            normalized['fcf'].append(fcf)
            normalized['operating_margin'].append(adjusted_oi / revenue if revenue > 0 else 0)
            normalized['fcf_conversion'].append(fcf / adjusted_oi if adjusted_oi > 0 else 0)

        # 평균 지표 계산
        normalized['avg_revenue_growth'] = self.calc.cagr(
            normalized['revenues'][0],
            normalized['revenues'][-1],
            len(normalized['revenues']) - 1
        ) if len(normalized['revenues']) > 1 else 0

        normalized['avg_operating_margin'] = sum(normalized['operating_margin']) / len(normalized['operating_margin'])
        normalized['avg_fcf_conversion'] = sum(normalized['fcf_conversion']) / len(normalized['fcf_conversion'])

        return normalized

    def project_financials(self,
                          base_financials: Dict,
                          assumptions: Dict,
                          periods: int = 5) -> List[Dict]:
        """
        재무제표 예측 (일반적으로 5년)

        Args:
            base_financials: 정규화된 과거 재무 데이터
            assumptions: 예측 가정
                {
                    'base_year': 2024,
                    'revenue_growth': [0.12, 0.10, 0.08, 0.06, 0.05],  # 연도별 성장률
                    'target_operating_margin': 0.15,  # 목표 영업이익률
                    'tax_rate': 0.25,
                    'depreciation_rate': 0.03,  # 매출액 대비 감가상각
                    'capex_rate': 0.05,  # 매출액 대비 CAPEX
                    'wc_rate': 0.10  # 매출 증가분 대비 운전자본 증가
                }
            periods: 예측 기간 (default: 5년)

        Returns:
            List[Dict]: 연도별 예측 재무제표
        """
        projections = []
        last_revenue = base_financials['revenues'][-1]
        base_year = assumptions['base_year']

        for year in range(1, periods + 1):
            # 매출 예측
            growth_rate = assumptions['revenue_growth'][year - 1]
            projected_revenue = last_revenue * (1 + growth_rate)

            # 영업이익 예측 (목표 마진)
            target_margin = assumptions.get('target_operating_margin',
                                           base_financials['avg_operating_margin'])
            projected_oi = projected_revenue * target_margin

            # NOPAT
            tax_rate = assumptions.get('tax_rate', 0.25)
            nopat = projected_oi * (1 - tax_rate)

            # 감가상각
            depreciation = projected_revenue * assumptions.get('depreciation_rate', 0.03)

            # CAPEX
            capex = projected_revenue * assumptions.get('capex_rate', 0.05)

            # 운전자본 증가
            revenue_increase = projected_revenue - last_revenue
            wc_change = revenue_increase * assumptions.get('wc_rate', 0.10)

            # FCF 계산
            fcf = nopat + depreciation - capex - wc_change

            projections.append({
                'year': base_year + year,
                'revenue': projected_revenue,
                'operating_income': projected_oi,
                'nopat': nopat,
                'depreciation': depreciation,
                'capex': capex,
                'wc_change': wc_change,
                'fcf': fcf,
                'operating_margin': target_margin,
                'fcf_margin': fcf / projected_revenue
            })

            last_revenue = projected_revenue

        return projections

    def calculate_wacc_detailed(self, wacc_inputs: Dict) -> Dict:
        """
        WACC 상세 계산

        Args:
            wacc_inputs:
                {
                    'risk_free_rate': 0.035,  # 10년 국고채 수익률
                    'beta': 1.2,  # 베타
                    'market_premium': 0.07,  # 시장위험프리미엄
                    'cost_of_debt': 0.05,  # 부채비용
                    'debt_ratio': 0.30,  # D/V
                    'tax_rate': 0.25  # 법인세율
                }

        Returns:
            Dict: WACC 및 구성요소
        """
        # 자기자본비용 (CAPM)
        cost_equity = (wacc_inputs['risk_free_rate'] +
                      wacc_inputs['beta'] * wacc_inputs['market_premium'])

        # WACC 계산
        wacc = self.calc.wacc(
            risk_free_rate=wacc_inputs['risk_free_rate'],
            beta=wacc_inputs['beta'],
            market_premium=wacc_inputs['market_premium'],
            cost_of_debt=wacc_inputs['cost_of_debt'],
            debt_ratio=wacc_inputs['debt_ratio'],
            tax_rate=wacc_inputs['tax_rate']
        )

        return {
            'wacc': wacc,
            'cost_of_equity': cost_equity,
            'cost_of_debt': wacc_inputs['cost_of_debt'],
            'after_tax_cost_of_debt': wacc_inputs['cost_of_debt'] * (1 - wacc_inputs['tax_rate']),
            'equity_weight': 1 - wacc_inputs['debt_ratio'],
            'debt_weight': wacc_inputs['debt_ratio'],
            'components': wacc_inputs
        }

    def discount_cash_flows(self, fcf_projections: List[Dict], wacc: float) -> Dict:
        """
        FCF 현재가치 할인

        Args:
            fcf_projections: 예측 FCF 리스트
            wacc: 할인율

        Returns:
            Dict: 할인된 FCF 상세
        """
        pv_fcf_list = []

        for t, projection in enumerate(fcf_projections, start=1):
            discount_factor = 1 / ((1 + wacc) ** t)
            pv_fcf = projection['fcf'] * discount_factor

            pv_fcf_list.append({
                'year': projection['year'],
                'fcf': projection['fcf'],
                'discount_factor': discount_factor,
                'pv_fcf': pv_fcf
            })

        total_pv_fcf = sum(item['pv_fcf'] for item in pv_fcf_list)

        return {
            'total_pv_fcf': total_pv_fcf,
            'pv_fcf_by_year': pv_fcf_list
        }

    def calculate_terminal_value_detailed(self,
                                         last_fcf: float,
                                         terminal_growth: float,
                                         wacc: float,
                                         last_period: int) -> Dict:
        """
        영구가치 상세 계산

        Args:
            last_fcf: 마지막 연도 FCF
            terminal_growth: 영구성장률
            wacc: WACC
            last_period: 마지막 예측 연도 (5년이면 5)

        Returns:
            Dict: 영구가치 상세
        """
        # Gordon Growth Model
        fcf_next_year = last_fcf * (1 + terminal_growth)
        terminal_value = self.calc.terminal_value(last_fcf, terminal_growth, wacc)
        pv_terminal_value = self.calc.pv_terminal_value(terminal_value, wacc, last_period)

        return {
            'last_fcf': last_fcf,
            'terminal_growth': terminal_growth,
            'fcf_next_year': fcf_next_year,
            'terminal_value': terminal_value,
            'pv_terminal_value': pv_terminal_value,
            'discount_factor': 1 / ((1 + wacc) ** last_period),
            'capitalization_rate': wacc - terminal_growth
        }

    def calculate_equity_value(self,
                              pv_fcf: float,
                              pv_tv: float,
                              adjustments: Dict) -> Dict:
        """
        주주가치 계산

        Args:
            pv_fcf: FCF 현재가치 합계
            pv_tv: 영구가치 현재가치
            adjustments:
                {
                    'cash': 현금및현금성자산,
                    'total_debt': 총 부채,
                    'non_operating_assets': 비영업자산,
                    'shares_outstanding': 발행주식수
                }

        Returns:
            Dict: 기업가치, 주주가치, 주당가치
        """
        # 기업가치 (Enterprise Value)
        enterprise_value = pv_fcf + pv_tv

        # 순부채 (Net Debt)
        net_debt = adjustments.get('total_debt', 0) - adjustments.get('cash', 0)

        # 비영업자산
        non_op_assets = adjustments.get('non_operating_assets', 0)

        # 주주가치 (Equity Value)
        equity_value = enterprise_value - net_debt + non_op_assets

        # 주당가치
        shares = adjustments['shares_outstanding']
        value_per_share = (equity_value * 1_000_000) / shares  # 백만원 → 원

        # 영구가치 비중 확인
        tv_ratio, is_normal = self.validator.sanity_check_terminal_value_ratio(pv_fcf, pv_tv)

        return {
            'enterprise_value': enterprise_value,
            'pv_fcf': pv_fcf,
            'pv_terminal_value': pv_tv,
            'net_debt': net_debt,
            'non_operating_assets': non_op_assets,
            'equity_value': equity_value,
            'shares_outstanding': shares,
            'value_per_share': value_per_share,
            'terminal_value_ratio': tv_ratio,
            'tv_ratio_is_normal': is_normal
        }

    def run_valuation(self, inputs: Dict) -> Dict:
        """
        DCF 평가 전체 프로세스 실행

        Args:
            inputs: 전체 입력 데이터
                {
                    'company_id': 'C12345',
                    'company_name': '삼성전자',
                    'valuation_date': '2025-01-01',
                    'historical_financials': [...],
                    'assumptions': {...},
                    'wacc_inputs': {...},
                    'adjustments': {...}
                }

        Returns:
            Dict: 전체 평가 결과
        """
        valuation_id = f"DCF_{inputs['company_id']}_{inputs['valuation_date'].replace('-', '')}"

        # Step 1: 과거 재무제표 정규화
        print(f"\n[Step 1] 과거 재무제표 정규화...")
        normalized = self.normalize_financials(inputs['historical_financials'])
        print(f"  - 평균 매출 성장률: {normalized['avg_revenue_growth']:.2%}")
        print(f"  - 평균 영업이익률: {normalized['avg_operating_margin']:.2%}")

        # Step 2: 재무제표 예측
        print(f"\n[Step 2] 재무제표 예측 (5년)...")
        projections = self.project_financials(
            normalized,
            inputs['assumptions'],
            periods=inputs.get('projection_period', 5)
        )
        print(f"  - 예측 기간: {projections[0]['year']} ~ {projections[-1]['year']}")
        print(f"  - 최종 연도 FCF: {projections[-1]['fcf']:,.0f}")

        # Step 3: WACC 계산
        print(f"\n[Step 3] WACC 계산...")
        wacc_result = self.calculate_wacc_detailed(inputs['wacc_inputs'])
        print(f"  - WACC: {wacc_result['wacc']:.4f} ({wacc_result['wacc']:.2%})")
        print(f"  - 자기자본비용: {wacc_result['cost_of_equity']:.2%}")

        # Step 4: FCF 할인
        print(f"\n[Step 4] FCF 현재가치 할인...")
        discounted = self.discount_cash_flows(projections, wacc_result['wacc'])
        print(f"  - PV(FCF): {discounted['total_pv_fcf']:,.0f}")

        # Step 5: 영구가치
        print(f"\n[Step 5] 영구가치 계산...")
        terminal_growth = inputs['assumptions']['terminal_growth']
        tv_result = self.calculate_terminal_value_detailed(
            projections[-1]['fcf'],
            terminal_growth,
            wacc_result['wacc'],
            len(projections)
        )
        print(f"  - 영구가치: {tv_result['terminal_value']:,.0f}")
        print(f"  - PV(TV): {tv_result['pv_terminal_value']:,.0f}")

        # Step 6: 기업가치 및 주당가치
        print(f"\n[Step 6] 기업가치 및 주당가치 산출...")
        equity_result = self.calculate_equity_value(
            discounted['total_pv_fcf'],
            tv_result['pv_terminal_value'],
            inputs['adjustments']
        )
        print(f"  - 기업가치: {equity_result['enterprise_value']:,.0f}")
        print(f"  - 주주가치: {equity_result['equity_value']:,.0f}")
        print(f"  - 주당가치: {equity_result['value_per_share']:,.0f}원")
        print(f"  - 영구가치 비중: {equity_result['terminal_value_ratio']:.2%}")

        # 최종 결과
        return {
            'valuation_id': valuation_id,
            'company_id': inputs['company_id'],
            'company_name': inputs.get('company_name', ''),
            'valuation_date': inputs['valuation_date'],
            'normalized_financials': normalized,
            'projections': projections,
            'wacc': wacc_result,
            'discounted_fcf': discounted,
            'terminal_value': tv_result,
            'valuation_result': equity_result,
            'created_at': datetime.now().isoformat()
        }


# 테스트 케이스
if __name__ == "__main__":
    print("=" * 80)
    print("DCF Engine - Test Case")
    print("=" * 80)

    # 샘플 입력 데이터 (KPMG 가이드 기반)
    test_inputs = {
        'company_id': 'TEST001',
        'company_name': '테스트기업',
        'valuation_date': '2025-01-01',
        'historical_financials': [
            {
                'year': 2022,
                'revenue': 100000000000,  # 1,000억
                'operating_income': 12000000000,  # 120억
                'net_income': 8000000000,
                'depreciation': 3000000000,
                'capex': 4000000000,
                'working_capital_change': 1000000000,
                'tax_rate': 0.25,
                'one_time_items': [500000000]  # 일회성 이익 5억
            },
            {
                'year': 2023,
                'revenue': 115000000000,
                'operating_income': 15000000000,
                'net_income': 10000000000,
                'depreciation': 3500000000,
                'capex': 5000000000,
                'working_capital_change': 1500000000,
                'tax_rate': 0.25
            },
            {
                'year': 2024,
                'revenue': 130000000000,
                'operating_income': 18000000000,
                'net_income': 12000000000,
                'depreciation': 4000000000,
                'capex': 6000000000,
                'working_capital_change': 1500000000,
                'tax_rate': 0.25
            }
        ],
        'assumptions': {
            'base_year': 2024,
            'revenue_growth': [0.12, 0.10, 0.08, 0.06, 0.05],
            'target_operating_margin': 0.15,
            'tax_rate': 0.25,
            'depreciation_rate': 0.03,
            'capex_rate': 0.05,
            'wc_rate': 0.10,
            'terminal_growth': 0.03
        },
        'wacc_inputs': {
            'risk_free_rate': 0.035,
            'beta': 1.2,
            'market_premium': 0.07,
            'cost_of_debt': 0.05,
            'debt_ratio': 0.30,
            'tax_rate': 0.25
        },
        'adjustments': {
            'cash': 10000000000,  # 현금 100억
            'total_debt': 30000000000,  # 부채 300억
            'non_operating_assets': 5000000000,  # 비영업자산 50억
            'shares_outstanding': 10000000  # 발행주식 1,000만주
        }
    }

    # DCF 실행
    engine = DCFEngine()
    result = engine.run_valuation(test_inputs)

    print("\n" + "=" * 80)
    print("DCF Valuation Results")
    print("=" * 80)
    print(f"기업가치: {result['valuation_result']['enterprise_value']:,.0f}원")
    print(f"주주가치: {result['valuation_result']['equity_value']:,.0f}원")
    print(f"주당가치: {result['valuation_result']['value_per_share']:,.0f}원")
    print("=" * 80)
