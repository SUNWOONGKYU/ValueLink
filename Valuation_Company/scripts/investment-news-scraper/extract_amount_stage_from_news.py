#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 기사에서 투자금액, 투자단계 추출
Gemini 2.5 Flash 사용
"""

import os
import sys
import json
import time
import re
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

def extract_with_gemini(company_name, url):
    """Gemini로 투자금액, 투자단계 추출"""

    prompt = f"""
다음 투자 뉴스 기사에서 정보를 추출해주세요:

**회사명**: {company_name}
**URL**: {url}

**추출할 정보:**
1. 투자금액 (예: 100억원, $10M)
2. 투자단계 (시드, 프리A, 시리즈A, 시리즈B, 시리즈C 등)

**출력 (JSON):**
```json
{{
    "amount": 100.0,
    "stage": "시리즈A"
}}
```

- amount는 억원 단위 숫자만 (100억원 → 100.0)
- stage는 한글로 (Series A → 시리즈A)
- 없으면 null
"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=256,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        if not response or not hasattr(response, 'text'):
            return None, None

        text = response.text.strip()

        # JSON 추출
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.rfind("```")
            if json_end > json_start:
                text = text[json_start:json_end].strip()

        result = json.loads(text)
        return result.get('amount'), result.get('stage')

    except Exception as e:
        # JSON 파싱 실패 시 텍스트에서 직접 추출
        if 'text' in locals():
            # 금액 추출
            amount_match = re.search(r'(\d+(?:\.\d+)?)\s*억', text)
            amount = float(amount_match.group(1)) if amount_match else None

            # 단계 추출
            stage = None
            stages = ['시리즈C', '시리즈B', '시리즈A', '프리A', '시드']
            for s in stages:
                if s in text:
                    stage = s
                    break

            return amount, stage

        return None, None

print("=" * 80)
print("Gemini로 투자금액, 투자단계 추출 (상위 20개만)")
print("=" * 80)

# 투자금액 없는 Deal 조회 (상위 20개만)
deals = supabase.table("deals")\
    .select("*")\
    .is_("amount", "null")\
    .limit(20)\
    .execute()

print(f"\n처리할 Deal: {len(deals.data)}개\n")

update_count = 0

for idx, deal in enumerate(deals.data, 1):
    company = deal['company_name']
    url = deal.get('news_url', '')

    print(f"[{idx}/{len(deals.data)}] {company}")

    amount, stage = extract_with_gemini(company, url)

    updates = {}
    if amount:
        updates['amount'] = amount
        print(f"  ✅ 금액: {amount}억원")

    if stage and (not deal.get('stage') or deal.get('stage') in ['-', 'None']):
        updates['stage'] = stage
        print(f"  ✅ 단계: {stage}")

    if updates:
        supabase.table("deals")\
            .update(updates)\
            .eq("id", deal['id'])\
            .execute()
        update_count += 1
    else:
        print(f"  ⚠️  추출 실패")

    time.sleep(1)

print(f"\n✅ {update_count}/{len(deals.data)}개 업데이트 완료")
