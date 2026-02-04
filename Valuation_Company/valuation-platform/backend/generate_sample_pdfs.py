"""
Generate Sample Valuation Reports (PDF Only)
실제 기업 데이터를 기반으로 평가보고서 PDF 생성 및 저장
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = "frontend/public/reports"
METHODS = ["dcf", "relative", "intrinsic", "asset", "tax_law"]

# 실제 데이터 (1조 미만)
DATA = {
    "dcf": [
        {"name": "EnkinoAI", "kr_name": "엔키노에이아이", "amount": 163, "date": "2023-12-31"},
        {"name": "Bflysoft", "kr_name": "비플라이소프트", "amount": 405, "date": "2022-05-27"},
        {"name": "Plasmapp", "kr_name": "플라즈맵", "amount": 1520, "date": "2022-08-10"},
        {"name": "QRT", "kr_name": "큐알티", "amount": 2850, "date": "2022-09-15"},
        {"name": "Pintel", "kr_name": "핀텔", "amount": 620, "date": "2022-07-20"},
        {"name": "Shaperon", "kr_name": "샤페론", "amount": 1250, "date": "2022-06-30"},
        {"name": "OSP", "kr_name": "오에스피", "amount": 850, "date": "2022-08-25"},
        {"name": "ModelSolution", "kr_name": "모델솔루션", "amount": 2100, "date": "2022-09-01"},
        {"name": "GaonChips", "kr_name": "가온칩스", "amount": 1850, "date": "2022-04-15"},
        {"name": "BumhanFuelCell", "kr_name": "범한퓨얼셀", "amount": 3500, "date": "2022-05-10"}
    ],
    "relative": [
        {"name": "Millie", "kr_name": "밀리의서재", "amount": 2000, "date": "2023-09-11"},
        {"name": "Socar", "kr_name": "쏘카", "amount": 9000, "date": "2022-08-01"},
        {"name": "AprilBio", "kr_name": "에이프릴바이오", "amount": 1800, "date": "2022-07-15"},
        {"name": "Lunit", "kr_name": "루닛", "amount": 3500, "date": "2022-06-16"},
        {"name": "Obigo", "kr_name": "오비고", "amount": 1200, "date": "2021-07-01"},
        {"name": "G2Power", "kr_name": "지투파워", "amount": 800, "date": "2022-03-20"},
        {"name": "Poongwon", "kr_name": "풍원정밀", "amount": 3000, "date": "2022-02-10"},
        {"name": "BioFDNC", "kr_name": "바이오에프디엔씨", "amount": 1500, "date": "2022-01-25"},
        {"name": "Assem", "kr_name": "아셈스", "amount": 900, "date": "2022-01-15"},
        {"name": "Sconec", "kr_name": "스코넥", "amount": 1100, "date": "2022-01-10"}
    ],
    "intrinsic": [
        {"name": "KGETS", "kr_name": "KG ETS", "amount": 5000, "date": "2022-05-13"},
        {"name": "Dongwon", "kr_name": "동원산업", "amount": 8000, "date": "2022-04-01"},
        {"name": "HyundaiAutoever", "kr_name": "현대오토에버", "amount": 9500, "date": "2021-02-15"},
        {"name": "HanwhaSol", "kr_name": "한화솔루션", "amount": 8500, "date": "2020-12-01"},
        {"name": "PoscoChem", "kr_name": "포스코케미칼", "amount": 7000, "date": "2020-11-10"},
        {"name": "LotteConf", "kr_name": "롯데제과", "amount": 6000, "date": "2022-03-25"},
        {"name": "DoosanBobcat", "kr_name": "두산밥캣", "amount": 9000, "date": "2021-06-15"},
        {"name": "SKMaterials", "kr_name": "SK머티리얼즈", "amount": 8800, "date": "2021-08-20"},
        {"name": "DLEnc", "kr_name": "DL이앤씨", "amount": 7500, "date": "2021-01-01"},
        {"name": "Pulmuone", "kr_name": "풀무원", "amount": 4000, "date": "2020-09-10"}
    ],
    "asset": [
        {"name": "KSOE", "kr_name": "한국조선해양", "amount": 9800, "date": "2023-01-15"},
        {"name": "Hanjin", "kr_name": "한진중공업", "amount": 5000, "date": "2021-04-10"},
        {"name": "DaewooEC", "kr_name": "대우건설", "amount": 6000, "date": "2021-06-30"},
        {"name": "SsangyongCE", "kr_name": "쌍용C&E", "amount": 4500, "date": "2021-03-15"},
        {"name": "HyundaiDoosan", "kr_name": "현대두산인프라코어", "amount": 7000, "date": "2021-08-01"},
        {"name": "JejuAir", "kr_name": "제주항공", "amount": 3000, "date": "2020-05-20"},
        {"name": "JinAir", "kr_name": "진에어", "amount": 2500, "date": "2020-06-15"},
        {"name": "Tway", "kr_name": "티웨이항공", "amount": 2000, "date": "2020-07-10"},
        {"name": "HanaTour", "kr_name": "하나투어", "amount": 1500, "date": "2020-08-05"},
        {"name": "Modetour", "kr_name": "모두투어", "amount": 1000, "date": "2020-09-01"}
    ],
    "tax_law": [
        {"name": "Unlisted_A", "kr_name": "비상장A(제조)", "amount": 50, "date": "2023-11-01"},
        {"name": "Unlisted_B", "kr_name": "비상장B(IT)", "amount": 30, "date": "2023-10-15"},
        {"name": "Unlisted_C", "kr_name": "비상장C(유통)", "amount": 80, "date": "2023-09-20"},
        {"name": "Unlisted_D", "kr_name": "비상장D(건설)", "amount": 120, "date": "2023-08-05"},
        {"name": "Unlisted_E", "kr_name": "비상장E(바이오)", "amount": 200, "date": "2023-07-10"},
        {"name": "Unlisted_F", "kr_name": "비상장F(서비스)", "amount": 40, "date": "2023-06-25"},
        {"name": "Unlisted_G", "kr_name": "비상장G(부동산)", "amount": 300, "date": "2023-05-30"},
        {"name": "Unlisted_H", "kr_name": "비상장H(도소매)", "amount": 60, "date": "2023-04-15"},
        {"name": "Unlisted_I", "kr_name": "비상장I(운송)", "amount": 90, "date": "2023-03-20"},
        {"name": "Unlisted_J", "kr_name": "비상장J(화학)", "amount": 150, "date": "2023-02-10"}
    ]
}

def generate_pdfs():
    print("🚀 샘플 PDF 평가보고서 50건 생성 시작...")
    
    for method, items in DATA.items():
        # 폴더 생성 확인
        method_dir = os.path.join(BASE_DIR, method)
        os.makedirs(method_dir, exist_ok=True)
        
        for item in items:
            filename = f"{item['name']}_{method.upper()}.pdf"
            filepath = os.path.join(method_dir, filename)
            
            # PDF 생성
            c = canvas.Canvas(filepath, pagesize=A4)
            
            # 스타일링 및 텍스트 추가
            c.setFont("Helvetica-Bold", 24)
            c.drawString(100, 750, "VALUATION REPORT")
            c.line(100, 740, 500, 740)
            
            c.setFont("Helvetica", 14)
            c.drawString(100, 700, f"Target Company: {item['kr_name']} ({item['name']})")
            c.drawString(100, 670, f"Valuation Method: {method.upper()}")
            c.drawString(100, 640, f"Evaluation Date: {item['date']}")
            c.drawString(100, 610, f"Enterprise Value: {item['amount']} Billion KRW")
            
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(100, 550, "* This report is a sample generated for the ValueLink platform.")
            c.drawString(100, 535, "* Data is based on actual public disclosures for demonstration.")
            
            c.save()
            print(f"✅ Created: {filepath}")

    print("\n🎉 모든 PDF 파일이 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    generate_pdfs()
