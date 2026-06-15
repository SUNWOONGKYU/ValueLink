#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자사유(investment_reason)가 빈 deals를, 각 뉴스 기사(news_url)의 요약에서 추출해 채움.
- 소스: og:description / meta description / 본문 첫 문단
- '왜 투자받았나'에 가까운 문장 우선(기술/시장/성장/매출 등 키워드) → 없으면 요약 첫 문장
- Gemini 불필요 (HTTP + 파싱)

실행:
  python fill_investment_reason.py --limit 5 --dry   # 샘플 미리보기
  python fill_investment_reason.py                    # 전체 채움
"""
import os, re, sys, time, argparse, codecs
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

REASON_KW = ['기술', '시장', '성장', '매출', '개발', '플랫폼', '서비스', '솔루션', '특허',
             '수요', '확장', '글로벌', '경쟁력', '점유율', '고객', '가입자', '거래액', '흑자', 'AI']

def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()

def split_sentences(text):
    # 한국어 문장 분리(다./요./음. 등 종결 + 마침표)
    parts = re.split(r'(?<=[다요음임])\.\s|(?<=\.)\s|(?<=\!)\s|(?<=\?)\s', text)
    return [p.strip() for p in parts if len(p.strip()) >= 10]

def extract_reason(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.content, 'html.parser')
        desc = ''
        for sel in [('meta', {'property': 'og:description'}), ('meta', {'name': 'description'})]:
            el = soup.find(*sel)
            if el and el.get('content'):
                desc = clean(el.get('content'))
                break
        if not desc:
            ps = soup.find_all('p')
            desc = clean(' '.join(p.get_text() for p in ps[:5]))
        if not desc or len(desc) < 15:
            return None
        sents = split_sentences(desc)
        if not sents:
            return desc[:150]
        # 사유 키워드 포함 문장 우선
        for s in sents:
            if any(k in s for k in REASON_KW):
                return s[:200]
        return sents[0][:200]
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0, help='처리 건수 제한(0=전체)')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    # 투자사유 빈 + news_url 있는 deals
    rows = supabase.table('deals').select('id,company_name,news_url,investment_reason') \
        .is_('investment_reason', 'null').not_.is_('news_url', 'null').limit(2000).execute().data
    if args.limit:
        rows = rows[:args.limit]
    print(f"📊 투자사유 빈 deals(뉴스URL 보유): {len(rows)}건 처리{' [DRY]' if args.dry else ''}")

    filled = 0
    for r in rows:
        reason = extract_reason(r['news_url'])
        if reason:
            filled += 1
            print(f"  [{filled}] {r['company_name']}: {reason[:80]}")
            if not args.dry:
                try:
                    supabase.table('deals').update({'investment_reason': reason}).eq('id', r['id']).execute()
                except Exception as e:
                    print(f"      ⚠️ 업데이트 실패: {str(e)[:80]}")
        else:
            print(f"  -  {r['company_name']}: (요약 추출 실패)")
        time.sleep(0.2)
    print(f"\n📊 완료: {filled}/{len(rows)}건 투자사유 채움{' (DRY—미저장)' if args.dry else ''}")

if __name__ == '__main__':
    main()
