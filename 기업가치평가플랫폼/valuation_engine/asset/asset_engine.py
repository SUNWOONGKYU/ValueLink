"""
자산가치평가법 엔진 (Asset Valuation Engine / NAV)
Net Asset Value Approach

작성일: 2025-10-17
핵심 질문: "지금 자산을 모두 팔면 얼마를 받을 수 있을까?"
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AssetValuation:
    """자산 평가 결과"""
    asset_type: str
    book_value: float  # 장부가 (백만원)
    fair_value: float  # 공정가치 (백만원)
    adjustment: float  # 조정액 (백만원)
    adjustment_reason: str


class AssetValuationEngine:
    """자산가치평가법 엔진 (NAV)"""

    def __init__(self):
        self.asset_valuations: List[AssetValuation] = []
        self.liability_valuations: List[AssetValuation] = []

    def run_valuation(self, balance_sheet: Dict, fair_value_data: Optional[Dict] = None) -> Dict:
        """
        전체 자산가치평가 (NAV) 실행

        Args:
            balance_sheet: 재무상태표 데이터
            fair_value_data: 공정가치 조정 데이터 (감정평가서 등)

        Returns:
            {
                'total_assets_fv': 자산 공정가치 합계,
                'total_liabilities_fv': 부채 공정가치 합계,
                'nav': 순자산가치,
                'nav_per_share': 주당 순자산가치,
                'asset_details': [...],
                'liability_details': [...]
            }
        """
        fair_value_data = fair_value_data or {}

        # 1. 자산 공정가치 평가
        assets_fv = self._value_assets(balance_sheet, fair_value_data)

        # 2. 부채 공정가치 평가
        liabilities_fv = self._value_liabilities(balance_sheet, fair_value_data)

        # 3. NAV 계산
        nav = assets_fv['total'] - liabilities_fv['total']

        # 4. 주당 NAV
        shares = balance_sheet.get('shares_outstanding', 1_000_000)
        nav_per_share = (nav * 1_000_000) / shares  # 원

        return {
            'total_assets_book': balance_sheet.get('total_assets', 0),
            'total_assets_fv': round(assets_fv['total'], 0),
            'total_liabilities_book': balance_sheet.get('total_liabilities', 0),
            'total_liabilities_fv': round(liabilities_fv['total'], 0),
            'nav': round(nav, 0),
            'nav_per_share': round(nav_per_share, 0),
            'asset_details': assets_fv['details'],
            'liability_details': liabilities_fv['details'],
            'total_adjustments': round(assets_fv['total_adjustment'] - liabilities_fv['total_adjustment'], 0)
        }

    # ==================== 자산 평가 ====================

    def _value_assets(self, balance_sheet: Dict, fair_value_data: Dict) -> Dict:
        """자산 공정가치 평가"""
        details = []
        total_fv = 0
        total_adjustment = 0

        # 1. 유동자산
        current_assets = self._value_current_assets(balance_sheet, fair_value_data)
        details.extend(current_assets['items'])
        total_fv += current_assets['total']
        total_adjustment += current_assets['total_adjustment']

        # 2. 유형자산
        fixed_assets = self._value_fixed_assets(balance_sheet, fair_value_data)
        details.extend(fixed_assets['items'])
        total_fv += fixed_assets['total']
        total_adjustment += fixed_assets['total_adjustment']

        # 3. 무형자산
        intangible_assets = self._value_intangible_assets(balance_sheet, fair_value_data)
        details.extend(intangible_assets['items'])
        total_fv += intangible_assets['total']
        total_adjustment += intangible_assets['total_adjustment']

        # 4. 투자자산
        investment_assets = self._value_investment_assets(balance_sheet, fair_value_data)
        details.extend(investment_assets['items'])
        total_fv += investment_assets['total']
        total_adjustment += investment_assets['total_adjustment']

        return {
            'total': total_fv,
            'total_adjustment': total_adjustment,
            'details': details
        }

    def _value_current_assets(self, balance_sheet: Dict, fair_value_data: Dict) -> Dict:
        """유동자산 평가"""
        items = []
        total = 0
        total_adjustment = 0

        # 현금 및 현금성 자산 (100% 공정가치)
        cash = balance_sheet.get('cash', 0)
        items.append({
            'asset_type': '현금 및 현금성자산',
            'book_value': cash,
            'fair_value': cash,
            'adjustment': 0,
            'adjustment_reason': '현금은 공정가치 = 장부가'
        })
        total += cash

        # 단기금융상품 (100% 공정가치)
        short_term_investments = balance_sheet.get('short_term_investments', 0)
        items.append({
            'asset_type': '단기금융상품',
            'book_value': short_term_investments,
            'fair_value': short_term_investments,
            'adjustment': 0,
            'adjustment_reason': '단기금융상품 시가 = 장부가'
        })
        total += short_term_investments

        # 매출채권 (대손충당금 고려)
        accounts_receivable = balance_sheet.get('accounts_receivable', 0)
        bad_debt_rate = fair_value_data.get('bad_debt_rate', 0.02)  # 2% 기본
        bad_debt_adjustment = accounts_receivable * bad_debt_rate
        ar_fv = accounts_receivable - bad_debt_adjustment

        items.append({
            'asset_type': '매출채권',
            'book_value': accounts_receivable,
            'fair_value': ar_fv,
            'adjustment': -bad_debt_adjustment,
            'adjustment_reason': f'대손율 {bad_debt_rate:.1%} 반영'
        })
        total += ar_fv
        total_adjustment -= bad_debt_adjustment

        # 재고자산 (저가법 적용)
        inventory = balance_sheet.get('inventory', 0)
        inventory_markdown = fair_value_data.get('inventory_markdown', 0.05)  # 5% 평가손
        inventory_adjustment = inventory * inventory_markdown
        inventory_fv = inventory - inventory_adjustment

        items.append({
            'asset_type': '재고자산',
            'book_value': inventory,
            'fair_value': inventory_fv,
            'adjustment': -inventory_adjustment,
            'adjustment_reason': f'재고 평가손 {inventory_markdown:.1%} 반영'
        })
        total += inventory_fv
        total_adjustment -= inventory_adjustment

        return {
            'total': total,
            'total_adjustment': total_adjustment,
            'items': items
        }

    def _value_fixed_assets(self, balance_sheet: Dict, fair_value_data: Dict) -> Dict:
        """유형자산 평가 (토지, 건물, 설비)"""
        items = []
        total = 0
        total_adjustment = 0

        # 토지 (감정평가 또는 공시지가)
        land_book = balance_sheet.get('land', 0)
        if 'land_appraisal' in fair_value_data:
            land_fv = fair_value_data['land_appraisal']
            reason = '감정평가액 적용'
        else:
            # 공시지가 ÷ 현실화율 (70%)
            land_fv = land_book * 1.5  # 약 50% 상승 가정
            reason = '공시지가 기준 추정 (장부가 × 1.5)'

        land_adjustment = land_fv - land_book
        items.append({
            'asset_type': '토지',
            'book_value': land_book,
            'fair_value': land_fv,
            'adjustment': land_adjustment,
            'adjustment_reason': reason
        })
        total += land_fv
        total_adjustment += land_adjustment

        # 건물 (재조달원가 - 경제적 감가상각)
        building_book = balance_sheet.get('building', 0)
        if 'building_appraisal' in fair_value_data:
            building_fv = fair_value_data['building_appraisal']
            reason = '감정평가액 적용'
        else:
            # 간소화: 장부가 × 0.9 (10% 할인)
            building_fv = building_book * 0.9
            reason = '경제적 감가상각 10% 반영'

        building_adjustment = building_fv - building_book
        items.append({
            'asset_type': '건물',
            'book_value': building_book,
            'fair_value': building_fv,
            'adjustment': building_adjustment,
            'adjustment_reason': reason
        })
        total += building_fv
        total_adjustment += building_adjustment

        # 기계장치 (시장가치 또는 순실현가치)
        machinery_book = balance_sheet.get('machinery', 0)
        machinery_depreciation = fair_value_data.get('machinery_depreciation', 0.20)  # 20% 추가 감가
        machinery_adjustment = -machinery_book * machinery_depreciation
        machinery_fv = machinery_book + machinery_adjustment

        items.append({
            'asset_type': '기계장치',
            'book_value': machinery_book,
            'fair_value': machinery_fv,
            'adjustment': machinery_adjustment,
            'adjustment_reason': f'경제적 감가상각 {machinery_depreciation:.0%} 추가'
        })
        total += machinery_fv
        total_adjustment += machinery_adjustment

        return {
            'total': total,
            'total_adjustment': total_adjustment,
            'items': items
        }

    def _value_intangible_assets(self, balance_sheet: Dict, fair_value_data: Dict) -> Dict:
        """무형자산 평가 (영업권, 특허, 소프트웨어)"""
        items = []
        total = 0
        total_adjustment = 0

        # 영업권 (손상검사)
        goodwill_book = balance_sheet.get('goodwill', 0)
        goodwill_impairment = fair_value_data.get('goodwill_impairment', 0)
        goodwill_fv = goodwill_book - goodwill_impairment

        items.append({
            'asset_type': '영업권',
            'book_value': goodwill_book,
            'fair_value': goodwill_fv,
            'adjustment': -goodwill_impairment,
            'adjustment_reason': '손상검사 결과 반영'
        })
        total += goodwill_fv
        total_adjustment -= goodwill_impairment

        # 특허권 / 상표권
        patents_book = balance_sheet.get('patents', 0)
        if 'patents_valuation' in fair_value_data:
            patents_fv = fair_value_data['patents_valuation']
            reason = '별도 평가액 적용'
        else:
            # 잔여 유효기간 고려 (간소화: 80% 인정)
            patents_fv = patents_book * 0.8
            reason = '잔여 유효기간 고려 (80%)'

        patents_adjustment = patents_fv - patents_book
        items.append({
            'asset_type': '특허권/상표권',
            'book_value': patents_book,
            'fair_value': patents_fv,
            'adjustment': patents_adjustment,
            'adjustment_reason': reason
        })
        total += patents_fv
        total_adjustment += patents_adjustment

        return {
            'total': total,
            'total_adjustment': total_adjustment,
            'items': items
        }

    def _value_investment_assets(self, balance_sheet: Dict, fair_value_data: Dict) -> Dict:
        """투자자산 평가 (주식, 채권 등)"""
        items = []
        total = 0
        total_adjustment = 0

        # 상장주식 (시가)
        listed_stocks_book = balance_sheet.get('listed_stocks', 0)
        if 'listed_stocks_market_value' in fair_value_data:
            listed_stocks_fv = fair_value_data['listed_stocks_market_value']
            reason = '거래소 시가 적용'
        else:
            listed_stocks_fv = listed_stocks_book
            reason = '장부가 = 시가 가정'

        listed_adjustment = listed_stocks_fv - listed_stocks_book
        items.append({
            'asset_type': '상장주식',
            'book_value': listed_stocks_book,
            'fair_value': listed_stocks_fv,
            'adjustment': listed_adjustment,
            'adjustment_reason': reason
        })
        total += listed_stocks_fv
        total_adjustment += listed_adjustment

        # 비상장주식 (별도 평가 필요)
        unlisted_stocks_book = balance_sheet.get('unlisted_stocks', 0)
        if 'unlisted_stocks_valuation' in fair_value_data:
            unlisted_stocks_fv = fair_value_data['unlisted_stocks_valuation']
            reason = 'DCF 등 별도 평가'
        else:
            # 보수적: 50% 할인
            unlisted_stocks_fv = unlisted_stocks_book * 0.5
            reason = '유동성 할인 50% 적용'

        unlisted_adjustment = unlisted_stocks_fv - unlisted_stocks_book
        items.append({
            'asset_type': '비상장주식',
            'book_value': unlisted_stocks_book,
            'fair_value': unlisted_stocks_fv,
            'adjustment': unlisted_adjustment,
            'adjustment_reason': reason
        })
        total += unlisted_stocks_fv
        total_adjustment += unlisted_adjustment

        return {
            'total': total,
            'total_adjustment': total_adjustment,
            'items': items
        }

    # ==================== 부채 평가 ====================

    def _value_liabilities(self, balance_sheet: Dict, fair_value_data: Dict) -> Dict:
        """부채 공정가치 평가"""
        items = []
        total = 0
        total_adjustment = 0

        # 단기부채 (장부가 = 공정가치)
        current_liabilities = balance_sheet.get('current_liabilities', 0)
        items.append({
            'asset_type': '유동부채',
            'book_value': current_liabilities,
            'fair_value': current_liabilities,
            'adjustment': 0,
            'adjustment_reason': '단기부채는 장부가 = 공정가치'
        })
        total += current_liabilities

        # 장기차입금 (현재가치 할인)
        long_term_debt_book = balance_sheet.get('long_term_debt', 0)
        if 'market_interest_rate' in fair_value_data:
            # 시장이자율로 재할인
            book_rate = balance_sheet.get('debt_interest_rate', 0.05)
            market_rate = fair_value_data['market_interest_rate']

            if market_rate > book_rate:
                # 시장이자율 상승 → 부채 공정가치 하락
                adjustment_rate = (book_rate - market_rate) * 0.5  # 간소화
                long_term_debt_adjustment = long_term_debt_book * adjustment_rate
                reason = f'시장이자율 {market_rate:.1%} 반영'
            else:
                long_term_debt_adjustment = 0
                reason = '장부가 = 공정가치'
        else:
            long_term_debt_adjustment = 0
            reason = '장부가 = 공정가치 가정'

        long_term_debt_fv = long_term_debt_book + long_term_debt_adjustment
        items.append({
            'asset_type': '장기차입금',
            'book_value': long_term_debt_book,
            'fair_value': long_term_debt_fv,
            'adjustment': long_term_debt_adjustment,
            'adjustment_reason': reason
        })
        total += long_term_debt_fv
        total_adjustment += long_term_debt_adjustment

        # 우발부채 (추가 인식)
        contingent_liabilities = fair_value_data.get('contingent_liabilities', 0)
        if contingent_liabilities > 0:
            items.append({
                'asset_type': '우발부채',
                'book_value': 0,
                'fair_value': contingent_liabilities,
                'adjustment': contingent_liabilities,
                'adjustment_reason': '소송/보증 등 우발부채 추가 인식'
            })
            total += contingent_liabilities
            total_adjustment += contingent_liabilities

        return {
            'total': total,
            'total_adjustment': total_adjustment,
            'details': items
        }


# ==================== 테스트 코드 ====================

if __name__ == "__main__":
    # 테스트 데이터
    balance_sheet = {
        "shares_outstanding": 1_000_000,
        "total_assets": 80_000,
        "total_liabilities": 20_000,

        # 유동자산
        "cash": 5_000,
        "short_term_investments": 2_000,
        "accounts_receivable": 8_000,
        "inventory": 5_000,

        # 유형자산
        "land": 10_000,
        "building": 15_000,
        "machinery": 10_000,

        # 무형자산
        "goodwill": 5_000,
        "patents": 3_000,

        # 투자자산
        "listed_stocks": 10_000,
        "unlisted_stocks": 7_000,

        # 부채
        "current_liabilities": 10_000,
        "long_term_debt": 10_000,
    }

    fair_value_data = {
        "bad_debt_rate": 0.03,  # 3% 대손
        "inventory_markdown": 0.10,  # 10% 재고평가손
        "land_appraisal": 18_000,  # 토지 감정가 180억
        "building_appraisal": 14_000,  # 건물 감정가 140억
        "machinery_depreciation": 0.25,  # 기계 25% 추가 감가
        "goodwill_impairment": 2_000,  # 영업권 손상 20억
        "unlisted_stocks_valuation": 5_000,  # 비상장주식 평가 50억
        "contingent_liabilities": 1_000,  # 우발부채 10억
    }

    # 엔진 실행
    engine = AssetValuationEngine()
    results = engine.run_valuation(balance_sheet, fair_value_data)

    # 결과 출력
    print("=" * 60)
    print("자산가치평가 (NAV) 결과")
    print("=" * 60)

    print(f"\n[자산]")
    print(f"  장부가 합계: {results['total_assets_book']:,}백만원")
    print(f"  공정가치 합계: {results['total_assets_fv']:,}백만원")
    print(f"  조정액: {results['total_assets_fv'] - results['total_assets_book']:+,}백만원")

    print(f"\n[부채]")
    print(f"  장부가 합계: {results['total_liabilities_book']:,}백만원")
    print(f"  공정가치 합계: {results['total_liabilities_fv']:,}백만원")
    print(f"  조정액: {results['total_liabilities_fv'] - results['total_liabilities_book']:+,}백만원")

    print(f"\n[순자산가치 (NAV)]")
    print(f"  NAV: {results['nav']:,}백만원")
    print(f"  주당 NAV: {results['nav_per_share']:,}원")
    print(f"  총 조정액: {results['total_adjustments']:+,}백만원")

    print(f"\n[자산 상세]")
    for item in results['asset_details']:
        print(f"  • {item['asset_type']}: {item['book_value']:,} → {item['fair_value']:,} "
              f"({item['adjustment']:+,}) - {item['adjustment_reason']}")

    print(f"\n[부채 상세]")
    for item in results['liability_details']:
        print(f"  • {item['asset_type']}: {item['book_value']:,} → {item['fair_value']:,} "
              f"({item['adjustment']:+,}) - {item['adjustment_reason']}")

    print("\n" + "=" * 60)
