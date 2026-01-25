import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def debug_site(name, url, verify=True):
    print(f"\n--- Debugging {name}: {url} ---")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=verify)
        print(f"Status Code: {resp.status_code}")
        print(f"Encoding (detected): {resp.encoding}")
        print(f"Apparent Encoding: {resp.apparent_encoding}")
        
        # 인코딩 강제 설정 (EUC-KR 등 시도)
        if 'thebell' in url or 'vmnews' in url:
             resp.encoding = 'EUC-KR' # or 'CP949'
             print(f"Forced Encoding to EUC-KR")

        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 제목 태그 찾기 시도 (더 넓은 범위로)
        titles = []
        if 'thebell' in url:
            # 더벨: dt a, .tit a
            titles = soup.select('dt a') + soup.select('.tit a')
        elif 'vmnews' in url:
            # 벤처경영신문: .list-titles a
            titles = soup.select('.list-titles a')
        elif 'daum' in url:
            # 다음: .tit_thumb a
            titles = soup.select('.tit_thumb a')
        
        print(f"Found {len(titles)} potential titles.")
        for t in titles[:3]:
            print(f" - {t.get_text(strip=True)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_site("The Bell", "https://www.thebell.co.kr/free/content/Article.asp?svccode=00")
    debug_site("VM News", "https://www.vmnews.co.kr/news/articleList.html?sc_section_code=S1N2&view_type=sm", verify=False)
    debug_site("Daum Venture", "https://news.daum.net/section/2/venture")
