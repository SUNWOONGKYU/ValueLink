#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쉬운 사이트 투자 뉴스 스크래핑
정적 HTML 사이트 위주로 빠르게 수집
"""

import os
import time
import json
import logging
from datetime import datetime, date
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_easy_sites_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supabase 연결
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# 기간
START_DATE = date(2026, 1, 1)
END_DATE = date.today()

# 키워드
KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피탈', 'VC', '엔젤투자', 'M&A', '인수', '억원', '조원']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


def contains_keyword(text: str) -> bool:
    """투자 관련 키워드 포함 여부"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)


def parse_date(date_str: str) -> str:
    """날짜 문자열을 YYYY-MM-DD 형식으로 변환"""
    date_formats = [
        '%Y-%m-%d',
        '%Y.%m.%d',
        '%Y/%m/%d',
        '%Y년 %m월 %d일',
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt).date()
            return parsed_date.isoformat()
        except ValueError:
            continue

    return None


def scrape_daum_news():
    """다음뉴스 벤처/스타트업 섹션 스크래핑"""
    articles = []
    site_number = 25
    site_name = "다음뉴스 벤처/스타트업"
    site_url = "https://news.daum.net"

    logger.info(f"🔍 [{site_name}] 스크래핑 시작...")

    try:
        url = "https://news.daum.net/breakingnews/digital/venture"
        logger.info(f"  접속: {url}")

        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 다음뉴스 기사 목록 찾기
        # 기사 리스트 컨테이너
        news_items = soup.select('ul.list_news2 li')
        logger.info(f"  발견: {len(news_items)}개 기사")

        for item in news_items:
            try:
                # 제목 및 URL
                link = item.select_one('a.link_txt')
                if not link:
                    continue

                title = link.get_text(strip=True)
                article_url = link.get('href', '')

                # 키워드 필터링
                if not contains_keyword(title):
                    continue

                # 날짜
                date_elem = item.select_one('span.info_time')
                if not date_elem:
                    continue

                date_text = date_elem.get_text(strip=True)
                # "2026.01.25" 형식
                published_date = parse_date(date_text)

                if not published_date:
                    continue

                # 날짜 범위 확인
                try:
                    date_obj = datetime.fromisoformat(published_date).date()
                    if not (START_DATE <= date_obj <= END_DATE):
                        continue
                except:
                    continue

                articles.append({
                    'site_number': site_number,
                    'site_name': site_name,
                    'site_url': site_url,
                    'article_title': title,
                    'article_url': article_url,
                    'published_date': published_date,
                    'content_snippet': None,
                })

                logger.info(f"  ✅ {title[:40]}... ({published_date})")

            except Exception as e:
                logger.error(f"  ❌ 기사 파싱 에러: {e}")
                continue

    except Exception as e:
        logger.error(f"❌ [{site_name}] 에러: {e}")

    logger.info(f"✅ [{site_name}] {len(articles)}건 수집")
    return articles


def scrape_mk_news():
    """매일경제 IT 섹션 스크래핑"""
    articles = []
    site_number = 24
    site_name = "매일경제 MK테크리뷰"
    site_url = "https://www.mk.co.kr"

    logger.info(f"🔍 [{site_name}] 스크래핑 시작...")

    try:
        url = "https://www.mk.co.kr/news/it/"
        logger.info(f"  접속: {url}")

        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 매일경제 기사 목록 찾기
        # 다양한 셀렉터 시도
        news_items = soup.select('div.news_node')
        if not news_items:
            news_items = soup.select('li.news_node')

        logger.info(f"  발견: {len(news_items)}개 기사")

        for item in news_items:
            try:
                # 제목 및 URL
                link = item.select_one('a')
                if not link:
                    continue

                title_elem = link.select_one('h3, h4, .news_ttl')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                article_url = link.get('href', '')

                # 절대 URL 변환
                if article_url and not article_url.startswith('http'):
                    article_url = site_url + article_url

                # 키워드 필터링
                if not contains_keyword(title):
                    continue

                # 날짜
                date_elem = item.select_one('span.date, .news_date')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    published_date = parse_date(date_text)

                    if published_date:
                        date_obj = datetime.fromisoformat(published_date).date()
                        if not (START_DATE <= date_obj <= END_DATE):
                            continue

                        articles.append({
                            'site_number': site_number,
                            'site_name': site_name,
                            'site_url': site_url,
                            'article_title': title,
                            'article_url': article_url,
                            'published_date': published_date,
                            'content_snippet': None,
                        })

                        logger.info(f"  ✅ {title[:40]}... ({published_date})")

            except Exception as e:
                logger.error(f"  ❌ 기사 파싱 에러: {e}")
                continue

    except Exception as e:
        logger.error(f"❌ [{site_name}] 에러: {e}")

    logger.info(f"✅ [{site_name}] {len(articles)}건 수집")
    return articles


def save_to_json(articles: List[Dict], filename: str = "inbox/investment_news_data.json"):
    """JSON 파일로 저장"""
    filepath = os.path.join(os.path.dirname(__file__), filename)

    # 기존 데이터 로드
    existing_data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            pass

    # 중복 제거
    existing_urls = {article.get('article_url') for article in existing_data}
    new_articles = [a for a in articles if a.get('article_url') not in existing_urls]

    # 병합
    all_articles = existing_data + new_articles

    # 저장
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    logger.info(f"💾 JSON 저장: {len(new_articles)}건 추가 (총 {len(all_articles)}건)")
    return len(new_articles)


def save_to_supabase(articles: List[Dict]) -> int:
    """Supabase에 저장"""
    if not articles:
        return 0

    saved_count = 0
    api_url = f"{SUPABASE_URL}/rest/v1/investment_news_articles"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    for article in articles:
        try:
            response = requests.post(api_url, json=article, headers=headers, timeout=30)

            if response.status_code == 201:
                saved_count += 1
                logger.info(f"  💾 Supabase: {article['article_title'][:40]}...")
            elif response.status_code == 409:
                logger.info(f"  ⚠️  중복: {article['article_title'][:40]}...")

        except Exception as e:
            logger.error(f"  ❌ 저장 에러: {e}")

    return saved_count


def main():
    """메인 실행"""
    logger.info("=" * 60)
    logger.info("📰 쉬운 사이트 투자 뉴스 스크래핑")
    logger.info(f"📅 기간: {START_DATE} ~ {END_DATE}")
    logger.info("=" * 60)

    all_articles = []

    # 다음뉴스
    articles_daum = scrape_daum_news()
    all_articles.extend(articles_daum)
    time.sleep(2)

    # 매일경제
    articles_mk = scrape_mk_news()
    all_articles.extend(articles_mk)

    # JSON 저장
    logger.info("\n" + "=" * 60)
    logger.info("💾 JSON 파일 저장 중...")
    saved_json = save_to_json(all_articles)

    # Supabase 저장
    if all_articles:
        logger.info("💾 Supabase 저장 중...")
        saved_db = save_to_supabase(all_articles)
        logger.info(f"✅ Supabase: {saved_db}건 저장")

    logger.info("\n" + "=" * 60)
    logger.info("✅ 스크래핑 완료!")
    logger.info(f"📊 총 수집: {len(all_articles)}건")
    logger.info(f"💾 JSON 추가: {saved_json}건")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
