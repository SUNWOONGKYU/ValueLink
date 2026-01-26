#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
더브이씨(TheVC.kr) 실시간 조회
- 투자받은 기업 정보 조회
- 투자자 정보 조회 및 검증
"""

import requests
from bs4 import BeautifulSoup
import re
import time


def search_company_on_thevc(company_name):
    """
    더브이씨에서 투자받은 기업 정보 조회

    Args:
        company_name: 기업명

    Returns:
        {
            'ceo': '대표자명',
            'founded': '설립일',
            'location': '위치',
            'industry': '업종',
            'description': '설명',
            'source': 'thevc.kr'
        }
    """
    print(f"\n[TheVC] Searching company: {company_name}")

    try:
        # 더브이씨 검색
        search_url = f"https://thevc.kr/s/{company_name}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  [WARN] HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 기업 정보 추출
        info = {}

        # 페이지 전체 텍스트에서 정보 추출
        page_text = soup.get_text()

        # 대표자 찾기
        ceo_patterns = [
            r'대표[:\s]+([가-힣]{2,4})',
            r'CEO[:\s]+([가-힣]{2,4})',
            r'대표이사[:\s]+([가-힣]{2,4})'
        ]
        for pattern in ceo_patterns:
            match = re.search(pattern, page_text)
            if match:
                info['ceo'] = match.group(1)
                break

        # 설립일 찾기
        founded_patterns = [
            r'(\d{4})년\s*설립',
            r'설립[:\s]+(\d{4})',
            r'Founded[:\s]+(\d{4})'
        ]
        for pattern in founded_patterns:
            match = re.search(pattern, page_text)
            if match:
                info['founded'] = f"{match.group(1)}-01-01"
                break

        # 위치 찾기
        location_keywords = ['서울', '판교', '강남', '부산', '대구', '광주', '대전', '인천']
        for keyword in location_keywords:
            if keyword in page_text:
                info['location'] = keyword
                break

        # 업종 찾기
        industry_keywords = [
            'AI', '인공지능', '헬스케어', '의료', '핀테크', '금융',
            '푸드테크', '식품', '이커머스', '커머스', 'SaaS', '클라우드',
            '모빌리티', '로봇', 'IoT', '블록체인', '게임', '교육', '에듀테크'
        ]
        found_industries = [kw for kw in industry_keywords if kw in page_text]
        if found_industries:
            info['industry'] = ', '.join(found_industries[:3])  # 최대 3개

        # 설명 찾기 (메타 태그 또는 첫 문단)
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            info['description'] = meta_desc['content'][:200]

        info['source'] = 'thevc.kr'

        print(f"  [SUCCESS] Found: {info}")
        return info if info else None

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return None


def search_investor_on_thevc(investor_name):
    """
    더브이씨에서 투자자 정보 조회 및 정식 명칭 확인

    Args:
        investor_name: 투자자명 (약칭 가능)

    Returns:
        {
            'official_name': '정식 투자사명',
            'website': '웹사이트',
            'focus_industries': '관심 업종',
            'investment_stage': '투자 단계',
            'source': 'thevc.kr'
        }
    """
    print(f"\n[TheVC] Searching investor: {investor_name}")

    try:
        # 더브이씨 투자사 검색
        search_url = f"https://thevc.kr/s/{investor_name}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  [WARN] HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 투자사 정보 추출
        info = {}
        page_text = soup.get_text()

        # 정식 명칭 찾기 (제목, h1, h2 등)
        title_tags = soup.find_all(['h1', 'h2', 'title'])
        for tag in title_tags:
            text = tag.get_text().strip()
            if any(kw in text for kw in ['벤처스', '캐피탈', 'VC', 'Ventures', '인베스트먼트']):
                info['official_name'] = text
                break

        # 웹사이트 찾기
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if any(domain in href for domain in ['.com', '.co.kr', '.kr', '.vc']):
                if 'thevc.kr' not in href:  # 더브이씨 자체 링크 제외
                    info['website'] = href
                    break

        # 관심 업종 찾기
        industry_keywords = [
            'AI', '헬스케어', '핀테크', '푸드테크', '이커머스',
            'SaaS', '모빌리티', '로봇', 'IoT', '블록체인'
        ]
        found_industries = [kw for kw in industry_keywords if kw in page_text]
        if found_industries:
            info['focus_industries'] = ', '.join(found_industries)

        # 투자 단계 찾기
        stage_keywords = ['시드', 'Seed', '프리A', 'Pre-A', '시리즈A', 'Series A', '시리즈B', 'Series B']
        found_stages = [kw for kw in stage_keywords if kw in page_text]
        if found_stages:
            info['investment_stage'] = ', '.join(found_stages)

        info['source'] = 'thevc.kr'

        print(f"  [SUCCESS] Found: {info}")
        return info if info else None

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return None


def enrich_deal_with_thevc(deal):
    """
    Deal 데이터를 더브이씨 정보로 보강

    Args:
        deal: {
            'company_name': '기업명',
            'investors': '투자자1, 투자자2',
            'ceo': None,
            'founded': None,
            ...
        }

    Returns:
        보강된 deal 객체
    """
    print(f"\n{'='*60}")
    print(f"Enriching deal: {deal.get('company_name')}")
    print(f"{'='*60}")

    # 1. 기업 정보 보강
    if deal.get('company_name'):
        company_info = search_company_on_thevc(deal['company_name'])

        if company_info:
            # 없는 정보만 채우기
            if not deal.get('ceo') and company_info.get('ceo'):
                deal['ceo'] = company_info['ceo']
                print(f"  [UPDATE] CEO: {deal['ceo']}")

            if not deal.get('founded') and company_info.get('founded'):
                deal['founded'] = company_info['founded']
                print(f"  [UPDATE] Founded: {deal['founded']}")

            if not deal.get('location') and company_info.get('location'):
                deal['location'] = company_info['location']
                print(f"  [UPDATE] Location: {deal['location']}")

            if not deal.get('industry') and company_info.get('industry'):
                deal['industry'] = company_info['industry']
                print(f"  [UPDATE] Industry: {deal['industry']}")

    # Rate limiting
    time.sleep(1)

    # 2. 투자자 정식 명칭 확인
    if deal.get('investors'):
        investor_list = [inv.strip() for inv in deal['investors'].split(',')]
        validated_investors = []

        for investor in investor_list:
            investor_info = search_investor_on_thevc(investor)

            if investor_info and investor_info.get('official_name'):
                validated_investors.append(investor_info['official_name'])
                print(f"  [VALIDATE] '{investor}' → '{investor_info['official_name']}'")
            else:
                validated_investors.append(investor)  # 못 찾으면 원본 유지

            time.sleep(1)  # Rate limiting

        deal['investors'] = ', '.join(validated_investors)

    print(f"\n[RESULT] Enriched deal:")
    print(f"  Company: {deal.get('company_name')}")
    print(f"  CEO: {deal.get('ceo')}")
    print(f"  Founded: {deal.get('founded')}")
    print(f"  Location: {deal.get('location')}")
    print(f"  Industry: {deal.get('industry')}")
    print(f"  Investors: {deal.get('investors')}")

    return deal


# 테스트
if __name__ == '__main__':
    print("="*60)
    print("TheVC.kr Real-time Search Test")
    print("="*60)

    # 테스트 1: 기업 검색
    test_company = "테크이노"  # 예시 - 실제 기업명으로 교체 필요
    company_result = search_company_on_thevc(test_company)

    # 테스트 2: 투자자 검색
    test_investor = "알토스"
    investor_result = search_investor_on_thevc(test_investor)

    # 테스트 3: Deal 보강
    test_deal = {
        'company_name': '테크이노',
        'investors': '알토스, 삼성벤처',
        'amount': '100억원',
        'stage': '시리즈A',
        'ceo': None,
        'founded': None,
        'location': None,
        'industry': None
    }

    enriched_deal = enrich_deal_with_thevc(test_deal)

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
