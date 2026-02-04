import httpx
import os

# 저장 경로
save_path = "frontend/public/reports/dcf/KISTI_Tech_Valuation.pdf"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# 실제 PDF 링크 (검색 결과 기반 추정)
url = "https://repository.kisti.re.kr/bitstream/10580/15478/1/KISTI_Tech_Valuation.pdf" # 예시 링크, 실제로는 검색된 링크 사용 필요

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download():
    print(f"Downloading {url}...")
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=60.0, verify=False) as client:
            response = client.get(url)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {save_path} ({len(response.content)/1024:.1f} KB)")
            else:
                print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    download()
