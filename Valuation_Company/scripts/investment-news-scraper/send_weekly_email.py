#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간 인사이트 리포트 이메일 발송 (일요일 10am)
- 지난 주 투자 통계 및 인사이트
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
import requests
from collections import Counter

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

RESEND_API_KEY = os.getenv('RESEND_API_KEY')


def get_last_week_deals():
    """
    지난 주 Deal 조회

    Returns:
        Deal 리스트
    """
    # 지난 주 월요일 ~ 일요일
    today = datetime.now().date()
    days_since_monday = (today.weekday() + 7) % 7  # 일요일 = 0
    last_monday = today - timedelta(days=days_since_monday + 6)
    last_sunday = last_monday + timedelta(days=6)

    result = supabase.table('deals').select('*').gte('news_date', last_monday.isoformat()).lte('news_date', f"{last_sunday.isoformat()} 23:59:59").order('news_date', desc=True).execute()

    return result.data


def analyze_deals(deals):
    """
    Deal 데이터 분석

    Args:
        deals: Deal 리스트

    Returns:
        분석 결과 딕셔너리
    """
    if not deals:
        return None

    # 투자 단계별 통계
    stages = [deal.get('stage') for deal in deals if deal.get('stage')]
    stage_counts = Counter(stages)

    # 업종별 통계
    industries = []
    for deal in deals:
        if deal.get('industry'):
            industries.extend([ind.strip() for ind in deal['industry'].split(',')])
    industry_counts = Counter(industries)

    # 지역별 통계
    locations = [deal.get('location') for deal in deals if deal.get('location')]
    location_counts = Counter(locations)

    # 투자자별 통계
    investors = []
    for deal in deals:
        if deal.get('investors'):
            investors.extend([inv.strip() for inv in deal['investors'].split(',')])
    investor_counts = Counter(investors)

    return {
        'total_deals': len(deals),
        'unique_companies': len(set(deal['company_name'] for deal in deals)),
        'stage_counts': stage_counts.most_common(5),
        'industry_counts': industry_counts.most_common(5),
        'location_counts': location_counts.most_common(5),
        'investor_counts': investor_counts.most_common(10)
    }


def generate_weekly_html(deals, stats):
    """
    주간 리포트 HTML 생성

    Args:
        deals: Deal 리스트
        stats: 분석 통계

    Returns:
        HTML 문자열
    """
    # 지난 주 날짜 범위
    today = datetime.now().date()
    days_since_monday = (today.weekday() + 7) % 7
    last_monday = today - timedelta(days=days_since_monday + 6)
    last_sunday = last_monday + timedelta(days=6)

    date_range = f"{last_monday.strftime('%Y.%m.%d')} ~ {last_sunday.strftime('%m.%d')}"

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
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #f5576c;
        }}
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #f5576c;
        }}
        .rank-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .rank-item:last-child {{
            border-bottom: none;
        }}
        .rank-number {{
            background: #f5576c;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            margin-right: 10px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Investment Weekly Insight</h1>
        <p>{date_range} 주간 투자 리포트</p>
    </div>

    <div class="content">
"""

    if not stats:
        html += """
        <div class="section">
            <p style="text-align: center; color: #6c757d;">
                지난 주 투자 뉴스가 없습니다.
            </p>
        </div>
"""
    else:
        # 주요 통계
        html += f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_deals']}</div>
                <div class="stat-label">총 투자 건수</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['unique_companies']}</div>
                <div class="stat-label">투자 기업 수</div>
            </div>
        </div>
"""

        # 투자 단계 Top 5
        if stats['stage_counts']:
            html += """
        <div class="section">
            <div class="section-title">📊 투자 단계 Top 5</div>
"""
            for i, (stage, count) in enumerate(stats['stage_counts'], 1):
                html += f"""
            <div class="rank-item">
                <div>
                    <span class="rank-number">{i}</span>
                    <span>{stage}</span>
                </div>
                <div><strong>{count}건</strong></div>
            </div>
"""
            html += """
        </div>
"""

        # 업종 Top 5
        if stats['industry_counts']:
            html += """
        <div class="section">
            <div class="section-title">🏢 업종 Top 5</div>
"""
            for i, (industry, count) in enumerate(stats['industry_counts'], 1):
                html += f"""
            <div class="rank-item">
                <div>
                    <span class="rank-number">{i}</span>
                    <span>{industry}</span>
                </div>
                <div><strong>{count}건</strong></div>
            </div>
"""
            html += """
        </div>
"""

        # 투자자 Top 10
        if stats['investor_counts']:
            html += """
        <div class="section">
            <div class="section-title">💼 활발한 투자자 Top 10</div>
"""
            for i, (investor, count) in enumerate(stats['investor_counts'], 1):
                html += f"""
            <div class="rank-item">
                <div>
                    <span class="rank-number">{i}</span>
                    <span>{investor}</span>
                </div>
                <div><strong>{count}건</strong></div>
            </div>
"""
            html += """
        </div>
"""

        # 지역 Top 5
        if stats['location_counts']:
            html += """
        <div class="section">
            <div class="section-title">📍 지역 Top 5</div>
"""
            for i, (location, count) in enumerate(stats['location_counts'], 1):
                html += f"""
            <div class="rank-item">
                <div>
                    <span class="rank-number">{i}</span>
                    <span>{location}</span>
                </div>
                <div><strong>{count}건</strong></div>
            </div>
"""
            html += """
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

    # 주간 인사이트 구독자 조회 (weekly 또는 both 구독자)
    result = supabase.table('newsletter_subscribers').select('*').eq('is_active', True).in_('subscription_type', ['weekly', 'both']).execute()

    subscribers = result.data

    if not subscribers:
        print("  [INFO] No subscribers found")
        return

    print(f"  [INFO] Found {len(subscribers)} subscribers")

    today = datetime.now().date()
    days_since_monday = (today.weekday() + 7) % 7
    last_monday = today - timedelta(days=days_since_monday + 6)
    last_sunday = last_monday + timedelta(days=6)

    date_range = f"{last_monday.strftime('%Y.%m.%d')}~{last_sunday.strftime('%m.%d')}"
    subject = f"[Investment Insight] {date_range} 주간 투자 리포트 ({len(deals)}건)"

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
                    'from': 'Investment Insight <insight@yourdomain.com>',
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
                    'email_type': 'weekly',
                    'subject': subject,
                    'status': 'sent',
                    'deals_count': len(deals),
                    'deals_ids': [deal['id'] for deal in deals] if deals else []
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
                    'email_type': 'weekly',
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
    print("Weekly Investment Insight Email")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 지난 주 Deal 조회
    deals = get_last_week_deals()

    print(f"\nFound {len(deals)} deals from last week")

    # 통계 분석
    stats = analyze_deals(deals)

    # 이메일 HTML 생성
    html_content = generate_weekly_html(deals, stats)

    # 구독자에게 발송
    send_email_to_subscribers(html_content, deals)

    print("\n[DONE] Email sending complete")


if __name__ == '__main__':
    main()
