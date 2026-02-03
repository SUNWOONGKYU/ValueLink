#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일일 뉴스 이메일 발송 (월-토 9am)
- 어제 수집된 투자 뉴스 발송
- Gmail SMTP 사용
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta, timezone

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Gmail SMTP 설정
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')


def get_yesterday_deals():
    """
    어제 수집된 Deal 조회

    Returns:
        Deal 리스트
    """
    KST = timezone(timedelta(hours=9))
    yesterday = (datetime.now(KST) - timedelta(days=1)).date()

    result = supabase.table('deals').select('*').gte('news_date', yesterday.isoformat()).lte('news_date', f"{yesterday.isoformat()} 23:59:59").order('news_date', desc=True).execute()

    return result.data


def generate_email_html(deals):
    """
    이메일 HTML 생성

    Args:
        deals: Deal 리스트

    Returns:
        HTML 문자열
    """
    KST = timezone(timedelta(hours=9))
    date_str = (datetime.now(KST) - timedelta(days=1)).strftime('%Y년 %m월 %d일')

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#f4f5f7; font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f5f7; padding:20px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">

    <!-- Header -->
    <tr>
        <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed); padding:24px 30px; text-align:center;">
            <h1 style="margin:0; color:#ffffff; font-size:20px; font-weight:700;">{date_str} 투자 뉴스 ({len(deals)}건)</h1>
        </td>
    </tr>

    <!-- Deals List -->
    <tr>
        <td style="padding:20px 30px;">
"""

    if not deals:
        html += """
            <p style="text-align:center; color:#999; padding:30px 0; font-size:15px;">어제 수집된 투자 뉴스가 없습니다.</p>
"""
    else:
        for i, deal in enumerate(deals):
            news_title = deal.get('news_title', '')
            amount = deal.get('amount', '')
            investors = deal.get('investors', '')

            border_top = 'border-top:1px solid #eee; padding-top:16px; margin-top:16px;' if i > 0 else ''

            # 기업명 | 투자자 | 투자금액
            info_parts = [f"<b>{deal['company_name']}</b>"]
            if investors:
                info_parts.append(investors)
            info_parts.append(str(amount) if amount else '금액 미공개')
            info_line = ' | '.join(info_parts)

            html += f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="{border_top}">
            <tr><td style="padding-bottom:14px;">
                <p style="margin:0 0 10px; font-size:18px; color:#1a1a1a;">{info_line}</p>
"""
            if news_title:
                html += f"""
                <p style="margin:0 0 10px; font-size:16px; color:#666; line-height:1.6;">{news_title}</p>
"""
            html += f"""
                <a href="{deal['news_url']}" style="font-size:17px; color:#4f46e5; text-decoration:none;" target="_blank">기사 전문 보기 &rarr;</a>
            </td></tr>
            </table>
"""

    html += """
        </td>
    </tr>

    <!-- CTA Button -->
    <tr>
        <td style="padding:10px 30px 24px; text-align:center;">
            <a href="https://sunwoongkyu.github.io/ValueLink/Valuation_Company/valuation-platform/frontend/app/deal.html"
               style="display:inline-block; background:#4f46e5; color:#ffffff; padding:12px 28px;
                      border-radius:6px; text-decoration:none; font-size:17px; font-weight:600;">
                전체 투자 뉴스 보러가기 &rarr;
            </a>
        </td>
    </tr>

    <!-- Footer -->
    <tr>
        <td style="background:#fafafa; padding:16px 30px; text-align:center; border-top:1px solid #eee;">
            <p style="margin:0; font-size:11px; color:#bbb;">ValueLink Deals | 구독 취소는 이 이메일에 회신</p>
        </td>
    </tr>

</table>
</td></tr>
</table>

</body>
</html>"""

    return html


def send_email_via_gmail(to_email, subject, html_content):
    """
    Gmail SMTP로 이메일 발송

    Args:
        to_email: 수신자 이메일
        subject: 제목
        html_content: HTML 본문

    Returns:
        True(성공) / False(실패)
    """
    msg = MIMEMultipart('alternative')
    msg['From'] = f'ValueLink Deals <{GMAIL_ADDRESS}>'
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  [SMTP ERROR] {str(e)[:200]}")
        return False


def send_email_to_subscribers(html_content, deals):
    """
    구독자들에게 이메일 발송

    Args:
        html_content: 이메일 HTML
        deals: Deal 리스트
    """
    print("\n[EMAIL] Fetching subscribers...")

    # 일일 뉴스 구독자 조회 (daily 또는 both 구독자)
    result = supabase.table('newsletter_subscribers').select('*').eq('is_active', True).in_('subscription_type', ['daily', 'both']).execute()

    subscribers = result.data

    if not subscribers:
        print("  [INFO] No subscribers found")
        return

    print(f"  [INFO] Found {len(subscribers)} subscribers")

    KST = timezone(timedelta(hours=9))
    date_str = (datetime.now(KST) - timedelta(days=1)).strftime('%Y.%m.%d')
    subject = f"[투자 뉴스] {date_str} ({len(deals)}건)"

    sent = 0
    failed = 0

    for subscriber in subscribers:
        try:
            success = send_email_via_gmail(subscriber['email'], subject, html_content)

            if success:
                sent += 1
                print(f"  [SENT] {subscriber['email']}")
            else:
                failed += 1
                print(f"  [FAILED] {subscriber['email']}")

        except Exception as e:
            failed += 1
            print(f"  [ERROR] {subscriber['email']}: {str(e)[:100]}")

    print(f"\n[RESULT] Sent: {sent}, Failed: {failed}")


def main():
    """메인 실행"""
    print("="*60)
    print("Daily Investment News Email (Gmail SMTP)")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Gmail 설정 확인
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("\n[ERROR] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")
        return

    # 어제 Deal 조회
    deals = get_yesterday_deals()

    print(f"\nFound {len(deals)} deals from yesterday")

    # 0건이면 이메일 발송 안 함
    if not deals:
        print("\n[SKIP] No deals found - skipping email")
        return

    # 이메일 HTML 생성
    html_content = generate_email_html(deals)

    # 구독자에게 발송
    send_email_to_subscribers(html_content, deals)

    print("\n[DONE] Email sending complete")


if __name__ == '__main__':
    main()
