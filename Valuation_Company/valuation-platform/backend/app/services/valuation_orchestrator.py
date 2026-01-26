"""
Valuation Orchestrator
평가 프로세스 전체를 관리하는 오케스트레이터

@task Valuation Orchestrator
@description 5개 평가 엔진 통합, 워크플로 관리, 진행률 추적, 자동 단계 전환
"""

from typing import Dict, Optional, Any
from datetime import datetime
import asyncio

from app.db.supabase_client import supabase_client
from app.services.valuation_engine.dcf.dcf_engine import DCFEngine
from app.services.valuation_engine.relative.relative_engine import RelativeValuationEngine
from app.services.valuation_engine.intrinsic.intrinsic_value_engine import CapitalMarketLawEngine
from app.services.valuation_engine.asset.asset_engine import AssetValuationEngine
from app.services.valuation_engine.tax.tax_law_engine import InheritanceTaxLawEngine


class ValuationOrchestrator:
    """
    평가 프로세스 오케스트레이터

    목적:
    - 5개 평가 엔진(DCF, Relative, Intrinsic, Asset, Tax) 통합
    - 평가 워크플로 관리 (Step 5~14)
    - 진행률 추적 및 자동 단계 전환
    - DB 상태 업데이트
    """

    # 단계별 진행률 매핑
    STEP_PROGRESS = {
        1: 0,    # Home 프로세스
        2: 0,    # Home 프로세스
        3: 0,    # Home 프로세스
        4: 0,    # 평가 방법 선택
        5: 10,   # 데이터 수집
        6: 30,   # 평가 실행
        7: 50,   # 회계사 검토 제출
        8: 60,   # 초안 보고서 생성
        9: 70,   # 초안 검토
        10: 75,  # 피드백 반영
        11: 80,  # 최종 보고서 생성
        12: 90,  # 최종 승인
        13: 95,  # 보고서 전달
        14: 100  # 완료
    }

    def __init__(self, project_id: str, method: str):
        """
        Args:
            project_id: 프로젝트 ID
            method: 평가 방법 ('dcf', 'relative', 'intrinsic', 'asset', 'inheritance_tax')
        """
        self.project_id = project_id
        self.method = method
        self.engine = self._load_engine()
        self.supabase = supabase_client

    def _load_engine(self):
        """평가 방법에 따라 적절한 엔진 로드"""
        engines = {
            'dcf': DCFEngine(),
            'relative': RelativeValuationEngine(),
            'intrinsic': CapitalMarketLawEngine(),
            'asset': AssetValuationEngine(),
            'inheritance_tax': InheritanceTaxLawEngine()
        }

        engine = engines.get(self.method)
        if not engine:
            raise ValueError(f"Unknown valuation method: {self.method}")

        return engine

    async def start_valuation(self) -> Dict:
        """
        평가 프로세스 시작 (Step 5)

        Returns:
            {
                'project_id': str,
                'method': str,
                'status': 'in_progress',
                'step': 5,
                'progress': 10
            }
        """
        # 1. 상태를 'in_progress'로 업데이트
        await self.update_status('in_progress', 5)

        # 2. 초기 상태 반환
        return {
            'project_id': self.project_id,
            'method': self.method,
            'status': 'in_progress',
            'step': 5,
            'progress': self.STEP_PROGRESS[5],
            'message': '평가를 시작합니다. 데이터 수집 중...'
        }

    async def collect_data(self, on_progress=None) -> Dict:
        """
        Step 5: 데이터 수집 시뮬레이션

        5개 데이터 수집 작업을 시뮬레이션하고 진행률 업데이트
        완료 시 자동으로 Step 6으로 전환

        Args:
            on_progress: 진행률 콜백 함수 (optional)

        Returns:
            {
                'completed': True,
                'data': {...},
                'next_step': 6
            }
        """
        data_tasks = [
            {'name': '재무제표 수집', 'duration': 1},
            {'name': '시장 데이터 수집', 'duration': 1},
            {'name': '비교기업 데이터 수집', 'duration': 1},
            {'name': '자산 정보 수집', 'duration': 1},
            {'name': '업종 벤치마크 수집', 'duration': 1}
        ]

        total_tasks = len(data_tasks)
        collected_data = {}

        for i, task in enumerate(data_tasks):
            # 진행률 계산 (0 -> 100)
            progress = int((i + 1) / total_tasks * 100)

            # 콜백 호출
            if on_progress:
                await on_progress({
                    'task': task['name'],
                    'progress': progress,
                    'status': 'collecting'
                })

            # 작업 시뮬레이션 (실제 환경에서는 실제 데이터 수집)
            await asyncio.sleep(task['duration'])

            # 데이터 저장 (예시)
            collected_data[task['name']] = {
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat()
            }

        # Step 6으로 자동 전환
        await self.update_status('in_progress', 6)

        return {
            'completed': True,
            'data': collected_data,
            'next_step': 6,
            'message': '데이터 수집이 완료되었습니다. 평가를 실행합니다.'
        }

    async def run_evaluation(self, inputs: Dict) -> Dict:
        """
        Step 6: 평가 엔진 실행

        선택된 평가 방법에 따라 적절한 엔진의 evaluate() 메서드 호출
        엔진의 단계별 진행률 추적
        결과를 DB에 저장
        완료 시 자동으로 Step 7로 전환

        Args:
            inputs: 평가 엔진 입력 데이터

        Returns:
            {
                'valuation_result': {...},
                'next_step': 7
            }
        """
        # 1. 평가 실행
        if self.method == 'dcf':
            result = self.engine.run_valuation(inputs)
        elif self.method == 'relative':
            result = self.engine.run_valuation(
                company_data=inputs.get('company_data'),
                comparable_companies=inputs.get('comparable_companies'),
                industry_benchmarks=inputs.get('industry_benchmarks')
            )
        elif self.method == 'intrinsic':
            result = self.engine.run_valuation(
                asset_value=inputs.get('asset_value'),
                income_value=inputs.get('income_value'),
                purpose=inputs.get('purpose', '합병')
            )
        elif self.method == 'asset':
            result = self.engine.run_valuation(
                balance_sheet=inputs.get('balance_sheet'),
                fair_value_data=inputs.get('fair_value_data')
            )
        elif self.method == 'inheritance_tax':
            result = self.engine.run_valuation(
                net_income_3yr=inputs.get('net_income_3yr'),
                net_assets=inputs.get('net_assets'),
                controlling_premium=inputs.get('controlling_premium', False),
                minority_discount=inputs.get('minority_discount', 0.0),
                marketability_discount=inputs.get('marketability_discount', 0.0)
            )
        else:
            raise ValueError(f"Unsupported method: {self.method}")

        # 2. 결과를 DB에 저장
        await self._save_valuation_result(result)

        # 3. Step 7로 자동 전환
        await self.update_status('in_progress', 7)

        return {
            'valuation_result': result,
            'next_step': 7,
            'message': '평가가 완료되었습니다. 회계사 검토를 요청합니다.'
        }

    async def submit_for_review(self) -> Dict:
        """
        Step 7: 회계사 검토 제출

        평가 결과를 회계사에게 제출
        회계사 알림 전송 (미래 기능)
        수동 승인 대기 상태로 전환

        Returns:
            {
                'submitted': True,
                'status': 'pending_review',
                'message': '회계사 검토 대기 중'
            }
        """
        # 1. 상태 업데이트
        await self.update_status('pending_review', 7)

        # 2. 회계사 알림 (미래 기능)
        # await self._notify_accountant()

        return {
            'submitted': True,
            'status': 'pending_review',
            'step': 7,
            'message': '회계사 검토가 요청되었습니다. 승인을 기다립니다.'
        }

    async def generate_draft(self, valuation_result: Dict) -> Dict:
        """
        Step 8: 초안 보고서 생성

        평가 결과를 기반으로 초안 PDF 보고서 생성
        진행률 추적
        Supabase Storage에 저장
        완료 시 자동으로 Step 9로 전환

        Args:
            valuation_result: 평가 결과 데이터

        Returns:
            {
                'draft_url': str,
                'next_step': 9
            }
        """
        # 1. 보고서 생성 (ReportGenerator 호출 - 미래 구현)
        # report_generator = ReportGenerator(self.method, valuation_result)
        # pdf_bytes = await report_generator.generate()

        # 시뮬레이션
        await asyncio.sleep(2)
        draft_url = f"https://storage.supabase.co/valuation-reports/{self.project_id}_draft.pdf"

        # 2. Supabase Storage에 저장 (미래 구현)
        # await self._save_to_storage(pdf_bytes, f"{self.project_id}_draft.pdf")

        # 3. Step 9로 자동 전환
        await self.update_status('in_progress', 9)

        return {
            'draft_url': draft_url,
            'next_step': 9,
            'message': '초안 보고서가 생성되었습니다.'
        }

    async def get_progress(self) -> Dict:
        """
        현재 진행률 조회

        DB에서 현재 step과 status 조회
        진행률 퍼센트 계산

        Returns:
            {
                'project_id': str,
                'method': str,
                'status': str,
                'step': int,
                'progress': int (0-100),
                'step_name': str
            }
        """
        # DB에서 프로젝트 조회 (테이블명은 실제 스키마에 따라 조정)
        # 여기서는 'valuation_projects' 테이블 가정
        result = await self.supabase.select(
            'valuation_projects',
            filters={'project_id': self.project_id}
        )

        if not result:
            return {
                'project_id': self.project_id,
                'error': 'Project not found'
            }

        project = result[0]
        current_step = project.get('current_step', 4)
        status = project.get('status', 'not_started')

        # 단계명 매핑
        step_names = {
            4: '평가 방법 선택',
            5: '데이터 수집',
            6: '평가 실행',
            7: '회계사 검토 제출',
            8: '초안 보고서 생성',
            9: '초안 검토',
            10: '피드백 반영',
            11: '최종 보고서 생성',
            12: '최종 승인',
            13: '보고서 전달',
            14: '완료'
        }

        return {
            'project_id': self.project_id,
            'method': self.method,
            'status': status,
            'step': current_step,
            'progress': self.STEP_PROGRESS.get(current_step, 0),
            'step_name': step_names.get(current_step, '알 수 없음')
        }

    async def advance_step(self) -> Dict:
        """
        다음 단계로 전환 (테스트용)

        현재 step을 1 증가시키고 DB 업데이트

        Returns:
            {
                'step': int,
                'progress': int,
                'message': str
            }
        """
        # 현재 진행률 조회
        current = await self.get_progress()
        current_step = current.get('step', 4)

        # 다음 단계
        next_step = current_step + 1
        if next_step > 14:
            return {
                'error': 'Already at final step',
                'step': 14,
                'progress': 100
            }

        # 업데이트
        await self.update_status('in_progress', next_step)

        return {
            'step': next_step,
            'progress': self.STEP_PROGRESS.get(next_step, 0),
            'message': f'Step {next_step}로 이동했습니다.'
        }

    async def update_status(self, status: str, step: int):
        """
        평가 방법의 상태 및 단계 업데이트

        Args:
            status: 'not_started', 'in_progress', 'pending_review', 'completed', 'failed'
            step: 현재 단계 (4~14)
        """
        # valuation_projects 테이블 업데이트 (실제 스키마에 따라 조정)
        update_data = {
            'status': status,
            'current_step': step,
            'progress': self.STEP_PROGRESS.get(step, 0),
            'updated_at': datetime.utcnow().isoformat()
        }

        await self.supabase.update(
            'valuation_projects',
            update_data,
            filters={'project_id': self.project_id}
        )

    async def _save_valuation_result(self, result: Dict):
        """평가 결과를 DB에 저장"""
        result_data = {
            'project_id': self.project_id,
            'method': self.method,
            'result': result,
            'created_at': datetime.utcnow().isoformat()
        }

        await self.supabase.insert('valuation_results', result_data)


# 테스트 코드
if __name__ == "__main__":
    import asyncio

    async def test_orchestrator():
        print("=" * 60)
        print("Valuation Orchestrator 테스트")
        print("=" * 60)

        # 1. 오케스트레이터 초기화
        orchestrator = ValuationOrchestrator(
            project_id="TEST_PROJECT_001",
            method="dcf"
        )

        print(f"\n[초기화 완료]")
        print(f"  프로젝트 ID: {orchestrator.project_id}")
        print(f"  평가 방법: {orchestrator.method}")
        print(f"  엔진: {type(orchestrator.engine).__name__}")

        # 2. 평가 시작
        print(f"\n[Step 5: 평가 시작]")
        start_result = await orchestrator.start_valuation()
        print(f"  상태: {start_result['status']}")
        print(f"  단계: {start_result['step']}")
        print(f"  진행률: {start_result['progress']}%")

        # 3. 데이터 수집
        print(f"\n[Step 5: 데이터 수집]")

        async def progress_callback(info):
            print(f"  → {info['task']}: {info['progress']}%")

        collect_result = await orchestrator.collect_data(on_progress=progress_callback)
        print(f"  완료: {collect_result['completed']}")
        print(f"  다음 단계: {collect_result['next_step']}")

        # 4. 진행률 조회
        print(f"\n[진행률 조회]")
        progress = await orchestrator.get_progress()
        print(f"  단계: {progress['step']} - {progress['step_name']}")
        print(f"  진행률: {progress['progress']}%")

        print("\n" + "=" * 60)

    # asyncio.run(test_orchestrator())
    print("테스트는 실제 DB 연결이 필요하므로 주석 처리되었습니다.")
