#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 1-1: 5개 언론사 직접 스크래핑
- WOWTALE
- 벤처스퀘어
- 아웃스탠딩
- 더VC
- 스타트업투데이

→ investment_news_articles 테이블에 저장
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
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

# 5개 언론사 설정 (더VC 제외, 플래텀 포함)
SITES = [
    {
        'number': 1,
        'name': 'WOWTALE',
        'url': 'https://www.wowtale.net',
        'search_url': 'https://www.wowtale.net/?s=투자유치',
        'selectors': {
            'article': 'article.post, div.post',
            'title': 'h2.entry-title a, h3.entry-title a',
            'link': 'h2.entry-title a, h3.entry-title a',
            'date': 'time.entry-date, .published'
        }
    },
    {
        'number': 9,
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net',
        'search_url': 'https://www.venturesquare.net/category/news-contents/news-trends/news/',
        'selectors': {
            'article': 'li',
            'title': 'h4.bold a.black',
            'link': 'h4.bold a.black',
            'date': 'time'
        }
    },
    {
        'number': 13,
        'name': '아웃스탠딩',
        'url': 'https://outstanding.kr',
        'search_url': 'https://outstanding.kr/?s=투자유치',
        'selectors': {
            'article': 'article.post, div.post-item',
            'title': 'h2 a, h3 a',
            'link': 'h2 a, h3 a',
            'date': 'time, .date'
        }
    },
    {
        'number': 10,
        'name': '플래텀',
        'url': 'https://platum.kr',
        'search_url': 'https://platum.kr/category/investment',
        'selectors': {
            'article': 'article.archive-post, div.post_content',
            'title': 'h2.entry-title a, .title a',
            'link': 'h2.entry-title a, .title a',
            'date': 'time.entry-date, .date'
        }
    },
    {
        'number': 11,
        'name': '스타트업투데이',
        'url': 'https://www.startuptoday.kr',
        'search_url': 'https://www.startuptoday.kr/news/articleList.html?sc_area=A&view_type=sm&sc_word=투자유치',
        'selectors': {
            'article': 'div.list-block, article',
            'title': 'div.list-titles a, h4.titles a',
            'link': 'div.list-titles a, h4.titles a',
            'date': '.list-dated, time'
        }
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

INVESTMENT_KEYWORDS = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', '벤처캐피털']


def parse_date(date_str):
    """날짜 문자열 파싱"""
    # 기본값: 오늘 날짜
    default_date = datetime.now().strftime('%Y-%m-%d')

    if not date_str:
        return default_date

    # 숫자만 추출
    numbers = re.findall(r'\d+', date_str)
    if len(numbers) >= 3:
        try:
            y, m, d = map(int, numbers[:3])
            if y < 100:
                y += 2000
            return f"{y:04d}-{m:02d}-{d:02d}"
        except:
            return default_date

    # 파싱 실패 시 기본값
    return default_date


def scrape_site(site_info):
    """사이트별 스크래핑"""
    articles = []

    print(f"\n{'='*60}")
    print(f"📰 {site_info['name']} 스크래핑 중...")
    print(f"{'='*60}")

    try:
        response = requests.get(site_info['search_url'], headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        # 기사 목록 추출
        items = soup.select(site_info['selectors']['article'])

        print(f"발견된 항목: {len(items)}개")

        for idx, item in enumerate(items[:30], 1):  # 최대 30개
            try:
                # 제목과 URL 추출 (같은 셀렉터)
                link_elem = item.select_one(site_info['selectors']['link'])
                if not link_elem:
                    # 대체 셀렉터 시도
                    link_elem = item.find('a')
                    if not link_elem:
                        continue

                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')

                # 제목이 너무 짧으면 건너뛰기
                if len(title) < 10:
                    continue

                # 공지사항 제외
                if '[공지]' in title or '공지' in title[:5]:
                    continue

                # 투자 관련 키워드 확인 (완화: 있으면 우선, 없어도 일부 포함)
                has_keyword = any(keyword in title for keyword in INVESTMENT_KEYWORDS)

                # 투자 섹션에서 가져오므로 키워드 없어도 일부 포함
                if not has_keyword and idx > 10:  # 상위 10개는 키워드 없어도 OK
                    continue

                # 상대 경로 → 절대 경로
                if url.startswith('/'):
                    url = site_info['url'] + url
                elif not url.startswith('http'):
                    url = site_info['url'] + '/' + url

                # 날짜 추출
                date_elem = item.select_one(site_info['selectors']['date'])
                date_str = None
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)

                published_date = parse_date(date_str)

                articles.append({
                    'site_number': site_info['number'],
                    'site_name': site_info['name'],
                    'site_url': site_info['url'],
                    'article_title': title,
                    'article_url': url,
                    'published_date': published_date,
                    'content_snippet': None
                })

                print(f"  [{idx}] {title[:50]}...")

            except Exception as e:
                continue

        print(f"✅ {site_info['name']}: {len(articles)}개 수집")

    except Exception as e:
        print(f"❌ {site_info['name']} 오류: {str(e)[:100]}")

    return articles


def save_to_db(articles):
    """DB에 저장"""
    print(f"\n{'='*60}")
    print(f"💾 DB 저장 중...")
    print(f"{'='*60}")

    saved_count = 0
    duplicate_count = 0

    for article in articles:
        try:
            # 중복 확인
            existing = supabase.table("investment_news_articles")\
                .select("id")\
                .eq("article_url", article['article_url'])\
                .execute()

            if existing.data:
                duplicate_count += 1
                continue

            # 저장
            supabase.table("investment_news_articles").insert({
                "site_number": article['site_number'],
                "site_name": article['site_name'],
                "site_url": article['site_url'],
                "article_title": article['article_title'],
                "article_url": article['article_url'],
                "published_date": article['published_date'],
                "content_snippet": article['content_snippet']
            }).execute()

            saved_count += 1

        except Exception as e:
            print(f"  ❌ 저장 실패: {article['article_title'][:30]}... - {str(e)[:50]}")

    print(f"\n✅ 저장 완료: {saved_count}개")
    print(f"⚠️ 중복 건너뜀: {duplicate_count}개")


def main():
    print("=" * 60)
    print("STEP 1-1: 5개 언론사 직접 스크래핑")
    print("=" * 60)

    all_articles = []

    for site in SITES:
        articles = scrape_site(site)
        all_articles.extend(articles)

    print(f"\n{'='*60}")
    print(f"📊 총 수집: {len(all_articles)}개")
    print(f"{'='*60}")

    # 사이트별 통계
    site_stats = {}
    for article in all_articles:
        site_name = article['site_name']
        site_stats[site_name] = site_stats.get(site_name, 0) + 1

    for site_name, count in site_stats.items():
        print(f"  - {site_name}: {count}개")

    # DB 저장
    if all_articles:
        save_to_db(all_articles)

    print(f"\n{'='*60}")
    print("STEP 1-1 완료!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
