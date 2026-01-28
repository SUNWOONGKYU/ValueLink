#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 뉴스 수집 테스트 (3개 회사만)
몰트봇이 발견한 회사들로 검증
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

model = genai.GenerativeModel('gemini-2.5-flash')

print("=" * 80)
print("Gemini 테스트: 몰트봇이 발견한 3개 회사")
print("=" * 80)

# 테스트 대상: 몰트봇이 발견한 회사들
TEST_COMPANIES = [
    {
        'name': '부스터즈',
        'expected': {
            'amount': '200억',
            'investor': 'FSN',
            'site': '이투데이'
        }
    },
    {
        'name': '소서릭스',
        'expected': {
            'investor': '네이버 D2SF',
            'site': '머니S'
        }
    },
    {
        'name': '엘리시젠',
        'expected': {
            'amount': '50억',
            'investor': '데일리파트너스',
            'site': '금융경제플러스'
        }
    }
]

def search_with_gemini(company_name):
    """Gemini로 투자 뉴스 검색"""

    prompt = f"""
다음 한국 스타트업의 최근 투자 유치 뉴스를 검색해주세요:

**회사명**: {company_name}

**검색 조건**:
- 투자 유치 관련 기사만 (시리즈A, 시드, 브릿지, 프리A 등)
- 한국 언론사 기사
- 최근 3개월 이내 발행된 기사
- 실제 투자 금액이나 투자자가 명시된 기사 우선

**필요한 정보**:
각 기사마다 다음 정보를 JSON 형식으로 제공:
1. article_title: 기사 제목
2. article_url: 기사 URL
3. site_name: 언론사명
4. published_date: 발행일 (YYYY-MM-DD)
5. summary: 투자 관련 핵심 내용 (투자자, 금액, 단계)

**출력 형식**:
```json
[
  {{
    "article_title": "제목",
    "article_url": "https://...",
    "site_name": "언론사",
    "published_date": "2026-01-15",
    "summary": "투자자명, 투자금액, 투자단계 등"
  }}
]
```

기사를 찾지 못했다면 빈 배열 []을 반환해주세요.
"""

    try:
        print(f"\n🔍 {company_name} 검색 중...")

        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )

        text = response.text.strip()

        print(f"\n  📝 Gemini 응답 (처음 500자):")
        print(f"  {text[:500]}")

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
        return articles

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 파싱 오류: {e}")
        print(f"  📝 파싱 시도한 텍스트: {text[:300]}")
        return []
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return []

def main():
    """테스트 실행"""

    results = []

    for idx, test_case in enumerate(TEST_COMPANIES, 1):
        company_name = test_case['name']
        expected = test_case['expected']

        print(f"\n[{idx}/{len(TEST_COMPANIES)}] {company_name}")
        print(f"  예상: {expected}")

        articles = search_with_gemini(company_name)

        if articles:
            print(f"  ✅ {len(articles)}개 기사 발견!")
            for i, article in enumerate(articles, 1):
                print(f"\n  [{i}] {article.get('article_title', 'N/A')}")
                print(f"      URL: {article.get('article_url', 'N/A')}")
                print(f"      언론사: {article.get('site_name', 'N/A')}")
                print(f"      발행일: {article.get('published_date', 'N/A')}")
                print(f"      요약: {article.get('summary', 'N/A')[:100]}...")

            results.append({
                'company': company_name,
                'expected': expected,
                'found': len(articles),
                'articles': articles,
                'success': True
            })
        else:
            print(f"  ❌ 기사 없음")
            results.append({
                'company': company_name,
                'expected': expected,
                'found': 0,
                'success': False
            })

    # 최종 결과
    print("\n" + "=" * 80)
    print("테스트 결과")
    print("=" * 80)

    success_count = sum(1 for r in results if r['success'])
    print(f"\n✅ 성공: {success_count}/{len(TEST_COMPANIES)}")
    print(f"❌ 실패: {len(TEST_COMPANIES) - success_count}/{len(TEST_COMPANIES)}")

    total_articles = sum(r['found'] for r in results)
    print(f"\n📊 총 발견 기사: {total_articles}개")

    # 결과 저장
    result_file = f"data/gemini_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_companies': TEST_COMPANIES,
            'results': results,
            'success_rate': f"{success_count}/{len(TEST_COMPANIES)}",
            'total_articles': total_articles,
            'timestamp': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 결과 저장: {result_file}")

    if success_count == len(TEST_COMPANIES):
        print("\n🎉 테스트 통과! 전체 수집 스크립트 실행 가능!")
    else:
        print("\n⚠️  일부 실패 - 프롬프트 조정 필요")

if __name__ == "__main__":
    main()
