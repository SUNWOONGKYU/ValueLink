# -*- coding: utf-8 -*-
"""
상속세 및 증여세법 평가법 엔진 (Inheritance Tax Law Valuation Engine)
상속세 및 증여세법 시행령 제54조·제56조

작성일: 2025-10-17

2026-07-16 법령 교정 — 순손익가치 가중평균(3:2:1)÷6÷환원율(구: 평균×3÷10%,
약 3배 과대계상), 80% 하한 신설, 할증 배제 3사유, 임의 할인 제거.
근거: 시행령 제54조·56조, 법 제63조③ (법제처 공식 API 원문 대조).

핵심 산식:
1. 순손익가치: 3개년 개별 순손익을 가중평균(직전년×3 + 2년전×2 + 3년전×1)÷6
   → 가중평균 후 0 하한 1회 적용 → ÷ 환원율(기본 10%) = 순손익가치
2. 가중평균: 일반법인 (순손익가치×3 + 순자산가치×2)÷5,
   부동산과다보유법인 (순손익가치×2 + 순자산가치×3)÷5
3. 순자산가치 80% 하한 (시행령 제54조 제1항 단서):
   가중평균액 < 순자산가치×80% 이면 순자산가치×80%를 평가액으로 함
4. 최대주주 등 할증 (법 제63조 제3항): 지분율 50% 초과이면 +20% 할증.
   단, 아래 중 하나에 해당하면 할증을 배제한다 (2026-02-27 시행 시행령 기준):
     ① 중소기업
     ② 중견기업
     ③ 평가기준일이 속하는 사업연도 전 3년 이내 사업연도부터 계속하여 결손금이 있는 법인
        (본 엔진은 입력된 3개년 순손익이 전부 음수이면 이 요건을 충족한 것으로 자동 판정한다)
5. 임의 할인(소액주주 할인, 비상장 유동성 할인) 없음 — 상증세법상 근거 없어 전면 삭제.

환원율은 "3년 만기 회사채 유통수익률을 고려하여 기획재정부령으로 정하는 이자율"이며
현행 시행규칙상 10%이나 고시로 변경될 수 있어 파라미터(discount_rate, 기본값 0.10)로
유지한다.

⚠️ 호환성 참고: 구 시그니처(net_income_3yr 합계 1개 값, controlling_premium,
minority_discount, marketability_discount)는 폐기되었다. 이 엔진을 호출하는
app/services/valuation_orchestrator.py도 함께 신 시그니처(net_income_year1/2/3,
is_real_estate_heavy, is_sme, is_medium_large, discount_rate)로 갱신했다.

⚠️ 2026-07-16 최대주주 판정 결함 수정 (지휘관 지시, 소대장 품질 감사에서 발견):
법 제63조 제3항의 "최대주주 등"은 지분율 50% 초과가 아니라 "본인 + 특수관계인의
지분을 합산해 그 합계가 가장 큰 주주 그룹"이다 (시행령 제53조). 지분율이 낮아도
(예: 40%) 특수관계인 합산 결과 최대주주 등이면 할증 대상이므로, 종전의
"지분율 50% 초과" 단독 판정은 이런 케이스를 놓쳐 과소평가를 낳는다. 이제
is_largest_shareholder(bool) 파라미터로 특수관계인 합산 판정 결과를 직접 입력받고,
이 값이 최대주주 등 할증 판정의 기준이 된다. 하위호환을 위해 파라미터 미지정(None)
시에는 종전처럼 지분율 50% 초과 여부로 추정하되, 결과에 "지분율 기준 추정 —
특수관계인 합산 확인 필요" 경고를 반환한다.
"""

import sys
from typing import Dict


class InheritanceTaxLawEngine:
    """상속세 및 증여세법 평가법 엔진 (법령 교정판)"""

    def __init__(self):
        pass

    def run_valuation(self,
                       net_income_year1: float,
                       net_income_year2: float,
                       net_income_year3: float,
                       net_assets: float,
                       is_real_estate_heavy: bool = False,
                       is_sme: bool = False,
                       is_medium_large: bool = False,
                       ownership_ratio: float = 0.0,
                       is_largest_shareholder: bool = None,
                       discount_rate: float = 0.10) -> Dict:
        """
        상증세법 평가 실행

        법적 근거: 상속세 및 증여세법 시행령 제54조(보충적 평가방법), 제56조(순손익가치)

        Args:
            net_income_year1: 직전연도(1년전) 순손익 (백만원, 가중치 3)
            net_income_year2: 2년전 순손익 (백만원, 가중치 2)
            net_income_year3: 3년전 순손익 (백만원, 가중치 1)
            net_assets: 순자산 장부가액 (백만원)
            is_real_estate_heavy: 부동산과다보유법인 여부 (True면 가중치 2:3, False면 3:2)
            is_sme: 중소기업 여부 (True면 최대주주 할증 배제)
            is_medium_large: 중견기업 여부 (True면 최대주주 할증 배제)
            ownership_ratio: 지분율 (참고용 — 최대주주 등 판정은 is_largest_shareholder 우선)
            is_largest_shareholder: 본인 + 특수관계인 합산 지분 기준 "최대주주 등"
                해당 여부 (법 제63조 제3항, 시행령 제53조). True/False로 명시하면 이
                값이 할증 판정 기준이 된다. None(미지정)이면 하위호환을 위해 지분율
                50% 초과 여부로 추정하고 경고를 반환한다.
            discount_rate: 환원율 (기본 10% = 0.10, 기획재정부령 고시 이자율 — 신고 시점 최신 고시값 확인 필요)

        Returns:
            계산 과정 전체를 담은 dict
        """
        # 1. 3개년 가중평균 순손익 (직전×3 + 2년전×2 + 3년전×1) ÷ 6
        raw_weighted_profit = (net_income_year1 * 3 + net_income_year2 * 2 + net_income_year3 * 1) / 6

        # 0 하한은 가중평균 이후 1회만 적용 (적자 연도를 먼저 0으로 올리면 과대계상됨)
        weighted_profit = max(0.0, raw_weighted_profit)
        floor_applied_to_profit = raw_weighted_profit < 0

        # 2. 순손익가치 = 가중평균 순손익 ÷ 환원율
        income_value = weighted_profit / discount_rate if discount_rate > 0 else 0.0

        # 3. 순자산가치
        asset_value = net_assets

        # 4. 가중평균 (법인 유형별 가중치)
        if is_real_estate_heavy:
            profit_weight, asset_weight = 2, 3
        else:
            profit_weight, asset_weight = 3, 2

        base_value = (income_value * profit_weight + asset_value * asset_weight) / 5

        # 5. 순자산가치 80% 하한 (시행령 제54조 제1항 단서)
        asset_floor = asset_value * 0.8
        floor_applied = base_value < asset_floor
        value_before_premium = asset_floor if floor_applied else base_value

        # 6. 최대주주 등 할증 판정 (법 제63조 제3항, 시행령 제53조)
        #    "최대주주 등"은 본인 + 특수관계인 지분을 합산해 그 합계가 가장 큰 주주
        #    그룹을 의미한다 — 지분율 50% 초과라는 단순 기준이 아니다. 지분율이 낮아도
        #    (예: 40%) 특수관계인 합산 결과 최대주주 등이면 할증 대상이다.
        #    is_largest_shareholder가 명시되면 그 값을 그대로 판정 기준으로 삼고,
        #    미지정(None)이면 하위호환을 위해 지분율 50% 초과 여부로 추정하되 경고를 낸다.
        #    할증 배제 사유 3가지 (2026-02-27 시행 시행령 기준):
        #    ① 중소기업 ② 중견기업 ③ 평가기준일 전 3년 이내부터 계속 결손금이 있는 법인
        adjustments = []
        is_continuing_loss = net_income_year1 < 0 and net_income_year2 < 0 and net_income_year3 < 0

        if is_largest_shareholder is not None:
            is_controlling = bool(is_largest_shareholder)
            largest_shareholder_basis = '입력값(본인+특수관계인 합산 최대주주 등 여부 직접 확인)'
            largest_shareholder_warning = None
        else:
            is_controlling = ownership_ratio > 0.50
            largest_shareholder_basis = '지분율 50% 초과 여부로 추정 (특수관계인 합산 미확인)'
            largest_shareholder_warning = (
                '최대주주 등 해당 여부를 지분율 50% 초과 기준으로 추정했습니다(특수관계인 '
                '합산 미확인). 상증세법 제63조 제3항의 "최대주주 등"은 본인과 특수관계인의 '
                '지분을 합산해 가장 지분이 많은 주주 그룹인지로 판정하므로, 지분율이 50% '
                '이하라도 특수관계인 합산 시 최대주주 등에 해당하면 할증 대상입니다. '
                '정확한 판정을 위해 is_largest_shareholder 값을 확인해 입력하세요.'
            )

        exemption_reasons = []
        if is_sme:
            exemption_reasons.append('중소기업')
        if is_medium_large:
            exemption_reasons.append('중견기업')
        if is_continuing_loss:
            exemption_reasons.append('평가기준일 전 3년 이내부터 계속 결손금이 있는 법인')

        premium_applied = is_controlling and not exemption_reasons
        final_value = value_before_premium

        if premium_applied:
            premium = value_before_premium * 0.20
            final_value += premium
            adjustments.append({
                'type': '최대주주 등 할증',
                'rate': 0.20,
                'amount': premium,
                'reason': f'상증세법 제63조 제3항 - 최대주주 등({largest_shareholder_basis}) 20% 할증, 할증 배제 사유 없음'
            })
        elif is_controlling and exemption_reasons:
            adjustments.append({
                'type': '최대주주 할증 배제',
                'rate': 0.0,
                'amount': 0.0,
                'reason': f"할증 배제 사유 해당: {', '.join(exemption_reasons)}"
            })

        return {
            'itl_value': round(final_value, 0),
            'income_value': round(income_value, 0),
            'asset_value': round(asset_value, 0),
            'base_value': round(base_value, 0),
            'raw_weighted_profit': round(raw_weighted_profit, 1),
            'weighted_profit': round(weighted_profit, 1),
            'floor_applied_to_profit': floor_applied_to_profit,
            'asset_floor': round(asset_floor, 0),
            'floor_applied': floor_applied,
            'value_before_premium': round(value_before_premium, 0),
            'profit_weight': profit_weight,
            'asset_weight': asset_weight,
            'is_continuing_loss': is_continuing_loss,
            'is_controlling': is_controlling,
            'largest_shareholder_basis': largest_shareholder_basis,
            'largest_shareholder_warning': largest_shareholder_warning,
            'premium_exemption_reasons': exemption_reasons,
            'adjustments': adjustments,
            'total_adjustment': round(final_value - value_before_premium, 0),
            'discount_rate': discount_rate,
            'legal_basis': '상속세 및 증여세법 시행령 제54조·제56조, 법 제63조 제3항',
            'formula': f'({income_value:,.0f} × {profit_weight} + {asset_value:,.0f} × {asset_weight}) ÷ 5'
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

    def determine_shareholder_type(self, ownership_ratio: float, is_largest_shareholder: bool = None) -> Dict:
        """
        주주 유형 판단 (최대주주 등 할증 대상 여부만 판단 — 임의 할인 로직 없음)

        Args:
            ownership_ratio: 지분율 (0.30 = 30%, 참고용)
            is_largest_shareholder: 본인+특수관계인 합산 최대주주 등 여부 (법 제63조③).
                None이면 하위호환으로 지분율 50% 초과 여부로 추정한다.

        Returns:
            {'type': ..., 'is_controlling': True/False, 'reason': ..., 'basis': ...}
        """
        if is_largest_shareholder is not None:
            basis = '입력값(특수관계인 합산 확인됨)'
            if is_largest_shareholder:
                return {
                    'type': '최대주주 등 (특수관계인 합산 최대지분)',
                    'is_controlling': True,
                    'reason': '본인과 특수관계인의 지분을 합산한 결과 최대지분 주주 그룹에 해당 - 상증세법 제63조 제3항 최대주주 할증 검토 대상',
                    'basis': basis,
                }
            return {
                'type': '일반주주 (특수관계인 합산해도 최대주주 아님)',
                'is_controlling': False,
                'reason': '본인과 특수관계인 지분을 합산해도 최대주주 등에 해당하지 않음 - 최대주주 할증 대상 아님',
                'basis': basis,
            }

        basis = '지분율 기준 추정(특수관계인 합산 미확인)'
        if ownership_ratio > 0.50:
            return {
                'type': '최대주주 등 (지분율 기준 추정)',
                'is_controlling': True,
                'reason': '지분율 50% 초과 - 상증세법 제63조 제3항 최대주주 할증 검토 대상 (특수관계인 합산 미확인 추정치)',
                'basis': basis,
            }
        return {
            'type': '일반주주 (지분율 기준 추정)',
            'is_controlling': False,
            'reason': '지분율 50% 이하 - 지분율만으로는 최대주주 아님. 특수관계인 합산 시 최대주주 등에 해당할 수 있어 확인 필요 (별도의 소액주주 할인 등 임의 할인은 상증세법상 근거 없어 적용하지 않음)',
            'basis': basis,
        }

    def generate_full_report(self,
                              net_income_year1: float,
                              net_income_year2: float,
                              net_income_year3: float,
                              net_assets: float,
                              shares_outstanding: int,
                              ownership_ratio: float,
                              is_real_estate_heavy: bool = False,
                              is_sme: bool = False,
                              is_medium_large: bool = False,
                              is_largest_shareholder: bool = None,
                              discount_rate: float = 0.10,
                              purpose: str = '상속/증여') -> Dict:
        """
        상증세법 평가 전체 보고서 생성

        Args:
            net_income_year1: 직전연도(1년전) 순손익 (백만원)
            net_income_year2: 2년전 순손익 (백만원)
            net_income_year3: 3년전 순손익 (백만원)
            net_assets: 순자산 장부가액 (백만원)
            shares_outstanding: 발행주식수
            ownership_ratio: 지분율 (참고용 — 최대주주 등 판정은 is_largest_shareholder 우선)
            is_real_estate_heavy: 부동산과다보유법인 여부
            is_sme: 중소기업 여부 (할증 배제 사유 ①)
            is_medium_large: 중견기업 여부 (할증 배제 사유 ②)
            is_largest_shareholder: 본인+특수관계인 합산 최대주주 등 여부 (법 제63조③).
                None이면 지분율 50% 초과 여부로 추정 + 경고.
            discount_rate: 환원율 (기본 10%)
            purpose: 평가 목적

        Returns:
            전체 보고서 Dict
        """
        shareholder_info = self.determine_shareholder_type(ownership_ratio, is_largest_shareholder)

        result = self.run_valuation(
            net_income_year1=net_income_year1,
            net_income_year2=net_income_year2,
            net_income_year3=net_income_year3,
            net_assets=net_assets,
            is_real_estate_heavy=is_real_estate_heavy,
            is_sme=is_sme,
            is_medium_large=is_medium_large,
            ownership_ratio=ownership_ratio,
            is_largest_shareholder=is_largest_shareholder,
            discount_rate=discount_rate,
        )

        value_per_share = self.calculate_value_per_share(
            result['itl_value'], shares_outstanding
        )

        report = {
            **result,
            'value_per_share': round(value_per_share, 0),
            'shares_outstanding': shares_outstanding,
            'ownership_ratio': ownership_ratio,
            'shareholder_type': shareholder_info['type'],
            'is_real_estate_heavy': is_real_estate_heavy,
            'is_sme': is_sme,
            'is_medium_large': is_medium_large,
            'is_largest_shareholder': is_largest_shareholder,
            'purpose': purpose,
            'net_income_year1': net_income_year1,
            'net_income_year2': net_income_year2,
            'net_income_year3': net_income_year3,
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
        if not adjustments_text:
            adjustments_text = "║ • (해당 없음)\n"

        floor_note = ""
        if result['floor_applied']:
            floor_note = f"\n║ ※ 순자산가치 80% 하한 적용 ({result['asset_value']:,}백만원 × 80% = {result['asset_floor']:,}백만원)"

        basis_note = f"\n║ ※ 최대주주 판정 근거: {result['largest_shareholder_basis']}"
        if result.get('largest_shareholder_warning'):
            basis_note += f"\n║ ⚠ {result['largest_shareholder_warning']}"

        summary = f"""
╔════════════════════════════════════════════════════════════╗
║           상증세법 평가 요약                                ║
╠════════════════════════════════════════════════════════════╣
║ 평가 목적: {purpose}
║ 법적 근거: {result['legal_basis']}
║ 주주 유형: {shareholder_info['type']}
║ 법인 유형: {'부동산과다보유법인' if result['profit_weight'] == 2 else '일반법인'}
║
║ [계산 과정]
║ 1. 3개년 가중평균 순손익: {result['weighted_profit']:,}백만원
║    (가중평균 전 값: {result['raw_weighted_profit']:,}백만원{' , 0 하한 적용됨' if result['floor_applied_to_profit'] else ''})
║ 2. 순손익가치 (÷환원율 {result['discount_rate']:.0%}): {result['income_value']:,}백만원
║
║ 3. 순자산가치: {result['asset_value']:,}백만원
║
║ 4. 가중평균 ({result['profit_weight']}:{result['asset_weight']}) 기본가치:
║    {result['base_value']:,}백만원{floor_note}
║
║ [최대주주 할증 판정]{basis_note}
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
    # 한국어 Windows 기본 콘솔(cp949)에서 summary의 박스 문자('╔' 등)가
    # UnicodeEncodeError를 일으키는 것을 방지하는 2중 방어.
    # 1) reconfigure로 stdout/stderr 자체를 UTF-8로 전환 시도 (미지원 환경 대비 try/except)
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

    # 2) reconfigure가 통하지 않는 환경(레거시 콘솔 등)에 대비해, 개별 print 호출도
    #    UnicodeEncodeError를 잡아 현재 stdout 인코딩 기준으로 대체 문자 처리 후 재출력
    def _safe_print(text=""):
        try:
            print(text)
        except UnicodeEncodeError:
            enc = getattr(sys.stdout, "encoding", None) or "utf-8"
            print(str(text).encode(enc, errors="replace").decode(enc, errors="replace"))

    _safe_print("=" * 60)
    _safe_print("상증세법 평가 테스트 (법령 교정판)")
    _safe_print("=" * 60)

    engine = InheritanceTaxLawEngine()

    _safe_print("\n[Case 1: 일반법인, 지배주주 80%, 비중소기업]")
    result1 = engine.generate_full_report(
        net_income_year1=13_000, net_income_year2=12_000, net_income_year3=10_000,
        net_assets=60_000, shares_outstanding=1_000_000, ownership_ratio=0.80,
        purpose='상속세 신고'
    )
    _safe_print(result1['summary'])
    assert result1['itl_value'] == 116_400.0, f"Case 1 검산 실패: {result1['itl_value']}"

    _safe_print("\n[Case 2: 80% 하한 발동 (3개년 적자, 순자산 큼, 비지배주주 30%)]")
    result2 = engine.generate_full_report(
        net_income_year1=-5_000, net_income_year2=-3_000, net_income_year3=-2_000,
        net_assets=100_000, shares_outstanding=500_000, ownership_ratio=0.30,
        purpose='증여세 신고'
    )
    _safe_print(result2['summary'])
    assert result2['itl_value'] == 80_000.0, f"Case 2 검산 실패: {result2['itl_value']}"

    _safe_print("\n[Case 3: 중소기업 특례 (Case 1과 동일 입력, 중소기업 → 할증 배제)]")
    result3 = engine.generate_full_report(
        net_income_year1=13_000, net_income_year2=12_000, net_income_year3=10_000,
        net_assets=60_000, shares_outstanding=1_000_000, ownership_ratio=0.80,
        is_sme=True, purpose='상속세 신고 (중소기업)'
    )
    _safe_print(result3['summary'])
    assert result3['itl_value'] == 97_000.0, f"Case 3 검산 실패: {result3['itl_value']}"

    _safe_print("\n[Case 4: 부동산과다보유법인 (Case 1과 동일 입력, 가중치 2:3)]")
    result4 = engine.generate_full_report(
        net_income_year1=13_000, net_income_year2=12_000, net_income_year3=10_000,
        net_assets=60_000, shares_outstanding=1_000_000, ownership_ratio=0.80,
        is_real_estate_heavy=True, purpose='상속세 신고 (부동산과다법인)'
    )
    _safe_print(result4['summary'])
    assert result4['itl_value'] == 101_600.0, f"Case 4 검산 실패: {result4['itl_value']}"

    _safe_print("\n[Case 5: 중견기업 특례 (Case 1과 동일 입력, 중견기업 → 할증 배제)]")
    result5 = engine.generate_full_report(
        net_income_year1=13_000, net_income_year2=12_000, net_income_year3=10_000,
        net_assets=60_000, shares_outstanding=1_000_000, ownership_ratio=0.80,
        is_medium_large=True, purpose='상속세 신고 (중견기업)'
    )
    _safe_print(result5['summary'])
    assert result5['itl_value'] == 97_000.0, f"Case 5 검산 실패: {result5['itl_value']}"

    _safe_print("\n[Case 6: 3년 연속 결손법인 자동 할증배제 (지배주주 60%, 3개년 전부 적자)]")
    result6 = engine.generate_full_report(
        net_income_year1=-1_000, net_income_year2=-2_000, net_income_year3=-1_500,
        net_assets=50_000, shares_outstanding=1_000_000, ownership_ratio=0.60,
        purpose='증여세 신고 (계속 결손법인)'
    )
    _safe_print(result6['summary'])
    assert result6['itl_value'] == 40_000.0, f"Case 6 검산 실패: {result6['itl_value']}"

    _safe_print("\n[Case 7: 최대주주 판정 결함 수정 검증 - 지분 40%(50% 이하)이나")
    _safe_print("         특수관계인 합산 시 최대주주 등(is_largest_shareholder=True), 비중소기업]")
    _safe_print("         Case 1과 동일 재무 -> 종전 '지분율 50% 초과' 기준이면 할증을")
    _safe_print("         놓쳐 97,000백만원으로 과소평가됐을 케이스. 수정 후 116,400 기대.")
    result7 = engine.generate_full_report(
        net_income_year1=13_000, net_income_year2=12_000, net_income_year3=10_000,
        net_assets=60_000, shares_outstanding=1_000_000, ownership_ratio=0.40,
        is_largest_shareholder=True, purpose='증여세 신고 (특수관계인 합산 최대주주, 지분 40%)'
    )
    _safe_print(result7['summary'])
    assert result7['itl_value'] == 116_400.0, f"Case 7 검산 실패: {result7['itl_value']}"
    assert result7['largest_shareholder_warning'] is None, "Case 7: is_largest_shareholder 명시 시 경고가 없어야 함"

    _safe_print("\n[Case 8: 하위호환 - is_largest_shareholder 미지정, 지분율 30%(50% 이하)]")
    _safe_print("         구형 JSON 호환: 지분율 기준 추정 -> 할증 미적용 + 경고 발생 확인")
    result8 = engine.generate_full_report(
        net_income_year1=13_000, net_income_year2=12_000, net_income_year3=10_000,
        net_assets=60_000, shares_outstanding=1_000_000, ownership_ratio=0.30,
        purpose='증여세 신고 (하위호환 - is_largest_shareholder 미지정)'
    )
    _safe_print(result8['summary'])
    assert result8['is_controlling'] is False, "Case 8: 지분 30% 추정이면 최대주주 아니어야 함"
    assert result8['largest_shareholder_warning'] is not None, "Case 8: 미지정 시 경고가 있어야 함"

    _safe_print("\n" + "=" * 60)
    _safe_print("전체 8케이스 검산 통과: 116,400 / 80,000 / 97,000 / 101,600 / 97,000 / 40,000 / 116,400 / (경고확인)")
    _safe_print("=" * 60)
