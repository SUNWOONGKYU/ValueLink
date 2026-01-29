"""
News Parser Service (Gemini)
AI 기반 뉴스 파싱 및 데이터 추출

@task Investment Tracker
@description Gemini를 사용하여 투자 뉴스에서 구조화된 데이터 추출
"""
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from google import genai

from app.core.config import settings
from app.services.news_crawler.base_crawler import CrawledNews

logger = logging.getLogger(__name__)


@dataclass
class ExtractedInvestmentData:
    """AI로 추출한 투자 데이터"""
    company_name_ko: str
    company_name_en: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    investment_amount_krw: Optional[float] = None  # 억원 단위
    valuation_pre_krw: Optional[float] = None      # 억원 단위
    valuation_post_krw: Optional[float] = None     # 억원 단위
    investment_stage: Optional[str] = None
    lead_investor: Optional[str] = None
    investors: Optional[List[Dict[str, str]]] = None
    summary: Optional[str] = None
    confidence_score: float = 0.0  # AI 추출 신뢰도


class NewsParser:
    """
    Gemini 기반 뉴스 파싱 서비스
    투자 뉴스에서 구조화된 데이터 추출
    """

    # 투자 단계 매핑
    STAGE_MAPPING = {
        "시드": "seed",
        "seed": "seed",
        "프리A": "pre_a",
        "프리 A": "pre_a",
        "pre-a": "pre_a",
        "pre a": "pre_a",
        "시리즈A": "series_a",
        "시리즈 A": "series_a",
        "series a": "series_a",
        "시리즈B": "series_b",
        "시리즈 B": "series_b",
        "series b": "series_b",
        "시리즈C": "series_c",
        "시리즈 C": "series_c",
        "series c": "series_c",
        "엔젤": "seed",
        "angel": "seed",
    }

    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_name = 'gemini-2.0-flash'  # 최신 무료 모델
        self.generation_config = {
            "temperature": 0.1,  # 낮은 온도로 일관된 추출
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

    async def parse_news(self, news: CrawledNews) -> Optional[ExtractedInvestmentData]:
        """
        단일 뉴스 기사에서 투자 정보 추출

        Args:
            news: 크롤링된 뉴스 객체

        Returns:
            추출된 투자 데이터 또는 None
        """
        prompt = self._build_extraction_prompt(news.title, news.content or "")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            extracted = self._parse_response(response.text)

            if extracted and extracted.company_name_ko:
                logger.info(f"Successfully extracted data for: {extracted.company_name_ko}")
                return extracted
            else:
                logger.warning(f"No company name extracted from: {news.title}")
                return None

        except Exception as e:
            logger.error(f"Error parsing news '{news.title}': {e}")
            return None

    async def parse_batch(
        self,
        news_list: List[CrawledNews]
    ) -> List[Dict[str, Any]]:
        """
        여러 뉴스 기사 일괄 파싱

        Args:
            news_list: 크롤링된 뉴스 목록

        Returns:
            추출된 데이터와 원본 뉴스 쌍의 목록
        """
        results = []

        for news in news_list:
            extracted = await self.parse_news(news)
            if extracted:
                results.append({
                    "news": news,
                    "extracted": extracted
                })

        logger.info(f"Parsed {len(results)}/{len(news_list)} news articles")
        return results

    def _build_extraction_prompt(self, title: str, content: str) -> str:
        """
        데이터 추출을 위한 프롬프트 생성 (정직하고 구체적인 추출 강조)

        Args:
            title: 뉴스 제목
            content: 뉴스 본문

        Returns:
            추출 프롬프트
        """
        return f"""당신은 팩트 기반의 금융 데이터 분석가입니다. 아래 뉴스에서 스타트업 투자 정보를 정확하게 추출하세요.

[뉴스 제목]
{title}

[뉴스 본문]
{content[:5000]}

아래 규칙을 엄격히 준수하여 JSON으로 응답하세요:

1. **절대 거짓말하지 마세요.** 뉴스 본문에 없는 내용을 추측하거나 지어내지 마세요.
2. **투자 금액**:
   - 구체적인 숫자가 있으면 '억원' 단위 숫자로 변환하세요. (예: "100억 원" -> 100)
   - "수십억 원", "규모 비공개" 등으로 나오면 **절대 추정하지 말고 null로 표시**하세요.
3. **업종(Industry)**:
   - "IT", "플랫폼", "AI", "서비스" 같이 모호한 단어를 **절대 사용하지 마세요.**
   - 구체적으로 적으세요. (예: "SaaS", "자율주행 로봇", "에듀테크", "바이오 진단키트", "핀테크 보안" 등)
4. **투자 단계**: 뉴스에 "시리즈A", "프리A" 등이 명시된 경우만 적으세요. 없으면 null.
5. **투자자**: 본문에 언급된 모든 투자사(VC, AC, 기업 등) 이름을 리스트에 담으세요.

{{
    "company_name_ko": "한글 기업명 (필수, (주) 제외)",
    "company_name_en": "영문 기업명 (본문에 없으면 null)",
    "industry": "구체적인 세부 업종 (IT/AI 금지)",
    "sub_industry": "더 구체적인 설명 또는 null",
    "investment_amount_krw": 숫자(억원) 또는 null (비공개/불확실 시 null),
    "valuation_post_krw": 기업가치(억원) 또는 null,
    "investment_stage": "시드/프리A/시리즈A/시리즈B 등 (명시된 경우만)",
    "lead_investor": "리드 투자자 (명시 안됐으면 null)",
    "investors": [
        {{"name": "투자자명"}}
    ],
    "summary": "핵심 내용 2문장 요약 (투자 내용 위주)",
    "confidence_score": 1.0 (확실함) ~ 0.0 (불확실)
}}"""

    def _parse_response(self, response_text: str) -> Optional[ExtractedInvestmentData]:
        """
        AI 응답을 파싱하여 데이터 객체로 변환

        Args:
            response_text: AI 응답 텍스트

        Returns:
            ExtractedInvestmentData 객체 또는 None
        """
        try:
            # JSON 추출 (마크다운 코드 블록 처리)
            json_str = response_text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]

            data = json.loads(json_str.strip())

            # 투자 단계 정규화
            stage = data.get("investment_stage")
            if stage:
                stage = self.STAGE_MAPPING.get(stage.lower(), stage)

            return ExtractedInvestmentData(
                company_name_ko=data.get("company_name_ko", ""),
                company_name_en=data.get("company_name_en"),
                industry=data.get("industry"),
                sub_industry=data.get("sub_industry"),
                investment_amount_krw=self._parse_amount(data.get("investment_amount_krw")),
                valuation_pre_krw=self._parse_amount(data.get("valuation_pre_krw")),
                valuation_post_krw=self._parse_amount(data.get("valuation_post_krw")),
                investment_stage=stage,
                lead_investor=data.get("lead_investor"),
                investors=data.get("investors"),
                summary=data.get("summary"),
                confidence_score=float(data.get("confidence_score", 0.0))
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None

    def _parse_amount(self, value: Any) -> Optional[float]:
        """
        금액 값 파싱 (다양한 형식 처리)

        Args:
            value: 원본 값

        Returns:
            float 또는 None
        """
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # 숫자만 추출
            import re
            numbers = re.findall(r'[\d.]+', value.replace(',', ''))
            if numbers:
                return float(numbers[0])

        return None

    async def generate_summary(self, news: CrawledNews) -> Optional[str]:
        """
        뉴스 요약 생성 (별도 메서드)

        Args:
            news: 크롤링된 뉴스

        Returns:
            요약 문자열
        """
        prompt = f"""다음 뉴스를 3문장 이내로 요약하세요. 핵심 정보(기업명, 투자금액, 투자자)를 포함하세요.

제목: {news.title}
내용: {news.content[:3000] if news.content else ''}

요약:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None


# 전역 인스턴스
news_parser = NewsParser()
