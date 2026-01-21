"""
1. DCF평가법 서비스

기존 DCF 엔진을 FastAPI 서비스로 래핑
"""

import sys
import os
from typing import Dict, Any, Optional
from pathlib import Path

# 기존 평가 엔진 경로 추가
ENGINE_PATH = Path(__file__).parent.parent.parent.parent / "기업가치평가플랫폼" / "valuation_engine"
if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))


class DCFService:
    """DCF평가법 서비스"""

    def __init__(self):
        """서비스 초기화"""
        try:
            # 기존 DCF 엔진 import
            from dcf.dcf_engine import DCFEngine
            self.engine = DCFEngine()
            self.engine_available = True
        except ImportError as e:
            print(f"⚠️ DCF 엔진 import 실패: {e}")
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
            'historical_financials',
            'assumptions',
            'wacc_inputs',
            'adjustments'
        ]

        for field in required_fields:
            if field not in input_data:
                return False, f"필수 필드 누락: {field}"

        # 과거 재무제표 검증
        if not isinstance(input_data['historical_financials'], list) or len(input_data['historical_financials']) < 3:
            return False, "과거 재무제표는 최소 3년 이상 필요합니다."

        return True, None

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        DCF 평가 계산 실행

        Args:
            input_data: 평가 입력 데이터
                {
                    'company_id': str,
                    'company_name': str,
                    'valuation_date': str,
                    'historical_financials': List[Dict],  # 과거 3~5년 재무제표
                    'assumptions': Dict,                   # 예측 가정
                    'wacc_inputs': Dict,                   # WACC 계산 입력
                    'adjustments': Dict                    # 순차입금, 비영업자산 등
                }

        Returns:
            Dict: DCF 평가 결과
                {
                    'enterprise_value': float,      # 기업가치
                    'equity_value': float,          # 주주가치
                    'value_per_share': float,       # 주당가치
                    'wacc': float,                  # WACC
                    'terminal_growth': float,       # 영구성장률
                    'pv_fcf': float,               # FCF 현가
                    'pv_terminal_value': float,    # 영구가치 현가
                    'projections': List[Dict],     # 예측 재무제표
                    'sensitivity_analysis': Dict   # 민감도 분석
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
            # 기존 DCF 엔진 실행
            result = self.engine.run_valuation(input_data)

            # 결과 포맷 변환 (FastAPI 응답용)
            return {
                'success': True,
                'enterprise_value': result['valuation_result']['enterprise_value'],
                'equity_value': result['valuation_result']['equity_value'],
                'value_per_share': result['valuation_result']['value_per_share'],
                'wacc': result['wacc']['wacc'],
                'terminal_growth': input_data['assumptions']['terminal_growth'],
                'pv_fcf': result['discounted_fcf']['total_pv_fcf'],
                'pv_terminal_value': result['terminal_value']['pv_terminal_value'],
                'projections': result['projections'],
                'sensitivity_analysis': self._run_sensitivity_analysis(input_data, result)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"DCF 계산 중 오류: {str(e)}",
                'enterprise_value': 0,
                'equity_value': 0
            }

    def _run_sensitivity_analysis(self, input_data: Dict[str, Any], base_result: Dict) -> Dict[str, Any]:
        """
        민감도 분석 실행

        Args:
            input_data: 원본 입력 데이터
            base_result: 기본 평가 결과

        Returns:
            Dict: 민감도 분석 결과
        """
        # TODO: 실제 민감도 분석 구현
        return {
            'wacc_sensitivity': {
                '7%': base_result['valuation_result']['equity_value'] * 1.1,
                '8%': base_result['valuation_result']['equity_value'],
                '9%': base_result['valuation_result']['equity_value'] * 0.9
            },
            'growth_sensitivity': {
                '1%': base_result['valuation_result']['equity_value'] * 0.95,
                '2%': base_result['valuation_result']['equity_value'],
                '3%': base_result['valuation_result']['equity_value'] * 1.05
            }
        }

    def _get_dummy_result(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        더미 결과 반환 (엔진 없을 경우)

        Args:
            input_data: 입력 데이터

        Returns:
            Dict: 더미 평가 결과
        """
        return {
            'success': True,
            'enterprise_value': 10000000000,
            'equity_value': 7000000000,
            'value_per_share': 70000,
            'wacc': 0.08,
            'terminal_growth': 0.02,
            'pv_fcf': 4000000000,
            'pv_terminal_value': 6000000000,
            'projections': [],
            'sensitivity_analysis': {},
            'note': 'DCF 엔진 미연동 - 더미 데이터'
        }
