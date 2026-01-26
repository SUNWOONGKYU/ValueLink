import requests

url = "https://www.venturesquare.net/category/news-contents/investment"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    resp = requests.get(url, headers=headers)
    with open('venturesquare_dump.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)
    print("Dump success")
except Exception as e:
    print(f"Error: {e}")
