#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.5 Flash - 새 API로 웹 검색
google-genai 패키지 사용
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Gemini 클라이언트 생성
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("=" * 80)
print("Gemini 2.5 Flash - 웹 검색 테스트 (새 API)")
print("=" * 80)

def search_with_grounding(company_name):
    """Google Search Grounding을 활용한 검색"""

    prompt = f"""
인터넷을 검색해서 다음 한국 스타트업의 최신 투자 유치 뉴스를 찾아주세요:

**회사명**: {company_name}

**검색 조건**:
- 투자 유치 관련 기사 (시리즈A, 시드, 브릿지, 프리A 등)
- 2026년 1월에 발행된 기사
- 한국 언론사 기사
- 투자 금액, 투자자, 투자단계가 명시된 기사

**중요**: 반드시 최신 인터넷 검색 결과를 사용해주세요. 학습 데이터가 아닌 실제 웹에서 검색한 결과를 제공해주세요.

**출력 형식** (JSON 배열):
```json
[
  {{
    "article_title": "기사 제목 전체",
    "article_url": "https://...",
    "site_name": "언론사명",
    "published_date": "YYYY-MM-DD",
    "summary": "투자자명, 투자금액, 투자단계 등 핵심 정보"
  }}
]
```

기사를 찾지 못했으면 빈 배열 `[]`을 반환하세요.
"""

    try:
        print(f"\n🔍 {company_name} 검색 중 (웹 검색 활성화)...")

        # Grounding 설정
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.8,
                max_output_tokens=4096,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        text = response.text.strip()

        print(f"\n  📝 Gemini 응답:")
        print(f"  {text}")
        print()

        # JSON 추출
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()

        articles = json.loads(text)

        if articles:
            print(f"  ✅ {len(articles)}개 기사 발견!")
        else:
            print(f"  ⚠️  기사 없음")

        return articles

    except Exception as e:
        print(f"  ❌ 오류: {e}")
        if 'text' in locals():
            print(f"  응답: {text[:500]}")
        return []

def main():
    """테스트 실행"""

    # 몰트봇이 발견한 회사로 테스트
    test_companies = ["부스터즈", "엘리시젠", "소서릭스"]

    results = []

    for idx, company_name in enumerate(test_companies, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(test_companies)}] {company_name}")
        print('='*80)

        articles = search_with_grounding(company_name)

        if articles:
            for i, article in enumerate(articles, 1):
                print(f"\n  [{i}]")
                print(f"  제목: {article.get('article_title', 'N/A')}")
                print(f"  URL: {article.get('article_url', 'N/A')}")
                print(f"  언론사: {article.get('site_name', 'N/A')}")
                print(f"  발행일: {article.get('published_date', 'N/A')}")
                print(f"  요약: {article.get('summary', 'N/A')[:100]}...")

            results.append({
                'company': company_name,
                'found': len(articles),
                'articles': articles
            })
        else:
            results.append({
                'company': company_name,
                'found': 0
            })

    # 최종 결과
    print(f"\n{'='*80}")
    print("최종 결과")
    print('='*80)

    total_articles = sum(r['found'] for r in results)
    success_count = sum(1 for r in results if r['found'] > 0)

    print(f"\n✅ 성공: {success_count}/{len(test_companies)}")
    print(f"📊 총 발견 기사: {total_articles}개")

    # 결과 저장
    result_file = f"data/gemini_grounding_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_companies': test_companies,
            'results': results,
            'total_articles': total_articles,
            'success_rate': f"{success_count}/{len(test_companies)}",
            'timestamp': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 결과 저장: {result_file}")

    if success_count == len(test_companies):
        print("\n🎉 테스트 통과! Gemini가 웹 검색으로 뉴스를 잘 찾습니다!")
    elif success_count > 0:
        print(f"\n⚠️  일부 성공 ({success_count}/{len(test_companies)})")
    else:
        print("\n❌ 모두 실패")

if __name__ == "__main__":
    main()
