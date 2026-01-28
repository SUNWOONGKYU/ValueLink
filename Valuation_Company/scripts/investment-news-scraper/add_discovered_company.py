#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
발굴한 신규 기업 Deal 테이블에 추가 (디앤티테크솔루션)
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

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

print("=" * 80)
print("발굴한 신규 기업 Deal 테이블에 추가")
print("=" * 80)

# 디앤티테크솔루션 기사 찾기
articles = supabase.table("investment_news_articles")\
    .select("*")\
    .ilike("article_title", "%디앤티%")\
    .execute()

if not articles.data:
    print("\n❌ 디앤티테크솔루션 기사를 찾을 수 없습니다.")
else:
    article = articles.data[0]
    print(f"\n✅ 기사 발견:")
    print(f"  제목: {article['article_title']}")
    print(f"  URL: {article['article_url']}")
    print(f"  사이트: {article['site_name']}")

    # Deal 레코드 생성
    deal = {
        'company_name': '디앤티테크솔루션',
        'industry': '산업 공정 자동화 솔루션 개발기업',
        'stage': '프리A',
        'investors': '리인인베스트먼트, L&S벤처캐피탈, 킹고투자파트너스 등',
        'amount': 64.0,
        'news_title': article['article_title'],
        'news_url': article['article_url'],
        'site_name': article['site_name'],
        'news_date': article['published_date'],
        'created_at': datetime.now().isoformat()
    }

    # 중복 확인
    existing = supabase.table("deals")\
        .select("id")\
        .eq("company_name", "디앤티테크솔루션")\
        .execute()

    if not existing.data:
        try:
            supabase.table("deals").insert(deal).execute()
            print(f"\n✅ Deal 테이블에 추가 완료!")
            print(f"  기업명: 디앤티테크솔루션")
            print(f"  투자자: {deal['investors']}")
            print(f"  투자금액: {deal['amount']}억원")
            print(f"  단계: {deal['stage']}")
        except Exception as e:
            print(f"\n❌ DB 오류: {e}")
    else:
        print(f"\n⚠️  이미 Deal 테이블에 있습니다.")

# 최종 통계
count_result = supabase.table("deals").select("id", count="exact").execute()
print(f"\n{'='*80}")
print(f"Deal 테이블 총 레코드: {count_result.count}개")
print(f"{'='*80}")

print("\n🎉 센서블박스 외 발굴 기업:")
print("  ✅ 디앤티테크솔루션 (64억원, 프리A)")
print("  ❌ 엘리시전 (아직 검색 중)")

print("\n💡 센서블박스(124개) + 발굴(1개) = 총 125개 기업!")
