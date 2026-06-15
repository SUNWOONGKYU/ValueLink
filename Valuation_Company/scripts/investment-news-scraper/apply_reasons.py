#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reasons_input.json(캐시된 기사 요약)에서, '진짜 투자유치 기사'인 건만 골라
투자사유 1문장을 추출해 deals.investment_reason 업데이트.
- 펀딩 기사 아님(기관/선거/IPO/M&A/일반)은 건너뜀(비워둠) → 별도 노이즈 후보로 집계
실행: python apply_reasons.py [--dry]
"""
import os, re, sys, json, argparse, codecs
from dotenv import load_dotenv
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
INP = os.path.join(os.path.dirname(__file__), 'reasons_input.json')

# 진짜 '투자 유치' 기사 신호
FUND_RE = re.compile(r'(투자\s*유치|투자를?\s*유치|시리즈\s*[A-Ea-e].{0,8}(유치|투자|마무리|완료)|'
                     r'시드\s*투자|프리\s*[A-Ea-e].{0,6}투자|프리시리즈|규모의?\s*(시리즈|시드|프리|투자).{0,6}(유치|조달|완료)|'
                     r'\d+\s*(억원?|만?\s*달러).{0,12}(유치|조달))')
# 펀딩 아님(제외)
NOT_FUND = ['선거', '후보', '출정식', '시장 후보', '도지사', '군수', '공약', '무죄', '공소기각',
            '전세금', '폭로', '무상증자', '유상증자' , '회생', '파산', '상장', 'IPO', '인수합병',
            'M&A', '소멸위기', '산업단지', '지원사업', '액셀러레이팅', '모집', '선정됐다', '수상',
            'MOU', '업무협약', '오픈 이노베이션', '오픈이노베이션', '펀드 조성', '펀드를', '플랫폼 가동']

REASON_KW = ['기술', '시장', '성장', '매출', '개발', '플랫폼', '서비스', '솔루션', '특허', '진출',
             '확대', '계획', '고도화', 'AI', '인공지능', '제품', '글로벌', '경쟁력', '모델', '사업']

def clean(s): return re.sub(r'\s+', ' ', s or '').strip()

def sentences(t):
    parts = re.split(r'(?<=[다요음임])\.\s|(?<=\.)\s|(?<=\!)\s|(?<=\?)\s', t)
    return [p.strip() for p in parts if len(p.strip()) >= 12]

def is_funding(summary, company):
    if not summary or len(summary) < 20:
        return False
    if any(x in summary for x in NOT_FUND):
        return False
    return bool(FUND_RE.search(summary))

def pick_reason(summary, company):
    sents = sentences(clean(summary))
    if not sents:
        return None
    # 회사명 포함 + 사유 키워드 문장 우선
    for s in sents:
        if company[:4] in s and any(k in s for k in REASON_KW):
            return s[:200]
    for s in sents:
        if any(k in s for k in REASON_KW):
            return s[:200]
    return sents[0][:200]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()
    data = json.load(open(INP, encoding='utf-8'))
    filled, skipped = 0, []
    for x in data:
        if is_funding(x['summary'], x['company']):
            reason = pick_reason(x['summary'], x['company'])
            if reason:
                filled += 1
                if filled <= 40:
                    print(f"  [채움] {x['company']}: {reason[:70]}")
                if not args.dry:
                    try:
                        supabase.table('deals').update({'investment_reason': reason}).eq('id', x['id']).execute()
                    except Exception as e:
                        print(f"    ⚠️ {x['company']} 실패: {str(e)[:60]}")
            else:
                skipped.append(x['company'])
        else:
            skipped.append(x['company'])
    print(f"\n📊 사유 채움: {filled}건 | 건너뜀(비펀딩/노이즈 후보): {len(skipped)}건{' [DRY]' if args.dry else ''}")
    # 건너뛴(노이즈 후보) 회사 목록 저장
    with open(os.path.join(os.path.dirname(__file__), 'noise_candidates.json'), 'w', encoding='utf-8') as f:
        json.dump([{'id': x['id'], 'company': x['company']} for x in data
                   if not is_funding(x['summary'], x['company'])], f, ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
