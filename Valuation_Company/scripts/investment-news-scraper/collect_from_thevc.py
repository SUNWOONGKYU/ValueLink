#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
더VC(thevc.kr)에서 기업 정보 수집
- CEO, 설립일, 지역, 누적투자액
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def search_thevc(company_name):
    """더VC에서 기업 검색"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    # 더VC 검색 URL
    search_url = f"https://thevc.kr/search?query={company_name}"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과에서 첫 번째 기업 링크 찾기
        company_link = soup.select_one('a[href^="/companies/"]')

        if company_link:
            company_url = "https://thevc.kr" + company_link['href']
            return company_url

        return None

    except Exception as e:
        print(f"   검색 실패: {str(e)[:50]}")
        return None


def extract_company_info(company_url):
    """기업 페이지에서 정보 추출"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        response = requests.get(company_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        info = {}

        # CEO 추출
        ceo_elem = soup.find(string=re.compile('대표|CEO'))
        if ceo_elem:
            ceo_text = ceo_elem.find_next().get_text(strip=True)
            info['ceo'] = ceo_text

        # 설립일 추출
        founded_elem = soup.find(string=re.compile('설립|설립일'))
        if founded_elem:
            founded_text = founded_elem.find_next().get_text(strip=True)
            # YYYY-MM-DD 형식으로 변환
            match = re.search(r'(\d{4})[년.-](\d{1,2})[월.-]?(\d{1,2})?', founded_text)
            if match:
                year = match.group(1)
                month = match.group(2).zfill(2)
                day = match.group(3).zfill(2) if match.group(3) else '01'
                info['founded'] = f"{year}-{month}-{day}"

        # 지역 추출
        location_elem = soup.find(string=re.compile('본사|위치|소재지'))
        if location_elem:
            location_text = location_elem.find_next().get_text(strip=True)
            info['location'] = location_text

        # 누적투자액 추출
        funding_elem = soup.find(string=re.compile('누적 투자금액|총 투자금액'))
        if funding_elem:
            funding_text = funding_elem.find_next().get_text(strip=True)
            # 억원 단위로 변환
            match = re.search(r'(\d+(?:,\d+)?)\s*억', funding_text)
            if match:
                amount = int(match.group(1).replace(',', ''))
                info['total_funding'] = amount

        return info

    except Exception as e:
        print(f"   추출 실패: {str(e)[:50]}")
        return {}


def collect_from_thevc():
    """더VC에서 기업 정보 수집"""

    print("=" * 70)
    print("더VC에서 기업 정보 수집")
    print("=" * 70)

    # CEO, founded, location이 없는 레코드 가져오기
    result = supabase.table("deals")\
        .select("id, company_name, ceo, founded, location, total_funding")\
        .limit(100)\
        .execute()

    deals = result.data
    print(f"\n처리할 레코드: {len(deals)}개\n")

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']

        print(f"[{idx}/{len(deals)}] {company_name}...", end=" ")

        # 더VC에서 기업 검색
        company_url = search_thevc(company_name)

        if not company_url:
            print("❌ 검색 결과 없음")
            fail_count += 1
            continue

        # 기업 정보 추출
        info = extract_company_info(company_url)

        if info:
            # DB 업데이트
            update_data = {}

            if 'ceo' in info and not deal.get('ceo'):
                update_data['ceo'] = info['ceo']

            if 'founded' in info and not deal.get('founded'):
                update_data['founded'] = info['founded']

            if 'location' in info and not deal.get('location'):
                update_data['location'] = info['location']

            if 'total_funding' in info and not deal.get('total_funding'):
                update_data['total_funding'] = info['total_funding']

            if update_data:
                supabase.table("deals")\
                    .update(update_data)\
                    .eq("id", deal['id'])\
                    .execute()

                result_str = []
                if 'ceo' in update_data:
                    result_str.append(f"CEO: {update_data['ceo']}")
                if 'founded' in update_data:
                    result_str.append(f"설립: {update_data['founded']}")
                if 'location' in update_data:
                    result_str.append(f"지역: {update_data['location']}")
                if 'total_funding' in update_data:
                    result_str.append(f"누적: {update_data['total_funding']}억")

                print(f"✅ {', '.join(result_str)}")
                success_count += 1
            else:
                print("⚠️ 정보 없음")
                fail_count += 1
        else:
            print("❌ 정보 추출 실패")
            fail_count += 1

        time.sleep(1)  # 크롤링 간격

    print("\n" + "=" * 70)
    print("수집 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    collect_from_thevc()
