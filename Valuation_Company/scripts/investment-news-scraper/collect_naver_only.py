#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naver 검색 API 전용 투자뉴스 수집기 (Gemini 불필요)
- Naver 뉴스 검색(title+description+pubDate) → 투자뉴스 필터 → 규칙 기반 추출 → deals 등록
- 추출: 회사명/투자금액(억)/투자단계/투자자/업종/지역  (.claude/rules/08_article-selection.md 기준)
- 회사별 최고 점수 기사 1건만 등록, 기존 deals와 점수 비교

실행: python collect_naver_only.py [--days N] [--dry]
  --days N : 최근 N일 뉴스만 (기본 3)
  --dry    : DB 저장 없이 추출 결과만 출력
"""
import os
import re
import sys
import time
import argparse
import codecs
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlparse
from dotenv import load_dotenv
import requests
from supabase import create_client

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
NAVER_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_SECRET = os.getenv('NAVER_CLIENT_SECRET')

SEARCH_KEYWORDS = ['투자 유치', '시리즈A 투자', '시리즈B 투자', '시리즈C 투자', '시드 투자',
                   '프리A 투자', '벤처투자 유치', '스타트업 투자유치', '프리시리즈A',
                   '투자 유치 스타트업', '억원 투자 유치', '시리즈 투자', '투자금 유치',
                   '벤처캐피탈 투자', '신규 투자 유치', '브릿지 투자']

# ── 추출 헬퍼 (규칙 08 키워드) ──
def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s or '').replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").strip()

AMOUNT_CAP = 9999   # 억. 1조(10000억) 이상은 한국 스타트업 라운드로 비현실적 → 오파싱 처리

# 비딜 컨텍스트 키워드 — 이 단어가 제목/본문에 있으면 금액을 None으로 취급
AMOUNT_NOISE_CONTEXT = (
    '몸값', '펀드 결성', '펀드결성', '기업가치', '기업 가치',
    '앤스로픽', '오픈AI', '오픈에이아이', '오픈 AI',
    'ChatGPT', 'Anthropic', 'OpenAI',
    '서울 1조', '시총', '시가총액', '운용 규모', '운용규모',
    '스케일업 펀드', '모태펀드', '성장금융', '정책펀드',
)

def extract_amount(text):
    """투자금액 → 억원 단위 정수. 없으면 None.
    - 1조(10000억) 이상은 오파싱으로 보고 None 반환
    - 비딜 컨텍스트(몸값/펀드결성/앤스로픽 등) 키워드가 있으면 None 반환
    """
    # 비딜 컨텍스트 선제 차단
    for kw in AMOUNT_NOISE_CONTEXT:
        if kw.lower() in text.lower():
            return None

    val = None
    # 조 단위: 파싱은 하되 상한 검사에서 걸림
    m = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*조\s*(\d[\d,]*)?\s*억?', text)
    if m:
        jo = float(m.group(1).replace(',', ''))
        eok = float(m.group(2).replace(',', '')) if m.group(2) else 0
        val = int(jo * 10000 + eok)
    if val is None:
        # 억 단위 (콤마 천단위만 허용 — '160000' 같은 비정상 연속숫자 배제)
        m = re.search(r'(\d{1,3}(?:,\d{3})*|\d{1,5})\s*억\s*원?', text)
        if m:
            val = int(float(m.group(1).replace(',', '')))
    if val is None:
        # 만 달러 / 달러
        m = re.search(r'(\d[\d,]*\.?\d*)\s*만\s*달러', text)
        if m:
            val = int(float(m.group(1).replace(',', '')) * 1.35)  # 만달러 → 억(≈1.35억/백만달러*0.01)
        else:
            m = re.search(r'(\d[\d,]*\.?\d*)\s*억\s*달러', text)
            if m:
                val = int(float(m.group(1).replace(',', '')) * 135)
    if val is not None and (val <= 0 or val > AMOUNT_CAP):
        return None
    return val

def extract_stage(text):
    patterns = [
        (r'시리즈\s*([A-Ea-e])', lambda m: f'시리즈{m.group(1).upper()}'),
        (r'series\s*([A-Ea-e])', lambda m: f'시리즈{m.group(1).upper()}'),
        (r'프리\s*[-]?\s*([A-Ea-e])|pre[-\s]*([A-Ea-e])', lambda m: '프리A'),
        (r'시드|seed', lambda m: '시드'),
        (r'브릿지|bridge', lambda m: '브릿지'),
        (r'프리시리즈|프리\s*시리즈', lambda m: '프리A'),
    ]
    for pat, fn in patterns:
        mm = re.search(pat, text, re.IGNORECASE)
        if mm:
            return fn(mm)
    return None

def extract_investors(text):
    # VC/투자사 명칭 패턴
    found = re.findall(r'([가-힣A-Za-z0-9]+(?:벤처스|인베스트먼트|캐피탈|벤처투자|자산운용|파트너스|인베스트|벤처캐피탈|VC|투자조합))', text)
    # 한 글자 등 노이즈 제거, 중복 제거
    inv = []
    for f in found:
        f = f.strip()
        if len(f) >= 3 and f not in inv:
            inv.append(f)
    return ', '.join(inv[:5]) if inv else None

INDUSTRY_MAP = {
    'AI': ['AI', '인공지능', '머신러닝', 'LLM', '생성형'],
    '헬스케어': ['헬스케어', '의료', '바이오', '디지털헬스', '제약', '진단'],
    '핀테크': ['핀테크', '금융', '결제', '페이', '대출', '보험'],
    '푸드테크': ['푸드테크', '식품', '외식', '배달'],
    '이커머스': ['이커머스', '커머스', '쇼핑', '리테일'],
    '모빌리티': ['모빌리티', '자율주행', '드론', '로보틱스', '로봇'],
    '콘텐츠': ['콘텐츠', '게임', '엔터', '미디어', '웹툰'],
    'SaaS': ['SaaS', '솔루션', '플랫폼', 'B2B'],
    '교육': ['교육', '에듀테크', '에듀'],
    '에너지': ['에너지', '배터리', '친환경', '기후'],
}
def extract_industry(text):
    for cat, kws in INDUSTRY_MAP.items():
        for kw in kws:
            if kw.lower() in text.lower():
                return cat
    return None

LOCATIONS = ['판교', '강남', '서울', '부산', '대구', '광주', '대전', '인천', '성남', '경기', '제주', '세종']
def extract_location(text):
    for loc in LOCATIONS:
        if loc in text:
            return loc
    return None

def extract_company(title):
    t = title.strip()
    # 선행 태그/꼭지 제거: [단독], 현장 줌인] 처럼 ']'로 끝나는 선행 꼭지
    t = re.sub(r'^[\[\【][^\]\】]*[\]\】]\s*', '', t)
    t = re.sub(r'^[^\[\]]{0,20}[\]\】]\s*', '', t)  # 여는 괄호 없이 'OOO]' 형태
    # 서술 클로즈 뒤 회사명: '…', '·', ':' 뒤를 우선 (예: "성장세에…스캐터랩, 500억")
    for sep in ['…', '...', '·', ' - ', ':']:
        if sep in t:
            tail = t.split(sep)[-1].strip()
            if tail:
                t = tail
                break
    t = t.strip().strip("'\"‘’“”")
    t = re.sub(r'^(스타트업|AI|딥테크|바이오|핀테크|글로벌)\s+', '', t)  # 선행 수식어 제거
    # 첫 콤마 앞
    if ',' in t:
        cand = t.split(',')[0].strip()
    else:
        cand = re.split(r'\s*(?:\d|시리즈|시드|프리|투자|유치|펀딩|조달|억|조|\(|‘|“)', t)[0].strip()
    cand = re.sub(r'\(대표[^)]*\)', '', cand)
    cand = cand.strip("'\"‘’“”()[]…· ")
    return cand if _valid_company(cand) else None

# 일반명사/기관/기사용어 — 회사명 아님
NOISE_COMPANY = {
    'AI', '서울시', '정부', '삼성', '쿠팡', '스페이스X', '미국', '국내', '스타트업', '벤처',
    '투자', '딥테크', '바이오', '핀테크', '기업가치', '기업', '회사', '대표', 'LVMH', '구글',
    '네이버', '카카오', '의료AI', '헤어케어 브랜드', '글로벌', '국가', '한국', '중국', '일본',
    'VC', '펀드', '정책', '시장', '업계', '신규', '최대', '역대',
    # 결함2 보완: 비회사명 구절 추가
    '확장 계획', '국가난제 해결', '인천 스타트업', '소속사', 'IRR',
    '앤스로픽', '오픈AI', '오픈에이아이', '몸값', '펀드 결성', '펀드결성',
    '서울', '경기', '인천', '부산', '대구', '광주',  # 지역명 단독 제외
}
# 회사명에 들어가면 안 되는 조사/서술 어미·동사 흔적
BAD_TOKENS = ('잡나', '노린다', '개발중', '도전', '나선', '성과', '의혹', '잇나', '뚫는', '쑥',
              '한다', '했다', '된다', '울린', '맞은', '앞둔', '두고', '관련', '위해', '담은',
              '참여', '유치', '확보', '돌입', '추진', '나서', '밝혀', '공개',
              # 결함2 보완: 기사 제목에 자주 나오는 서술구 토큰
              '계획', '해결', '본격화', '강화', '성장', '진출', '선정', '출범')
EXTRA_NOISE2 = {'매출', '신규 자금', '젠슨 황', '양동', '신규', '자금', '투자사', '신규 투자',
                '대규모', '누적', '추가', '기관', '복수', '국내외'}

VC_SUFFIX = ('벤처스', '인베스트먼트', '캐피탈', '벤처투자', '파트너스', '자산운용', '벤처캐피탈', '인베스트')
EXTRA_NOISE = {'미래에셋', 'MS', '캠코', '양보다 질', '직접', '동남권', '도면 AI', '네이버 D',
               '비트코인', '한국벤처투자', '신한', 'KB', '산업은행', '기보', '신보'}

# 회사명으로 볼 수 없는 접미사 패턴 (지자체·기관·행정구역)
BAD_SUFFIX_RE = re.compile(
    r'(군$|시청$|도청$|본부$|진흥원$|경제자유구역청$|테크노파크$|창조경제혁신센터$'
    r'|혁신센터$|엑셀러레이터$|인큐베이터$|지원센터$|협회$|연합회$|연구원$|연구소$)',
)

def _valid_company(cand):
    if not cand or not (1 < len(cand) <= 20):
        return False
    if cand in NOISE_COMPANY or cand in EXTRA_NOISE or cand in EXTRA_NOISE2:
        return False
    if cand.count(' ') >= 2:                 # 문장형 제외 (공백 2개 이상 = 구/문장)
        return False
    if re.search(r'[0-9.]', cand):           # 숫자/마침표(잘린 제목) 제외
        return False
    if '(' in cand and ')' not in cand:      # 괄호 잘림 제외
        return False
    if cand.endswith(VC_SUFFIX):             # 투자사명이 회사로 오인된 경우 제외
        return False
    if BAD_SUFFIX_RE.search(cand):           # 결함2: 기관/지자체 접미사 제외
        return False
    if any(b in cand for b in BAD_TOKENS):
        return False
    if cand.endswith(('은', '는', '이', '가', '의', '를', '을', '에', '도', '로', '와', '과')):
        return False                         # 조사로 끝나면 문장 일부
    # 결함2: 한 글자 이하(len>1 이미 체크됨) 또는 완전 한글 일반명사 패턴
    # 2글자인데 단순 2자 한글 일반어(시장, 기업, 투자, 성장 등)는 BAD_TOKENS 또는 NOISE_COMPANY에서 처리
    return True

# 비투자(펀딩 아님) 기사 제외 키워드
EXCLUDE = ['과징금', '공모주', '공모가', '수요예측', '상장', 'IPO', '소송', '파산', '회수',
           '매각', '인수합병', 'M&A', '벌금', '제재', '횡령', '구속', '논란', '후폭풍',
           '코스닥', '코스피', '청약', '배당', '실적', '주가', '시총',
           # 결함1 보완: 펀드결성·몸값·해외 대형 라운드는 딜이 아님
           '펀드 결성', '펀드결성', '몸값', '기업 가치', '기업가치',
           '앤스로픽', '오픈AI', '오픈에이아이', '오픈 AI',
           '인천 스타트업', '국가난제', '소속사', 'IRR',
           # 펀드 조성 관련 (투자자 측 행위, 딜 아님)
           '펀드 조성', '펀드조성', '벤처펀드 조성', '모태펀드', '정책펀드']

def is_investment_news(text):
    if any(x in text for x in EXCLUDE):
        return False
    has_invest = ('투자 유치' in text or '투자유치' in text or '유치' in text
                  or '펀딩' in text or '투자를 유치' in text or '조달' in text)
    has_money_or_stage = bool(re.search(r'\d\s*억|\d\s*조|달러|시리즈|시드|프리\s*[A-Ea-e]|라운드', text))
    return has_invest and has_money_or_stage

def calc_score(info):
    s = 0
    if info.get('amount'): s += 3
    if info.get('investors'): s += 3
    if info.get('stage'): s += 2
    if info.get('industry'): s += 1
    if info.get('location'): s += 1
    return s

def site_from_url(url):
    try:
        host = urlparse(url).netloc.replace('www.', '')
        return host or '미디어'
    except Exception:
        return '미디어'

# ── 메인 ──
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=3)
    ap.add_argument('--since', type=str, default=None, help='백필: 이 날짜(YYYY-MM-DD) 이후 전부 수집 (페이지네이션)')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    KST = timezone(timedelta(hours=9))
    if args.since:
        floor_date = args.since
        backfill = True
        print(f"📰 Naver 백필 수집 시작 ({floor_date} 이후, 페이지네이션){' [DRY]' if args.dry else ''}")
    else:
        floor_date = (datetime.now(KST) - timedelta(days=args.days)).strftime('%Y-%m-%d')
        backfill = False
        print(f"📰 Naver 전용 수집 시작 (최근 {args.days}일, {floor_date} 이후){' [DRY]' if args.dry else ''}")

    headers = {'X-Naver-Client-Id': NAVER_ID, 'X-Naver-Client-Secret': NAVER_SECRET}
    collected, seen_urls = [], set()
    oldest_seen = None

    # Naver API: display 최대 100, start 최대 1000 → 키워드당 최대 1000건. 백필 시 깊게 페이지네이션.
    starts = list(range(1, 1001, 100)) if backfill else [1]
    display = 100 if backfill else 50

    def process_item(it):
        nonlocal oldest_seen
        link = it.get('originallink') or it.get('link', '')
        if not link or link in seen_urls:
            return None
        pub = it.get('pubDate', '')
        try:
            d = datetime.strptime(pub[:25].strip(), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
        except Exception:
            return None
        if oldest_seen is None or d < oldest_seen:
            oldest_seen = d
        if d < floor_date:
            return d
        title = strip_tags(it.get('title', ''))
        desc = strip_tags(it.get('description', ''))
        text = f"{title} {desc}"
        if not is_investment_news(text):
            seen_urls.add(link)
            return d
        seen_urls.add(link)
        company = extract_company(title)
        if not company:
            return d
        info = {
            'company_name': company,
            'amount': extract_amount(text),
            'stage': extract_stage(text),
            'investors': extract_investors(text),
            'industry': extract_industry(text),
            'location': extract_location(text),
            'news_title': title, 'news_url': link, 'news_date': d,
            'site_name': site_from_url(link),
        }
        info['_score'] = calc_score(info)
        collected.append(info)
        return d

    for kw in SEARCH_KEYWORDS:
        try:
            for st in starts:
                url = f"https://openapi.naver.com/v1/search/news.json?query={quote(kw)}&sort=date&display={display}&start={st}"
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    print(f"  ⚠️ Naver {kw} start={st}: {r.status_code}")
                    break
                items = r.json().get('items', [])
                if not items:
                    break
                page_dates = [process_item(it) for it in items]
                page_dates = [d for d in page_dates if d]
                # 이 페이지가 전부 floor_date 이전이면 더 과거이므로 중단(최신순 정렬)
                if backfill and page_dates and all(d < floor_date for d in page_dates):
                    break
                if backfill:
                    time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ {kw} 오류: {str(e)[:80]}")

    print(f"📊 투자뉴스 후보: {len(collected)}건 (검색이 닿은 가장 과거 기사일: {oldest_seen})")

    # 회사별 최고 점수 1건
    best = {}
    for c in collected:
        name = c['company_name']
        if name not in best or c['_score'] > best[name]['_score']:
            best[name] = c
    print(f"📊 회사 수(중복 제거): {len(best)}")

    if args.dry:
        confident = [c for c in best.values() if c.get('amount') or c.get('investors')]
        print(f"📊 고신뢰(금액/투자자 보유): {len(confident)}건")
        for c in sorted(confident, key=lambda x: -x['_score']):
            print(f"  [{c['_score']}] {c['company_name']} | {c.get('amount')}억 | {c.get('stage')} | {c.get('industry')} | {c.get('investors')}")
        print("DRY 모드 — 저장 안 함")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    existing = supabase.table('deals').select('news_url,company_name').execute()
    existing_urls = {d['news_url'] for d in existing.data if d.get('news_url')}
    existing_companies = {d['company_name'] for d in existing.data if d.get('company_name')}

    # 신뢰도 게이트: 금액 또는 투자자(3점 항목) 중 하나 이상 있어야 저장
    confident = [c for c in best.values() if c.get('amount') or c.get('investors')]
    print(f"📊 고신뢰(금액/투자자 보유): {len(confident)}건")

    inserted = 0
    for c in confident:
        if c['news_url'] in existing_urls or c['company_name'] in existing_companies:
            continue
        rec = {k: c[k] for k in ('company_name', 'amount', 'stage', 'investors', 'industry',
                                 'location', 'news_title', 'news_url', 'news_date', 'site_name')
               if c.get(k) is not None}
        if c.get('industry'):
            from_cat = c['industry']
            rec['industry_category'] = from_cat
        try:
            supabase.table('deals').insert(rec).execute()
            inserted += 1
            print(f"  ✅ [{inserted}] {c['news_date']} | {c['company_name']} | {c.get('amount')}억 | {c.get('stage')} | 점수{c['_score']}")
        except Exception as e:
            print(f"  ⚠️ 저장 실패({c['company_name']}): {str(e)[:120]}")

    print(f"\n📊 완료! 신규 {inserted}건 등록")

    # 번호 재정렬 (최신순)
    if inserted:
        deals = supabase.table('deals').select('id').order('news_date', desc=True).execute()
        for idx, d in enumerate(deals.data, 1):
            supabase.table('deals').update({'number': idx}).eq('id', d['id']).execute()
        print(f"✅ {len(deals.data)}건 번호 재정렬 완료")


if __name__ == '__main__':
    main()
