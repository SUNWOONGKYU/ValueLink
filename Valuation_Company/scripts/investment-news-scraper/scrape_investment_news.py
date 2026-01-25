#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 스크래핑 스크립트
작성일: 2026-01-25
용도: 국내 19개 투자유치 뉴스 사이트 스크래핑 및 Supabase 저장
"""

import os
import time
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
# from supabase import create_client, Client

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ================================================================
# 설정
# ================================================================

# Supabase 연결
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("환경변수 SUPABASE_URL과 SUPABASE_KEY를 .env 파일에 설정해주세요.")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 대상 사이트 목록
SITES = [
    {'number': 8, 'name': '더브이씨', 'url': 'https://thevc.kr'},
    {'number': 9, 'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net'},
    {'number': 10, 'name': '플래텀', 'url': 'https://platum.kr'},
    {'number': 11, 'name': '스타트업투데이', 'url': 'https://startuptoday.kr'},
    {'number': 12, 'name': '스타트업엔', 'url': 'https://startupn.kr'},
    {'number': 13, 'name': '아웃스탠딩', 'url': 'https://outstanding.kr'},
    {'number': 14, 'name': '모비인사이드', 'url': 'https://mobiinside.co.kr'},
    {'number': 15, 'name': '지디넷코리아', 'url': 'https://www.zdnet.co.kr'},
    {'number': 16, 'name': '더벨', 'url': 'https://www.thebell.co.kr'},
    {'number': 17, 'name': '넥스트유니콘', 'url': 'https://nextunicorn.kr'},
    {'number': 18, 'name': '테크월드뉴스', 'url': 'https://www.epnc.co.kr'},
    {'number': 19, 'name': 'AI타임스', 'url': 'https://www.aitimes.com'},
    {'number': 20, 'name': '벤처경영신문', 'url': 'https://www.vmnews.co.kr'},
    {'number': 21, 'name': '뉴스톱', 'url': 'https://www.newstopkorea.com'},
    {'number': 22, 'name': '블로터', 'url': 'https://www.bloter.net'},
    {'number': 23, 'name': '이코노미스트', 'url': 'https://www.economist.co.kr'},
    {'number': 24, 'name': '매일경제 MK테크리뷰', 'url': 'https://www.mk.co.kr/news/it'},
    {'number': 25, 'name': '다음뉴스 벤처/스타트업', 'url': 'https://news.daum.net/section/2/venture'},
    {'number': 26, 'name': '대한민국 정책브리핑', 'url': 'https://www.korea.kr'},
]

# 검색 키워드 (투자유치 관련)
KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피털', 'VC', '엔젤투자', '프리시리즈', '브릿지']

# 기간 설정
START_DATE = date(2026, 1, 1)
END_DATE = date.today()

# 요청 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

REQUEST_DELAY = 2  # 요청 간 대기 시간 (초)


# ================================================================
# 유틸리티 함수
# ================================================================

def contains_keyword(text: str) -> bool:
    """텍스트에 투자 관련 키워드가 포함되어 있는지 확인"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)


def parse_date(date_str: str) -> Optional[date]:
    """날짜 문자열을 date 객체로 변환 (다양한 형식 지원)"""
    date_formats = [
        '%Y-%m-%d',
        '%Y.%m.%d',
        '%Y/%m/%d',
        '%Y년 %m월 %d일',
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue

    logger.warning(f"날짜 파싱 실패: {date_str}")
    return None


def is_valid_date(article_date: date) -> bool:
    """기사 날짜가 수집 기간 내에 있는지 확인"""
    return START_DATE <= article_date <= END_DATE


# ================================================================
# 스크래핑 함수 (사이트별 커스터마이징 필요)
# ================================================================

def _scrape_thevc_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ thevc.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_venturesquare_net(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles = []
    site_number = site_info['number']
    site_name = site_info['name']
    site_url_base = site_info['url'] # Base URL

    # 벤처스퀘어 홈페이지의 "스타트업 토픽" 섹션에서 기사 추출
    # 이 섹션은 ul#topic-news-list 내부에 기사 목록이 있습니다.
    # HTML 덤프 분석 결과, 이 부분이 제목과 날짜 정보를 모두 포함하고 있어 가장 적합합니다.

    # target_url은 scrape_site_dispatch에서 이미 처리했으므로 여기서는 response.text를 그대로 사용

    try:
        # article_elem 대신 topic-news-list의 li 요소들을 찾습니다.
        article_elements = soup.select('ul#topic-news-list > li')
        logger.info(f"[{site_name}] Found {len(article_elements)} potential article elements in 'ul#topic-news-list > li'.")

        for i, article_elem in enumerate(article_elements):
            logger.debug(f"[{site_name}] Processing article element {i+1}: {article_elem.prettify()[:500]}...") # Print first 500 chars for brevity
            try:
                # 제목 추출: h4.bold 안에 있는 a 태그
                title_elem = article_elem.select_one('h4.bold a')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # 키워드 필터링
                if not contains_keyword(title):
                    continue

                # URL 추출: h4.bold 안에 있는 a 태그의 href 속성
                article_url = title_elem['href']
                if not article_url.startswith('http'):
                    article_url = site_url_base.rstrip('/') + article_url

                # 날짜 추출: time 태그의 datetime 속성
                date_elem = article_elem.select_one('time[datetime]')
                published_date = None
                if date_elem and date_elem.has_attr('datetime'):
                    # datetime 속성값은 'YYYY-MM-DD HH:MM:SS' 형식일 수 있음
                    # parse_date 함수는 다양한 형식을 처리할 수 있습니다.
                    date_text = date_elem['datetime'].split('T')[0] # 'YYYY-MM-DD' 부분만 사용
                    published_date = parse_date(date_text)

                # 날짜가 없거나 기간 외면 스킵
                if not published_date or not is_valid_date(published_date):
                    continue

                # 내용 발췌 (선택 사항): Venturesquare의 이 섹션에서는 발췌가 명확하지 않음
                snippet = None # 이 섹션에서는 발췌가 명확하지 않으므로 None으로 설정

                articles.append({
                    'site_number': site_number,
                    'site_name': site_name,
                    'site_url': site_url_base, # Use the base site URL
                    'article_title': title,
                    'article_url': article_url,
                    'published_date': published_date.isoformat(),
                    'content_snippet': snippet,
                })

            except Exception as e:
                logger.error(f"[{site_name}] 기사 파싱 중 오류: {e} (URL: {article_url if 'article_url' in locals() else 'N/A'})")
                continue

    except Exception as e:
        logger.error(f"❌ [{site_name}] 스크래핑 오류: {e}")

    logger.info(f"✅ [{site_number}] {site_name}: {len(articles)}건 수집")
    return articles

def _scrape_platum_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ platum.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_startuptoday_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ startuptoday.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_startupn_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ startupn.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_outstanding_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ outstanding.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_mobiinside_co_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ mobiinside.co.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_zdnet_co_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.zdnet.co.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_thebell_co_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.thebell.co.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_nextunicorn_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ nextunicorn.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_epnc_co_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.epnc.co.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_aitimes_com(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.aitimes.com 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_vmnews_co_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.vmnews.co.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_newstopkorea_com(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.newstopkorea.com 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_bloter_net(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.bloter.net 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_economist_co_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.economist.co.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_mk_co_kr_news_it(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.mk.co.kr/news/it 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_news_daum_net_section_2_venture(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ news.daum.net/section/2/venture 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data

def _scrape_korea_kr(soup: BeautifulSoup, site_info: Dict) -> List[Dict]:
    articles_data = []
    # ⚠️ www.korea.kr 사이트 HTML 구조에 맞춰 셀렉터 수정 필요
    logger.warning(f"⚠️ {site_info['name']} ({site_info['url']}) 스크래핑 로직: 수동 구현 필요")
    return articles_data


# 사이트별 스크래핑 함수 매핑
SITE_SCRAPERS = {
    'https://thevc.kr': _scrape_thevc_kr,
    'https://www.venturesquare.net': _scrape_venturesquare_net,
    'https://platum.kr': _scrape_platum_kr,
    'https://startuptoday.kr': _scrape_startuptoday_kr,
    'https://startupn.kr': _scrape_startupn_kr,
    'https://outstanding.kr': _scrape_outstanding_kr,
    'https://mobiinside.co.kr': _scrape_mobiinside_co_kr,
    'https://www.zdnet.co.kr': _scrape_zdnet_co_kr,
    'https://www.thebell.co.kr': _scrape_thebell_co_kr,
    'https://nextunicorn.kr': _scrape_nextunicorn_kr,
    'https://www.epnc.co.kr': _scrape_epnc_co_kr,
    'https://www.aitimes.com': _scrape_aitimes_com,
    'https://www.vmnews.co.kr': _scrape_vmnews_co_kr,
    'https://www.newstopkorea.com': _scrape_newstopkorea_com,
    'https://www.bloter.net': _scrape_bloter_net,
    'https://www.economist.co.kr': _scrape_economist_co_kr,
    'https://www.mk.co.kr/news/it': _scrape_mk_co_kr_news_it,
    'https://news.daum.net/section/2/venture': _scrape_news_daum_net_section_2_venture,
    'https://www.korea.kr': _scrape_korea_kr,
}


def scrape_site_dispatch(site: Dict) -> List[Dict]:
    """
    각 사이트의 URL에 따라 적절한 스크래핑 함수를 호출하는 디스패처.
    각 사이트별 HTML 구조에 맞게 `_scrape_사이트명` 함수를 구현해야 합니다.
    """
    articles = []
    site_number = site['number']
    site_name = site['name']
    site_url = site['url']

    logger.info(f"🔍 [{site_number}] {site_name} 스크래핑 시작...")

    try:
        # 사이트 메인 페이지 요청
        # 벤처경영신문 (www.vmnews.co.kr)의 SSL 오류를 우회하기 위해 verify=False 추가
        if site_url == 'https://www.vmnews.co.kr':
            response = requests.get(site_url, headers=HEADERS, timeout=10, verify=False)
        else:
            response = requests.get(site_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        # TODO: 대부분의 한국어 사이트는 EUC-KR 또는 CP949를 사용할 수 있으므로,
        #       response.encoding을 'utf-8'로 강제하기 전에 requests가 자동으로 감지하도록 하거나,
        #       chardet 라이브러리 등을 사용하여 인코딩을 명시적으로 감지하는 것이 좋습니다.
        #       현재는 기본적으로 utf-8로 시도하고, 실패 시 수동 조정이 필요할 수 있습니다.
        response.encoding = 'utf-8' # 기본적으로 utf-8로 시도

        soup = BeautifulSoup(response.text, 'lxml')

        # 해당 사이트에 맞는 스크래퍼 함수 호출
        scraper_func = SITE_SCRAPERS.get(site_url)
        if scraper_func:
            articles = scraper_func(soup, site)
        else:
            logger.error(f"❌ [{site_number}] {site_name}에 대한 스크래퍼 함수를 찾을 수 없습니다.")

        logger.info(f"✅ [{site_number}] {site_name}: {len(articles)}건 수집")

    except requests.RequestException as e:
        logger.error(f"❌ [{site_number}] {site_name} 요청 실패: {e}")
    except Exception as e:
        logger.error(f"❌ [{site_number}] {site_name} 스크래핑 오류: {e}")

    return articles



# ================================================================
# Supabase 저장
# ================================================================

def save_to_supabase(articles: List[Dict]) -> int:
    """
    수집된 기사를 Supabase에 저장 (REST API 직접 호출)
    """
    if not articles:
        return 0

    saved_count = 0
    batch_size = 100

    # REST API 엔드포인트
    api_url = f"{SUPABASE_URL}/rest/v1/investment_news_articles"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]

        try:
            # REST API POST 요청
            response = requests.post(api_url, json=batch, headers=headers, timeout=30)

            if response.status_code == 201:
                saved_count += len(batch)
                logger.info(f"💾 Supabase 저장: {len(batch)}건 (누적: {saved_count}건)")
            elif response.status_code == 409:
                # 중복 URL
                logger.warning(f"⚠️  중복 URL 감지, 스킵: {len(batch)}건")
            else:
                logger.error(f"❌ Supabase 저장 실패 (HTTP {response.status_code}): {response.text}")

        except requests.RequestException as e:
            logger.error(f"❌ Supabase 저장 요청 실패: {e}")
        except Exception as e:
            logger.error(f"❌ Supabase 저장 오류: {e}")

    return saved_count


# ================================================================
# 메인 함수
# ================================================================

def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("📰 투자 뉴스 스크래핑 시작")
    logger.info(f"📅 기간: {START_DATE} ~ {END_DATE}")
    logger.info(f"🌐 대상 사이트: {len(SITES)}개")
    logger.info("=" * 60)

    start_time = time.time()
    total_articles = []

    # 사이트별 스크래핑
    for idx, site in enumerate(SITES, 1):
        logger.info(f"\n[{idx}/{len(SITES)}] {site['name']} 처리 중...")

        articles = scrape_site_dispatch(site)
        total_articles.extend(articles)

        # 요청 간 대기 (서버 부하 방지)
        if idx < len(SITES):
            logger.info(f"⏳ {REQUEST_DELAY}초 대기 중...")
            time.sleep(REQUEST_DELAY)

    # Supabase 저장
    logger.info("\n" + "=" * 60)
    logger.info("💾 Supabase 저장 시작...")
    saved_count = save_to_supabase(total_articles)

    # 결과 요약
    elapsed_time = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("✅ 스크래핑 완료!")
    logger.info(f"📊 수집 건수: {len(total_articles)}건")
    logger.info(f"💾 저장 건수: {saved_count}건")
    logger.info(f"⏱️  소요 시간: {elapsed_time:.2f}초")
    logger.info("=" * 60)

    # 사이트별 통계
    logger.info("\n📈 사이트별 수집 건수:")
    site_stats = {}
    for article in total_articles:
        site_name = article['site_name']
        site_stats[site_name] = site_stats.get(site_name, 0) + 1

    for site_name, count in sorted(site_stats.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  - {site_name}: {count}건")

    # 랭킹 업데이트 안내
    logger.info("\n" + "=" * 60)
    logger.info("📌 다음 단계:")
    logger.info("1. Supabase에서 다음 SQL 실행:")
    logger.info("   SELECT update_news_ranking();")
    logger.info("2. 랭킹 확인:")
    logger.info("   SELECT * FROM v_latest_ranking;")
    logger.info("=" * 60)


# ================================================================
# 실행
# ================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 치명적 오류: {e}", exc_info=True)
