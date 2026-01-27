#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 검색으로 CEO, 설립일 수집
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
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


def extract_ceo_from_text(text):
    """텍스트에서 CEO 이름 추출"""

    exclude_keywords = [
        '주식회사', '스타트업', '기업', '회사',
        '와우테일', '우테일', '벤처스퀘어', '더브이씨',
        '인터뷰', '기자', '편집장', '작성자', '대표이사'
    ]

    patterns = [
        r'대표(?:이사)?\s*:\s*([가-힣]{2,4})',
        r'대표(?:이사)?\s+([가-힣]{2,4})(?:\s|,|\.|\))',
        r'([가-힣]{2,4})\s+대표(?:이사)?',
        r'CEO\s*:\s*([가-힣]{2,4})',
        r'CEO\s+([가-힣]{2,4})',
        r'\(대표\s*:\s*([가-힣]{2,4})\)',
        r'\(대표\s+([가-힣]{2,4})\)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            ceo_name = match.group(1)
            if len(ceo_name) >= 2:
                excluded = False
                for keyword in exclude_keywords:
                    if keyword in ceo_name:
                        excluded = True
                        break
                if not excluded:
                    return ceo_name

    return None


def extract_founded_from_text(text):
    """텍스트에서 설립일 추출"""

    patterns = [
        r'설립(?:일)?\s*:\s*(\d{4})[년.-]?(?:\d{1,2})?[월.-]?(?:\d{1,2})?',
        r'(\d{4})년\s*(?:설립|창업|창립|출범)',
        r'(?:설립|창업|창립|출범)\s*:\s*(\d{4})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            year = match.group(1)
            if 1990 <= int(year) <= 2026:
                return f"{year}-01-01"

    return None


def search_naver(company_name):
    """네이버 검색으로 기업 정보 찾기"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    # 네이버 검색 URL
    search_url = f"https://search.naver.com/search.naver?query={company_name}+스타트업+대표"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 검색 결과 텍스트 추출
        search_text = soup.get_text()

        info = {}

        # CEO 추출
        ceo = extract_ceo_from_text(search_text)
        if ceo:
            info['ceo'] = ceo

        # 설립일 추출
        founded = extract_founded_from_text(search_text)
        if founded:
            info['founded'] = founded

        return info

    except Exception as e:
        print(f"   검색 오류: {str(e)[:30]}")
        return {}


def collect_from_naver():
    """네이버 검색으로 CEO, 설립일 수집"""

    print("=" * 70)
    print("네이버 검색으로 CEO, 설립일 수집")
    print("=" * 70)

    # CEO 또는 founded가 없는 레코드 가져오기 (50개씩)
    result = supabase.table("deals")\
        .select("id, company_name, ceo, founded")\
        .limit(50)\
        .execute()

    deals = result.data
    print(f"\n처리할 레코드: {len(deals)}개\n")

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']

        # 이미 둘 다 있으면 스킵
        if deal.get('ceo') and deal.get('founded'):
            continue

        print(f"[{idx}/{len(deals)}] {company_name}...", end=" ")

        # 네이버 검색
        info = search_naver(company_name)

        if info:
            update_data = {}

            if 'ceo' in info and not deal.get('ceo'):
                update_data['ceo'] = info['ceo']

            if 'founded' in info and not deal.get('founded'):
                update_data['founded'] = info['founded']

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

                print(f"✅ {', '.join(result_str)}")
                success_count += 1
            else:
                print("⚠️ 정보 없음")
                fail_count += 1
        else:
            print("❌ 검색 실패")
            fail_count += 1

        time.sleep(1)  # 검색 간격

    print("\n" + "=" * 70)
    print("수집 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    collect_from_naver()
