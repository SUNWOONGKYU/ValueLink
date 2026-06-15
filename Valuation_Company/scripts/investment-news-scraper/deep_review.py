#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
심층 재심사 — investment_reason 가 빈 deals를 재검토.
  - 깊은 펀딩 판정으로 '진짜 투자유치 기사'면 사유 채워 보존
  - 펀딩 기사가 아니면(투자사유 발견 불가) 삭제
요약은 reasons_input.json 캐시 우선, 없으면 news_url 재조회.
실행: python deep_review.py [--apply]
"""
import os, re, sys, json, time, argparse, codecs
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
CACHE = {}
p = os.path.join(os.path.dirname(__file__), 'reasons_input.json')
if os.path.exists(p):
    for x in json.load(open(p, encoding='utf-8')):
        if x.get('summary'):
            CACHE[x['id']] = x['summary']

def clean(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()

def fetch_summary(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if r.status_code != 200: return ''
        soup = BeautifulSoup(r.content, 'html.parser')
        for sel in [('meta', {'property': 'og:description'}), ('meta', {'name': 'description'})]:
            el = soup.find(*sel)
            if el and el.get('content'): return clean(el.get('content'))[:300]
        ps = soup.find_all('p')
        return clean(' '.join(x.get_text() for x in ps[:5]))[:300]
    except Exception:
        return ''

# 깊은 펀딩 신호(놓쳤던 표현 포함)
FUND = re.compile(
    r'(투자\s*유치|유치했다|유치에\s*성공|투자를?\s*(유치|단행|받|마무리|완료)|'
    r'(자금|투자금)\s*(을|를)?\s*(유치|조달|확보)|자금\s*조달|신규\s*자금|'
    r'(시드|시리즈\s*[A-Ea-e]|프리\s*[A-Ea-e]|프리시리즈|브릿지|라운드)\s*(투자|펀딩)?.{0,12}(유치|조달|완료|마무리|클로징|성공|진행)|'
    r'\d[\d,\.]*\s*(억원?|만?\s*달러|억\s*달러|엔).{0,18}(유치|조달|투자|규모)|'
    r'전략적\s*투자|지분\s*투자|시드\s*투자|프리\s*시리즈|시리즈\s*[A-Ea-e]\s*라운드|투자\s*라운드.{0,8}(완료|마무리|성공)|'
    r'베팅했다|투자했다고)')
# 펀딩 아님(우선 제외)
NOT_FUND = ['선거','후보','출정식','도지사','군수','시장 후보','공약','내란','민주당','국민의힘','출마',
            '무죄','공소기각','전세금','폭로','녹취','구속','횡령','벌금','제재','소송',
            '무상증자','회생','파산','상장 준비','IPO','공모주','공모가','수요예측','청약','코스닥 상장',
            '인수합병','M&A 가능','매각','수상','선정됐다','선정된','참가 기업','참여 기업','모집','출시했다',
            '업무협약','MOU','오픈 이노베이션','오픈이노베이션','지원사업','액셀러레이팅','펀드 조성',
            '펀드를 조성','플랫폼 가동','협약','클러스터 입주','산업단지','테크노파크','수상했다','개최',
            '주가','시간외','레버리지','발행어음','채권 발행','무상','분할']

REASON_KW = ['기술','시장','성장','매출','개발','플랫폼','서비스','솔루션','특허','진출','확대',
             '계획','고도화','AI','인공지능','제품','글로벌','경쟁력','모델','사업','데이터','로봇']

def sentences(t):
    return [p.strip() for p in re.split(r'(?<=[다요음임])\.\s|(?<=\.)\s|(?<=\!)\s|(?<=\?)\s', t) if len(p.strip()) >= 12]

def is_funding(s):
    if not s or len(s) < 20: return False
    if any(x in s for x in NOT_FUND): return False
    return bool(FUND.search(s))

def pick_reason(s, company):
    sents = sentences(clean(s))
    for x in sents:
        if company[:3] in x and any(k in x for k in REASON_KW): return x[:200]
    for x in sents:
        if any(k in x for k in REASON_KW): return x[:200]
    return sents[0][:200] if sents else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    rows = [r for r in supabase.table('deals').select('id,company_name,news_url,investment_reason,amount,stage').limit(5000).execute().data
            if not r.get('investment_reason')]
    print(f"📊 사유 없는 deals 재심사: {len(rows)}건")

    def has_deal_data(r):
        if r.get('amount') not in (None, 0):
            return True
        st = (r.get('stage') or '').strip()
        return st not in ('', 'TBD', 'unknown', '-')

    to_fill, to_keep, to_delete = [], [], []
    for r in rows:
        s = CACHE.get(r['id']) or (fetch_summary(r['news_url']) if r.get('news_url') else '')
        if not CACHE.get(r['id']) and r.get('news_url'):
            time.sleep(0.1)
        funding = is_funding(s)
        if funding:
            reason = pick_reason(s, r['company_name'])
            if reason: to_fill.append((r, reason)); continue
        # 금액/단계가 있으면 진짜 투자 딜 → 보존(사유는 비워둘 수 있음)
        if has_deal_data(r):
            to_keep.append(r); continue
        to_delete.append(r)
    print(f"  → 보존(금액/단계 보유, 사유 비어도 유지): {len(to_keep)}건")
    print(f"  → 펀딩 재확인(사유채움·보존): {len(to_fill)}건")
    print(f"  → 비펀딩(삭제): {len(to_delete)}건")
    print("\n[보존/채움 샘플]")
    for r, reason in to_fill[:20]: print(f"  +{r['company_name']}: {reason[:55]}")
    print("\n[삭제 샘플]")
    for r in to_delete[:30]: print(f"  -{r['company_name']}")
    if not args.apply:
        print("\n[DRY] 적용하려면 --apply"); return
    for r, reason in to_fill:
        try: supabase.table('deals').update({'investment_reason': reason}).eq('id', r['id']).execute()
        except Exception: pass
    d = 0
    for r in to_delete:
        try: supabase.table('deals').delete().eq('id', r['id']).execute(); d += 1
        except Exception: pass
    print(f"\n✅ 사유 채움 {len(to_fill)} | 삭제 {d}")
    deals = supabase.table('deals').select('id').order('news_date', desc=True).execute().data
    for i, x in enumerate(deals, 1):
        supabase.table('deals').update({'number': i}).eq('id', x['id']).execute()
    print(f"✅ {len(deals)}건 재정렬")

if __name__ == '__main__':
    main()
