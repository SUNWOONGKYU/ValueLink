# 투자 뉴스 스크래핑 및 랭킹 시스템 프로젝트 계획서

**작성일**: 2026-01-25
**프로젝트명**: 국내 투자유치 뉴스 사이트 랭킹 시스템

---

## 📋 프로젝트 개요

### 목적
국내 주요 투자유치 관련 뉴스 사이트 19개의 뉴스 게재 건수를 파악하고, 게재 건수에 따라 1위부터 19위까지 랭킹을 매깁니다.

### 기간
**2026년 1월 1일 ~ 2026년 1월 25일** (오늘)

### 대상 사이트 (19개)
| 번호 | 사이트 URL | 사이트명 |
|------|-----------|----------|
| 8 | thevc.kr | 더브이씨 |
| 9 | www.venturesquare.net | 벤처스퀘어 |
| 10 | platum.kr | 플래텀 |
| 11 | startuptoday.kr | 스타트업투데이 |
| 12 | startupn.kr | 스타트업엔 |
| 13 | outstanding.kr | 아웃스탠딩 |
| 14 | mobiinside.co.kr | 모비인사이드 |
| 15 | www.zdnet.co.kr | 지디넷코리아 |
| 16 | www.thebell.co.kr | 더벨 |
| 17 | nextunicorn.kr | 넥스트유니콘 |
| 18 | www.epnc.co.kr | 테크월드뉴스 |
| 19 | www.aitimes.com | AI타임스 |
| 20 | www.vmnews.co.kr | 벤처경영신문 |
| 21 | www.newstopkorea.com | 뉴스톱 |
| 22 | www.bloter.net | 블로터 |
| 23 | www.economist.co.kr | 이코노미스트 |
| 24 | www.mk.co.kr/news/it | 매일경제 MK테크리뷰 |
| 25 | news.daum.net/section/2/venture | 다음뉴스 벤처/스타트업 |
| 26 | www.korea.kr | 대한민국 정책브리핑 |

---

## 👥 역할 분담

### 1. Claude Code (AI Assistant)
**담당 작업**:
- ✅ Supabase 테이블 생성 SQL 스크립트 작성
- ✅ Python 스크래핑 스크립트 작성 (Supabase 직접 연동)
- ✅ 설정 파일 및 문서 작성 (.env.example, README.md)

### 2. 재미나 ICI (데이터 수집 및 분석)
**담당 작업**:
- Python 스크립트 실행 (19개 사이트 데이터 수집)
- Supabase 데이터 분석
- 사이트별 뉴스 건수 집계
- 랭킹 생성 및 결과 도출

### 3. 사용자 (프로젝트 관리자)
**담당 작업**:
- Supabase 접속 정보 제공 (URL, anon key)
- 재미나 ICI에게 작업 지시
- 최종 결과 확인 및 승인

---

## 🗄️ 데이터베이스 구조

### 테이블 1: `investment_news_articles` (기사 저장)

**용도**: 수집된 모든 투자유치 뉴스 기사를 저장

| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | SERIAL | 기본 키 | PRIMARY KEY |
| site_number | INTEGER | 사이트 번호 (8-26) | NOT NULL |
| site_name | TEXT | 사이트명 | NOT NULL |
| site_url | TEXT | 사이트 URL | NOT NULL |
| article_title | TEXT | 기사 제목 | NOT NULL |
| article_url | TEXT | 기사 URL | NOT NULL, UNIQUE |
| published_date | DATE | 발행일 | NOT NULL |
| content_snippet | TEXT | 기사 내용 발췌 | |
| collected_at | TIMESTAMP | 수집 시간 | DEFAULT NOW() |

**인덱스**:
- `site_number` (사이트별 조회 최적화)
- `published_date` (날짜 범위 조회 최적화)
- `article_url` (중복 방지)

---

### 테이블 2: `investment_news_ranking` (사이트별 집계)

**용도**: 사이트별 뉴스 건수 집계 및 랭킹

| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | SERIAL | 기본 키 | PRIMARY KEY |
| site_number | INTEGER | 사이트 번호 (8-26) | NOT NULL, UNIQUE |
| site_name | TEXT | 사이트명 | NOT NULL |
| site_url | TEXT | 사이트 URL | NOT NULL |
| news_count | INTEGER | 뉴스 건수 | DEFAULT 0 |
| rank | INTEGER | 랭킹 (1-19) | |
| period_start | DATE | 집계 시작일 | DEFAULT '2026-01-01' |
| period_end | DATE | 집계 종료일 | DEFAULT CURRENT_DATE |
| last_updated | TIMESTAMP | 마지막 업데이트 | DEFAULT NOW() |

**인덱스**:
- `site_number` (UNIQUE)
- `rank` (랭킹 조회 최적화)

---

## 🔧 Python 스크래핑 스크립트 사양

### 파일명
`scrape_investment_news.py`

### 주요 기능

#### 1. 웹 스크래핑
- **라이브러리**: `requests`, `beautifulsoup4`
- **대상**: 19개 뉴스 사이트
- **수집 데이터**:
  - 기사 제목
  - 기사 URL
  - 발행일
  - 기사 내용 일부 (선택 사항)

#### 2. 데이터 필터링
- **날짜 범위**: 2026-01-01 ~ 오늘
- **키워드 매칭**: "투자", "투자유치", "펀딩", "시리즈", "벤처캐피털" 등
- **중복 제거**: URL 기준 중복 방지

#### 3. Supabase 직접 저장
- **라이브러리**: `supabase-py`
- **테이블**: `investment_news_articles`
- **배치 처리**: 100건씩 INSERT
- **에러 핸들링**: 중복 URL 무시 (UNIQUE 제약)

#### 4. 진행 상황 로깅
- **로그 파일**: `scraping_log.txt`
- **콘솔 출력**: 실시간 진행 상황
- **통계**:
  - 사이트별 수집 건수
  - 전체 소요 시간
  - 에러 발생 건수

### 환경변수 설정 (`.env`)
```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

### 의존성 (requirements.txt)
```
requests>=2.31.0
beautifulsoup4>=4.12.0
supabase>=2.0.0
python-dotenv>=1.0.0
lxml>=4.9.0
```

---

## 📊 데이터 분석 (재미나 ICI 담당)

### 집계 쿼리 예시

#### 1. 사이트별 뉴스 건수 집계
```sql
SELECT
    site_number,
    site_name,
    COUNT(*) as news_count
FROM investment_news_articles
WHERE published_date BETWEEN '2026-01-01' AND CURRENT_DATE
GROUP BY site_number, site_name
ORDER BY news_count DESC;
```

#### 2. 랭킹 테이블 업데이트
```sql
WITH ranked_sites AS (
    SELECT
        site_number,
        site_name,
        site_url,
        COUNT(*) as news_count,
        RANK() OVER (ORDER BY COUNT(*) DESC) as rank
    FROM investment_news_articles
    WHERE published_date BETWEEN '2026-01-01' AND CURRENT_DATE
    GROUP BY site_number, site_name, site_url
)
INSERT INTO investment_news_ranking
    (site_number, site_name, site_url, news_count, rank, last_updated)
SELECT
    site_number,
    site_name,
    site_url,
    news_count,
    rank,
    NOW()
FROM ranked_sites
ON CONFLICT (site_number)
DO UPDATE SET
    news_count = EXCLUDED.news_count,
    rank = EXCLUDED.rank,
    last_updated = NOW();
```

#### 3. 최종 랭킹 조회
```sql
SELECT
    rank,
    site_name,
    site_url,
    news_count
FROM investment_news_ranking
ORDER BY rank ASC;
```

---

## 🚀 실행 프로세스

### Phase 1: 준비 (Claude Code)
1. ✅ SQL 스크립트 작성 (`create_tables.sql`)
2. ✅ Python 스크립트 작성 (`scrape_investment_news.py`)
3. ✅ 설정 파일 작성 (`.env.example`)
4. ✅ 사용 가이드 작성 (`README.md`)
5. ✅ 파일 저장 위치: `scripts/investment-news-scraper/`

### Phase 2: 환경 설정 (사용자)
1. Supabase 프로젝트 접속
2. SQL 스크립트 실행 (테이블 생성)
3. `.env` 파일 생성 (Supabase URL, Key 입력)
4. Python 패키지 설치: `pip install -r requirements.txt`
5. 재미나 ICI에게 접속 정보 공유

### Phase 3: 데이터 수집 (재미나 ICI)
1. Python 스크립트 실행: `python scrape_investment_news.py`
2. 19개 사이트 순차적 스크래핑
3. Supabase `investment_news_articles` 테이블에 자동 저장
4. 로그 파일 확인 (`scraping_log.txt`)

### Phase 4: 데이터 분석 (재미나 ICI)
1. Supabase 접속
2. 사이트별 뉴스 건수 집계 (SQL 쿼리)
3. `investment_news_ranking` 테이블 업데이트
4. 최종 랭킹 조회 및 결과 도출

### Phase 5: 결과 확인 (사용자)
1. 랭킹 테이블 확인
2. 분석 결과 검토
3. 필요 시 추가 분석 요청

---

## 📁 프로젝트 파일 구조

```
scripts/investment-news-scraper/
├── PROJECT_PLAN.md              # 이 파일 (프로젝트 계획서)
├── create_tables.sql            # Supabase 테이블 생성 SQL
├── scrape_investment_news.py    # Python 스크래핑 스크립트
├── requirements.txt             # Python 의존성 패키지 목록
├── .env.example                 # 환경변수 설정 예시
├── README.md                    # 사용 가이드
└── scraping_log.txt             # 스크래핑 로그 (실행 후 생성)
```

---

## ⚠️ 주의사항

### 법적/윤리적 고려사항
1. **robots.txt 준수**: 각 사이트의 크롤링 정책 확인
2. **요청 간격**: 서버 부하 방지를 위해 요청 간 1-2초 대기
3. **User-Agent 설정**: 크롤러 식별 정보 명시
4. **저작권**: 기사 전문이 아닌 제목/URL/발췌만 저장

### 기술적 고려사항
1. **동적 사이트**: JavaScript 렌더링 필요 시 Selenium 사용 고려
2. **사이트 구조 변경**: 스크래핑 로직 유지보수 필요
3. **에러 처리**: 네트워크 오류, 타임아웃 대응
4. **중복 방지**: URL 기준 UNIQUE 제약으로 중복 INSERT 방지

### 보안
1. **환경변수 관리**: `.env` 파일을 `.gitignore`에 추가
2. **Supabase Key**: anon key (읽기/쓰기) 사용, service_role key 사용 금지
3. **접속 정보 공유**: 안전한 채널 사용 (암호화된 메시지)

---

## 📈 예상 결과물

### 1. Supabase 테이블
- `investment_news_articles`: 약 200-500건 예상 (사이트당 평균 10-25건)
- `investment_news_ranking`: 19개 사이트 랭킹

### 2. 랭킹 예시
| 순위 | 사이트명 | 뉴스 건수 |
|------|---------|----------|
| 1 | 벤처스퀘어 | 45건 |
| 2 | 플래텀 | 38건 |
| 3 | 더브이씨 | 32건 |
| ... | ... | ... |
| 19 | 대한민국 정책브리핑 | 5건 |

---

## 🔄 향후 확장 계획

### 단기 (1-2주)
- 일일 자동 수집 (cron job 설정)
- 데이터 시각화 대시보드
- 이메일 알림 (신규 뉴스 발생 시)

### 중기 (1-3개월)
- AI 기반 투자 규모 추출 (예: "100억 투자유치")
- 업종별 분류 (핀테크, 이커머스, AI 등)
- 투자사 정보 추출 (VC 이름)

### 장기 (3-6개월)
- 투자 트렌드 분석
- 예측 모델 (투자 건수 예측)
- API 제공 (외부 서비스 연동)

---

## 📞 문의 및 지원

**작성자**: Claude Code (AI Assistant)
**프로젝트 관리**: 사용자
**데이터 수집/분석**: 재미나 ICI

**파일 위치**: `scripts/investment-news-scraper/PROJECT_PLAN.md`

---

**작성 완료일**: 2026-01-25
**버전**: 1.0
