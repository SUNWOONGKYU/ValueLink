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

REM ── 결함3: 일요일(0) 가드 — 일요일에는 이메일 발송만 건너뜀, 수집은 계속 ──
for /f "tokens=1" %%d in ('powershell -NoProfile -Command "(Get-Date).DayOfWeek.value__"') do set DOW=%%d
echo [INFO] DayOfWeek=%DOW% (0=Sunday) >> %LOG%

REM 1) 뉴스 수집 (요일 무관 매일 실행)
%PY% "%SCRDIR%\collect_naver_only.py" --days 2 >> %LOG% 2>&1
set COLLECT_ERR=%ERRORLEVEL%

REM 수집 실패 시 본인 메일 알림
if %COLLECT_ERR% NEQ 0 (
    echo [ERROR] collect_naver_only.py 실패 (errorlevel=%COLLECT_ERR%) >> %LOG%
    %PY% "%SCRDIR%\send_daily_email.py" --notify-error "collect_naver_only 실패 (code=%COLLECT_ERR%)" >> %LOG% 2>&1
    goto :end
)

REM 2) 구독자 일일 이메일 발송 — 일요일(0) 제외 (어제 딜 없으면 스크립트가 자동 스킵)
if "%DOW%"=="0" (
    echo [SKIP] 일요일 — 구독자 이메일 발송 건너뜀 >> %LOG%
    goto :end
)

%PY% "%SCRDIR%\send_daily_email.py" >> %LOG% 2>&1
set EMAIL_ERR=%ERRORLEVEL%

if %EMAIL_ERR% NEQ 0 (
    echo [ERROR] send_daily_email.py 실패 (errorlevel=%EMAIL_ERR%) >> %LOG%
    %PY% "%SCRDIR%\send_daily_email.py" --notify-error "send_daily_email 실패 (code=%EMAIL_ERR%)" >> %LOG% 2>&1
)

:end
echo ===== %date% %time% END ===== >> %LOG%
