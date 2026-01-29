import json
import os

# Define the file path
file_path = 'backend/reparse_result.json'

# Define the refinement mapping
refinements = {
    "SDT": "Quantum/DX",
    "에디트콜렉티브": "Proptech/AI",
    "타이디비": "Database/Infra",
    "Konnect": "Web3/Platform",
    "코넥트": "Web3/Platform",
    "한국딥러닝": "AI/OCR",
    "리벨리온": "AI Semiconductor",
    "크라우드웍스": "AI Data Platform",
    "메타 플랫폼스": "Metaverse/SNS",
    "올거나이즈": "AI/LLM",
    "로그프레소": "Cybersecurity",
    "큐빅": "AI/Synthetic Data",
    "아이에스티이": "Semiconductor Equipment",
    "그린다": "Waste Management",
    "오피스허브": "Shared Office",
    "탄탄코어": "Semiconductor IP",
    "알스퀘어": "Proptech/Data",
    "밸류맵": "Proptech/Data",
    "십일리터": "Pet Healthcare",
    "위드포인츠": "Loyalty Platform",
    "퓨어스페이스": "Food Tech",
    "휴이노": "Digital Healthcare",
    "인탑스": "Manufacturing/EMS",
    "어메스": "Mobility/AI",
    "뉴패러다임인베스트먼트": "VC/Accelerator",
    "아워스팟": "Edutech",
    "한패스": "Fintech/Forex",
    "법무법인 미션": "Legal Service",
    "세종창조경제혁신센터": "Accelerator",
    "아크리얼": "Display Materials",
    "와디즈임팩트": "Crowdfunding",
    "와디즈": "Crowdfunding/Platform",
    "자비스앤빌런즈": "Tax Tech",
    "아셉틱": "Medical Device",
    "퍼슬리": "Data Platform",
    "워터베이션": "Eco Tech",
    "주미당": "F&B",
    "긱스로프트": "Game/Content",
    "플로라운지": "O2O/Flower",
    "네이버클라우드": "Cloud/AI",
    "바이버": "Luxury Commerce",
    "KRG그룹": "Mobility/Logistics", # Estimated
    "피키": "Social/Platform", # Piky
    "매니패스트": "IT/Software",
    "엘바": "AgriTech/Smart Farm", # Estimated
    "블루포인트파트너스": "Accelerator/VC",
    "넥스트파이낸스이니셔티브": "Fintech",
    "뉴아이": "Fintech/AI",
    "빅웨이브카": "Mobility/Used Car",
    "차봇 모빌리티": "Mobility Platform",
    "열다컴퍼니": "O2O/Service",
    "클래시스": "Medical Device/Aesthetics"
}

def refine_industries():
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    # Process companies
    if 'companies' in data:
        for company in data['companies']:
            name = company.get('company')
            current_industry = company.get('industry')
            
            # Refine if name is in our mapping
            if name in refinements:
                new_industry = refinements[name]
                if current_industry != new_industry:
                    print(f"Updating {name}: {current_industry} -> {new_industry}")
                    company['industry'] = new_industry
                    updated_count += 1
            
            # Additional heuristic for "AI" if not mapped
            elif current_industry == "AI":
                print(f"Warning: Unmapped 'AI' industry for {name}. Needs manual check.")
                
            # Additional heuristic for "IT" if not mapped
            elif current_industry == "IT":
                print(f"Warning: Unmapped 'IT' industry for {name}. Needs manual check.")

    # Save updated data
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    print(f"Total updated entries: {updated_count}")
    print("Refinement complete.")

if __name__ == "__main__":
    refine_industries()
