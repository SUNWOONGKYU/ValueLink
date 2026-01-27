#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 기사에서 기업 정보 추출
- CEO, 설립일, 지역, 투자금액, 날짜
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import time

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def extract_ceo_from_text(text):
    """텍스트에서 CEO 이름 추출"""

    # 제외할 키워드들
    exclude_keywords = [
        '주식회사', '스타트업', '기업', '회사',
        '와우테일', '우테일', '벤처스퀘어', '더브이씨',
        '인터뷰', '기자', '편집장', '작성자'
    ]

    # 패턴들
    patterns = [
        r'대표(?:이사)?\s+([가-힣]{2,4})(?:\s|,|\.)',
        r'([가-힣]{2,4})\s+대표(?:이사)?(?:\s|,|\.)',
        r'CEO\s+([가-힣]{2,4})(?:\s|,|\.)',
        r'([가-힣]{2,4})\s+CEO(?:\s|,|\.)',
        r'공동대표\s+([가-힣]{2,4})(?:\s|,|\.)',
        r'\(대표\s*([가-힣]{2,4})\)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            ceo_name = match.group(1)
            # 제외 키워드 확인
            if len(ceo_name) >= 2:
                excluded = False
                for keyword in exclude_keywords:
                    if keyword in ceo_name:
                        excluded = True
                        break
                if not excluded:
                    return ceo_name

    return None


def extract_founded_from_text(text):
    """텍스트에서 설립일 추출"""

    # 패턴들 (더 다양하게)
    patterns = [
        r'(\d{4})년\s*(?:설립|창업|창립|출범)',
        r'(?:설립|창업|창립|출범)\s*(\d{4})년',
        r'(\d{4})년\s*(?:설립|창업|창립|출범)(?:된|한|된)',
        r'(\d{4})년에\s*(?:설립|창업|창립|출범)',
        r'(\d{4})년\s*(?:부터|에)\s*(?:설립|창업|창립|출범)',
        r'(\d{4})\.\d{1,2}\s*(?:설립|창업|창립)',  # 2019.03 설립
        r'(\d{4})-\d{1,2}\s*(?:설립|창업|창립)',   # 2019-03 설립
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            year = match.group(1)
            # 1990~2026 사이만 유효
            if 1990 <= int(year) <= 2026:
                return f"{year}-01-01"  # YYYY-MM-DD 형식

    return None


def extract_location_from_text(text):
    """텍스트에서 지역 추출"""

    # 패턴들 - 주요 지역명
    locations = [
        '판교', '강남', '서초', '역삼', '삼성', '테헤란',
        '서울', '부산', '대구', '인천', '광주', '대전', '울산',
        '성남', '용인', '수원', '안양', '부천',
        '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
    ]

    patterns = [
        r'([가-힣]+)(?:에\s*본사|에\s*위치|소재)',
        r'본사[를]?\s*둔\s*([가-힣]+)',
        r'([가-힣]+)\s*(?:본사|사무실)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            location = match.group(1)
            # 주요 지역명에 포함되는지 확인
            for loc in locations:
                if loc in location:
                    return loc

    # 직접 지역명 검색
    for loc in locations:
        if loc in text:
            return loc

    return None


def extract_amount_from_text(text):
    """텍스트에서 투자금액 추출"""

    patterns = [
        r'(\d+(?:\.\d+)?)\s*억\s*원',
        r'(\d+(?:\.\d+)?)\s*억',
        r'(\d+(?:,\d+)?)\s*억',
        r'(\d+)\s*조\s*(\d+)\s*억',
        r'(\d+)\s*조',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if '조' in pattern:
                if len(match.groups()) == 2:  # X조 Y억
                    jo = int(match.group(1))
                    eok = int(match.group(2))
                    return jo * 10000 + eok
                else:  # X조
                    return int(match.group(1)) * 10000
            else:
                return int(float(match.group(1)))

    return None


def extract_date_from_html(soup, url):
    """HTML에서 날짜 추출"""

    # 메타 태그에서 추출
    meta_tags = [
        'article:published_time',
        'publishedDate',
        'datePublished',
        'pubdate',
    ]

    for tag in meta_tags:
        meta = soup.find('meta', property=tag) or soup.find('meta', attrs={'name': tag})
        if meta and meta.get('content'):
            try:
                date_str = meta.get('content')
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass

    # time 태그에서 추출
    time_tag = soup.find('time')
    if time_tag:
        datetime_attr = time_tag.get('datetime')
        if datetime_attr:
            try:
                date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass

    # URL에서 날짜 패턴 찾기
    url_date_patterns = [
        r'/(\d{4})/(\d{2})/(\d{2})/',
        r'/(\d{8})/',
    ]

    for pattern in url_date_patterns:
        match = re.search(pattern, url)
        if match:
            if len(match.groups()) == 3:
                return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            else:
                date_str = match.group(1)
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    return None


def extract_company_info():
    """뉴스 기사에서 기업 정보 추출"""

    print("=" * 70)
    print("뉴스 기사에서 기업 정보 추출")
    print("=" * 70)

    # 정보가 없는 레코드 가져오기 (50개씩 처리)
    result = supabase.table("deals")\
        .select("id, company_name, news_url, news_title, ceo, founded, location, amount, news_date")\
        .limit(50)\
        .execute()

    deals = result.data
    print(f"\n처리할 레코드: {len(deals)}개\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    success_count = 0
    fail_count = 0

    for idx, deal in enumerate(deals, 1):
        company_name = deal['company_name']
        news_url = deal.get('news_url')

        print(f"[{idx}/{len(deals)}] {company_name}...", end=" ")

        if not news_url:
            print("❌ URL 없음")
            fail_count += 1
            continue

        try:
            # 뉴스 페이지 크롤링
            response = requests.get(news_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 본문 텍스트 추출
            article_text = soup.get_text()

            # 정보 추출
            update_data = {}

            # CEO 추출 (없을 때만)
            if not deal.get('ceo'):
                ceo = extract_ceo_from_text(article_text)
                if ceo:
                    update_data['ceo'] = ceo

            # 설립일 추출 (없을 때만)
            if not deal.get('founded'):
                founded = extract_founded_from_text(article_text)
                if founded:
                    update_data['founded'] = founded

            # 지역 추출 (없을 때만)
            if not deal.get('location'):
                location = extract_location_from_text(article_text)
                if location:
                    update_data['location'] = location

            # 투자금액 추출 (없을 때만)
            if not deal.get('amount'):
                amount = extract_amount_from_text(article_text)
                if amount:
                    update_data['amount'] = amount

            # 날짜 추출 (없을 때만)
            if not deal.get('news_date'):
                news_date = extract_date_from_html(soup, news_url)
                if news_date:
                    update_data['news_date'] = news_date

            # DB 업데이트
            if update_data:
                supabase.table("deals")\
                    .update(update_data)\
                    .eq("id", deal['id'])\
                    .execute()

                result_str = []
                if 'ceo' in update_data:
                    result_str.append(f"CEO: {update_data['ceo']}")
                if 'founded' in update_data:
                    result_str.append(f"설립: {update_data['founded']}")
                if 'location' in update_data:
                    result_str.append(f"지역: {update_data['location']}")
                if 'amount' in update_data:
                    result_str.append(f"💰 {update_data['amount']}억")
                if 'news_date' in update_data:
                    result_str.append(f"📅 {update_data['news_date']}")

                print(f"✅ {', '.join(result_str)}")
                success_count += 1
            else:
                print("⚠️ 정보 없음")
                fail_count += 1

            time.sleep(0.3)  # 크롤링 간격

        except Exception as e:
            print(f"❌ {str(e)[:30]}")
            fail_count += 1

    print("\n" + "=" * 70)
    print("추출 완료")
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)


if __name__ == '__main__':
    extract_company_info()
