#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deals 테이블에서 회사명이 노이즈(문장형/조사끝/잘린제목/일반어구)인 행을 정리.
기본은 dry(목록만). 실제 삭제는 --apply (파괴적 — 사용자 승인 후에만).

실행:
  python cleanup_noise_deals.py            # 삭제 후보 목록만
  python cleanup_noise_deals.py --apply     # 실제 삭제
"""
import os, re, sys, argparse, codecs
from dotenv import load_dotenv
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

NOISE_TOK = ['지분', '매출', '열풍', '초기', '진화', '프로그램', '지원', '계약', '인력', '산업',
             '두각', '품었', '불붙', '전략적', '완패', '출범', '역물류', '클래리티', '월가',
             '보유', '신규', '자금', '대규모', '누적', '추가', '기관', '복수', '국내외', '참여',
             '확보', '돌입', '추진', '은행', '증권사', '주식', '센터', '협회', '정부', '펀드']
JOSA_END = ('은', '는', '이', '가', '의', '를', '을', '에', '도', '로', '와', '과', '서', '부터', '까지')
VC_SUFFIX = ('벤처스', '인베스트먼트', '캐피탈', '벤처투자', '파트너스', '자산운용', '벤처캐피탈')

def is_noise(n):
    # ⚠️ 단일 토큰(공백 없음) 회사명은 보존 — 한국 회사명은 이/로/가 등으로 끝나는 경우가 흔함
    if not n:
        return True
    n = n.strip()
    if len(n) <= 1:
        return True
    if re.search(r'[‘’“”]', n):                 # 따옴표 잔재
        return True
    if re.search(r'\]', n):                     # '...] OOO' 잘린 꼭지
        return True
    if ' ' not in n:
        return False                            # 단어 1개 = 회사명으로 간주(보존)
    # 이하 공백 포함(여러 단어)인 경우만 노이즈 판정
    if n.count(' ') >= 2:                        # 단어 3개+ = 문장
        return True
    last = n.split(' ')[-1]
    if last.endswith(JOSA_END):                 # 마지막 단어가 조사로 끝 = 문장
        return True
    if any(t in n for t in NOISE_TOK):
        return True
    if re.search(r'(김|이|박|최|정|대표)[가-힣]{1,2}$', n):
        return True                             # 'OOO 김지현' 류 사람이름 꼬리
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    rows = supabase.table('deals').select('id,company_name,news_date').limit(5000).execute().data
    noisy = [r for r in rows if is_noise(r.get('company_name'))]
    print(f"전체 deals: {len(rows)} | 노이즈 판정: {len(noisy)}")
    print("--- 삭제 후보 (회사명) ---")
    for r in noisy:
        print(f"  {r['company_name']}  ({r.get('news_date')})")

    if not args.apply:
        print(f"\n[DRY] 실제 삭제하려면 --apply (승인 후). 보존: {len(rows)-len(noisy)}건")
        return

    print(f"\n🔴 {len(noisy)}건 삭제 시작...")
    deleted = 0
    for r in noisy:
        try:
            supabase.table('deals').delete().eq('id', r['id']).execute()
            deleted += 1
        except Exception as e:
            print(f"  ⚠️ 삭제 실패 {r['company_name']}: {str(e)[:80]}")
    print(f"✅ {deleted}건 삭제 완료")
    # 번호 재정렬
    deals = supabase.table('deals').select('id').order('news_date', desc=True).execute().data
    for idx, d in enumerate(deals, 1):
        supabase.table('deals').update({'number': idx}).eq('id', d['id']).execute()
    print(f"✅ {len(deals)}건 번호 재정렬 완료")

if __name__ == '__main__':
    main()
