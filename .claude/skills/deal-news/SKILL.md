---
name: deal-news
description: Deal 뉴스 자동 수집 - GitHub Actions 트리거 + 모니터링 + 결과 확인
argument-hint: "[날짜 YYYY-MM-DD]"
allowed-tools: "Bash(gh *), Bash(cd *), Bash(sleep *), Read, Grep"
---

# Deal News 자동 수집

투자 뉴스를 자동으로 수집합니다. GitHub Actions 워크플로우를 트리거하고 결과를 확인합니다.

## 프로세스

### Step 1: 워크플로우 트리거

날짜 인자가 있으면 해당 날짜, 없으면 어제 날짜로 수집합니다.

```bash
# 인자 있을 때
gh workflow run "Daily Investment News Scraper" --ref master -f target_date=$ARGUMENTS

# 인자 없을 때
gh workflow run "Daily Investment News Scraper" --ref master
```

실행 디렉토리: 레포지토리 루트 (C:\ValueLink)

### Step 2: 실행 대기 및 모니터링

```bash
# 10초 대기 후 상태 확인
sleep 10
gh run list --workflow="Daily Investment News Scraper" --limit 1
```

- `in_progress`이면 완료될 때까지 30초 간격으로 재확인 (최대 5분)
- `completed`이면 Step 3으로

### Step 3: 결과 확인

```bash
# 최신 run ID로 결과 확인
gh run view {RUN_ID}
```

- **success**: Step 4로 → 상세 로그 확인
- **failure**: Step 5로 → 에러 분석

### Step 4: 성공 시 상세 로그

```bash
gh run view {RUN_ID} --log 2>&1 | grep -E "수집|저장|완료|기사|deal|0개|건|투자|❌|✅|⚠️"
```

사용자에게 보고할 내용:
- 수집된 기사 수
- 저장된 건수
- 탈락된 기사와 사유
- 이메일 발송 여부

### Step 5: 실패 시 에러 분석

```bash
gh run view {RUN_ID} --log-failed 2>&1 | grep -E "error|Error|Traceback|TypeError|ModuleNotFoundError|exit code" | head -20
```

에러 원인을 분석하고 사용자에게 보고:
- 에러 종류 (스크립트 오류, 환경변수 누락, 의존성 문제 등)
- 해당 코드 위치
- 수정 방안 제안

## 사용 예시

```
/deal-news              # 어제 날짜 뉴스 수집
/deal-news 2026-01-30   # 특정 날짜 뉴스 수집
```

## 관련 파일

- 워크플로우: `.github/workflows/daily-news-scraper.yml`
- 수집 스크립트: `Valuation_Company/scripts/investment-news-scraper/daily_auto_collect.py`
- 이메일 발송: `Valuation_Company/scripts/investment-news-scraper/send_daily_email.py`
