import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def debug_venturesquare():
    url = 'https://www.venturesquare.net/category/news-contents/news-trends/news/'
    print(f"--- Debugging VentureSquare: {url} ---")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Select items
        items = soup.select('li h4.bold a.black')
        print(f"Found {len(items)} items with selector 'li h4.bold a.black'")
        
        for i, item in enumerate(items[:5]):
            print(f"\nItem {i+1}:")
            title = item.get_text(strip=True)
            print(f"  Title: {title}")
            
            li = item.find_parent('li')
            if li:
                time_elem = li.select_one('time')
                print(f"  Time Tag: {time_elem}")
                if time_elem:
                    print(f"  datetime attr: {time_elem.get('datetime')}")
                    print(f"  text content: {time_elem.get_text(strip=True)}")
            else:
                print("  No parent li found")
                
    except Exception as e:
        print(f"Error: {e}")

def debug_platum():
    url = 'https://platum.kr/category/investment'
    print(f"\n--- Debugging Platum: {url} ---")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        items = soup.select('article.archive-post')
        print(f"Found {len(items)} items with selector 'article.archive-post'")
        
        for i, item in enumerate(items[:5]):
            print(f"\nItem {i+1}:")
            title_elem = item.select_one('h2.entry-title a')
            if title_elem:
                print(f"  Title: {title_elem.get_text(strip=True)}")
            else:
                print("  No title found")
                
            time_elem = item.select_one('time.entry-date')
            print(f"  Time Tag: {time_elem}")
            if time_elem:
                print(f"  datetime attr: {time_elem.get('datetime')}")
                print(f"  text content: {time_elem.get_text(strip=True)}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_venturesquare()
    debug_platum()
