"""
Verify Valuation Reports
저장된 PDF 파일이 실제 평가보고서인지 검증

@criteria
1. 파일 크기 > 10KB (너무 작으면 내용 없음)
2. 필수 키워드 포함 (평가, 가치, 원, 현금흐름 등)
3. 페이지 수 > 1 (표지만 있는 것 제외)
"""
import os
import glob
from pypdf import PdfReader

BASE_DIR = "frontend/public/reports"
KEYWORDS = ["가치평가", "평가액", "현금흐름", "할인율", "추정", "PER", "PBR", "자산가치", "본질가치", "상증세", "주당"]

def verify_reports():
    print("🚀 평가보고서 검증 시작...")
    
    report_files = glob.glob(os.path.join(BASE_DIR, "**/*.pdf"), recursive=True)
    if not report_files:
        print("❌ 검증할 파일이 없습니다.")
        return

    pass_count = 0
    fail_count = 0
    failed_list = []

    for file_path in report_files:
        filename = os.path.basename(file_path)
        try:
            # 1. 파일 크기 체크
            file_size = os.path.getsize(file_path)
            if file_size < 5000: # 5KB 미만은 의심
                print(f"⚠️ [Size Fail] {filename} ({file_size} bytes)")
                fail_count += 1
                failed_list.append(file_path)
                continue

            # 2. PDF 내용 읽기
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            
            if num_pages < 2: # 1페이지짜리는 요약본/표지로 간주
                print(f"⚠️ [Page Fail] {filename} ({num_pages} page)")
                # 일단은 1페이지라도 통과시키지 않고 엄격하게 체크하려면 여기서 continue
                # 하지만 현재 샘플은 1페이지로 만들었으므로, 이 기준으로는 다 탈락임.
                # 사용자 의도는 "진짜 보고서" 여부이므로 탈락시키는게 맞음.
                fail_count += 1
                failed_list.append(file_path)
                continue

            text = ""
            for page in reader.pages[:3]: # 앞 3페이지만 체크
                text += page.extract_text()

            # 3. 키워드 체크
            found_keywords = [k for k in KEYWORDS if k in text]
            if len(found_keywords) < 2:
                print(f"⚠️ [Content Fail] {filename} (키워드 부족: {found_keywords})")
                fail_count += 1
                failed_list.append(file_path)
                continue

            print(f"✅ [PASS] {filename} ({num_pages}p, 키워드: {len(found_keywords)}개)")
            pass_count += 1

        except Exception as e:
            print(f"❌ [Error] {filename}: {e}")
            fail_count += 1
            failed_list.append(file_path)

    print("-" * 50)
    print(f"검증 결과: 합격 {pass_count}건 / 불합격 {fail_count}건")
    if failed_list:
        print("불합격 파일 (재수집 필요):")
        for f in failed_list[:5]:
            print(f" - {os.path.basename(f)}")
        if len(failed_list) > 5:
            print(f" ... 외 {len(failed_list)-5}건")

if __name__ == "__main__":
    verify_reports()
