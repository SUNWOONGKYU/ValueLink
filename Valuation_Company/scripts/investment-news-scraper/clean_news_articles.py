#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""investment_news_articles 테이블에서 잘못된 뉴스 제거"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# 잘못된 패턴
wrong_patterns = [
    'thevc.kr',
    '기업정보',
    'THE VC',
    'the Vc',
    'VC 포트폴리오',
]

# 전체 뉴스 조회
articles = supabase.table("investment_news_articles").select("*").execute()

print(f"전체 뉴스: {len(articles.data)}개")

to_delete = []

for article in articles.data:
    url = article.get('article_url', '')
    title = article.get('article_title', '')
    
    should_delete = False
    reason = []
    
    for pattern in wrong_patterns:
        if pattern in url or pattern in title:
            should_delete = True
            reason.append(pattern)
    
    if should_delete:
        to_delete.append({
            'id': article['id'],
            'title': title,
            'reason': ', '.join(reason)
        })

print(f"삭제할 뉴스: {len(to_delete)}개\n")

for item in to_delete[:20]:
    print(f"  {item['title'][:50]}...")
    print(f"  이유: {item['reason']}")
    
    supabase.table("investment_news_articles").delete().eq("id", item['id']).execute()

if len(to_delete) > 20:
    print(f"  ... 외 {len(to_delete) - 20}개")

print(f"\n총 {len(to_delete)}개 삭제 완료")
