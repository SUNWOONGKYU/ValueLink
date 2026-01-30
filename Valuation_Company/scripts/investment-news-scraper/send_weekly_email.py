#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간 투자 리포트 이메일 발송 (일요일 10am KST)
- 지난 주 투자 통계 및 인사이트
- Gmail SMTP 사용
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
from collections import Counter

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Gmail SMTP 설정
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')


def get_last_week_deals():
    """
    지난 주 Deal 조회 (월요일 ~ 일요일)

    Returns:
        Deal 리스트
    """
    today = datetime.now().date()
    # 일요일 실행 기준: 지난 월요일 ~ 지난 토요일(어제)
    days_since_monday = (today.weekday() + 7) % 7
    last_monday = today - timedelta(days=days_since_monday + 6)
    last_sunday = last_monday + timedelta(days=6)

    result = supabase.table('deals').select('*').gte(
        'news_date', last_monday.isoformat()
    ).lte(
        'news_date', f"{last_sunday.isoformat()} 23:59:59"
    ).order('news_date', desc=True).execute()

    return result.data


def parse_amount(amount_str):
    """
    투자금액 문자열을 억원 단위 숫자로 변환

    Args:
        amount_str: "100억원", "50억", "1000만 달러" 등

    Returns:
        float (억원 단위), 파싱 불가 시 0
    """
    if not amount_str and amount_str != 0:
        return 0

    # 숫자 타입이면 그대로 반환 (DB에서 숫자로 저장된 경우, 억원 단위)
    if isinstance(amount_str, (int, float)):
        return float(amount_str)

    amount_str = str(amount_str).strip()

    # "약", "총", "최대", "규모" 등 제거
    cleaned = re.sub(r'(약|총|최대|규모|원|이상|이내)', '', amount_str).strip()

    # 억 단위 매칭: "100억", "2.5억"
    match = re.search(r'([\d,.]+)\s*억', cleaned)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return float(num_str)
        except ValueError:
            return 0

    # 만 달러 → 억원 환산 (대략 1300만원/만달러 기준)
    match = re.search(r'([\d,.]+)\s*만\s*달러', cleaned)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return float(num_str) * 0.13  # 대략적 환산
        except ValueError:
            return 0

    # $NM (million) → 억원
    match = re.search(r'\$\s*([\d,.]+)\s*[Mm]', cleaned)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return float(num_str) * 0.13
        except ValueError:
            return 0

    return 0


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

    # 투자금액 파싱
    for deal in deals:
        deal['_parsed_amount'] = parse_amount(deal.get('amount', ''))

    total_amount = sum(d['_parsed_amount'] for d in deals)

    # 금액 기준 Top 5
    deals_with_amount = sorted(deals, key=lambda d: d['_parsed_amount'], reverse=True)
    top5_deals = deals_with_amount[:5]

    # 최대 규모 딜
    max_deal = deals_with_amount[0] if deals_with_amount else None

    # 업종별 통계 (DB의 industry_category 사용)
    industry_stats = {}
    for deal in deals:
        cat = deal.get('industry_category')
        if cat:
            if cat not in industry_stats:
                industry_stats[cat] = {'count': 0, 'amount': 0}
            industry_stats[cat]['count'] += 1
            industry_stats[cat]['amount'] += deal['_parsed_amount']

    # 건수 기준 정렬
    industry_sorted = sorted(industry_stats.items(), key=lambda x: x[1]['count'], reverse=True)

    # 가장 활발한 업종 (2건 이상만, 없으면 1건이라도)
    top_industry = None
    for item in industry_sorted:
        if item[1]['count'] >= 2:
            top_industry = item
            break
    if not top_industry and industry_sorted:
        top_industry = industry_sorted[0]

    # 투자단계별 통계
    stages = [deal.get('stage') for deal in deals if deal.get('stage')]
    stage_counts = Counter(stages).most_common()

    # 투자자별 통계
    investors = []
    for deal in deals:
        if deal.get('investors'):
            investors.extend([inv.strip() for inv in deal['investors'].split(',')])
    investor_counts = Counter(investors).most_common(5)

    return {
        'total_deals': len(deals),
        'total_amount': total_amount,
        'max_deal': max_deal,
        'top_industry': top_industry,
        'top5_deals': top5_deals,
        'industry_sorted': industry_sorted[:7],
        'stage_counts': stage_counts,
        'investor_counts': investor_counts,
    }


def generate_weekly_html(deals, stats):
    """
    주간 리포트 HTML 생성 (테이블 기반, daily와 동일 스타일)

    Args:
        deals: Deal 리스트
        stats: 분석 통계

    Returns:
        HTML 문자열
    """
    today = datetime.now().date()
    days_since_monday = (today.weekday() + 7) % 7
    last_monday = today - timedelta(days=days_since_monday + 6)
    last_sunday = last_monday + timedelta(days=6)

    date_range = f"{last_monday.month}월 {last_monday.day}일 ~ {last_sunday.month}월 {last_sunday.day}일"
    date_range_short = f"{last_monday.month}.{last_monday.day}~{last_sunday.month}.{last_sunday.day}"
    deal_count = len(deals) if deals else 0

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
        <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed); padding:28px 30px; text-align:center;">
            <h1 style="margin:0; color:#ffffff; font-size:20px; font-weight:700;">{date_range} 주간 투자 리포트 ({deal_count}건)</h1>
        </td>
    </tr>
"""

    if not stats:
        html += """
    <tr>
        <td style="padding:40px 30px; text-align:center;">
            <p style="color:#999; font-size:15px;">지난 주 투자 뉴스가 없습니다.</p>
        </td>
    </tr>
"""
    else:
        # ---- 1) 핵심 요약 3줄 ----
        total_amount_str = f"약 {stats['total_amount']:,.0f}억원" if stats['total_amount'] > 0 else "금액 미공개 다수"
        top_ind_name = stats['top_industry'][0] if stats['top_industry'] else '-'
        top_ind_count = stats['top_industry'][1]['count'] if stats['top_industry'] else 0
        max_deal = stats['max_deal']
        max_deal_str = f"{max_deal['company_name']} {max_deal.get('amount', '금액 미공개')}" if max_deal else '-'

        html += f"""
    <tr>
        <td style="padding:24px 30px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f0ff; border-radius:8px; border-left:4px solid #4f46e5;">
            <tr><td style="padding:16px 20px;">
                <p style="margin:0 0 6px; font-size:14px; color:#333; line-height:1.7;">
                    &#8226; 이번 주 총 <b>{stats['total_deals']}건</b>, 총 투자금액 <b>{total_amount_str}</b><br>
                    &#8226; 가장 활발한 업종: <b>{top_ind_name}</b> ({top_ind_count}건)<br>
                    &#8226; 최대 규모: <b>{max_deal_str}</b>
                </p>
            </td></tr>
            </table>
        </td>
    </tr>
"""

        # ---- 2) 주요 딜 Top 5 ----
        html += """
    <tr>
        <td style="padding:20px 30px 8px;">
            <h2 style="margin:0 0 14px; font-size:16px; color:#4f46e5; font-weight:700;">주요 딜 Top 5</h2>
"""
        for i, deal in enumerate(stats['top5_deals']):
            border_top = 'border-top:1px solid #eee; padding-top:14px; margin-top:14px;' if i > 0 else ''
            company = deal.get('company_name', '')
            investors_str = deal.get('investors', '')
            amount = deal.get('amount', '금액 미공개')
            news_title = deal.get('news_title', '')
            news_url = deal.get('news_url', '#')

            info_parts = [f"<b>{company}</b>"]
            if investors_str:
                info_parts.append(investors_str)
            info_parts.append(amount if amount else '금액 미공개')
            info_line = ' | '.join(info_parts)

            html += f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="{border_top}">
            <tr><td style="padding-bottom:12px;">
                <p style="margin:0 0 8px; font-size:15px; color:#1a1a1a;">{info_line}</p>
"""
            if news_title:
                html += f"""
                <p style="margin:0 0 6px; font-size:13px; color:#666; line-height:1.5;">{news_title}</p>
"""
            html += f"""
                <a href="{news_url}" style="font-size:13px; color:#4f46e5; text-decoration:none;" target="_blank">기사 전문 보기 &rarr;</a>
            </td></tr>
            </table>
"""

        html += """
        </td>
    </tr>
"""

        # ---- 3) 업종별 동향 ----
        if stats['industry_sorted']:
            industry_items = []
            for name, data in stats['industry_sorted']:
                amt = f" ({data['amount']:,.0f}억원)" if data['amount'] > 0 else ""
                industry_items.append(f"{name}: {data['count']}건{amt}")
            industry_text = ' | '.join(industry_items)

            html += f"""
    <tr>
        <td style="padding:12px 30px 8px;">
            <h2 style="margin:0 0 10px; font-size:16px; color:#4f46e5; font-weight:700;">업종별 동향</h2>
            <p style="margin:0; font-size:14px; color:#444; line-height:1.8; background:#fafafa; padding:12px 16px; border-radius:6px;">{industry_text}</p>
        </td>
    </tr>
"""

        # ---- 4) 투자단계별 분포 ----
        if stats['stage_counts']:
            stage_items = [f"{stage}: {count}건" for stage, count in stats['stage_counts']]
            stage_text = ' | '.join(stage_items)

            html += f"""
    <tr>
        <td style="padding:12px 30px 8px;">
            <h2 style="margin:0 0 10px; font-size:16px; color:#4f46e5; font-weight:700;">투자단계별 분포</h2>
            <p style="margin:0; font-size:14px; color:#444; line-height:1.8; background:#fafafa; padding:12px 16px; border-radius:6px;">{stage_text}</p>
        </td>
    </tr>
"""

        # ---- 5) 활발한 투자자 Top 5 ----
        if stats['investor_counts']:
            investor_items = [f"{name} ({count}건)" for name, count in stats['investor_counts']]
            investor_text = ' | '.join(investor_items)

            html += f"""
    <tr>
        <td style="padding:12px 30px 8px;">
            <h2 style="margin:0 0 10px; font-size:16px; color:#4f46e5; font-weight:700;">이번 주 활발한 투자자 Top 5</h2>
            <p style="margin:0; font-size:14px; color:#444; line-height:1.8; background:#fafafa; padding:12px 16px; border-radius:6px;">{investor_text}</p>
        </td>
    </tr>
"""

    # ---- 6) CTA 버튼 ----
    html += """
    <tr>
        <td style="padding:20px 30px 24px; text-align:center;">
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

    # 주간 인사이트 구독자 조회 (weekly 또는 both 구독자)
    result = supabase.table('newsletter_subscribers').select('*').eq(
        'is_active', True
    ).in_('subscription_type', ['weekly', 'both']).execute()

    subscribers = result.data

    if not subscribers:
        print("  [INFO] No subscribers found")
        return

    print(f"  [INFO] Found {len(subscribers)} subscribers")

    today = datetime.now().date()
    days_since_monday = (today.weekday() + 7) % 7
    last_monday = today - timedelta(days=days_since_monday + 6)
    last_sunday = last_monday + timedelta(days=6)

    date_range = f"{last_monday.month}.{last_monday.day}~{last_sunday.month}.{last_sunday.day}"
    subject = f"[주간 투자 리포트] {date_range} ({len(deals)}건)"

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
    print("=" * 60)
    print("Weekly Investment Report Email (Gmail SMTP)")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Gmail 설정 확인
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("\n[ERROR] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")
        return

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
