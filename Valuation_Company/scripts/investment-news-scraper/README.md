# 투자 뉴스 스크래핑 및 랭킹 시스템

**국내 19개 투자유치 뉴스 사이트의 뉴스 수집 및 랭킹 시스템**

---

## 📋 프로젝트 개요

- **목적**: 2026년 1월 1일 ~ 현재까지 투자유치 관련 뉴스 수집 및 사이트별 랭킹
- **대상**: 19개 주요 투자/벤처 뉴스 사이트
- **저장**: Supabase 데이터베이스
- **분석**: 뉴스 건수 기반 1-19위 랭킹

---

## 🚀 빠른 시작

### 1단계: 환경 설정

#### Python 설치 확인
```bash
python --version  # Python 3.8 이상 필요
```

#### 패키지 설치
```bash
cd scripts/investment-news-scraper
pip install -r requirements.txt
```

---

### 2단계: Supabase 설정

#### 1) Supabase 프로젝트 생성
1. https://supabase.com 접속
2. 로그인 (없으면 가입)
3. "New Project" 클릭
4. 프로젝트명 입력 및 생성 대기 (1-2분)

#### 2) 테이블 생성
1. Supabase 대시보드 > SQL Editor 메뉴
2. `create_tables.sql` 파일 내용 복사
3. SQL Editor에 붙여넣기
4. "Run" 버튼 클릭

✅ **결과 확인**:
- "Table Editor" 메뉴에서 테이블 2개 확인:
  - `investment_news_articles`
  - `investment_news_ranking`

#### 3) API 키 확인
1. Settings > API 메뉴
2. 다음 정보 복사:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...` (긴 문자열)

---

### 3단계: 환경변수 설정

#### .env 파일 생성
```bash
cp .env.example .env
```

#### .env 파일 수정
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

⚠️ **실제 값으로 변경하세요!**

---

### 4단계: 스크립트 실행

```bash
python scrape_investment_news.py
```

**예상 소요 시간**: 5-10분 (사이트별 2초 대기)

**실행 중 로그**:
```
📰 투자 뉴스 스크래핑 시작
📅 기간: 2026-01-01 ~ 2026-01-25
🌐 대상 사이트: 19개
==================================================
[1/19] 더브이씨 처리 중...
🔍 [8] 더브이씨 스크래핑 시작...
✅ [8] 더브이씨: 12건 수집
⏳ 2초 대기 중...
...
✅ 스크래핑 완료!
📊 수집 건수: 234건
💾 저장 건수: 234건
```

---

### 5단계: 랭킹 업데이트

#### Supabase에서 SQL 실행
1. Supabase 대시보드 > SQL Editor
2. 다음 SQL 실행:
```sql
SELECT update_news_ranking();
```

#### 랭킹 확인
```sql
SELECT * FROM v_latest_ranking;
```

**결과 예시**:
| rank | site_name | news_count |
|------|-----------|------------|
| 1 | 벤처스퀘어 | 45 |
| 2 | 플래텀 | 38 |
| 3 | 더브이씨 | 32 |
| ... | ... | ... |

---

## 📁 파일 구조

```
scripts/investment-news-scraper/
├── README.md                    # 이 파일
├── PROJECT_PLAN.md              # 프로젝트 계획서
├── create_tables.sql            # 테이블 생성 SQL
├── scrape_investment_news.py    # 스크래핑 스크립트
├── requirements.txt             # Python 패키지 목록
├── .env.example                 # 환경변수 예시
├── .env                         # 환경변수 (직접 생성)
└── scraping_log.txt             # 실행 로그 (자동 생성)
```

---

## 🗄️ 데이터베이스 구조

### 테이블 1: `investment_news_articles`

**용도**: 수집된 모든 뉴스 기사 저장

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 자동 증가 ID |
| site_number | INTEGER | 사이트 번호 (8-26) |
| site_name | TEXT | 사이트명 |
| site_url | TEXT | 사이트 URL |
| article_title | TEXT | 기사 제목 |
| article_url | TEXT | 기사 URL (UNIQUE) |
| published_date | DATE | 발행일 |
| content_snippet | TEXT | 내용 발췌 |
| collected_at | TIMESTAMP | 수집 시간 |

### 테이블 2: `investment_news_ranking`

**용도**: 사이트별 뉴스 건수 집계 및 랭킹

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 자동 증가 ID |
| site_number | INTEGER | 사이트 번호 (UNIQUE) |
| site_name | TEXT | 사이트명 |
| site_url | TEXT | 사이트 URL |
| news_count | INTEGER | 뉴스 건수 |
| rank | INTEGER | 랭킹 (1-19) |
| period_start | DATE | 집계 시작일 |
| period_end | DATE | 집계 종료일 |
| last_updated | TIMESTAMP | 마지막 업데이트 |

---

## 🎯 사이트 목록 (19개)

| 번호 | 사이트명 | URL |
|------|---------|-----|
| 8 | 더브이씨 | thevc.kr |
| 9 | 벤처스퀘어 | www.venturesquare.net |
| 10 | 플래텀 | platum.kr |
| 11 | 스타트업투데이 | startuptoday.kr |
| 12 | 스타트업엔 | startupn.kr |
| 13 | 아웃스탠딩 | outstanding.kr |
| 14 | 모비인사이드 | mobiinside.co.kr |
| 15 | 지디넷코리아 | www.zdnet.co.kr |
| 16 | 더벨 | www.thebell.co.kr |
| 17 | 넥스트유니콘 | nextunicorn.kr |
| 18 | 테크월드뉴스 | www.epnc.co.kr |
| 19 | AI타임스 | www.aitimes.com |
| 20 | 벤처경영신문 | www.vmnews.co.kr |
| 21 | 뉴스톱 | www.newstopkorea.com |
| 22 | 블로터 | www.bloter.net |
| 23 | 이코노미스트 | www.economist.co.kr |
| 24 | 매일경제 MK테크리뷰 | www.mk.co.kr/news/it |
| 25 | 다음뉴스 벤처/스타트업 | news.daum.net/section/2/venture |
| 26 | 대한민국 정책브리핑 | www.korea.kr |

---

## 🔧 스크립트 커스터마이징

### 사이트별 스크래핑 로직 수정

`scrape_investment_news.py`의 `scrape_generic_site()` 함수는 **기본 템플릿**입니다.

**각 사이트의 HTML 구조에 맞게 커스터마이징이 필요합니다.**

#### 예시: 벤처스퀘어
```python
def scrape_venturesquare(site: Dict) -> List[Dict]:
    """벤처스퀘어 전용 스크래핑"""
    articles = []
    url = 'https://www.venturesquare.net/category/investment'

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')

    # 벤처스퀘어의 실제 HTML 구조에 맞게 수정
    for article_elem in soup.select('.article-list .item'):
        title = article_elem.select_one('.title').get_text(strip=True)
        article_url = article_elem.select_one('a')['href']
        date_text = article_elem.select_one('.date').get_text(strip=True)
        published_date = parse_date(date_text)

        if contains_keyword(title) and is_valid_date(published_date):
            articles.append({
                'site_number': 9,
                'site_name': '벤처스퀘어',
                'site_url': 'www.venturesquare.net',
                'article_title': title,
                'article_url': article_url,
                'published_date': published_date.isoformat(),
            })

    return articles
```

---

## 🔍 유용한 SQL 쿼리

### 1. 전체 뉴스 수 확인
```sql
SELECT COUNT(*) as total_articles
FROM investment_news_articles
WHERE published_date BETWEEN '2026-01-01' AND CURRENT_DATE;
```

### 2. 날짜별 뉴스 건수
```sql
SELECT published_date, COUNT(*) as daily_count
FROM investment_news_articles
GROUP BY published_date
ORDER BY published_date DESC;
```

### 3. 특정 사이트 뉴스 목록
```sql
SELECT article_title, article_url, published_date
FROM investment_news_articles
WHERE site_number = 9  -- 벤처스퀘어
ORDER BY published_date DESC;
```

### 4. 키워드별 검색
```sql
SELECT site_name, article_title, published_date
FROM investment_news_articles
WHERE article_title ILIKE '%시리즈%'
ORDER BY published_date DESC;
```

### 5. 랭킹 재계산
```sql
SELECT update_news_ranking();
SELECT * FROM v_latest_ranking;
```

---

## ⚠️ 주의사항

### 법적/윤리적
- ✅ **robots.txt 준수**: 각 사이트의 크롤링 정책 확인
- ✅ **요청 간격**: 2초 대기로 서버 부하 방지
- ✅ **저작권**: 기사 전문이 아닌 제목/URL만 저장

### 기술적
- ⚠️ **동적 사이트**: JavaScript 렌더링 필요 시 Selenium 사용
- ⚠️ **사이트 구조 변경**: 정기적으로 스크래핑 로직 점검 필요
- ⚠️ **에러 처리**: 네트워크 오류 시 재시도 로직 추가 고려

### 보안
- 🔒 **.env 파일**: 절대 Git에 커밋하지 않기 (`.gitignore` 확인)
- 🔒 **Supabase Key**: anon key 사용 (service_role key 사용 금지)

---

## 🐛 문제 해결

### 1. 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 설치
pip install requests beautifulsoup4 lxml supabase python-dotenv
```

### 2. Supabase 연결 오류
- `.env` 파일이 존재하는지 확인
- SUPABASE_URL과 SUPABASE_KEY가 올바른지 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

### 3. 스크래핑 실패
- 사이트가 접근 가능한지 브라우저에서 확인
- `scraping_log.txt` 파일에서 에러 메시지 확인
- 특정 사이트만 실패 시: HTML 구조 변경 가능성

### 4. 중복 URL 에러
- 정상 동작 (이미 수집된 기사는 자동 스킵)
- 로그에 "⚠️ 중복 URL 감지" 메시지 출력

---

## 📊 데이터 분석 (재미나 ICI)

### Python으로 랭킹 조회
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# 랭킹 업데이트
supabase.rpc('update_news_ranking').execute()

# 랭킹 조회
ranking = supabase.table('investment_news_ranking').select('*').order('rank').execute()

for site in ranking.data:
    print(f"{site['rank']}위: {site['site_name']} ({site['news_count']}건)")
```

---

## 📞 문의

**작성자**: Claude Code (AI Assistant)
**작성일**: 2026-01-25
**프로젝트**: 투자 뉴스 스크래핑 및 랭킹 시스템

---

## 📝 라이선스

이 프로젝트는 교육 및 분석 목적으로 제작되었습니다.
각 뉴스 사이트의 이용약관을 준수해주세요.
