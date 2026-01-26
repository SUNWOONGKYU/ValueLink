# Investment News Network 데이터베이스 구조

> 전체 시스템의 데이터 흐름과 테이블 관계

---

## 📊 테이블 구조 개요

```
┌─────────────────────────────────────────────────────────────┐
│  5개 메인 테이블 + 3개 View                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. investment_news_network_sources (11개 소스 관리)         │
│  2. investment_news_articles (모든 수집 기사)                │
│  3. deals (선정된 투자 뉴스)                                 │
│  4. email_subscribers (구독자)                              │
│  5. email_send_log (발송 기록)                              │
│                                                             │
│  View:                                                      │
│  - recent_investment_news (최근 뉴스)                        │
│  - daily_collection_stats (일일 통계)                        │
│  - weekly_insight (주간 인사이트)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. investment_news_network_sources

**용도:** 11개 뉴스 소스 관리

| 필드 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 기본키 |
| rank | INTEGER | 순위 (1-11) |
| category | TEXT | 'RSS', 'Web Scraping', 'VC Database' |
| source_number | INTEGER | 고유 번호 (9, 10, 11, ...) |
| source_name | TEXT | 소스명 (벤처스퀘어, ...) |
| source_url | TEXT | URL |
| collection_method | TEXT | 'RSS' 또는 'Web Scraping' |
| rss_url | TEXT | RSS 피드 URL (있는 경우) |
| selector | TEXT | CSS 선택자 (웹 스크래핑 시) |
| is_active | BOOLEAN | 활성화 여부 |
| expected_daily_count | INTEGER | 예상 일일 수집량 |
| last_collected_at | TIMESTAMPTZ | 마지막 수집 시간 |

**초기 데이터:**

```
Category 1: RSS Sources (4개)
1. 벤처스퀘어 (rank=1, source_number=9)
2. 아웃스탠딩 (rank=2, source_number=13)
3. 플래텀 (rank=3, source_number=10)
4. 비석세스 (rank=4, source_number=14)

Category 2: Web Scraping Sources (6개)
5. 스타트업투데이 (rank=5, source_number=11)
6. 스타트업엔 (rank=6, source_number=12)
7. 블로터 (rank=7, source_number=22)
8. 이코노미스트 (rank=8, source_number=23)
9. AI타임스 (rank=9, source_number=19)
10. 넥스트유니콘 (rank=10, source_number=21)

Category 3: VC Database (1개)
11. 더브이씨 (rank=11, source_number=8)
```

---

## 2. investment_news_articles

**용도:** 수집된 모든 기사 저장 (중복 제거 안 함)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 기본키 |
| source_number | INTEGER | 소스 번호 (FK) |
| source_name | TEXT | 소스명 |
| source_url | TEXT | 소스 URL |
| article_title | TEXT | 기사 제목 |
| article_url | TEXT | 기사 URL (UNIQUE) |
| published_date | TIMESTAMPTZ | 발행일 |
| content_snippet | TEXT | 기사 요약 |

**점수 관련 필드 (11점 만점):**

| 필드 | 타입 | 점수 | 설명 |
|------|------|------|------|
| score | INTEGER | 0-11 | 총 점수 |
| has_amount | BOOLEAN | 3점 | 투자금액 유무 |
| has_investors | BOOLEAN | 3점 | 투자자 유무 |
| has_stage | BOOLEAN | 2점 | 투자단계 유무 |
| has_industry | BOOLEAN | 1점 | 업종 유무 |
| has_location | BOOLEAN | 1점 | 지역 유무 |
| has_employees | BOOLEAN | 1점 | 직원수 유무 |

**상태 필드:**

| 필드 | 타입 | 설명 |
|------|------|------|
| is_korean_company | BOOLEAN | 한국 기업 여부 |
| is_selected | BOOLEAN | Deal 테이블 선정 여부 |
| selected_at | TIMESTAMPTZ | 선정 시간 |

**데이터 흐름:**

```
RSS/웹 스크래핑
    ↓
일단 모두 저장 (article_url 기준 중복 체크)
    ↓
점수 계산 (Gemini)
    ↓
같은 기업 기사끼리 비교
    ↓
최고 점수 기사만 is_selected = true
    ↓
deals 테이블로 이동
```

---

## 3. deals

**용도:** 기업별 최고 점수 기사만 선정

| 필드 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 기본키 |

**기사 정보:**

| 필드 | 타입 | 설명 |
|------|------|------|
| article_id | INTEGER | investment_news_articles.id (FK) |
| news_title | TEXT | 기사 제목 |
| news_url | TEXT | 기사 URL |
| news_date | TIMESTAMPTZ | 기사 발행일 |
| site_name | TEXT | 출처 |
| article_score | INTEGER | 기사 점수 (11점 만점) |

**회사 정보 (Gemini + TheVC + Naver):**

| 필드 | 타입 | 데이터 출처 |
|------|------|-----------|
| company_name | TEXT | Gemini (필수) |
| ceo | TEXT | Gemini → TheVC → Naver |
| founded | DATE | Gemini → TheVC → Naver |
| industry | TEXT | Gemini → TheVC |
| location | TEXT | Gemini → TheVC → Naver |
| employees | INTEGER | Gemini → Naver |
| description | TEXT | TheVC |

**투자 정보 (Gemini):**

| 필드 | 타입 | 설명 |
|------|------|------|
| investors | TEXT | 투자자 (TheVC로 정식명칭 검증) |
| amount | TEXT | 투자금액 |
| stage | TEXT | 투자단계 |

**데이터 출처 추적:**

| 필드 | 타입 | 설명 |
|------|------|------|
| gemini_extracted | BOOLEAN | Gemini로 추출 |
| thevc_enriched | BOOLEAN | TheVC로 보강 |
| naver_enriched | BOOLEAN | Naver API로 보강 |

---

## 4. email_subscribers

**용도:** 이메일 구독자 관리

| 필드 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 기본키 |
| email | TEXT | 이메일 주소 (UNIQUE) |
| name | TEXT | 이름 (선택) |

**구독 설정:**

| 필드 | 타입 | 설명 |
|------|------|------|
| daily_news | BOOLEAN | 일일 뉴스 (월-토 9am) |
| weekly_insight | BOOLEAN | 주간 인사이트 (일 10am) |

**상태:**

| 필드 | 타입 | 설명 |
|------|------|------|
| is_active | BOOLEAN | 구독 활성화 |
| email_verified | BOOLEAN | 이메일 인증 |
| verification_token | TEXT | 인증 토큰 |
| subscribed_at | TIMESTAMPTZ | 구독 시작 |
| unsubscribed_at | TIMESTAMPTZ | 구독 해지 |
| last_sent_at | TIMESTAMPTZ | 마지막 발송 |

---

## 5. email_send_log

**용도:** 이메일 발송 기록

| 필드 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 기본키 |
| subscriber_id | INTEGER | 구독자 ID (FK) |
| email_type | TEXT | 'daily' 또는 'weekly' |
| subject | TEXT | 이메일 제목 |

**발송 정보:**

| 필드 | 타입 | 설명 |
|------|------|------|
| sent_at | TIMESTAMPTZ | 발송 시간 |
| status | TEXT | 'sent', 'failed', 'bounced' |
| error_message | TEXT | 에러 메시지 (실패 시) |

**내용 정보:**

| 필드 | 타입 | 설명 |
|------|------|------|
| deals_count | INTEGER | 포함된 Deal 개수 |
| deals_ids | INTEGER[] | Deal ID 배열 |

---

## 데이터 흐름 전체도

```
┌─────────────────────────────────────────────────────────────┐
│  매일 오전 8시: 뉴스 수집                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RSS (4개) + 웹 스크래핑 (6개)                               │
│      ↓                                                      │
│  investment_news_articles 테이블 (모든 기사 저장)            │
│      ↓                                                      │
│  Gemini: 점수 계산 (11점)                                    │
│      ↓                                                      │
│  기업별 최고 점수 선정                                        │
│      ↓                                                      │
│  Gemini: Deal 정보 추출                                      │
│      ↓                                                      │
│  TheVC: 회사/투자자 정보 보강 ⭐                             │
│      ↓                                                      │
│  Naver API: 부족한 정보 추가 검색                            │
│      ↓                                                      │
│  deals 테이블 (최종 저장)                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  매일 오전 9시 (월-토): 일일 이메일 발송                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  email_subscribers (daily_news = true)                      │
│      ↓                                                      │
│  어제 deals (WHERE news_date = YESTERDAY)                   │
│      ↓                                                      │
│  이메일 발송                                                 │
│      ↓                                                      │
│  email_send_log 기록                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  일요일 오전 10시: 주간 인사이트 리포트                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  email_subscribers (weekly_insight = true)                  │
│      ↓                                                      │
│  지난 주 deals + weekly_insight View                        │
│      ↓                                                      │
│  통계 분석 (총 투자 건수, 단계별, 업종별)                     │
│      ↓                                                      │
│  이메일 발송                                                 │
│      ↓                                                      │
│  email_send_log 기록                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## View 설명

### 1. recent_investment_news

**용도:** Deal 페이지에서 최근 100건 표시

```sql
SELECT * FROM recent_investment_news LIMIT 10;
```

### 2. daily_collection_stats

**용도:** 소스별 일일 수집 통계

```sql
SELECT * FROM daily_collection_stats
WHERE collection_date = CURRENT_DATE;
```

### 3. weekly_insight

**용도:** 주간 인사이트 리포트 데이터

```sql
SELECT * FROM weekly_insight
WHERE week_start = DATE_TRUNC('week', CURRENT_DATE - INTERVAL '7 days');
```

---

## 유용한 쿼리 모음

### 오늘 수집된 기사 수

```sql
SELECT source_name, COUNT(*)
FROM investment_news_articles
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY source_name;
```

### 기업별 최신 투자 뉴스

```sql
SELECT company_name, news_date, amount, stage, investors
FROM deals
ORDER BY news_date DESC
LIMIT 10;
```

### 투자 단계별 통계

```sql
SELECT stage, COUNT(*) as count, AVG(article_score) as avg_score
FROM deals
GROUP BY stage
ORDER BY count DESC;
```

### 소스별 선정률

```sql
SELECT
    a.source_name,
    COUNT(*) as total_articles,
    SUM(CASE WHEN a.is_selected THEN 1 ELSE 0 END) as selected,
    ROUND(100.0 * SUM(CASE WHEN a.is_selected THEN 1 ELSE 0 END) / COUNT(*), 2) as selection_rate
FROM investment_news_articles a
GROUP BY a.source_name
ORDER BY selection_rate DESC;
```

### 활성 구독자 수

```sql
SELECT
    SUM(CASE WHEN daily_news THEN 1 ELSE 0 END) as daily_subscribers,
    SUM(CASE WHEN weekly_insight THEN 1 ELSE 0 END) as weekly_subscribers
FROM email_subscribers
WHERE is_active = true;
```

---

## 데이터 보강 우선순위

```
회사 정보:
1. Gemini 추출 (기사에서)
2. TheVC 조회 (더 정확한 정보)
3. Naver API (보충)

투자자 정보:
1. Gemini 추출 (기사에서)
2. TheVC 검증 (정식 명칭 확인)
```

**예시:**

```
기사: "AI 스타트업 테크이노, 알토스로부터 투자"

Step 1 (Gemini):
- company_name: 테크이노
- investors: 알토스
- ceo: ? (없음)
- founded: ? (없음)

Step 2 (TheVC):
- ceo: 김철수
- founded: 2020-03-15
- location: 판교
- industry: AI, 헬스케어
- investors: 알토스 → 알토스벤처스 (정식명칭)

Step 3 (Naver - 필요 시):
- employees: 50명
```

---

## 스키마 파일

**SQL 파일:** `scripts/investment-news-scraper/DATABASE_SCHEMA.sql`

**실행 방법:**

```bash
# Supabase SQL Editor에서 실행
# 또는
psql -h [host] -U [user] -d [database] -f DATABASE_SCHEMA.sql
```
