import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import date

# 벤처스퀘어 'Startup News' 카테고리
URL_PATTERN = "https://www.venturesquare.net/category/news-contents/news-trends/news/page/{}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_venturesquare_real():
    articles = []
    print("벤처스퀘어 재시도 (올바른 URL)...")

    for page in range(1, 11): # 10페이지까지
        url = URL_PATTERN.format(page)
        print(f"Checking Page {page}: {url}")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, 'lxml')
            
            # 벤처스퀘어는 h4.bold a.black 구조 (이전 디버깅 경험 참고)
            # 혹은 일반적인 h2 a
            items = soup.select('h4.bold a') or soup.select('.post-title a') or soup.select('h2 a')

            page_cnt = 0
            for item in items:
                title = item.get_text(strip=True)
                link = item.get('href')
                
                if len(title) < 5: continue

                # 키워드 필터 (투자, 유치, 펀딩)
                if any(k in title for k in ['투자', '유치', '펀딩']):
                    # 날짜 확인 (목록에 날짜가 있는지 체크)
                    # 보통 li 태그 안에 time 태그가 있음
                    li = item.find_parent('li')
                    date_str = "Unknown"
                    if li:
                        time_tag = li.select_one('time')
                        if time_tag:
                            date_str = time_tag.get('datetime') or time_tag.get_text(strip=True)
                    
                    # 2026년인지 확인 (날짜가 없으면 일단 수집, 있으면 필터)
                    if '2026' in date_str or date_str == "Unknown":
                        print(f"  [Found] {title} ({date_str})")
                        articles.append({
                            'site_name': '벤처스퀘어',
                            'title': title,
                            'url': link,
                            'date': date_str
                        })
                        page_cnt += 1
            
            if page_cnt == 0:
                print("  -> 이 페이지에 매칭되는 기사 없음")
                
        except Exception as e:
            print(f"Error: {e}")
            
    return articles

if __name__ == "__main__":
    data = get_venturesquare_real()
    
    save_path = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\venturesquare_final.json'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSaved {len(data)} items to {save_path}")
