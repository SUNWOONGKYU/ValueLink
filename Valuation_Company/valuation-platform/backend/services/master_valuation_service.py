"""
통합 평가 서비스 (Master Valuation Service)

5가지 평가법을 통합하여 최종 의견을 도출
"""

from typing import Dict, Any, List
from .dcf_service import DCFService
from .relative_service import RelativeService
from .intrinsic_service import IntrinsicService
from .asset_service import AssetService
from .tax_service import TaxService


class MasterValuationService:
    """
    통합 평가 서비스

    5가지 평가법의 결과를 종합하여 최종 기업가치 의견 도출
    """

    def __init__(self):
        """서비스 초기화 - 5가지 평가 엔진 인스턴스 생성"""
        self.dcf_service = DCFService()
        self.relative_service = RelativeService()
        self.intrinsic_service = IntrinsicService()
        self.asset_service = AssetService()
        self.tax_service = TaxService()

    def run_integrated_valuation(
        self,
        methods: List[str],
        input_data: Dict[str, Any],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        통합 평가 실행

        Args:
            methods: 사용할 평가법 리스트
                ['dcf', 'relative', 'capital_market_law', 'asset', 'inheritance_tax_law']
            input_data: 각 평가법별 입력 데이터
                {
                    'dcf': {...},
                    'relative': {...},
                    'capital_market_law': {...},
                    'asset': {...},
                    'inheritance_tax_law': {...}
                }
            weights: 각 평가법의 가중치 (선택)
                {'dcf': 0.4, 'relative': 0.3, ...}

        Returns:
            Dict: 통합 평가 결과
                {
                    'method_results': List[Dict],   # 개별 평가법 결과
                    'final_value': float,           # 최종 기업가치
                    'value_range': Dict,            # 평가 범위
                    'weighted_average': float,      # 가중평균 가치
                    'recommendation': str           # 최종 의견
                }
        """
        results = {}

        # 1. 각 평가법 실행
        for method in methods:
            if method == 'dcf':
                results['dcf'] = self.dcf_service.calculate(input_data.get('dcf', {}))
            elif method == 'relative':
                results['relative'] = self.relative_service.calculate(input_data.get('relative', {}))
            elif method == 'capital_market_law':
                results['capital_market_law'] = self.intrinsic_service.calculate(input_data.get('capital_market_law', {}))
            elif method == 'asset':
                results['asset'] = self.asset_service.calculate(input_data.get('asset', {}))
            elif method == 'inheritance_tax_law':
                results['inheritance_tax_law'] = self.tax_service.calculate(input_data.get('inheritance_tax_law', {}))

        # 2. 가중치 설정 (없으면 균등 가중)
        if not weights:
            weights = {method: 1.0 / len(methods) for method in methods}

        # 3. 가중평균 계산
        weighted_sum = 0
        total_weight = 0
        values = []

        for method, result in results.items():
            if result.get('success'):
                equity_value = result.get('equity_value', 0)
                weight = weights.get(method, 1.0)
                weighted_sum += equity_value * weight
                total_weight += weight
                values.append(equity_value)

        weighted_average = weighted_sum / total_weight if total_weight > 0 else 0

        # 4. 평가 범위 계산
        if values:
            value_range = {
                'min': min(values),
                'median': sorted(values)[len(values) // 2],
                'max': max(values)
            }
        else:
            value_range = {'min': 0, 'median': 0, 'max': 0}

        # 5. 최종 의견 도출
        final_value = weighted_average
        recommendation = self._generate_recommendation(results, final_value, value_range)

        # 6. 결과 포맷팅
        method_results = [
            {
                'method': method,
                'method_name': self._get_method_name(method),
                'equity_value': result.get('equity_value', 0),
                'weight': weights.get(method, 1.0),
                'success': result.get('success', False),
                'note': result.get('note', '')
            }
            for method, result in results.items()
        ]

        return {
            'method_results': method_results,
            'final_value': final_value,
            'value_range': value_range,
            'weighted_average': weighted_average,
            'recommendation': recommendation,
            'valuation_summary': {
                'total_methods_used': len(methods),
                'successful_methods': sum(1 for r in results.values() if r.get('success')),
                'weights': weights
            }
        }

    def _get_method_name(self, method_code: str) -> str:
        """평가법 코드를 한글명으로 변환"""
        method_names = {
            'dcf': 'DCF평가법',
            'relative': '상대가치평가법',
            'capital_market_law': '본질가치평가법',
            'asset': '자산가치평가법',
            'inheritance_tax_law': '상증세법평가법'
        }
        return method_names.get(method_code, method_code)

    def _generate_recommendation(
        self,
        results: Dict[str, Any],
        final_value: float,
        value_range: Dict[str, float]
    ) -> str:
        """
        최종 의견 생성

        Args:
            results: 개별 평가법 결과
            final_value: 최종 가치
            value_range: 평가 범위

        Returns:
            str: 최종 의견
        """
        # 평가 범위 분석
        value_spread = value_range['max'] - value_range['min']
        spread_ratio = value_spread / final_value if final_value > 0 else 0

        if spread_ratio < 0.1:
            consistency = "평가법 간 결과가 매우 일관적입니다."
        elif spread_ratio < 0.3:
            consistency = "평가법 간 결과가 대체로 일관적입니다."
        else:
            consistency = "평가법 간 결과 편차가 다소 큽니다."

        # 최종 의견
        recommendation = f"""
종합 평가 의견:

1. 평가 결과
   - 최종 기업가치: {final_value:,.0f}원
   - 평가 범위: {value_range['min']:,.0f}원 ~ {value_range['max']:,.0f}원
   - 평가 중간값: {value_range['median']:,.0f}원

2. 평가 일관성
   - {consistency}
   - 평가 범위 편차율: {spread_ratio:.1%}

3. 평가 방법론
   - 사용된 평가법: {len(results)}개
   - 성공적으로 완료된 평가: {sum(1 for r in results.values() if r.get('success'))}개

4. 최종 의견
   본 평가는 {len(results)}가지 평가법을 종합하여 도출한 결과입니다.
   최종 기업가치는 {final_value:,.0f}원으로 평가되며,
   평가 범위는 {value_range['min']:,.0f}원에서 {value_range['max']:,.0f}원 사이입니다.
        """.strip()

        return recommendation

    def select_valuation_method(
        self,
        company_info: Dict[str, Any],
        purpose: str
    ) -> List[str]:
        """
        회사 정보와 평가 목적에 따라 적합한 평가법 선택

        Args:
            company_info: 회사 정보
                {
                    'company_type': str,  # 'listed' or 'unlisted'
                    'industry': str,
                    'profitability': str,  # 'high', 'medium', 'low', 'loss'
                    'asset_intensity': str  # 'high', 'medium', 'low'
                }
            purpose: 평가 목적
                'merger', 'acquisition', 'investment', 'tax', 'listing', etc.

        Returns:
            List[str]: 권장 평가법 리스트
        """
        recommended_methods = []

        # 1. DCF평가법 (미래 수익성이 좋고 예측 가능한 경우)
        if company_info.get('profitability') in ['high', 'medium']:
            recommended_methods.append('dcf')

        # 2. 상대가치평가법 (비교 가능한 유사 기업이 있는 경우)
        if company_info.get('company_type') == 'listed' or purpose in ['merger', 'acquisition']:
            recommended_methods.append('relative')

        # 3. 본질가치평가법 (자본시장법 - M&A, 유상증자 등)
        if purpose in ['merger', 'acquisition', 'capital_increase']:
            recommended_methods.append('capital_market_law')

        # 4. 자산가치평가법 (자산 집약적 산업, 부실 기업)
        if company_info.get('asset_intensity') == 'high' or company_info.get('profitability') == 'loss':
            recommended_methods.append('asset')

        # 5. 상증세법평가법 (상속/증여세 목적)
        if purpose in ['tax', 'inheritance', 'gift']:
            recommended_methods.append('inheritance_tax_law')

        # 최소 1개는 반환 (없으면 DCF)
        if not recommended_methods:
            recommended_methods.append('dcf')

        return recommended_methods
