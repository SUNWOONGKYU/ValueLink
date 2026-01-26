"""
Notification Service
이메일 알림 서비스 (Resend API 사용)

@description 평가 프로세스의 주요 단계에서 사용자에게 알림 전송
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime

from app.db.supabase_client import supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    알림 서비스
    이메일 및 SMS 알림 전송
    """

    def __init__(self):
        self.supabase = supabase_client
        # Resend API 설정
        self.resend_enabled = hasattr(settings, 'RESEND_API_KEY') and settings.RESEND_API_KEY
        if self.resend_enabled:
            self.from_email = getattr(settings, 'FROM_EMAIL', 'ValueLink <noreply@valuelink.co.kr>')
            logger.info("✅ Resend API configured. Emails will be sent via Resend.")
        else:
            self.from_email = 'ValueLink <noreply@valuelink.co.kr>'
            logger.warning("⚠️ RESEND_API_KEY not configured. Notifications will be logged only.")

    # ============================================================
    # 단계별 알림 메서드
    # ============================================================

    async def notify_step_complete(
        self,
        project_id: str,
        method: str,
        step: int
    ) -> bool:
        """
        단계 완료 알림

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법 (income/market/asset)
            step: 완료된 단계 번호

        Returns:
            bool: 알림 성공 여부
        """
        try:
            # 프로젝트 및 사용자 정보 조회
            project_data = await self._get_project_data(project_id, method)
            if not project_data:
                logger.error(f"Project not found: {project_id} ({method})")
                return False

            user_id = project_data.get("user_id")
            user_data = await self._get_user_data(user_id)
            if not user_data:
                logger.error(f"User not found: {user_id}")
                return False

            # 사용자 알림 설정 확인
            preferences = self._get_user_preferences(user_data)
            if not preferences.get("email_notifications", True):
                logger.info(f"User {user_id} has disabled email notifications")
                return True

            # 단계별 알림 메시지 생성
            message_data = self._get_step_message(method, step)
            if not message_data:
                logger.warning(f"No notification configured for step {step}")
                return True

            # 이메일 전송
            user_email = user_data.get("email")
            if user_email:
                await self.send_email(
                    to=user_email,
                    subject=message_data["subject"],
                    body=message_data["body"],
                    html=True
                )

            logger.info(f"Notification sent for project {project_id}, step {step}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False

    async def notify_approval_required(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        관리자 승인 필요 알림 (Step 3)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        try:
            project_data = await self._get_project_data(project_id, method)
            if not project_data:
                return False

            # 관리자 이메일 조회 (users 테이블에서 role='admin' 조회)
            admin_users = await self.supabase.select(
                "users",
                columns="email",
                filters={"role": "admin"}
            )

            if not admin_users:
                logger.warning("No admin users found for approval notification")
                return False

            company_name = project_data.get("company_name", "Unknown")
            subject = f"[평가 승인 요청] {company_name} 프로젝트"
            body = f"""
            <h2>평가 승인 요청</h2>
            <p>새로운 평가 프로젝트가 승인을 기다리고 있습니다.</p>
            <ul>
                <li><strong>기업명:</strong> {company_name}</li>
                <li><strong>평가 방법:</strong> {method.upper()}</li>
                <li><strong>프로젝트 ID:</strong> {project_id}</li>
            </ul>
            <p>관리자 페이지에서 승인 처리를 진행해주세요.</p>
            """

            # 모든 관리자에게 이메일 전송
            for admin in admin_users:
                await self.send_email(
                    to=admin["email"],
                    subject=subject,
                    body=body,
                    html=True
                )

            logger.info(f"Approval notification sent for project {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send approval notification: {str(e)}")
            return False

    async def notify_review_complete(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        회계사 검토 완료 알림 (Step 7 -> 8)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        return await self._notify_user_step(
            project_id,
            method,
            "회계사 검토가 완료되었습니다",
            "초안 보고서 작성이 시작되었습니다."
        )

    async def notify_draft_ready(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        초안 보고서 준비 완료 알림 (Step 9)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        return await self._notify_user_step(
            project_id,
            method,
            "초안 보고서가 준비되었습니다",
            "고객 페이지에서 초안 보고서를 확인하실 수 있습니다."
        )

    async def notify_final_ready(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        최종 보고서 준비 완료 알림 (Step 12)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        return await self._notify_user_step(
            project_id,
            method,
            "최종 보고서가 준비되었습니다",
            "결제 후 최종 보고서를 다운로드하실 수 있습니다."
        )

    async def notify_payment_required(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        결제 필요 알림 (Step 13)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        return await self._notify_user_step(
            project_id,
            method,
            "결제를 진행해주세요",
            "최종 보고서 수령을 위해 결제를 완료해주세요."
        )

    async def notify_report_delivered(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        보고서 전달 완료 알림 (Step 14)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        return await self._notify_user_step(
            project_id,
            method,
            "보고서가 전달되었습니다",
            "평가 보고서를 다운로드하실 수 있습니다. 감사합니다."
        )

    async def notify_revision_requested(
        self,
        project_id: str,
        method: str
    ) -> bool:
        """
        수정 요청 알림 (Step 10)
        회계사에게 수정이 필요함을 알림

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            bool: 알림 성공 여부
        """
        try:
            project_data = await self._get_project_data(project_id, method)
            if not project_data:
                return False

            # 회계사 이메일 조회 (users 테이블에서 role='accountant' 조회)
            accountant_users = await self.supabase.select(
                "users",
                columns="email",
                filters={"role": "accountant"}
            )

            if not accountant_users:
                logger.warning("No accountant users found for revision notification")
                return False

            company_name = project_data.get("company_name", "Unknown")
            subject = f"[수정 요청] {company_name} 프로젝트"
            body = f"""
            <h2>초안 수정 요청</h2>
            <p>고객이 초안 보고서에 대한 수정을 요청했습니다.</p>
            <ul>
                <li><strong>기업명:</strong> {company_name}</li>
                <li><strong>평가 방법:</strong> {method.upper()}</li>
                <li><strong>프로젝트 ID:</strong> {project_id}</li>
            </ul>
            <p>수정 사항을 확인하고 반영해주세요.</p>
            """

            # 모든 회계사에게 이메일 전송
            for accountant in accountant_users:
                await self.send_email(
                    to=accountant["email"],
                    subject=subject,
                    body=body,
                    html=True
                )

            logger.info(f"Revision notification sent for project {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send revision notification: {str(e)}")
            return False

    # ============================================================
    # 이메일 및 SMS 전송
    # ============================================================

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        이메일 전송 (Resend API 사용)

        Args:
            to: 수신자 이메일
            subject: 제목
            body: 본문
            html: HTML 형식 여부

        Returns:
            bool: 전송 성공 여부
        """
        try:
            # Resend API Key 확인
            resend_api_key = getattr(settings, 'RESEND_API_KEY', None)

            if not resend_api_key:
                # Resend API Key 미설정 시 콘솔 로그만
                logger.warning("⚠️ RESEND_API_KEY not configured. Email not sent.")
                logger.info(f"""
                ===== EMAIL NOTIFICATION (NOT SENT) =====
                To: {to}
                Subject: {subject}
                Body:
                {body}
                =========================================
                """)
                return True

            # Resend API를 통한 이메일 전송
            import httpx

            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "from": self.from_email or "ValueLink <noreply@valuelink.co.kr>",
                "to": [to],
                "subject": subject,
            }

            if html:
                payload["html"] = body
            else:
                payload["text"] = body

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    logger.info(f"✅ Email sent successfully to {to} via Resend")
                    return True
                else:
                    logger.error(f"❌ Resend API error: {response.status_code} - {response.text}")
                    return False
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    async def send_sms(
        self,
        phone: str,
        message: str
    ) -> bool:
        """
        SMS 전송 (향후 구현)

        Args:
            phone: 수신자 전화번호
            message: 메시지 내용

        Returns:
            bool: 전송 성공 여부
        """
        # TODO: Twilio 또는 AWS SNS 연동
        logger.info(f"""
        ===== SMS NOTIFICATION (NOT IMPLEMENTED) =====
        To: {phone}
        Message: {message}
        ==============================================
        """)
        return True

    # ============================================================
    # 내부 헬퍼 메서드
    # ============================================================

    async def _get_project_data(
        self,
        project_id: str,
        method: str
    ) -> Optional[Dict]:
        """
        프로젝트 데이터 조회

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법

        Returns:
            Optional[Dict]: 프로젝트 데이터
        """
        try:
            table_name = f"valuation_projects_{method}"
            result = await self.supabase.select(
                table_name,
                filters={"project_id": project_id}
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get project data: {str(e)}")
            return None

    async def _get_user_data(self, user_id: str) -> Optional[Dict]:
        """
        사용자 데이터 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[Dict]: 사용자 데이터
        """
        try:
            result = await self.supabase.select(
                "users",
                filters={"id": user_id}
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get user data: {str(e)}")
            return None

    def _get_user_preferences(self, user_data: Dict) -> Dict:
        """
        사용자 알림 설정 조회

        Args:
            user_data: 사용자 데이터

        Returns:
            Dict: 알림 설정
        """
        return {
            "email_notifications": user_data.get("email_notifications", True),
            "sms_notifications": user_data.get("sms_notifications", False)
        }

    def _get_step_message(self, method: str, step: int) -> Optional[Dict]:
        """
        단계별 알림 메시지 템플릿 조회

        Args:
            method: 평가 방법
            step: 단계 번호

        Returns:
            Optional[Dict]: 메시지 템플릿 (subject, body)
        """
        # 단계별 알림 메시지 매핑
        step_messages = {
            3: {
                "subject": "평가 신청이 접수되었습니다",
                "body": """
                <h2>평가 신청 접수 완료</h2>
                <p>귀하의 기업가치평가 신청이 정상적으로 접수되었습니다.</p>
                <p>관리자 승인 후 데이터 수집 단계로 진행될 예정입니다.</p>
                <p>진행 상황은 고객 페이지에서 확인하실 수 있습니다.</p>
                """
            },
            5: {
                "subject": "데이터 수집이 완료되었습니다",
                "body": """
                <h2>데이터 수집 완료</h2>
                <p>귀사의 재무 데이터 수집이 완료되었습니다.</p>
                <p>현재 평가 작업이 진행 중입니다.</p>
                """
            },
            6: {
                "subject": "평가가 완료되었습니다",
                "body": """
                <h2>평가 완료</h2>
                <p>기업가치평가가 완료되었습니다.</p>
                <p>현재 회계사 검토 단계에 있습니다.</p>
                """
            },
            7: {
                "subject": "회계사 검토가 시작되었습니다",
                "body": """
                <h2>회계사 검토 진행 중</h2>
                <p>평가 결과에 대한 회계사 검토가 진행 중입니다.</p>
                <p>검토 완료 후 초안 보고서를 확인하실 수 있습니다.</p>
                """
            },
            9: {
                "subject": "초안 보고서가 준비되었습니다",
                "body": """
                <h2>초안 보고서 준비 완료</h2>
                <p>기업가치평가 초안 보고서가 준비되었습니다.</p>
                <p>고객 페이지에서 초안을 확인하시고 피드백을 주시기 바랍니다.</p>
                """
            },
            12: {
                "subject": "최종 보고서가 준비되었습니다",
                "body": """
                <h2>최종 보고서 준비 완료</h2>
                <p>기업가치평가 최종 보고서가 준비되었습니다.</p>
                <p>결제를 완료하시면 보고서를 다운로드하실 수 있습니다.</p>
                """
            },
            13: {
                "subject": "결제를 진행해주세요",
                "body": """
                <h2>결제 요청</h2>
                <p>최종 보고서 수령을 위해 결제를 완료해주세요.</p>
                <p>결제 후 즉시 보고서를 다운로드하실 수 있습니다.</p>
                """
            },
            14: {
                "subject": "보고서가 전달되었습니다",
                "body": """
                <h2>보고서 전달 완료</h2>
                <p>기업가치평가 보고서가 전달되었습니다.</p>
                <p>고객 페이지에서 언제든지 다운로드하실 수 있습니다.</p>
                <p>ValueLink를 이용해주셔서 감사합니다.</p>
                """
            }
        }

        return step_messages.get(step)

    async def _notify_user_step(
        self,
        project_id: str,
        method: str,
        subject: str,
        message: str
    ) -> bool:
        """
        사용자에게 단계별 알림 전송 (공통 로직)

        Args:
            project_id: 프로젝트 ID
            method: 평가 방법
            subject: 이메일 제목
            message: 이메일 본문

        Returns:
            bool: 알림 성공 여부
        """
        try:
            project_data = await self._get_project_data(project_id, method)
            if not project_data:
                return False

            user_id = project_data.get("user_id")
            user_data = await self._get_user_data(user_id)
            if not user_data:
                return False

            preferences = self._get_user_preferences(user_data)
            if not preferences.get("email_notifications", True):
                return True

            company_name = project_data.get("company_name", "귀사")
            body = f"""
            <h2>{subject}</h2>
            <p><strong>기업명:</strong> {company_name}</p>
            <p><strong>평가 방법:</strong> {method.upper()}</p>
            <p>{message}</p>
            <p>자세한 내용은 고객 페이지에서 확인하실 수 있습니다.</p>
            """

            user_email = user_data.get("email")
            if user_email:
                await self.send_email(
                    to=user_email,
                    subject=f"[ValueLink] {subject}",
                    body=body,
                    html=True
                )

            return True

        except Exception as e:
            logger.error(f"Failed to send user notification: {str(e)}")
            return False


# 전역 인스턴스
notification_service = NotificationService()
