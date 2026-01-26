# 투자 뉴스 수집 기획서

> Top 10 뉴스 제공기관별 수집 방법 설계

---

## 1. 현재 문제점 분석

### 기존 방식의 문제
- ❌ **scrape_daily.py**: Gemini에게 "뉴스 수집해줘" 요청 → 실제 크롤링 불가
- ❌ **더브이씨(thevc.kr)**: 투자사 목록 페이지를 크롤링함
- ❌ **데이터 부족**: 27개 기사만 수집됨
- ❌ **필터링 부족**: 일본 기업, 외국 기업, 투자사가 섞임

---

## 2. Top 10 사이트별 수집 방법

| # | 사이트 | URL | 수집 방법 | 우선순위 |
|---|--------|-----|----------|---------|
| 1 | 벤처스퀘어 | venturesquare.net | RSS 피드 | ⭐⭐⭐ 최우선 |
| 2 | 스타트업투데이 | startuptoday.kr | 웹 스크래핑 | ⭐⭐⭐ |
| 3 | 아웃스탠딩 | outstanding.kr | 웹 스크래핑 | ⭐⭐ |
| 4 | 더벨 | thebell.co.kr | 웹 스크래핑 (유료) | ⭐ |
| 5 | 더브이씨 | thevc.kr | ❌ 제외 (투자사 목록) | - |
| 6 | 스타트업엔 | startupn.kr | 웹 스크래핑 | ⭐⭐ |
| 7 | 블로터 | bloter.net | RSS 피드 | ⭐⭐⭐ |
| 8 | 이코노미스트 | economist.co.kr | 웹 스크래핑 | ⭐ |
| 9 | 플래텀 | platum.kr | RSS 피드 | ⭐⭐⭐ |
| 10 | AI타임스 | aitimes.com | 웹 스크래핑 | ⭐⭐ |

---

## 3. 수집 방법별 상세 설계

### 방법 A: RSS 피드 (권장) ⭐⭐⭐

**장점:**
- ✅ 공식 제공 방식 (안정적)
- ✅ 최신 기사 자동 업데이트
- ✅ 구조화된 데이터 (제목, URL, 날짜, 요약)
- ✅ 빠른 수집 속도

**단점:**
- ⚠️ 일부 사이트만 제공

**구현:**
```python
import feedparser

def scrape_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        articles.append({
            'title': entry.title,
            'url': entry.link,
            'published': entry.published,
            'summary': entry.summary
        })

    return articles
```

**지원 사이트:**
- 벤처스퀘어: `https://www.venturesquare.net/feed`
- 플래텀: `https://platum.kr/feed`
- 블로터: `https://www.bloter.net/feed`

---

### 방법 B: 웹 스크래핑 (BeautifulSoup) ⭐⭐

**장점:**
- ✅ RSS 없는 사이트도 수집 가능
- ✅ 상세 정보 추출 가능

**단점:**
- ⚠️ HTML 구조 변경 시 수정 필요
- ⚠️ 속도 느림
- ⚠️ 서버 부하 (Rate limiting 필요)

**구현:**
```python
import requests
from bs4 import BeautifulSoup

def scrape_website(url, selector):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.select(selector):
        title = item.select_one('.title').text
        link = item.select_one('a')['href']
        articles.append({'title': title, 'url': link})

    return articles
```

**적용 사이트:**
- 스타트업투데이
- 아웃스탠딩
- 스타트업엔
- AI타임스

---

### 방법 C: 검색 API (보조) ⭐

**장점:**
- ✅ 키워드 필터링 가능
- ✅ 날짜 범위 지정 가능

**단점:**
- ⚠️ API 키 필요
- ⚠️ 일일 제한

**구현:**
```python
# Naver 검색 API
def search_naver(query, site):
    url = "https://openapi.naver.com/v1/search/news.json"
    params = {
        'query': f'site:{site} {query}',
        'display': 10
    }
    # ...
```

**적용:**
- 더벨 (유료 사이트)
- 이코노미스트

---

## 4. 사이트별 상세 크롤링 전략

### 1. 벤처스퀘어 (venturesquare.net) ⭐⭐⭐

**방법:** RSS 피드
```
RSS URL: https://www.venturesquare.net/feed
카테고리: 투자 뉴스 필터링 필요
```

**필터링:**
- 제목에 "투자", "유치", "시리즈" 포함
- 한국 기업명 포함

**예상 수집량:** 하루 5-10건

---

### 2. 스타트업투데이 (startuptoday.kr) ⭐⭐⭐

**방법:** 웹 스크래핑
```
URL: https://startuptoday.kr/news/articleList.html?view_type=sm
Selector: .article-list-item
```

**필터링:**
- 카테고리: "투자/IR"
- 제목 키워드 필터

**예상 수집량:** 하루 3-7건

---

### 3. 아웃스탠딩 (outstanding.kr) ⭐⭐

**방법:** 웹 스크래핑
```
URL: https://outstanding.kr/category/investment
Selector: .post-item
```

**특징:**
- 유료 멤버십 콘텐츠 있음
- 무료 기사만 수집

**예상 수집량:** 하루 2-5건

---

### 4. 더벨 (thebell.co.kr) ⭐

**방법:** Naver 검색 API (보조)
```
이유: 유료 사이트
대안: 제목만 수집 또는 제외
```

**예상 수집량:** 하루 1-3건 (제한적)

---

### 5. 더브이씨 (thevc.kr) ❌

**방법:** 제외
```
이유: 투자사 목록 페이지, 투자 뉴스 아님
```

---

### 6. 스타트업엔 (startupn.kr) ⭐⭐

**방법:** 웹 스크래핑
```
URL: https://startupn.kr/news
Selector: .news-item
```

**예상 수집량:** 하루 3-5건

---

### 7. 블로터 (bloter.net) ⭐⭐⭐

**방법:** RSS 피드
```
RSS URL: https://www.bloter.net/feed
카테고리: 스타트업
```

**예상 수집량:** 하루 3-7건

---

### 8. 이코노미스트 (economist.co.kr) ⭐

**방법:** 웹 스크래핑
```
URL: https://economist.co.kr/economy/startup
Selector: .article-list
```

**예상 수집량:** 하루 2-4건

---

### 9. 플래텀 (platum.kr) ⭐⭐⭐

**방법:** RSS 피드
```
RSS URL: https://platum.kr/feed
카테고리: 투자 뉴스
```

**예상 수집량:** 하루 5-10건

---

### 10. AI타임스 (aitimes.com) ⭐⭐

**방법:** 웹 스크래핑
```
URL: https://www.aitimes.com/news/articleList.html?sc_section_code=S1N12
Selector: .article-list
```

**예상 수집량:** 하루 3-5건

---

## 5. 필터링 전략 (3단계)

### 1단계: 사전 필터링 (수집 시)

**제목 키워드 필터:**
```python
INCLUDE_KEYWORDS = [
    '투자', '유치', '펀딩', '시리즈', 'VC',
    '억원', '조달', '라운드', '벤처캐피탈'
]

EXCLUDE_KEYWORDS = [
    'IR', 'M&A', '대표', '인사', '행사',
    '세미나', '컨퍼런스', '채용'
]
```

**사이트별 제외:**
- 더브이씨: 전체 제외
- 더벨: 유료 기사 제외

---

### 2단계: 한국 기업 필터링 (Gemini)

**프롬프트:**
```
제목: "{title}"

질문: 이 기사가 한국 기업의 투자 유치 뉴스인가?

조건:
1. 한국 기업이어야 함 (일본, 미국, 글로벌 기업 제외)
2. 실제 투자를 받은 스타트업이어야 함
3. 투자사 목록이 아니어야 함

YES/NO로 답변:
```

---

### 3단계: Deal 정보 추출 (Gemini)

**통과한 기사만 상세 추출:**
```
- company_name (한국 기업명)
- ceo (대표자)
- industry (업종)
- stage (투자 단계)
- investors (투자자)
- amount (투자 금액)
- location (본사 위치)
```

---

## 6. 수집 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: 사이트별 뉴스 수집                                   │
│  ├─ RSS 피드 (벤처스퀘어, 플래텀, 블로터)                     │
│  ├─ 웹 스크래핑 (스타트업투데이, 아웃스탠딩 등)               │
│  └─ 검색 API (더벨, 이코노미스트)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: 1단계 필터링 (키워드)                               │
│  ├─ 투자 키워드 포함 확인                                    │
│  ├─ 제외 키워드 체크                                         │
│  └─ 중복 URL 제거                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: investment_news_articles 테이블 저장                │
│  (모든 기사 일단 저장)                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: 2단계 필터링 (Gemini - 한국 기업 여부)              │
│  → YES 기사만 다음 단계로                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Deal 정보 추출 (Gemini)                             │
│  → 회사명, 투자금액, 투자자 등 추출                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: deals 테이블 저장                                   │
│  (한국 기업 투자 뉴스만)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 예상 수집량 (하루 기준)

| 사이트 | 예상 수집량 | 한국 기업 비율 | 최종 Deal |
|--------|------------|---------------|----------|
| 벤처스퀘어 | 5-10건 | 80% | 4-8건 |
| 스타트업투데이 | 3-7건 | 80% | 2-5건 |
| 아웃스탠딩 | 2-5건 | 70% | 1-3건 |
| 더벨 | 1-3건 | 60% | 1-2건 |
| 더브이씨 | 제외 | - | - |
| 스타트업엔 | 3-5건 | 80% | 2-4건 |
| 블로터 | 3-7건 | 70% | 2-5건 |
| 이코노미스트 | 2-4건 | 60% | 1-2건 |
| 플래텀 | 5-10건 | 80% | 4-8건 |
| AI타임스 | 3-5건 | 80% | 2-4건 |
| **합계** | **27-56건** | **75%** | **20-42건** |

---

## 8. 구현 우선순위

### Phase 1: RSS 피드 (1주일) ⭐⭐⭐
- 벤처스퀘어
- 플래텀
- 블로터
- **목표:** 하루 10-20건 수집

### Phase 2: 웹 스크래핑 (2주일) ⭐⭐
- 스타트업투데이
- 아웃스탠딩
- 스타트업엔
- AI타임스
- **목표:** 하루 15-30건 추가

### Phase 3: 보조 수단 (3주일) ⭐
- Naver 검색 API (더벨, 이코노미스트)
- **목표:** 하루 5-10건 추가

---

## 9. 기술 스택

| 구분 | 라이브러리 | 용도 |
|------|-----------|------|
| RSS 파싱 | `feedparser` | RSS 피드 읽기 |
| 웹 스크래핑 | `BeautifulSoup4`, `requests` | HTML 파싱 |
| AI 필터링 | `google-generativeai` | 한국 기업 판단, 정보 추출 |
| DB 저장 | `supabase-py` | Supabase 연동 |
| 스케줄링 | GitHub Actions | 매일 자동 실행 |

---

## 10. 에러 핸들링

### 사이트 접속 실패
```python
try:
    response = requests.get(url, timeout=10)
except:
    # 다음 사이트로
    continue
```

### Rate Limiting
```python
import time
time.sleep(1)  # 1초 대기
```

### Gemini API 할당량 초과
```python
# 하루 1500건 제한
# 배치 처리로 분산
```

---

## 11. 모니터링

### 수집 로그
```
[2026-01-26 08:00]
- 벤처스퀘어: 7건 수집, 5건 Deal 저장
- 플래텀: 8건 수집, 6건 Deal 저장
- 합계: 15건 수집, 11건 Deal 저장
```

### Slack 알림
```
- 수집 성공 시: 건수 알림
- 실패 시: 에러 알림
- 0건 수집 시: 경고 알림
```

---

## 12. 차후 개선 방향

1. **실시간 수집**: RSS 피드 실시간 모니터링
2. **키워드 알림**: 특정 기업 투자 시 즉시 알림
3. **트렌드 분석**: 업종별/단계별 투자 트렌드
4. **투자자 네트워크**: 투자자 간 관계 분석
5. **이메일 뉴스레터**: 구독자에게 일일 요약 발송

---

## 요약

**핵심 전략:**
1. ✅ RSS 피드 우선 (벤처스퀘어, 플래텀, 블로터)
2. ✅ 웹 스크래핑 보조 (스타트업투데이 등)
3. ✅ 3단계 필터링 (키워드 → 한국 기업 → Deal 추출)
4. ✅ 더브이씨 제외 (투자사 목록)
5. ✅ 하루 20-42건 한국 기업 투자 뉴스 수집 목표
