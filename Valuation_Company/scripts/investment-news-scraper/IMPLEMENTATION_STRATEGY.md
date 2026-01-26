# 10개 사이트 뉴스 수집 구현 전략

> 실제 테스트 결과 기반 구현 방법

---

## 연구 결과 요약

### ✅ 수집 가능: 8개 사이트

| # | 사이트 | 방법 | 상태 | 상세 |
|---|--------|------|------|------|
| 1 | **벤처스퀘어** | RSS | ✅ | 30개 기사, 최신 업데이트 |
| 2 | **스타트업투데이** | 웹 스크래핑 | ✅ | selector: `article`, 8개 요소 |
| 3 | **아웃스탠딩** | RSS | ✅ | 10개 기사 |
| 4 | 더벨 | - | ❌ | 유료 사이트, 선택자 없음 |
| 5 | 더브이씨 | - | ❌ | 투자사 목록, 선택자 없음 |
| 6 | **스타트업엔** | 웹 스크래핑 | ✅ | selector: `article`, 15개 요소 |
| 7 | **블로터** | 웹 스크래핑 | ✅ | selector: `article`, 23개 요소 (RSS 피드 비어있음) |
| 8 | **이코노미스트** | 웹 스크래핑 | ✅ | selector: `h2 a`, 2개 요소 |
| 9 | **플래텀** | RSS | ✅ | 10개 기사 |
| 10 | **AI타임스** | 웹 스크래핑 | ✅ | selector: `article`, 7개 요소 |

**결과:**
- ✅ RSS: 3개 (벤처스퀘어, 아웃스탠딩, 플래텀)
- ✅ 웹 스크래핑: 5개 (스타트업투데이, 스타트업엔, 블로터, 이코노미스트, AI타임스)
- ❌ 제외: 2개 (더벨, 더브이씨)

---

## 구현 단계

### Phase 1: RSS 피드 (3개 사이트) ⭐⭐⭐

**우선순위: 최우선**
- 벤처스퀘어
- 아웃스탠딩
- 플래텀

**예상 수집량:** 하루 30-50건

**구현 코드:**
```python
import feedparser

def collect_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        articles.append({
            'title': entry.title,
            'url': entry.link,
            'published': entry.published,
            'summary': entry.get('summary', '')
        })

    return articles

# 벤처스퀘어
venturesquare = collect_rss('https://www.venturesquare.net/feed')

# 아웃스탠딩
outstanding = collect_rss('https://outstanding.kr/feed')

# 플래텀
platum = collect_rss('https://platum.kr/feed')
```

---

### Phase 2: 웹 스크래핑 (5개 사이트) ⭐⭐

**우선순위: 중요**
- 스타트업투데이
- 스타트업엔
- 블로터
- 이코노미스트
- AI타임스

**예상 수집량:** 하루 20-40건

---

## 사이트별 상세 구현 방법

### 1. 벤처스퀘어 (RSS) ⭐⭐⭐

```python
URL = 'https://www.venturesquare.net/feed'

def collect_venturesquare():
    feed = feedparser.parse(URL)
    articles = []

    for entry in feed.entries:
        # 투자 키워드 필터링
        if any(kw in entry.title for kw in ['투자', '유치', '시리즈']):
            articles.append({
                'site_number': 9,
                'site_name': '벤처스퀘어',
                'site_url': 'https://www.venturesquare.net',
                'article_title': entry.title,
                'article_url': entry.link,
                'published_date': entry.published,
                'content_snippet': entry.get('summary', '')[:500]
            })

    return articles
```

**예상:** 하루 10-20건

---

### 2. 스타트업투데이 (웹 스크래핑) ⭐⭐

```python
URL = 'https://startuptoday.kr'
SELECTOR = 'article'

def collect_startuptoday():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for article in soup.select(SELECTOR):
        title_elem = article.select_one('h2, h3, .title')
        link_elem = article.select_one('a')

        if title_elem and link_elem:
            title = title_elem.text.strip()
            link = link_elem['href']

            # 절대 URL 변환
            if not link.startswith('http'):
                link = URL + link

            # 투자 키워드 필터링
            if any(kw in title for kw in ['투자', '유치', '시리즈']):
                articles.append({
                    'site_number': 11,
                    'site_name': '스타트업투데이',
                    'site_url': URL,
                    'article_title': title,
                    'article_url': link,
                    'published_date': datetime.now().strftime('%Y-%m-%d'),
                    'content_snippet': None
                })

    return articles
```

**예상:** 하루 3-7건

---

### 3. 아웃스탠딩 (RSS) ⭐⭐

```python
URL = 'https://outstanding.kr/feed'

def collect_outstanding():
    feed = feedparser.parse(URL)
    articles = []

    for entry in feed.entries:
        # 투자 키워드 필터링
        if any(kw in entry.title for kw in ['투자', '유치', '스타트업']):
            articles.append({
                'site_number': 13,
                'site_name': '아웃스탠딩',
                'site_url': 'https://outstanding.kr',
                'article_title': entry.title,
                'article_url': entry.link,
                'published_date': entry.published,
                'content_snippet': entry.get('summary', '')[:500]
            })

    return articles
```

**예상:** 하루 5-10건

---

### 4. 더벨 ❌ 제외

**이유:**
- 유료 사이트 (로그인 필요)
- 웹 스크래핑 불가능
- Naver 검색 API로도 제한적

**대안:**
- 제목만 Naver 검색 API로 수집 (제한적)
- 또는 완전 제외

---

### 5. 더브이씨 ❌ 제외

**이유:**
- 투자사 목록 페이지 (투자 뉴스 아님)
- 이전에 잘못된 데이터 수집됨

**결정:** 완전 제외

---

### 6. 스타트업엔 (웹 스크래핑) ⭐⭐

```python
URL = 'https://startupn.kr'
SELECTOR = 'article'

def collect_startupn():
    # 스타트업투데이와 유사한 로직
    # selector: article
    pass
```

**예상:** 하루 3-5건

---

### 7. 블로터 (웹 스크래핑) ⭐⭐

```python
URL = 'https://www.bloter.net'
SELECTOR = 'article'

def collect_bloter():
    # RSS 피드가 비어있으므로 웹 스크래핑 사용
    # selector: article
    pass
```

**예상:** 하루 3-7건

---

### 8. 이코노미스트 (웹 스크래핑) ⭐

```python
URL = 'https://www.economist.co.kr'
SELECTOR = 'h2 a'

def collect_economist():
    # selector: h2 a
    # 링크가 적을 수 있음 (2개)
    pass
```

**예상:** 하루 2-4건

---

### 9. 플래텀 (RSS) ⭐⭐⭐

```python
URL = 'https://platum.kr/feed'

def collect_platum():
    feed = feedparser.parse(URL)
    articles = []

    for entry in feed.entries:
        # 투자 키워드 필터링
        if any(kw in entry.title for kw in ['투자', '유치', '시리즈']):
            articles.append({
                'site_number': 10,
                'site_name': '플래텀',
                'site_url': 'https://platum.kr',
                'article_title': entry.title,
                'article_url': entry.link,
                'published_date': entry.published,
                'content_snippet': entry.get('summary', '')[:500]
            })

    return articles
```

**예상:** 하루 5-10건

---

### 10. AI타임스 (웹 스크래핑) ⭐⭐

```python
URL = 'https://www.aitimes.com'
SELECTOR = 'article'

def collect_aitimes():
    # selector: article
    pass
```

**예상:** 하루 3-5건

---

## 통합 수집 스크립트 구조

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 뉴스 수집 스크립트
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# RSS 수집 함수들
def collect_rss_sites():
    all_articles = []

    # 벤처스퀘어
    all_articles.extend(collect_venturesquare())

    # 아웃스탠딩
    all_articles.extend(collect_outstanding())

    # 플래텀
    all_articles.extend(collect_platum())

    return all_articles


# 웹 스크래핑 수집 함수들
def collect_web_scraping_sites():
    all_articles = []

    # 스타트업투데이
    all_articles.extend(collect_startuptoday())

    # 스타트업엔
    all_articles.extend(collect_startupn())

    # 블로터
    all_articles.extend(collect_bloter())

    # 이코노미스트
    all_articles.extend(collect_economist())

    # AI타임스
    all_articles.extend(collect_aitimes())

    return all_articles


# 메인 실행
def main():
    print("뉴스 수집 시작")

    # RSS 수집
    rss_articles = collect_rss_sites()
    print(f"RSS: {len(rss_articles)}건")

    # 웹 스크래핑 수집
    web_articles = collect_web_scraping_sites()
    print(f"Web: {len(web_articles)}건")

    # 합계
    all_articles = rss_articles + web_articles
    print(f"Total: {len(all_articles)}건")

    # 필터링 (한국 기업, 투자 뉴스)
    filtered = filter_korean_investment_news(all_articles)
    print(f"Filtered: {len(filtered)}건")

    # Supabase 저장
    save_to_supabase(filtered)

    return filtered


if __name__ == '__main__':
    main()
```

---

## 예상 수집량 (하루 기준)

| 방법 | 사이트 수 | 기사 수 | 한국 기업 (75%) |
|------|----------|---------|----------------|
| RSS | 3개 | 30-50건 | 22-37건 |
| 웹 스크래핑 | 5개 | 20-40건 | 15-30건 |
| **합계** | **8개** | **50-90건** | **37-67건** |

**최종 목표:** 하루 **40-70건** 한국 기업 투자 뉴스

---

## 구현 일정

| Phase | 작업 | 예상 시간 |
|-------|------|----------|
| Phase 1 | RSS 3개 구현 | 2시간 |
| Phase 2 | 웹 스크래핑 5개 구현 | 4시간 |
| Phase 3 | 통합 & 테스트 | 2시간 |
| **총합** | | **8시간** |

---

## 다음 단계

### 1. Phase 1 구현 (RSS 3개)
```bash
python collect_rss_news.py
```

### 2. Phase 2 구현 (웹 스크래핑 5개)
```bash
python collect_web_news.py
```

### 3. 통합 실행
```bash
python collect_all_news.py
```

---

## 주의사항

### Rate Limiting
```python
import time

# 각 사이트 수집 후 1초 대기
time.sleep(1)
```

### 에러 핸들링
```python
try:
    articles = collect_site()
except Exception as e:
    print(f"Error: {e}")
    articles = []
```

### 중복 제거
```python
# URL 기준 중복 제거
seen_urls = set()
unique_articles = []

for article in all_articles:
    if article['article_url'] not in seen_urls:
        seen_urls.add(article['article_url'])
        unique_articles.append(article)
```

---

## 요약

✅ **수집 가능:** 8개 사이트
- RSS: 3개 (벤처스퀘어, 아웃스탠딩, 플래텀)
- 웹 스크래핑: 5개 (스타트업투데이, 스타트업엔, 블로터, 이코노미스트, AI타임스)

❌ **제외:** 2개 사이트
- 더벨 (유료)
- 더브이씨 (투자사 목록)

🎯 **목표:** 하루 40-70건 한국 기업 투자 뉴스 수집
