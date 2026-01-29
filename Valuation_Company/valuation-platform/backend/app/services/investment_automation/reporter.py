"""
Daily Report Service
투자 유치 뉴스 데일리 리포트 발송
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DailyReporter:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASSWORD")
        self.enabled = bool(self.smtp_user and self.smtp_pass)

    def send_report(self, deals: List[Dict[str, Any]], target_emails: List[str]):
        """데일리 리포트 이메일 발송"""
        if not self.enabled:
            logger.warning("SMTP settings not found. Skipping email report.")
            return False

        if not deals:
            logger.info("No deals to report today.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = ", ".join(target_emails)
            msg['Subject'] = f"[ValueLink] {len(deals)}건의 새로운 투자 유치 소식"

            # HTML 템플릿 생성
            html_content = self._generate_html(deals)
            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"✅ Daily report sent to {len(target_emails)} recipients")
            return True
        except Exception as e:
            logger.error(f"Failed to send daily report: {e}")
            return False

    def _generate_html(self, deals: List[Dict[str, Any]]) -> str:
        """이메일용 HTML 생성"""
        rows = ""
        for deal in deals:
            rows += f"""
            <tr>
                <td style='padding: 10px; border-bottom: 1px solid #eee;'>{deal['company_name']}</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee;'>{deal['industry']}</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee;'>{deal['amount']}억원</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee;'><a href='{deal['news_url']}'>기사보기</a></td>
            </tr>
            """
        
        return f"""
        <html>
            <body>
                <h2>📊 오늘의 투자 유치 뉴스</h2>
                <table style='width: 100%; border-collapse: collapse;'>
                    <tr style='background: #f4f4f4;'>
                        <th style='padding: 10px; text-align: left;'>기업명</th>
                        <th style='padding: 10px; text-align: left;'>주요사업</th>
                        <th style='padding: 10px; text-align: left;'>투자금액</th>
                        <th style='padding: 10px; text-align: left;'>뉴스</th>
                    </tr>
                    {rows}
                </table>
                <p style='margin-top: 20px;'>자세한 내용은 <a href='https://valuelink.ai'>ValueLink 플랫폼</a>에서 확인하세요.</p>
            </body>
        </html>
        """
