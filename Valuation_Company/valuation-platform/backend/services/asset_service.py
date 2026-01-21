"""
4. 자산가치평가법 서비스

기존 자산가치평가 엔진을 FastAPI 서비스로 래핑
"""

import sys
from typing import Dict, Any, Optional
from pathlib import Path

# 기존 평가 엔진 경로 추가
ENGINE_PATH = Path(__file__).parent.parent.parent.parent / "기업가치평가플랫폼" / "valuation_engine"
if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))


class AssetService:
    """자산가치평가법 서비스"""

    def __init__(self):
        """서비스 초기화"""
        try:
            # 기존 자산가치평가 엔진 import (있다면)
            # from asset.asset_engine import AssetEngine
            # self.engine = AssetEngine()
            self.engine = None
            self.engine_available = False
        except ImportError as e:
            print(f"⚠️ 자산가치평가 엔진 import 실패: {e}")
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
            'assets',  # 자산 목록
            'liabilities'  # 부채 목록
        ]

        for field in required_fields:
            if field not in input_data:
                return False, f"필수 필드 누락: {field}"

        # 자산/부채 데이터 검증
        if not isinstance(input_data['assets'], dict):
            return False, "자산 데이터는 딕셔너리 형태여야 합니다."

        if not isinstance(input_data['liabilities'], dict):
            return False, "부채 데이터는 딕셔너리 형태여야 합니다."

        return True, None

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        자산가치평가 계산 실행

        Args:
            input_data: 평가 입력 데이터
                {
                    'company_id': str,
                    'company_name': str,
                    'valuation_date': str,
                    'assets': {                       # 자산 항목별
                        'current_assets': float,
                        'tangible_assets': float,
                        'intangible_assets': float,
                        'investments': float
                    },
                    'liabilities': {                  # 부채 항목별
                        'current_liabilities': float,
                        'non_current_liabilities': float
                    },
                    'adjustment_method': str,         # 조정 방법 (book_value, market_value, liquidation)
                    'discount_rate': float            # 할인율 (청산가치일 경우)
                }

        Returns:
            Dict: 자산가치평가 결과
                {
                    'enterprise_value': float,      # 기업가치
                    'equity_value': float,          # 주주가치 (순자산가치)
                    'book_value': float,            # 장부가치
                    'adjusted_value': float,        # 조정 후 가치
                    'liquidation_value': float,     # 청산가치 (해당시)
                    'asset_breakdown': Dict,        # 자산 구성
                    'liability_breakdown': Dict     # 부채 구성
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
            # 기존 자산가치평가 엔진 실행
            result = self.engine.run_valuation(input_data)

            # 결과 포맷 변환 (FastAPI 응답용)
            return {
                'success': True,
                'enterprise_value': result['valuation_result']['enterprise_value'],
                'equity_value': result['valuation_result']['equity_value'],
                'book_value': result['book_value'],
                'adjusted_value': result['adjusted_value'],
                'liquidation_value': result.get('liquidation_value'),
                'asset_breakdown': result['assets'],
                'liability_breakdown': result['liabilities']
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"자산가치평가 계산 중 오류: {str(e)}",
                'enterprise_value': 0,
                'equity_value': 0
            }

    def _get_dummy_result(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        더미 결과 반환 (엔진 없을 경우)

        Args:
            input_data: 입력 데이터

        Returns:
            Dict: 더미 평가 결과
        """
        # 자산 합계
        assets = input_data.get('assets', {})
        total_assets = sum(assets.values())

        # 부채 합계
        liabilities = input_data.get('liabilities', {})
        total_liabilities = sum(liabilities.values())

        # 순자산가치 (NAV)
        nav = total_assets - total_liabilities

        # 조정 방법에 따른 가치
        adjustment_method = input_data.get('adjustment_method', 'book_value')
        if adjustment_method == 'liquidation':
            # 청산가치: 자산 × (1 - 할인율)
            discount_rate = input_data.get('discount_rate', 0.3)
            adjusted_value = total_assets * (1 - discount_rate) - total_liabilities
            liquidation_value = adjusted_value
        else:
            # 장부가치 또는 시장가치
            adjusted_value = nav
            liquidation_value = None

        return {
            'success': True,
            'enterprise_value': adjusted_value,
            'equity_value': adjusted_value,
            'book_value': nav,
            'adjusted_value': adjusted_value,
            'liquidation_value': liquidation_value,
            'asset_breakdown': {
                'current_assets': assets.get('current_assets', 2000000000),
                'tangible_assets': assets.get('tangible_assets', 3000000000),
                'intangible_assets': assets.get('intangible_assets', 500000000),
                'investments': assets.get('investments', 500000000),
                'total': total_assets or 6000000000
            },
            'liability_breakdown': {
                'current_liabilities': liabilities.get('current_liabilities', 800000000),
                'non_current_liabilities': liabilities.get('non_current_liabilities', 1200000000),
                'total': total_liabilities or 2000000000
            },
            'adjustment_method': adjustment_method,
            'formula': 'NAV = 총자산 - 총부채',
            'note': '자산가치평가 엔진 미연동 - 더미 데이터'
        }
