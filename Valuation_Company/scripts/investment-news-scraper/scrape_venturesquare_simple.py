import requests
from bs4 import BeautifulSoup
import json
import os
import re

# 벤처스퀘어 투자 뉴스 URL
URL_PATTERN = "https://www.venturesquare.net/category/news-contents/investment/page/{}"

# 헤더 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_venturesquare_news():
    articles = []
    print("벤처스퀘어 수집 시작...")

    for page in range(1, 6):  # 1~5페이지
        url = URL_PATTERN.format(page)
        print(f"페이지 {page} 읽는 중... {url}")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, 'lxml')
            
            # 기사 목록 (class="post-item" 등 확인 필요하지만, 보통 h2, h3 a 태그 사용)
            # 벤처스퀘어 구조: <h3 class="post-title"><a href="...">제목</a></h3>
            items = soup.select('h3.post-title a') # 벤처스퀘어 전용 선택자

            if not items:
                # 선택자가 틀렸을 수 있으니 범용으로 재시도
                items = soup.select('.post-item a') or soup.select('h2 a')

            for item in items:
                title = item.get_text(strip=True)
                link = item.get('href')
                
                # 2026년 기사인지 확인 (날짜는 상세 페이지 안 들어가면 목록에 있을 수도/없을 수도)
                # 벤처스퀘어 목록에는 날짜가 <span class="post-meta-item post-date">2026.01.26</span> 이렇게 있음
                # 부모 요소로 올라가서 날짜 찾기
                parent = item.find_parent('article') or item.find_parent('div')
                date_str = ""
                if parent:
                    date_elem = parent.select_one('.post-date')
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                
                # 날짜가 없거나 2026년이 아니면 스킵 (정밀 필터링은 나중에 하더라도 일단 2026 포함되면 수집)
                if '2026' not in date_str:
                    continue

                # 키워드 필터 (투자, 유치)
                if '투자' in title or '유치' in title:
                    print(f"  [발견] {title} ({date_str})")
                    articles.append({
                        'site_name': '벤처스퀘어',
                        'title': title,
                        'url': link,
                        'date': date_str
                    })
                    
        except Exception as e:
            print(f"에러 발생: {e}")
            
    return articles

if __name__ == "__main__":
    data = get_venturesquare_news()
    
    # 저장
    save_path = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\venturesquare_2026.json'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\n총 {len(data)}건 수집 완료. 파일 저장: {save_path}")
