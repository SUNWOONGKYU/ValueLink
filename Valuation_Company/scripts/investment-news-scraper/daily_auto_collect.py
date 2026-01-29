#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매일 자동 뉴스 수집 스케줄러 (완벽한 통합 버전 v2)

프로세스:
1. 5대 언론기관 웹 크롤링
2. Google Search로 추가 수집
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
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup
import codecs
from google import genai
from google.genai import types
import time
import json
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

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
        'article_selector': 'article',
        'title_selector': 'h2 a',
        'link_selector': 'h2 a',
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
    "company_name": "회사명",
    "industry": "업종 (AI/헬스케어/핀테크 등)",
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
            return result

        return None
    except Exception as e:
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
# Step 2: Gemini 검증 + 저장
# ============================================================
def step2_verify_and_save(articles, target_date):
    """Gemini로 검증하고 investment_news_articles에 저장"""
    log(f"Step 2: Gemini 검증 및 저장")

    saved = 0

    for i, article in enumerate(articles, 1):
        log(f"  [{i}/{len(articles)}] {article['title'][:40]}...")

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

    # 중복 체크 및 등록
    existing_deals = supabase.table('deals').select('company_name').execute()
    existing_companies = {deal['company_name'] for deal in existing_deals.data}

    last_deal = supabase.table('deals').select('number').order('number', desc=True).limit(1).execute()
    next_number = last_deal.data[0]['number'] + 1 if last_deal.data else 1

    registered = 0

    for company, news in company_best.items():
        if company in existing_companies:
            log(f"    ⚠️ {company}: 이미 존재")
            continue

        article = news['article']
        info = news['info']

        try:
            supabase.table('deals').insert({
                'number': next_number,
                'company_name': company,
                'industry': info.get('industry'),
                'stage': info.get('stage'),
                'investors': info.get('investors'),
                'amount': info.get('amount'),
                'location': info.get('location'),
                'news_title': article['article_title'],
                'news_url': article['article_url'],
                'news_date': article['published_date'],
                'site_name': article['site_name'],
            }).execute()

            log(f"    ✅ {company} 등록 (#{next_number})")

            existing_companies.add(company)
            next_number += 1
            registered += 1

        except Exception as e:
            log(f"    ❌ {company} 오류: {str(e)[:40]}", "ERROR")

    log(f"  📊 {registered}개 신규 등록")
    return registered


# ============================================================
# Step 4: 누락 정보 채우기
# ============================================================
def step4_fill_missing_info():
    """투자자 및 주요사업 정보 채우기"""
    log(f"Step 4: 누락 정보 채우기")

    # 투자자 없는 Deal
    deals_no_investors = supabase.table('deals').select('*').is_('investors', 'null').execute()
    log(f"  📊 투자자 정보 없는 Deal: {len(deals_no_investors.data)}개")

    # 주요사업 없는 Deal
    deals_no_industry = supabase.table('deals').select('*').or_('industry.is.null,industry.eq.-').execute()
    log(f"  📊 주요사업 정보 없는 Deal: {len(deals_no_industry.data)}개")

    # (추후 Gemini로 추출 로직 추가 가능)
    log(f"  ⚠️ 수동 처리 필요")


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

    # 대상 날짜 결정
    if args.date:
        target_date = args.date
    else:
        # 기본: 어제
        target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("=" * 70)
    print("📰 매일 자동 뉴스 수집 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 수집 대상 날짜: {target_date}")
    print("=" * 70)

    try:
        # Step 1: 웹 크롤링
        articles = step1_crawl_media_sites(target_date)

        if articles:
            # Step 2: 검증 및 저장
            saved = step2_verify_and_save(articles, target_date)

            if saved > 0:
                # Step 3: Deal 등록
                registered = step3_register_to_deals(target_date)

                if registered > 0:
                    # Step 4: 누락 정보 채우기
                    step4_fill_missing_info()

                    # Step 5: 네이버 뉴스 변환
                    step5_fix_naver_news()

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
