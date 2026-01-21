"""
3. 본질가치평가법 서비스 (자본시장법)

기존 본질가치평가 엔진을 FastAPI 서비스로 래핑
"""

import sys
from typing import Dict, Any, Optional
from pathlib import Path

# 기존 평가 엔진 경로 추가
ENGINE_PATH = Path(__file__).parent.parent.parent.parent / "기업가치평가플랫폼" / "valuation_engine"
if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))


class IntrinsicService:
    """본질가치평가법 서비스 (자본시장법)"""

    def __init__(self):
        """서비스 초기화"""
        try:
            # 기존 본질가치평가 엔진 import (있다면)
            # from capital_market_law.cml_engine import CMLEngine
            # self.engine = CMLEngine()
            self.engine = None
            self.engine_available = False
        except ImportError as e:
            print(f"⚠️ 본질가치평가 엔진 import 실패: {e}")
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
            'transaction_type',  # 거래 유형 (M&A, 유상증자 등)
            'shares_outstanding',
            'net_asset_value',
            'earning_power_value'
        ]

        for field in required_fields:
            if field not in input_data:
                return False, f"필수 필드 누락: {field}"

        # 거래 유형 검증
        valid_transaction_types = ['merger', 'acquisition', 'capital_increase', 'stock_exchange']
        if input_data['transaction_type'] not in valid_transaction_types:
            return False, f"유효하지 않은 거래 유형: {input_data['transaction_type']}"

        return True, None

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        본질가치평가 계산 실행 (자본시장법 기준)

        Args:
            input_data: 평가 입력 데이터
                {
                    'company_id': str,
                    'company_name': str,
                    'valuation_date': str,
                    'transaction_type': str,          # 거래 유형
                    'shares_outstanding': int,        # 발행주식수
                    'net_asset_value': float,         # 순자산가치
                    'earning_power_value': float,     # 수익가치
                    'comparable_value': float,        # 비교가치 (선택)
                    'adjustment_factors': Dict        # 조정 요소
                }

        Returns:
            Dict: 본질가치평가 결과
                {
                    'enterprise_value': float,      # 기업가치
                    'equity_value': float,          # 주주가치
                    'value_per_share': float,       # 주당가치
                    'nav_weight': float,            # 순자산가치 가중치
                    'earning_weight': float,        # 수익가치 가중치
                    'weighted_value': float,        # 가중평균 가치
                    'final_value': float            # 최종 본질가치
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
            # 기존 본질가치평가 엔진 실행
            result = self.engine.run_valuation(input_data)

            # 결과 포맷 변환 (FastAPI 응답용)
            return {
                'success': True,
                'enterprise_value': result['valuation_result']['enterprise_value'],
                'equity_value': result['valuation_result']['equity_value'],
                'value_per_share': result['valuation_result']['value_per_share'],
                'nav_weight': result['weights']['nav'],
                'earning_weight': result['weights']['earning'],
                'weighted_value': result['weighted_value'],
                'final_value': result['final_intrinsic_value']
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"본질가치평가 계산 중 오류: {str(e)}",
                'enterprise_value': 0,
                'equity_value': 0
            }

    def _get_dummy_result(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        더미 결과 반환 (엔진 없을 경우)

        자본시장법 기준: 순자산가치(NAV)와 수익가치를 1:1.5 또는 2:3 가중평균

        Args:
            input_data: 입력 데이터

        Returns:
            Dict: 더미 평가 결과
        """
        # 자본시장법 기본 공식 (1:1.5 가중평균)
        nav = input_data.get('net_asset_value', 5000000000)
        earning = input_data.get('earning_power_value', 8000000000)

        # 1:1.5 가중평균
        weighted_value = (nav * 1 + earning * 1.5) / 2.5

        return {
            'success': True,
            'enterprise_value': weighted_value,
            'equity_value': weighted_value,
            'value_per_share': weighted_value / input_data.get('shares_outstanding', 100000),
            'nav_weight': 0.4,      # 1 / 2.5
            'earning_weight': 0.6,  # 1.5 / 2.5
            'weighted_value': weighted_value,
            'final_value': weighted_value,
            'components': {
                'net_asset_value': nav,
                'earning_power_value': earning,
                'comparable_value': input_data.get('comparable_value', 0)
            },
            'formula': '(NAV × 1 + 수익가치 × 1.5) ÷ 2.5',
            'note': '본질가치평가 엔진 미연동 - 더미 데이터 (자본시장법 1:1.5 공식)'
        }
