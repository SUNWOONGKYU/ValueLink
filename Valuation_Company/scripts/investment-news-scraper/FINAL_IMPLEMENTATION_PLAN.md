# 최종 구현 계획 - 투자 뉴스 수집 시스템

> 비석세스 추가 + 더브이씨 투자사 DB 활용

---

## 1. 최종 Top 10 구성

| # | 사이트 | 용도 | 수집 방법 | 상태 | 예상 수집량 |
|---|--------|------|----------|------|-------------|
| 1 | **벤처스퀘어** | 투자 뉴스 | RSS | ✅ | 10-20건/일 |
| 2 | **스타트업투데이** | 투자 뉴스 | 웹 스크래핑 | ✅ | 3-7건/일 |
| 3 | **아웃스탠딩** | 투자 뉴스 | RSS | ✅ | 5-10건/일 |
| 4 | **비석세스** 🆕 | **투자 뉴스** | **RSS** | ✅ | **5-10건/일** |
| 5 | **더브이씨** 🔄 | **투자사 DB** | **별도 크롤링** | ✅ | **100+ VC** |
| 6 | **스타트업엔** | 투자 뉴스 | 웹 스크래핑 | ✅ | 3-5건/일 |
| 7 | **블로터** | 투자 뉴스 | 웹 스크래핑 | ✅ | 3-7건/일 |
| 8 | **이코노미스트** | 투자 뉴스 | 웹 스크래핑 | ✅ | 2-4건/일 |
| 9 | **플래텀** | 투자 뉴스 | RSS | ✅ | 5-10건/일 |
| 10 | **AI타임스** | 투자 뉴스 | 웹 스크래핑 | ✅ | 3-5건/일 |

**변경 사항:**
- ❌ 더벨 제외 (유료 사이트)
- ➕ 비석세스 추가 (RSS + 투자 키워드 41개!)
- 🔄 더브이씨 용도 변경 (투자 뉴스 → 투자사 DB)

**예상 결과:**
- 📰 **투자 뉴스:** 하루 40-75건 (9개 사이트)
- 🏢 **투자사 DB:** 100+ 투자사 프로필

---

## 2. 구현 단계

### Phase 1: RSS 수집 (4개 사이트) ⭐⭐⭐

**우선순위: 최우선**

| # | 사이트 | RSS URL | 예상 |
|---|--------|---------|------|
| 1 | 벤처스퀘어 | `https://www.venturesquare.net/feed` | 10-20건 |
| 2 | 아웃스탠딩 | `https://outstanding.kr/feed` | 5-10건 |
| 3 | 플래텀 | `https://platum.kr/feed` | 5-10건 |
| 4 | **비석세스** 🆕 | `https://besuccess.com/feed` | **5-10건** |

**목표:** 하루 25-50건 수집
**구현 시간:** 2-3시간

---

### Phase 2: 웹 스크래핑 (5개 사이트) ⭐⭐

**우선순위: 중요**

| # | 사이트 | 선택자 | 예상 |
|---|--------|--------|------|
| 1 | 스타트업투데이 | `article` | 3-7건 |
| 2 | 스타트업엔 | `article` | 3-5건 |
| 3 | 블로터 | `article` | 3-7건 |
| 4 | 이코노미스트 | `h2 a` | 2-4건 |
| 5 | AI타임스 | `article` | 3-5건 |

**목표:** 하루 15-25건 수집
**구현 시간:** 4-5시간

---

### Phase 3: 투자사 DB 구축 (더브이씨) ⭐

**우선순위: 보조**

**목표:**
- 100+ 투자사 프로필 수집
- Deal 테이블 investors 필드 검증
- 투자사별 포트폴리오 분석

**구현 시간:** 2주 (백그라운드)

---

## 3. 비석세스 상세 정보

### 사이트 정보

**URL:** https://besuccess.com
**RSS:** https://besuccess.com/feed

**특징:**
- ✅ 한국 스타트업 생태계 뉴스
- ✅ 영문 기사 포함 (글로벌 뉴스)
- ✅ 투자 키워드 **41개** (가장 많음!)
- ✅ RSS 피드 20개 엔트리

### 수집 코드

```python
def collect_besuccess():
    """비석세스 RSS 수집"""

    URL = 'https://besuccess.com/feed'

    feed = feedparser.parse(URL)
    articles = []

    for entry in feed.entries:
        # 투자 키워드 필터링
        title = entry.title

        if any(kw in title for kw in ['투자', '유치', 'funding', 'investment', 'series']):
            articles.append({
                'site_number': 14,  # 새 번호
                'site_name': '비석세스',
                'site_url': 'https://besuccess.com',
                'article_title': title,
                'article_url': entry.link,
                'published_date': entry.published,
                'content_snippet': entry.get('summary', '')[:500]
            })

    return articles
```

### 예상 결과

```
[비석세스]
- "AI 스타트업 XYZ, 100억원 시리즈A 투자 유치"
- "Korean Startup ABC Raises $10M Series B"
- "핀테크 기업 DEF, 알토스벤처스로부터 투자"
...
```

---

## 4. 통합 수집 프로세스

### 전체 흐름도

```
┌──────────────────────────────────────────────────────────┐
│  STEP 1: 뉴스 수집 (9개 사이트)                           │
│  ├─ RSS 피드 (4개): 벤처스퀘어, 아웃스탠딩, 플래텀,       │
│  │                   비석세스                             │
│  └─ 웹 스크래핑 (5개): 스타트업투데이, 스타트업엔,        │
│                        블로터, 이코노미스트, AI타임스      │
│  → 하루 40-75건 수집                                      │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 2: 키워드 필터링                                    │
│  ├─ 포함: 투자, 유치, 시리즈, 펀딩                        │
│  ├─ 제외: IR, M&A, 행사, 인사                            │
│  └─ 중복 URL 제거                                        │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 3: investment_news_articles 저장                   │
│  (모든 기사 일단 저장)                                    │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 4: Gemini - 한국 기업 판단                          │
│  → YES: 다음 단계                                        │
│  → NO: 제외                                              │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 5: Gemini - Deal 정보 추출                          │
│  회사명, 투자금액, 투자자, 업종, 단계 등                   │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 6: 투자사 검증 (TheVC DB) 🆕                        │
│  "알토스" → "알토스벤처스" (정식 명칭)                     │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  STEP 7: deals 테이블 저장                                │
│  (한국 기업 투자 뉴스만 + 검증된 투자사명)                 │
└──────────────────────────────────────────────────────────┘
```

---

## 5. 데이터베이스 구조

### 기존 테이블

**investment_news_articles** (모든 기사)
```sql
- id
- site_number
- site_name
- site_url
- article_title
- article_url
- published_date
- content_snippet
```

**deals** (한국 기업 투자 뉴스)
```sql
- id
- company_name
- ceo
- industry
- stage
- investors
- amount
- location
- news_title
- news_url
- news_date
- site_name
```

### 새 테이블 (투자사 DB) 🆕

**investors**
```sql
CREATE TABLE investors (
  id SERIAL PRIMARY KEY,
  vc_name TEXT UNIQUE NOT NULL,
  vc_name_en TEXT,
  website TEXT,
  contact_email TEXT,
  focus_industries TEXT[],
  investment_stage TEXT[],
  total_investments INTEGER DEFAULT 0,
  thevc_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**deal_investors** (관계 테이블)
```sql
CREATE TABLE deal_investors (
  deal_id INTEGER REFERENCES deals(id),
  investor_id INTEGER REFERENCES investors(id),
  PRIMARY KEY (deal_id, investor_id)
);
```

---

## 6. 구현 코드 구조

### 메인 스크립트: `collect_all_news.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 뉴스 수집 스크립트
- RSS 4개 사이트
- 웹 스크래핑 5개 사이트
- TheVC 투자사 DB 연동
"""

def main():
    print("=" * 60)
    print("투자 뉴스 수집 시작")
    print("=" * 60)

    # Phase 1: RSS 수집
    rss_articles = []
    rss_articles.extend(collect_venturesquare())
    rss_articles.extend(collect_outstanding())
    rss_articles.extend(collect_platum())
    rss_articles.extend(collect_besuccess())  # 🆕 비석세스 추가

    print(f"\n[RSS] {len(rss_articles)}건 수집")

    # Phase 2: 웹 스크래핑
    web_articles = []
    web_articles.extend(collect_startuptoday())
    web_articles.extend(collect_startupn())
    web_articles.extend(collect_bloter())
    web_articles.extend(collect_economist())
    web_articles.extend(collect_aitimes())

    print(f"[WEB] {len(web_articles)}건 수집")

    # 합계
    all_articles = rss_articles + web_articles
    print(f"[TOTAL] {len(all_articles)}건")

    # 키워드 필터링
    filtered = filter_investment_news(all_articles)
    print(f"[FILTERED] {len(filtered)}건")

    # Supabase 저장
    save_to_supabase(filtered)

    # Phase 3: Deal 정보 추출 및 투자사 검증
    extract_deals_with_vc_validation()

    print("\n완료!")


if __name__ == '__main__':
    main()
```

---

## 7. 구현 일정

### Week 1: 핵심 기능 구현

**Day 1-2: RSS 수집 (4개)**
- [x] 벤처스퀘어
- [x] 아웃스탠딩
- [x] 플래텀
- [ ] 비석세스 🆕

**Day 3-5: 웹 스크래핑 (5개)**
- [ ] 스타트업투데이
- [ ] 스타트업엔
- [ ] 블로터
- [ ] 이코노미스트
- [ ] AI타임스

**Day 6-7: 통합 및 테스트**
- [ ] 통합 스크립트 작성
- [ ] 중복 제거
- [ ] Supabase 저장 테스트

---

### Week 2: 투자사 DB 구축

**Day 1-3: 기본 DB**
- [ ] TheVC.kr 투자사 목록 수집
- [ ] investors 테이블 생성
- [ ] 주요 투자사 100개 저장

**Day 4-5: Deal 연동**
- [ ] 투자사 검증 로직 추가
- [ ] deal_investors 테이블 연동

**Day 6-7: 테스트 및 검증**
- [ ] 전체 프로세스 테스트
- [ ] 데이터 품질 검증

---

## 8. 예상 성과

### 투자 뉴스 수집

**하루 기준:**
- RSS (4개): 25-50건
- 웹 (5개): 15-25건
- **합계: 40-75건**
- 한국 기업 (75%): **30-55건**

**월간 기준:**
- 전체: 1,200-2,250건
- 한국 기업: **900-1,650건**

### 투자사 DB

- 투자사 프로필: **100+ VC**
- 투자사명 정규화: **100%**
- 투자자 데이터 품질: **대폭 향상**

---

## 9. 다음 단계

### 즉시 실행 (오늘)

**A. 비석세스 RSS 수집 구현**
```bash
python collect_besuccess.py
```

**B. Supabase 테이블 업데이트**
```sql
-- investment_news_ranking에 비석세스 추가
INSERT INTO investment_news_ranking (rank, site_number, site_name, site_url)
VALUES (4, 14, '비석세스', 'https://besuccess.com');

-- 더벨 랭킹 제거 또는 비활성화
DELETE FROM investment_news_ranking WHERE site_name = '더벨';
```

**C. 투자사 테이블 생성**
```sql
-- investors 테이블 생성
CREATE TABLE investors (...);

-- deal_investors 테이블 생성
CREATE TABLE deal_investors (...);
```

### 단기 (1주일)

**D. 전체 통합 수집 스크립트 완성**
**E. 자동 스케줄링 설정 (GitHub Actions)**
**F. 모니터링 및 로깅**

---

## 10. 기대 효과

### Before (현재)

```
❌ 27개 기사만 수집
❌ 대부분 일본/외국 기업
❌ 투자사명 불통일 ("알토스", "알토스벤처스")
❌ 1월 19일 데이터로 멈춤
```

### After (구현 후)

```
✅ 하루 30-55건 한국 기업 투자 뉴스
✅ 9개 사이트 자동 수집
✅ 투자사명 정규화 (100+ VC DB)
✅ 매일 자동 업데이트
✅ Deal 페이지 실시간 갱신
```

---

## 요약

**핵심 변경:**
1. ➕ **비석세스 추가** (RSS, 투자 키워드 41개)
2. ❌ **더벨 제외** (유료 사이트)
3. 🔄 **더브이씨 활용** (투자사 DB 구축)

**목표:**
- 📰 하루 **30-55건** 한국 기업 투자 뉴스
- 🏢 **100+ 투자사** 프로필 DB
- 📊 투자자 데이터 **품질 향상**

**일정:** 2주 완성
