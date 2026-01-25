#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 스크래핑 스크립트 v2
작성일: 2026-01-26
작성자: Claude Code
용도: 국내 투자유치 뉴스 사이트 스크래핑 및 Supabase 저장 (REST API 방식)
"""

import os
import time
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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

# 대상 사이트 목록
SITES = [
    {
        'number': 9,
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net/category/news-contents/news-trends/news/',
        'max_pages': 10  # 최근 10페이지 수집 (약 80건)
    },
    # 다른 사이트들은 순차적으로 추가 (Selenium 또는 API 필요)
]

# 검색 키워드 (투자유치 관련)
KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피털', 'VC', '엔젤투자', '프리시리즈', '브릿지', 'M&A', '인수']

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
# 스크래핑 함수
# ================================================================

def scrape_venturesquare(site_info: Dict) -> List[Dict]:
    """
    벤처스퀘어 스크래핑
    URL 패턴: https://www.venturesquare.net/category/news-contents/news-trends/news/page/{N}/
    """
    articles = []
    site_number = site_info['number']
    site_name = site_info['name']
    base_url = site_info['url']
    max_pages = site_info.get('max_pages', 3)

    logger.info(f"🔍 [{site_name}] 스크래핑 시작 (최대 {max_pages}페이지)")

    for page in range(1, max_pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"

        try:
            logger.info(f"  📄 페이지 {page} 요청: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'lxml')

            # 기사 목록 추출: h4.bold 안의 a 태그
            article_elements = soup.select('h4.bold a.black')
            logger.info(f"  ✅ {len(article_elements)}개 기사 발견")

            for elem in article_elements:
                try:
                    title = elem.get_text(strip=True)

                    # 키워드 필터링
                    if not contains_keyword(title):
                        continue

                    # URL
                    article_url = elem.get('href', '')
                    if not article_url.startswith('http'):
                        article_url = 'https://www.venturesquare.net' + article_url

                    # 날짜: 동일한 li 태그 내의 time 요소
                    li_parent = elem.find_parent('li')
                    if not li_parent:
                        continue

                    date_elem = li_parent.select_one('time[datetime]')
                    if not date_elem:
                        continue

                    date_text = date_elem.get('datetime', '').split('T')[0]
                    published_date = parse_date(date_text)

                    if not published_date or not is_valid_date(published_date):
                        continue

                    # 기사 데이터 저장
                    articles.append({
                        'site_number': site_number,
                        'site_name': site_name,
                        'site_url': 'https://www.venturesquare.net',
                        'article_title': title,
                        'article_url': article_url,
                        'published_date': published_date.isoformat(),
                        'content_snippet': None,
                    })

                    logger.info(f"  ✅ 수집: {title[:50]}... ({published_date})")

                except Exception as e:
                    logger.error(f"  ❌ 기사 파싱 오류: {e}")
                    continue

            # 페이지 간 대기
            if page < max_pages:
                time.sleep(1)

        except requests.RequestException as e:
            logger.error(f"  ❌ 페이지 {page} 요청 실패: {e}")
            break
        except Exception as e:
            logger.error(f"  ❌ 페이지 {page} 스크래핑 오류: {e}")
            break

    logger.info(f"✅ [{site_name}] 총 {len(articles)}건 수집 완료")
    return articles


# 사이트별 스크래핑 함수 매핑
SITE_SCRAPERS = {
    9: scrape_venturesquare,
    # 다른 사이트는 순차적으로 추가
}


def scrape_site(site: Dict) -> List[Dict]:
    """사이트별 스크래핑 디스패처"""
    site_number = site['number']
    scraper_func = SITE_SCRAPERS.get(site_number)

    if not scraper_func:
        logger.warning(f"⚠️  {site['name']} (#{site_number}) 스크래퍼 미구현")
        return []

    return scraper_func(site)


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
    failed_count = 0

    # REST API 엔드포인트
    api_url = f"{SUPABASE_URL}/rest/v1/investment_news_articles"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    # 개별 저장 (중복 처리를 위해)
    for article in articles:
        try:
            response = requests.post(api_url, json=article, headers=headers, timeout=30)

            if response.status_code == 201:
                saved_count += 1
                logger.info(f"  💾 저장 성공: {article['article_title'][:50]}...")
            elif response.status_code == 409:
                # 중복 URL
                logger.info(f"  ⚠️  중복 URL 스킵: {article['article_title'][:50]}...")
            else:
                failed_count += 1
                logger.error(f"  ❌ 저장 실패 (HTTP {response.status_code}): {article['article_title'][:50]}...")
                logger.error(f"     응답: {response.text[:200]}")

        except requests.RequestException as e:
            failed_count += 1
            logger.error(f"  ❌ 저장 요청 실패: {e}")
        except Exception as e:
            failed_count += 1
            logger.error(f"  ❌ 저장 오류: {e}")

    logger.info(f"💾 Supabase 저장 완료: 성공 {saved_count}건 / 실패 {failed_count}건")
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

        articles = scrape_site(site)
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

    # 랭킹 업데이트 안내
    if saved_count > 0:
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
