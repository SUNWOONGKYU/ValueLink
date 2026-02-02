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
    월요일 발행 기준: 지난 월요일(7일 전) ~ 지난 일요일(어제)

    Returns:
        Deal 리스트
    """
    today = datetime.now().date()
    # 월요일 발행 기준: 7일 전(지난 월요일) ~ 어제(일요일)
    last_monday = today - timedelta(days=7)
    last_sunday = today - timedelta(days=1)

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
    # 월요일 발행 기준: 7일 전(지난 월요일) ~ 어제(일요일)
    last_monday = today - timedelta(days=7)
    last_sunday = today - timedelta(days=1)

    date_range = f"{last_monday.year}년 {last_monday.month}월 {last_monday.day}일 ~ {last_sunday.month}월 {last_sunday.day}일"
    date_range_short = f"{last_monday.year}.{last_monday.month}.{last_monday.day}~{last_sunday.month}.{last_sunday.day}"
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
        <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed); padding:32px 30px; text-align:center;">
            <p style="margin:0 0 6px; color:rgba(255,255,255,0.8); font-size:13px; font-weight:400; letter-spacing:0.5px;">WEEKLY DEAL REPORT</p>
            <h1 style="margin:0; color:#ffffff; font-size:21px; font-weight:700; line-height:1.4;">{date_range}</h1>
            <p style="margin:8px 0 0; color:rgba(255,255,255,0.9); font-size:14px;">총 {deal_count}건의 투자 뉴스</p>
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
    <!-- Section 1: Summary -->
    <tr>
        <td style="padding:28px 30px 12px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f7ff; border-radius:10px; border:1px solid #e8e5ff;">
            <tr><td style="padding:20px 24px;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td width="36" valign="top" style="padding-right:12px;">
                            <table cellpadding="0" cellspacing="0"><tr><td style="width:32px; height:32px; background:#4f46e5; border-radius:8px; text-align:center; line-height:32px; color:#fff; font-size:15px; font-weight:700;">&#931;</td></tr></table>
                        </td>
                        <td valign="middle">
                            <p style="margin:0; font-size:14px; color:#6b7280; line-height:1.3;">총 투자 건수 / 금액</p>
                            <p style="margin:4px 0 0; font-size:17px; color:#1a1a1a; font-weight:700;">{stats['total_deals']}건&nbsp;&nbsp;&#183;&nbsp;&nbsp;{total_amount_str}</p>
                        </td>
                    </tr>
                </table>
            </td></tr>
            <tr><td style="padding:0 24px;"><table width="100%" cellpadding="0" cellspacing="0"><tr><td style="border-top:1px solid #e8e5ff;"></td></tr></table></td></tr>
            <tr><td style="padding:14px 24px 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td width="50%" valign="top" style="padding-right:10px;">
                            <table cellpadding="0" cellspacing="0">
                                <tr>
                                    <td width="32" valign="top" style="padding-right:10px;">
                                        <table cellpadding="0" cellspacing="0"><tr><td style="width:28px; height:28px; background:#ede9fe; border-radius:6px; text-align:center; line-height:28px; color:#7c3aed; font-size:13px;">&#9650;</td></tr></table>
                                    </td>
                                    <td valign="top">
                                        <p style="margin:0; font-size:12px; color:#6b7280;">활발한 업종</p>
                                        <p style="margin:2px 0 0; font-size:14px; color:#1a1a1a; font-weight:600;">{top_ind_name} ({top_ind_count}건)</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                        <td width="50%" valign="top" style="padding-left:10px;">
                            <table cellpadding="0" cellspacing="0">
                                <tr>
                                    <td width="32" valign="top" style="padding-right:10px;">
                                        <table cellpadding="0" cellspacing="0"><tr><td style="width:28px; height:28px; background:#fef3c7; border-radius:6px; text-align:center; line-height:28px; color:#d97706; font-size:13px;">&#9733;</td></tr></table>
                                    </td>
                                    <td valign="top">
                                        <p style="margin:0; font-size:12px; color:#6b7280;">최대 규모</p>
                                        <p style="margin:2px 0 0; font-size:14px; color:#1a1a1a; font-weight:600;">{max_deal_str}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td></tr>
            <tr><td style="padding-bottom:6px;"></td></tr>
            </table>
        </td>
    </tr>
"""

        # ---- 2) 주요 딜 Top 5 ----
        html += """
    <!-- Section 2: Top 5 Deals -->
    <tr>
        <td style="padding:20px 30px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px;">
            <tr>
                <td style="padding-bottom:4px; border-bottom:2px solid #4f46e5;">
                    <h2 style="margin:0; font-size:16px; color:#4f46e5; font-weight:700;">&#x1F4B0; &#xFE0E;주요 딜 Top 5</h2>
                </td>
            </tr>
            </table>
"""
        for i, deal in enumerate(stats['top5_deals']):
            company = deal.get('company_name', '')
            investors_str = deal.get('investors', '')
            amount = deal.get('amount', '금액 미공개')
            news_title = deal.get('news_title', '')
            news_url = deal.get('news_url', '#')
            rank = i + 1

            # Alternate row background for visual rhythm
            card_bg = '#ffffff' if i % 2 == 0 else '#fafbff'
            border_color = '#e5e7eb' if i > 0 else '#4f46e5'

            html += f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px; border:1px solid {border_color}; border-radius:8px; overflow:hidden;">
            <tr>
                <td style="background:{card_bg}; padding:16px 18px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <!-- Rank number -->
                        <td width="36" valign="top" style="padding-right:14px;">
                            <table cellpadding="0" cellspacing="0"><tr><td style="width:30px; height:30px; background:{'#4f46e5' if rank <= 3 else '#7c3aed' if rank == 4 else '#8b5cf6'}; border-radius:50%; text-align:center; line-height:30px; color:#ffffff; font-size:14px; font-weight:700;">{rank}</td></tr></table>
                        </td>
                        <!-- Deal info -->
                        <td valign="top">
                            <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td>
                                    <span style="font-size:16px; font-weight:700; color:#111827;">{company}</span>
                                    <span style="display:inline-block; margin-left:8px; padding:2px 10px; background:{'#4f46e5' if rank == 1 else '#7c3aed'}; color:#ffffff; border-radius:12px; font-size:12px; font-weight:600; line-height:20px;">{amount if amount else '금액 미공개'}</span>
                                </td>
                            </tr>
                            </table>
"""
            if investors_str:
                html += f"""
                            <p style="margin:6px 0 0; font-size:13px; color:#6b7280; line-height:1.4;">&#x25B8; 투자자: {investors_str}</p>
"""
            if news_title:
                html += f"""
                            <p style="margin:6px 0 0; font-size:13px; color:#4b5563; line-height:1.5;">{news_title}</p>
"""
            html += f"""
                            <table cellpadding="0" cellspacing="0" style="margin-top:8px;"><tr><td><a href="{news_url}" style="font-size:12px; color:#4f46e5; text-decoration:none; font-weight:500;" target="_blank">기사 전문 보기 &rarr;</a></td></tr></table>
                        </td>
                    </tr>
                    </table>
                </td>
            </tr>
            </table>
"""

        html += """
        </td>
    </tr>
"""

        # ---- 3) 업종별 동향 ----
        if stats['industry_sorted']:
            industry_badges = ''
            badge_colors = ['#4f46e5', '#7c3aed', '#6366f1', '#8b5cf6', '#a78bfa', '#818cf8', '#c4b5fd']
            for idx, (name, data) in enumerate(stats['industry_sorted']):
                amt = f" &#183; {data['amount']:,.0f}억" if data['amount'] > 0 else ""
                bg = badge_colors[idx % len(badge_colors)]
                industry_badges += f'<td style="padding:0 6px 8px 0;"><table cellpadding="0" cellspacing="0"><tr><td style="background:{bg}; color:#ffffff; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:500; white-space:nowrap;">{name} {data["count"]}건{amt}</td></tr></table></td>'

            html += f"""
    <!-- Section 3: Industry -->
    <tr>
        <td style="padding:22px 30px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
            <tr>
                <td style="padding-bottom:4px; border-bottom:2px solid #7c3aed;">
                    <h2 style="margin:0; font-size:16px; color:#7c3aed; font-weight:700;">&#x1F3ED; &#xFE0E;업종별 동향</h2>
                </td>
            </tr>
            </table>
            <table cellpadding="0" cellspacing="0">
            <tr>{industry_badges}</tr>
            </table>
        </td>
    </tr>
"""

        # ---- 4) 투자단계별 분포 ----
        if stats['stage_counts']:
            stage_badges = ''
            stage_bg_colors = ['#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5']
            for idx, (stage, count) in enumerate(stats['stage_counts']):
                bg = stage_bg_colors[idx % len(stage_bg_colors)]
                text_color = '#ffffff' if idx < 3 else '#065f46'
                stage_badges += f'<td style="padding:0 6px 8px 0;"><table cellpadding="0" cellspacing="0"><tr><td style="background:{bg}; color:{text_color}; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:500; white-space:nowrap;">{stage} {count}건</td></tr></table></td>'

            html += f"""
    <!-- Section 4: Investment Stages -->
    <tr>
        <td style="padding:22px 30px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
            <tr>
                <td style="padding-bottom:4px; border-bottom:2px solid #059669;">
                    <h2 style="margin:0; font-size:16px; color:#059669; font-weight:700;">&#x1F4CA; &#xFE0E;투자단계별 분포</h2>
                </td>
            </tr>
            </table>
            <table cellpadding="0" cellspacing="0">
            <tr>{stage_badges}</tr>
            </table>
        </td>
    </tr>
"""

        # ---- 5) 활발한 투자자 Top 5 ----
        if stats['investor_counts']:
            investor_rows = ''
            for idx, (name, count) in enumerate(stats['investor_counts']):
                rank = idx + 1
                bar_width = int((count / stats['investor_counts'][0][1]) * 100) if stats['investor_counts'][0][1] > 0 else 100
                investor_rows += f"""
                <tr>
                    <td style="padding:8px 0; border-bottom:1px solid #f3f4f6;">
                        <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td width="28" style="font-size:13px; color:#9ca3af; font-weight:600;">{rank}.</td>
                            <td style="font-size:14px; color:#1f2937; font-weight:600;">{name}</td>
                            <td width="80" align="right">
                                <table cellpadding="0" cellspacing="0" align="right"><tr><td style="background:#ede9fe; color:#7c3aed; padding:3px 12px; border-radius:12px; font-size:12px; font-weight:700;">{count}건</td></tr></table>
                            </td>
                        </tr>
                        </table>
                    </td>
                </tr>
"""

            html += f"""
    <!-- Section 5: Top Investors -->
    <tr>
        <td style="padding:22px 30px 8px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
            <tr>
                <td style="padding-bottom:4px; border-bottom:2px solid #d97706;">
                    <h2 style="margin:0; font-size:16px; color:#d97706; font-weight:700;">&#x1F465; &#xFE0E;이번 주 활발한 투자자 Top 5</h2>
                </td>
            </tr>
            </table>
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#fffbeb; border-radius:8px; padding:4px 16px;">
                {investor_rows}
            </table>
        </td>
    </tr>
"""

    # ---- 6) CTA 버튼 ----
    html += """
    <!-- Section 6: CTA -->
    <tr>
        <td style="padding:28px 30px 28px; text-align:center;">
            <table cellpadding="0" cellspacing="0" align="center">
            <tr><td style="background:linear-gradient(135deg,#4f46e5,#7c3aed); border-radius:8px;">
                <a href="https://sunwoongkyu.github.io/ValueLink/Valuation_Company/valuation-platform/frontend/app/deal.html"
                   style="display:inline-block; color:#ffffff; padding:14px 36px;
                          text-decoration:none; font-size:16px; font-weight:700; letter-spacing:0.3px;">
                    전체 투자 뉴스 보러가기 &rarr;
                </a>
            </td></tr>
            </table>
        </td>
    </tr>

    <!-- Footer -->
    <tr>
        <td style="background:#f9fafb; padding:20px 30px; text-align:center; border-top:1px solid #e5e7eb;">
            <p style="margin:0 0 4px; font-size:12px; color:#9ca3af;">ValueLink Deals Weekly Report</p>
            <p style="margin:0; font-size:11px; color:#d1d5db;">구독 취소는 이 이메일에 회신해 주세요</p>
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
    # 월요일 발행 기준: 7일 전(지난 월요일) ~ 어제(일요일)
    last_monday = today - timedelta(days=7)
    last_sunday = today - timedelta(days=1)

    date_range = f"{last_monday.year}.{last_monday.month}.{last_monday.day}~{last_sunday.month}.{last_sunday.day}"
    subject = f"[주간 딜 리포트] {date_range} ({len(deals)}건)"

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
