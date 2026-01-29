import httpx
import os

# 저장 경로
save_path = "frontend/public/reports/dcf/비플라이소프트_DCF_202206.pdf"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# DART PDF 다운로드 URL (예시 링크 - 실제 고유 번호 기반)
# 실제로는 공시 번호를 정확히 알아야 함. 여기서는 공개된 PDF 링크를 사용.
url = "https://dart.fss.or.kr/pdf/download/main.do?rcpNo=20220527000511&dcmNo=8631211" # 예시 공시 번호

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def download_test():
    print(f"Downloading PDF from {url}...")
    try:
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(url)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Successfully saved: {save_path}")
                print(f"File Size: {len(response.content) / 1024:.2f} KB")
            else:
                print(f"❌ Failed to download. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    download_test()
