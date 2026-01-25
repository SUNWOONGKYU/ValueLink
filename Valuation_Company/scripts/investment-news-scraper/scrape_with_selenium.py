#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자 뉴스 스크래핑 (Selenium 버전)
Selenium을 사용하여 JavaScript 렌더링 사이트도 스크래핑
"""

import os
import time
import json
import logging
from datetime import datetime, date
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import requests

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_selenium_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supabase 연결
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# 기간 설정
START_DATE = date(2026, 1, 1)
END_DATE = date.today()

# 키워드
KEYWORDS = ['투자', '투자유치', '펀딩', '시리즈', '벤처캐피털', 'VC', '엔젤투자', 'M&A', '인수']


def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


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


def scrape_thevc(driver):
    """THE VC 스크래핑"""
    articles = []
    site_number = 8
    site_name = "더브이씨"
    site_url = "https://thevc.kr"

    logger.info(f"🔍 [{site_name}] 스크래핑 시작...")

    try:
        # 투자 페이지 접속
        url = "https://thevc.kr/browse/investments"
        driver.get(url)

        # JavaScript 렌더링 대기
        time.sleep(3)

        # 페이지 스크롤 (lazy loading 대응)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 투자 항목 찾기
        # THE VC는 투자 DB 형태이므로 다른 방식 필요
        logger.info(f"  페이지 로드 완료: {driver.title}")

        # 페이지 소스 확인
        page_source = driver.page_source

        # 간단한 테스트: 페이지에 "투자" 키워드가 있는지 확인
        if "투자" in page_source:
            logger.info(f"  ✅ 페이지에서 '투자' 키워드 발견")

        # TODO: THE VC의 실제 HTML 구조에 맞게 스크래핑 로직 구현
        # 현재는 테스트 단계

    except Exception as e:
        logger.error(f"  ❌ 에러: {e}")

    logger.info(f"✅ [{site_name}] {len(articles)}건 수집 완료")
    return articles


def scrape_platum(driver):
    """플래텀 스크래핑"""
    articles = []
    site_number = 10
    site_name = "플래텀"
    site_url = "https://platum.kr"

    logger.info(f"🔍 [{site_name}] 스크래핑 시작...")

    try:
        # 뉴스 페이지
        url = "https://platum.kr/news/"
        driver.get(url)
        time.sleep(3)

        logger.info(f"  페이지 로드 완료: {driver.title}")

        # TODO: 플래텀 HTML 구조에 맞게 구현

    except Exception as e:
        logger.error(f"  ❌ 에러: {e}")

    logger.info(f"✅ [{site_name}] {len(articles)}건 수집 완료")
    return articles


def save_to_json(articles: List[Dict], filename: str = "inbox/investment_news_data.json"):
    """JSON 파일로 저장"""
    filepath = os.path.join(os.path.dirname(__file__), filename)

    # 기존 데이터 로드 (있으면)
    existing_data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            pass

    # 중복 제거 (article_url 기준)
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
    """Supabase에 저장 (REST API)"""
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
                logger.info(f"  💾 Supabase 저장: {article['article_title'][:50]}...")
            elif response.status_code == 409:
                logger.info(f"  ⚠️  중복 URL: {article['article_title'][:50]}...")
            else:
                logger.error(f"  ❌ 저장 실패 (HTTP {response.status_code})")
        except Exception as e:
            logger.error(f"  ❌ 저장 에러: {e}")

    return saved_count


def main():
    """메인 실행"""
    logger.info("=" * 60)
    logger.info("📰 투자 뉴스 스크래핑 시작 (Selenium)")
    logger.info(f"📅 기간: {START_DATE} ~ {END_DATE}")
    logger.info("=" * 60)

    driver = None
    all_articles = []

    try:
        # WebDriver 설정
        logger.info("🔧 Chrome WebDriver 설정 중...")
        driver = setup_driver()
        logger.info("✅ WebDriver 준비 완료")

        # 테스트: THE VC 스크래핑
        articles_thevc = scrape_thevc(driver)
        all_articles.extend(articles_thevc)

        # 테스트: 플래텀 스크래핑
        articles_platum = scrape_platum(driver)
        all_articles.extend(articles_platum)

        # JSON 저장
        logger.info("\n" + "=" * 60)
        logger.info("💾 JSON 파일 저장 중...")
        saved_json = save_to_json(all_articles)

        # Supabase 저장
        if all_articles:
            logger.info("💾 Supabase 저장 중...")
            saved_db = save_to_supabase(all_articles)
            logger.info(f"✅ Supabase 저장 완료: {saved_db}건")

        logger.info("\n" + "=" * 60)
        logger.info("✅ 스크래핑 완료!")
        logger.info(f"📊 총 수집: {len(all_articles)}건")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ 치명적 에러: {e}", exc_info=True)

    finally:
        if driver:
            driver.quit()
            logger.info("🔧 WebDriver 종료")


if __name__ == '__main__':
    main()
