@echo off
echo ======================================================
echo   ValueLink Daily Investment News Automation
echo ======================================================
cd /d %~dp0backend
python daily_automation.py
echo ======================================================
echo   Process Completed.
pause
