@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
REM ValueLink 딜 뉴스 일일 수집 (Naver 전용, Gemini/GitHub Actions 불필요)
REM Windows 작업 스케줄러가 매일 호출
"C:\Python314\python.exe" "C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\collect_naver_only.py" --days 2 >> "C:\ValueLink\Valuation_Company\scripts\investment-news-scraper\scheduler.log" 2>&1
