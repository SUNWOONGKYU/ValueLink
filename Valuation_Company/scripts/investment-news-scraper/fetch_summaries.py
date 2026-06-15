#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자사유 빈 deals의 기사 요약(og:description/본문)을 수집해 JSON으로 저장.
Claude Code(구독)가 이 JSON을 읽고 투자사유를 생성하기 위한 입력.
출력: reasons_input.json  [{id, company, news_date, summary}]
"""
import os, re, sys, time, json, codecs
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
OUT = os.path.join(os.path.dirname(__file__), 'reasons_input.json')

def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()

def summary(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if r.status_code != 200:
            return ''
        soup = BeautifulSoup(r.content, 'html.parser')
        for sel in [('meta', {'property': 'og:description'}), ('meta', {'name': 'description'})]:
            el = soup.find(*sel)
            if el and el.get('content'):
                return clean(el.get('content'))[:300]
        ps = soup.find_all('p')
        return clean(' '.join(p.get_text() for p in ps[:5]))[:300]
    except Exception:
        return ''

def main():
    rows = supabase.table('deals').select('id,company_name,news_url,news_date') \
        .is_('investment_reason', 'null').not_.is_('news_url', 'null').limit(2000).execute().data
    print(f"📊 대상 {len(rows)}건 요약 수집...")
    out = []
    for i, r in enumerate(rows, 1):
        s = summary(r['news_url'])
        out.append({'id': r['id'], 'company': r['company_name'],
                    'news_date': r.get('news_date'), 'summary': s})
        if i % 50 == 0:
            print(f"  {i}/{len(rows)}")
        time.sleep(0.15)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    got = sum(1 for x in out if x['summary'])
    print(f"✅ 저장: {OUT} ({got}/{len(out)}건 요약 확보)")

if __name__ == '__main__':
    main()
