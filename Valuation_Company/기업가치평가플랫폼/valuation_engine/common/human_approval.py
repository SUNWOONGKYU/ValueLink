"""
인간 승인 레이어 (Human Approval Layer)

목적: AI 자동 계산과 인간 전문가 판단을 분리
- AI가 3가지 시나리오 제시
- 인간 평가자가 선택 또는 직접 입력
- 22개 판단 포인트 관리

작성일: 2025-10-17
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ApprovalStatus(Enum):
    """승인 상태"""
    PENDING = "대기"  # AI 시나리오 제시, 평가자 응답 대기
    APPROVED = "승인"  # 평가자가 선택/승인
    REJECTED = "거부"  # 평가자가 재계산 요청
    CUSTOM = "직접입력"  # 평가자가 직접 값 입력


@dataclass
class Scenario:
    """AI 제시 시나리오"""
    label: str  # "낙관적", "중립적", "보수적"
    value: Any  # 실제 값
    description: str  # 설명
    is_recommended: bool = False  # 추천 여부


@dataclass
class ApprovalPoint:
    """인간 승인 필요 지점"""
    id: str  # 예: "DCF_GROWTH_RATE"
    category: str  # "DCF", "상대가치", "NAV" 등
    name: str  # "매출 성장률"
    importance: int  # 1~3 (⭐ 수)
    question: str  # 평가자에게 보여줄 질문
    scenarios: List[Scenario]  # AI가 제시하는 3가지 시나리오
    context: Dict  # 추가 정보 (과거 데이터, 업종 평균 등)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_value: Any = None  # 평가자가 선택/입력한 최종 값
    approval_reason: str = ""  # 승인 사유


class HumanApprovalManager:
    """인간 승인 관리자 - 22개 판단 포인트 관리"""

    def __init__(self):
        self.approval_points: Dict[str, ApprovalPoint] = {}
        self.approval_order: List[str] = []  # 승인 순서

    # ==================== DCF 판단 포인트 ====================

    def request_growth_rate_approval(self, business_plan: Dict, historical_data: Dict,
                                     industry_avg: float) -> ApprovalPoint:
        """
        DCF #1: 매출 성장률 승인 요청 ⭐⭐⭐

        Args:
            business_plan: 사업계획서 성장률 {'2024': 0.40, '2025': 0.35, ...}
            historical_data: 과거 실적 성장률 {'avg_3yr': 0.45}
            industry_avg: 업종 평균 성장률 0.10

        Returns:
            ApprovalPoint
        """
        bp_avg = sum(business_plan.values()) / len(business_plan)

        scenarios = [
            Scenario(
                label="낙관적",
                value=business_plan,
                description=f"사업계획서 그대로 (연평균 {bp_avg:.0%})",
                is_recommended=False
            ),
            Scenario(
                label="중립적",
                value={(year: (bp_rate + industry_avg) / 2)
                       for year, bp_rate in business_plan.items()},
                description=f"사업계획서와 업종 평균 절충 (연평균 {(bp_avg + industry_avg)/2:.0%})",
                is_recommended=True  # 추천
            ),
            Scenario(
                label="보수적",
                value={(year: industry_avg) for year in business_plan.keys()},
                description=f"업종 평균 수준 (연평균 {industry_avg:.0%})",
                is_recommended=False
            )
        ]

        point = ApprovalPoint(
            id="DCF_GROWTH_RATE",
            category="DCF",
            name="매출 성장률",
            importance=3,  # ⭐⭐⭐
            question="미래 매출 성장률 시나리오를 선택하시겠습니까?",
            scenarios=scenarios,
            context={
                'business_plan': business_plan,
                'historical_growth': historical_data,
                'industry_avg': industry_avg,
                'warning': "사업계획서는 일반적으로 낙관적입니다. 업종 평균과 비교 검토하세요."
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    def request_wacc_approval(self, auto_calculated_wacc: float,
                             beta: float, rf: float, mrp: float) -> ApprovalPoint:
        """
        DCF #2: WACC 승인 요청 ⭐⭐⭐

        Args:
            auto_calculated_wacc: AI 자동 계산 WACC
            beta: 업종 베타
            rf: 무위험이자율
            mrp: 시장위험 프리미엄

        Returns:
            ApprovalPoint
        """
        scenarios = [
            Scenario(
                label="낙관적",
                value=auto_calculated_wacc,
                description=f"{auto_calculated_wacc:.2%} (추가 위험 없음)",
                is_recommended=False
            ),
            Scenario(
                label="중립적",
                value=auto_calculated_wacc + 0.01,  # +1%
                description=f"{auto_calculated_wacc + 0.01:.2%} (비상장 위험 프리미엄 +1%)",
                is_recommended=True
            ),
            Scenario(
                label="보수적",
                value=auto_calculated_wacc + 0.03,  # +3%
                description=f"{auto_calculated_wacc + 0.03:.2%} (신생기업 위험 프리미엄 +3%)",
                is_recommended=False
            )
        ]

        point = ApprovalPoint(
            id="DCF_WACC",
            category="DCF",
            name="WACC (할인율)",
            importance=3,
            question="WACC 시나리오를 선택하시겠습니까?",
            scenarios=scenarios,
            context={
                'calculation': f"Re = {rf:.2%} + {beta:.2f} × {mrp:.2%} = {rf + beta * mrp:.2%}",
                'warning': "WACC는 DCF 결과에 가장 큰 영향을 미칩니다."
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    def request_one_time_items_approval(self, detected_items: List[Dict]) -> ApprovalPoint:
        """
        DCF #3: 일회성 항목 조정 승인 ⭐⭐⭐

        Args:
            detected_items: AI가 감지한 일회성 항목
                [
                    {'year': 2023, 'item': '부동산 매각 차익', 'amount': 5000, 'type': '영업외수익'},
                    {'year': 2022, 'item': '소송 배상금', 'amount': -3000, 'type': '영업외비용'},
                    ...
                ]

        Returns:
            ApprovalPoint
        """
        # 각 항목별로 제거/유지 선택
        scenarios = []
        for item in detected_items:
            scenarios.append({
                'item_id': f"{item['year']}_{item['item']}",
                'year': item['year'],
                'description': f"{item['item']}: {item['amount']:+,}백만원 ({item['type']})",
                'amount': item['amount'],
                'options': ['제거 (추천)', '유지']
            })

        point = ApprovalPoint(
            id="DCF_ONE_TIME_ITEMS",
            category="DCF",
            name="일회성 항목 조정",
            importance=3,
            question="일회성 항목을 제거하시겠습니까?",
            scenarios=[],  # 각 항목별 선택이므로 scenarios 대신 context에 저장
            context={
                'items': scenarios,
                'warning': "일회성 제거 → 정상 수익력 파악 가능"
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    def request_ebitda_margin_approval(self, historical_margins: List[float],
                                       industry_avg: float) -> ApprovalPoint:
        """
        DCF #4: 영업이익률 승인 ⭐⭐

        Args:
            historical_margins: 과거 마진 [0.106, 0.122, 0.151]
            industry_avg: 업종 평균 마진 0.185

        Returns:
            ApprovalPoint
        """
        current_margin = historical_margins[-1]
        trend = "개선 추세" if historical_margins[-1] > historical_margins[0] else "악화 추세"

        scenarios = [
            Scenario(
                label="낙관적",
                value=0.20,
                description="규모의 경제 효과 → 20%까지 상승",
                is_recommended=False
            ),
            Scenario(
                label="중립적",
                value=industry_avg,
                description=f"업종 평균 수준 유지 ({industry_avg:.0%})",
                is_recommended=True
            ),
            Scenario(
                label="보수적",
                value=current_margin,
                description=f"현재 수준 유지 ({current_margin:.0%})",
                is_recommended=False
            )
        ]

        point = ApprovalPoint(
            id="DCF_EBITDA_MARGIN",
            category="DCF",
            name="영업이익률",
            importance=2,
            question="미래 영업이익률 시나리오를 선택하시겠습니까?",
            scenarios=scenarios,
            context={
                'historical': historical_margins,
                'trend': trend,
                'industry_avg': industry_avg
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    # ==================== 상대가치평가 판단 포인트 ====================

    def request_comparable_companies_approval(self, auto_selected: List[Dict]) -> ApprovalPoint:
        """
        상대가치 #1: 비교기업 선정 승인 ⭐⭐

        Args:
            auto_selected: AI가 자동 선정한 비교기업
                [
                    {'name': '더블유게임즈', 'ticker': '192080', 'similarity': 92,
                     'per': 10.0, 'industry': '소프트웨어', 'revenue': 450},
                    ...
                ]

        Returns:
            ApprovalPoint
        """
        point = ApprovalPoint(
            id="REL_COMPARABLE_COMPANIES",
            category="상대가치평가",
            name="비교기업 선정",
            importance=2,
            question="AI가 선정한 비교기업이 적절한가요?",
            scenarios=[
                Scenario(
                    label="적절함",
                    value=auto_selected,
                    description="그대로 사용",
                    is_recommended=True
                ),
                Scenario(
                    label="일부 제외",
                    value="custom",
                    description="유사도 낮은 기업 제외",
                    is_recommended=False
                ),
                Scenario(
                    label="직접 선택",
                    value="manual",
                    description="직접 비교기업 선택",
                    is_recommended=False
                )
            ],
            context={
                'companies': auto_selected,
                'total_count': len(auto_selected),
                'avg_similarity': sum(c['similarity'] for c in auto_selected) / len(auto_selected)
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    def request_marketability_discount_approval(self, is_ipo_preparing: bool = False) -> ApprovalPoint:
        """
        상대가치 #2: 비상장 할인율 승인 ⭐⭐⭐

        Args:
            is_ipo_preparing: IPO 준비 중 여부

        Returns:
            ApprovalPoint
        """
        scenarios = [
            Scenario(
                label="할인 없음",
                value=0.0,
                description="0% (IPO 준비 중, 유동성 확보 가능)",
                is_recommended=is_ipo_preparing
            ),
            Scenario(
                label="20% 할인",
                value=0.20,
                description="20% (일반적 비상장 할인율)",
                is_recommended=not is_ipo_preparing
            ),
            Scenario(
                label="30% 할인",
                value=0.30,
                description="30% (지배주주 외 소액주주)",
                is_recommended=False
            )
        ]

        point = ApprovalPoint(
            id="REL_MARKETABILITY_DISCOUNT",
            category="상대가치평가",
            name="비상장 할인율",
            importance=3,
            question="비상장 유동성 할인을 적용하시겠습니까?",
            scenarios=scenarios,
            context={
                'is_ipo_preparing': is_ipo_preparing,
                'warning': "비상장 기업은 유동성 부족으로 할인 필요"
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    # ==================== 자산가치평가 판단 포인트 ====================

    def request_land_building_fv_approval(self, book_value: Dict,
                                         has_appraisal: bool = False,
                                         appraisal_value: float = 0) -> ApprovalPoint:
        """
        NAV #1: 토지/건물 공정가치 승인 ⭐⭐⭐

        Args:
            book_value: {'land': 10000, 'building': 15000}
            has_appraisal: 감정평가서 보유 여부
            appraisal_value: 감정평가액

        Returns:
            ApprovalPoint
        """
        if has_appraisal:
            scenarios = [
                Scenario(
                    label="감정평가액 사용",
                    value=appraisal_value,
                    description=f"{appraisal_value:,}백만원 (감정평가서)",
                    is_recommended=True
                )
            ]
        else:
            estimated = book_value['land'] * 1.5 + book_value['building'] * 0.9
            scenarios = [
                Scenario(
                    label="AI 추정값",
                    value=estimated,
                    description=f"{estimated:,}백만원 (공시지가 기준 추정)",
                    is_recommended=True
                ),
                Scenario(
                    label="장부가 그대로",
                    value=book_value['land'] + book_value['building'],
                    description=f"{book_value['land'] + book_value['building']:,}백만원",
                    is_recommended=False
                )
            ]

        point = ApprovalPoint(
            id="NAV_LAND_BUILDING_FV",
            category="자산가치평가",
            name="토지/건물 공정가치",
            importance=3,
            question="토지/건물 공정가치를 어떻게 산정하시겠습니까?",
            scenarios=scenarios,
            context={
                'book_value': book_value,
                'has_appraisal': has_appraisal,
                'warning': "감정평가서 없이 진행 시 정확도 낮음"
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    def request_contingent_liabilities_approval(self) -> ApprovalPoint:
        """
        NAV #2: 우발부채 인식 승인 ⭐⭐⭐

        Returns:
            ApprovalPoint
        """
        point = ApprovalPoint(
            id="NAV_CONTINGENT_LIABILITIES",
            category="자산가치평가",
            name="우발부채 인식",
            importance=3,
            question="계류 중인 소송이나 채무 보증이 있습니까?",
            scenarios=[
                Scenario(
                    label="없음",
                    value=0,
                    description="우발부채 없음",
                    is_recommended=False
                ),
                Scenario(
                    label="있음 - 직접 입력",
                    value="custom",
                    description="소송 청구액 × 패소 확률",
                    is_recommended=False
                )
            ],
            context={
                'example': "소송 청구액 10억 × 패소 확률 30% = 3억 우발부채"
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    # ==================== 통합 판단 포인트 ====================

    def request_final_value_range_approval(self, five_method_results: Dict) -> ApprovalPoint:
        """
        통합 #1: 최종 가치 범위 선택 ⭐⭐⭐

        Args:
            five_method_results: {
                'dcf': 735,
                'relative': 690,
                'nav': 742,
                'cml': 738,
                'itl': 730
            }

        Returns:
            ApprovalPoint
        """
        values = list(five_method_results.values())
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)

        scenarios = [
            Scenario(
                label="전체 범위",
                value=(min_val, max_val),
                description=f"{min_val:,.0f}억 ~ {max_val:,.0f}억 (±{((max_val-min_val)/avg_val*100):.1f}%)",
                is_recommended=False
            ),
            Scenario(
                label="평균 ±10%",
                value=(avg_val * 0.9, avg_val * 1.1),
                description=f"{avg_val * 0.9:,.0f}억 ~ {avg_val * 1.1:,.0f}억",
                is_recommended=True
            ),
            Scenario(
                label="평가 목적별 가중평균",
                value="weighted",
                description="M&A: DCF 50% + 상대 30% + NAV 20%",
                is_recommended=False
            )
        ]

        point = ApprovalPoint(
            id="INTEGRATED_VALUE_RANGE",
            category="통합",
            name="최종 가치 범위",
            importance=3,
            question="최종 기업가치 범위를 어떻게 설정하시겠습니까?",
            scenarios=scenarios,
            context={
                'five_methods': five_method_results,
                'min': min_val,
                'max': max_val,
                'avg': avg_val,
                'median': sorted(values)[len(values) // 2]
            }
        )

        self.approval_points[point.id] = point
        self.approval_order.append(point.id)
        return point

    # ==================== 승인 처리 ====================

    def approve(self, point_id: str, selected_scenario: int = None,
               custom_value: Any = None, reason: str = "") -> bool:
        """
        평가자가 승인 처리

        Args:
            point_id: 승인 포인트 ID
            selected_scenario: 선택한 시나리오 인덱스 (0, 1, 2)
            custom_value: 직접 입력 값
            reason: 승인 사유

        Returns:
            성공 여부
        """
        if point_id not in self.approval_points:
            return False

        point = self.approval_points[point_id]

        if custom_value is not None:
            # 직접 입력
            point.approved_value = custom_value
            point.status = ApprovalStatus.CUSTOM
        elif selected_scenario is not None:
            # 시나리오 선택
            if 0 <= selected_scenario < len(point.scenarios):
                point.approved_value = point.scenarios[selected_scenario].value
                point.status = ApprovalStatus.APPROVED
            else:
                return False
        else:
            return False

        point.approval_reason = reason
        return True

    def get_all_approvals(self) -> Dict:
        """모든 승인 결과 가져오기"""
        return {
            point_id: {
                'name': point.name,
                'status': point.status.value,
                'approved_value': point.approved_value,
                'reason': point.approval_reason
            }
            for point_id, point in self.approval_points.items()
        }

    def get_pending_approvals(self) -> List[ApprovalPoint]:
        """승인 대기 중인 항목만 가져오기"""
        return [
            point for point in self.approval_points.values()
            if point.status == ApprovalStatus.PENDING
        ]

    def is_all_approved(self) -> bool:
        """모든 항목이 승인되었는지 확인"""
        return all(
            point.status in [ApprovalStatus.APPROVED, ApprovalStatus.CUSTOM]
            for point in self.approval_points.values()
        )


# ==================== 사용 예시 ====================

if __name__ == "__main__":
    # 승인 관리자 생성
    manager = HumanApprovalManager()

    # 1. DCF 성장률 승인 요청
    print("=" * 60)
    print("1. 매출 성장률 승인 요청")
    print("=" * 60)

    business_plan = {2024: 0.40, 2025: 0.35, 2026: 0.30, 2027: 0.25, 2028: 0.20}
    historical = {'avg_3yr': 0.45}
    industry_avg = 0.10

    growth_point = manager.request_growth_rate_approval(
        business_plan, historical, industry_avg
    )

    print(f"\n질문: {growth_point.question}")
    print(f"\n시나리오:")
    for i, scenario in enumerate(growth_point.scenarios):
        recommend = " ⭐ 추천" if scenario.is_recommended else ""
        print(f"  [{i}] {scenario.label}: {scenario.description}{recommend}")

    # 평가자가 시나리오 1 (중립적) 선택
    manager.approve("DCF_GROWTH_RATE", selected_scenario=1, reason="업종 평균과 절충이 합리적")

    print(f"\n✅ 승인됨: {manager.approval_points['DCF_GROWTH_RATE'].approved_value}")

    # 2. WACC 승인 요청
    print("\n" + "=" * 60)
    print("2. WACC 승인 요청")
    print("=" * 60)

    wacc_point = manager.request_wacc_approval(
        auto_calculated_wacc=0.0886,
        beta=1.15,
        rf=0.035,
        mrp=0.055
    )

    print(f"\n질문: {wacc_point.question}")
    print(f"계산: {wacc_point.context['calculation']}")
    print(f"\n시나리오:")
    for i, scenario in enumerate(wacc_point.scenarios):
        recommend = " ⭐ 추천" if scenario.is_recommended else ""
        print(f"  [{i}] {scenario.label}: {scenario.description}{recommend}")

    # 평가자가 직접 입력 (10.5%)
    manager.approve("DCF_WACC", custom_value=0.105, reason="비상장 위험 고려하여 10.5% 적용")

    print(f"\n✅ 승인됨: {manager.approval_points['DCF_WACC'].approved_value:.2%}")

    # 3. 전체 승인 현황
    print("\n" + "=" * 60)
    print("전체 승인 현황")
    print("=" * 60)

    all_approvals = manager.get_all_approvals()
    for point_id, info in all_approvals.items():
        print(f"\n{info['name']}: {info['status']}")
        print(f"  승인값: {info['approved_value']}")
        print(f"  사유: {info['reason']}")

    print(f"\n전체 승인 완료: {manager.is_all_approved()}")
