#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기업 정보 검색 (네이버 검색 API 활용)
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

def search_company_info_naver(company_name):
    """
    네이버 검색 API로 기업 정보 검색

    Args:
        company_name: 기업명

    Returns:
        dict: 추가 정보 (ceo, founded, location, website 등)
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print(f"  [WARNING] Naver API keys not found, skipping search")
        return {}

    try:
        # 네이버 블로그 검색
        search_query = f"{company_name} 스타트업 대표 설립"
        url = "https://openapi.naver.com/v1/search/blog.json"

        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }

        params = {
            'query': search_query,
            'display': 10,
            'sort': 'sim'  # 정확도순
        }

        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            # 검색 결과에서 정보 추출 (간단한 패턴 매칭)
            info = {
                'ceo': None,
                'founded': None,
                'location': None,
                'website': None
            }

            # 모든 검색 결과 텍스트 합치기
            all_text = ' '.join([item.get('description', '') + ' ' + item.get('title', '') for item in items])

            # 대표자 찾기
            import re
            ceo_patterns = [
                r'대표[:\s]+([가-힣]{2,4})',
                r'CEO[:\s]+([가-힣]{2,4})',
                r'([가-힣]{2,4})\s*대표',
                r'대표이사[:\s]+([가-힣]{2,4})'
            ]

            for pattern in ceo_patterns:
                match = re.search(pattern, all_text)
                if match:
                    info['ceo'] = match.group(1)
                    break

            # 설립일 찾기
            founded_patterns = [
                r'(\d{4})년\s*설립',
                r'설립[:\s]+(\d{4})',
                r'(\d{4})년\s*창립'
            ]

            for pattern in founded_patterns:
                match = re.search(pattern, all_text)
                if match:
                    year = match.group(1)
                    info['founded'] = f"{year}-01-01"
                    break

            # 본사 위치 찾기
            location_keywords = ['서울', '경기', '판교', '강남', '부산', '대전', '광주', '대구', '인천']
            for keyword in location_keywords:
                if keyword in all_text:
                    info['location'] = keyword
                    break

            return info

        else:
            print(f"  [WARNING] Naver API error: {response.status_code}")
            return {}

    except Exception as e:
        print(f"  [WARNING] Search failed: {e}")
        return {}

def search_company_info_google(company_name):
    """
    구글 검색으로 기업 정보 보강 (무료, API 키 불필요)

    Args:
        company_name: 기업명

    Returns:
        dict: 추가 정보
    """
    try:
        # 간단한 구글 검색 (스크래핑 방식 - 제한적)
        # 실제로는 Google Custom Search API를 사용하는 것이 좋지만,
        # 여기서는 간단한 예시만 제공

        import requests
        from bs4 import BeautifulSoup

        search_query = f"{company_name} 스타트업 대표 설립"
        url = f"https://www.google.com/search?q={search_query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 검색 결과에서 텍스트 추출
            snippets = soup.find_all('div', class_='BNeawe')
            all_text = ' '.join([s.get_text() for s in snippets])

            info = {}

            # 간단한 패턴 매칭 (네이버와 동일한 방식)
            import re

            # 대표자
            ceo_match = re.search(r'대표[:\s]+([가-힣]{2,4})', all_text)
            if ceo_match:
                info['ceo'] = ceo_match.group(1)

            # 설립일
            founded_match = re.search(r'(\d{4})년\s*설립', all_text)
            if founded_match:
                info['founded'] = f"{founded_match.group(1)}-01-01"

            return info

        return {}

    except Exception as e:
        print(f"  [WARNING] Google search failed: {e}")
        return {}

def enrich_company_info(company_name, existing_info):
    """
    기업 정보 보강 (기존 정보에 누락된 것만 검색)

    Args:
        company_name: 기업명
        existing_info: 기존 정보 (dict)

    Returns:
        dict: 보강된 정보
    """
    if not company_name:
        return existing_info

    # 누락된 필드 확인
    missing_fields = []
    for field in ['ceo', 'founded', 'location']:
        if not existing_info.get(field):
            missing_fields.append(field)

    if not missing_fields:
        print(f"  [INFO] All fields present, skipping search")
        return existing_info

    print(f"  [INFO] Searching for missing fields: {', '.join(missing_fields)}")

    # 네이버 검색 시도
    search_result = search_company_info_naver(company_name)

    # 구글 검색으로 보완 (네이버 결과가 없으면)
    if not search_result or not any(search_result.values()):
        print(f"  [INFO] Trying Google search...")
        search_result = search_company_info_google(company_name)

    # 기존 정보에 병합 (기존 값 우선)
    for key, value in search_result.items():
        if value and not existing_info.get(key):
            existing_info[key] = value
            print(f"  [FOUND] {key}: {value}")

    return existing_info

if __name__ == '__main__':
    # 테스트
    test_companies = ['카카오', '네이버', '토스']

    for company in test_companies:
        print(f"\n=== Testing: {company} ===")
        info = enrich_company_info(company, {})
        print(json.dumps(info, indent=2, ensure_ascii=False))
