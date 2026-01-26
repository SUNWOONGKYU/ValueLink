# Investment News Network 설치 및 실행 가이드

> 완전 자동화 투자 뉴스 수집 시스템

---

## 📋 시스템 구성

```
Investment News Network
├── 11개 소스 (RSS 4 + 웹스크래핑 6 + VC DB 1)
├── Gemini AI (점수 계산 + Deal 정보 추출)
├── TheVC (회사/투자자 정보 보강)
├── Naver API (부족한 정보 추가)
└── 이메일 시스템 (일일 + 주간)
```

---

## 🚀 설치 단계

### 1. 환경 변수 설정

`.env` 파일 생성:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Gemini API
GEMINI_API_KEY=your-gemini-key

# Naver API
NAVER_CLIENT_ID=your-client-id
NAVER_CLIENT_SECRET=your-client-secret

# Resend (이메일)
RESEND_API_KEY=your-resend-key
```

### 2. Python 패키지 설치

```bash
cd scripts/investment-news-scraper
pip install -r requirements.txt
```

### 3. Supabase 스키마 적용

```bash
python apply_schema.py
```

**입력 필요:**
- Supabase Database 비밀번호 (Settings → Database에서 확인)

**생성되는 테이블:**
- investment_news_network_sources (11개 소스)
- investment_news_articles (수집된 모든 기사)
- deals (선정된 투자 뉴스)
- email_subscribers (구독자)
- email_send_log (발송 기록)

### 4. GitHub Secrets 설정

**GitHub 레포지토리 → Settings → Secrets and variables → Actions**

```
SUPABASE_URL
SUPABASE_KEY
GEMINI_API_KEY
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
RESEND_API_KEY
```

---

## 🎯 수동 실행 (테스트)

### RSS 수집만 실행

```bash
python collect_rss.py
```

**수집 소스:**
- 벤처스퀘어
- 아웃스탠딩
- 플래텀
- 비석세스

### 웹 스크래핑만 실행

```bash
python collect_web.py
```

**수집 소스:**
- 스타트업투데이
- 스타트업엔
- 블로터
- 이코노미스트
- AI타임스
- 넥스트유니콘

### 전체 프로세스 실행

```bash
python collect_and_enrich.py
```

**실행 순서:**
1. RSS + 웹 스크래핑 수집
2. Gemini로 점수 계산
3. 기업별 최고 점수 선정
4. Gemini로 Deal 정보 추출
5. TheVC로 보강
6. Naver API로 보강
7. deals 테이블 저장

### TheVC 테스트

```bash
python search_thevc.py
```

**테스트 항목:**
- 기업 정보 조회
- 투자자 정보 조회
- Deal 보강

### 일일 이메일 테스트

```bash
python send_daily_email.py
```

**발송 내용:**
- 어제 수집된 투자 뉴스
- HTML 이메일 템플릿

### 주간 이메일 테스트

```bash
python send_weekly_email.py
```

**발송 내용:**
- 지난 주 투자 통계
- 단계/업종/투자자 순위
- HTML 리포트

---

## ⏰ 자동화 스케줄

### GitHub Actions 워크플로우

**1. 매일 오전 8시 (월-토)**
- 파일: `.github/workflows/investment-news-daily.yml`
- 작업:
  - 뉴스 수집 (RSS + 웹스크래핑)
  - Gemini/TheVC/Naver 보강
  - deals 테이블 저장
  - 일일 이메일 발송 (월-토만)

**2. 매주 일요일 오전 10시**
- 파일: `.github/workflows/investment-news-weekly.yml`
- 작업:
  - 주간 인사이트 리포트 발송

### 스케줄 확인

```bash
# GitHub Actions 워크플로우 수동 실행
# GitHub 레포지토리 → Actions → 워크플로우 선택 → Run workflow
```

---

## 📊 데이터 흐름

```
┌─────────────────────────────────────────────────────────────┐
│  매일 오전 8시                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RSS (4개) + 웹스크래핑 (6개)                                │
│      ↓                                                      │
│  investment_news_articles 테이블                            │
│      ↓                                                      │
│  Gemini: 점수 계산 (11점)                                    │
│      ↓                                                      │
│  기업별 최고 점수 선정                                        │
│      ↓                                                      │
│  Gemini: Deal 정보 추출                                      │
│      ↓                                                      │
│  TheVC: 회사/투자자 보강 ⭐                                  │
│      ↓                                                      │
│  Naver API: 부족한 정보 추가                                 │
│      ↓                                                      │
│  deals 테이블 저장                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  매일 오전 9시 (월-토)                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  어제 deals 조회                                             │
│      ↓                                                      │
│  HTML 이메일 생성                                            │
│      ↓                                                      │
│  구독자 발송                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  일요일 오전 10시                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  지난 주 deals 조회                                          │
│      ↓                                                      │
│  통계 분석 (단계/업종/투자자)                                 │
│      ↓                                                      │
│  HTML 리포트 생성                                            │
│      ↓                                                      │
│  구독자 발송                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 모니터링

### Supabase SQL Editor에서 확인

**오늘 수집된 기사 수:**
```sql
SELECT source_name, COUNT(*)
FROM investment_news_articles
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY source_name;
```

**최근 Deal 목록:**
```sql
SELECT company_name, amount, stage, investors, news_date
FROM deals
ORDER BY news_date DESC
LIMIT 10;
```

**소스별 선정률:**
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

### GitHub Actions 로그

```
GitHub 레포지토리 → Actions → 워크플로우 실행 내역 확인
```

---

## ⚙️ 설정 변경

### 수집 소스 추가/제거

`scripts/investment-news-scraper/collect_rss.py` 또는 `collect_web.py` 수정

### 투자 키워드 추가

`INVESTMENT_KEYWORDS` 리스트 수정:
```python
INVESTMENT_KEYWORDS = [
    '투자', '유치', '시리즈', 'funding', ...
]
```

### 제외 키워드 추가

`EXCLUDED_KEYWORDS` 리스트 수정:
```python
EXCLUDED_KEYWORDS = [
    'IR', 'M&A', '인수', ...
]
```

### 이메일 템플릿 수정

`send_daily_email.py` 또는 `send_weekly_email.py`의 `generate_*_html()` 함수 수정

---

## 🐛 문제 해결

### 스키마 적용 실패

```bash
# Supabase Database 비밀번호 확인
# Settings → Database → Database password 재설정
```

### Gemini API 할당량 초과

```bash
# gemini-2.5-flash 모델 사용 (높은 할당량)
# Rate limiting 시간 조정: time.sleep(0.6) → time.sleep(1)
```

### TheVC 조회 실패

```bash
# 웹사이트 구조 변경 가능
# search_thevc.py의 선택자 업데이트 필요
```

### 이메일 발송 실패

```bash
# Resend API 키 확인
# 발신자 이메일 도메인 인증 필요
```

---

## 📝 파일 구조

```
scripts/investment-news-scraper/
├── apply_schema.py              # 스키마 적용
├── collect_rss.py               # RSS 수집 (4개)
├── collect_web.py               # 웹스크래핑 (6개)
├── collect_and_enrich.py        # 통합 + 보강
├── search_thevc.py              # TheVC 조회
├── search_company_info.py       # Naver API
├── send_daily_email.py          # 일일 이메일
├── send_weekly_email.py         # 주간 이메일
├── requirements.txt             # 패키지 의존성
├── DATABASE_SCHEMA.sql          # 스키마 정의
├── DATABASE_STRUCTURE.md        # 스키마 문서
└── SETUP_GUIDE.md               # 이 파일
```

---

## 📞 지원

문제가 있거나 질문이 있으면:
1. GitHub Issues 등록
2. 로그 파일 첨부
3. 에러 메시지 복사

---

## 🎉 완료 체크리스트

- [ ] .env 파일 생성
- [ ] Python 패키지 설치
- [ ] Supabase 스키마 적용
- [ ] GitHub Secrets 설정
- [ ] RSS 수집 테스트
- [ ] 웹스크래핑 테스트
- [ ] 전체 프로세스 테스트
- [ ] TheVC 조회 테스트
- [ ] 이메일 발송 테스트
- [ ] GitHub Actions 워크플로우 확인

---

**모든 설정이 완료되었습니다! 🚀**

매일 오전 8시에 자동으로 뉴스를 수집하고,
오전 9시에 구독자들에게 이메일을 발송합니다.
