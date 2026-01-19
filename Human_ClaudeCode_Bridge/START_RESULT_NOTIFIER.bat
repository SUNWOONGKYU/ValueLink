@echo off
echo ================================================================================
echo   ORDER RESULT NOTIFIER
echo ================================================================================
echo.
echo This will automatically show completed order results in your Claude Code session.
echo You don't need to ask "did you finish?" - it will tell you automatically!
echo.
echo Starting...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0result_notifier.ps1"
pause
