#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.5 Flash로 뉴스 게재 시간 추출
URL에서 날짜 못 찾은 76개 처리
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client, Client

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

# Gemini 클라이언트
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 80)
print("Gemini 2.5 Flash - 뉴스 게재 시간 추출")
print("=" * 80)

def extract_date_with_gemini(url, company_name):
    """Gemini로 뉴스 페이지 접속해서 게재일 추출"""

    prompt = f"""
다음 URL의 뉴스 기사 페이지를 확인하고, 정확한 게재일(발행일)을 찾아주세요:

**URL**: {url}
**기업명**: {company_name}

**찾아야 할 정보:**
- 기사 게재일/발행일 (published date)
- 기사 작성일 (written date)

**중요:**
- 실제 뉴스가 발행된 날짜를 찾아야 합니다
- DB 저장 시간이나 수정 시간이 아닙니다
- 메타데이터, 본문 상단, URL 등에서 날짜를 확인하세요

**출력 형식 (JSON):**
```json
{{
    "published_date": "YYYY-MM-DD",
    "source": "어디서 찾았는지 (예: 본문 상단, 메타데이터, URL)"
}}
```

날짜를 찾지 못했으면:
```json
{{
    "published_date": null,
    "source": "날짜 정보 없음"
}}
```
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        if not response or not hasattr(response, 'text'):
            return {"published_date": None, "source": "응답 없음"}

        text = response.text.strip()

        # JSON 추출 (더 robust하게)
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.rfind("```")  # 마지막 ``` 찾기
            if json_end > json_start:
                text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.rfind("```")
            if json_end > json_start:
                text = text[json_start:json_end].strip()

        # JSON 파싱 시도
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            # JSON이 아니면 텍스트에서 날짜 추출 시도
            import re
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
            if date_match:
                return {
                    "published_date": date_match.group(1),
                    "source": "텍스트에서 추출"
                }
            else:
                return {"published_date": None, "source": f"JSON 파싱 실패: {text[:100]}"}

    except Exception as e:
        print(f"    ❌ Gemini 오류: {e}")
        return {"published_date": None, "source": f"오류: {str(e)[:50]}"}

# Deal 테이블에서 뉴스 URL 있는 전체 데이터 가져오기
print("\n📋 전체 Deal 조회 중...")
deals = supabase.table("deals")\
    .select("*")\
    .not_.is_("news_url", "null")\
    .order("number")\
    .execute()

print(f"총 {len(deals.data)}개 Deal (뉴스 URL 있음)")

# 우선순위: 2026-01-28 먼저 처리
deals_priority = [d for d in deals.data if d.get('news_date') == '2026-01-28']
deals_other = [d for d in deals.data if d.get('news_date') != '2026-01-28']

print(f"  - 2026-01-28 (우선): {len(deals_priority)}개")
print(f"  - 기타: {len(deals_other)}개")

# 전체 처리
deals_to_process = deals.data
print(f"\n처리할 Deal: {len(deals_to_process)}개 (전체)")

update_count = 0
failed = []

for idx, deal in enumerate(deals.data, 1):
    company = deal['company_name']
    url = deal.get('news_url')

    if not url:
        print(f"\n[{idx}/{len(deals.data)}] {company}: URL 없음")
        continue

    print(f"\n[{idx}/{len(deals.data)}] {company}")
    print(f"  URL: {url[:70]}...")

    # Gemini로 날짜 추출
    result = extract_date_with_gemini(url, company)

    if result.get('published_date'):
        extracted_date = result['published_date']
        source = result.get('source', 'N/A')

        print(f"  ✅ 발견: {extracted_date} (출처: {source})")

        # Deal 테이블 업데이트
        supabase.table("deals")\
            .update({'news_date': extracted_date})\
            .eq("id", deal['id'])\
            .execute()

        # 뉴스 테이블도 업데이트
        supabase.table("investment_news_articles")\
            .update({'published_date': extracted_date})\
            .eq("article_url", url)\
            .execute()

        update_count += 1
    else:
        source = result.get('source', 'N/A')
        print(f"  ⚠️  날짜 없음: {source}")
        failed.append({
            'company': company,
            'url': url,
            'reason': source
        })

    # API 제한 방지 (60 RPM)
    time.sleep(1)

# 최종 결과
print("\n" + "=" * 80)
print("최종 결과")
print("=" * 80)

print(f"\n✅ 성공: {update_count}개")
print(f"❌ 실패: {len(failed)}개")

if failed:
    print(f"\n⚠️  날짜 못 찾은 기업 ({len(failed)}개):")
    for item in failed[:10]:
        print(f"  - {item['company']}: {item['reason']}")
    if len(failed) > 10:
        print(f"  ... 외 {len(failed)-10}개")

# 뉴스 게재일 분포
deals_updated = supabase.table("deals").select("news_date").execute()
from collections import Counter
date_counter = Counter([d['news_date'] for d in deals_updated.data if d.get('news_date')])

print(f"\n📊 뉴스 게재일 분포 (상위 10개):")
for date, count in sorted(date_counter.items(), reverse=True)[:10]:
    print(f"  {date}: {count}개")

# 결과 저장
result_file = f"data/gemini_date_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(deals.data),
        'success': update_count,
        'failed': failed,
        'timestamp': datetime.now().isoformat()
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 결과 저장: {result_file}")
