"""
5. 상증세법평가법 서비스

기존 상증세법평가 엔진을 FastAPI 서비스로 래핑
"""

import sys
from typing import Dict, Any, Optional
from pathlib import Path

# 기존 평가 엔진 경로 추가
ENGINE_PATH = Path(__file__).parent.parent.parent.parent / "기업가치평가플랫폼" / "valuation_engine"
if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))


class TaxService:
    """상증세법평가법 서비스"""

    def __init__(self):
        """서비스 초기화"""
        try:
            # 기존 상증세법평가 엔진 import (있다면)
            # from inheritance_tax_law.itl_engine import ITLEngine
            # self.engine = ITLEngine()
            self.engine = None
            self.engine_available = False
        except ImportError as e:
            print(f"⚠️ 상증세법평가 엔진 import 실패: {e}")
            self.engine = None
            self.engine_available = False

    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        입력 데이터 검증

        Args:
            input_data: 평가 입력 데이터

        Returns:
            (유효 여부, 에러 메시지)
        """
        required_fields = [
            'company_id',
            'company_name',
            'valuation_date',
            'company_type',  # 상장/비상장
            'net_asset_value',
            'earnings',  # 최근 3년 순손익
            'weighted_average_per'  # 가중평균 PER
        ]

        for field in required_fields:
            if field not in input_data:
                return False, f"필수 필드 누락: {field}"

        # 회사 유형 검증
        if input_data['company_type'] not in ['listed', 'unlisted']:
            return False, "회사 유형은 'listed' 또는 'unlisted'여야 합니다."

        # 순손익 데이터 검증
        if not isinstance(input_data['earnings'], list) or len(input_data['earnings']) < 3:
            return False, "최근 3년 순손익 데이터가 필요합니다."

        return True, None

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        상증세법평가 계산 실행

        Args:
            input_data: 평가 입력 데이터
                {
                    'company_id': str,
                    'company_name': str,
                    'valuation_date': str,
                    'company_type': str,              # 'listed' or 'unlisted'
                    'net_asset_value': float,         # 순자산가치
                    'earnings': List[float],          # 최근 3년 순손익
                    'weighted_average_per': float,    # 가중평균 PER (동종업종)
                    'discount_rate': float,           # 할인율 (비상장 기업)
                    'control_premium': float          # 지배권 프리미엄 (선택)
                }

        Returns:
            Dict: 상증세법평가 결과
                {
                    'enterprise_value': float,      # 기업가치
                    'equity_value': float,          # 주주가치
                    'value_per_share': float,       # 주당가치
                    'nav_component': float,         # 순자산가치 부분
                    'earning_component': float,     # 수익가치 부분
                    'weighted_value': float,        # 가중평균 가치
                    'discount_applied': float,      # 할인 적용 (비상장)
                    'final_value': float            # 최종 평가액
                }
        """
        # 입력 검증
        is_valid, error_msg = self.validate_inputs(input_data)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg,
                'enterprise_value': 0,
                'equity_value': 0
            }

        # 엔진 사용 가능 여부 확인
        if not self.engine_available:
            # 엔진 없을 경우 더미 데이터 반환
            return self._get_dummy_result(input_data)

        try:
            # 기존 상증세법평가 엔진 실행
            result = self.engine.run_valuation(input_data)

            # 결과 포맷 변환 (FastAPI 응답용)
            return {
                'success': True,
                'enterprise_value': result['valuation_result']['enterprise_value'],
                'equity_value': result['valuation_result']['equity_value'],
                'value_per_share': result['valuation_result']['value_per_share'],
                'nav_component': result['components']['nav'],
                'earning_component': result['components']['earning'],
                'weighted_value': result['weighted_value'],
                'discount_applied': result.get('discount_applied', 0),
                'final_value': result['final_value']
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"상증세법평가 계산 중 오류: {str(e)}",
                'enterprise_value': 0,
                'equity_value': 0
            }

    def _get_dummy_result(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        더미 결과 반환 (엔진 없을 경우)

        상증세법 기본 공식:
        - 상장법인: (NAV × 3 + 수익가치 × 2) ÷ 5
        - 비상장법인: [(NAV × 3 + 수익가치 × 2) ÷ 5] × (1 - 할인율)

        Args:
            input_data: 입력 데이터

        Returns:
            Dict: 더미 평가 결과
        """
        # 순자산가치
        nav = input_data.get('net_asset_value', 5000000000)

        # 수익가치 계산 (최근 3년 평균 순손익 × PER)
        earnings = input_data.get('earnings', [800000000, 900000000, 1000000000])
        avg_earning = sum(earnings) / len(earnings)
        per = input_data.get('weighted_average_per', 10.0)
        earning_value = avg_earning * per

        # 가중평균 (3:2)
        weighted_value = (nav * 3 + earning_value * 2) / 5

        # 비상장 할인 적용
        company_type = input_data.get('company_type', 'unlisted')
        if company_type == 'unlisted':
            discount_rate = input_data.get('discount_rate', 0.2)  # 기본 20%
            final_value = weighted_value * (1 - discount_rate)
            discount_applied = weighted_value * discount_rate
        else:
            final_value = weighted_value
            discount_applied = 0

        return {
            'success': True,
            'enterprise_value': final_value,
            'equity_value': final_value,
            'value_per_share': final_value / input_data.get('shares_outstanding', 100000),
            'nav_component': nav,
            'earning_component': earning_value,
            'weighted_value': weighted_value,
            'discount_applied': discount_applied,
            'final_value': final_value,
            'calculation_details': {
                'nav': nav,
                'avg_earning': avg_earning,
                'per': per,
                'earning_value': earning_value,
                'formula': '(NAV × 3 + 수익가치 × 2) ÷ 5',
                'discount_rate': input_data.get('discount_rate', 0.2) if company_type == 'unlisted' else 0
            },
            'company_type': company_type,
            'note': '상증세법평가 엔진 미연동 - 더미 데이터'
        }
