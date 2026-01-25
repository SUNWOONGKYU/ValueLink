import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
}

url = "https://www.thebell.co.kr/free/content/Article.asp?svccode=00"

print("Fetching The Bell...")
try:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = 'utf-8'
    print(f"Status: {resp.status_code}")
    print(f"Length: {len(resp.text)}")
    
    soup = BeautifulSoup(resp.text, 'lxml')
    items = soup.select('.listBox li')
    print(f"Items found: {len(items)}")
    
    if len(items) > 0:
        print("Success! First item:")
        print(items[0].get_text()[:100])
    else:
        print("No items found. Dumping HTML head...")
        print(resp.text[:500])

except Exception as e:
    print(f"Error: {e}")
