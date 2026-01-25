import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import date

OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\missing_sites_data.json'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Upgrade-Insecure-Requests': '1',
}

def parse_date(date_str):
    try:
        nums = re.findall(r'\d+', date_str)
        if len(nums) >= 3:
            y, m, d = map(int, nums[:3])
            if y < 100: y += 2000
            return date(y, m, d).isoformat()
    except:
        pass
    return date.today().isoformat()

def scrape_thebell_force():
    url = "https://www.thebell.co.kr/free/content/Article.asp?svccode=00"
    print("Fetching The Bell (Force Mode)...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'lxml')
        
        items = soup.select('.listBox li')
        articles = []
        
        # 키워드 필터 없이 상위 5개 무조건 수집
        for item in items[:5]:
            try:
                title_elem = item.select_one('dt a')
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href')
                if not link.startswith('http'):
                    link = 'https://www.thebell.co.kr/free/content/' + link
                    
                date_elem = item.select_one('.date')
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                
                articles.append({
                    'site_number': 16,
                    'site_name': '더벨',
                    'site_url': 'https://www.thebell.co.kr',
                    'article_title': title,
                    'article_url': link,
                    'published_date': parse_date(date_str),
                    'content_snippet': "강제 수집 (키워드 미발견)"
                })
            except: continue
            
        return articles
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    data = scrape_thebell_force()
    
    print(f"\nCollected {len(data)} items from The Bell.")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved to {OUTPUT_FILE}")
