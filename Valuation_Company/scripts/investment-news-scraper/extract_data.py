import json
import re
import csv

def extract_thevc_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to find the JSON-like data in the script tags
    # The data seems to be in a large array or object structure
    # Let's look for investee names and source URLs
    
    # Simple regex to find company names and URLs
    # Example: "name":"오픈마일", ... "url":"https://biz.chosun.com/..."
    # The structure in the file is a bit complex, but let's try to find patterns.
    
    # Extract names and products
    names = re.findall(r'"name":"([^"]+)"', content)
    urls = re.findall(r'"url":"(https?://[^"]+)"', content)
    
    # Actually, the file has a lot of "url" fields for logos etc.
    # We need to find the "source" URL.
    # In the snippet: "source":75},"c8a7632a... "url":76},"https://biz.chosun.com/..."
    # It's using some indexing. This is likely Nuxt/Vue hydration data.
    
    # Let's try a different approach: search for company names and then find the nearest URL
    return content

def load_companies():
    companies = []
    for i in range(1, 4):
        file_path = f'scripts/investment-news-scraper/not_found_group{i}.csv'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    companies.append(row)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return companies

def main():
    companies = load_companies()
    print(f"Loaded {len(companies)} companies")
    
    # Extract from venturesquare_final.json
    vs_data = []
    try:
        with open('scripts/investment-news-scraper/inbox/venturesquare_final.json', 'r', encoding='utf-8') as f:
            vs_data = json.load(f)
    except Exception as e:
        print(f"Error loading venturesquare_final.json: {e}")
    
    results = []
    for comp in companies:
        name = comp['기업명']
        found_url = None
        found_source = None
        
        # Check in VentureSquare data
        for item in vs_data:
            if name in item['title'] or item['title'].startswith(name[:3]):
                found_url = item['url']
                found_source = '벤처스퀘어'
                break
        
        if not found_url:
            # Special case for known typos
            typo_map = {
                '이노션스': '이노서스',
                '큐투켓': '큐투컷',
                '디디덴웰케어': '다다닥헬스케어',
                '핵사후면케어': '헥사휴먼케어',
                '엘리사젠': '엘리시젠',
                '소프트웨어융합연구소': '소프트웨어융합연구소', # same but check investors
            }
            mapped_name = typo_map.get(name, name)
            for item in vs_data:
                if mapped_name in item['title']:
                    found_url = item['url']
                    found_source = '벤처스퀘어'
                    break
        
        comp['뉴스URL'] = found_url if found_url else ''
        comp['뉴스소스'] = found_source if found_source else ''
        results.append(comp)
    
    # Count found
    found_count = len([c for c in results if c['뉴스URL']])
    print(f"Found {found_count} URLs from VentureSquare JSON")
    
    # Save partial results
    with open('scripts/investment-news-scraper/gemini_results_v1.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    main()
