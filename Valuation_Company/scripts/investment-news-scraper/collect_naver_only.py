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
        # 부정 선읽기: "1억 달러"·"1억원 달러"가 "1억"으로 오파싱되지 않도록 → 달러 분기로 넘김
        m = re.search(r'(\d{1,3}(?:,\d{3})*|\d{1,5})\s*억\s*원?(?!\s*(?:원\s*)?달러)', text)
        if m:
            val = int(float(m.group(1).replace(',', '')))
    if val is None:
        # 달러 환산 (환율 ≈ 1,350원/달러 기준)
        #  · 백만 달러(1M USD) ≈ 13.5억원
        #  · 만 달러(1만 USD = 0.01M)  → ×0.135억
        #  · 억 달러(1억 USD = 100M)   → ×1,350억
        # 주의: '억 달러'가 '만 달러'의 부분일치가 되지 않도록 억 달러를 먼저 검사
        m = re.search(r'(\d[\d,]*\.?\d*)\s*억\s*달러', text)
        if m:
            val = round(float(m.group(1).replace(',', '')) * 1350)        # 억달러 → 억원
        else:
            m = re.search(r'(\d[\d,]*\.?\d*)\s*만\s*달러', text)
            if m:
                # 만달러 ×0.135억. 0.135 리터럴의 부동소수 오차를 피해 135/1000 정수연산으로 결정론화
                val = round(float(m.group(1).replace(',', '')) * 135 / 1000)
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

# 일반명사/기관/기사용어 — 회사명 아님 (완전 일치만. 부분 포함은 BAD_TOKENS·NON_COMPANY_KEYWORDS로)
NOISE_COMPANY = {
    'AI', '서울시', '정부', '삼성', '쿠팡', '스페이스X', '미국', '국내', '스타트업', '벤처',
    '투자', '딥테크', '바이오', '핀테크', '기업가치', '기업', '회사', '대표', 'LVMH', '구글',
    '네이버', '카카오', '의료AI', '헤어케어 브랜드', '글로벌', '국가', '한국', '중국', '일본',
    'VC', '펀드', '정책', '시장', '업계', '신규', '최대', '역대',
    '확장 계획', '국가난제 해결', '인천 스타트업', '소속사', 'IRR',
    # 앤스로픽은 실제 회사명이므로 NOISE에서 제거 — EXCLUDE(기사 게이트)에서만 처리
    '오픈AI', '오픈에이아이', '몸값', '펀드 결성', '펀드결성',
    '서울', '경기', '인천', '부산', '대구', '광주',  # 지역명 단독 제외
    # 명백한 일반어구/문장조각 (고유명사 토큰 전무)
    '추론', '창업', '외화', '창구', '산단', '반도체',
    '클라우드 기업', '우주 스타트업', '등 딥테크', '유럽기업',
    '사업 확장', '소부장·팹리스 기업', '오가노이드 스타트업', 'VC서 잇따라',
    '유니콘 등극', '지배적 디자인',
    '총력 승리', '한때 유니콘', '호주 중심', '미국은 빅테크',
    '보상률', '항공업계', '공룡들', '복지부', '상생협력기금',
    '포용금융의 미래', '우승팀', '산업계',
    # 대기업/대형사 (투자유치 기사의 피투자사 아님 — 보통 투자자/주체로 오파싱)
    '삼성전자', '두산밥캣', '두산', '넥슨', '혼다', 'CATL', '크래프톤',
    # 일반어/기사조각 완전일치
    '주식계좌', '물리 경제', '기후 위험', '중소게임업체', '세일 리서치', '프로젝트 제타',
    '한국에서', '美 VC들',
    # 대기업/상장사/포털 (투자유치 피투자사 아님)
    'LG전자', '다음', '키움', '한화', '심텍', '글랜우드', '스텔란티스',
    '리가켐바이오', '아미코젠', '수산인더스트리', '韓타이어', 'IMM인베스트',
    # 지역/도시·일반어 단독
    '동탄', '아산', '세계',
}

# 회사명에 들어가면 안 되는 서술 어미·동사 흔적 (완전 포함 검사)
BAD_TOKENS = ('잡나', '노린다', '개발중', '의혹', '잇나', '뚫는', '쑥',
              '한다', '했다', '된다', '울린', '맞은', '앞둔', '두고', '관련', '위해', '담은',
              '참여', '유치', '확보', '돌입', '추진', '나서', '밝혀', '공개',
              '본격화', '해결', '출범',
              # 명백한 동사·조각
              '사줘', '잇따라', '둔화', '활동지수',
              # 기사 동사·서술 조각 (겨냥/인정/가속/잠재력 등)
              '겨냥', '인정', '가속', '잠재력', '돌파', '달성', '주목',
              # 06-27 넓은스캔 기사조각 명사·동사 (실회사명엔 안 나옴)
              '최대', '확대', '확장', '속도', '선도', '발판', '부족', '복귀', '경쟁',
              '첫걸음', '흥행', '열고', '부담', '육성', '협력', '다변화', '인력',
              '도전', '주도', '동맹', '제휴', '존재감', '신작', '카운트다운',
              '신사업', '빅데이터', '공급망', '레버리지', '오버행', '현금흐름',
              '매물', '최대주주', '지배구', '혁신성장', '창업시대', '공소')

EXTRA_NOISE2 = {'매출', '신규 자금', '젠슨 황', '양동', '신규', '자금', '투자사', '신규 투자',
                '대규모', '누적', '추가', '기관', '복수', '국내외',
                # 06-28: 회사명 아닌 기사 명사구 (질병/스포츠팀) 안전망
                # ('한국 기공사 실력'은 NON_COMPANY_KEYWORDS '실력' 부분일치가 커버 — 감사 c07a1232 지적②)
                '복부암', '뉴욕 메츠',
                # 06-29: 금융사 나열 조각 (가운뎃점 1개 — 투자자 나열이 회사명으로 오추출)
                '신한·키움'}

# 투자사 접미사 — 이 접미사만으로 끝나는 후보는 투자사이지 피투자회사 아님
# 단, 충분히 긴(5글자 이상) 고유명사는 실제 회사명일 수 있으므로 6글자 이상은 통과
VC_SUFFIX_RE = re.compile(
    r'(?:인베스트먼트|인베스트|벤처투자|자산운용|벤처캐피탈)$'   # 항상 차단 (IMM인베스트 등 VC 전용 접미사)
)
VC_SUFFIX_SHORT_RE = re.compile(
    r'(?:벤처스|캐피탈|파트너스|인베)$'                         # 6글자 미만이면 차단, 이상이면 통과
)
# 구버전 호환: extract_investors 에서 여전히 tuple 형식으로 참조하므로 유지
VC_SUFFIX = ('벤처스', '인베스트먼트', '캐피탈', '벤처투자', '파트너스', '자산운용', '벤처캐피탈', '인베스트')

EXTRA_NOISE = {'미래에셋', 'MS', '캠코', '양보다 질', '직접', '동남권', '도면 AI', '네이버 D',
               '비트코인', '한국벤처투자', '신한', 'KB', '산업은행', '기보', '신보'}

# 회사명으로 볼 수 없는 접미사 패턴 (지자체·기관·행정구역)
# 주의: '연구소'는 실제 스타트업명에도 쓰임(무인화연구소 등) → 제외
# '군$' 단독은 '산군' 같은 브랜드명도 차단 → 지역명이 앞에 붙은 형태만 차단
BAD_SUFFIX_RE = re.compile(
    r'(?:[가-힣]{2,}군$|시청$|도청$|본부$|진흥원$|경제자유구역청$|테크노파크$'
    r'|창조경제혁신센터$|혁신센터$|엑셀러레이터$|인큐베이터$|지원센터$|협회$|연합회$|연구원$'
    r'|학교$|창경센터$|벤처$)',  # 학교·창업경제센터·VC약칭(IBK벤처 등)
)

# 비회사 고빈도 키워드 — 이 단어가 후보 문자열에 포함되면 회사명 아님
# 범위를 좁게 유지: 회사명에 절대 나올 수 없는 패턴만
NON_COMPANY_KEYWORDS = (
    '출정식', '국가산단', '시의회', '지방선거', '경제자유구역',
    # 대학/교육기관
    '대학', '산학협력단',
    # 투자사/펀드 (피투자사 아님)
    '컨소시엄', '펀드', 'VC', '벤처투자', '美',
    # 언론/미디어
    '헤드라인', '머니투데이',
    # 인명·직함·일반명사 조각
    '대표', '업체', '치료제', '리서치', '프로젝트',
    # 직함·기관·지자체·운용사 (스타트업 피투자사 아님)
    '군수', '시장님', '회장', '사장', '의원', '장관', '지사', '청장',
    '그룹', '공단', '진흥공단', '콘진원', '경과원', '해수부', '무협', '경찰',
    '운용', 'PEF', 'ETF', 'AUM', '사관학교', '진흥원', '캠프', '국비', '도비',
    # 정부·클러스터 사업 조각
    '거점', '클러스터', '특구', '단지',
    # 06-27 넓은스캔: 증권/기금/보증/유망/한자/K-조각
    '증권', '기금', '보증', '유망', '韓', 'K-바이오', 'K-콘텐츠',
    # 06-28: 기사 명사구 조각 (회사명에 거의 안 쓰임)
    '실력',
    # 06-29: 기사 동사구 조각 ('○○ 선정' 류) — 회사명에 안 쓰임
    '선정',
)

def _valid_company(cand):
    if not cand or not (1 < len(cand) <= 20):
        return False
    # ① 집합 기반 거부 (완전 일치)
    if cand in NOISE_COMPANY or cand in EXTRA_NOISE or cand in EXTRA_NOISE2:
        return False
    # ② 공백 3개 이상 = 문장 (공백 2개까지는 '매니폴드 시큐리티 AI' 같은 경우 허용)
    if cand.count(' ') >= 3:
        return False
    # ② 공백 1개 뒤 마지막 토큰이 1글자 한글이면 잘린 조각 (예: '반도체 제', '혁신 창')
    if ' ' in cand and re.fullmatch(r'[가-힣]', cand.rsplit(' ', 1)[-1]):
        return False
    # ③ 숫자·마침표: 브랜드명 숫자(로카101, 1에스와이유)는 허용, 소수점·날짜 패턴만 거부
    if re.search(r'[.]', cand):
        return False
    if '(' in cand and ')' not in cand:      # 괄호 잘림 제외
        return False
    # ③-b 투자자 나열(가운뎃점 2개 이상)·따옴표 조각 = 회사명 아님
    if cand.count('·') >= 2:                  # 예: 삼성·SK·현대차·LG, 메타·피델리티·a
        return False
    if any(q in cand for q in ("'", "’", '"', '“', '”')):  # 예: 포털' 승부수, 포털 '다음
        return False
    # ④ VC 접미사 차단 — 항상 차단 접미사
    if VC_SUFFIX_RE.search(cand):
        return False
    # ④ VC 단축 접미사 — 6글자 미만만 차단 (엘케이벤처스=6글자 → 통과)
    if VC_SUFFIX_SHORT_RE.search(cand) and len(cand) < 6:
        return False
    if BAD_SUFFIX_RE.search(cand):           # 기관/지자체 접미사 제외
        return False
    if any(b in cand for b in BAD_TOKENS):
        return False
    # ⑤-0 단위(억/조원/만원) 포함 = 금액조각이 섞인 잘린 이름 (실회사명엔 안 나옴)
    if '억' in cand or '조원' in cand or '만원' in cand:
        return False
    # ⑤-0b 지자체 '○○시'로 끝남 = 지역명 (실제 시 이름 목록 — '제로해시' 같은 회사 오탈락 방지)
    _CITY_SI = ('서울시', '부산시', '대구시', '인천시', '광주시', '대전시', '울산시', '세종시',
                '수원시', '성남시', '용인시', '고양시', '창원시', '청주시', '천안시', '전주시',
                '포항시', '김해시', '의정부시', '평택시', '안산시', '안양시', '부천시', '화성시',
                '남양주시', '파주시', '김포시', '광명시', '시흥시', '군산시', '경산시', '구미시',
                '원주시', '춘천시', '강릉시', '목포시', '여수시', '순천시', '진주시', '양산시')
    if cand.endswith(_CITY_SI):
        return False
    # ⑤-0c 끝이 '공백+1~3 영숫자' = 잘린 조각 (호환 L, 언두 3, …로부터 3)
    if re.search(r'\s[0-9A-Za-z]{1,3}$', cand):
        return False
    # ⑤-0d 문장부호로 끝남 (물음표/말줄임/느낌표)
    if cand.endswith(('?', '…', '!')):
        return False
    # ⑤ 확실한 조사로 끝나는 경우만 거부 (이/로/나/고/며 등 한글 브랜드 어미는 제외)
    #   복합 보조사 '에만/에서만/로만'은 명백한 문장 조각 (예: '로봇 스타트업에만')
    #   ('으로만'은 '로만' endswith에 항상 선포섭되어 불필요 — 감사 c07a1232 지적①)
    if cand.endswith(('은', '는', '가', '의', '를', '을', '와', '과', '에',
                      '에서', '으로', '부터', '까지', '에게',
                      '에만', '에서만', '로만')):
        return False                         # 조사로 끝나면 문장 일부
    # ⑤-b 대학 약칭: 순한글 2~5자가 '대'로 끝나면 교육기관(호서대/충남대/서울대 등) → 거부
    if 2 <= len(cand) <= 5 and re.fullmatch(r'[가-힣]+대', cand):
        return False
    # ⑥ 비회사 키워드 포함 시 거부 (좁은 범위만)
    if any(kw in cand for kw in NON_COMPANY_KEYWORDS):
        return False
    # ⑦ 2글자 순수 한글이면서 명백한 일반어만 거부 (집합 기반 — 과잉 차단 방지)
    if len(cand) == 2 and re.fullmatch(r'[가-힣]{2}', cand):
        _TWO_CHAR_NOISE = {
            '추론', '창업', '외화', '창구', '산단', '사줘', '시장', '기업', '투자',
            '성장', '확장', '진출', '조달', '채권', '선거', '골프', '승리', '등극',
        }
        if cand in _TWO_CHAR_NOISE:
            return False
    return True

# 비투자(펀딩 아님) 기사 제외 키워드
EXCLUDE = ['과징금', '공모주', '공모가', '수요예측', '상장', 'IPO', '소송', '파산', '회수',
           '매각', '인수합병', 'M&A', '벌금', '제재', '횡령', '구속', '논란', '후폭풍',
           '코스닥', '코스피', '청약', '배당', '실적', '주가', '시총',
           # 결함1 보완: 펀드결성·몸값·해외 대형 라운드는 딜이 아님
           '펀드 결성', '펀드결성', '몸값', '기업 가치', '기업가치',
           # 앤스로픽은 실회사이므로 EXCLUDE 제거 — 몸값/기업가치 키워드가 상위에서 처리
           '오픈AI', '오픈에이아이', '오픈 AI',
           '인천 스타트업', '국가난제', '소속사', 'IRR',
           # 펀드 조성 관련 (투자자 측 행위, 딜 아님)
           '펀드 조성', '펀드조성', '벤처펀드 조성', '모태펀드', '정책펀드',
           # 결함3 보완: 선거·스포츠·시장분석·채권조달 배제
           '선거운동', '출정식', '선거', '후보', 'LIV 골프', '골프', 'LIV',
           '채권 조달', '채권조달', '호주달러 채권', '외화 조달', '외화조달',
           '시장분석', '빅테크 투자', 'AI 패권', '국책펀드',
           # 국가·기관 지원 (스타트업 딜 아님)
           '국가산단', '경제자유구역', '성장금융', '스케일업 펀드',
           # 대형 해외 빅테크 라운드 (국내 스타트업 아님)
           'xAI', '머스크의', 'OpenAI', 'Anthropic', '데이터브릭스',
           # M&A 완료(투자 유치 아님) — '인수 제안 거절'은 매칭 안 되도록 '완료/확정/지분'만
           '인수 완료', '인수 확정', '지분 인수', '지분 취득',
           # 정부·지자체 예산/사업 (스타트업 딜 아님)
           '국·도비', '국비·도비', '테스트베드 선정']

def is_investment_news(text):
    if any(x in text for x in EXCLUDE):
        return False
    # 선거·스포츠·채권 기사 패턴 정규식 추가 차단
    if re.search(r'선거(운동|전략|결과|캠페인)|후보(등록|공약|지지)|골프.*(투자|유치)|채권.*(조달|발행)', text):
        return False
    has_invest = ('투자 유치' in text or '투자유치' in text or '유치' in text
                  or '펀딩' in text or '투자를 유치' in text or '조달' in text)
    has_stage = bool(re.search(r'시리즈|시드|프리\s*시리즈|프리\s*[A-Ea-e]|라운드', text))
    has_money = bool(re.search(r'\d\s*억|\d\s*조|달러', text))
    # ① 유치/펀딩류면 금액 또는 단계 중 하나만 있어도 딜 (금액 미공개 라운드 포함)
    # ② 유치어가 없어도 '단계+금액+투자' 동시 언급이면 딜 ("50억 시리즈A 마무리…투자")
    return (has_invest and (has_money or has_stage)) or (has_stage and has_money and '투자' in text)

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
