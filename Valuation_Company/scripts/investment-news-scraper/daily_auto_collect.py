#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매일 자동 뉴스 수집 스케줄러 (완벽한 통합 버전 v3)

프로세스:
1. 5대 언론기관 웹 크롤링
2. Google Search로 추가 수집 (Gemini)
3. Gemini로 투자 뉴스 검증
4. investment_news_articles 테이블 저장
5. Deal 테이블 등록 (회사당 최고 점수 1개)
6. 누락 정보 채우기 (Gemini로 투자자, 주요사업)
7. 네이버 API로 추가 검증/보완
8. 네이버 뉴스 → 실제 언론사 변환
9. Deal 번호 재정렬
10. 이메일 발송

실행: python daily_auto_collect.py [--date YYYY-MM-DD]
"""

import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup
import codecs
from google import genai
from google.genai import types
import time
import json
import re
from urllib.parse import urlparse, quote

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv(override=True)  # .env 파일을 시스템 환경변수보다 우선


# 업종 대분류 카테고리 매핑
INDUSTRY_CATEGORIES = {
    'AI': ['AI', '인공지능', 'AI 기반', 'AI 에이전트', 'AI·양자', '머신러닝', '딥러닝', 'LLM', '생성형'],
    '헬스케어': ['헬스케어', '바이오', '의료', '제약', '건강', '체성분', '클리닉', '메디', '진단', '신약', '헬스'],
    '핀테크': ['핀테크', '금융', '공급망 금융', '자산', '보험', '페이', '결제', '증권', '인슈어'],
    '이커머스': ['이커머스', '커머스', 'M&A 플랫폼', '쇼핑', '리테일', '유통'],
    '모빌리티': ['모빌리티', '자동차', '리스', '렌트', '자율주행', '물류', '배송'],
    '뷰티/패션': ['뷰티', '스킨케어', '화장품', '패션', '의류'],
    '콘텐츠/엔터': ['콘텐츠', '웹툰', 'IP 제작', '엔터', '게임', '미디어', '영상'],
    '우주항공': ['위성', '우주', '항공', '에어로스페이스', '드론'],
    'IT/하드웨어': ['IT 기기', '하드웨어', '반도체', '센서', '로봇', '제조'],
    'SaaS/B2B': ['SaaS', '솔루션', '클라우드', 'B2B', 'HR', 'ERP'],
    '농업/푸드': ['스마트팜', '농업', '푸드', '식품', '푸드테크', '에어로포닉'],
    '에듀테크': ['에듀', '교육', '학습', '러닝'],
    '부동산/건설': ['부동산', '프롭', '건설', '건축', '인테리어'],
    '에너지/환경': ['에너지', '태양광', '배터리', '탄소', '환경', '그린', '수소', '친환경'],
}


def categorize_industry(raw_industry):
    """세부 업종을 대분류 카테고리로 매핑"""
    if not raw_industry:
        return None
    for category, keywords in INDUSTRY_CATEGORIES.items():
        for kw in keywords:
            if kw in raw_industry:
                return category
    return '기타'


# 투자단계 정규화 매핑
STAGE_MAP = {
    '시리즈 A': '시리즈A', '시리즈 B': '시리즈B', '시리즈 C': '시리즈C',
    '시리즈 D': '시리즈D', '시리즈 E': '시리즈E',
    '프리 A': '프리A', '프리 시드': '프리시드',
    'Series A': '시리즈A', 'Series B': '시리즈B', 'Series C': '시리즈C',
    'Series D': '시리즈D', 'Series E': '시리즈E',
    'Pre-A': '프리A', 'Pre A': '프리A',
    'Seed': '시드', 'Pre-Seed': '프리시드', 'Pre-seed': '프리시드',
    'Bridge': '브릿지', 'Pre-IPO': '프리IPO', 'pre-IPO': '프리IPO',
}
VALID_STAGES = {'프리시드', '시드', '프리A', '프리A 브릿지', '시리즈A', '시리즈B',
                '시리즈C', '시리즈D', '시리즈E', '프리IPO', 'M&A', '브릿지'}


def normalize_stage(raw_stage):
    """투자단계를 정규화 (띄어쓰기/영어 통일, 투자자명 오입력 제거)"""
    if not raw_stage:
        return None
    stage = raw_stage.strip()
    # 매핑 테이블에 있으면 변환
    if stage in STAGE_MAP:
        return STAGE_MAP[stage]
    # 유효한 stage면 그대로
    if stage in VALID_STAGES:
        return stage
    # 유효하지 않으면 null (투자자명 오입력 등)
    return None


# Supabase & Gemini 클라이언트
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 5대 언론기관
MEDIA_SITES = [
    {
        'id': 9,
        'name': '벤처스퀘어',
        'url': 'https://www.venturesquare.net/category/news/',
        'article_selector': 'article.post',
        'title_selector': 'h5 a',
        'link_selector': 'h5 a',
    },
    {
        'id': 11,
        'name': '스타트업투데이',
        'url': 'https://www.startuptoday.kr/news/articleList.html',
        'article_selector': 'div.article-list-content',
        'title_selector': 'h4.titles',
        'link_selector': 'a',
    },
    {
        'id': 13,
        'name': '아웃스탠딩',
        'url': 'https://outstanding.kr/',
        'article_selector': 'article',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
    },
    {
        'id': 10,
        'name': '플래텀',
        'url': 'https://platum.kr/',
        'article_selector': 'article',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
    },
    {
        'id': 1,
        'name': 'WOWTALE',
        'url': 'https://wowtale.net/',
        'article_selector': 'a.kb-advanced-heading-link',
        'title_selector': 'h2',
        'link_selector': 'self',  # 특수: article 요소 자체가 링크
    },
]


def log(message, level="INFO"):
    """로그 출력"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")


def extract_article_date(html_content, url):
    """기사 HTML에서 발행일 추출"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 메타 태그에서 날짜 추출
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        if date_meta:
            date_str = date_meta.get('content', '')
            return date_str.split('T')[0] if 'T' in date_str else date_str[:10]

        # time 태그
        time_tag = soup.find('time')
        if time_tag:
            datetime_attr = time_tag.get('datetime')
            if datetime_attr:
                return datetime_attr.split('T')[0] if 'T' in datetime_attr else datetime_attr[:10]

        return None
    except:
        return None


def verify_with_gemini(title, url):
    """Gemini로 투자 뉴스인지 검증"""
    prompt = f"""
다음 뉴스 제목이 스타트업 투자유치 뉴스인지 확인해주세요:

제목: {title}

JSON 형식으로만 답변:
{{
    "is_investment": true,
    "company": "회사명",
    "stage": "시드/프리A/시리즈A 등",
    "investors": "투자자명",
    "amount": 숫자만
}}

투자유치 뉴스가 아니면 {{"is_investment": false}}만 출력하세요.
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=256,
                response_mime_type='application/json'
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            result = json.loads(text)
            return result

        return None
    except Exception as e:
        # JSON 파싱 실패 시 키워드 기반 판단
        invest_keywords = ['투자', '유치', '펀딩', '시리즈', '라운드']
        if any(kw in title for kw in invest_keywords):
            return {'is_investment': True, 'company': None, 'stage': None, 'investors': None, 'amount': None}
        return {'is_investment': False}


def extract_deal_info_with_gemini(title, url):
    """Gemini로 뉴스에서 Deal 정보 추출"""
    prompt = f"""
다음 투자유치 뉴스에서 정보를 추출해주세요:

제목: {title}

JSON 형식으로만 답변:
{{
    "company_name": "회사명 (법인명)",
    "industry": "주요사업 (AI/헬스케어/핀테크 등)",
    "stage": "투자단계 (시드/프리A/시리즈A 등)",
    "investors": "투자자 (콤마로 구분)",
    "amount": "투자금액 (억원 숫자만)",
    "location": "지역",
    "employees": "직원수 (숫자만)"
}}

조건:
- 정보 없으면 null
- amount는 억원 단위 숫자만 (50억 → 50)
- employees는 숫자만
- 투자유치 뉴스가 아니면 company_name을 null로
- ⚠️ company_name은 반드시 법인명/회사명이어야 함 (서비스명/브랜드명/플랫폼명 금지!)
  예: "차즘을 운영하는 디자인앤프랙티스" → company_name은 "디자인앤프랙티스" (차즘 아님)
  예: "토스를 운영하는 비바리퍼블리카" → company_name은 "비바리퍼블리카" (토스 아님)
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=512,
                response_mime_type='application/json'
            )
        )

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            result = json.loads(text)
            # Gemini가 배열로 응답하는 경우 첫 번째 요소 사용
            if isinstance(result, list):
                result = result[0] if result else {}
            return result

        return None
    except Exception as e:
        log(f"    ⚠️ Gemini 추출 오류: {str(e)[:50]}", "WARN")
        return None


def calculate_score(info):
    """기사 점수 계산 (11점 만점)"""
    score = 0

    if info.get('amount'):
        score += 3
    if info.get('investors'):
        score += 3
    if info.get('stage'):
        score += 2
    if info.get('industry'):
        score += 1
    if info.get('location'):
        score += 1
    if info.get('employees'):
        score += 1

    return score


def extract_site_name_from_url(url):
    """URL에서 실제 언론사명 추출"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # og:site_name 메타 태그
            og_site = soup.find('meta', {'property': 'og:site_name'})
            if og_site and og_site.get('content'):
                return og_site.get('content').strip()

            # publisher 메타 태그
            publisher = soup.find('meta', {'name': 'publisher'})
            if publisher and publisher.get('content'):
                return publisher.get('content').strip()

        return None
    except:
        return None


# ============================================================
# Step 1: 5대 언론기관 웹 크롤링
# ============================================================
def step1_crawl_media_sites(target_date):
    """5대 언론기관에서 뉴스 크롤링"""
    log(f"Step 1: 5대 언론기관 크롤링 시작 (목표 날짜: {target_date})")

    all_articles = []

    for site in MEDIA_SITES:
        log(f"  📰 {site['name']} 크롤링 중...")

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(site['url'], headers=headers, timeout=10)

            if response.status_code != 200:
                log(f"    ❌ HTTP {response.status_code}", "ERROR")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            article_elements = soup.select(site['article_selector'])[:20]

            site_articles = 0
            for article in article_elements:
                try:
                    title_elem = article.select_one(site['title_selector'])

                    # link_selector가 'self'면 article 요소 자체가 링크
                    if site['link_selector'] == 'self':
                        link_elem = article
                    else:
                        link_elem = article.select_one(site['link_selector'])

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')

                    # 상대 경로 처리
                    if url.startswith('/'):
                        base_url = site['url'].split('?')[0].rsplit('/', 1)[0]
                        url = base_url + url

                    if not url.startswith('http'):
                        continue

                    # 투자 키워드 필터
                    invest_keywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드', 'Pre-A', '시드']
                    if any(kw in title for kw in invest_keywords):
                        all_articles.append({
                            'site_id': site['id'],
                            'site_name': site['name'],
                            'title': title,
                            'url': url,
                        })
                        site_articles += 1

                    time.sleep(0.3)
                except:
                    continue

            log(f"    ✅ {site_articles}개 발견")

        except Exception as e:
            log(f"    ❌ 크롤링 오류: {str(e)[:50]}", "ERROR")

        time.sleep(1)

    log(f"  📊 총 {len(all_articles)}개 기사 수집")
    return all_articles


# ============================================================
# Step 1.5: Google Search로 추가 수집 (Gemini Grounding)
# ============================================================
def step1_5_google_search(target_date, existing_urls):
    """Google Search로 추가 투자 뉴스 수집"""
    log(f"Step 1.5: Google Search 추가 수집")

    search_queries = [
        f"스타트업 투자유치 {target_date}",
        f"시리즈A 투자 {target_date}",
        f"벤처투자 유치 {target_date}",
        f"스타트업 펀딩 {target_date}",
    ]

    additional_articles = []

    for query in search_queries:
        log(f"  🔍 검색: {query[:30]}...")

        prompt = f"""
다음 검색어로 한국 스타트업 투자유치 뉴스를 찾아주세요:
"{query}"

최근 뉴스 중 실제 투자유치 발표 뉴스만 찾아서 JSON 배열로 답변하세요:
[
    {{
        "title": "기사 제목",
        "url": "기사 URL",
        "source": "언론사명"
    }}
]

조건:
- 실제 투자유치 발표 뉴스만 (단순 분석/전망 기사 제외)
- 한국 스타트업 관련만
- 최대 5개까지
- 뉴스가 없으면 빈 배열 []
"""

        try:
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=1024,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )

            if response and hasattr(response, 'text'):
                text = response.text.strip()

                # JSON 추출
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    results = json.loads(json_match.group())

                    for item in results:
                        url = item.get('url', '')

                        # 중복 체크
                        if url and url not in existing_urls:
                            additional_articles.append({
                                'site_id': 0,  # Google Search
                                'site_name': item.get('source', 'Google Search'),
                                'title': item.get('title', ''),
                                'url': url,
                            })
                            existing_urls.add(url)

                    log(f"    ✅ {len(results)}개 발견")
                else:
                    log(f"    ⚠️ 결과 없음")

        except Exception as e:
            log(f"    ❌ 검색 오류: {str(e)[:40]}", "ERROR")

        time.sleep(2)  # API 제한 고려

    log(f"  📊 Google Search로 {len(additional_articles)}개 추가 수집")
    return additional_articles


# ============================================================
# Step 2: Gemini 검증 + 저장
# ============================================================
def step2_verify_and_save(articles, target_date):
    """Gemini로 검증하고 investment_news_articles에 저장"""
    log(f"Step 2: Gemini 검증 및 저장")

    saved = 0

    for i, article in enumerate(articles, 1):
        log(f"  [{i}/{len(articles)}] {article['title'][:40]}...")

        # 와우테일 공지사항 제외
        if '[공지]' in article['title'] or '공지사항' in article['title']:
            log(f"    ⚠️ 공지사항 제외")
            continue

        # 중복 체크
        existing = supabase.table('investment_news_articles').select('id').eq('article_url', article['url']).execute()
        if existing.data:
            log(f"    ⚠️ 중복")
            continue

        # 날짜 추출
        try:
            article_response = requests.get(article['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            published_date = extract_article_date(article_response.content, article['url']) if article_response.status_code == 200 else None
        except:
            published_date = None

        # 날짜 필터
        if published_date != target_date:
            log(f"    ❌ 날짜 범위 밖 ({published_date})")
            continue

        # Gemini 검증
        gemini_result = verify_with_gemini(article['title'], article['url'])

        if gemini_result and gemini_result.get('is_investment'):
            # 저장
            try:
                supabase.table('investment_news_articles').insert({
                    'site_number': article['site_id'],
                    'site_name': article['site_name'],
                    'site_url': urlparse(article['url']).netloc,
                    'article_title': article['title'],
                    'article_url': article['url'],
                    'published_date': published_date,
                    'collected_at': datetime.now().isoformat(),  # 수집 시간 저장
                    'has_amount': gemini_result.get('amount') is not None,
                    'has_investors': gemini_result.get('investors') is not None,
                    'has_stage': gemini_result.get('stage') is not None,
                }).execute()

                saved += 1
                log(f"    ✅ 저장 완료")
            except Exception as e:
                log(f"    ❌ 저장 오류: {str(e)[:40]}", "ERROR")
        else:
            log(f"    ❌ 투자 뉴스 아님")

        time.sleep(1)

    log(f"  📊 {saved}개 저장 완료")
    return saved


# ============================================================
# Step 3: Deal 테이블 등록
# ============================================================
def step3_register_to_deals(target_date):
    """Deal 테이블에 등록 (회사당 최고 점수 1개)"""
    log(f"Step 3: Deal 테이블 등록")

    # 해당 날짜 뉴스 가져오기
    articles = supabase.table('investment_news_articles').select('*').eq('published_date', target_date).execute()

    if not articles.data:
        log(f"  ⚠️ 해당 날짜 뉴스 없음")
        return 0

    log(f"  📰 {len(articles.data)}개 뉴스 처리 중...")

    # 각 뉴스에서 정보 추출
    news_with_info = []

    for article in articles.data:
        info = extract_deal_info_with_gemini(article['article_title'], article['article_url'])

        if info and info.get('company_name'):
            score = calculate_score(info)
            news_with_info.append({
                'article': article,
                'info': info,
                'score': score
            })
            log(f"    ✅ {info['company_name']} (점수: {score})")

        time.sleep(0.8)

    log(f"  📊 {len(news_with_info)}개 회사 발견")

    # 회사별 최고 점수 선택
    company_best = {}
    for news in news_with_info:
        company = news['info']['company_name']
        score = news['score']

        if company not in company_best or score > company_best[company]['score']:
            company_best[company] = news

    # 기존 deals 가져오기 (점수 비교용)
    existing_deals = supabase.table('deals').select('*').execute()

    # 회사별 기존 deal 정보 저장 {회사명: {stage: deal_data}}
    existing_company_deals = {}
    existing_news_urls = set()

    for deal in existing_deals.data:
        company = deal['company_name']
        stage = deal.get('stage') or 'unknown'
        news_url = deal.get('news_url')

        if company not in existing_company_deals:
            existing_company_deals[company] = {}

        # 기존 deal의 점수 계산
        existing_score = 0
        if deal.get('amount'): existing_score += 3
        if deal.get('investors'): existing_score += 3
        if deal.get('stage'): existing_score += 2
        if deal.get('industry'): existing_score += 1
        if deal.get('location'): existing_score += 1

        existing_company_deals[company][stage] = {
            'id': deal['id'],
            'score': existing_score,
            'deal': deal
        }

        if news_url:
            existing_news_urls.add(news_url)

    last_deal = supabase.table('deals').select('number').order('number', desc=True).limit(1).execute()
    next_number = last_deal.data[0]['number'] + 1 if last_deal.data else 1

    registered = 0
    updated = 0

    for company, news in company_best.items():
        article = news['article']
        info = news['info']
        new_stage = normalize_stage(info.get('stage')) or 'unknown'
        new_score = news['score']
        news_url = article.get('article_url')

        # 1. 같은 뉴스 URL이면 중복
        if news_url in existing_news_urls:
            log(f"    ⚠️ {company}: 같은 뉴스 URL 존재")
            continue

        # 2. 회사가 존재하는지 확인
        if company in existing_company_deals:
            company_stages = existing_company_deals[company]

            # 같은 라운드가 있는지 확인
            if new_stage in company_stages:
                existing_info = company_stages[new_stage]
                existing_score = existing_info['score']

                # 점수 비교: 새 뉴스가 더 높으면 업데이트
                if new_score > existing_score:
                    log(f"    🔄 {company}: 더 높은 점수 뉴스 발견 ({existing_score} → {new_score})")

                    # 기존 deal 업데이트
                    new_industry = info.get('industry') or existing_info['deal'].get('industry')
                    supabase.table('deals').update({
                        'industry': new_industry,
                        'industry_category': categorize_industry(new_industry),
                        'investors': info.get('investors') or existing_info['deal'].get('investors'),
                        'amount': info.get('amount') or existing_info['deal'].get('amount'),
                        'location': info.get('location') or existing_info['deal'].get('location'),
                        'news_title': article['article_title'],
                        'news_url': article['article_url'],
                        'news_date': article['published_date'],
                        'site_name': article['site_name'],
                    }).eq('id', existing_info['id']).execute()

                    updated += 1
                    log(f"    ✅ {company} 업데이트 완료")
                else:
                    log(f"    ⚠️ {company}: 같은 라운드({new_stage}) 이미 존재 (기존 점수 {existing_score} >= 새 점수 {new_score})")
                continue

            else:
                # 새로운 투자 라운드
                log(f"    🆕 {company}: 새로운 투자 라운드({new_stage}) 발견!")

        # 신규 등록
        try:
            supabase.table('deals').insert({
                'number': next_number,
                'company_name': company,
                'industry': info.get('industry'),
                'industry_category': categorize_industry(info.get('industry')),
                'stage': normalize_stage(info.get('stage')),
                'investors': info.get('investors'),
                'amount': info.get('amount'),
                'location': info.get('location'),
                'news_title': article['article_title'],
                'news_url': article['article_url'],
                'news_date': article['published_date'],
                'site_name': article['site_name'],
            }).execute()

            log(f"    ✅ {company} 등록 (#{next_number})")

            # 등록된 회사의 stage 정보 업데이트
            if company not in existing_company_deals:
                existing_company_deals[company] = {}
            existing_company_deals[company][new_stage] = {'score': new_score}
            existing_news_urls.add(news_url)

            next_number += 1
            registered += 1

        except Exception as e:
            log(f"    ❌ {company} 오류: {str(e)[:40]}", "ERROR")

    log(f"  📊 신규 {registered}개 등록, {updated}개 업데이트")
    return registered + updated


# ============================================================
# Step 4: 누락 정보 채우기 (Gemini로 뉴스 본문에서 추출)
# ============================================================
def step4_fill_missing_info():
    """투자자 및 주요사업 정보 채우기"""
    log(f"Step 4: 누락 정보 채우기")

    # 정보가 부족한 Deal 가져오기
    deals = supabase.table('deals').select('*').or_(
        'investors.is.null,industry.is.null,industry.eq.-,investment_reason.is.null'
    ).execute()

    if not deals.data:
        log(f"  ✅ 누락 정보 없음")
        return

    log(f"  📊 정보 부족한 Deal: {len(deals.data)}개")

    updated = 0

    for deal in deals.data:
        company = deal['company_name']
        news_url = deal.get('news_url')
        news_title = deal.get('news_title', '')

        if not news_url:
            log(f"    ⚠️ {company}: URL 없음")
            continue

        log(f"    🔍 {company}...")

        # 뉴스 본문 크롤링
        try:
            response = requests.get(news_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:15]])
            else:
                content = ""
        except:
            content = ""

        # Gemini로 정보 추출
        prompt = f"""
다음 투자유치 뉴스에서 정보를 추출하세요:

제목: {news_title}
본문: {content[:2000]}

JSON 형식으로만 답변:
{{
    "investors": "투자자명 (콤마 구분, 없으면 null)",
    "industry": "주요사업 (2-4단어, 없으면 null)",
    "investment_reason": "이 회사가 투자를 받은 핵심 이유 (기술력/시장성/매출성장 등 1문장, 없으면 null)"
}}
"""

        try:
            gemini_response = gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=256,
                    response_mime_type='application/json'
                )
            )

            if gemini_response and hasattr(gemini_response, 'text'):
                info = json.loads(gemini_response.text.strip())
                if isinstance(info, list):
                    info = info[0] if info else {}

                update_data = {}

                if info.get('investors') and not deal.get('investors'):
                    update_data['investors'] = info['investors']

                if info.get('industry') and (not deal.get('industry') or deal.get('industry') == '-'):
                    update_data['industry'] = info['industry']
                    update_data['industry_category'] = categorize_industry(info['industry'])

                if info.get('investment_reason') and info['investment_reason'] != 'null':
                    update_data['investment_reason'] = info['investment_reason']

                if update_data:
                    supabase.table('deals').update(update_data).eq('id', deal['id']).execute()
                    log(f"      ✅ 업데이트: {update_data}")
                    updated += 1
                else:
                    log(f"      ⚠️ 추가 정보 없음")

        except Exception as e:
            log(f"      ❌ 오류: {str(e)[:40]}", "ERROR")

        time.sleep(1)

    log(f"  ✅ {updated}개 정보 채움")


# ============================================================
# Step 5: 네이버 뉴스 → 실제 언론사 변환
# ============================================================
def step5_fix_naver_news():
    """네이버 뉴스로 표시된 항목의 실제 언론사 추출"""
    log(f"Step 5: 네이버 뉴스 언론사 변환")

    result = supabase.table('deals').select('id,company_name,site_name,news_url').eq('site_name', '네이버 뉴스').execute()

    if not result.data:
        log(f"  ✅ 변환 필요 없음")
        return

    log(f"  📊 {len(result.data)}개 항목 처리 중...")

    updated = 0
    for deal in result.data:
        real_site = extract_site_name_from_url(deal['news_url'])

        if real_site:
            supabase.table('deals').update({'site_name': real_site}).eq('id', deal['id']).execute()
            updated += 1

        time.sleep(0.5)

    log(f"  ✅ {updated}개 변환 완료")


# ============================================================
# Step 5.5: 네이버 API로 데이터 정제/검증
# ============================================================
def step5_5_naver_api_enrichment():
    """네이버 뉴스 API로 데이터 정제 및 추가 정보 수집"""
    log(f"Step 5.5: 네이버 API 데이터 정제")

    # 네이버 API 키 확인
    naver_client_id = os.getenv("NAVER_CLIENT_ID")
    naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")

    if not naver_client_id or not naver_client_secret:
        log(f"  ⚠️ 네이버 API 키 미설정 (NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)")
        log(f"  ⚠️ https://developers.naver.com 에서 API 키 발급 필요")
        return

    # 투자자 정보가 없는 Deal 가져오기
    deals_to_enrich = supabase.table('deals').select('*').or_(
        'investors.is.null,industry.is.null,industry.eq.-'
    ).execute()

    if not deals_to_enrich.data:
        log(f"  ✅ 정제 필요 없음")
        return

    log(f"  📊 {len(deals_to_enrich.data)}개 Deal 정제 중...")

    enriched = 0

    for deal in deals_to_enrich.data:
        company = deal['company_name']
        log(f"    🔍 {company}...")

        # 네이버 뉴스 검색
        search_query = f"{company} 투자"
        url = f"https://openapi.naver.com/v1/search/news.json?query={quote(search_query)}&display=5&sort=date"

        headers = {
            "X-Naver-Client-Id": naver_client_id,
            "X-Naver-Client-Secret": naver_client_secret
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                if items:
                    # 가장 관련성 높은 기사에서 정보 추출
                    best_item = items[0]
                    title = best_item.get('title', '').replace('<b>', '').replace('</b>', '')
                    description = best_item.get('description', '').replace('<b>', '').replace('</b>', '')

                    # Gemini로 정보 추출
                    combined_text = f"제목: {title}\n내용: {description}"

                    extract_prompt = f"""
다음 뉴스에서 투자 정보를 추출하세요:
{combined_text}

JSON 형식으로만 답변:
{{
    "investors": "투자자명 (없으면 null)",
    "industry": "주요사업 (2-3단어, 없으면 null)",
    "amount": "투자금액 (억원 숫자만, 없으면 null)"
}}
"""
                    extract_response = gemini_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=extract_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0,
                            max_output_tokens=256,
                            response_mime_type='application/json'
                        )
                    )

                    if extract_response and hasattr(extract_response, 'text'):
                        info = json.loads(extract_response.text.strip())
                        if isinstance(info, list):
                            info = info[0] if info else {}

                        # 업데이트할 필드 결정
                        update_data = {}

                        if info.get('investors') and not deal.get('investors'):
                            update_data['investors'] = info['investors']

                        if info.get('industry') and (not deal.get('industry') or deal.get('industry') == '-'):
                            update_data['industry'] = info['industry']
                            update_data['industry_category'] = categorize_industry(info['industry'])

                        if info.get('amount') and not deal.get('amount'):
                            update_data['amount'] = info['amount']

                        if update_data:
                            supabase.table('deals').update(update_data).eq('id', deal['id']).execute()
                            log(f"      ✅ 업데이트: {list(update_data.keys())}")
                            enriched += 1
                        else:
                            log(f"      ⚠️ 추가 정보 없음")

                else:
                    log(f"      ⚠️ 검색 결과 없음")

            else:
                log(f"      ❌ API 오류: {response.status_code}", "ERROR")

        except Exception as e:
            log(f"      ❌ 오류: {str(e)[:40]}", "ERROR")

        time.sleep(0.5)  # API 제한 고려

    log(f"  ✅ {enriched}개 정제 완료")


# ============================================================
# Step 6: Deal 번호 재정렬
# ============================================================
def step6_renumber_deals():
    """Deal 번호를 최신순으로 재정렬"""
    log(f"Step 6: Deal 번호 재정렬")

    deals = supabase.table('deals').select('*').order('news_date', desc=True).order('id', desc=True).execute()

    log(f"  📊 총 {len(deals.data)}개 Deal 재정렬 중...")

    # Step 1: 음수로 변경 (중복 방지)
    for i, deal in enumerate(deals.data, 1):
        supabase.table('deals').update({'number': -i}).eq('id', deal['id']).execute()

    # Step 2: 양수로 변경
    for new_number, deal in enumerate(deals.data, 1):
        supabase.table('deals').update({'number': new_number}).eq('id', deal['id']).execute()

    log(f"  ✅ 최신순 1~{len(deals.data)}번 재정렬 완료")


# ============================================================
# 메인 실행
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='매일 자동 뉴스 수집')
    parser.add_argument('--date', type=str, help='수집 대상 날짜 (YYYY-MM-DD)', default=None)
    args = parser.parse_args()

    # 대상 날짜 결정 (KST 기준)
    KST = timezone(timedelta(hours=9))
    if args.date:
        target_date = args.date
    else:
        # 기본: KST 기준 어제 (GitHub Actions는 UTC이므로 KST 변환 필수)
        target_date = (datetime.now(KST) - timedelta(days=1)).strftime('%Y-%m-%d')

    print("=" * 70)
    print("📰 매일 자동 뉴스 수집 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 수집 대상 날짜: {target_date}")
    print("=" * 70)

    try:
        # Step 1: 웹 크롤링
        articles = step1_crawl_media_sites(target_date)

        # Step 1.5: Google Search 추가 수집
        existing_urls = {a['url'] for a in articles}
        google_articles = step1_5_google_search(target_date, existing_urls)
        articles.extend(google_articles)

        if articles:
            # Step 2: 검증 및 저장
            saved = step2_verify_and_save(articles, target_date)

            # Step 3: Deal 등록 (저장된 뉴스 없어도 시도 - 이미 저장된 뉴스가 있을 수 있음)
            registered = step3_register_to_deals(target_date)

            # Step 4: 누락 정보 채우기
            step4_fill_missing_info()

            # Step 5: 네이버 뉴스 변환
            step5_fix_naver_news()

            # Step 5.5: 네이버 API로 데이터 정제
            step5_5_naver_api_enrichment()

            # Step 6: 번호 재정렬
            step6_renumber_deals()

        print("\n" + "=" * 70)
        print("✅ 모든 작업 완료!")
        print("=" * 70)

    except Exception as e:
        log(f"오류 발생: {str(e)}", "ERROR")
        raise


if __name__ == '__main__':
    main()
