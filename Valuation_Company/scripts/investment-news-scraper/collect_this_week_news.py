#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이번 주 투자유치 뉴스 수집 (2026-01-27 ~ 2026-01-28)

프로세스:
1. 5대 언론기관 크롤링 (벤처스퀘어, 스타트업투데이, 아웃스탠딩, 더브이씨, 스타트업엔)
2. Gemini로 투자 뉴스 검증
3. 네이버 API로 보완
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from google import genai
from google.genai import types

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 5대 언론기관
MEDIA_SITES = [
    {
        'id': 9,
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net/category/news/',
        'article_selector': 'article.post',
        'title_selector': 'h5 a',
        'link_selector': 'h5 a',
        'date_selector': 'time.entry-date',
    },
    {
        'id': 11,
        'name': '스타트업투데이',
        'url': 'https://www.startuptoday.kr/news/articleList.html',
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles',
        'link_selector': 'a',
        'date_selector': 'span.byline',
    },
    {
        'id': 13,
        'name': '아웃스탠딩',
        'url': 'https://outstanding.kr/',
        'article_selector': 'article',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
        'date_selector': 'time',
    },
    {
        'id': 8,
        'name': '더브이씨',
        'url': 'https://thevc.kr/news',
        'article_selector': 'div.news-item',
        'title_selector': 'h3 a',
        'link_selector': 'h3 a',
        'date_selector': 'span.date',
    },
    {
        'id': 12,
        'name': '스타트업엔',
        'url': 'https://www.startupn.kr/news/articleList.html',
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles',
        'link_selector': 'a',
        'date_selector': 'span.byline',
    },
]

def extract_article_date(html_content, url):
    """기사 HTML에서 발행일 추출"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 날짜 추출 패턴
        date_patterns = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'pubdate'}),
            ('time', {'datetime': True}),
        ]

        for tag_name, attrs in date_patterns:
            tag = soup.find(tag_name, attrs)
            if tag:
                date_str = tag.get('content') or tag.get('datetime')
                if date_str:
                    if 'T' in date_str:
                        return date_str.split('T')[0]
                    else:
                        return date_str[:10]

        return None
    except:
        return None

def verify_with_gemini(title, url):
    """Gemini로 투자 뉴스인지 검증 및 정보 추출"""
    prompt = f"""
다음 뉴스 제목이 스타트업 투자유치 뉴스인지 확인해주세요:

제목: {title}

JSON 형식으로만 답변:
{{
    "is_investment": true,
    "company": "회사명",
    "stage": "시드/프리A/시리즈A 등",
    "investors": "투자자명",
    "amount": 숫자만
}}

투자유치 뉴스가 아니면 {{"is_investment": false}}만 출력하세요.
"""

    try:
        import json

        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=256,
                response_mime_type='application/json'
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            result = json.loads(text)
            return result

        return None
    except Exception as e:
        # JSON 파싱 실패 시 기본값 반환 (투자 키워드가 있으면 true)
        invest_keywords = ['투자', '유치', '펀딩', '시리즈', '라운드']
        if any(kw in title for kw in invest_keywords):
            return {'is_investment': True, 'company': None, 'stage': None, 'investors': None, 'amount': None}
        return {'is_investment': False}

def crawl_media_site(site):
    """언론사 사이트에서 최신 뉴스 크롤링 (2026-01-27 ~ 2026-01-28)"""
    print(f"\n📰 {site['name']} 크롤링 중...")

    articles = []

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(site['url'], headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            return articles

        soup = BeautifulSoup(response.content, 'html.parser')
        article_elements = soup.select(site['article_selector'])[:20]  # 최신 20개

        print(f"  검색된 기사: {len(article_elements)}개")

        for article in article_elements:
            try:
                # 제목 & 링크
                title_elem = article.select_one(site['title_selector'])
                link_elem = article.select_one(site['link_selector'])

                if not title_elem or not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                url = link_elem.get('href', '')

                # 상대 경로 처리
                if url.startswith('/'):
                    base_url = site['url'].split('?')[0].rsplit('/', 1)[0]
                    url = base_url + url

                if not url.startswith('http'):
                    continue

                # 투자 키워드 필터
                invest_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'Pre-A', '시드', '라운드']
                if any(kw in title for kw in invest_keywords):
                    # 일단 수집 (날짜는 나중에 추출)
                    articles.append({
                        'site_id': site['id'],
                        'site_name': site['name'],
                        'title': title,
                        'url': url,
                        'published_date': None  # Gemini 검증 시 추출
                    })
                    print(f"    ✅ {title[:60]}...")

                time.sleep(0.3)

            except Exception as e:
                continue

    except Exception as e:
        print(f"  ❌ 크롤링 오류: {str(e)[:50]}")

    return articles

def save_to_database(articles):
    """investment_news_articles 테이블에 저장"""
    print(f"\n💾 DB 저장 중... ({len(articles)}개)")

    saved = 0

    for article in articles:
        try:
            # 중복 체크
            existing = supabase.table('investment_news_articles')\
                .select('id')\
                .eq('article_url', article['url'])\
                .execute()

            if existing.data:
                print(f"  ⚠️  중복: {article['title'][:40]}...")
                continue

            # 날짜 추출
            print(f"  🔍 {article['title'][:40]}... ", end='')

            article_response = requests.get(article['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            published_date = extract_article_date(article_response.content, article['url']) if article_response.status_code == 200 else None

            # 2026-01-27 ~ 2026-01-28만 처리
            if published_date not in ['2026-01-27', '2026-01-28']:
                print(f"❌ 날짜 범위 밖 ({published_date})")
                continue

            # Gemini 검증
            gemini_result = verify_with_gemini(article['title'], article['url'])

            if gemini_result and gemini_result.get('is_investment'):
                print(f"✅ 투자 뉴스 ({published_date})")

                # 저장
                supabase.table('investment_news_articles').insert({
                    'site_number': article['site_id'],
                    'site_name': article['site_name'],
                    'site_url': article['url'].split('/')[2],  # domain
                    'article_title': article['title'],
                    'article_url': article['url'],
                    'published_date': published_date,
                    'has_amount': gemini_result.get('amount') is not None,
                    'has_investors': gemini_result.get('investors') is not None,
                    'has_stage': gemini_result.get('stage') is not None,
                }).execute()

                saved += 1
            else:
                print(f"❌ 투자 뉴스 아님 ({published_date})")

            time.sleep(1)  # API 제한

        except Exception as e:
            print(f"  ❌ 저장 오류: {str(e)[:50]}")

    print(f"\n✅ {saved}개 저장 완료")

# 메인
print("=" * 80)
print("이번 주 투자유치 뉴스 수집 (2026-01-27 ~ 2026-01-28)")
print("=" * 80)

all_articles = []

# Step 1: 5대 언론기관 크롤링
for site in MEDIA_SITES:
    articles = crawl_media_site(site)
    all_articles.extend(articles)
    time.sleep(2)

print(f"\n📊 총 수집: {len(all_articles)}개")

# Step 2: Gemini 검증 및 DB 저장
if all_articles:
    save_to_database(all_articles)
else:
    print("\n⚠️  수집된 기사가 없습니다.")

print("\n완료!")
