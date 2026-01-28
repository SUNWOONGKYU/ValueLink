#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal 테이블에서 기업명 수정 및 누락 기업 추가
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
print("Deal 테이블 기업명 수정 및 누락 기업 추가")
print("=" * 80)

# 1. 잘못된 "기업명" 레코드 삭제
print("\n1️⃣ 잘못된 레코드 삭제")
try:
    result = supabase.table("deals").delete().eq("company_name", "기업명").execute()
    print("  ✅ '기업명' 레코드 삭제 완료")
except Exception as e:
    print(f"  ❌ 오류: {e}")

# 2. 이름이 다른 기업들을 올바른 이름으로 추가
print("\n2️⃣ 올바른 이름으로 기업 추가")

# "부스터즈" → "부스터스"
try:
    result = supabase.table("deals").select("*").eq("company_name", "부스터즈").execute()
    if result.data:
        deal = result.data[0]
        deal['company_name'] = '부스터스'
        del deal['id']  # id 제거
        del deal['created_at']
        del deal['updated_at']
        deal['created_at'] = datetime.now().isoformat()

        # 기존 부스터스가 있는지 확인
        existing = supabase.table("deals").select("id").eq("company_name", "부스터스").execute()
        if not existing.data:
            supabase.table("deals").insert(deal).execute()
            print("  ✅ 부스터즈 → 부스터스 추가")
        else:
            print("  ⚠️  부스터스 이미 있음")
except Exception as e:
    print(f"  ❌ 부스터스 오류: {e}")

# "소서릭스" → "소서릭스코리아"
try:
    result = supabase.table("deals").select("*").eq("company_name", "소서릭스").execute()
    if result.data:
        deal = result.data[0]
        deal['company_name'] = '소서릭스코리아'
        del deal['id']
        del deal['created_at']
        del deal['updated_at']
        deal['created_at'] = datetime.now().isoformat()

        existing = supabase.table("deals").select("id").eq("company_name", "소서릭스코리아").execute()
        if not existing.data:
            supabase.table("deals").insert(deal).execute()
            print("  ✅ 소서릭스 → 소서릭스코리아 추가")
        else:
            print("  ⚠️  소서릭스코리아 이미 있음")
except Exception as e:
    print(f"  ❌ 소서릭스코리아 오류: {e}")

# 3. investment_news_articles에서 나머지 3개 기업 찾아서 추가
print("\n3️⃣ 기사는 있지만 Deal에 없는 기업 추가")

# 뉴타입인더스트리즈
try:
    articles = supabase.table("investment_news_articles")\
        .select("*")\
        .ilike("article_title", "%뉴타입인더스트리즈%")\
        .execute()

    if articles.data:
        article = articles.data[0]
        deal = {
            'company_name': '뉴타입인더스트리즈',
            'industry': '방위산업 AI 스타트업',
            'stage': None,
            'investors': '블루포인트파트너스',
            'amount': None,
            'news_title': article['article_title'],
            'news_url': article['article_url'],
            'site_name': article['site_name'],
            'news_date': article['published_date'],
            'created_at': datetime.now().isoformat()
        }

        existing = supabase.table("deals").select("id").eq("company_name", "뉴타입인더스트리즈").execute()
        if not existing.data:
            supabase.table("deals").insert(deal).execute()
            print("  ✅ 뉴타입인더스트리즈 추가")
        else:
            print("  ⚠️  뉴타입인더스트리즈 이미 있음")
except Exception as e:
    print(f"  ❌ 뉴타입인더스트리즈 오류: {e}")

# 펩티르나테라퓨틱스
try:
    articles = supabase.table("investment_news_articles")\
        .select("*")\
        .ilike("article_title", "%펩티르나%")\
        .execute()

    if articles.data:
        article = articles.data[0]
        deal = {
            'company_name': '펩티르나테라퓨틱스',
            'industry': 'siRNA 약물전달체 개발 기업',
            'stage': '시드',
            'investors': '와우파트너스',
            'amount': None,
            'news_title': article['article_title'],
            'news_url': article['article_url'],
            'site_name': article['site_name'],
            'news_date': article['published_date'],
            'created_at': datetime.now().isoformat()
        }

        existing = supabase.table("deals").select("id").eq("company_name", "펩티르나테라퓨틱스").execute()
        if not existing.data:
            supabase.table("deals").insert(deal).execute()
            print("  ✅ 펩티르나테라퓨틱스 추가")
        else:
            print("  ⚠️  펩티르나테라퓨틱스 이미 있음")
except Exception as e:
    print(f"  ❌ 펩티르나테라퓨틱스 오류: {e}")

# 덱사스튜디오
try:
    articles = supabase.table("investment_news_articles")\
        .select("*")\
        .ilike("article_title", "%덱사스튜디오%")\
        .execute()

    if articles.data:
        article = articles.data[0]
        deal = {
            'company_name': '덱사스튜디오',
            'industry': 'MMORPG 전문 개발사',
            'stage': '시드',
            'investors': 'NC소프트',
            'amount': None,
            'news_title': article['article_title'],
            'news_url': article['article_url'],
            'site_name': article['site_name'],
            'news_date': article['published_date'],
            'created_at': datetime.now().isoformat()
        }

        existing = supabase.table("deals").select("id").eq("company_name", "덱사스튜디오").execute()
        if not existing.data:
            supabase.table("deals").insert(deal).execute()
            print("  ✅ 덱사스튜디오 추가")
        else:
            print("  ⚠️  덱사스튜디오 이미 있음")
except Exception as e:
    print(f"  ❌ 덱사스튜디오 오류: {e}")

# 최종 통계
print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)

count_result = supabase.table("deals").select("id", count="exact").execute()
print(f"\n✅ Deal 테이블 총 레코드: {count_result.count}개")

print("\n❌ 최종 미발견 기업: 2개")
print("  1. 디앤티테크솔루션")
print("  2. 엘리시전")

print(f"\n📊 센서블박스 커버리지: {count_result.count}/124 = {count_result.count/124*100:.1f}%")
