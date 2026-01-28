#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import sys
import os
from dotenv import load_dotenv
from supabase import create_client

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# CSV 로드
csv_data = {}
with open('sensible_companies_2026_01_GEMINI.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company = row.get('기업명', '').strip()
        if company and company not in ['기업명', '```']:
            amount_str = row.get('신규', '').strip()
            csv_data[company] = amount_str

# Deal 테이블 로드
deals = supabase.table('deals').select('company_name, amount').execute()

# 투자금액 없는 Deal 회사
empty_amount = [d for d in deals.data if not d.get('amount')]

print(f'CSV 회사: {len(csv_data)}개')
print(f'투자금액 없는 Deal: {len(empty_amount)}개')

# 매칭 확인
matched = 0
not_matched = []

for deal in empty_amount[:10]:
    company = deal['company_name']
    if company in csv_data:
        print(f'✅ {company}: CSV에 {csv_data[company]}')
        matched += 1
    else:
        print(f'❌ {company}: CSV에 없음')
        not_matched.append(company)

print(f'\n매칭: {matched}/10')
