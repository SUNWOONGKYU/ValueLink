#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1단계 테스트: 첫 10개 기업만
"""

import os, sys, csv, requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
from supabase import create_client

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# 벤처스퀘어만 테스트
SITE = {
    'number': 9,
    'name': '벤처스퀘어',
    'url': 'https://www.venturesquare.net',
    'search_url': 'https://www.venturesquare.net/?s={keyword}'
}

HEADERS = {'User-Agent': 'Mozilla/5.0'}

print("=" * 60)
print("1단계 테스트 (벤처스퀘어, 10개 기업)")
print("=" * 60)

with open('sensible_companies_2026_01_COMPLETE.csv', 'r', encoding='utf-8') as f:
    companies = list(csv.DictReader(f))[:10]

found = 0

for idx, row in enumerate(companies, 1):
    company = row['기업명']
    print(f"[{idx}/10] {company}...", end=' ')

    try:
        url = SITE['search_url'].format(keyword=quote(f"{company} 투자"))
        r = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(r.content, 'html.parser')

        links = soup.select('h4.bold a.black, h2 a, h3 a')

        for link in links[:5]:
            title = link.get_text(strip=True)
            if company in title and '투자' in title:
                article_url = link.get('href')
                if not article_url.startswith('http'):
                    article_url = SITE['url'] + article_url

                # 중복 확인
                existing = supabase.table("investment_news_articles").select("id").eq("article_url", article_url).execute()

                if not existing.data:
                    supabase.table("investment_news_articles").insert({
                        "site_number": SITE['number'],
                        "site_name": SITE['name'],
                        "site_url": SITE['url'],
                        "article_title": title,
                        "article_url": article_url,
                        "published_date": "2026-01-27"
                    }).execute()
                    print(f"✅ 저장")
                    found += 1
                else:
                    print(f"⚠️ 중복")
                break
        else:
            print("❌ 못 찾음")

    except Exception as e:
        print(f"❌ {str(e)[:30]}")

print(f"\n{'='*60}")
print(f"결과: {found}개 발견")
print(f"{'='*60}")
