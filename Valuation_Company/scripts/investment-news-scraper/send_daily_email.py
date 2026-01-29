#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일일 뉴스 이메일 발송 (월-토 9am)
- 어제 수집된 투자 뉴스 발송
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
import requests

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

RESEND_API_KEY = os.getenv('RESEND_API_KEY')


def get_yesterday_deals():
    """
    어제 수집된 Deal 조회

    Returns:
        Deal 리스트
    """
    yesterday = (datetime.now() - timedelta(days=1)).date()

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
    date_str = (datetime.now() - timedelta(days=1)).strftime('%Y년 %m월 %d일')

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Noto Sans KR', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
        }}
        .deal {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .deal-title {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .deal-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}
        .deal-badge {{
            background: #e9ecef;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 13px;
        }}
        .deal-link {{
            display: inline-block;
            margin-top: 10px;
            color: #667eea;
            text-decoration: none;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 12px;
        }}
        .stats {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stats-number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Investment News Daily</h1>
        <p>{date_str} 투자 뉴스</p>
    </div>

    <div class="content">
        <div class="stats">
            <div class="stats-number">{len(deals)}</div>
            <div>건의 투자 뉴스</div>
        </div>
"""

    if not deals:
        html += """
        <div class="deal">
            <p style="text-align: center; color: #6c757d;">
                어제 수집된 투자 뉴스가 없습니다.
            </p>
        </div>
"""
    else:
        for deal in deals:
            html += f"""
        <div class="deal">
            <div class="deal-title">{deal['company_name']}</div>
            <div>{deal.get('industry', 'N/A')} · {deal.get('location', 'N/A')}</div>

            <div class="deal-info">
"""
            if deal.get('amount'):
                html += f"""
                <span class="deal-badge">💰 {deal['amount']}</span>
"""
            if deal.get('stage'):
                html += f"""
                <span class="deal-badge">📈 {deal['stage']}</span>
"""
            if deal.get('investors'):
                html += f"""
                <span class="deal-badge">🤝 {deal['investors']}</span>
"""

            html += f"""
            </div>

            <a href="{deal['news_url']}" class="deal-link" target="_blank">
                기사 전문 보기 →
            </a>
        </div>
"""

    html += """
    </div>

    <div class="footer">
        <p>Investment News Network</p>
        <p>구독 취소를 원하시면 <a href="#">여기</a>를 클릭하세요</p>
    </div>
</body>
</html>
"""

    return html


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

    date_str = (datetime.now() - timedelta(days=1)).strftime('%Y.%m.%d')
    subject = f"[Investment News] {date_str} 투자 뉴스 ({len(deals)}건)"

    # Resend API로 발송
    sent = 0
    failed = 0

    for subscriber in subscribers:
        try:
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {RESEND_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': 'Investment News <news@yourdomain.com>',
                    'to': subscriber['email'],
                    'subject': subject,
                    'html': html_content
                }
            )

            if response.status_code == 200:
                sent += 1
                print(f"  [SENT] {subscriber['email']}")

                # 발송 로그 저장
                supabase.table('email_send_log').insert({
                    'subscriber_id': subscriber['id'],
                    'email_type': 'daily',
                    'subject': subject,
                    'status': 'sent',
                    'deals_count': len(deals),
                    'deals_ids': [deal['id'] for deal in deals]
                }).execute()

                # 마지막 발송 시간 업데이트
                supabase.table('email_subscribers').update({
                    'last_sent_at': datetime.now().isoformat()
                }).eq('id', subscriber['id']).execute()

            else:
                failed += 1
                print(f"  [FAILED] {subscriber['email']}: {response.status_code}")

                # 실패 로그 저장
                supabase.table('email_send_log').insert({
                    'subscriber_id': subscriber['id'],
                    'email_type': 'daily',
                    'subject': subject,
                    'status': 'failed',
                    'error_message': response.text[:500]
                }).execute()

        except Exception as e:
            failed += 1
            print(f"  [ERROR] {subscriber['email']}: {str(e)[:100]}")

    print(f"\n[RESULT] Sent: {sent}, Failed: {failed}")


def main():
    """메인 실행"""
    print("="*60)
    print("Daily Investment News Email")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 어제 Deal 조회
    deals = get_yesterday_deals()

    print(f"\nFound {len(deals)} deals from yesterday")

    # 이메일 HTML 생성
    html_content = generate_email_html(deals)

    # 구독자에게 발송
    send_email_to_subscribers(html_content, deals)

    print("\n[DONE] Email sending complete")


if __name__ == '__main__':
    main()
