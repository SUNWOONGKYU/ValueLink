"""
AI 클라이언트 - 50:30:20 하이브리드 전략 구현
Claude 50% | OpenAI 30% | Gemini 20%
"""
import anthropic
import google.generativeai as genai
from openai import AsyncOpenAI
from typing import Dict, Any, Optional
from app.core.config import settings

class ClaudeClient:
    """
    Claude 3.5 Sonnet - 50% 사용
    - 핵심 비즈니스 로직 (DCF, 상대가치 계산)
    - 보안 중요 작업
    - 코드 검증 및 리뷰
    - PDF 보고서 생성
    """

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.model = "claude-3-5-sonnet-20241022"

    async def evaluate_dcf_logic(self, code: str, data: Dict) -> Dict:
        """DCF 계산 로직 검증 (핵심 비즈니스)"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": f"""Verify DCF calculation logic:

Code:
{code}

Input Data:
{data}

Return JSON with:
- is_valid: bool
- errors: list[str]
- suggestions: list[str]
"""
            }]
        )
        return {"content": response.content[0].text}

    async def calculate_dcf(
        self,
        free_cash_flows: list[float],
        discount_rate: float,
        terminal_growth_rate: float,
        shares_outstanding: int
    ) -> Dict:
        """DCF 평가 계산 (Claude 담당)"""
        prompt = f"""Calculate DCF valuation:

Free Cash Flows (5 years): {free_cash_flows}
Discount Rate (WACC): {discount_rate}%
Terminal Growth Rate: {terminal_growth_rate}%
Shares Outstanding: {shares_outstanding:,}

Provide detailed calculation with:
1. PV of each year's FCF
2. Terminal Value calculation
3. Enterprise Value
4. Equity Value per share
5. Step-by-step reasoning

Return as JSON.
"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        return {"content": response.content[0].text}

    async def review_security(self, code: str) -> Dict:
        """보안 코드 리뷰 (Claude 담당)"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"Review this code for security vulnerabilities:\n\n{code}"
            }]
        )
        return {"content": response.content[0].text}


class GeminiClient:
    """
    Gemini 1.5 Pro - 20% 사용
    - 기업 리서치 (Google Search 통합)
    - 산업 분석
    - 대용량 문서 처리 (2M 토큰 컨텍스트)
    - 실시간 데이터 수집
    """

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def analyze_large_document(
        self,
        text: str,
        max_context: int = 2_000_000
    ) -> Dict:
        """대용량 문서 분석 (Gemini 2M 토큰 활용)"""
        response = self.model.generate_content(
            f"Analyze this document and extract key information:\n\n{text[:max_context]}"
        )
        return {"content": response.text}

    async def research_company(
        self,
        company_name: str,
        ticker: Optional[str] = None
    ) -> Dict:
        """기업 리서치 (Google Search 활용)"""
        query = f"""Research {company_name} ({ticker if ticker else 'unlisted'}):

1. Company overview and business model
2. Recent news and developments
3. Key financial metrics
4. Industry position and competitors
5. Growth prospects

Provide comprehensive analysis using latest information.
"""
        response = self.model.generate_content(query)
        return {"content": response.text}

    async def analyze_industry(
        self,
        industry: str,
        region: str = "South Korea"
    ) -> Dict:
        """산업 분석 (Gemini 담당)"""
        query = f"""Analyze {industry} industry in {region}:

1. Market size and growth rate
2. Key trends and drivers
3. Competitive landscape
4. Regulatory environment
5. Future outlook

Use latest market data.
"""
        response = self.model.generate_content(query)
        return {"content": response.text}


class OpenAIClient:
    """
    GPT-4o - 30% 사용
    - 이미지 OCR (재무제표 스캔본)
    - PDF 재무제표 분석
    - Excel 수식 생성
    - 사용자 챗봇
    - 구조화된 데이터 출력
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"

    async def analyze_pdf_financial_statement(
        self,
        pdf_text: str
    ) -> Dict:
        """재무제표 PDF 분석 (OpenAI로 이동 - 30% 사용)"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial statement analysis expert. Extract data as structured JSON."
                },
                {
                    "role": "user",
                    "content": f"Extract financial data from this statement: {pdf_text}"
                }
            ],
            response_format={"type": "json_object"}
        )
        return {"content": response.choices[0].message.content}

    async def extract_from_image(
        self,
        image_base64: str,
        image_type: str = "financial_statement"
    ) -> Dict:
        """이미지에서 재무 데이터 추출 (Vision API)"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract {image_type} data from this image as structured JSON."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        return {"content": response.choices[0].message.content}

    async def generate_excel_formula(
        self,
        description: str,
        cell_references: Dict
    ) -> Dict:
        """Excel 수식 생성 (Structured Outputs)"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an Excel formula expert. Generate correct Excel formulas."
                },
                {
                    "role": "user",
                    "content": f"Generate Excel formula for: {description}\nCell references: {cell_references}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "excel_formula",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "formula": {"type": "string"},
                            "explanation": {"type": "string"},
                            "cell_range": {"type": "string"}
                        },
                        "required": ["formula", "explanation"]
                    }
                }
            }
        )
        return {"content": response.choices[0].message.content}

    async def chatbot_response(
        self,
        user_message: str,
        conversation_history: list
    ) -> Dict:
        """사용자 챗봇 응답 (OpenAI 담당)"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant for a corporate valuation platform. Answer in Korean."
            }
        ] + conversation_history + [
            {"role": "user", "content": user_message}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return {"content": response.choices[0].message.content}


# 전역 클라이언트 인스턴스
claude_client = ClaudeClient()
gemini_client = GeminiClient()
openai_client = OpenAIClient()
