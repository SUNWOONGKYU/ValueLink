#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 2: 각 기업의 최적 기사 선정 및 Deal 테이블 저장
"""

import os
import sys
import csv
import re
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from collections import defaultdict

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

# 센서블박스 기업 데이터 (Gemini 추출 데이터)
GEMINI_CSV = 'sensible_companies_2026_01_GEMINI.csv'

# 사이트 랭킹 (상위 10개)
SITE_RANKING = {
    '벤처스퀘어': 1,
    '스타트업투데이': 2,
    '아웃스탠딩': 3,
    '더브이씨': 4,
    '스타트업엔': 5,
    '블로터': 6,
    '이코노미스트': 7,
    '플래텀': 8,
    'AI타임스': 9,
    '뉴스톱': 10,
    'WOWTALE': 11,
    '더벨': 12,
}


def score_article(article):
    """
    기사 점수 계산 (08_article-selection.md 규칙)

    점수 배점:
    - 투자금액: 3점
    - 투자자: 3점
    - 투자단계: 2점
    - 업종: 1점
    - 지역: 1점
    - 직원수: 1점
    총 11점 만점
    """

    title = article['article_title']
    score = 0

    # 투자금액 (3점)
    amount_patterns = [
        r'\d+억\s*원', r'\d+억원', r'\$\d+M', r'\d+만\s*달러'
    ]
    if any(re.search(pattern, title) for pattern in amount_patterns):
        score += 3

    # 투자자 (3점) - VC, 회사명 등
    investor_keywords = [
        '벤처스', '투자', '캐피탈', 'VC', '파트너스', '인베스트먼트',
        '알토스', '삼성', 'SBI', 'KB', 'NH', '본엔젤스', 'D2SF'
    ]
    if any(kw in title for kw in investor_keywords):
        score += 3

    # 투자단계 (2점)
    stage_keywords = ['시리즈', 'Series', '프리A', '프리IPO', '시드', 'Seed', '라운드']
    if any(kw in title for kw in stage_keywords):
        score += 2

    # 업종 (1점)
    sector_keywords = ['AI', '헬스케어', '핀테크', '푸드테크', '이커머스', '로봇', '바이오']
    if any(kw in title for kw in sector_keywords):
        score += 1

    # 지역 (1점)
    location_keywords = ['판교', '강남', '서울', '부산', '대구', '대전']
    if any(kw in title for kw in location_keywords):
        score += 1

    # 직원수 (1점)
    employee_patterns = [r'직원\s*\d+명', r'임직원\s*\d+명', r'팀원\s*\d+명']
    if any(re.search(pattern, title) for pattern in employee_patterns):
        score += 1

    return score


def select_best_article(articles):
    """
    여러 기사 중 최적 기사 선정

    우선순위:
    1. 점수 (11점 만점)
    2. 글자수 (많을수록)
    3. 발행일 (최신)
    4. 사이트 랭킹 (상위)
    """

    if not articles:
        return None

    if len(articles) == 1:
        return articles[0]

    # 점수 계산
    for article in articles:
        article['score'] = score_article(article)
        article['title_length'] = len(article['article_title'])
        article['site_rank'] = SITE_RANKING.get(article['site_name'], 99)

    # 정렬: 점수 desc, 글자수 desc, 발행일 desc, 사이트랭킹 asc
    sorted_articles = sorted(
        articles,
        key=lambda x: (
            -x['score'],
            -x['title_length'],
            x['published_date'],
            x['site_rank']
        ),
        reverse=True
    )

    best = sorted_articles[0]

    return best


def extract_investment_data(article, company_data):
    """
    기사 제목에서 투자 데이터 추출
    """

    title = article['article_title']

    # 투자금액 추출
    amount = None
    amount_match = re.search(r'(\d+)억\s*원', title)
    if amount_match:
        amount = f"{amount_match.group(1)}억원"

    # 투자단계 추출
    stage = None
    stage_patterns = {
        '시리즈A': r'시리즈\s*A',
        '시리즈B': r'시리즈\s*B',
        '시리즈C': r'시리즈\s*C',
        '프리A': r'프리\s*A',
        '프리IPO': r'프리\s*IPO',
        '시드': r'시드|Seed'
    }
    for stage_name, pattern in stage_patterns.items():
        if re.search(pattern, title):
            stage = stage_name
            break

    # 센서블박스 데이터에서 가져오기 (기사에 없으면)
    if company_data:
        if not amount and company_data.get('신규'):
            amount = company_data['신규']
        if not stage and company_data.get('단계'):
            stage = company_data['단계']

    # 투자자는 센서블박스 데이터 우선
    investors = company_data.get('투자자', '') if company_data else ''

    # 업종은 센서블박스 데이터
    sector = company_data.get('주요사업', '') if company_data else ''

    return {
        'amount': amount,
        'stage': stage,
        'investors': investors,
        'sector': sector
    }


def main():
    print("=" * 80)
    print("STEP 2: 각 기업의 최적 기사 선정 및 Deal 테이블 저장")
    print("=" * 80)

    # 1. 센서블박스 기업 데이터 로드
    print("\n📂 센서블박스 기업 데이터 로드 중...")
    company_dict = {}

    with open(GEMINI_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_name = row['기업명']
            company_dict[company_name] = row

    print(f"   ✅ {len(company_dict)}개 기업 로드")

    # 2. investment_news_articles 테이블에서 모든 기사 로드
    print("\n📰 수집된 기사 로드 중...")
    result = supabase.table("investment_news_articles").select("*").execute()
    all_articles = result.data

    print(f"   ✅ {len(all_articles)}개 기사 로드")

    # 3. 기업명별로 기사 그룹핑
    print("\n📊 기업별 기사 그룹핑 중...")
    company_articles = defaultdict(list)

    for article in all_articles:
        # 기업명 찾기
        for company_name in company_dict.keys():
            if company_name in article['article_title']:
                company_articles[company_name].append(article)
                break

    print(f"   ✅ {len(company_articles)}개 기업 그룹핑 완료")

    # 4. 각 기업별 최적 기사 선정
    print("\n🎯 기업별 최적 기사 선정 중...\n")

    selected_articles = []

    for idx, (company_name, articles) in enumerate(sorted(company_articles.items()), 1):
        print(f"[{idx:3d}/{len(company_articles)}] {company_name:25s} ({len(articles)}개 기사)", end=' ')

        # 최적 기사 선정
        best = select_best_article(articles)

        if best:
            print(f"→ 점수: {best['score']}/11, 사이트: {best['site_name']}")

            # 투자 데이터 추출
            investment_data = extract_investment_data(best, company_dict.get(company_name))

            selected_articles.append({
                'company_name': company_name,
                'article': best,
                'investment_data': investment_data
            })
        else:
            print("→ ❌ 기사 없음")

    print(f"\n   ✅ {len(selected_articles)}개 기업의 최적 기사 선정 완료")

    # 5. Deal 테이블에 저장
    print("\n💾 Deal 테이블에 저장 중...")

    saved = 0
    errors = 0

    for item in selected_articles:
        company_name = item['company_name']
        article = item['article']
        inv_data = item['investment_data']

        # Deal 레코드 생성
        deal_record = {
            'company_name': company_name,
            'sector': inv_data['sector'][:100] if inv_data['sector'] else None,
            'stage': inv_data['stage'],
            'investors': inv_data['investors'][:200] if inv_data['investors'] else None,
            'amount': inv_data['amount'],
            'region': None,  # 기사에서 추출 안 됨
            'employees': None,  # 기사에서 추출 안 됨
            'news_title': article['article_title'],
            'news_url': article['article_url'],
            'news_site': article['site_name'],
            'published_date': article['published_date'],
            'created_at': datetime.now().isoformat()
        }

        try:
            # 중복 확인 (기업명 기준)
            existing = supabase.table("deals")\
                .select("id")\
                .eq("company_name", company_name)\
                .execute()

            if not existing.data:
                supabase.table("deals").insert(deal_record).execute()
                saved += 1
            else:
                # 업데이트
                supabase.table("deals")\
                    .update(deal_record)\
                    .eq("company_name", company_name)\
                    .execute()
                saved += 1
        except Exception as e:
            print(f"   ❌ {company_name} 저장 실패: {e}")
            errors += 1

    print(f"   ✅ {saved}개 저장 완료")
    if errors > 0:
        print(f"   ❌ {errors}개 오류")

    # 6. 최종 통계
    print("\n" + "=" * 80)
    print("STEP 2 완료!")
    print("=" * 80)

    deal_count = supabase.table("deals").select("id", count="exact").execute()

    print(f"\n📊 최종 통계:")
    print(f"   - 분석한 기사: {len(all_articles)}개")
    print(f"   - 커버한 기업: {len(company_articles)}개")
    print(f"   - Deal 테이블 레코드: {deal_count.count}개")
    print(f"\n✅ 각 기업의 최고 품질 투자 뉴스가 Deal 테이블에 저장되었습니다!")


if __name__ == '__main__':
    main()
