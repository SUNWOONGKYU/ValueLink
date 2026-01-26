import json
import os

# 파일 경로
FILE_A = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\final_collected_news.json'
FILE_B = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\missing_sites_data.json'
OUTPUT_FILE = r'C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\inbox\investment_news_final_v1.json'

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def main():
    data_a = load_json(FILE_A) # 27건 (벤처스퀘어, 블로터)
    data_b = load_json(FILE_B) # 10건 (더벨)
    
    # 통합 및 정규화
    merged = []
    seen_urls = set()
    
    # Data A 처리
    for item in data_a:
        url = item.get('url') or item.get('article_url')
        if url and url not in seen_urls:
            merged.append({
                'site_name': item.get('site_name'),
                'title': item.get('title') or item.get('article_title'),
                'url': url,
                'published_date': item.get('date_snippet') or item.get('published_date') or '2026-01-XX',
                'source': 'auto_scraper'
            })
            seen_urls.add(url)
            
    # Data B 처리
    for item in data_b:
        url = item.get('article_url') or item.get('url')
        if url and url not in seen_urls:
             merged.append({
                'site_name': item.get('site_name'),
                'title': item.get('article_title'),
                'url': url,
                'published_date': item.get('published_date'),
                'source': 'manual_scraper'
            })
             seen_urls.add(url)
             
    # 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        
    print(f"Final Merge Complete: {len(merged)} items saved.")
    print(f"File: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
