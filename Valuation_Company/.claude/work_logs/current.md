# 작업 로그

## 2026-01-25: 투자 뉴스 스크래핑 시스템 구축

### 작업 상태: 🟡 진행 중

---

## 작업 내용

### 1. 프로젝트 설정 ✅ 완료
- 폴더 생성: `scripts/investment-news-scraper/`
- 파일 7개 생성:
  - `PROJECT_PLAN.md` (프로젝트 계획서)
  - `create_tables.sql` (테이블 생성 SQL)
  - `scrape_investment_news.py` (스크래핑 스크립트)
  - `requirements.txt` (패키지 목록)
  - `.env.example` (환경변수 예시)
  - `.env` (실제 환경변수 - Supabase 연결)
  - `README.md` (사용 가이드)
  - `.gitignore` (보안 설정)

### 2. Supabase 테이블 생성 ✅ 완료
- `investment_news_articles` 테이블 생성
- `investment_news_ranking` 테이블 생성
- 19개 사이트 초기 데이터 INSERT
- 함수 및 뷰 생성 (`update_news_ranking()`, `v_latest_ranking`)

### 3. 환경 설정 ✅ 완료
- Python 패키지 설치 완료
- .env 파일 생성 (기존 Supabase 연결 정보 사용)

### 4. 테스트 실행 ✅ 완료
- 스크립트 실행: `python scrape_investment_news.py`
- 결과: **0건 수집** (예상된 결과)
- 원인: 범용 템플릿 함수가 실제 사이트 HTML 구조와 불일치

### 5. 재미나 ICI 작업 요청서 작성 ✅ 완료
- 파일: `REQUEST_TO_JEMINA_ICI.md`
- 내용:
  - 현재 상황 설명
  - 문제점 분석
  - 수정 방법 상세 가이드
  - 테스트 방법
  - 주의사항

---

## 다음 단계

### 재미나 ICI 작업 (데이터 수집)
1. 각 사이트 HTML 구조 분석
2. 사이트별 스크래핑 함수 커스터마이징
3. 테스트 및 데이터 수집
4. Supabase 데이터 확인

### 데이터 분석 (재미나 ICI)
1. `SELECT update_news_ranking();` 실행
2. 랭킹 조회 및 결과 도출
3. 사용자에게 최종 보고

---

## 파일 위치

**프로젝트 폴더**:
```
C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\
```

**생성된 파일**:
- PROJECT_PLAN.md
- create_tables.sql
- scrape_investment_news.py
- requirements.txt
- .env
- .env.example
- README.md
- .gitignore
- REQUEST_TO_JEMINA_ICI.md
- scraping_log.txt (자동 생성)

---

## 기술 스택

- Python 3.8+
- requests, beautifulsoup4, lxml
- supabase-py
- python-dotenv
- Supabase (PostgreSQL)

---

## 대상 사이트 (19개)

8-26번 사이트 (더브이씨, 벤처스퀘어, 플래텀 등)

---

## 비고

- 스크래핑 스크립트는 범용 템플릿으로 작성됨
- 실제 데이터 수집을 위해서는 사이트별 커스터마이징 필수
- 재미나 ICI가 HTML 구조 분석 및 수정 담당

---

## 2026-01-26: 평가법별 14단계 프로세스 구현

### 작업 상태: 🟡 진행 중 (Phase 1 시작 예정)

---

## 완료된 작업

### 1. 담당 공인회계사 섹션 추가 ✅
- 5개 평가법 가이드 페이지 사이드바에 "담당 공인회계사" 섹션 추가
- 파일 생성:
  - `accountant-profile.html` (회계사 프로필 페이지)
  - `create_accountants_table.sql` (Supabase 테이블)
  - `update_accountants_table.sql` (데이터 업데이트)
- 회계사 정보: 선웅규 (CPA 2353), 연세대 경영학과, 4개 회계법인 경력
- 색상: 파란색 계열로 통일
- 커밋: `feacca6`

### 2. 프로세스 용어 연구 및 확정 ✅
- general-purpose 에이전트로 고객 관점 용어 연구
- 금융/컨설팅/법무 서비스 벤치마크
- 14단계 프로세스 최종 확정
- 용어 원칙:
  - 고객이 하는 단계: 능동형 ("신청", "제출", "확인")
  - 대기/진행 단계: 진행형 ("~중")
  - "회사"/"기업" 생략으로 간결화

### 3. 평가법 정보 정리 ✅
- 본질가치평가법 영문명: Intrinsic Value Method
- 프로젝트 코드 변경: `IP` → `IV`
- 파일명 변경 예정:
  - `ipo-portal.html` → `intrinsic-portal.html`
  - `ipo-valuation.html` → `intrinsic-valuation.html`

### 4. 프로젝트 ID 부여 방식 확인 ✅
- 형식: `[회사영문명5글자]-[YYMMDDHHmm]-[평가법코드]`
- 예시: `APPLE-2601261530-DC`

### 5. 평가 엔진 확인 ✅
- 위치: `backend/app/services/valuation_engine/`
- 5개 엔진 모두 존재 확인 (dcf, relative, intrinsic, asset, tax)

### 6. 업무인수인계서 작성 ✅
- 파일: `Human_ClaudeCode_Bridge/Reports/평가법별_14단계_프로세스_구현_인수인계서.md`
- 내용:
  - 완료된 작업 정리
  - 확정된 14단계 프로세스
  - 평가법별 매핑 정보
  - 앞으로 해야 할 작업 (Phase 1-5)
  - 구현 우선순위
  - 주요 결정사항
  - 참고 자료

---

## 확정된 14단계 프로세스

| # | 단계명 | 담당 | 기존 페이지 | 작업 |
|---|--------|------|------------|------|
| 1 | 서비스 안내 | 고객 | mockup-valuation.html | URL 수정 |
| 2 | 평가 신청 | 고객 | project-create.html | 평가법 파라미터 |
| 3 | 관리자 승인 대기 | 관리자 | ❌ | **신규 생성** |
| 4 | 평가 기초자료 제출 | 고객 | {method}-portal.html | 링크 연결 |
| 5 | 데이터 수집 중 | AI | ❌ | **신규 생성** |
| 6 | 평가 진행 중 | 엔진 | ❌ | **신규 생성** |
| 7 | 공인회계사 검토 중 | 회계사 | ❌ | **신규 생성** |
| 8 | 평가보고서 초안 생성 | AI | ❌ | **신규 생성** |
| 9 | 평가보고서 초안 확인 | 고객 | {method}-valuation.html | 초안 모드 |
| 10 | 수정 요청 | 고객 | project-detail.html | 수정 탭 |
| 11 | 평가보고서 최종안 작성 | 회계사 | ❌ | **신규 생성** |
| 12 | 평가보고서 최종안 확인 | 고객 | {method}-valuation.html | 최종안 모드 |
| 13 | 결제하기 | 고객 | ❌ | **신규 생성** |
| 14 | 평가보고서 수령 | 고객 | ❌ | **신규 생성** |

---

## 다음 작업 (Phase 1 - 즉시 시작)

### 1. 본질가치평가법 파일명 변경
- [ ] `ipo-portal.html` → `intrinsic-portal.html`
- [ ] `ipo-valuation.html` → `intrinsic-valuation.html`
- [ ] `project-create.html`에서 `IP` → `IV` 변경
- [ ] DB methodCodeMap 수정

### 2. 가이드 페이지에 평가법 표시 추가
- [ ] `guide-dcf.html`
- [ ] `guide-relative.html`
- [ ] `guide-intrinsic.html`
- [ ] `guide-asset.html`
- [ ] `guide-tax.html`

### 3. 사이드바 동적 링크 JavaScript 작성
- [ ] 공통 JavaScript 함수 (`sidebar-links.js`)
- [ ] 5개 가이드 페이지에 스크립트 포함

---

## 참고 문서

- **인수인계서**: `Human_ClaudeCode_Bridge/Reports/평가법별_14단계_프로세스_구현_인수인계서.md`
- **시스템 구성도**: `기업가치평가_시스템_구성도.svg`
- **회계사 프로필**: `accountant-profile.html`

---

**최종 업데이트**: 2026-01-26
**상태**: Phase 1 시작 예정
**예상 완료**: 2주 (Phase 1-5)
