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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
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

def scrape_thebell_direct():
    url = "https://www.thebell.co.kr/free/content/Article.asp?svccode=00"
    print("Fetching The Bell (Direct)...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8' # UTF-8 강제
        soup = BeautifulSoup(resp.text, 'lxml')
        
        items = soup.select('.listBox li')
        articles = []
        
        for item in items:
            try:
                title_elem = item.select_one('dt a')
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href')
                if not link.startswith('http'):
                    link = 'https://www.thebell.co.kr/free/content/' + link
                    
                date_elem = item.select_one('.date')
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                
                # 키워드 필터 (간단하게)
                if any(k in title for k in ['투자', '펀딩', 'VC', '스타트업', '인수', 'M&A', '유치']):
                    articles.append({
                        'site_number': 16,
                        'site_name': '더벨',
                        'site_url': 'https://www.thebell.co.kr',
                        'article_title': title,
                        'article_url': link,
                        'published_date': parse_date(date_str),
                        'content_snippet': None
                    })
            except: continue
            
        return articles
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    # 더벨 수집
    data = scrape_thebell_direct()
    
    # 넥스트유니콘, 벤처경영신문, 다음뉴스 -> 실패 처리 (로그 출력)
    print("\n=== Failure Report ===")
    print("- 넥스트유니콘: 동적 로딩/로그인 필요 (Selenium 필수)")
    print("- 벤처경영신문: SSL/접근 차단 (403/404)")
    print("- 다음뉴스: 섹션 구조 변경으로 인한 파싱 실패")

    # 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(data)} items from The Bell to {OUTPUT_FILE}")
