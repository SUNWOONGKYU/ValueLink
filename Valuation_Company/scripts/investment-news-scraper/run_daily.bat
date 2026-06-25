@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set "PYTHONIOENCODING=utf-8"
set "SCRDIR=C:\ValueLink\Valuation_Company\scripts\investment-news-scraper"
set "PY=C:\Python314\python.exe"
set "LOG=%SCRDIR%\scheduler.log"
REM ValueLink deal-news daily collect + subscriber email (Naver only)
REM Task Scheduler calls daily 08:00. arg "nomail" = skip email (verify mode)
REM NOTE: keep this file PURE ASCII / no BOM. cmd cannot parse a BOM-prefixed .bat.

echo.>> "%LOG%"
echo ===== %date% %time% RUN (arg=%1) =====>> "%LOG%"

if not exist "%PY%" (
    echo [FATAL] Python not found: %PY%>> "%LOG%"
    echo ===== %date% %time% END no-python =====>> "%LOG%"
    exit /b 2
)

REM 1) collect (every day)
"%PY%" "%SCRDIR%\collect_naver_only.py" --days 2 >> "%LOG%" 2>&1
set COLLECT_ERR=%ERRORLEVEL%
echo [INFO] collect exit=%COLLECT_ERR%>> "%LOG%"
if not "%COLLECT_ERR%"=="0" (
    echo [ERROR] collect failed code=%COLLECT_ERR%>> "%LOG%"
    "%PY%" "%SCRDIR%\send_daily_email.py" --notify-error "collect failed code=%COLLECT_ERR%" >> "%LOG%" 2>&1
    echo ===== %date% %time% END collect-fail =====>> "%LOG%"
    exit /b %COLLECT_ERR%
)

REM verify mode: skip email
if /i "%1"=="nomail" (
    echo [SKIP] nomail verify - email skipped>> "%LOG%"
    echo ===== %date% %time% END nomail =====>> "%LOG%"
    exit /b 0
)

REM Sunday(0): skip subscriber email
for /f "tokens=1" %%d in ('powershell -NoProfile -Command "(Get-Date).DayOfWeek.value__"') do set DOW=%%d
echo [INFO] DayOfWeek=%DOW% 0=Sunday>> "%LOG%"
if "%DOW%"=="0" (
    echo [SKIP] Sunday - subscriber email skipped>> "%LOG%"
    echo ===== %date% %time% END sun =====>> "%LOG%"
    exit /b 0
)

REM 2) subscriber email (failure does NOT fail the task - collect already ok)
"%PY%" "%SCRDIR%\send_daily_email.py" >> "%LOG%" 2>&1
set EMAIL_ERR=%ERRORLEVEL%
echo [INFO] email exit=%EMAIL_ERR%>> "%LOG%"
if not "%EMAIL_ERR%"=="0" (
    echo [WARN] email failed code=%EMAIL_ERR% - task still ok since collect succeeded>> "%LOG%"
    "%PY%" "%SCRDIR%\send_daily_email.py" --notify-error "email failed code=%EMAIL_ERR%" >> "%LOG%" 2>&1
)
echo ===== %date% %time% END =====>> "%LOG%"
exit /b 0
