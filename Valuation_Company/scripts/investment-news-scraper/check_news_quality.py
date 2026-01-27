#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
92개 뉴스 URL 품질 체크
- URL 접근 가능 여부
- 실제 투자 뉴스 여부
- 기업명 일치 여부
"""

import os
import sys
import csv
import requests
from bs4 import BeautifulSoup
import random

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 투자 관련 키워드
INVESTMENT_KEYWORDS = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'VC', '벤처캐피털', 'M&A', '인수']

# 공지사항 제외 키워드
EXCLUDE_KEYWORDS = ['공지', '[공지]', '모집', '초대', '안내']


def check_url_quality(company_name, url, stage, amount):
    """URL 품질 체크"""

    print(f"\n{'='*60}")
    print(f"기업: {company_name}")
    print(f"단계: {stage} | 금액: {amount}")
    print(f"URL: {url[:60]}...")
    print(f"{'='*60}")

    result = {
        'company_name': company_name,
        'url': url,
        'accessible': False,
        'is_investment_news': False,
        'has_company_name': False,
        'is_announcement': False,
        'title': None,
        'error': None
    }

    try:
        # URL 접근
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            result['accessible'] = True
            print("✅ URL 접근 가능")

            soup = BeautifulSoup(response.content, 'html.parser')

            # 제목 추출
            title_elem = soup.find('title') or soup.find('h1')
            if title_elem:
                title = title_elem.get_text(strip=True)
                result['title'] = title
                print(f"제목: {title[:80]}...")

                # 공지사항 체크
                if any(keyword in title for keyword in EXCLUDE_KEYWORDS):
                    result['is_announcement'] = True
                    print("❌ 공지사항 (제외 대상)")
                else:
                    print("✅ 일반 기사 (공지사항 아님)")

                # 투자 뉴스 체크
                if any(keyword in title for keyword in INVESTMENT_KEYWORDS):
                    result['is_investment_news'] = True
                    print("✅ 투자 뉴스 키워드 포함")
                else:
                    print("⚠️ 투자 뉴스 키워드 없음")

                # 기업명 체크
                if company_name in title or company_name in response.text[:1000]:
                    result['has_company_name'] = True
                    print("✅ 기업명 일치")
                else:
                    print("⚠️ 기업명 불일치")

        else:
            result['error'] = f"HTTP {response.status_code}"
            print(f"❌ HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        result['error'] = "Timeout"
        print("❌ 타임아웃")
    except Exception as e:
        result['error'] = str(e)[:50]
        print(f"❌ 오류: {str(e)[:50]}")

    return result


def main():
    print("=" * 60)
    print("92개 뉴스 URL 품질 체크")
    print("=" * 60)

    csv_file = 'final_found_urls.csv'

    # CSV 읽기
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    print(f"\n총 {len(companies)}개 레코드")

    # 무작위 10개 샘플링
    samples = random.sample(companies, min(10, len(companies)))

    print(f"무작위 {len(samples)}개 샘플 체크\n")

    results = []

    for row in samples:
        result = check_url_quality(
            row['기업명'],
            row['뉴스URL'],
            row['단계'],
            row['신규']
        )
        results.append(result)

    # 전체 통계
    print(f"\n{'='*60}")
    print("품질 체크 결과")
    print(f"{'='*60}")

    accessible_count = sum(1 for r in results if r['accessible'])
    investment_count = sum(1 for r in results if r['is_investment_news'])
    company_match_count = sum(1 for r in results if r['has_company_name'])
    announcement_count = sum(1 for r in results if r['is_announcement'])

    print(f"✅ URL 접근 가능: {accessible_count}/{len(results)} ({accessible_count*100/len(results):.0f}%)")
    print(f"✅ 투자 뉴스: {investment_count}/{len(results)} ({investment_count*100/len(results):.0f}%)")
    print(f"✅ 기업명 일치: {company_match_count}/{len(results)} ({company_match_count*100/len(results):.0f}%)")
    print(f"❌ 공지사항: {announcement_count}/{len(results)} ({announcement_count*100/len(results):.0f}%)")

    print(f"\n{'='*60}")

    # 문제 있는 URL 리스트
    problems = []
    for r in results:
        if not r['accessible']:
            problems.append(f"접근 불가: {r['company_name']} - {r['url'][:50]}")
        elif r['is_announcement']:
            problems.append(f"공지사항: {r['company_name']} - {r['title'][:50]}")
        elif not r['is_investment_news']:
            problems.append(f"투자뉴스 아님: {r['company_name']} - {r['title'][:50]}")

    if problems:
        print("⚠️ 문제 발견:")
        for p in problems:
            print(f"  - {p}")
    else:
        print("✅ 모든 샘플 품질 양호!")

    print(f"{'='*60}")


if __name__ == '__main__':
    main()
