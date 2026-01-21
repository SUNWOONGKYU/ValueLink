"""
상속세 및 증여세법 평가법 엔진 (Inheritance Tax Law Valuation Engine)
상속세 및 증여세법 시행령 제54조

작성일: 2025-10-17
핵심 질문: "상속세 및 증여세법상 평가액은?"
"""

from typing import Dict, Optional


class InheritanceTaxLawEngine:
    """상속세 및 증여세법 평가법 엔진"""

    def __init__(self):
        pass

    def run_valuation(self,
                     net_income_3yr: float,
                     net_assets: float,
                     controlling_premium: bool = False,
                     minority_discount: float = 0.0,
                     marketability_discount: float = 0.0) -> Dict:
        """
        상증세법 평가 실행

        법적 근거: 상속세 및 증여세법 시행령 제54조
        계산식: (순손익가치 × 3 + 순자산가치 × 2) ÷ 5

        Args:
            net_income_3yr: 최근 3년 순손익 합계 (백만원)
            net_assets: 순자산 장부가액 (백만원)
            controlling_premium: 지배주주 여부 (True면 +20% 할증)
            minority_discount: 소액주주 할인율 (0.10 = 10% 할인)
            marketability_discount: 유동성 할인율 (0.20 = 20% 할인)

        Returns:
            {
                'itl_value': 상증세법 평가액,
                'income_value': 순손익가치,
                'asset_value': 순자산가치,
                'base_value': 할증/할인 전 기본가치,
                'adjustments': 할증/할인 내역,
                'value_per_share': 주당 가치
            }
        """

        # 1. 순손익가치 계산
        # 순손익가치 = (최근 3년 순손익 합계 / 3) × 3 / 0.10
        # = 평균 순손익 × 30
        avg_net_income = net_income_3yr / 3
        income_value = avg_net_income * 3 / 0.10  # 할인율 10% 적용

        # 2. 순자산가치
        asset_value = net_assets

        # 3. 가중평균 (순손익가치 × 3, 순자산가치 × 2)
        base_value = (income_value * 3 + asset_value * 2) / 5

        # 4. 할증/할인 적용
        adjustments = []
        final_value = base_value

        if controlling_premium:
            # 지배주주 할증 20%
            premium = base_value * 0.20
            final_value += premium
            adjustments.append({
                'type': '지배주주 할증',
                'rate': 0.20,
                'amount': premium,
                'reason': '상증세법 시행령 제54조 - 지배주주 20% 할증'
            })
        else:
            # 소액주주 할인
            if minority_discount > 0:
                discount_amount = base_value * minority_discount
                final_value -= discount_amount
                adjustments.append({
                    'type': '소액주주 할인',
                    'rate': -minority_discount,
                    'amount': -discount_amount,
                    'reason': f'소액주주 {minority_discount:.0%} 할인'
                })

        # 유동성 할인 (비상장)
        if marketability_discount > 0:
            discount_amount = base_value * marketability_discount
            final_value -= discount_amount
            adjustments.append({
                'type': '유동성 할인',
                'rate': -marketability_discount,
                'amount': -discount_amount,
                'reason': f'비상장 주식 유동성 할인 {marketability_discount:.0%}'
            })

        return {
            'itl_value': round(final_value, 0),
            'income_value': round(income_value, 0),
            'asset_value': round(asset_value, 0),
            'base_value': round(base_value, 0),
            'avg_net_income': round(avg_net_income, 0),
            'adjustments': adjustments,
            'total_adjustment': round(final_value - base_value, 0),
            'legal_basis': '상속세 및 증여세법 시행령 제54조',
            'formula': f'({income_value:,.0f} × 3 + {asset_value:,.0f} × 2) ÷ 5'
        }

    def calculate_value_per_share(self, itl_value: float, shares_outstanding: int) -> float:
        """
        주당 가치 계산

        Args:
            itl_value: 상증세법 평가액 (백만원)
            shares_outstanding: 발행주식수

        Returns:
            주당 가치 (원)
        """
        return (itl_value * 1_000_000) / shares_outstanding

    def determine_shareholder_type(self, ownership_ratio: float) -> Dict:
        """
        주주 유형 판단 (지배주주 vs 소액주주)

        Args:
            ownership_ratio: 지분율 (0.30 = 30%)

        Returns:
            {
                'type': '지배주주' or '소액주주',
                'controlling_premium': True/False,
                'recommended_minority_discount': 할인율
            }
        """
        if ownership_ratio >= 0.50:
            # 50% 이상 → 지배주주
            return {
                'type': '지배주주 (과반)',
                'controlling_premium': True,
                'recommended_minority_discount': 0.0,
                'reason': '지분율 50% 이상 - 경영권 보유'
            }
        elif ownership_ratio >= 0.30:
            # 30~50% → 준지배주주
            return {
                'type': '준지배주주',
                'controlling_premium': False,
                'recommended_minority_discount': 0.10,  # 10% 할인
                'reason': '지분율 30~50% - 경영 참여 가능'
            }
        elif ownership_ratio >= 0.10:
            # 10~30% → 유력주주
            return {
                'type': '유력주주',
                'controlling_premium': False,
                'recommended_minority_discount': 0.20,  # 20% 할인
                'reason': '지분율 10~30% - 일부 영향력'
            }
        else:
            # 10% 미만 → 소액주주
            return {
                'type': '소액주주',
                'controlling_premium': False,
                'recommended_minority_discount': 0.30,  # 30% 할인
                'reason': '지분율 10% 미만 - 경영권 없음'
            }

    def generate_full_report(self,
                            net_income_3yr: float,
                            net_assets: float,
                            shares_outstanding: int,
                            ownership_ratio: float,
                            is_listed: bool = False,
                            purpose: str = '상속/증여') -> Dict:
        """
        상증세법 평가 전체 보고서 생성

        Args:
            net_income_3yr: 최근 3년 순손익 합계 (백만원)
            net_assets: 순자산 장부가액 (백만원)
            shares_outstanding: 발행주식수
            ownership_ratio: 지분율
            is_listed: 상장 여부
            purpose: 평가 목적

        Returns:
            전체 보고서 Dict
        """
        # 1. 주주 유형 판단
        shareholder_info = self.determine_shareholder_type(ownership_ratio)

        # 2. 할인율 결정
        minority_discount = shareholder_info['recommended_minority_discount']
        marketability_discount = 0.0 if is_listed else 0.20  # 비상장 20% 할인

        # 3. 상증세법 평가
        result = self.run_valuation(
            net_income_3yr=net_income_3yr,
            net_assets=net_assets,
            controlling_premium=shareholder_info['controlling_premium'],
            minority_discount=minority_discount,
            marketability_discount=marketability_discount
        )

        # 4. 주당 가치
        value_per_share = self.calculate_value_per_share(
            result['itl_value'], shares_outstanding
        )

        # 5. 보고서 통합
        report = {
            **result,
            'value_per_share': round(value_per_share, 0),
            'shares_outstanding': shares_outstanding,
            'ownership_ratio': ownership_ratio,
            'shareholder_type': shareholder_info['type'],
            'is_listed': is_listed,
            'purpose': purpose,
            'summary': self._generate_summary(
                result, value_per_share, shareholder_info, purpose
            )
        }

        return report

    def _generate_summary(self, result: Dict, value_per_share: float,
                         shareholder_info: Dict, purpose: str) -> str:
        """평가 요약 텍스트 생성"""
        adjustments_text = ""
        for adj in result['adjustments']:
            adjustments_text += f"║ • {adj['type']}: {adj['rate']:+.0%} ({adj['amount']:+,.0f}백만원)\n"

        summary = f"""
╔════════════════════════════════════════════════════════════╗
║           상증세법 평가 요약                                ║
╠════════════════════════════════════════════════════════════╣
║ 평가 목적: {purpose}
║ 법적 근거: {result['legal_basis']}
║ 주주 유형: {shareholder_info['type']}
║
║ [계산 과정]
║ 1. 순손익가치: {result['income_value']:,}백만원
║    (최근 3년 평균 순손익 {result['avg_net_income']:,} × 30)
║
║ 2. 순자산가치: {result['asset_value']:,}백만원
║
║ 3. 가중평균 (순손익×3 + 순자산×2) ÷ 5:
║    {result['base_value']:,}백만원
║
║ [할증/할인]
{adjustments_text}║    총 조정: {result['total_adjustment']:+,}백만원
║
║ [최종 평가액]
║ • 기업가치: {result['itl_value']:,}백만원
║ • 주당가치: {value_per_share:,.0f}원
╚════════════════════════════════════════════════════════════╝
        """
        return summary.strip()


# ==================== 테스트 코드 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("상증세법 평가 테스트")
    print("=" * 60)

    # Case 1: 지배주주 (50% 이상)
    print("\n[Case 1: 지배주주 상속 (지분 80%)]")

    net_income_3yr = 35_000  # 최근 3년 순손익 합계 350억 (100억, 120억, 130억)
    net_assets = 60_000  # 순자산 600억
    shares = 1_000_000
    ownership = 0.80

    engine = InheritanceTaxLawEngine()
    result = engine.generate_full_report(
        net_income_3yr=net_income_3yr,
        net_assets=net_assets,
        shares_outstanding=shares,
        ownership_ratio=ownership,
        is_listed=False,
        purpose='상속세 신고'
    )

    print(result['summary'])

    # Case 2: 소액주주 (10% 미만)
    print("\n" + "=" * 60)
    print("\n[Case 2: 소액주주 증여 (지분 5%)]")

    result2 = engine.generate_full_report(
        net_income_3yr=net_income_3yr,
        net_assets=net_assets,
        shares_outstanding=shares,
        ownership_ratio=0.05,  # 5% 소액주주
        is_listed=False,
        purpose='증여세 신고'
    )

    print(result2['summary'])

    # Case 3: 비교
    print("\n" + "=" * 60)
    print("\n[주주 유형별 가치 비교]")
    print(f"• 지배주주 (80%): {result['itl_value']:,}백만원 ({result['value_per_share']:,}원/주)")
    print(f"• 소액주주 (5%):  {result2['itl_value']:,}백만원 ({result2['value_per_share']:,}원/주)")
    print(f"• 차이: {result['itl_value'] - result2['itl_value']:+,}백만원 "
          f"({(result['itl_value'] / result2['itl_value'] - 1) * 100:+.1f}%)")

    print("\n" + "=" * 60)

    # Case 4: 상장사 vs 비상장사
    print("\n[Case 4: 상장사 vs 비상장사 비교]")

    result_listed = engine.run_valuation(
        net_income_3yr=net_income_3yr,
        net_assets=net_assets,
        controlling_premium=False,
        minority_discount=0.30,  # 소액주주 30%
        marketability_discount=0.0  # 상장사 → 유동성 할인 없음
    )

    result_unlisted = engine.run_valuation(
        net_income_3yr=net_income_3yr,
        net_assets=net_assets,
        controlling_premium=False,
        minority_discount=0.30,  # 소액주주 30%
        marketability_discount=0.20  # 비상장 → 유동성 할인 20%
    )

    print(f"\n상장사 (유동성 할인 없음): {result_listed['itl_value']:,}백만원")
    print(f"비상장사 (유동성 할인 20%): {result_unlisted['itl_value']:,}백만원")
    print(f"차이: {result_listed['itl_value'] - result_unlisted['itl_value']:+,}백만원 "
          f"({(result_listed['itl_value'] / result_unlisted['itl_value'] - 1) * 100:+.1f}%)")

    print("\n" + "=" * 60)

    # Case 5: 실전 예시 - 가업승계
    print("\n[Case 5: 실전 예시 - 가업승계]")

    print("\n[시나리오]")
    print("• 부모 (지배주주 80%) → 자녀에게 40% 증여")
    print("• 증여 후: 부모 40%, 자녀 40%")

    # 증여 전 (부모 80%)
    result_before = engine.generate_full_report(
        net_income_3yr=net_income_3yr,
        net_assets=net_assets,
        shares_outstanding=shares,
        ownership_ratio=0.80,
        is_listed=False,
        purpose='증여 전 평가'
    )

    # 증여 후 (자녀 40%)
    result_after = engine.generate_full_report(
        net_income_3yr=net_income_3yr,
        net_assets=net_assets,
        shares_outstanding=shares,
        ownership_ratio=0.40,
        is_listed=False,
        purpose='증여 후 평가'
    )

    print(f"\n증여 전 (부모 80% 보유 시 주당 가치):")
    print(f"  주당가치: {result_before['value_per_share']:,}원")
    print(f"  총가치: {result_before['itl_value']:,}백만원")

    print(f"\n증여 후 (자녀 40% 보유 시 주당 가치):")
    print(f"  주당가치: {result_after['value_per_share']:,}원")
    print(f"  40% 가치: {result_after['itl_value'] * 0.40 / 0.40:,.0f}백만원")

    print(f"\n40% 증여세 과세표준:")
    print(f"  {result_after['value_per_share']:,}원 × {shares * 0.40:,.0f}주")
    print(f"  = {result_after['value_per_share'] * shares * 0.40 / 1_000_000:,.0f}백만원")

    print("\n" + "=" * 60)
