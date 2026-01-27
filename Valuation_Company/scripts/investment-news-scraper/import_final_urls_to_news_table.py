#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
92개 기업의 실제 투자 뉴스 URL을 investment_news_articles 테이블에 저장
"""

import os
import sys
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# 사이트명 → site_number 매핑
SITE_MAPPING = {
    'WOWTALE': 1,
    '벤처스퀘어': 9,
    '플래텀': 10,
    '스타트업투데이': 11,
    '아웃스탠딩': 13,
    '더브이씨': 8,
    '더벨': 16,
    '조선비즈': 24,
    '매일경제': 24,
    'MK테크리뷰': 24,
    '블로터': 22,
    '로봇신문': 99,
    '아시아경제': 99,
    '한국경제': 23,
    '이데일리': 99,
    '헬로티': 99,
    'ZDNet Korea': 15,
    '원티드': 99,
    '코리아데일리': 99,
    '서울경제': 99,
    '스타트업 투데이': 11
}

# 사이트명 → site_url 매핑
SITE_URL_MAPPING = {
    'WOWTALE': 'https://wowtale.net',
    '벤처스퀘어': 'https://www.venturesquare.net',
    '플래텀': 'https://platum.kr',
    '스타트업투데이': 'https://www.startuptoday.kr',
    '아웃스탠딩': 'https://outstanding.kr',
    '더브이씨': 'https://thevc.kr',
    '더벨': 'https://www.thebell.co.kr',
    '조선비즈': 'https://biz.chosun.com',
    '매일경제': 'https://www.mk.co.kr',
    'MK테크리뷰': 'https://www.mk.co.kr',
    '블로터': 'https://www.bloter.net',
    '로봇신문': 'https://www.irobotnews.com',
    '아시아경제': 'https://www.asiae.co.kr',
    '한국경제': 'https://www.hankyung.com',
    '이데일리': 'https://www.edaily.co.kr',
    '헬로티': 'https://www.hellot.net',
    'ZDNet Korea': 'https://www.zdnet.co.kr',
    '원티드': 'https://www.wanted.co.kr',
    '코리아데일리': 'https://www.koreadaily.com',
    '서울경제': 'https://www.sedaily.com',
    '스타트업 투데이': 'https://www.startuptoday.kr'
}


def get_published_date(week_str):
    """주차 정보로 발행일 추정"""
    # 2026년 1월 27일 기준 역산
    base_date = datetime(2026, 1, 27)

    # 주차 파싱
    if '주차' in week_str:
        week_num = int(week_str.replace('주차', ''))
        # 5주차 = 최신 (오늘)
        # 4주차 = 1주 전
        # 3주차 = 2주 전
        weeks_ago = 5 - week_num
        target_date = base_date - timedelta(weeks=weeks_ago)
        return target_date.strftime('%Y-%m-%d')

    return base_date.strftime('%Y-%m-%d')


def main():
    print("=" * 60)
    print("92개 기업 뉴스 URL → investment_news_articles 테이블 저장")
    print("=" * 60)

    csv_file = 'final_found_urls.csv'

    # CSV 읽기
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 레코드\n")

    saved_count = 0
    duplicate_count = 0
    error_count = 0

    for idx, row in enumerate(companies, 1):
        company_name = row['기업명']
        stage = row['단계']
        amount = row['신규']
        news_url = row['뉴스URL']
        site_name = row['뉴스소스']
        week = row['주차']

        # 사이트 정보
        site_number = SITE_MAPPING.get(site_name, 99)
        site_url = SITE_URL_MAPPING.get(site_name, '')

        # 발행일
        published_date = get_published_date(week)

        # 제목 생성
        if amount and amount != '비공개' and amount != '-':
            article_title = f"{company_name} {stage} {amount} 투자 유치"
        else:
            article_title = f"{company_name} {stage} 투자 유치"

        print(f"[{idx}/{len(companies)}] {company_name}...", end=' ')

        try:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", news_url)\
                .execute()

            if existing.data:
                print("⚠️ 중복")
                duplicate_count += 1
                continue

            # 저장
            supabase.table("investment_news_articles").insert({
                "site_number": site_number,
                "site_name": site_name,
                "site_url": site_url,
                "article_title": article_title,
                "article_url": news_url,
                "published_date": published_date,
                "content_snippet": f"{company_name} | {stage} | {amount}"
            }).execute()

            print(f"✅ 저장 [{site_name}]")
            saved_count += 1

        except Exception as e:
            print(f"❌ 오류: {str(e)[:50]}")
            error_count += 1

    print(f"\n{'='*60}")
    print("저장 완료")
    print(f"{'='*60}")
    print(f"✅ 저장: {saved_count}개")
    print(f"⚠️ 중복: {duplicate_count}개")
    print(f"❌ 오류: {error_count}개")
    print(f"{'='*60}")

    # 사이트별 통계
    site_stats = {}
    for row in companies:
        site_name = row['뉴스소스']
        site_stats[site_name] = site_stats.get(site_name, 0) + 1

    print("\n📰 사이트별 통계:")
    for site, count in sorted(site_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {site}: {count}개")


if __name__ == '__main__':
    main()
