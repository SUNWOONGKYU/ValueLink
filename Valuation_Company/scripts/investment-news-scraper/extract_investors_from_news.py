#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 기사에서 투자자 정보 다시 추출
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


def extract_investors_from_text(text):
    """텍스트에서 투자자 추출"""

    # 투자사 키워드 패턴
    vc_keywords = [
        '벤처스', '벤처캐피탈', '캐피탈', '인베스트먼트', '파트너스',
        'VC', 'Partners', 'Capital', 'Ventures', 'Investment',
        '투자', '액셀러레이터'
    ]

    # 투자자 리스트 추출 패턴
    patterns = [
        r'([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자|VC|Partners|Capital|Ventures))[,\s·・]+',
        r'([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자|VC|Partners|Capital|Ventures))(?:\s*등|\s*외)',
        r'([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자|VC|Partners|Capital|Ventures))(?:\s*이\s*투자|\s*가\s*투자|\s*로부터)',
    ]

    investors = set()

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            investor = match.group(1).strip()
            # 최소 2글자 이상, 최대 30글자 이하
            if 2 <= len(investor) <= 30:
                investors.add(investor)

    # 여러 투자자가 나열된 패턴
    list_patterns = [
        r'([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자)),\s*([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자))',
        r'([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자))·([가-힣A-Za-z0-9]+(?:벤처스|캐피탈|파트너스|인베스트먼트|투자))',
    ]

    for pattern in list_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            for i in range(1, len(match.groups()) + 1):
                investor = match.group(i).strip()
                if 2 <= len(investor) <= 30:
                    investors.add(investor)

    if investors:
        return ', '.join(sorted(investors))

    return None


def extract_investors():
    """뉴스 기사에서 투자자 다시 추출"""

    print("=" * 70)
    print("뉴스 기사에서 투자자 정보 재추출")
    print("=" * 70)

    # 모든 Deal 가져오기
    result = supabase.table("deals")\
        .select("id, company_name, news_url, investors")\
        .execute()

    deals = result.data
    print(f"\n총 레코드: {len(deals)}개")

    # 투자자가 깨진 것만 필터링 (콤마가 없는 모든 레코드)
    to_process = []
    for deal in deals:
        investors = deal.get('investors') or ''
        # 콤마가 없는 경우 = 깨진 데이터 또는 단일 투자자
        if investors and ',' not in investors:
            to_process.append(deal)

    print(f"재추출 대상: {len(to_process)}개\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(to_process, 1):
        company_name = deal['company_name']
        news_url = deal.get('news_url')
        old_investors = deal.get('investors', '')

        print(f"[{idx}/{len(to_process)}] {company_name}...")
        print(f"  기존: {old_investors[:50]}...")

        if not news_url:
            print("  ❌ URL 없음")
            fail_count += 1
            continue

        try:
            # 뉴스 페이지 크롤링
            response = requests.get(news_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 본문 텍스트 추출
            article_text = soup.get_text()

            # 투자자 추출
            new_investors = extract_investors_from_text(article_text)

            if new_investors:
                # DB 업데이트
                supabase.table("deals")\
                    .update({"investors": new_investors})\
                    .eq("id", deal['id'])\
                    .execute()

                print(f"  ✅ 수정: {new_investors[:50]}...")
                success_count += 1
            else:
                print(f"  ⚠️ 투자자 없음")
                fail_count += 1

            time.sleep(0.5)  # 크롤링 간격

        except Exception as e:
            print(f"  ❌ 오류: {str(e)[:50]}")
            fail_count += 1

    print("\n" + "=" * 70)
    print("재추출 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    extract_investors()
