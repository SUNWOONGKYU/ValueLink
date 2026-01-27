#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
더VC에서 실제로 어떤 정보가 표시되는지 확인
"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')  # 백그라운드 실행
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

# 테스트할 기업명
test_companies = ['팡세', '토스', '당근마켓', '마켓컬리']

print("=" * 70)
print("더VC 정보 확인")
print("=" * 70)

try:
    driver = webdriver.Chrome(options=chrome_options)

    for company_name in test_companies:
        print(f"\n[ {company_name} 검색 ]")

        # 더VC 검색
        search_url = f'https://thevc.kr/search?query={company_name}'
        driver.get(search_url)

        # 페이지 로딩 대기
        time.sleep(3)

        # 페이지 소스 확인
        page_source = driver.page_source

        # 검색 결과에서 기업 링크 찾기
        try:
            # 여러 선택자 시도
            selectors = [
                "a[href*='/companies/']",
                "a[href*='/startups/']",
                ".company-card a",
                ".startup-card a",
            ]

            company_link = None
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        company_link = elements[0]
                        break
                except:
                    continue

            if company_link:
                company_url = company_link.get_attribute('href')
                print(f"✅ 기업 페이지 발견: {company_url}")

                # 기업 페이지로 이동
                driver.get(company_url)
                time.sleep(3)

                # 페이지 텍스트 추출
                page_text = driver.find_element(By.TAG_NAME, 'body').text

                # 찾을 정보
                info_keywords = {
                    'CEO': ['대표', 'CEO', '공동대표'],
                    'Founded': ['설립', '창립', '설립일'],
                    'Total Funding': ['누적 투자', '총 투자', '누적투자금', 'Total Investment'],
                    'Latest Investment': ['최근 투자', '투자 라운드', 'Series'],
                }

                print("\n표시되는 정보:")
                for info_type, keywords in info_keywords.items():
                    found = False
                    for keyword in keywords:
                        if keyword in page_text:
                            # 주변 텍스트 추출 (100자)
                            idx = page_text.find(keyword)
                            context = page_text[max(0, idx-20):idx+80]
                            print(f"  ✅ {info_type}: ...{context}...")
                            found = True
                            break
                    if not found:
                        print(f"  ❌ {info_type}: 정보 없음")

            else:
                print("❌ 기업 페이지를 찾을 수 없습니다")

        except Exception as e:
            print(f"❌ 오류: {str(e)[:100]}")

        print("-" * 70)

    driver.quit()

except Exception as e:
    print(f"\n❌ 브라우저 오류: {e}")
    print("\nChromeDriver가 설치되어 있지 않을 수 있습니다.")
    print("설치 방법: pip install webdriver-manager")

print("\n" + "=" * 70)
