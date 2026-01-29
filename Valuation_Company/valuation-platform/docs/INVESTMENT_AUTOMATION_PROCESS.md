# 투자 뉴스 자동 수집 및 정제 시스템 (Daily Automation)

이 문서는 매일 아침 6시에 실행되는 투자 뉴스 자동화 프로세스의 상세 설계와 운영 방법을 설명합니다.

## 🔄 프로세스 흐름 (Daily Workflow)

### 1단계: 뉴스 수집 (Collecting) - 오전 6:00
*   **대상:** 전일 발생한 투자 관련 뉴스
*   **채널 (6대 핵심 채널):**
    1.  와우테일 (Wowtale)
    2.  벤처스퀘어 (VentureSquare)
    3.  플래텀 (Platum)
    4.  스타트업투데이 (StartupToday)
    5.  아웃스탠딩 (Outstanding)
    6.  Naver 뉴스 (키워드: "투자 유치") + Google 뉴스 보조
*   **조건:** 제목/본문에 "투자 유치", "투자사", "피투자사" 정보가 포함된 기사 선별

### 2단계: 최적 뉴스 선별 (Selection)
*   동일 기업의 투자가 여러 매체에서 보도될 경우, 가장 정보량이 많고 신뢰도가 높은(Gemini 점수 기반) 1개의 기사를 대표 기사로 선정하여 `deals` 테이블에 등록합니다.

### 3단계: AI 데이터 정제 (AI Extraction)
*   **도구:** Gemini AI (`gemini-2.0-flash`)
*   **추출 항목:** 기업명, 주요 사업(한글), 투자 단계, 투자 금액, 투자자 목록, 뉴스 요약 등
*   **저장:** `deals` 테이블에 정규화된 데이터 업데이트

### 4단계: 데이터 보강 및 검증 (Enrichment)
*   AI 추출 결과가 미흡하거나(예: 업종 모호) 필수 정보가 누락된 경우 수행합니다.
*   **방법:** 네이버 검색 API(또는 웹 크롤링)를 통해 "{기업명} 주요 사업" 등을 추가 검색하여 데이터 보충

### 5단계: 데일리 뉴스레터 발송 (Reporting)
*   정제된 어제의 투자 뉴스를 요약하여 등록된 이메일로 리포트를 발송합니다.

## 🛠️ 시스템 구성 파일

| 파일명 | 역할 | 비고 |
|--------|------|------|
| `daily_automation.py` | 전체 프로세스 통합 실행기 | 메인 엔트리 포인트 |
| `news_crawler/` | 6대 매체별 크롤러 모듈 | 신규 3종 추가 예정 |
| `news_parser.py` | Gemini AI 기반 데이터 추출기 | 기존 모듈 활용 |
| `data_enricher.py` | 네이버 API 기반 데이터 보강기 | 신규 개발 |
| `daily_reporter.py` | 이메일 리포트 생성 및 발송기 | 신규 개발 |

## ⚙️ 설정 (Environment Variables)

`.env` 파일에 다음 정보가 필요합니다:
*   `GOOGLE_API_KEY`: Gemini AI 사용
*   `NAVER_CLIENT_ID` & `NAVER_CLIENT_SECRET`: 네이버 검색 API (키가 없을 경우 크롤링으로 대체)
*   `SMTP_USER` & `SMTP_PASSWORD`: 이메일 발송용 설정

## 🚀 실행 방법

### 1. 윈도우 작업 스케줄러 등록
1.  `run_daily_job.bat` 파일을 생성합니다.
2.  윈도우 작업 스케줄러에서 매일 오전 6시에 해당 배치 파일을 실행하도록 등록합니다.

```batch
@echo off
cd /d C:\ValueLink\Valuation_Company\valuation-platform\backend
python daily_automation.py
```

### 2. 수동 실행
```bash
cd backend
python daily_automation.py
```

---
*Last Updated: 2026-01-29*
