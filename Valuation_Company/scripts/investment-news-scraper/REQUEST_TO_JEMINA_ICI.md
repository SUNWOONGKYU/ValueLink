# 재미나 ICI 작업 요청서

**작성일**: 2026-01-25
**요청자**: 사용자
**작성자**: Claude Code

---

## 📋 현재 상황

### ✅ 완료된 작업 (Claude Code)
1. Supabase 테이블 2개 생성 완료
   - `investment_news_articles` (기사 저장)
   - `investment_news_ranking` (랭킹 집계)

2. Python 스크래핑 스크립트 작성 완료
   - 파일: `scrape_investment_news.py`
   - 환경 설정: `.env` (Supabase 연결 완료)
   - 패키지 설치: 완료

3. 테스트 실행 결과
   - ❌ **수집 건수: 0건**
   - ❌ 모든 사이트에서 데이터 수집 실패

---

## ❌ 문제점

**원인**: `scrape_generic_site()` 함수가 **범용 템플릿**이라서 각 사이트의 실제 HTML 구조와 맞지 않음

**로그 확인**:
```
[8] 더브이씨: 0건 수집
[9] 벤처스퀘어: 0건 수집
[10] 플래텀: 0건 수집
... (모든 사이트 0건)
```

---

## 🎯 재미나 ICI가 해야 할 작업

### 작업 내용
**각 사이트의 HTML 구조에 맞게 스크래핑 함수 커스터마이징**

### 대상 사이트 (19개)
| 번호 | 사이트명 | URL |
|------|---------|-----|
| 8 | 더브이씨 | https://thevc.kr |
| 9 | 벤처스퀘어 | https://www.venturesquare.net |
| 10 | 플래텀 | https://platum.kr |
| 11 | 스타트업투데이 | https://startuptoday.kr |
| 12 | 스타트업엔 | https://startupn.kr |
| 13 | 아웃스탠딩 | https://outstanding.kr |
| 14 | 모비인사이드 | https://mobiinside.co.kr |
| 15 | 지디넷코리아 | https://www.zdnet.co.kr |
| 16 | 더벨 | https://www.thebell.co.kr |
| 17 | 넥스트유니콘 | https://nextunicorn.kr |
| 18 | 테크월드뉴스 | https://www.epnc.co.kr |
| 19 | AI타임스 | https://www.aitimes.com |
| 20 | 벤처경영신문 | https://www.vmnews.co.kr |
| 21 | 뉴스톱 | https://www.newstopkorea.com |
| 22 | 블로터 | https://www.bloter.net |
| 23 | 이코노미스트 | https://www.economist.co.kr |
| 24 | 매일경제 MK테크리뷰 | https://www.mk.co.kr/news/it |
| 25 | 다음뉴스 벤처/스타트업 | https://news.daum.net/section/2/venture |
| 26 | 대한민국 정책브리핑 | https://www.korea.kr |

---

## 📁 파일 위치

**프로젝트 경로**:
```
C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\
```

**수정할 파일**:
```
scrape_investment_news.py
```

**수정할 함수**:
- `scrape_generic_site()` (137번째 줄부터)

---

## 🔧 수정 방법

### 현재 코드 (범용 템플릿 - 작동 안 함)

```python
def scrape_generic_site(site: Dict) -> List[Dict]:
    """범용 스크래핑 함수 (작동 안 함)"""

    # 기사 목록 추출 (실제로는 사이트별로 다름)
    article_elements = soup.select('article') or soup.select('.article-item')

    for element in article_elements:
        # 제목 추출
        title_elem = element.select_one('h2, h3, .title')
        # URL 추출
        link_elem = element.select_one('a[href]')
        # 날짜 추출
        date_elem = element.select_one('.date, .publish-date')
```

### 수정 방법 (사이트별 커스터마이징)

#### 단계 1: 사이트 HTML 구조 분석

각 사이트를 브라우저에서 열고:
1. F12 (개발자 도구)
2. Elements 탭
3. 기사 제목 요소 찾기 → 클래스명, 태그 확인

**예시 (벤처스퀘어)**:
- 기사 목록: `<div class="post-list">`
- 개별 기사: `<article class="post-item">`
- 제목: `<h3 class="post-title">`
- 링크: `<a class="post-link" href="...">`
- 날짜: `<time class="post-date">2026-01-15</time>`

#### 단계 2: 사이트별 함수 작성

**권장 방식**: 사이트별로 별도 함수 작성

```python
def scrape_venturesquare(site: Dict) -> List[Dict]:
    """벤처스퀘어 전용 스크래핑"""
    articles = []
    site_number = site['number']
    site_name = site['name']

    # 투자 섹션 URL
    url = 'https://www.venturesquare.net/category/investment'

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')

    # 실제 HTML 구조에 맞게 수정
    for article_elem in soup.select('article.post-item'):  # 실제 셀렉터
        try:
            # 제목
            title = article_elem.select_one('h3.post-title').get_text(strip=True)

            # 키워드 필터링
            if not contains_keyword(title):
                continue

            # URL
            article_url = article_elem.select_one('a.post-link')['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.venturesquare.net' + article_url

            # 날짜
            date_text = article_elem.select_one('time.post-date').get_text(strip=True)
            published_date = parse_date(date_text)

            # 날짜 필터링
            if not published_date or not is_valid_date(published_date):
                continue

            # 내용 발췌 (선택 사항)
            snippet_elem = article_elem.select_one('.post-excerpt')
            snippet = snippet_elem.get_text(strip=True)[:200] if snippet_elem else None

            articles.append({
                'site_number': site_number,
                'site_name': site_name,
                'site_url': 'www.venturesquare.net',
                'article_title': title,
                'article_url': article_url,
                'published_date': published_date.isoformat(),
                'content_snippet': snippet,
            })

        except Exception as e:
            logger.error(f"기사 파싱 중 오류: {e}")
            continue

    logger.info(f"✅ [{site_number}] {site_name}: {len(articles)}건 수집")
    return articles


def scrape_platum(site: Dict) -> List[Dict]:
    """플래텀 전용 스크래핑"""
    # 플래텀 HTML 구조에 맞게 작성
    ...


# ... 19개 사이트 각각 함수 작성
```

#### 단계 3: main() 함수 수정

```python
def main():
    """메인 실행 함수"""

    # 사이트별 스크래핑 함수 매핑
    scraping_functions = {
        8: scrape_venturesquare,  # 더브이씨 (잘못 매핑됨, 수정 필요)
        9: scrape_venturesquare,
        10: scrape_platum,
        11: scrape_startuptoday,
        # ... 나머지 사이트
    }

    for idx, site in enumerate(SITES, 1):
        site_number = site['number']

        # 해당 사이트 전용 함수 호출
        if site_number in scraping_functions:
            articles = scraping_functions[site_number](site)
        else:
            # 기본 함수 (작동 안 함)
            articles = scrape_generic_site(site)

        total_articles.extend(articles)
        time.sleep(REQUEST_DELAY)
```

---

## 🔍 HTML 구조 분석 팁

### 방법 1: 브라우저 개발자 도구
1. 사이트 열기
2. F12 (개발자 도구)
3. 기사 제목 우클릭 → "검사"
4. HTML 구조 확인

### 방법 2: Python으로 확인
```python
import requests
from bs4 import BeautifulSoup

url = 'https://www.venturesquare.net'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# HTML 출력 (파일로 저장)
with open('venturesquare.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

# 브라우저에서 열어서 구조 확인
```

### 방법 3: 일반적인 패턴

**기사 목록 컨테이너**:
- `<div class="news-list">`, `<section class="articles">`
- `<ul class="post-list">`, `<div id="content">`

**개별 기사**:
- `<article>`, `<li class="post">`, `<div class="item">`

**제목**:
- `<h1>`, `<h2>`, `<h3>`
- `.title`, `.headline`, `.post-title`

**링크**:
- `<a href="...">`

**날짜**:
- `<time>`, `<span class="date">`, `.publish-date`

---

## 🧪 테스트 방법

### 1. 개별 사이트 테스트

함수를 수정할 때마다:
```python
# scrape_investment_news.py 맨 아래 추가
if __name__ == '__main__':
    # 테스트: 벤처스퀘어만
    test_site = {'number': 9, 'name': '벤처스퀘어', 'url': 'https://www.venturesquare.net'}
    articles = scrape_venturesquare(test_site)
    print(f"수집 건수: {len(articles)}")
    if articles:
        print("첫 번째 기사:", articles[0])
```

실행:
```powershell
python scrape_investment_news.py
```

### 2. 전체 실행

모든 사이트 함수 작성 완료 후:
```powershell
python scrape_investment_news.py
```

### 3. 데이터 확인

Supabase SQL Editor에서:
```sql
-- 전체 건수
SELECT COUNT(*) FROM investment_news_articles;

-- 사이트별 건수
SELECT site_name, COUNT(*) as cnt
FROM investment_news_articles
GROUP BY site_name
ORDER BY cnt DESC;

-- 최근 기사 10개
SELECT site_name, article_title, published_date
FROM investment_news_articles
ORDER BY collected_at DESC
LIMIT 10;
```

---

## ⚠️ 주의사항

### 1. 동적 사이트 (JavaScript 렌더링)
일부 사이트는 JavaScript로 콘텐츠를 로드합니다.

**확인 방법**:
```python
response = requests.get(url)
print(response.text)  # HTML에 기사가 없으면 JavaScript 사이트
```

**해결책**: Selenium 사용
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)  # JavaScript 로딩 대기

# Selenium으로 요소 찾기
articles = driver.find_elements(By.CSS_SELECTOR, 'article.post')
```

**Selenium 설치**:
```powershell
pip install selenium webdriver-manager
```

### 2. robots.txt 확인
각 사이트의 크롤링 정책 확인:
```
https://www.venturesquare.net/robots.txt
```

### 3. 요청 제한
- 너무 빠른 요청은 IP 차단 가능
- 현재 설정: 2초 대기 (적절함)

### 4. SSL 에러
로그에 SSL 에러가 있었음 (벤처경영신문):
```python
# SSL 검증 비활성화 (임시)
response = requests.get(url, headers=HEADERS, verify=False)
```

---

## 📊 예상 결과

각 사이트별 평균 10-25건 수집 예상:
- 총 200-500건

성공 시:
```
✅ 스크래핑 완료!
📊 수집 건수: 287건
💾 저장 건수: 287건

📈 사이트별 수집 건수:
  - 벤처스퀘어: 45건
  - 플래텀: 38건
  - 더브이씨: 32건
  ...
```

---

## 🚀 완료 후 작업

### 1. 랭킹 업데이트
Supabase SQL Editor에서:
```sql
SELECT update_news_ranking();
```

### 2. 랭킹 조회
```sql
SELECT * FROM v_latest_ranking;
```

### 3. 결과 보고
사용자에게 최종 랭킹 제공

---

## 📞 문의

**파일 위치**: `C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\`
**문제 발생 시**: 로그 확인 (`scraping_log.txt`)

---

**작성 완료**: 2026-01-25
**요청자**: 사용자
**담당자**: 재미나 ICI
