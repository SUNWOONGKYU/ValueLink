import httpx
import os

BASE_DIR = "frontend/public/reports/relative/"
os.makedirs(BASE_DIR, exist_ok=True)

# 실제 검색된 링크 (가정: KB증권 리포트 등)
# 실제 링크는 유효기간이나 접근 권한이 있을 수 있어, 공개된 리포트 사이트(한경컨센서스 등)를 우회적으로 이용하거나
# 구글 검색 결과에서 나온 직접 링크를 사용해야 함.
TARGETS = [
    {
        "company": "AprilBio",
        "url": "https://img.kbsec.com/upload/research/report/20220713143527257.pdf" # KB IPO Brief 예시 링크
    },
    {
        "company": "Lunit",
        "url": "https://img.kbsec.com/upload/research/report/20220616143527257.pdf" # 예시
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download():
    print("🚀 IPO 리포트 다운로드 시도...")
    for t in TARGETS:
        save_path = os.path.join(BASE_DIR, f"{t['company']}_IPO_Report.pdf")
        try:
            with httpx.Client(headers=headers, verify=False) as client:
                res = client.get(t['url'])
                if res.status_code == 200:
                    with open(save_path, "wb") as f:
                        f.write(res.content)
                    print(f"✅ Saved: {save_path}")
                else:
                    print(f"❌ Failed: {t['company']} ({res.status_code})")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    download()
