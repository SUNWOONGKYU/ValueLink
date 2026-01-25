#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE VC 투자 데이터 스크래핑 (Selenium)
"""

import os
import time
import json
import logging
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scrape_thevc():
    """THE VC 투자 데이터 수집"""
    driver = setup_driver()
    articles = []

    try:
        url = "https://thevc.kr/browse/investments"
        logger.info(f"📍 접속 중: {url}")

        driver.get(url)
        time.sleep(5)  # JavaScript 렌더링 대기

        # 스크롤 다운 (lazy loading)
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        logger.info(f"✅ 페이지 로드 완료: {driver.title}")

        # HTML 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # 페이지 소스 저장 (디버깅용)
        with open('thevc_page_source.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        logger.info("📄 페이지 소스 저장: thevc_page_source.html")

        # 투자 데이터 추출 시도
        # THE VC는 투자 DB이므로 테이블 또는 카드 형식으로 되어 있을 것

        # 방법 1: 테이블 행 찾기
        rows = soup.find_all('tr')
        logger.info(f"🔍 테이블 행 수: {len(rows)}")

        # 방법 2: 투자 카드 찾기
        cards = soup.find_all('div', class_=lambda x: x and ('card' in x.lower() or 'item' in x.lower()))
        logger.info(f"🔍 카드 수: {len(cards)}")

        # 방법 3: 링크에서 "투자" 키워드 포함된 것 찾기
        links = soup.find_all('a', href=True)
        investment_links = [link for link in links if '투자' in link.get_text()]
        logger.info(f"🔍 '투자' 포함 링크: {len(investment_links)}")

        # 샘플 데이터 출력
        for i, link in enumerate(investment_links[:5]):
            logger.info(f"  {i+1}. {link.get_text()[:50]} -> {link['href']}")

    except Exception as e:
        logger.error(f"❌ 에러: {e}", exc_info=True)

    finally:
        driver.quit()

    return articles


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🔍 THE VC 페이지 분석 시작")
    logger.info("=" * 60)

    articles = scrape_thevc()

    logger.info("=" * 60)
    logger.info(f"✅ 완료: {len(articles)}건 수집")
    logger.info("=" * 60)
