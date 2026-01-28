#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""잘못된 뉴스 URL/제목 제거"""
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
    ('thevc.kr', 'URL'),
    ('기업정보', 'title'),
    ('- THE VC', 'title'),
    ('- the Vc', 'title'),
    ('Google News', 'title'),
]

deals = supabase.table("deals").select("*").execute()

removed = 0

for deal in deals.data:
    url = deal.get('news_url') or ''
    title = deal.get('news_title') or ''
    
    should_remove = False
    
    for pattern, field_type in wrong_patterns:
        if field_type == 'URL' and pattern in url:
            should_remove = True
            break
        elif field_type == 'title' and pattern in title:
            should_remove = True
            break
    
    if should_remove:
        print(f"{deal['company_name']}: {title[:50]}...")
        
        supabase.table("deals").update({
            'news_url': None,
            'news_title': None,
            'site_name': None
        }).eq("id", deal['id']).execute()
        
        removed += 1

print(f"\n총 {removed}개 제거 완료")
