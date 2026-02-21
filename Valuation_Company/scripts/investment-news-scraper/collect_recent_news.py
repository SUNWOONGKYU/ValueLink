# -*- coding: utf-8 -*-
"""
2월 11일 이후 최신 뉴스 수집 (Gemini quota 최적화)
"""
import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 인코딩
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

import requests
from supabase import create_client

# Supabase 연결
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("📰 2월 11일 이후 최신 투자 뉴스 수집 시작...")

# 1단계: Naver 검색 API로 뉴스 수집 (2월 11일 이후)
print("\n✅ 1단계: Naver 검색 API로 뉴스 수집...")

headers = {
    'X-Naver-Client-Id': NAVER_CLIENT_ID,
    'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
}

keywords = ['투자 유치', '시리즈', '펀딩', '창업', '스타트업 투자']
collected_news = []

for keyword in keywords:
    try:
        url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&sort=date&display=50&start=1"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                pub_date = item.get('pubDate', '')
                if pub_date:
                    try:
                        dt = datetime.strptime(pub_date[:16], "%a, %d %b %Y")
                        date_str = dt.strftime("%Y-%m-%d")
                        
                        if date_str >= "2026-02-11":
                            collected_news.append({
                                'title': item.get('title', '').replace('<b>', '').replace('</b>', ''),
                                'url': item.get('link', ''),
                                'site': item.get('source', ''),
                                'date': date_str,
                                'keyword': keyword
                            })
                    except:
                        pass
        else:
            print(f"⚠️ Naver API 오류 {keyword}: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Naver 검색 오류: {str(e)}")

print(f"📰 수집된 뉴스: {len(collected_news)}개")

# 중복 제거
unique_news = []
seen_urls = set()
for news in collected_news:
    if news['url'] not in seen_urls:
        unique_news.append(news)
        seen_urls.add(news['url'])

print(f"✅ 중복 제거 후: {len(unique_news)}개\n")

# 2단계: 회사명 추출
print("✅ 2단계: 회사명 추출...")

for news in unique_news:
    title = news['title']
    if ',' in title:
        company_name = title.split(',')[0].strip()
        news['company'] = company_name
    else:
        parts = title.split()
        news['company'] = parts[0] if parts else 'Unknown'

# 3단계: Supabase에 저장
print("✅ 3단계: Supabase에 저장...\n")

inserted = 0
for news in unique_news:
    try:
        existing = supabase.table('deals').select('*').eq('news_url', news['url']).execute()
        
        if not existing.data:
            record = {
                'company_name': news.get('company', 'Unknown'),
                'news_title': news['title'],
                'news_url': news['url'],
                'site_name': news['site'],
                'news_date': news['date'],
                'industry': 'TBD',
                'stage': 'TBD'
            }
            
            response = supabase.table('deals').insert(record).execute()
            inserted += 1
            print(f"✅ [{inserted}] {news['date']} | {news.get('company', 'Unknown')} | {news['site']}")
    except Exception as e:
        print(f"⚠️ 저장 실패: {str(e)}")

print(f"\n📊 완료! {inserted}개 새 뉴스 추가됨")

# 4단계: 번호 재정렬
print("\n✅ 4단계: 번호 재정렬...")
try:
    deals = supabase.table('deals').select('id').order('news_date', desc=False).execute()
    
    for idx, deal in enumerate(deals.data, 1):
        supabase.table('deals').update({'number': idx}).eq('id', deal['id']).execute()
    
    print(f"✅ {len(deals.data)}개 레코드 재정렬 완료!")
except Exception as e:
    print(f"⚠️ 재정렬 실패: {str(e)}")

print("\n✅ 모든 작업 완료! 🎉")
