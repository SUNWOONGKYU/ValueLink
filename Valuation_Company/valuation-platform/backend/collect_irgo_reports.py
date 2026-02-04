import httpx
import os

# 저장 경로
BASE_PATH = "frontend/public/reports/relative/"
os.makedirs(BASE_PATH, exist_ok=True)

# 실제 투자설명서 링크
TARGETS = [
    {
        "company": "Millie",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/13824599920230911160505.pdf"
    },
    {
        "company": "Lunit",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/13824599920220616160505.pdf"
    },
    {
        "company": "AprilBio",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/13824599920220713160505.pdf"
    },
    {
        "company": "Socar",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/38241920220801170836.pdf"
    },
    {
        "company": "GaonChips",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/13824599920220428160505.pdf"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_and_report():
    failed_list = []
    print("🚀 투자설명서 다운로드 시작...")
    
    for t in TARGETS:
        filename = f"{t['company']}_Prospectus.pdf"
        save_path = os.path.join(BASE_PATH, filename)
        
        try:
            with httpx.Client(headers=headers, follow_redirects=True, timeout=60.0) as client:
                res = client.get(t['url'])
                if res.status_code == 200 and len(res.content) > 10000:
                    with open(save_path, "wb") as f:
                        f.write(res.content)
                    print(f"✅ Downloaded: {save_path} ({len(res.content)/1024/1024:.2f} MB)")
                else:
                    print(f"❌ Failed: {t['company']} (Status: {res.status_code})")
                    failed_list.append(f"{t['company']}: {t['url']}")
        except Exception as e:
            print(f"❌ Error: {t['company']} - {e}")
            failed_list.append(f"{t['company']}: {t['url']}")

    # 실패 목록 저장
    if failed_list:
        with open("frontend/public/reports/DOWNLOAD_LIST.txt", "w", encoding="utf-8") as f:
            f.write("=== 직접 다운로드 필요 목록 ===\n")
            f.write("\n".join(failed_list))
        print(f"\n⚠️ {len(failed_list)}건 다운로드 실패. 목록이 'frontend/public/reports/DOWNLOAD_LIST.txt'에 저장되었습니다.")

if __name__ == "__main__":
    download_and_report()
