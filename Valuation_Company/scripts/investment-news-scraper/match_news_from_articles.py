#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""investment_news_articles 테이블에서 뉴스 찾아서 Deal 테이블에 매칭"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# news_title이 없는 Deal 조회
deals = supabase.table("deals").select("*").is_("news_title", "null").execute()

print(f"뉴스 제목 없는 Deal: {len(deals.data)}개\n")

matched = 0

for deal in deals.data:
    company = deal['company_name']
    print(f"{company} 검색 중...")
    
    # investment_news_articles에서 기업명으로 검색
    articles = supabase.table("investment_news_articles")\
        .select("*")\
        .ilike("article_title", f"%{company}%")\
        .order("published_date", desc=True)\
        .limit(5)\
        .execute()
    
    if articles.data:
        # 투자유치 관련 키워드가 있는 기사 찾기
        invest_keywords = ['투자', '유치', '펀딩', 'Pre-A', '시리즈', '시드', 'Seed', 'Series']
        
        best_article = None
        for article in articles.data:
            title = article.get('article_title', '')
            
            # 잘못된 패턴 제외
            if any(x in title for x in ['기업정보', 'THE VC', 'Google News', 'VC 포트폴리오']):
                continue
            
            # 투자유치 키워드 확인
            if any(keyword in title for keyword in invest_keywords):
                best_article = article
                break
        
        if best_article:
            print(f"  ✅ 매칭: {best_article['article_title'][:50]}...")
            print(f"     언론: {best_article.get('site_name', '-')}")
            print(f"     날짜: {best_article.get('published_date', '-')}")
            
            supabase.table("deals").update({
                'news_url': best_article['article_url'],
                'news_title': best_article['article_title'],
                'site_name': best_article.get('site_name'),
                'news_date': best_article.get('published_date')
            }).eq("id", deal['id']).execute()
            
            matched += 1
        else:
            print(f"  ⚠️  적절한 뉴스 없음 ({len(articles.data)}개 검색)")
    else:
        print(f"  ❌ 검색 결과 없음")
    
    print()

print(f"총 {matched}개 매칭 완료")
