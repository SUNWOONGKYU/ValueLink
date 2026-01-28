#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from urllib.parse import urlparse
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def extract_media_from_url(url):
    domain_to_media = {
        'donga.com': '동아일보',
        'it.donga.com': '동아일보',
        'venturesquare.net': '벤처스퀘어',
        'wowtale.net': 'WOWTALE',
        'platum.kr': '플래텀',
        'thevc.kr': '더벨',
        'etnews.com': '전자신문',
        'startuptoday.kr': '스타트업투데이',
        'biz.chosun.com': '조선비즈',
        'bloter.net': '블로터',
        'aitimes.com': 'AI타임스',
        'moneyt오day.co.kr': '머니투데이',
        'etoday.co.kr': '이투데이',
        'moneys.co.kr': '머니S'
    }
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        domain = domain.replace('www.', '')
        
        for key, value in domain_to_media.items():
            if key in domain:
                return value
    except:
        pass
    
    return None

# site_name 수정
deals = supabase.table("deals").select("*").execute()

invalid_sites = ['네이버 뉴스', 'Google News', 'VC 포트폴리오']
updated = 0

for deal in deals.data:
    site_name = deal.get('site_name')
    news_url = deal.get('news_url')
    
    if site_name in invalid_sites and news_url:
        real_media = extract_media_from_url(news_url)
        if real_media:
            supabase.table("deals").update({'site_name': real_media}).eq("id", deal['id']).execute()
            print(f'{deal["company_name"]}: {site_name} → {real_media}')
            updated += 1

print(f'\n총 {updated}개 업데이트 완료')
