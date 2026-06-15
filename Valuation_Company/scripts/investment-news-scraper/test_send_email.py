#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""일일 뉴스레터 테스트 발송 — 지정한 한 명에게만 발송(전체 구독자 X)."""
import sys, codecs, argparse
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
import send_daily_email as s

ap = argparse.ArgumentParser()
ap.add_argument('--to', default='wksun999@naver.com')
args = ap.parse_args()

if not s.GMAIL_ADDRESS or not s.GMAIL_APP_PASSWORD:
    print("[ERROR] GMAIL_ADDRESS/APP_PASSWORD .env 미설정"); sys.exit(1)

deals = s.get_yesterday_deals()
print(f"어제 deals: {len(deals)}건")
html = s.generate_email_html(deals)
subject = f"[테스트][투자 뉴스] 어제 {len(deals)}건"
ok = s.send_email_via_gmail(args.to, subject, html)
print(f"테스트 발송 → {args.to}: {'성공' if ok else '실패'}")
