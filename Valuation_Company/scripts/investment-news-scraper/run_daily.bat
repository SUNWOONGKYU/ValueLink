@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set SCRDIR=C:\ValueLink\Valuation_Company\scripts\investment-news-scraper
set PY="C:\Python314\python.exe"
set LOG="%SCRDIR%\scheduler.log"
REM ValueLink 딜 뉴스 일일 수집 + 구독자 이메일 발송 (Naver 전용, Gemini/GitHub Actions 불필요)
REM Windows 작업 스케줄러가 매일 08:00 호출
echo. >> %LOG%
echo ===== %date% %time% RUN ===== >> %LOG%
REM 1) 뉴스 수집
%PY% "%SCRDIR%\collect_naver_only.py" --days 2 >> %LOG% 2>&1
REM 2) 구독자 일일 이메일 발송 (어제 딜 없으면 스크립트가 자동 스킵)
%PY% "%SCRDIR%\send_daily_email.py" >> %LOG% 2>&1
