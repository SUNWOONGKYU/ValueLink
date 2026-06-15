#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2차 노이즈 정리 — 회사명 기준 고정밀(실제 회사 보존).
대상: investment_reason 이 비어 있는 deals (비펀딩 후보). 그중 '명백히 회사가 아닌' 행만 삭제.
실행: python cleanup_noise_v2.py [--apply]
"""
import os, re, sys, argparse, codecs
from dotenv import load_dotenv
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# 정확 일치 블록리스트 (정치인/일반어구/기관 약어 등 — 회사 아님)
EXACT = {
    '고창군','이승기','MC몽','공소기각','현근택','김태흠','오세현','머스크',
    '보유 지분','월 매출','기업 가치','기업당','콘텐츠 기업','클라우드 기업','금융지주사',
    '은행·증권사','초기','하반기','올해','연간','전년대비','전년比','전년 대비','유니콘',
    '반도체','아이디어','찬스','사무직','재원','외화','수익률','확신','내년','공공','뷰티',
    '주식에 완패','SNS서','육성에 포커스','빅파마는 왜','괜찮나?','한때 유니콘','미국은 빅테크',
    '호주 중심','호주 신규','美 위협?','오버행은 부담','극과 극','우주제','지구 두','시간당',
    '사람보다 정교해졌다','맛보기편','실현가능성 의문','전세계','초기','주요','연간','공격적',
    'AI·반도체\' 딥테크','등 딥테크','K우주항공','경북 제','네이버 자금','로봇 출하','식료품 배달',
    '데이터센터 공략','대법원 계약','네이버 등에서','현대차 신규','IPTV 회사서','상하이 과학혁신',
    '빈푸드','한국농업기술진흥원','농진원','중진공','콘진원','대덕특구본부','특구재단','경기혁신센터',
    '대구창조경제혁신센터','경산이노베이션아카데미','인제엔젤투자클럽','스케일업허브','서울대기술지주',
    'KVIC','KVI','한국벤처투자','부산의 VC','전북','전북테크노파크','충북도','경주시','구미시','인천시',
    '광양경자청','국립공주대','국립부경대','삼성전자','GM','AWS','벤츠','셀트리온','SK바이오팜','길리어드',
    'LH','MBK','키움證','신한투자증권','한국산업은행','중화텔레콤','브로드컴','경기창조경제혁신센터',
    '재팬 엑스포','오픈이노베이션','제약사','중기부·제약사','유망벤처기업','확장 본격화','롯데GRS',
    '오픈AI·앤스로픽도 쓴다','오픈AI 제쳤다','오픈AI 추월','앤스로픽 몸값','몸값','앤스로픽',
    '머스크의 xAI','데이터브릭스','한국산업은행·IBK기업은행','경기 레벨업','인구소멸위기 청도군',
    '청도군','홍천군','의령군','경산이노베이션아카데미','경과원','지분','확신','마케팅 투자','피터틸',
    '단기임대 리브애니웨어','기업 모티프테크놀로지스','모티프','모티프테크','에이전트 고도화',
    '리걸테크 멘타트','센티언트랩스','센티언트','퓨리오사AI-브로드컴','크래프톤·텐센트','크래프톤서',
    'i-point] 스카이인텔리전스','건설 자동화','신규 자금','신규 FI','美 클래리티법','월가 K-열풍',
    '출범 초기부터','도약 프로그램','딥테크로 진화','역물류’ 케이존','탄소중립 지원','네이버로부터 전략적',
    '상업화 계약','불붙는 스타트업','반도체’ 하이퍼엑셀','한국딥러닝 김지현','AI·사이버보안 인력',
    '제품 산업','파이어플라이 품었다','영화도 진화해야','바이오·AI 두각','엑스페릭스 등서','반짝 히트’였나',
    '한기대 지원기업','美 오이시팜','의왕시 ‘유니콘로드','산업은행 베팅','국민성장펀드가 불붙였다',
    '美 와이스로부터','스타트업 \'브이원씨','주식회사 플라이투','보광인베스트먼트 펀드','서울먹거리센터 기업',
    '특검 "김건희','두핸즈 품고','ICT기업들 러브콜','K콘텐트','콘텐츠 기업','내가 키우지"[월드콘',
    '거래량 부족','신앙테크','육성에 포커스','전략적','오픈 이노베이션','오픈이노베이션',
}
# 접미사 기반(기관/지자체) — 회사명이 이걸로 끝나면 노이즈
SUFFIX = ('군','시청','도청','본부','진흥원','경제자유구역청','테크노파크','창조경제혁신센터')

def is_noise_name(n):
    if not n: return True
    n = n.strip()
    if n in EXACT: return True
    if any(n.endswith(s) for s in SUFFIX): return True
    if re.search(r'(후보|시장|군수|도지사|의원|장관)$', n): return True
    return False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    rows = supabase.table('deals').select('id,company_name,investment_reason').limit(5000).execute().data
    # 사유 비어 있고 + 명백 비회사명
    targets = [r for r in rows if not r.get('investment_reason') and is_noise_name(r['company_name'])]
    print(f"전체 {len(rows)} | 삭제 대상(사유없음+명백노이즈) {len(targets)}")
    for r in targets: print("  ", r['company_name'])
    if not args.apply:
        print(f"\n[DRY] 삭제하려면 --apply. 보존 예정: {len(rows)-len(targets)}")
        return
    deleted = 0
    for r in targets:
        try:
            supabase.table('deals').delete().eq('id', r['id']).execute(); deleted += 1
        except Exception as e:
            print(f"  ⚠️ {r['company_name']} 실패: {str(e)[:60]}")
    print(f"\n✅ {deleted}건 삭제")
    deals = supabase.table('deals').select('id').order('news_date', desc=True).execute().data
    for i, d in enumerate(deals, 1):
        supabase.table('deals').update({'number': i}).eq('id', d['id']).execute()
    print(f"✅ {len(deals)}건 번호 재정렬")

if __name__ == '__main__':
    main()
