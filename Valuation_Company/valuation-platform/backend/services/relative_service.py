"""
2. 상대가치평가법 서비스

기존 상대가치평가 엔진을 FastAPI 서비스로 래핑
"""

import sys
from typing import Dict, Any, Optional
from pathlib import Path

# 기존 평가 엔진 경로 추가
ENGINE_PATH = Path(__file__).parent.parent.parent.parent / "기업가치평가플랫폼" / "valuation_engine"
if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))


class RelativeService:
    """상대가치평가법 서비스"""

    def __init__(self):
        """서비스 초기화"""
        try:
            # 기존 상대가치평가 엔진 import (있다면)
            # from relative.relative_engine import RelativeEngine
            # self.engine = RelativeEngine()
            self.engine = None
            self.engine_available = False
        except ImportError as e:
            print(f"⚠️ 상대가치평가 엔진 import 실패: {e}")
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
            'financial_data',
            'comparable_companies',
            'multiples'
        ]

        for field in required_fields:
            if field not in input_data:
                return False, f"필수 필드 누락: {field}"

        # 비교 대상 기업 검증
        if not isinstance(input_data['comparable_companies'], list) or len(input_data['comparable_companies']) < 3:
            return False, "비교 대상 기업은 최소 3개 이상 필요합니다."

        return True, None

    def calculate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        상대가치평가 계산 실행

        Args:
            input_data: 평가 입력 데이터
                {
                    'company_id': str,
                    'company_name': str,
                    'valuation_date': str,
                    'financial_data': Dict,           # 재무 데이터 (매출, 이익, 자산 등)
                    'comparable_companies': List[Dict], # 비교 대상 기업 리스트
                    'multiples': List[str]            # 사용할 배수 (PER, PBR, PSR 등)
                }

        Returns:
            Dict: 상대가치평가 결과
                {
                    'enterprise_value': float,      # 기업가치
                    'equity_value': float,          # 주주가치
                    'value_per_share': float,       # 주당가치
                    'multiples_analysis': Dict,     # 배수 분석
                    'comparable_analysis': List,    # 비교 기업 분석
                    'valuation_range': Dict         # 평가 범위
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
            # 기존 상대가치평가 엔진 실행
            result = self.engine.run_valuation(input_data)

            # 결과 포맷 변환 (FastAPI 응답용)
            return {
                'success': True,
                'enterprise_value': result['valuation_result']['enterprise_value'],
                'equity_value': result['valuation_result']['equity_value'],
                'value_per_share': result['valuation_result']['value_per_share'],
                'multiples_analysis': result['multiples_analysis'],
                'comparable_analysis': result['comparable_companies'],
                'valuation_range': result['valuation_range']
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"상대가치평가 계산 중 오류: {str(e)}",
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
        return {
            'success': True,
            'enterprise_value': 9000000000,
            'equity_value': 6500000000,
            'value_per_share': 65000,
            'multiples_analysis': {
                'PER': {
                    'company_per': 12.5,
                    'industry_average_per': 15.0,
                    'discount': -16.7  # %
                },
                'PBR': {
                    'company_pbr': 2.0,
                    'industry_average_pbr': 2.5,
                    'discount': -20.0  # %
                },
                'PSR': {
                    'company_psr': 1.5,
                    'industry_average_psr': 1.8,
                    'discount': -16.7  # %
                }
            },
            'comparable_analysis': [
                {
                    'company_name': '비교기업A',
                    'revenue': 1500000000,
                    'per': 14.5,
                    'pbr': 2.3,
                    'market_cap': 21750000000
                },
                {
                    'company_name': '비교기업B',
                    'revenue': 1800000000,
                    'per': 15.5,
                    'pbr': 2.7,
                    'market_cap': 27900000000
                }
            ],
            'valuation_range': {
                'min': 6000000000,
                'median': 6500000000,
                'max': 7000000000
            },
            'note': '상대가치평가 엔진 미연동 - 더미 데이터'
        }
