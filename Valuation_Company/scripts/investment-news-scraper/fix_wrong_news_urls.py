#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
잘못된 뉴스 URL 찾기 및 수정
- 공지사항, 행사 페이지 등 제외
- 실제 투자 기사 URL로 교체
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from supabase import create_client, Client
import time

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

# 5개 뉴스 소스
MEDIA_SITES = [
    {
        'name': 'WOWTALE',
        'search_url': 'https://www.wowtale.net/?s={keyword}',
        'link_selector': 'h2 a, h3 a',
        'exclude_patterns': [r'/\d{4}/\d{2}/\d{2}/\d+/$'],  # 실제 기사 패턴
    },
    {
        'name': '벤처스퀘어',
        'search_url': 'https://www.venturesquare.net/?s={keyword}',
        'link_selector': 'h2.entry-title a, h3.entry-title a',
    },
    {
        'name': '스타트업투데이',
        'search_url': 'https://www.startuptoday.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word={keyword}',
        'link_selector': 'div.list-titles a, h4.titles a',
    },
    {
        'name': '아웃스탠딩',
        'search_url': 'https://outstanding.kr/?s={keyword}',
        'link_selector': 'h2 a, h3 a',
    },
    {
        'name': '플래텀',
        'search_url': 'https://platum.kr/?s={keyword}',
        'link_selector': 'h2.entry-title a',
    },
]


def is_wrong_url(url):
    """잘못된 URL인지 확인 (공지사항, 행사 페이지 등)"""

    wrong_patterns = [
        r'공지',
        r'초대',
        r'데모데이',
        r'행사',
        r'안내',
        r'프로그램',
    ]

    for pattern in wrong_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    return False


def check_article_content(url):
    """기사 내용 확인 (투자 관련 키워드 포함 여부)"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 제목 추출
        title = soup.find('h1') or soup.find('title')
        title_text = title.get_text() if title else ""

        # 제목에 공지/행사 키워드 있으면 False
        exclude_title_keywords = ['공지', '초대', '데모데이', '안내', '프로그램', '행사']
        for keyword in exclude_title_keywords:
            if keyword in title_text:
                return False

        # 본문 텍스트
        article_text = soup.get_text()

        # 투자금액 패턴 확인 (필수)
        amount_patterns = [
            r'\d+억\s*원',
            r'\d+억',
            r'\d+조\s*\d+억',
        ]

        has_amount = False
        for pattern in amount_patterns:
            if re.search(pattern, article_text):
                has_amount = True
                break

        if not has_amount:
            return False

        # 투자 관련 키워드 확인
        investment_keywords = ['투자 유치', '시리즈', '조달', '펀딩']
        has_investment_keyword = False
        for keyword in investment_keywords:
            if keyword in article_text:
                has_investment_keyword = True
                break

        return has_investment_keyword

    except Exception as e:
        print(f"   확인 오류: {str(e)[:30]}")
        return False


def search_correct_news_url(company_name):
    """올바른 뉴스 URL 검색"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    for site in MEDIA_SITES:
        try:
            search_url = site['search_url'].format(keyword=company_name)
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            links = soup.select(site['link_selector'])

            for link in links[:5]:  # 상위 5개만 확인
                news_url = link.get('href', '')

                # 상대 URL이면 절대 URL로 변환
                if news_url.startswith('/'):
                    base_url = search_url.split('?')[0].rstrip('/')
                    news_url = base_url + news_url

                # 잘못된 URL 패턴 제외
                if is_wrong_url(news_url):
                    continue

                # 기사 내용 확인 (투자 키워드 포함 여부)
                if check_article_content(news_url):
                    return {
                        'url': news_url,
                        'site_name': site['name'],
                        'title': link.get_text(strip=True)
                    }

        except Exception as e:
            continue

    return None


def fix_wrong_news_urls():
    """잘못된 뉴스 URL 수정"""

    print("=" * 70)
    print("잘못된 뉴스 URL 찾기 및 수정")
    print("=" * 70)

    # 모든 Deal 가져오기 (테스트: 20개)
    result = supabase.table("deals")\
        .select("id, company_name, news_url, site_name")\
        .limit(20)\
        .execute()

    deals = result.data
    print(f"\n처리할 레코드: {len(deals)}개\n")

    fixed_count = 0
    wrong_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']
        news_url = deal.get('news_url', '')

        print(f"[{idx}/{len(deals)}] {company_name}...", end=" ")

        # URL 확인
        if is_wrong_url(news_url):
            print(f"❌ 잘못된 URL", end=" ")
            wrong_count += 1

            # 올바른 URL 검색
            correct_news = search_correct_news_url(company_name)

            if correct_news:
                # DB 업데이트
                supabase.table("deals")\
                    .update({
                        "news_url": correct_news['url'],
                        "site_name": correct_news['site_name'],
                        "news_title": correct_news['title']
                    })\
                    .eq("id", deal['id'])\
                    .execute()

                print(f"→ ✅ 수정: {correct_news['site_name']}")
                fixed_count += 1
            else:
                print("→ ⚠️ 대체 URL 없음")
        else:
            # 투자 키워드 확인
            if not check_article_content(news_url):
                print(f"⚠️ 투자 기사 아님", end=" ")
                wrong_count += 1

                # 올바른 URL 검색
                correct_news = search_correct_news_url(company_name)

                if correct_news:
                    supabase.table("deals")\
                        .update({
                            "news_url": correct_news['url'],
                            "site_name": correct_news['site_name'],
                            "news_title": correct_news['title']
                        })\
                        .eq("id", deal['id'])\
                        .execute()

                    print(f"→ ✅ 수정: {correct_news['site_name']}")
                    fixed_count += 1
                else:
                    print("→ ⚠️ 대체 URL 없음")
            else:
                print("✅ OK")

        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("수정 완료")
    print("=" * 70)
    print(f"❌ 잘못된 URL: {wrong_count}개")
    print(f"✅ 수정 완료: {fixed_count}개")
    print("=" * 70)


if __name__ == '__main__':
    fix_wrong_news_urls()
