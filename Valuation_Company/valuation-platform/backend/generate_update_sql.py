import json
import os

file_path = 'backend/reparse_result.json'
output_path = 'backend/update_industry.sql'

def generate_sql():
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'companies' not in data:
        print("Error: 'companies' key not found in JSON.")
        return

    sql_statements = [
        "-- Update industry fields in deals table",
        "-- Generated from reparse_result.json",
        ""
    ]

    for item in data['companies']:
        company_name = item.get('company')
        industry = item.get('industry')
        if company_name and industry:
            safe_company = company_name.replace("'", "''")
            safe_industry = industry.replace("'", "''")
            sql_statements.append(f"UPDATE deals SET industry = '{safe_industry}' WHERE company_name = '{safe_company}';")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ SQL 파일 생성 완료: {output_path} (총 {len(sql_statements)-3}개 구문)")

if __name__ == "__main__":
    generate_sql()
