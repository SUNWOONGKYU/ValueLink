#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO, 설립일 백그라운드 수집 (장시간 실행)
- 253개 전체 기업 처리
- 진행 상황 로그 파일에 기록
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

# 로그 파일 경로
LOG_FILE = "ceo_founded_collection.log"


def log(message):
    """로그 출력 및 파일 저장"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


def extract_ceo_from_text(text):
    """텍스트에서 CEO 이름 추출"""

    exclude_keywords = [
        '주식회사', '스타트업', '기업', '회사',
        '와우테일', '우테일', '벤처스퀘어', '더브이씨',
        '인터뷰', '기자', '편집장', '작성자', '대표이사'
    ]

    patterns = [
        r'대표(?:이사)?\s*:\s*([가-힣]{2,4})',
        r'대표(?:이사)?\s+([가-힣]{2,4})(?:\s|,|\.|\)|은|가)',
        r'([가-힣]{2,4})\s+대표(?:이사)?',
        r'CEO\s*:\s*([가-힣]{2,4})',
        r'CEO\s+([가-힣]{2,4})',
        r'\(대표\s*:\s*([가-힣]{2,4})\)',
        r'\(대표\s+([가-힣]{2,4})\)',
        r'공동대표\s+([가-힣]{2,4})',
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
        r'(\d{4})\.\d{1,2}\s*(?:설립|창업)',
        r'(\d{4})-\d{1,2}\s*(?:설립|창업)',
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

    # 네이버 검색 URL (여러 쿼리 시도)
    search_queries = [
        f"{company_name} 스타트업 대표",
        f"{company_name} 기업 설립",
        f"{company_name} CEO",
    ]

    all_text = ""

    for query in search_queries:
        try:
            search_url = f"https://search.naver.com/search.naver?query={query}"
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            all_text += soup.get_text() + "\n"
            time.sleep(0.5)  # 검색 간격
        except Exception as e:
            continue

    if not all_text:
        return {}

    info = {}

    # CEO 추출
    ceo = extract_ceo_from_text(all_text)
    if ceo:
        info['ceo'] = ceo

    # 설립일 추출
    founded = extract_founded_from_text(all_text)
    if founded:
        info['founded'] = founded

    return info


def collect_ceo_founded_background():
    """CEO, 설립일 백그라운드 수집"""

    log("=" * 70)
    log("CEO, 설립일 백그라운드 수집 시작")
    log("=" * 70)

    # 전체 레코드 가져오기
    result = supabase.table("deals")\
        .select("id, company_name, ceo, founded")\
        .execute()

    deals = result.data
    log(f"\n총 레코드: {len(deals)}개")

    # CEO 또는 founded가 없는 것만 필터링
    to_process = [d for d in deals if not d.get('ceo') or not d.get('founded')]
    log(f"처리할 레코드: {len(to_process)}개\n")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for idx, deal in enumerate(to_process, 1):
        company_name = deal['company_name']

        # 이미 둘 다 있으면 스킵
        if deal.get('ceo') and deal.get('founded'):
            skip_count += 1
            continue

        log(f"[{idx}/{len(to_process)}] {company_name}...")

        # 네이버 검색
        try:
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

                    log(f"  ✅ {', '.join(result_str)}")
                    success_count += 1
                else:
                    log(f"  ⚠️ 정보 없음")
                    fail_count += 1
            else:
                log(f"  ❌ 검색 실패")
                fail_count += 1

        except Exception as e:
            log(f"  ❌ 오류: {str(e)[:50]}")
            fail_count += 1

        time.sleep(2)  # 검색 간격 (네이버 차단 방지)

        # 10개마다 중간 보고
        if idx % 10 == 0:
            log(f"\n--- 중간 보고 ({idx}/{len(to_process)}) ---")
            log(f"성공: {success_count}개, 실패: {fail_count}개")
            log("")

    log("\n" + "=" * 70)
    log("수집 완료")
    log("=" * 70)
    log(f"✅ 성공: {success_count}개")
    log(f"❌ 실패: {fail_count}개")
    log(f"⏭️ 스킵: {skip_count}개")
    log("=" * 70)


if __name__ == '__main__':
    collect_ceo_founded_background()
