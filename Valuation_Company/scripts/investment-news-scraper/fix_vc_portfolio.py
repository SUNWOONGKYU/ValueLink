#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE VC 포트폴리오 페이지를 가진 Deal 제거 또는 수정"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# VC 포트폴리오 URL을 가진 Deal 찾기
deals = supabase.table("deals").select("*").eq("site_name", "VC 포트폴리오").execute()

print(f"VC 포트폴리오 Deal: {len(deals.data)}개")

for deal in deals.data:
    company = deal['company_name']
    print(f"\n{company}:")
    print(f"  현재 URL: {deal['news_url']}")
    
    # news_url과 news_title을 NULL로 설정
    supabase.table("deals").update({
        'news_url': None,
        'news_title': None,
        'site_name': None
    }).eq("id", deal['id']).execute()
    
    print(f"  ✅ news_url, news_title, site_name을 NULL로 설정")

print(f"\n총 {len(deals.data)}개 수정 완료")
