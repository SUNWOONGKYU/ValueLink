#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매일 자동 실행되는 투자 뉴스 스크래퍼 (Gemini API 사용)
Top 5 사이트에서만 뉴스 수집 (WOWTALE, 벤처스퀘어, 더벨, 플래텀, 스타트업투데이)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

# 환경 변수 로드
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Top 5 사이트 정의 (분석 결과 기반)
TOP_5_SITES = [
    {'number': 1, 'name': 'WOWTALE', 'url': 'https://wowtale.net'},
    {'number': 9, 'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net'},
    {'number': 16, 'name': '더벨', 'url': 'https://www.thebell.co.kr'},
    {'number': 10, 'name': '플래텀', 'url': 'https://platum.kr'},
    {'number': 11, 'name': '스타트업투데이', 'url': 'https://startuptoday.kr'},
]

def collect_news_with_gemini():
    """Gemini API로 뉴스 수집"""

    print(f"🤖 Gemini API를 사용하여 뉴스 수집 시작...")
    print(f"📅 수집 기간: 어제 ({(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')})")

    # Gemini API 설정
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    # 어제 날짜
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 프롬프트 생성
    sites_list = "\n".join([f"{i+1}. {site['name']} (site_number: {site['number']}) - {site['url']}"
                            for i, site in enumerate(TOP_5_SITES)])

    prompt = f"""
다음 10개 사이트에서 {yesterday} 날짜의 투자 유치 관련 뉴스를 수집해주세요.

대상 사이트:
{sites_list}

수집 조건:
- 날짜: {yesterday}
- 키워드: 투자, 투자유치, 펀딩, 시리즈, 벤처캐피탈, VC, M&A
- 각 사이트당 최소 3개 이상 수집

JSON 형식으로 반환:
[
  {{
    "site_number": 9,
    "site_name": "벤처스퀘어",
    "site_url": "https://www.venturesquare.net",
    "article_title": "기사 제목",
    "article_url": "기사 URL",
    "published_date": "{yesterday}",
    "content_snippet": null
  }}
]

중요: 반드시 유효한 JSON 배열만 반환하고, 추가 설명은 하지 마세요.
"""

    try:
        # Gemini API 호출
        response = model.generate_content(prompt)
        json_text = response.text

        # JSON 파싱
        # 코드 블록 제거 (```json ... ```)
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()

        articles = json.loads(json_text)

        print(f"✅ Gemini API 응답 성공: {len(articles)}건 수집")
        return articles

    except Exception as e:
        print(f"❌ Gemini API 오류: {str(e)}")
        return []

def save_to_supabase(articles):
    """Supabase에 저장"""

    print(f"\n💾 Supabase에 저장 시작...")

    success = 0
    duplicate = 0
    error = 0

    for idx, article in enumerate(articles, 1):
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/investment_news_articles",
                headers={
                    'apikey': SUPABASE_KEY,
                    'Authorization': f'Bearer {SUPABASE_KEY}',
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                json=article
            )

            if response.status_code == 201:
                success += 1
                print(f"  ✅ [{idx}/{len(articles)}] {article['site_name']}")
            elif response.status_code == 409:
                duplicate += 1
                print(f"  ⚠️  [{idx}/{len(articles)}] 중복: {article['site_name']}")
            else:
                error += 1
                print(f"  ❌ [{idx}/{len(articles)}] 실패 ({response.status_code})")

        except Exception as e:
            error += 1
            print(f"  ❌ [{idx}/{len(articles)}] 오류: {str(e)}")

    print(f"\n📊 저장 결과:")
    print(f"  ✅ 성공: {success}건")
    print(f"  ⚠️  중복: {duplicate}건")
    print(f"  ❌ 실패: {error}건")
    print(f"  📝 총: {len(articles)}건")

    return success, duplicate, error

def main():
    """메인 실행 함수"""

    print("=" * 60)
    print("📰 일일 투자 뉴스 자동 수집 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Gemini API로 뉴스 수집
    articles = collect_news_with_gemini()

    if not articles:
        print("\n⚠️  수집된 기사가 없습니다. 종료합니다.")
        return

    # 2. Supabase에 저장
    success, duplicate, error = save_to_supabase(articles)

    # 3. 결과 로그 저장
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'total_collected': len(articles),
        'success': success,
        'duplicate': duplicate,
        'error': error
    }

    with open('daily_scrape_log.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    print("\n✅ 일일 뉴스 수집 완료!")
    print("=" * 60)

if __name__ == '__main__':
    main()
