import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import date

# 설정
OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\missing_sites_data.json'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
}

print("Fetching The Bell (Final Fix)...")

try:
    resp = requests.get("https://www.thebell.co.kr/free/content/Article.asp?svccode=00", headers=HEADERS, timeout=10)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    items = soup.select('.listBox li')
    
    articles = []
    for item in items:
        try:
            # dt a 시도, 없으면 그냥 a, 그것도 없으면 class="tit"
            t = item.select_one('dt a') or item.select_one('.tit a') or item.select_one('a')
            
            if not t: continue
            
            title = t.get_text(strip=True)
            link = t.get('href')
            
            # 제목이 너무 짧으면 스킵 (네비게이션 링크일 수 있음)
            if len(title) < 5: continue
            
            if link and not link.startswith('http'):
                link = 'https://www.thebell.co.kr/free/content/' + link
            
            d = item.select_one('.date')
            d_str = d.get_text(strip=True) if d else ""
            
            pub_date = date.today().isoformat()
            try:
                nums = re.findall(r'\d+', d_str)
                if len(nums) >= 3:
                    y, m, d = map(int, nums[:3])
                    if y < 100: y += 2000
                    pub_date = date(y, m, d).isoformat()
            except: pass

            articles.append({
                'site_number': 16,
                'site_name': '더벨',
                'site_url': 'https://www.thebell.co.kr',
                'article_title': title,
                'article_url': link,
                'published_date': pub_date,
                'content_snippet': "Final Fix Collected"
            })
        except: continue

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(articles)} items.")

except Exception as e:
    print(f"Global error: {e}")
