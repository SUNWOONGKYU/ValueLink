"""
AI Router - 50:30:20 하이브리드 전략
Claude 50% | ChatGPT 30% | Gemini 20%
"""
from enum import Enum
from typing import Literal

class TaskType(str, Enum):
    # Claude 50% - 핵심 비즈니스 로직
    BUSINESS_LOGIC = "business_logic"
    SECURITY = "security"
    CODE_REVIEW = "code_review"
    DCF_CALCULATION = "dcf_calculation"
    COMPARABLE_CALCULATION = "comparable_calculation"
    PDF_GENERATION = "pdf_generation"
    DATA_VALIDATION = "data_validation"

    # OpenAI 30% - 멀티모달/구조화/챗봇
    IMAGE_OCR = "image_ocr"
    EXCEL_FORMULA = "excel_formula"
    CHATBOT = "chatbot"
    STRUCTURED_OUTPUT = "structured_output"
    PDF_ANALYSIS = "pdf_analysis"
    FINANCIAL_STATEMENT_EXTRACTION = "financial_statement_extraction"

    # Gemini 20% - 대용량/실시간 검색
    COMPANY_RESEARCH = "company_research"
    INDUSTRY_ANALYSIS = "industry_analysis"
    LARGE_CONTEXT = "large_context"
    REAL_TIME_DATA = "real_time_data"

class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

class AIRouter:
    """
    AI 작업을 최적의 모델로 라우팅
    Claude 50% - 품질 최우선 (핵심 로직, 보안)
    OpenAI 30% - 멀티모달/구조화 (이미지 OCR, PDF 분석, 챗봇)
    Gemini 20% - 실시간 검색/대용량 (기업 리서치, 산업 분석)
    """

    def select_model(
        self,
        task_type: TaskType,
        priority: TaskPriority = TaskPriority.NORMAL,
        context_size: int = 0
    ) -> Literal["claude", "gemini", "openai"]:
        """
        작업 유형과 우선순위에 따라 최적의 AI 모델 선택

        Args:
            task_type: 작업 유형
            priority: 우선순위 (CRITICAL은 항상 Claude)
            context_size: 컨텍스트 크기 (토큰 수)

        Returns:
            "claude" | "gemini" | "openai"
        """

        # 최우선: 중요 작업은 무조건 Claude (품질 최우선)
        if priority == TaskPriority.CRITICAL:
            return "claude"

        # Claude 50% - 핵심 비즈니스 로직
        if task_type in [
            TaskType.BUSINESS_LOGIC,
            TaskType.SECURITY,
            TaskType.CODE_REVIEW,
            TaskType.DCF_CALCULATION,
            TaskType.COMPARABLE_CALCULATION,
            TaskType.PDF_GENERATION,
            TaskType.DATA_VALIDATION,
        ]:
            return "claude"

        # OpenAI 30% - 멀티모달, PDF 분석, 챗봇
        if task_type in [
            TaskType.IMAGE_OCR,
            TaskType.EXCEL_FORMULA,
            TaskType.CHATBOT,
            TaskType.STRUCTURED_OUTPUT,
            TaskType.PDF_ANALYSIS,
            TaskType.FINANCIAL_STATEMENT_EXTRACTION,
        ]:
            return "openai"

        # Gemini 20% - 실시간 검색, 대용량 컨텍스트
        if task_type in [
            TaskType.COMPANY_RESEARCH,
            TaskType.INDUSTRY_ANALYSIS,
            TaskType.LARGE_CONTEXT,
            TaskType.REAL_TIME_DATA,
        ] or context_size > 200_000:
            return "gemini"

        # 기본값: Claude (품질 최우선)
        return "claude"

    def get_model_config(self, model: str) -> dict:
        """모델별 설정 반환"""
        configs = {
            "claude": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4096,
                "temperature": 0.0,
                "usage_ratio": 0.50,
            },
            "openai": {
                "model": "gpt-4o",
                "max_tokens": 4096,
                "temperature": 0.0,
                "usage_ratio": 0.30,
            },
            "gemini": {
                "model": "gemini-1.5-pro",
                "max_tokens": 8192,
                "temperature": 0.0,
                "usage_ratio": 0.20,
            }
        }
        return configs.get(model, configs["claude"])

# 전역 라우터 인스턴스
ai_router = AIRouter()
