#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 처리 결과 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def check_final_results():
    """최종 결과 확인"""

    print("="*60)
    print("Final Processing Results")
    print("="*60)

    # Google News 기사 조회
    result = supabase.table('investment_news_articles').select('*').eq('site_number', 100).execute()

    articles = result.data
    print(f"\nTotal Google News articles: {len(articles)}")

    # 점수 분석
    scores = [a.get('score', 0) for a in articles if a.get('score') is not None]
    has_company = sum(1 for a in articles if a.get('has_amount'))
    has_investors = sum(1 for a in articles if a.get('has_investors'))
    has_stage = sum(1 for a in articles if a.get('has_stage'))
    has_industry = sum(1 for a in articles if a.get('has_industry'))
    has_location = sum(1 for a in articles if a.get('has_location'))

    print(f"\n[Scores]")
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"  Average score: {avg_score:.2f} / 11")
        print(f"  Max score: {max(scores)}")
        print(f"  Min score: {min(scores)}")

        # 점수 분포
        score_dist = {}
        for s in scores:
            score_dist[s] = score_dist.get(s, 0) + 1

        print(f"\n[Score Distribution]")
        for score in sorted(score_dist.keys(), reverse=True):
            count = score_dist[score]
            print(f"  {score:2d}점: {count:3d}개 ({count/len(scores)*100:5.1f}%)")

    print(f"\n[Field Coverage]")
    print(f"  투자금액 (3점): {has_company:3d}개 ({has_company/len(articles)*100:5.1f}%)")
    print(f"  투자자   (3점): {has_investors:3d}개 ({has_investors/len(articles)*100:5.1f}%)")
    print(f"  투자단계 (2점): {has_stage:3d}개 ({has_stage/len(articles)*100:5.1f}%)")
    print(f"  업종     (1점): {has_industry:3d}개 ({has_industry/len(articles)*100:5.1f}%)")
    print(f"  지역     (1점): {has_location:3d}개 ({has_location/len(articles)*100:5.1f}%)")

    # 고득점 기사 샘플 (8점 이상)
    high_score = [a for a in articles if a.get('score', 0) >= 8]
    print(f"\n[High Score Articles (>= 8점): {len(high_score)}개]")
    for article in high_score[:5]:
        print(f"  {article.get('score')}점: {article['article_title'][:60]}...")

    # 저득점 기사 샘플 (0-2점)
    low_score = [a for a in articles if a.get('score', 0) <= 2]
    print(f"\n[Low Score Articles (<= 2점): {len(low_score)}개]")
    for article in low_score[:5]:
        print(f"  {article.get('score')}점: {article['article_title'][:60]}...")

    print(f"\n{'='*60}")
    print("Conclusion")
    print(f"{'='*60}")

    quality_rate = (has_company / len(articles)) * 100
    coverage_rate = (sum([has_company, has_investors, has_stage]) / (len(articles) * 3)) * 100

    print(f"\n1. 품질: 투자금액 포함률 {quality_rate:.1f}%")
    if quality_rate >= 40:
        print("   [OK] 품질 양호")
    else:
        print("   [WARN] 품질 낮음 - TheVC 검증 필요")

    print(f"\n2. 커버리지: 핵심 3개 필드 평균 {coverage_rate:.1f}%")
    if coverage_rate >= 30:
        print("   [OK] 커버리지 양호")
    else:
        print("   [WARN] 커버리지 낮음")

    print(f"\n3. 다음 단계:")
    print("   1) TheVC로 기업명/투자자 검증")
    print("   2) Naver API로 기업 정보 보강")
    print("   3) 점수 기반 최종 Deal 선정")


if __name__ == '__main__':
    check_final_results()
