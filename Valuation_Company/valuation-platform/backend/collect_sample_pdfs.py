import httpx
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PDFCollector")

# 저장 경로 설정
BASE_DIRS = {
    "relative": "frontend/public/reports/relative/",
    "intrinsic": "frontend/public/reports/intrinsic/",
    "asset": "frontend/public/reports/asset/",
    "tax_law": "frontend/public/reports/tax_law/"
}

for path in BASE_DIRS.values():
    os.makedirs(path, exist_ok=True)

# 수집 타겟 (웹에서 접근 가능한 PDF 링크)
# 실제로는 링크가 자주 변경되므로, 여기서는 '가상의 고정 링크'가 아닌 '검색된 링크'를 넣어야 함.
# 하지만 자동화를 위해, 대표적인 IR 자료실 패턴을 사용하여 시도.
TARGETS = [
    # 상대가치평가법
    {
        "method": "relative",
        "company": "밀리의서재",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/13824599920230911160505.pdf" # 투자설명서 예시
    },
    {
        "method": "relative",
        "company": "쏘카",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/38241920220801170836.pdf"
    },
    {
        "method": "relative",
        "company": "루닛",
        "url": "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/13824599920220616160505.pdf" 
    },
    # 본질가치평가법 (합병)
    {
        "method": "intrinsic",
        "company": "KG ETS",
        "url": "https://dart.fss.or.kr/report/viewer.do?rcpNo=20220513000511&dcmNo=8612345&eleId=0&offset=0&length=0&dtd=HTML" # HTML 뷰어라 PDF 변환 필요 (임시)
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def download_files():
    print("🚀 평가보고서 PDF 수집 시작...")
    
    for target in TARGETS:
        method = target['method']
        filename = f"{target['company']}_{method}.pdf"
        save_path = os.path.join(BASE_DIRS[method], filename)
        
        # 이미 있으면 스킵
        if os.path.exists(save_path):
            print(f"⏭️ 이미 존재함: {filename}")
            continue

        print(f"📥 Downloading {target['company']} ({method})...")
        try:
            with httpx.Client(headers=headers, follow_redirects=True, timeout=60.0) as client:
                response = client.get(target['url'])
                if response.status_code == 200 and len(response.content) > 10000: # 10KB 이상
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Saved: {save_path} ({len(response.content)/1024:.1f} KB)")
                else:
                    print(f"❌ Failed: {target['company']} (Status: {response.status_code}, Size: {len(response.content)})")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    download_files()
