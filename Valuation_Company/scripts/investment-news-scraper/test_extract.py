import re
import csv

def extract_sources(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all source URLs
    # Pattern: "url":"https://..."
    # We want to exclude logos and images
    exclude_patterns = ['logo', 'image', 'profile', 'product', 'organizations', 'svg', 'png', 'jpg', 'jpeg']
    
    raw_urls = re.findall(r'"url":"(https?://[^"]+)"', content)
    source_urls = []
    for url in raw_urls:
        if not any(ex in url for ex in exclude_patterns):
            source_urls.append(url)
    
    # Find all company names
    # Pattern: "name":"..."
    names = re.findall(r'"name":"([^"]+)"', content)
    
    return names, source_urls

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
            pass
    return companies

def main():
    names, source_urls = extract_sources('scripts/investment-news-scraper/thevc_page_source.html')
    print(f"Extracted {len(names)} names and {len(source_urls)} source URLs from TheVC")
    
    companies = load_companies()
    
    # Try to match names with URLs
    # Since the structure is complex, let's just use Google for accuracy
    # but I can use these found URLs as candidates.
    
    # Print some URLs to see if they are useful
    for url in source_urls[:20]:
        print(f"Candidate: {url}")

if __name__ == '__main__':
    main()
