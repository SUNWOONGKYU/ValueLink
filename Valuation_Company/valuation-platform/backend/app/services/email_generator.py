"""
Email Generator Service (Claude)
AI 기반 영업 이메일 템플릿 생성

@task Investment Tracker
@description Claude를 사용하여 맞춤형 영업 이메일 생성
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

import anthropic

from app.core.config import settings
from app.models.investment_tracker import StartupCompany, InvestmentRound

logger = logging.getLogger(__name__)


@dataclass
class GeneratedEmail:
    """생성된 이메일 템플릿"""
    subject: str
    body: str
    template_type: str  # initial, follow_up
    generation_prompt: str


class EmailGenerator:
    """
    Claude 기반 이메일 생성 서비스
    투자 유치 기업에 맞춤형 영업 이메일 생성
    """

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_initial_email(
        self,
        company: StartupCompany,
        latest_round: Optional[InvestmentRound] = None,
        sender_company: str = "밸류링크",
        sender_service: str = "기업가치평가 서비스"
    ) -> GeneratedEmail:
        """
        초기 접촉 이메일 생성

        Args:
            company: 스타트업 기업 정보
            latest_round: 최근 투자 라운드 정보
            sender_company: 발신 회사명
            sender_service: 제공 서비스명

        Returns:
            생성된 이메일 객체
        """
        prompt = self._build_initial_email_prompt(
            company=company,
            latest_round=latest_round,
            sender_company=sender_company,
            sender_service=sender_service
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,  # 약간의 창의성
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            result = self._parse_email_response(response.content[0].text)

            return GeneratedEmail(
                subject=result["subject"],
                body=result["body"],
                template_type="initial",
                generation_prompt=prompt
            )

        except Exception as e:
            logger.error(f"Error generating email for {company.name_ko}: {e}")
            # 기본 템플릿 반환
            return self._get_fallback_email(company, "initial")

    async def generate_follow_up_email(
        self,
        company: StartupCompany,
        previous_contact_summary: str,
        sender_company: str = "밸류링크"
    ) -> GeneratedEmail:
        """
        후속 이메일 생성

        Args:
            company: 스타트업 기업 정보
            previous_contact_summary: 이전 연락 요약
            sender_company: 발신 회사명

        Returns:
            생성된 이메일 객체
        """
        prompt = self._build_follow_up_prompt(
            company=company,
            previous_contact_summary=previous_contact_summary,
            sender_company=sender_company
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            result = self._parse_email_response(response.content[0].text)

            return GeneratedEmail(
                subject=result["subject"],
                body=result["body"],
                template_type="follow_up",
                generation_prompt=prompt
            )

        except Exception as e:
            logger.error(f"Error generating follow-up email for {company.name_ko}: {e}")
            return self._get_fallback_email(company, "follow_up")

    def _build_initial_email_prompt(
        self,
        company: StartupCompany,
        latest_round: Optional[InvestmentRound],
        sender_company: str,
        sender_service: str
    ) -> str:
        """초기 접촉 이메일 프롬프트 생성"""

        # 투자 정보 문자열 구성
        investment_info = ""
        if latest_round:
            investment_info = f"""
- 최근 투자 단계: {latest_round.stage.value if latest_round.stage else '알 수 없음'}
- 투자 금액: {latest_round.investment_amount_krw}억원
- 리드 투자자: {latest_round.lead_investor or '알 수 없음'}"""

        return f"""당신은 B2B 영업 전문가입니다. 다음 스타트업에 초기 접촉 이메일을 작성해주세요.

[대상 기업 정보]
- 기업명: {company.name_ko}
- 업종: {company.industry or '스타트업'}
- 세부 분야: {company.sub_industry or ''}
- 기업 설명: {company.description or '최근 투자를 유치한 스타트업'}
{investment_info}

[발신자 정보]
- 회사: {sender_company}
- 서비스: {sender_service}

[이메일 요구사항]
1. 제목은 간결하고 호기심을 유발하되 스팸처럼 보이지 않게
2. 투자 유치 축하로 시작하되 과하지 않게
3. {sender_service}가 기업 성장에 도움이 될 수 있음을 자연스럽게 언급
4. 짧은 미팅이나 통화 요청으로 마무리
5. 전체 길이는 200자 내외로 간결하게
6. 한국어로 작성, 존칭 사용

다음 형식으로 응답하세요:
[제목]
(이메일 제목)

[본문]
(이메일 본문)"""

    def _build_follow_up_prompt(
        self,
        company: StartupCompany,
        previous_contact_summary: str,
        sender_company: str
    ) -> str:
        """후속 이메일 프롬프트 생성"""

        return f"""당신은 B2B 영업 전문가입니다. 다음 스타트업에 후속 이메일을 작성해주세요.

[대상 기업 정보]
- 기업명: {company.name_ko}
- 업종: {company.industry or '스타트업'}

[이전 연락 내용]
{previous_contact_summary}

[발신자 정보]
- 회사: {sender_company}

[이메일 요구사항]
1. 이전 연락을 자연스럽게 상기시키기
2. 부담스럽지 않게 관심 확인
3. 추가 가치 제안 (사례, 자료 등)
4. 간단한 다음 단계 제안
5. 150자 내외로 더욱 간결하게
6. 한국어로 작성, 존칭 사용

다음 형식으로 응답하세요:
[제목]
(이메일 제목)

[본문]
(이메일 본문)"""

    def _parse_email_response(self, response_text: str) -> Dict[str, str]:
        """AI 응답에서 제목과 본문 분리"""

        subject = ""
        body = ""

        lines = response_text.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("[제목]"):
                current_section = "subject"
                continue
            elif line.startswith("[본문]"):
                current_section = "body"
                continue

            if current_section == "subject" and line:
                subject = line
            elif current_section == "body":
                body += line + "\n"

        return {
            "subject": subject.strip(),
            "body": body.strip()
        }

    def _get_fallback_email(
        self,
        company: StartupCompany,
        template_type: str
    ) -> GeneratedEmail:
        """기본 템플릿 반환 (AI 실패 시)"""

        if template_type == "initial":
            return GeneratedEmail(
                subject=f"{company.name_ko} 대표님, 축하드립니다!",
                body=f"""안녕하세요, {company.name_ko} 대표님.

최근 투자 유치 소식을 접하고 연락드립니다.

저희 밸류링크는 AI 기반 기업가치평가 서비스를 제공하고 있습니다.
기업 성장 과정에서 가치 측정이 필요하실 때 도움드릴 수 있습니다.

간단히 소개드릴 기회를 주시면 감사하겠습니다.

감사합니다.""",
                template_type="initial",
                generation_prompt="fallback"
            )
        else:
            return GeneratedEmail(
                subject=f"Re: {company.name_ko} 대표님께",
                body=f"""안녕하세요, {company.name_ko} 대표님.

지난번 연락 이후 안부 여쭙니다.

혹시 기업가치평가 관련하여 궁금하신 점이 있으시면
편하게 말씀해 주세요.

좋은 하루 되세요.""",
                template_type="follow_up",
                generation_prompt="fallback"
            )

    async def regenerate_email(
        self,
        company: StartupCompany,
        feedback: str,
        original_email: GeneratedEmail
    ) -> GeneratedEmail:
        """
        피드백을 반영하여 이메일 재생성

        Args:
            company: 스타트업 기업 정보
            feedback: 사용자 피드백
            original_email: 원본 이메일

        Returns:
            수정된 이메일 객체
        """
        prompt = f"""다음 이메일을 피드백에 맞게 수정해주세요.

[원본 이메일]
제목: {original_email.subject}
본문: {original_email.body}

[피드백]
{feedback}

[대상 기업]
{company.name_ko} ({company.industry or '스타트업'})

수정된 이메일을 다음 형식으로 응답하세요:
[제목]
(수정된 제목)

[본문]
(수정된 본문)"""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            result = self._parse_email_response(response.content[0].text)

            return GeneratedEmail(
                subject=result["subject"],
                body=result["body"],
                template_type=original_email.template_type,
                generation_prompt=prompt
            )

        except Exception as e:
            logger.error(f"Error regenerating email: {e}")
            return original_email


# 전역 인스턴스
email_generator = EmailGenerator()
